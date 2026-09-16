from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ProjectStatus(str, Enum):
    PLANNED = "PLANNED"
    VALIDATING = "VALIDATING"
    WAITING_FOR_RESOURCES = "WAITING_FOR_RESOURCES"
    BUILDING = "BUILDING"
    VERIFYING = "VERIFYING"
    RECOVERING = "RECOVERING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class ConstructionProgress(BaseModel):
    completed_blocks: int = 0
    planned_blocks: int = 0
    percentage: float = 0.0

class ComponentStatusRecord(BaseModel):
    name: str
    status: ProjectStatus = ProjectStatus.PLANNED
    completed_blocks: int = 0
    total_blocks: int = 0
    verified: bool = False

class ConstructionStep(BaseModel):
    x: int
    y: int
    z: int
    block: str
    component_name: str
    verified: bool = False

class ConstructionPlan(BaseModel):
    project_id: str
    blueprint_id: str
    anchor: Dict[str, int]
    bounds: Dict[str, Dict[str, int]]  # {"min": {"x":..., "y":..., "z":...}, "max": {...}}
    steps: List[ConstructionStep] = Field(default_factory=list)
    total_blocks: int = 0
    materials_required: Dict[str, int] = Field(default_factory=dict)

class ConstructionProject(BaseModel):
    project_id: str
    name: str
    blueprint_id: str
    structure_type: str = "custom"
    status: ProjectStatus = ProjectStatus.PLANNED
    progress: ConstructionProgress = Field(default_factory=ConstructionProgress)
    anchor_position: Dict[str, int]
    orientation: str = "north"
    current_component: Optional[str] = None
    components: List[ComponentStatusRecord] = Field(default_factory=list)
    failures: List[str] = Field(default_factory=list)
    last_verified: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
