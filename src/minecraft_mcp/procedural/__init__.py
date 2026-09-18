"""
Procedural Construction Engine & Token-Efficient Geometry IR for Minecraft Java Edition.
Phase 4 Architecture.
"""

from minecraft_mcp.procedural.ir import (
    GeometryNode,
    TransformSpec,
    BoxNode,
    PlaneNode,
    CylinderNode,
    SphereNode,
    EllipsoidNode,
    CircleNode,
    RingNode,
    ArcNode,
    EllipseNode,
    EllipseRingNode,
    PolygonNode,
    ExtrusionNode,
    LoftLayer,
    LoftNode,
    CSGUnionNode,
    CSGSubtractNode,
    CSGIntersectNode,
    RadialArrayNode,
    LinearArrayNode,
    GridArrayNode,
    StackNode,
    ArchNode,
    ColumnNode,
    DomeNode,
    VaultNode,
    BalconyNode,
    StaircaseNode,
    parse_geometry_spec,
)
from minecraft_mcp.procedural.voxel_space import VoxelSpace
from minecraft_mcp.procedural.rasterizer import GeometryRasterizer
from minecraft_mcp.procedural.compiler import VoxelCompiler, CompiledBuildPlan
from minecraft_mcp.procedural.foundation import TerrainAdaptiveFoundationEngine
from minecraft_mcp.procedural.session import ProceduralSessionManager
from minecraft_mcp.procedural.transactions import BuildTransactionManager, CompactVerificationReport

__all__ = [
    "GeometryNode",
    "TransformSpec",
    "BoxNode",
    "PlaneNode",
    "CylinderNode",
    "SphereNode",
    "EllipsoidNode",
    "CircleNode",
    "RingNode",
    "ArcNode",
    "EllipseNode",
    "EllipseRingNode",
    "PolygonNode",
    "ExtrusionNode",
    "LoftLayer",
    "LoftNode",
    "CSGUnionNode",
    "CSGSubtractNode",
    "CSGIntersectNode",
    "RadialArrayNode",
    "LinearArrayNode",
    "GridArrayNode",
    "StackNode",
    "ArchNode",
    "ColumnNode",
    "DomeNode",
    "VaultNode",
    "BalconyNode",
    "StaircaseNode",
    "VoxelSpace",
    "GeometryRasterizer",
    "VoxelCompiler",
    "CompiledBuildPlan",
    "TerrainAdaptiveFoundationEngine",
    "ProceduralSessionManager",
    "BuildTransactionManager",
    "CompactVerificationReport",
    "parse_geometry_spec",
    "TEMPLATES_METADATA",
    "register_builtin_templates",
    "get_template_catalog",
    "build_template_spec",
]

from minecraft_mcp.procedural.templates_library import (
    TEMPLATES_METADATA,
    register_builtin_templates,
    get_template_catalog,
    build_template_spec,
)
