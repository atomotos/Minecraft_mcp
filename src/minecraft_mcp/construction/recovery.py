import datetime
from enum import Enum
from typing import Dict, Any, List, Optional
import structlog

from minecraft_mcp.client.bridge import BridgeClient
from minecraft_mcp.construction.engine import ConstructionEngine
from minecraft_mcp.construction.verifier import StructureVerifier
from minecraft_mcp.models.construction import ProjectStatus, ConstructionPlan, ConstructionProject
from minecraft_mcp.safety import validate_coordinates

logger = structlog.get_logger("minecraft_mcp.recovery")

class ConstructionFailureType(str, Enum):
    NO_MATERIAL = "NO_MATERIAL"
    BLOCK_NOT_FOUND = "BLOCK_NOT_FOUND"
    OBSTRUCTED = "OBSTRUCTED"
    CHUNK_UNLOADED = "CHUNK_UNLOADED"
    PLAYER_STUCK = "PLAYER_STUCK"
    VERIFICATION_FAILED = "VERIFICATION_FAILED"

class RecoveryManager:
    """
    Diagnoses construction failures, classifies errors, and executes automated
    repair routines to restore structures to their planned state.
    """

    def __init__(self, bridge_client: Optional[BridgeClient] = None):
        self.client = bridge_client or BridgeClient()
        self.verifier = StructureVerifier(bridge_client=self.client)

    def classify_error(self, error_message: str) -> ConstructionFailureType:
        """Classifies an error string into a structured failure category."""
        msg = error_message.lower()
        if "material" in msg or "resource" in msg or "missing" in msg and "inventory" in msg:
            return ConstructionFailureType.NO_MATERIAL
        elif "unknown block" in msg or "not found" in msg:
            return ConstructionFailureType.BLOCK_NOT_FOUND
        elif "stuck" in msg or "locomotion" in msg:
            return ConstructionFailureType.PLAYER_STUCK
        elif "unloaded" in msg or "chunk" in msg:
            return ConstructionFailureType.CHUNK_UNLOADED
        elif "verification" in msg or "mismatch" in msg:
            return ConstructionFailureType.VERIFICATION_FAILED
        else:
            return ConstructionFailureType.OBSTRUCTED

    async def repair_structure(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes automated repair on a construction project:
        1. Validates discrepancies against the construction plan.
        2. Clears unwanted obstruction blocks.
        3. Places missing or corrupted blocks.
        4. Re-verifies structure integrity.
        """
        engine = ConstructionEngine.get_instance(self.client)
        plan = engine.last_plan
        project = engine.current_project or engine.last_completed_project

        if not plan:
            return {
                "success": False,
                "error": "No construction plan found in memory to repair.",
            }

        if project_id and plan.project_id != project_id:
            return {
                "success": False,
                "error": f"Plan for project_id '{project_id}' not found in active session.",
            }

        # Step 1: Run verification to identify discrepancies
        verif_before = await self.verifier.verify_plan(plan, project_id=plan.project_id)
        discrepancies = verif_before.get("discrepancies", [])

        if not discrepancies:
            return {
                "success": True,
                "project_id": plan.project_id,
                "message": "Structure is already 100% verified. No repairs required.",
                "repaired_count": 0,
                "verification": verif_before,
            }

        repaired_count = 0
        repair_errors: List[str] = []

        # Step 2 & 3: Fix each discrepancy
        for item in discrepancies:
            pos = item["pos"]
            expected = item["expected"]
            disc_type = item["type"]

            try:
                validate_coordinates(pos["x"], pos["y"], pos["z"])
                # If there's an obstruction/mismatch, break it first
                if disc_type == "MISMATCH":
                    await self.client.break_block(pos["x"], pos["y"], pos["z"], drop_resources=False)

                # Set the expected block
                await self.client.set_block(pos["x"], pos["y"], pos["z"], expected)
                repaired_count += 1
            except Exception as e:
                repair_errors.append(f"Failed repairing at ({pos['x']}, {pos['y']}, {pos['z']}): {str(e)}")

        # Step 4: Re-verify structure
        verif_after = await self.verifier.verify_plan(plan, project_id=plan.project_id)

        # Update engine project state
        if project:
            if verif_after.get("valid", False):
                project.status = ProjectStatus.COMPLETED
                project.failures.clear()
            else:
                project.status = ProjectStatus.RECOVERING

        return {
            "success": True,
            "project_id": plan.project_id,
            "repaired_count": repaired_count,
            "remaining_discrepancies": verif_after.get("discrepancies_count", 0),
            "repair_errors": repair_errors,
            "verification_after": verif_after,
            "status": "COMPLETED" if verif_after.get("valid", False) else "PARTIAL",
        }
