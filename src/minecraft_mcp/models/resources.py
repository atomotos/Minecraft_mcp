from enum import Enum
from typing import Dict, List
from pydantic import BaseModel, Field

class ResourceStatus(str, Enum):
    SUFFICIENT = "SUFFICIENT"
    SHORTAGE = "SHORTAGE"
    UNOBTAINABLE = "UNOBTAINABLE"

class CraftingStep(BaseModel):
    recipe_id: str
    input_items: Dict[str, int]
    output_item: str
    output_count: int

class CraftingRecipe(BaseModel):
    recipe_id: str
    output_item: str
    output_count: int = 1
    inputs: Dict[str, int] = Field(default_factory=dict)

class ResourceRequirement(BaseModel):
    required: Dict[str, int] = Field(default_factory=dict)
    available: Dict[str, int] = Field(default_factory=dict)
    missing: Dict[str, int] = Field(default_factory=dict)
    craftable: bool = False
    crafting_plan: List[CraftingStep] = Field(default_factory=list)
    status: ResourceStatus = ResourceStatus.SUFFICIENT

