"""
Geometry Intermediate Representation (Geometry IR) for Minecraft Procedural Construction.
Declarative, composable Abstract Syntax Tree (AST) representing continuous and discrete 3D spatial volumes.
"""

from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field

class TransformSpec(BaseModel):
    """Affine transformation specification applied to a geometry node."""
    translation: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    rotation_y: float = Field(default=0.0, description="Yaw rotation around Y axis in degrees")
    rotation_x: float = Field(default=0.0, description="Pitch rotation around X axis in degrees")
    rotation_z: float = Field(default=0.0, description="Roll rotation around Z axis in degrees")
    scale: List[float] = Field(default_factory=lambda: [1.0, 1.0, 1.0])
    mirror: Optional[Literal["X", "Y", "Z"]] = Field(default=None, description="Axis to mirror across")

class GeometryNode(BaseModel):
    """Base class for all procedural geometry AST nodes."""
    id: Optional[str] = None
    type: str
    material: str = "minecraft:stone"
    transform: Optional[TransformSpec] = None

# ---------------------------------------------------------------------------
# Basic Mathematical Primitives
# ---------------------------------------------------------------------------

class BoxNode(GeometryNode):
    type: Literal["box"] = "box"
    min_pt: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    max_pt: List[float] = Field(default_factory=lambda: [1.0, 1.0, 1.0])
    hollow: bool = False
    wall_thickness: int = 1

class PlaneNode(GeometryNode):
    type: Literal["plane"] = "plane"
    origin: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    width: int = 5
    depth: int = 5
    plane: Literal["XZ", "XY", "YZ"] = "XZ"

class CylinderNode(GeometryNode):
    type: Literal["cylinder"] = "cylinder"
    center: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    radius: float = 3.0
    height: int = 5
    axis: Literal["X", "Y", "Z"] = "Y"
    hollow: bool = False
    wall_thickness: int = 1

class SphereNode(GeometryNode):
    type: Literal["sphere"] = "sphere"
    center: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    radius: float = 4.0
    hollow: bool = False
    wall_thickness: int = 1

class EllipsoidNode(GeometryNode):
    type: Literal["ellipsoid"] = "ellipsoid"
    center: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    radii: List[float] = Field(default_factory=lambda: [4.0, 6.0, 4.0])
    hollow: bool = False
    wall_thickness: int = 1

# ---------------------------------------------------------------------------
# Circular & Planar Curves
# ---------------------------------------------------------------------------

class CircleNode(GeometryNode):
    type: Literal["circle"] = "circle"
    center: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    radius: float = 5.0
    plane: Literal["XZ", "XY", "YZ"] = "XZ"
    filled: bool = True
    thickness: int = 1

class RingNode(GeometryNode):
    type: Literal["ring"] = "ring"
    center: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    outer_radius: float = 6.0
    inner_radius: float = 4.0
    height: int = 1
    plane: Literal["XZ", "XY", "YZ"] = "XZ"

class ArcNode(GeometryNode):
    type: Literal["arc"] = "arc"
    center: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    radius: float = 5.0
    start_angle: float = 0.0   # in degrees
    end_angle: float = 180.0   # in degrees
    thickness: int = 1
    height: int = 1
    plane: Literal["XZ", "XY", "YZ"] = "XZ"

class EllipseNode(GeometryNode):
    type: Literal["ellipse"] = "ellipse"
    center: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    radius_x: float = 6.0
    radius_z: float = 4.0
    height: int = 1
    filled: bool = True

class EllipseRingNode(GeometryNode):
    type: Literal["ellipse_ring"] = "ellipse_ring"
    center: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    outer_rx: float = 8.0
    outer_rz: float = 6.0
    inner_rx: float = 6.0
    inner_rz: float = 4.0
    height: int = 1

# ---------------------------------------------------------------------------
# Profiles, Extrusion & Lofting
# ---------------------------------------------------------------------------

class PolygonNode(GeometryNode):
    type: Literal["polygon"] = "polygon"
    vertices: List[List[float]] = Field(default_factory=list, description="List of [x, z] 2D coordinates")
    height: int = 1
    base_y: float = 0.0
    filled: bool = True

class ExtrusionNode(GeometryNode):
    type: Literal["extrusion"] = "extrusion"
    profile: Dict[str, Any] = Field(default_factory=dict, description="2D profile spec or polygon")
    vector: List[float] = Field(default_factory=lambda: [0.0, 10.0, 0.0])
    hollow: bool = False
    wall_thickness: int = 1

class LoftLayer(BaseModel):
    y: float
    radius: Optional[float] = None
    scale: float = 1.0
    rotation: float = 0.0
    shape: str = "circle"  # "circle", "square", "octagon"

class LoftNode(GeometryNode):
    type: Literal["loft"] = "loft"
    base_center: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    layers: List[LoftLayer] = Field(default_factory=list)
    hollow: bool = True
    wall_thickness: int = 1

# ---------------------------------------------------------------------------
# CSG Booleans
# ---------------------------------------------------------------------------

class CSGUnionNode(GeometryNode):
    type: Literal["union"] = "union"
    children: List[Dict[str, Any]] = Field(default_factory=list)

class CSGSubtractNode(GeometryNode):
    type: Literal["subtract"] = "subtract"
    base: Dict[str, Any] = Field(default_factory=dict)
    subtrahends: List[Dict[str, Any]] = Field(default_factory=list)

class CSGIntersectNode(GeometryNode):
    type: Literal["intersect"] = "intersect"
    children: List[Dict[str, Any]] = Field(default_factory=list)

# ---------------------------------------------------------------------------
# Repetition & Arrays
# ---------------------------------------------------------------------------

class RadialArrayNode(GeometryNode):
    type: Literal["radial_array"] = "radial_array"
    child: Dict[str, Any] = Field(default_factory=dict)
    count: int = 8
    radius: float = 10.0
    center: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    orient: Literal["tangent", "radial", "none"] = "tangent"
    start_angle: float = 0.0
    arc_angle: float = 360.0

class LinearArrayNode(GeometryNode):
    type: Literal["linear_array"] = "linear_array"
    child: Dict[str, Any] = Field(default_factory=dict)
    count: int = 5
    spacing: List[float] = Field(default_factory=lambda: [3.0, 0.0, 0.0])

class GridArrayNode(GeometryNode):
    type: Literal["grid_array"] = "grid_array"
    child: Dict[str, Any] = Field(default_factory=dict)
    count_x: int = 3
    count_z: int = 3
    spacing_x: float = 4.0
    spacing_z: float = 4.0

class StackNode(GeometryNode):
    type: Literal["stack"] = "stack"
    layers: List[Dict[str, Any]] = Field(default_factory=list)
    spacing_y: float = 0.0

class TemplateInstanceNode(GeometryNode):
    type: Literal["instance"] = "instance"
    template_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)

# ---------------------------------------------------------------------------
# Architectural Primitives Layer
# ---------------------------------------------------------------------------

class ArchNode(GeometryNode):
    type: Literal["arch"] = "arch"
    style: Literal["roman_round", "gothic_pointed", "islamic_horseshoe", "segmental"] = "roman_round"
    width: int = 6
    height: int = 8
    depth: int = 1
    keystone: bool = True
    pillar_material: Optional[str] = None

class ColumnNode(GeometryNode):
    type: Literal["column"] = "column"
    style: Literal["classical", "fluted", "smooth"] = "classical"
    radius: float = 0.8
    height: int = 6
    fluted: bool = False
    capital: bool = True
    base: bool = True
    capital_material: Optional[str] = None
    base_material: Optional[str] = None

class DomeNode(GeometryNode):
    type: Literal["dome"] = "dome"
    style: Literal["hemisphere", "onion", "coffered", "saucer"] = "hemisphere"
    radius: float = 6.0
    height: Optional[float] = None
    oculus: bool = False
    finial: bool = True
    finial_material: str = "minecraft:gold_block"

class VaultNode(GeometryNode):
    type: Literal["vault"] = "vault"
    style: Literal["barrel", "groin", "ribbed"] = "barrel"
    width: int = 7
    depth: int = 10
    height: int = 5

class BalconyNode(GeometryNode):
    type: Literal["balcony"] = "balcony"
    width: int = 5
    depth: int = 3
    railing_material: str = "minecraft:iron_bars"
    corbel_material: Optional[str] = None

class StaircaseNode(GeometryNode):
    type: Literal["staircase"] = "staircase"
    style: Literal["spiral", "straight", "double"] = "spiral"
    radius: float = 3.0
    height: int = 8
    step_material: str = "minecraft:stone_stairs"
    central_pillar_material: str = "minecraft:stone_bricks"

NODE_TYPE_MAP = {
    "box": BoxNode,
    "plane": PlaneNode,
    "cylinder": CylinderNode,
    "sphere": SphereNode,
    "ellipsoid": EllipsoidNode,
    "circle": CircleNode,
    "ring": RingNode,
    "arc": ArcNode,
    "ellipse": EllipseNode,
    "ellipse_ring": EllipseRingNode,
    "polygon": PolygonNode,
    "extrusion": ExtrusionNode,
    "loft": LoftNode,
    "union": CSGUnionNode,
    "subtract": CSGSubtractNode,
    "intersect": CSGIntersectNode,
    "radial_array": RadialArrayNode,
    "linear_array": LinearArrayNode,
    "grid_array": GridArrayNode,
    "stack": StackNode,
    "instance": TemplateInstanceNode,
    "arch": ArchNode,
    "column": ColumnNode,
    "dome": DomeNode,
    "vault": VaultNode,
    "balcony": BalconyNode,
    "staircase": StaircaseNode,
}

def parse_geometry_spec(data: Union[GeometryNode, Dict[str, Any]]) -> GeometryNode:
    """Parses a dictionary spec into its typed GeometryNode AST model."""
    if isinstance(data, GeometryNode):
        return data
    if not isinstance(data, dict):
        raise ValueError(f"Expected dict for geometry spec, got {type(data)}")
    
    node_type = data.get("type", "box").lower()
    cls = NODE_TYPE_MAP.get(node_type)
    if not cls:
        raise ValueError(f"Unknown geometry node type: '{node_type}'. Supported types: {list(NODE_TYPE_MAP.keys())}")
    return cls.model_validate(data)

