from enum import Enum
from typing import Dict, Any, Optional
import datetime
from pydantic import BaseModel, Field

class AgentEventType(str, Enum):
    PLAYER_MOVED = "PlayerMoved"
    BLOCK_CHANGED = "BlockChanged"
    ACTION_COMPLETED = "ActionCompleted"
    ACTION_FAILED = "ActionFailed"
    RESOURCE_SHORTAGE = "ResourceShortage"
    CONSTRUCTION_COMPONENT_COMPLETED = "ConstructionComponentCompleted"
    CONSTRUCTION_FAILED = "ConstructionFailed"
    CONSTRUCTION_RECOVERED = "ConstructionRecovered"
    CONSTRUCTION_COMPLETED = "ConstructionCompleted"
    PLAYER_STUCK = "PlayerStuck"

class AgentEvent(BaseModel):
    type: AgentEventType
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    payload: Dict[str, Any] = Field(default_factory=dict)
    requires_decision: bool = False

