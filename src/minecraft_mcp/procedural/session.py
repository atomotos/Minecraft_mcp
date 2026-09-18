"""
Stateful Geometry Session and Handle Registry for Minecraft Procedural Construction.
Allows AI agents to build, mutate, and compose complex 3D architecture using compact server-side references.
"""

import uuid
import threading
from typing import Dict, Any, List, Optional
from minecraft_mcp.procedural.ir import (
    GeometryNode,
    CSGUnionNode,
    CSGSubtractNode,
    CSGIntersectNode,
    RadialArrayNode,
    LinearArrayNode,
    GridArrayNode,
    StackNode,
    TemplateInstanceNode,
    parse_geometry_spec,
)
from minecraft_mcp.procedural.rasterizer import GeometryRasterizer
from minecraft_mcp.procedural.voxel_space import VoxelSpace

class ProceduralSession:
    """Represents a stateful procedural construction workspace."""

    def __init__(self, session_id: str, name: str):
        self.session_id = session_id
        self.name = name
        self.handles: Dict[str, GeometryNode] = {}
        self.last_handle: Optional[str] = None

    def add_node(self, node: GeometryNode, handle_id: Optional[str] = None) -> str:
        hid = handle_id or f"geom_{len(self.handles) + 1}_{uuid.uuid4().hex[:6]}"
        node.id = hid
        self.handles[hid] = node
        self.last_handle = hid
        return hid

    def get_node(self, handle_id: str) -> Optional[GeometryNode]:
        return self.handles.get(handle_id)

class ProceduralSessionManager:
    """Global manager for stateful procedural geometry sessions and shared templates."""

    _instance: Optional["ProceduralSessionManager"] = None
    _lock = threading.RLock()

    def __init__(self):
        self.sessions: Dict[str, ProceduralSession] = {}
        self.templates: Dict[str, Dict[str, Any]] = {}
        from minecraft_mcp.procedural.templates_library import register_builtin_templates
        register_builtin_templates(self)

    @classmethod
    def get_instance(cls) -> "ProceduralSessionManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = ProceduralSessionManager()
            return cls._instance

    def create_session(self, name: str = "default") -> str:
        with self._lock:
            session_id = f"sess_{uuid.uuid4().hex[:8]}"
            self.sessions[session_id] = ProceduralSession(session_id, name)
            return session_id

    def get_session(self, session_id: str) -> Optional[ProceduralSession]:
        with self._lock:
            return self.sessions.get(session_id)

    def define_template(self, template_name: str, spec: Dict[str, Any]) -> str:
        """Registers a reusable architectural prefab template."""
        with self._lock:
            self.templates[template_name] = spec
            return template_name

    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self.templates.get(template_name)

    def add_primitive(self, session_id: str, spec: Dict[str, Any]) -> str:
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found")
        node = parse_geometry_spec(spec)
        return session.add_node(node)

    def compose(
        self,
        session_id: str,
        operation: str,
        handles: List[str],
        params: Optional[Dict[str, Any]] = None
    ) -> str:
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found")

        params = params or {}
        op = operation.lower()

        if op == "union":
            child_specs = [session.get_node(h).model_dump() for h in handles if session.get_node(h)]
            node = CSGUnionNode(children=child_specs)
        elif op == "subtract":
            if not handles:
                raise ValueError("Subtract operation requires at least 1 base handle")
            base_node = session.get_node(handles[0])
            if not base_node:
                raise ValueError(f"Base handle '{handles[0]}' not found")
            sub_specs = [session.get_node(h).model_dump() for h in handles[1:] if session.get_node(h)]
            node = CSGSubtractNode(base=base_node.model_dump(), subtrahends=sub_specs)
        elif op == "intersect":
            child_specs = [session.get_node(h).model_dump() for h in handles if session.get_node(h)]
            node = CSGIntersectNode(children=child_specs)
        elif op == "radial_array":
            if not handles:
                raise ValueError("radial_array requires a child handle")
            child_node = session.get_node(handles[0])
            if not child_node:
                raise ValueError(f"Handle '{handles[0]}' not found")
            node = RadialArrayNode(
                child=child_node.model_dump(),
                count=params.get("count", 8),
                radius=params.get("radius", 10.0),
                center=params.get("center", [0.0, 0.0, 0.0]),
                orient=params.get("orient", "tangent"),
                start_angle=params.get("start_angle", 0.0),
                arc_angle=params.get("arc_angle", 360.0),
            )
        elif op == "linear_array":
            if not handles:
                raise ValueError("linear_array requires a child handle")
            child_node = session.get_node(handles[0])
            node = LinearArrayNode(
                child=child_node.model_dump(),
                count=params.get("count", 5),
                spacing=params.get("spacing", [3.0, 0.0, 0.0]),
            )
        elif op == "grid_array":
            if not handles:
                raise ValueError("grid_array requires a child handle")
            child_node = session.get_node(handles[0])
            node = GridArrayNode(
                child=child_node.model_dump(),
                count_x=params.get("count_x", 3),
                count_z=params.get("count_z", 3),
                spacing_x=params.get("spacing_x", 4.0),
                spacing_z=params.get("spacing_z", 4.0),
            )
        elif op == "stack":
            child_specs = [session.get_node(h).model_dump() for h in handles if session.get_node(h)]
            node = StackNode(layers=child_specs, spacing_y=params.get("spacing_y", 0.0))
        else:
            raise ValueError(f"Unknown composition operation: '{operation}'")

        return session.add_node(node)

    def instantiate_template(
        self,
        session_id: str,
        template_name: str,
        transform: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found")
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not registered")

        from minecraft_mcp.procedural.ir import TransformSpec
        t_spec = TransformSpec.model_validate(transform) if transform else None
        node = TemplateInstanceNode(
            template_name=template_name,
            parameters=parameters or {},
            transform=t_spec,
        )
        return session.add_node(node)

    def rasterize_session(self, session_id: str, root_handle: Optional[str] = None) -> VoxelSpace:
        """Rasterizes the session's geometry into a VoxelSpace."""
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found")

        rasterizer = GeometryRasterizer(template_registry=self.templates)
        target_handle = root_handle or session.last_handle
        if not target_handle or target_handle not in session.handles:
            raise ValueError(f"No geometry nodes in session '{session_id}' to compile")

        node = session.handles[target_handle]
        return rasterizer.rasterize(node)

