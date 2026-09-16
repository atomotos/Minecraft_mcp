import datetime
import threading
from typing import Dict, Any, List, Optional
from minecraft_mcp.models.spatial import (
    SpatialWorldModel,
    Landmark,
    LandmarkCategory,
    StructureRecord,
    RegionBounds,
)

class SpatialWorldModelManager:
    _instance: Optional["SpatialWorldModelManager"] = None
    _lock = threading.Lock()

    def __init__(self):
        self._model = SpatialWorldModel(
            player_position=None,
            regions=[],
            explored_areas=[],
            landmarks=[],
            structures=[],
            resource_locations=[],
            known_obstacles=[],
            last_updated=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )

    @classmethod
    def get_instance(cls) -> "SpatialWorldModelManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = SpatialWorldModelManager()
            return cls._instance

    def get_model(self) -> SpatialWorldModel:
        with self._lock:
            return self._model.model_copy(deep=True)

    def update_player_position(self, x: float, y: float, z: float) -> None:
        with self._lock:
            self._model.player_position = {"x": round(x, 2), "y": round(y, 2), "z": round(z, 2)}
            self._model.last_updated = datetime.datetime.now(datetime.timezone.utc).isoformat()

    def record_explored_area(self, center: List[int], radius: int, total_blocks: int) -> None:
        with self._lock:
            area = {
                "center": center,
                "radius": radius,
                "scanned_blocks": total_blocks,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }
            self._model.explored_areas.append(area)
            if len(self._model.explored_areas) > 50:
                self._model.explored_areas.pop(0)
            self._model.last_updated = datetime.datetime.now(datetime.timezone.utc).isoformat()

    def record_region(self, min_pos: Dict[str, int], max_pos: Dict[str, int], surface_material: Optional[str] = None, flatness: Optional[float] = None) -> RegionBounds:
        with self._lock:
            region = RegionBounds(
                min=min_pos,
                max=max_pos,
                surface_material=surface_material,
                flatness_score=flatness,
                inspected_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            )
            self._model.regions.append(region)
            if len(self._model.regions) > 20:
                self._model.regions.pop(0)
            self._model.last_updated = datetime.datetime.now(datetime.timezone.utc).isoformat()
            return region

    def add_landmark(self, name: str, x: float, y: float, z: float, category: str = "custom", tags: Optional[List[str]] = None) -> Landmark:
        with self._lock:
            cat_enum = LandmarkCategory.CUSTOM
            try:
                cat_enum = LandmarkCategory(category.lower())
            except Exception:
                pass

            landmark = Landmark(
                name=name,
                position={"x": round(x, 2), "y": round(y, 2), "z": round(z, 2)},
                category=cat_enum,
                tags=tags or [],
                created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            )
            # Replace existing landmark with same name if found
            self._model.landmarks = [lm for lm in self._model.landmarks if lm.name.lower() != name.lower()]
            self._model.landmarks.append(landmark)
            self._model.last_updated = datetime.datetime.now(datetime.timezone.utc).isoformat()
            return landmark

    def get_landmarks(self, category: Optional[str] = None) -> List[Landmark]:
        with self._lock:
            if not category or category.lower() == "all":
                return [lm.model_copy() for lm in self._model.landmarks]
            return [lm.model_copy() for lm in self._model.landmarks if lm.category.value.lower() == category.lower()]

    def record_structure(self, project_id: str, name: str, structure_type: str, bounds: Dict[str, Dict[str, int]], status: str = "BUILDING") -> StructureRecord:
        with self._lock:
            rec = StructureRecord(
                project_id=project_id,
                name=name,
                structure_type=structure_type,
                bounds=bounds,
                status=status,
                completed_at=None,
            )
            self._model.structures = [s for s in self._model.structures if s.project_id != project_id]
            self._model.structures.append(rec)
            self._model.last_updated = datetime.datetime.now(datetime.timezone.utc).isoformat()
            return rec

    def update_structure_status(self, project_id: str, status: str) -> bool:
        with self._lock:
            for s in self._model.structures:
                if s.project_id == project_id:
                    s.status = status
                    if status == "COMPLETED":
                        s.completed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    self._model.last_updated = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    return True
            return False

    def get_structures(self) -> List[StructureRecord]:
        with self._lock:
            return [s.model_copy() for s in self._model.structures]
