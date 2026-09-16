from typing import List, Optional
from pydantic import BaseModel, Field

class BlockProperties(BaseModel):
    solid: bool = True
    transparent: bool = False
    flammable: bool = False
    gravity: bool = False

class BlockAppearance(BaseModel):
    color: Optional[str] = None
    texture_category: Optional[str] = None  # e.g. "wood", "stone", "glass", "metal"

class BlockConstructionUses(BaseModel):
    uses: List[str] = Field(default_factory=list)  # e.g. ["wall", "floor", "foundation", "beam", "roof"]

class BlockRelationships(BaseModel):
    family: Optional[str] = None
    stairs: Optional[str] = None
    slab: Optional[str] = None
    door: Optional[str] = None
    wall: Optional[str] = None
    fence: Optional[str] = None

class BlockKnowledge(BaseModel):
    id: str
    name: str
    appearance: BlockAppearance = Field(default_factory=BlockAppearance)
    properties: BlockProperties = Field(default_factory=BlockProperties)
    construction: BlockConstructionUses = Field(default_factory=BlockConstructionUses)
    relationships: BlockRelationships = Field(default_factory=BlockRelationships)

class MaterialPaletteKnowledge(BaseModel):
    id: str
    name: str
    category: str
    blocks: List[str] = Field(default_factory=list)

class ArchitectureKnowledge(BaseModel):
    templates: List[str] = Field(default_factory=list)
    styles: List[str] = Field(default_factory=list)
    component_types: List[str] = Field(default_factory=list)
