import datetime
import threading
from typing import Optional, Dict, Any, List
import structlog

from minecraft_mcp.client.bridge import BridgeClient, BridgeError
from minecraft_mcp.models.construction import (
    ConstructionPlan,
    ConstructionProject,
    ConstructionProgress,
    ComponentStatusRecord,
    ProjectStatus,
)
from minecraft_mcp.tracker import ActionStateTracker
from minecraft_mcp.models.actions import ActionStateEnum
from minecraft_mcp.safety import validate_coordinates, SafetyError

logger = structlog.get_logger("minecraft_mcp.construction")

class ConstructionEngine:
    _instance: Optional["ConstructionEngine"] = None
    _lock = threading.Lock()

    def __init__(self, client: Optional[BridgeClient] = None):
        self.client = client or BridgeClient()
        self.current_project: Optional[ConstructionProject] = None
        self.last_completed_project: Optional[ConstructionProject] = None
        self.last_plan: Optional[ConstructionPlan] = None
        self._cancel_requested = False

    @classmethod
    def get_instance(cls, client: Optional[BridgeClient] = None) -> "ConstructionEngine":
        with cls._lock:
            if cls._instance is None:
                cls._instance = ConstructionEngine(client=client)
            return cls._instance

    def get_current_project(self) -> Optional[ConstructionProject]:
        with self._lock:
            return self.current_project.model_copy() if self.current_project else None

    def cancel_construction(self) -> bool:
        with self._lock:
            self._cancel_requested = True
            if self.current_project:
                self.current_project.status = ProjectStatus.CANCELLED
                return True
            return False

    async def execute_plan(
        self,
        plan: ConstructionPlan,
        clear_envelope: bool = True,
        structure_type: str = "custom",
        project_name: Optional[str] = None
    ) -> ConstructionProject:
        """Executes a sequenced ConstructionPlan via the Fabric bridge."""
        self._cancel_requested = False
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Group steps by component
        component_names = []
        comp_steps_map: Dict[str, List[Dict[str, Any]]] = {}
        for s in plan.steps:
            if s.component_name not in comp_steps_map:
                component_names.append(s.component_name)
                comp_steps_map[s.component_name] = []
            comp_steps_map[s.component_name].append({"x": s.x, "y": s.y, "z": s.z, "block": s.block})

        components_records = [
            ComponentStatusRecord(
                name=cname,
                status=ProjectStatus.PLANNED,
                completed_blocks=0,
                total_blocks=len(comp_steps_map[cname]),
                verified=False
            )
            for cname in component_names
        ]

        project = ConstructionProject(
            project_id=plan.project_id,
            name=project_name or f"Construct {plan.blueprint_id}",
            blueprint_id=plan.blueprint_id,
            structure_type=structure_type,
            status=ProjectStatus.BUILDING,
            progress=ConstructionProgress(completed_blocks=0, planned_blocks=plan.total_blocks, percentage=0.0),
            anchor_position=plan.anchor,
            components=components_records,
            failures=[],
            created_at=now_str,
            updated_at=now_str,
        )

        with self._lock:
            self.current_project = project
            self.last_plan = plan

        action_tracker = ActionStateTracker.get_instance()
        async with action_tracker.track("build_structure", ActionStateEnum.BUILDING, target={"project_id": plan.project_id, "total_blocks": plan.total_blocks}):
            try:
                # 1. Clear envelope airspace if requested
                if clear_envelope:
                    b_min = plan.bounds["min"]
                    b_max = plan.bounds["max"]
                    clear_y1 = b_min["y"] + 1
                    clear_y2 = min(319, b_max["y"] + 1)
                    if clear_y1 <= clear_y2:
                        try:
                            # Use fill_region in safe batches if volume <= 500
                            vol = (b_max["x"] - b_min["x"] + 1) * (clear_y2 - clear_y1 + 1) * (b_max["z"] - b_min["z"] + 1)
                            if vol <= 500:
                                await self.client.fill_region(
                                    b_min["x"], clear_y1, b_min["z"],
                                    b_max["x"], clear_y2, b_max["z"],
                                    "minecraft:air"
                                )
                        except Exception as e:
                            logger.warning("Envelope clearance skipped or partial", error=str(e))

                # 2. Build each component in sequence
                total_placed = 0
                for comp_record in project.components:
                    if self._cancel_requested:
                        project.status = ProjectStatus.CANCELLED
                        break

                    project.current_component = comp_record.name
                    comp_record.status = ProjectStatus.BUILDING

                    c_steps = comp_steps_map[comp_record.name]
                    # Batch placement (max 500 blocks per batch)
                    batch_size = 500
                    comp_placed = 0
                    for i in range(0, len(c_steps), batch_size):
                        if self._cancel_requested:
                            break
                        batch = c_steps[i:i + batch_size]
                        for b in batch:
                            try:
                                validate_coordinates(b["x"], b["y"], b["z"])
                                await self.client.set_block(b["x"], b["y"], b["z"], b["block"])
                                comp_placed += 1
                                total_placed += 1
                            except Exception as ex:
                                project.failures.append(f"Failed block at ({b['x']}, {b['y']}, {b['z']}): {str(ex)}")

                        project.progress.completed_blocks = total_placed
                        project.progress.percentage = round((total_placed / max(1, plan.total_blocks)) * 100.0, 2)
                        project.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

                    comp_record.completed_blocks = comp_placed
                    comp_record.status = ProjectStatus.COMPLETED if comp_placed == len(c_steps) else ProjectStatus.FAILED
                    comp_record.verified = (comp_placed == len(c_steps))

                # Finalize status
                if self._cancel_requested:
                    project.status = ProjectStatus.CANCELLED
                elif len(project.failures) == 0:
                    project.status = ProjectStatus.COMPLETED
                else:
                    project.status = ProjectStatus.FAILED

                project.last_verified = datetime.datetime.now(datetime.timezone.utc).isoformat()
                project.updated_at = project.last_verified

            except Exception as e:
                project.status = ProjectStatus.FAILED
                project.failures.append(str(e))
                logger.error("Construction project execution failed", error=str(e))

            finally:
                with self._lock:
                    self.last_completed_project = project.model_copy()

        return project
