"""
Multi-Agent Orchestration Blackboard & Spatial Collision Guard for Minecraft MCP.
Enables specialized subagents (Surveyor, Mason, Artisan, QA Inspector) to share
real-time state, coordinate spatial zones, and track project milestones without context blowout.
"""

import threading
import time
from typing import Dict, Any, List, Optional, Tuple


class SpatialZone:
    """Represents an active 3D bounding box assigned to a specific subagent."""

    def __init__(self, zone_id: str, agent_id: str, bounds: Dict[str, Any], zone_name: str = ""):
        self.zone_id = zone_id
        self.agent_id = agent_id
        self.zone_name = zone_name or zone_id
        # Normalize bounds: min: [x,y,z], max: [x,y,z]
        b_min = bounds.get("min", [0, 0, 0])
        b_max = bounds.get("max", [0, 0, 0])
        self.min_x = min(b_min[0], b_max[0])
        self.max_x = max(b_min[0], b_max[0])
        self.min_y = min(b_min[1], b_max[1])
        self.max_y = max(b_min[1], b_max[1])
        self.min_z = min(b_min[2], b_max[2])
        self.max_z = max(b_min[2], b_max[2])

    def overlaps_with(self, other: "SpatialZone") -> bool:
        """Determines if two 3D spatial zones intersect."""
        x_overlap = self.min_x <= other.max_x and self.max_x >= other.min_x
        y_overlap = self.min_y <= other.max_y and self.max_y >= other.min_y
        z_overlap = self.min_z <= other.max_z and self.max_z >= other.min_z
        return x_overlap and y_overlap and z_overlap

    def to_dict(self) -> Dict[str, Any]:
        return {
            "zone_id": self.zone_id,
            "agent_id": self.agent_id,
            "zone_name": self.zone_name,
            "bounds": {
                "min": [self.min_x, self.min_y, self.min_z],
                "max": [self.max_x, self.max_y, self.max_z],
            }
        }


class SubagentRecord:
    """Tracks a single active subagent within the architectural guild."""

    VALID_STATES = {"IDLE", "ASSIGNED", "WORKING", "EXECUTING", "VERIFYING", "COMPLETED", "FAILED"}

    def __init__(self, agent_id: str, role: str, current_task: str = ""):
        self.agent_id = agent_id
        self.role = role
        self.state = "IDLE"
        self.current_task = current_task
        self.assigned_zone: Optional[Dict[str, Any]] = None
        self.created_at = time.time()
        self.updated_at = time.time()

    def update_state(self, state: str, task: Optional[str] = None):
        st = state.upper()
        if st in self.VALID_STATES:
            self.state = st
        if task is not None:
            self.current_task = task
        self.updated_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "state": self.state,
            "current_task": self.current_task,
            "assigned_zone": self.assigned_zone,
            "updated_at": self.updated_at,
        }


class OrchestrationBlackboard:
    """Thread-safe singleton managing inter-agent state, spatial boundaries, and project synchronization."""

    _instance: Optional["OrchestrationBlackboard"] = None
    _lock = threading.Lock()

    def __init__(self):
        self.project_id: str = "project_default"
        self.monument_name: str = "Unspecified Monument"
        self.roster: Dict[str, SubagentRecord] = {}
        self.zones: Dict[str, SpatialZone] = {}  # keyed by agent_id
        self.blackboard: Dict[str, Any] = {
            "project_id": self.project_id,
            "monument_name": self.monument_name,
            "status": "INITIALIZED",
            "site_datum_y": None,
            "surveyed_footprint": None,
            "structural_bounds": None,
            "material_tokens": {},
            "notes": [],
        }
        self.progress: Dict[str, Any] = {
            "overall_pct": 0.0,
            "current_phase": "NOT_STARTED",
            "phases": {
                "SURVEY_FOUNDATION": {"progress_pct": 0.0, "status": "PENDING", "blocks_placed": 0},
                "STRUCTURAL_SHELL": {"progress_pct": 0.0, "status": "PENDING", "blocks_placed": 0},
                "ARCHITECTURAL_DETAILING": {"progress_pct": 0.0, "status": "PENDING", "blocks_placed": 0},
                "QA_CERTIFICATION": {"progress_pct": 0.0, "status": "PENDING", "blocks_placed": 0},
            },
            "total_blocks_placed": 0,
            "total_bridge_calls": 0,
        }
        self.scorecard: Dict[str, Any] = {
            "status": "UNVERIFIED",
            "bounds_match": False,
            "expected_volume": 0,
            "verified_blocks": 0,
            "integrity_checksum": None,
            "samples_checked": 0,
            "discrepancies": 0,
            "repaired_blocks": 0,
            "certified": False,
        }

    @classmethod
    def get_instance(cls) -> "OrchestrationBlackboard":
        with cls._lock:
            if cls._instance is None:
                cls._instance = OrchestrationBlackboard()
            return cls._instance

    def reset_project(self, project_id: str, monument_name: str = "") -> None:
        """Resets blackboard and progress for a new architectural monument project."""
        with self._lock:
            self.project_id = project_id
            self.monument_name = monument_name or project_id
            self.roster.clear()
            self.zones.clear()
            self.blackboard = {
                "project_id": self.project_id,
                "monument_name": self.monument_name,
                "status": "INITIALIZED",
                "site_datum_y": None,
                "surveyed_footprint": None,
                "structural_bounds": None,
                "material_tokens": {},
                "notes": [],
            }
            self.progress = {
                "overall_pct": 0.0,
                "current_phase": "INITIALIZED",
                "phases": {
                    "SURVEY_FOUNDATION": {"progress_pct": 0.0, "status": "PENDING", "blocks_placed": 0},
                    "STRUCTURAL_SHELL": {"progress_pct": 0.0, "status": "PENDING", "blocks_placed": 0},
                    "ARCHITECTURAL_DETAILING": {"progress_pct": 0.0, "status": "PENDING", "blocks_placed": 0},
                    "QA_CERTIFICATION": {"progress_pct": 0.0, "status": "PENDING", "blocks_placed": 0},
                },
                "total_blocks_placed": 0,
                "total_bridge_calls": 0,
            }
            self.scorecard = {
                "status": "UNVERIFIED",
                "bounds_match": False,
                "expected_volume": 0,
                "verified_blocks": 0,
                "integrity_checksum": None,
                "samples_checked": 0,
                "discrepancies": 0,
                "repaired_blocks": 0,
                "certified": False,
            }

    # -----------------------------------------------------------------------
    # Subagent Roster Management
    # -----------------------------------------------------------------------

    def register_subagent(self, agent_id: str, role: str, current_task: str = "") -> Dict[str, Any]:
        """Registers a subagent to the active roster."""
        with self._lock:
            record = SubagentRecord(agent_id, role, current_task)
            self.roster[agent_id] = record
            return record.to_dict()

    def update_subagent_state(self, agent_id: str, state: str, current_task: Optional[str] = None) -> bool:
        """Updates subagent lifecycle state."""
        with self._lock:
            if agent_id not in self.roster:
                return False
            self.roster[agent_id].update_state(state, current_task)
            return True

    def get_roster(self) -> Dict[str, Any]:
        """Returns the full active subagent roster."""
        with self._lock:
            return {aid: rec.to_dict() for aid, rec in self.roster.items()}

    # -----------------------------------------------------------------------
    # Spatial Zoning & Collision Guard
    # -----------------------------------------------------------------------

    def assign_zone(
        self,
        agent_id: str,
        bounds: Dict[str, Any],
        zone_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Assigns a 3D bounding box to an agent, performing collision checks against
        all currently active zones to prevent conflicting block placements.
        """
        with self._lock:
            new_zone = SpatialZone(
                zone_id=f"zone_{agent_id}",
                agent_id=agent_id,
                bounds=bounds,
                zone_name=zone_name or f"Zone for {agent_id}"
            )

            # Check collision with existing active zones (excluding self)
            for other_id, existing_zone in self.zones.items():
                if other_id != agent_id and new_zone.overlaps_with(existing_zone):
                    return {
                        "success": False,
                        "conflict": True,
                        "colliding_agent": other_id,
                        "colliding_zone": existing_zone.to_dict(),
                        "error": (
                            f"Spatial collision detected! Zone for '{agent_id}' overlaps with "
                            f"active zone '{existing_zone.zone_name}' assigned to '{other_id}'."
                        )
                    }

            self.zones[agent_id] = new_zone
            if agent_id in self.roster:
                self.roster[agent_id].assigned_zone = new_zone.to_dict()

            return {
                "success": True,
                "conflict": False,
                "zone": new_zone.to_dict(),
            }

    def release_zone(self, agent_id: str) -> None:
        """Releases the spatial zone assigned to an agent."""
        with self._lock:
            if agent_id in self.zones:
                del self.zones[agent_id]
            if agent_id in self.roster:
                self.roster[agent_id].assigned_zone = None

    def get_active_zones(self) -> List[Dict[str, Any]]:
        """Returns all currently active spatial zones."""
        with self._lock:
            return [z.to_dict() for z in self.zones.values()]

    # -----------------------------------------------------------------------
    # Inter-Agent Shared Blackboard
    # -----------------------------------------------------------------------

    def set_blackboard_value(self, key: str, value: Any) -> None:
        """Sets an arbitrary shared state parameter on the blackboard."""
        with self._lock:
            self.blackboard[key] = value

    def get_blackboard_value(self, key: str, default: Any = None) -> Any:
        """Retrieves a shared state parameter from the blackboard."""
        with self._lock:
            return self.blackboard.get(key, default)

    def get_blackboard_state(self) -> Dict[str, Any]:
        """Returns the full inter-agent blackboard state."""
        with self._lock:
            return dict(self.blackboard)

    # -----------------------------------------------------------------------
    # Hierarchical Progress Tracker
    # -----------------------------------------------------------------------

    def update_progress(
        self,
        phase_name: str,
        progress_pct: float,
        blocks_placed: int = 0,
        bridge_calls: int = 0,
        status: str = "IN_PROGRESS"
    ) -> Dict[str, Any]:
        """Updates milestone progress for a specific construction phase."""
        with self._lock:
            p_key = phase_name.upper()
            if p_key not in self.progress["phases"]:
                self.progress["phases"][p_key] = {"progress_pct": 0.0, "status": "PENDING", "blocks_placed": 0}

            self.progress["phases"][p_key]["progress_pct"] = max(0.0, min(100.0, progress_pct))
            self.progress["phases"][p_key]["status"] = status
            self.progress["phases"][p_key]["blocks_placed"] += blocks_placed

            self.progress["total_blocks_placed"] += blocks_placed
            self.progress["total_bridge_calls"] += bridge_calls
            self.progress["current_phase"] = p_key

            # Compute overall weighted progress
            phase_count = len(self.progress["phases"])
            if phase_count > 0:
                total_pct = sum(p["progress_pct"] for p in self.progress["phases"].values())
                self.progress["overall_pct"] = round(total_pct / phase_count, 1)

            return dict(self.progress)

    def get_progress(self) -> Dict[str, Any]:
        """Returns the current hierarchical progress report."""
        with self._lock:
            return dict(self.progress)

    # -----------------------------------------------------------------------
    # QA Inspection Scorecard
    # -----------------------------------------------------------------------

    def record_scorecard(self, scorecard_data: Dict[str, Any]) -> None:
        """Records the latest QA verification scorecard."""
        with self._lock:
            self.scorecard.update(scorecard_data)

    def get_scorecard(self) -> Dict[str, Any]:
        """Returns the latest QA verification scorecard."""
        with self._lock:
            return dict(self.scorecard)

