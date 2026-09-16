import os
import json
from typing import Optional, Dict, Any, AsyncIterator
import httpx
import websockets

from minecraft_mcp.models import (
    ServerStatus,
    PlayerStatus,
    PlayerPosition,
    PlayerInventory,
    BlockInfo,
    WorldInfo,
    NearbyEntitiesResponse,
)
from minecraft_mcp.models.world import AreaBlocksResponse

class BridgeError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message

class BridgeClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        ws_url: Optional[str] = None,
        timeout: float = 5.0,
    ):
        self.base_url = (base_url or os.getenv("FABRIC_BRIDGE_URL", "http://127.0.0.1:25585")).rstrip("/")
        self.ws_url = ws_url or os.getenv("FABRIC_WS_URL", "ws://127.0.0.1:25585/api/v1/ws/player")
        self.timeout = timeout

    async def _request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.request(method, url, params=params, json=json_data)
            except httpx.ConnectError:
                raise BridgeError("NOT_CONNECTED", f"Could not connect to Fabric Bridge at {self.base_url}")
            except httpx.TimeoutException:
                raise BridgeError("TIMEOUT", f"Bridge request to {endpoint} timed out after {self.timeout}s")

        try:
            data = response.json()
        except Exception:
            raise BridgeError("INVALID_RESPONSE", f"Non-JSON response from server (status {response.status_code}): {response.text[:200]}")

        if not data.get("success", False):
            err = data.get("error") or {}
            code = err.get("code", "BRIDGE_ERROR")
            msg = err.get("message", "Unknown bridge error occurred")
            raise BridgeError(code, msg)

        return data.get("data")

    async def get_status(self) -> ServerStatus:
        data = await self._request("GET", "/api/v1/status")
        return ServerStatus.model_validate(data)

    async def get_player_status(self, player: Optional[str] = None) -> PlayerStatus:
        params = {"player": player} if player else {}
        data = await self._request("GET", "/api/v1/player/status", params=params)
        return PlayerStatus.model_validate(data)

    async def get_player_position(self, player: Optional[str] = None) -> PlayerPosition:
        params = {"player": player} if player else {}
        data = await self._request("GET", "/api/v1/player/position", params=params)
        return PlayerPosition.model_validate(data)

    async def get_player_inventory(self, player: Optional[str] = None) -> PlayerInventory:
        params = {"player": player} if player else {}
        data = await self._request("GET", "/api/v1/player/inventory", params=params)
        return PlayerInventory.model_validate(data)

    async def get_block(self, x: int, y: int, z: int) -> BlockInfo:
        params = {"x": x, "y": y, "z": z}
        data = await self._request("GET", "/api/v1/world/block", params=params)
        return BlockInfo.model_validate(data)

    async def get_blocks(
        self,
        min_x: int, min_y: int, min_z: int,
        max_x: int, max_y: int, max_z: int,
        include_air: bool = False
    ) -> AreaBlocksResponse:
        body = {
            "min": {"x": min_x, "y": min_y, "z": min_z},
            "max": {"x": max_x, "y": max_y, "z": max_z},
            "includeAir": include_air,
        }
        data = await self._request("POST", "/api/v1/world/blocks", json_data=body)
        return AreaBlocksResponse.model_validate(data)

    async def get_entities(
        self,
        radius: float = 16.0,
        filter_type: str = "all",
        player: Optional[str] = None,
    ) -> NearbyEntitiesResponse:
        params = {"radius": radius, "type": filter_type}
        if player:
            params["player"] = player
        data = await self._request("GET", "/api/v1/world/entities", params=params)
        return NearbyEntitiesResponse.model_validate(data)

    async def get_world_info(self) -> WorldInfo:
        data = await self._request("GET", "/api/v1/world/info")
        return WorldInfo.model_validate(data)

    async def set_game_mode(self, game_mode: str = "creative", player: Optional[str] = None) -> Dict[str, Any]:
        body: Dict[str, Any] = {"gameMode": game_mode}
        if player:
            body["player"] = player
        return await self._request("POST", "/api/v1/player/gamemode", json_data=body)

    async def set_block(self, x: int, y: int, z: int, block_state: str, flags: int = 11) -> Dict[str, Any]:
        body = {
            "x": x,
            "y": y,
            "z": z,
            "blockState": block_state,
            "flags": flags,
        }
        return await self._request("POST", "/api/v1/world/set_block", json_data=body)

    async def break_block(self, x: int, y: int, z: int, drop_resources: bool = True, player: Optional[str] = None) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "x": x,
            "y": y,
            "z": z,
            "dropResources": drop_resources,
        }
        if player:
            body["player"] = player
        return await self._request("POST", "/api/v1/world/break_block", json_data=body)

    async def fill_region(
        self,
        from_x: int, from_y: int, from_z: int,
        to_x: int, to_y: int, to_z: int,
        block_state: str,
        replace_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "from": {"x": from_x, "y": from_y, "z": from_z},
            "to": {"x": to_x, "y": to_y, "z": to_z},
            "blockState": block_state,
        }
        if replace_filter:
            body["replaceFilter"] = replace_filter
        return await self._request("POST", "/api/v1/world/fill", json_data=body)

    async def interact_with_block(self, x: int, y: int, z: int, hand: str = "main_hand", player: Optional[str] = None) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "x": x,
            "y": y,
            "z": z,
            "hand": hand,
        }
        if player:
            body["player"] = player
        return await self._request("POST", "/api/v1/world/interact", json_data=body)

    async def move_player(
        self,
        x: float, y: float, z: float,
        speed: float = 1.0,
        tolerance: float = 1.0,
        player: Optional[str] = None
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "x": x,
            "y": y,
            "z": z,
            "speed": speed,
            "tolerance": tolerance,
        }
        if player:
            body["player"] = player
        return await self._request("POST", "/api/v1/player/move", json_data=body)

    async def stop_player(self, player: Optional[str] = None) -> Dict[str, Any]:
        body: Dict[str, Any] = {}
        if player:
            body["player"] = player
        return await self._request("POST", "/api/v1/player/stop", json_data=body)

    async def teleport_player(
        self,
        x: float, y: float, z: float,
        yaw: Optional[float] = None,
        pitch: Optional[float] = None,
        player: Optional[str] = None
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {"x": x, "y": y, "z": z}
        if yaw is not None:
            body["yaw"] = yaw
        if pitch is not None:
            body["pitch"] = pitch
        if player:
            body["player"] = player
        return await self._request("POST", "/api/v1/player/teleport", json_data=body)

    async def rotate_player(self, yaw: float, pitch: float, player: Optional[str] = None) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "yaw": yaw,
            "pitch": pitch,
        }
        if player:
            body["player"] = player
        return await self._request("POST", "/api/v1/player/rotate", json_data=body)

    async def select_slot(self, slot: int, player: Optional[str] = None) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "slot": slot,
        }
        if player:
            body["player"] = player
        return await self._request("POST", "/api/v1/player/select_slot", json_data=body)

    async def use_item(self, hand: str = "main_hand", player: Optional[str] = None) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "hand": hand,
        }
        if player:
            body["player"] = player
        return await self._request("POST", "/api/v1/player/use_item", json_data=body)

    async def drop_item(self, entire_stack: bool = False, player: Optional[str] = None) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "entireStack": entire_stack,
        }
        if player:
            body["player"] = player
        return await self._request("POST", "/api/v1/player/drop", json_data=body)

    async def swing_arm(self, hand: str = "main_hand", player: Optional[str] = None) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "hand": hand,
        }
        if player:
            body["player"] = player
        return await self._request("POST", "/api/v1/player/swing", json_data=body)

    async def stream_player_ticks(self, player: Optional[str] = None) -> AsyncIterator[Dict[str, Any]]:
        async with websockets.connect(self.ws_url) as ws:
            sub_msg = {"action": "subscribe"}
            if player:
                sub_msg["player"] = player
            await ws.send(json.dumps(sub_msg))

            async for message in ws:
                data = json.loads(message)
                if data.get("event") == "player_tick":
                    yield data

