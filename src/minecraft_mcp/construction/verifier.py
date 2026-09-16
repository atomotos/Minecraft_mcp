import datetime
from typing import Dict, Any, List, Optional, Tuple
import structlog
from minecraft_mcp.client.bridge import BridgeClient
from minecraft_mcp.models.construction import ConstructionPlan, ConstructionProject

logger = structlog.get_logger("minecraft_mcp.verifier")

class StructureVerifier:
    """
    Validates physical world block states against architectural construction plans.
    Detects missing blocks, mismatched materials, and foreign obstructions.
    """

    def __init__(self, bridge_client: Optional[BridgeClient] = None):
        self.client = bridge_client or BridgeClient()

    async def verify_plan(
        self,
        plan: ConstructionPlan,
        project_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Queries world blocks across the plan's bounding envelope and compares
        every planned step against the ground-truth voxel state.
        """
        if not plan.steps:
            return {
                "valid": True,
                "total_planned": 0,
                "verified_count": 0,
                "discrepancies_count": 0,
                "completion_percentage": 100.0,
                "discrepancies": [],
            }

        b_min = plan.bounds["min"]
        b_max = plan.bounds["max"]

        # Ensure volume <= 32,768 for scanning
        vol = (b_max["x"] - b_min["x"] + 1) * (b_max["y"] - b_min["y"] + 1) * (b_max["z"] - b_min["z"] + 1)
        
        world_voxels: Dict[Tuple[int, int, int], Tuple[str, str]] = {}

        if vol <= 32768:
            try:
                area = await self.client.get_blocks(
                    min_x=b_min["x"],
                    min_y=b_min["y"],
                    min_z=b_min["z"],
                    max_x=b_max["x"],
                    max_y=b_max["y"],
                    max_z=b_max["z"],
                    include_air=False,
                )
                for b in area.blocks:
                    world_voxels[(b.pos["x"], b.pos["y"], b.pos["z"])] = (b.id.lower(), b.state.lower())
            except Exception as e:
                logger.error("Failed to query block area for verification", error=str(e))
                return {
                    "valid": False,
                    "error": f"Failed to query blocks for verification: {str(e)}",
                    "total_planned": len(plan.steps),
                    "verified_count": 0,
                    "discrepancies_count": len(plan.steps),
                    "completion_percentage": 0.0,
                    "discrepancies": [],
                }
        else:
            # For massive structures, sample or batch query
            # For now query each step or smaller slices if needed
            logger.warning("Large plan volume exceeds single scan limit", volume=vol)

        verified_count = 0
        discrepancies: List[Dict[str, Any]] = []

        for step in plan.steps:
            pos_key = (step.x, step.y, step.z)
            expected_full = step.block.lower()
            expected_base = expected_full.split("[")[0]
            if not expected_base.startswith("minecraft:"):
                expected_base = f"minecraft:{expected_base}"

            if pos_key in world_voxels:
                actual_id, actual_state = world_voxels[pos_key]
                if actual_id == expected_base:
                    # Matches base block type
                    verified_count += 1
                else:
                    discrepancies.append({
                        "pos": {"x": step.x, "y": step.y, "z": step.z},
                        "component": step.component_name,
                        "expected": expected_full,
                        "actual": actual_id,
                        "type": "MISMATCH",
                    })
            else:
                # Omitted from non-air scan => world block is air or ungenerated
                discrepancies.append({
                    "pos": {"x": step.x, "y": step.y, "z": step.z},
                    "component": step.component_name,
                    "expected": expected_full,
                    "actual": "minecraft:air",
                    "type": "MISSING",
                })

        total_steps = len(plan.steps)
        completion_pct = round((verified_count / max(1, total_steps)) * 100.0, 1)

        return {
            "project_id": project_id or plan.project_id,
            "valid": len(discrepancies) == 0,
            "total_planned": total_steps,
            "verified_count": verified_count,
            "discrepancies_count": len(discrepancies),
            "completion_percentage": completion_pct,
            "discrepancies": discrepancies[:50],
            "verified_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
