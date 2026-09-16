from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class LandmarkCategory(str, Enum):
    BASE = "base"
    SITE = "site"
    QUARRY = "quarry"
    HAZARD = "hazard"
    STRUCTURE = "structure"
    CUSTOM = "custom"

class Landmark(BaseModel):
    name: str
    position: Dict[str, float]  # {"x": ..., "y": ..., "z": ...}
    category: LandmarkCategory = LandmarkCategory.CUSTOM
    tags: List[str] = Field(default_factory=list)
    created_at: Optional[str] = None

class StructureRecord(BaseModel):
    project_id: str
    name: str
    structure_type: str
    bounds: Dict[str, Dict[str, int]]
    status: str
    completed_at: Optional[str] = None

class RegionBounds(BaseModel):
    min: Dict[str, int]
    max: Dict[str, int]
    surface_material: Optional[str] = None
    flatness_score: Optional[float] = None
    inspected_at: Optional[str] = None

class SpatialWorldModel(BaseModel):
    player_position: Optional[Dict[str, float]] = None
    regions: List[RegionBounds] = Field(default_factory=list)
    explored_areas: List[Dict[str, Any]] = Field(default_factory=list)
    landmarks: List[Landmark] = Field(default_factory=list)
    structures: List[StructureRecord] = Field(default_factory=list)
    resource_locations: List[Dict[str, Any]] = Field(default_factory=list)
    known_obstacles: List[Dict[str, Any]] = Field(default_factory=list)
    last_updated: Optional[str] = None
