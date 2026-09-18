"""
Sync all MCP tool schemas into Antigravity cache directory:
~/.gemini/antigravity/mcp/minecraft/
"""

import asyncio
import json
import os
from pathlib import Path
from minecraft_mcp.server import server

CACHE_DIR = Path("/Users/arhamowais/.gemini/antigravity/mcp/minecraft")

async def sync_schemas():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tools = await server.list_tools()
    print(f"Syncing {len(tools)} tool schemas to {CACHE_DIR}...")

    for t in tools:
        schema = {
            "name": t.name,
            "description": t.description,
            "parameters": getattr(t, "input_schema", getattr(t, "inputSchema", {})),
        }
        dest = CACHE_DIR / f"{t.name}.json"
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(schema, f, separators=(",", ":"))
        print(f"  ✓ {t.name}.json")

    print("Sync complete!")

if __name__ == "__main__":
    asyncio.run(sync_schemas())
