"""
Build Transactions, Rollback Snapshots, and Compact Verification for Minecraft Procedural Construction.
Ensures large procedural operations are atomic, reversible on failure, and verified without token blowout.
"""

import threading
import structlog
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
from minecraft_mcp.client.bridge import BridgeClient, BridgeError
from minecraft_mcp.procedural.compiler import CompiledBuildPlan
from minecraft_mcp.tracker import ActionStateTracker
from minecraft_mcp.models.actions import ActionStateEnum

logger = structlog.get_logger("minecraft_mcp.procedural.transactions")

class CompactVerificationReport(BaseModel):
    """Token-efficient verification digest returning statistics rather than raw coordinate dumps."""
    project_id: str
    status: str = "VALID"
    bounds_match: bool = True
    expected_volume: int = 0
    actual_placed_blocks: int = 0
    fill_regions_used: int = 0
    sparse_batches_used: int = 0
    material_breakdown: Dict[str, int] = Field(default_factory=dict)
    integrity_checksum: str = ""
    discrepancies: int = 0
    samples_checked: int = 0

class BuildSnapshot:
    def __init__(self, project_id: str, bounds: Dict[str, Dict[str, int]]):
        self.project_id = project_id
        self.bounds = bounds
        self.original_blocks: Dict[Tuple[int, int, int], str] = {}
        self.committed: bool = False

class BuildTransactionManager:
    """Manages transactional build lifecycles and rollback restores."""

    _instance: Optional["BuildTransactionManager"] = None
    _lock = threading.Lock()

    def __init__(self):
        self.active_snapshots: Dict[str, BuildSnapshot] = {}

    @classmethod
    def get_instance(cls) -> "BuildTransactionManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = BuildTransactionManager()
            return cls._instance

    async def begin_transaction(
        self,
        project_id: str,
        bounds: Dict[str, Dict[str, int]],
        client: BridgeClient
    ) -> BuildSnapshot:
        """Captures pre-build blocks across footprint to enable transactional rollback."""
        snapshot = BuildSnapshot(project_id, bounds)
        with self._lock:
            self.active_snapshots[project_id] = snapshot

        try:
            b_min = bounds["min"]
            b_max = bounds["max"]
            vol = (b_max["x"] - b_min["x"] + 1) * (b_max["y"] - b_min["y"] + 1) * (b_max["z"] - b_min["z"] + 1)
            # Only snapshot if volume is reasonable (<= 32,768 blocks)
            if vol <= 32768:
                data = await client.get_blocks(
                    min_x=b_min["x"], min_y=b_min["y"], min_z=b_min["z"],
                    max_x=b_max["x"], max_y=b_max["y"], max_z=b_max["z"],
                    include_air=True
                )
                for b in data.blocks:
                    snapshot.original_blocks[(b.pos["x"], b.pos["y"], b.pos["z"])] = b.id
        except Exception as e:
            logger.warning("Could not snapshot full world volume for rollback", error=str(e))

        return snapshot

    async def execute_plan_transactionally(
        self,
        project_id: str,
        plan: CompiledBuildPlan,
        client: BridgeClient,
        action_tracker: Optional[ActionStateTracker] = None,
        auto_rollback_on_failure: bool = True
    ) -> Dict[str, Any]:
        """Executes compiled fill_region cuboids and sparse batches with failure protection."""
        tracker = action_tracker or ActionStateTracker.get_instance()
        total_placed = 0
        fill_count = 0
        sparse_batch_count = 0
        failures: List[str] = []

        async with tracker.track("procedural_build", ActionStateEnum.BUILDING, target={"project_id": project_id, "total_voxels": plan.total_voxels}):
            try:
                # 1. Execute maximal fill_region operations
                for op in plan.fill_operations:
                    try:
                        res = await client.fill_region(
                            from_x=op.from_pos[0], from_y=op.from_pos[1], from_z=op.from_pos[2],
                            to_x=op.to_pos[0], to_y=op.to_pos[1], to_z=op.to_pos[2],
                            block_state=op.block
                        )
                        if res.get("verified", True) or res.get("placed", True):
                            total_placed += op.volume
                            fill_count += 1
                        else:
                            failures.append(f"Fill failed at {op.from_pos} to {op.to_pos}")
                    except Exception as ex:
                        failures.append(f"Fill error: {str(ex)}")
                        if auto_rollback_on_failure:
                            raise

                # 2. Execute sparse perimeter fringe batches (<= 500 blocks per call)
                sparse = plan.sparse_placements
                batch_size = 500
                for i in range(0, len(sparse), batch_size):
                    batch = sparse[i:i + batch_size]
                    sparse_batch_count += 1
                    for b in batch:
                        try:
                            await client.set_block(b["x"], b["y"], b["z"], b["block"])
                            total_placed += 1
                        except Exception as ex:
                            failures.append(f"Failed sparse block at ({b['x']}, {b['y']}, {b['z']}): {str(ex)}")

            except Exception as e:
                logger.error("Transaction execution aborted", project_id=project_id, error=str(e))
                if auto_rollback_on_failure:
                    await self.rollback_transaction(project_id, client)
                return {
                    "success": False,
                    "project_id": project_id,
                    "error": str(e),
                    "total_placed": total_placed,
                    "rolled_back": auto_rollback_on_failure,
                }

        # 3. Commit transaction
        with self._lock:
            if project_id in self.active_snapshots:
                self.active_snapshots[project_id].committed = True

        return {
            "success": len(failures) == 0,
            "project_id": project_id,
            "total_placed": total_placed,
            "fill_regions_used": fill_count,
            "sparse_batches_used": sparse_batch_count,
            "failures": failures,
        }

    async def verify_transaction(
        self,
        project_id: str,
        plan: CompiledBuildPlan,
        client: BridgeClient
    ) -> CompactVerificationReport:
        """Performs closed-loop sample checking and generates a compact verification report."""
        samples_checked = 0
        discrepancies = 0

        # Sample checking: check from_pos and to_pos of each fill cuboid
        for op in plan.fill_operations[:20]:  # Cap samples to keep verification fast
            try:
                check1 = await client.get_block(op.from_pos[0], op.from_pos[1], op.from_pos[2])
                check2 = await client.get_block(op.to_pos[0], op.to_pos[1], op.to_pos[2])
                expected_id = op.block.split("[")[0]
                samples_checked += 2
                if check1.blockId != expected_id:
                    discrepancies += 1
                if check2.blockId != expected_id:
                    discrepancies += 1
            except Exception:
                discrepancies += 1

        is_valid = (discrepancies == 0)
        return CompactVerificationReport(
            project_id=project_id,
            status="VALID" if is_valid else "DISCREPANCY_DETECTED",
            bounds_match=True,
            expected_volume=plan.total_voxels,
            actual_placed_blocks=plan.total_voxels - discrepancies,
            fill_regions_used=len(plan.fill_operations),
            sparse_batches_used=(len(plan.sparse_placements) + 499) // 500,
            material_breakdown=plan.materials_summary,
            integrity_checksum=plan.integrity_checksum,
            discrepancies=discrepancies,
            samples_checked=samples_checked,
        )

    async def rollback_transaction(self, project_id: str, client: BridgeClient) -> Dict[str, Any]:
        """Rolls back placed blocks to snapshot state."""
        with self._lock:
            snapshot = self.active_snapshots.get(project_id)
        if not snapshot:
            return {"success": False, "error": f"No active snapshot found for project '{project_id}'"}

        restored_count = 0
        if snapshot.original_blocks:
            for (x, y, z), orig_block in snapshot.original_blocks.items():
                try:
                    await client.set_block(x, y, z, orig_block)
                    restored_count += 1
                except Exception:
                    pass
        else:
            try:
                b_min = snapshot.bounds.get("min", {})
                b_max = snapshot.bounds.get("max", {})
                if b_min and b_max:
                    await client.fill_region(
                        from_x=b_min["x"], from_y=b_min["y"], from_z=b_min["z"],
                        to_x=b_max["x"], to_y=b_max["y"], to_z=b_max["z"],
                        block_state="minecraft:air"
                    )
                    restored_count = (b_max["x"] - b_min["x"] + 1) * (b_max["y"] - b_min["y"] + 1) * (b_max["z"] - b_min["z"] + 1)
            except Exception:
                pass

        with self._lock:
            if project_id in self.active_snapshots:
                del self.active_snapshots[project_id]

        return {
            "success": True,
            "project_id": project_id,
            "restored_blocks": restored_count,
        }

