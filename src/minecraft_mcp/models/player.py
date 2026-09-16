from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Vec3Pos(BaseModel):
    x: float
    y: float
    z: float

class BlockPos(BaseModel):
    x: int
    y: int
    z: int

class Rotation(BaseModel):
    yaw: float
    pitch: float
    headYaw: float

class ItemSlot(BaseModel):
    id: str
    count: int

class InventorySlot(BaseModel):
    slot: int
    id: str
    count: int

class PlayerStatus(BaseModel):
    uuid: str
    name: str
    position: Vec3Pos
    blockPosition: BlockPos
    rotation: Rotation
    health: float
    maxHealth: float
    food: int
    saturation: float
    gameMode: str
    dimension: str
    selectedSlot: int
    heldItem: Optional[ItemSlot] = None

class PlayerPosition(BaseModel):
    x: float
    y: float
    z: float
    yaw: float
    pitch: float
    headYaw: float

class PlayerInventory(BaseModel):
    selectedSlot: int
    hotbar: List[InventorySlot]
    main: List[InventorySlot]
    armor: Dict[str, Optional[ItemSlot]]
    offhand: Optional[ItemSlot] = None

