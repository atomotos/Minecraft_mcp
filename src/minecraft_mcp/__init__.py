def main() -> None:
    print("Hello from minecraft-mcp!")
from .server import server, main

__all__ = ["server", "main"]
