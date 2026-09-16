from pydantic import BaseModel
from typing import List

class ServerStatus(BaseModel):
    connected: bool
    minecraft_version: str
    tps: float
    mspt: float
    player_count: int
    max_players: int
    players: List[str]

