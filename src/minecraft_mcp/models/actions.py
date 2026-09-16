from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class ActionStateEnum(str, Enum):
    IDLE = "IDLE"
    MOVING = "MOVING"
    BUILDING = "BUILDING"
    MINING = "MINING"
    INTERACTING = "INTERACTING"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"

class StructuredActionResult(BaseModel):
    success: bool = True
    action: str
    position: Optional[Dict[str, int]] = None
    block: Optional[str] = None
    previous_block: Optional[str] = None
    current_block: Optional[str] = None
    placed: Optional[bool] = None
    destroyed: Optional[bool] = None
    verified: bool = False
    dropped_items: Optional[bool] = None
    from_pos: Optional[Dict[str, int]] = Field(default=None, alias="from")
    to_pos: Optional[Dict[str, int]] = Field(default=None, alias="to")
    volume: Optional[int] = None
    requested_count: Optional[int] = None
    placed_count: Optional[int] = None
    failed_count: Optional[int] = None
    target_block: Optional[str] = None
    interaction_type: Optional[str] = None
    state_changed: Optional[bool] = None
    bounds: Optional[Dict[str, Dict[str, int]]] = None
    tick: Optional[int] = None

class MovementResult(BaseModel):
    success: bool = True
    action: str = "move_to"
    start_position: Optional[Dict[str, float]] = None
    current_position: Optional[Dict[str, float]] = None
    target_position: Optional[Dict[str, float]] = None
    final_position: Optional[Dict[str, float]] = None
    status: str  # "reached", "moving", "stuck", "cancelled"
    distance_remaining: float = 0.0
    tick: Optional[int] = None

class ActionState(BaseModel):
    state: ActionStateEnum = ActionStateEnum.IDLE
    current_action: Optional[str] = None
    target: Optional[Dict[str, Any]] = None
    last_result: Optional[Dict[str, Any]] = None
    updated_at: Optional[str] = None

