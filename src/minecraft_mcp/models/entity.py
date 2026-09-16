from pydantic import BaseModel
from typing import List, Optional, Dict

class EntityInfo(BaseModel):
    id: int
    uuid: str
    type: str
    position: Dict[str, float]
    distance: float
    isAlive: bool
    health: Optional[float] = None
    maxHealth: Optional[float] = None

class NearbyEntitiesResponse(BaseModel):
    entities: List[EntityInfo]

