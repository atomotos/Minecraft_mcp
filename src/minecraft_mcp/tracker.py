import datetime
import threading
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, AsyncIterator
from minecraft_mcp.models.actions import ActionState, ActionStateEnum

class ActionStateTracker:
    _instance: Optional["ActionStateTracker"] = None
    _lock = threading.Lock()

    def __init__(self):
        self._state = ActionState(
            state=ActionStateEnum.IDLE,
            current_action=None,
            target=None,
            last_result=None,
            updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat()
        )

    @classmethod
    def get_instance(cls) -> "ActionStateTracker":
        with cls._lock:
            if cls._instance is None:
                cls._instance = ActionStateTracker()
            return cls._instance

    def get_state(self) -> ActionState:
        with self._lock:
            return self._state.model_copy()

    def set_state(
        self,
        state: ActionStateEnum,
        action: Optional[str] = None,
        target: Optional[Dict[str, Any]] = None,
        last_result: Optional[Dict[str, Any]] = None
    ) -> None:
        with self._lock:
            self._state = ActionState(
                state=state,
                current_action=action,
                target=target,
                last_result=last_result if last_result is not None else self._state.last_result,
                updated_at=datetime.datetime.now(datetime.timezone.utc).isoformat()
            )

    @asynccontextmanager
    async def track(
        self,
        action: str,
        state: ActionStateEnum,
        target: Optional[Dict[str, Any]] = None
    ) -> AsyncIterator[None]:
        self.set_state(state=state, action=action, target=target)
        try:
            yield
            self.set_state(state=ActionStateEnum.IDLE, action=None, target=None)
        except Exception as e:
            self.set_state(
                state=ActionStateEnum.FAILED,
                action=action,
                target=target,
                last_result={"error": str(e)}
            )
            raise

