import re
from typing import Dict, Any, List, Tuple

MIN_Y = -64
MAX_Y = 320
MAX_BATCH_SIZE = 500
MAX_VOLUME = 500

BLOCK_ID_PATTERN = re.compile(r"^(?:[a-z0-9_.-]+:)?[a-z0-9_./-]+(?:\[[a-z0-9_.,=\-]+\])?$")

class SafetyError(ValueError):
    """Raised when an action violates deterministic safety boundaries."""
    pass

def validate_coordinates(x: int, y: int, z: int) -> None:
    """Validates that coordinates are within Minecraft world height boundaries."""
    if not (MIN_Y <= y <= MAX_Y):
        raise SafetyError(
            f"Coordinate Y={y} violates safety boundaries. Y must be between {MIN_Y} and {MAX_Y}."
        )

def validate_block_id(block: str) -> str:
    """Validates and normalizes block identifier."""
    if not block or not isinstance(block, str):
        raise SafetyError("Block identifier must be a non-empty string.")
    
    clean_block = block.strip()
    if not clean_block:
        raise SafetyError("Block identifier cannot be empty or whitespace.")

    # Auto-prefix default namespace if omitted and does not contain ':'
    if ":" not in clean_block.split("[")[0]:
        clean_block = f"minecraft:{clean_block}"

    if not BLOCK_ID_PATTERN.match(clean_block):
        raise SafetyError(f"Invalid block ID syntax: '{block}'. Must match '[namespace:]id[properties]'.")

    return clean_block

def validate_region(from_pos: Tuple[int, int, int], to_pos: Tuple[int, int, int], max_volume: int = MAX_VOLUME) -> int:
    """Validates region coordinates and calculates total volume."""
    fx, fy, fz = from_pos
    tx, ty, tz = to_pos

    validate_coordinates(fx, fy, fz)
    validate_coordinates(tx, ty, tz)

    dx = abs(tx - fx) + 1
    dy = abs(ty - fy) + 1
    dz = abs(tz - fz) + 1
    volume = dx * dy * dz

    if volume > max_volume:
        raise SafetyError(
            f"Region volume ({volume} blocks) exceeds maximum safety limit of {max_volume} blocks."
        )
    return volume

def validate_batch_placement(blocks: List[Dict[str, Any]], max_batch: int = MAX_BATCH_SIZE) -> List[Dict[str, Any]]:
    """6-Stage validation pipeline for batch block placement."""
    if not blocks:
        raise SafetyError("Block list cannot be empty.")
    if len(blocks) > max_batch:
        raise SafetyError(
            f"Batch size ({len(blocks)} blocks) exceeds maximum allowed limit of {max_batch} blocks."
        )

    validated_blocks = []
    for i, item in enumerate(blocks):
        if not isinstance(item, dict):
            raise SafetyError(f"Block at index {i} must be a dictionary with x, y, z, and block.")
        for coord in ("x", "y", "z"):
            if coord not in item:
                raise SafetyError(f"Block at index {i} is missing coordinate '{coord}'.")
            if not isinstance(item[coord], int):
                raise SafetyError(f"Block at index {i} '{coord}' must be an integer, got {type(item[coord])}.")
        if "block" not in item:
            raise SafetyError(f"Block at index {i} is missing 'block' ID.")

        x, y, z = item["x"], item["y"], item["z"]
        validate_coordinates(x, y, z)
        block_id = validate_block_id(item["block"])

        validated_blocks.append({"x": x, "y": y, "z": z, "block": block_id})

    return validated_blocks

