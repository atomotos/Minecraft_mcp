import datetime
import math
import threading
from typing import Dict, Any, List, Optional
from minecraft_mcp.models.events import AgentEvent, AgentEventType

class EventAggregator:
    """
    Buffers high-frequency tick streams and world updates, filtering them
    into discrete, actionable AgentEvents.
    """
    _instance: Optional["EventAggregator"] = None
    _lock = threading.Lock()

    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self._events: List[AgentEvent] = []
        self._last_position: Optional[Dict[str, float]] = None

    @classmethod
    def get_instance(cls) -> "EventAggregator":
        with cls._lock:
            if cls._instance is None:
                cls._instance = EventAggregator()
            return cls._instance

    def emit(
        self,
        event_type: AgentEventType,
        payload: Optional[Dict[str, Any]] = None,
        requires_decision: bool = False,
    ) -> AgentEvent:
        """Publishes an event to the aggregator queue."""
        event = AgentEvent(
            type=event_type,
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            payload=payload or {},
            requires_decision=requires_decision,
        )
        with self._lock:
            self._events.append(event)
            if len(self._events) > self.max_history:
                self._events.pop(0)
        return event

    def process_player_tick(self, tick_data: Dict[str, Any]) -> Optional[AgentEvent]:
        """
        Filters high-frequency WebSocket player ticks. Emits a PlayerMoved event
        only when the displacement exceeds 1.0 block.
        """
        player_data = tick_data.get("data", {})
        pos = player_data.get("position", {})
        if not pos or "x" not in pos:
            return None

        curr_x = float(pos["x"])
        curr_y = float(pos["y"])
        curr_z = float(pos["z"])

        with self._lock:
            if self._last_position is None:
                self._last_position = {"x": curr_x, "y": curr_y, "z": curr_z}
                return None

            dist = math.sqrt(
                (curr_x - self._last_position["x"]) ** 2
                + (curr_y - self._last_position["y"]) ** 2
                + (curr_z - self._last_position["z"]) ** 2
            )

            if dist >= 1.0:
                self._last_position = {"x": curr_x, "y": curr_y, "z": curr_z}
                event = AgentEvent(
                    type=AgentEventType.PLAYER_MOVED,
                    payload={"position": self._last_position, "delta": round(dist, 2)},
                    requires_decision=False,
                )
                self._events.append(event)
                if len(self._events) > self.max_history:
                    self._events.pop(0)
                return event

        return None

    def get_recent_events(
        self,
        limit: int = 20,
        event_type: Optional[AgentEventType] = None,
    ) -> List[AgentEvent]:
        """Retrieves recent events matching optional filter criteria."""
        with self._lock:
            evs = [e.model_copy() for e in self._events]

        if event_type:
            evs = [e for e in evs if e.type == event_type]

        return evs[-limit:]

    def clear(self) -> None:
        """Clears all buffered events."""
        with self._lock:
            self._events.clear()
            self._last_position = None

