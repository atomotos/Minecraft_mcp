from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class BlockPosModel(BaseModel):
    x: int
    y: int
    z: int

class BlockInfo(BaseModel):
    position: BlockPosModel
    loaded: bool = True
    blockId: Optional[str] = None
    blockState: Optional[str] = None
    properties: Optional[Dict[str, str]] = None
    isAir: Optional[bool] = None
    isSolid: Optional[bool] = None

class ScannedBlock(BaseModel):
    pos: Dict[str, int]
    id: str
    state: str

class AreaBlocksResponse(BaseModel):
    count: int
    blocks: List[ScannedBlock]

class AreaSummary(BaseModel):
    center: List[int]
    radius: int
    format: str
    total_blocks_scanned: int
    material_histogram: Dict[str, int]
    surface_material: Optional[str] = None
    ascii_slice: Optional[str] = None

class WorldInfo(BaseModel):
    dimension: str
    timeOfDay: int
    gameTime: int
    isDay: bool
    isRaining: bool
    isThundering: bool
    minY: int
    height: int

