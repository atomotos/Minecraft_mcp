"""
Geometry Rasterizer: Converts continuous and composite Geometry IR nodes into discrete 3D VoxelSpace.
Implements analytical voxelization, Signed Distance Field (SDF) bounds, Point-in-Polygon, and CSG evaluation.
"""

import math
from typing import Dict, Any, List, Tuple, Optional
from minecraft_mcp.procedural.ir import (
    GeometryNode,
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
    LoftNode,
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
from minecraft_mcp.procedural.voxel_space import VoxelSpace
from minecraft_mcp.procedural.transform import transform_voxel_space, transform_point

class GeometryRasterizer:
    """Analytical 3D rasterization compiler for Geometry IR."""

    def __init__(self, template_registry: Optional[Dict[str, Dict[str, Any]]] = None):
        self.templates = template_registry or {}

    def rasterize(self, node_or_spec: Any) -> VoxelSpace:
        """Main entry point: rasterizes any GeometryNode into a discrete VoxelSpace."""
        node = parse_geometry_spec(node_or_spec)
        space = VoxelSpace()

        # 1. Dispatch based on node type
        if isinstance(node, BoxNode):
            self._rasterize_box(node, space)
        elif isinstance(node, PlaneNode):
            self._rasterize_plane(node, space)
        elif isinstance(node, CylinderNode):
            self._rasterize_cylinder(node, space)
        elif isinstance(node, SphereNode):
            self._rasterize_sphere(node, space)
        elif isinstance(node, EllipsoidNode):
            self._rasterize_ellipsoid(node, space)
        elif isinstance(node, CircleNode):
            self._rasterize_circle(node, space)
        elif isinstance(node, RingNode):
            self._rasterize_ring(node, space)
        elif isinstance(node, ArcNode):
            self._rasterize_arc(node, space)
        elif isinstance(node, EllipseNode):
            self._rasterize_ellipse(node, space)
        elif isinstance(node, EllipseRingNode):
            self._rasterize_ellipse_ring(node, space)
        elif isinstance(node, PolygonNode):
            self._rasterize_polygon(node, space)
        elif isinstance(node, ExtrusionNode):
            self._rasterize_extrusion(node, space)
        elif isinstance(node, LoftNode):
            self._rasterize_loft(node, space)
        elif isinstance(node, CSGUnionNode):
            self._rasterize_union(node, space)
        elif isinstance(node, CSGSubtractNode):
            self._rasterize_subtract(node, space)
        elif isinstance(node, CSGIntersectNode):
            self._rasterize_intersect(node, space)
        elif isinstance(node, RadialArrayNode):
            self._rasterize_radial_array(node, space)
        elif isinstance(node, LinearArrayNode):
            self._rasterize_linear_array(node, space)
        elif isinstance(node, GridArrayNode):
            self._rasterize_grid_array(node, space)
        elif isinstance(node, StackNode):
            self._rasterize_stack(node, space)
        elif isinstance(node, TemplateInstanceNode):
            self._rasterize_instance(node, space)
        else:
            # Architectural or custom node fallback
            from minecraft_mcp.procedural.architectural import rasterize_architectural_primitive
            arch_space = rasterize_architectural_primitive(node, self)
            space.merge(arch_space)

        # 2. Apply node-level affine transformation if present
        if node.transform:
            space = transform_voxel_space(space, node.transform)

        return space

    # -----------------------------------------------------------------------
    # Basic Mathematical Primitives
    # -----------------------------------------------------------------------

    def _rasterize_box(self, node: BoxNode, space: VoxelSpace) -> None:
        min_x = int(math.floor(min(node.min_pt[0], node.max_pt[0])))
        max_x = int(math.ceil(max(node.min_pt[0], node.max_pt[0])))
        min_y = int(math.floor(min(node.min_pt[1], node.max_pt[1])))
        max_y = int(math.ceil(max(node.min_pt[1], node.max_pt[1])))
        min_z = int(math.floor(min(node.min_pt[2], node.max_pt[2])))
        max_z = int(math.ceil(max(node.min_pt[2], node.max_pt[2])))

        thick = node.wall_thickness
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                for z in range(min_z, max_z + 1):
                    if node.hollow:
                        on_boundary = (
                            (x - min_x < thick or max_x - x < thick) or
                            (y - min_y < thick or max_y - y < thick) or
                            (z - min_z < thick or max_z - z < thick)
                        )
                        if not on_boundary:
                            continue
                    space.set_voxel(x, y, z, node.material)

    def _rasterize_plane(self, node: PlaneNode, space: VoxelSpace) -> None:
        ox, oy, oz = int(round(node.origin[0])), int(round(node.origin[1])), int(round(node.origin[2]))
        w, d = node.width, node.depth
        if node.plane == "XZ":
            for x in range(ox, ox + w):
                for z in range(oz, oz + d):
                    space.set_voxel(x, oy, z, node.material)
        elif node.plane == "XY":
            for x in range(ox, ox + w):
                for y in range(oy, oy + d):
                    space.set_voxel(x, y, oz, node.material)
        elif node.plane == "YZ":
            for y in range(oy, oy + w):
                for z in range(oz, oz + d):
                    space.set_voxel(ox, y, z, node.material)

    def _rasterize_cylinder(self, node: CylinderNode, space: VoxelSpace) -> None:
        cx, cy, cz = node.center[0], node.center[1], node.center[2]
        r = node.radius
        r_sq = r * r
        inner_r_sq = max(0.0, (r - node.wall_thickness)) ** 2 if node.hollow else 0.0

        r_ceil = int(math.ceil(r))
        h = node.height
        if node.axis == "Y":
            base_y = int(round(cy))
            for y in range(base_y, base_y + h):
                for dx in range(-r_ceil, r_ceil + 1):
                    for dz in range(-r_ceil, r_ceil + 1):
                        dist_sq = dx * dx + dz * dz
                        if dist_sq <= r_sq + 0.25:
                            if node.hollow and dist_sq < inner_r_sq:
                                continue
                            space.set_voxel(int(round(cx + dx)), y, int(round(cz + dz)), node.material)

    def _rasterize_sphere(self, node: SphereNode, space: VoxelSpace) -> None:
        cx, cy, cz = node.center[0], node.center[1], node.center[2]
        r = node.radius
        r_sq = r * r
        inner_r_sq = max(0.0, (r - node.wall_thickness)) ** 2 if node.hollow else 0.0
        r_ceil = int(math.ceil(r))

        for dx in range(-r_ceil, r_ceil + 1):
            for dy in range(-r_ceil, r_ceil + 1):
                for dz in range(-r_ceil, r_ceil + 1):
                    dist_sq = dx * dx + dy * dy + dz * dz
                    if dist_sq <= r_sq + 0.25:
                        if node.hollow and dist_sq < inner_r_sq:
                            continue
                        space.set_voxel(int(round(cx + dx)), int(round(cy + dy)), int(round(cz + dz)), node.material)

    def _rasterize_ellipsoid(self, node: EllipsoidNode, space: VoxelSpace) -> None:
        cx, cy, cz = node.center[0], node.center[1], node.center[2]
        rx, ry, rz = max(0.1, node.radii[0]), max(0.1, node.radii[1]), max(0.1, node.radii[2])
        ix_ceil, iy_ceil, iz_ceil = int(math.ceil(rx)), int(math.ceil(ry)), int(math.ceil(rz))

        inner_rx = max(0.1, rx - node.wall_thickness)
        inner_ry = max(0.1, ry - node.wall_thickness)
        inner_rz = max(0.1, rz - node.wall_thickness)

        for dx in range(-ix_ceil, ix_ceil + 1):
            for dy in range(-iy_ceil, iy_ceil + 1):
                for dz in range(-iz_ceil, iz_ceil + 1):
                    val = (dx * dx) / (rx * rx) + (dy * dy) / (ry * ry) + (dz * dz) / (rz * rz)
                    if val <= 1.05:
                        if node.hollow:
                            inner_val = (dx * dx) / (inner_rx * inner_rx) + (dy * dy) / (inner_ry * inner_ry) + (dz * dz) / (inner_rz * inner_rz)
                            if inner_val < 0.95:
                                continue
                        space.set_voxel(int(round(cx + dx)), int(round(cy + dy)), int(round(cz + dz)), node.material)

    # -----------------------------------------------------------------------
    # Circular & Planar Curves
    # -----------------------------------------------------------------------

    def _rasterize_circle(self, node: CircleNode, space: VoxelSpace) -> None:
        cx, cy, cz = node.center[0], node.center[1], node.center[2]
        r = node.radius
        r_sq = r * r
        inner_sq = max(0.0, (r - node.thickness)) ** 2 if not node.filled else 0.0
        r_ceil = int(math.ceil(r))

        for dx in range(-r_ceil, r_ceil + 1):
            for dz in range(-r_ceil, r_ceil + 1):
                d_sq = dx * dx + dz * dz
                if d_sq <= r_sq + 0.25:
                    if not node.filled and d_sq < inner_sq:
                        continue
                    space.set_voxel(int(round(cx + dx)), int(round(cy)), int(round(cz + dz)), node.material)

    def _rasterize_ring(self, node: RingNode, space: VoxelSpace) -> None:
        cx, cy, cz = node.center[0], node.center[1], node.center[2]
        outer_sq = node.outer_radius ** 2
        inner_sq = node.inner_radius ** 2
        r_ceil = int(math.ceil(node.outer_radius))

        base_y = int(round(cy))
        for y in range(base_y, base_y + node.height):
            for dx in range(-r_ceil, r_ceil + 1):
                for dz in range(-r_ceil, r_ceil + 1):
                    d_sq = dx * dx + dz * dz
                    if inner_sq <= d_sq <= outer_sq + 0.25:
                        space.set_voxel(int(round(cx + dx)), y, int(round(cz + dz)), node.material)

    def _rasterize_arc(self, node: ArcNode, space: VoxelSpace) -> None:
        cx, cy, cz = node.center[0], node.center[1], node.center[2]
        r = node.radius
        r_min = max(0.0, r - (node.thickness / 2.0))
        r_max = r + (node.thickness / 2.0)
        min_sq = r_min ** 2
        max_sq = r_max ** 2
        r_ceil = int(math.ceil(r_max))

        # Normalize angles to [0, 360)
        s_ang = node.start_angle % 360.0
        e_ang = node.end_angle % 360.0
        spans_zero = s_ang > e_ang

        base_y = int(round(cy))
        for y in range(base_y, base_y + node.height):
            for dx in range(-r_ceil, r_ceil + 1):
                for dz in range(-r_ceil, r_ceil + 1):
                    d_sq = dx * dx + dz * dz
                    if min_sq <= d_sq <= max_sq + 0.25:
                        ang = math.degrees(math.atan2(dz, dx)) % 360.0
                        in_arc = (s_ang <= ang <= e_ang) if not spans_zero else (ang >= s_ang or ang <= e_ang)
                        if in_arc:
                            space.set_voxel(int(round(cx + dx)), y, int(round(cz + dz)), node.material)

    def _rasterize_ellipse(self, node: EllipseNode, space: VoxelSpace) -> None:
        cx, cy, cz = node.center[0], node.center[1], node.center[2]
        rx, rz = max(0.1, node.radius_x), max(0.1, node.radius_z)
        ix_ceil, iz_ceil = int(math.ceil(rx)), int(math.ceil(rz))

        base_y = int(round(cy))
        for y in range(base_y, base_y + node.height):
            for dx in range(-ix_ceil, ix_ceil + 1):
                for dz in range(-iz_ceil, iz_ceil + 1):
                    if (dx * dx) / (rx * rx) + (dz * dz) / (rz * rz) <= 1.05:
                        space.set_voxel(int(round(cx + dx)), y, int(round(cz + dz)), node.material)

    def _rasterize_ellipse_ring(self, node: EllipseRingNode, space: VoxelSpace) -> None:
        cx, cy, cz = node.center[0], node.center[1], node.center[2]
        orx, orz = max(0.1, node.outer_rx), max(0.1, node.outer_rz)
        irx, irz = max(0.1, node.inner_rx), max(0.1, node.inner_rz)
        ix_ceil, iz_ceil = int(math.ceil(orx)), int(math.ceil(orz))

        base_y = int(round(cy))
        for y in range(base_y, base_y + node.height):
            for dx in range(-ix_ceil, ix_ceil + 1):
                for dz in range(-iz_ceil, iz_ceil + 1):
                    outer_val = (dx * dx) / (orx * orx) + (dz * dz) / (orz * orz)
                    inner_val = (dx * dx) / (irx * irx) + (dz * dz) / (irz * irz)
                    if inner_val >= 0.95 and outer_val <= 1.05:
                        space.set_voxel(int(round(cx + dx)), y, int(round(cz + dz)), node.material)

    # -----------------------------------------------------------------------
    # Profiles, Extrusion & Lofting
    # -----------------------------------------------------------------------

    def _point_in_polygon(self, px: float, pz: float, vertices: List[List[float]]) -> bool:
        """Ray-casting algorithm for point-in-polygon inclusion."""
        inside = False
        n = len(vertices)
        if n < 3:
            return False
        j = n - 1
        for i in range(n):
            xi, zi = vertices[i][0], vertices[i][1]
            xj, zj = vertices[j][0], vertices[j][1]
            if ((zi > pz) != (zj > pz)) and (px < (xj - xi) * (pz - zi) / (zj - zi + 1e-9) + xi):
                inside = not inside
            j = i
        return inside

    def _rasterize_polygon(self, node: PolygonNode, space: VoxelSpace) -> None:
        if not node.vertices:
            return
        xs = [v[0] for v in node.vertices]
        zs = [v[1] for v in node.vertices]
        min_x, max_x = int(math.floor(min(xs))), int(math.ceil(max(xs)))
        min_z, max_z = int(math.floor(min(zs))), int(math.ceil(max(zs)))

        base_y = int(round(node.base_y))
        for y in range(base_y, base_y + node.height):
            for x in range(min_x, max_x + 1):
                for z in range(min_z, max_z + 1):
                    if self._point_in_polygon(x + 0.5, z + 0.5, node.vertices):
                        space.set_voxel(x, y, z, node.material)

    def _rasterize_extrusion(self, node: ExtrusionNode, space: VoxelSpace) -> None:
        # Rasterize base 2D profile at Y=0
        base_node = parse_geometry_spec(node.profile)
        base_space = self.rasterize(base_node)

        # Extrude along vector steps
        dx, dy, dz = node.vector
        steps = max(1, int(round(math.sqrt(dx * dx + dy * dy + dz * dz))))
        step_x = dx / steps
        step_y = dy / steps
        step_z = dz / steps

        for s in range(steps + 1):
            cur_ox = int(round(s * step_x))
            cur_oy = int(round(s * step_y))
            cur_oz = int(round(s * step_z))
            space.merge(base_space, offset=(cur_ox, cur_oy, cur_oz))

    def _rasterize_loft(self, node: LoftNode, space: VoxelSpace) -> None:
        """Continuous vertical cross-section lofting between multi-level profiles."""
        if len(node.layers) < 2:
            return

        sorted_layers = sorted(node.layers, key=lambda l: l.y)
        cx, cz = node.base_center[0], node.base_center[2]

        for i in range(len(sorted_layers) - 1):
            l0 = sorted_layers[i]
            l1 = sorted_layers[i + 1]

            y_start = int(round(l0.y))
            y_end = int(round(l1.y))
            if y_end <= y_start:
                continue

            r0 = l0.radius if l0.radius is not None else 5.0 * l0.scale
            r1 = l1.radius if l1.radius is not None else 5.0 * l1.scale

            for y in range(y_start, y_end + (1 if i == len(sorted_layers) - 2 else 0)):
                t = (y - y_start) / float(y_end - y_start)
                curr_r = (1.0 - t) * r0 + t * r1
                curr_rot = (1.0 - t) * l0.rotation + t * l1.rotation
                shape = l0.shape

                r_sq = curr_r * curr_r
                inner_r_sq = max(0.0, curr_r - node.wall_thickness) ** 2 if node.hollow else 0.0
                r_ceil = int(math.ceil(curr_r))

                for dx in range(-r_ceil, r_ceil + 1):
                    for dz in range(-r_ceil, r_ceil + 1):
                        if shape == "circle":
                            d_sq = dx * dx + dz * dz
                            if d_sq <= r_sq + 0.25:
                                if node.hollow and d_sq < inner_r_sq:
                                    continue
                                space.set_voxel(int(round(cx + dx)), y, int(round(cz + dz)), node.material)
                        elif shape == "square":
                            # Square setback with optional rotation
                            rx, rz = dx, dz
                            if curr_rot != 0.0:
                                rad = math.radians(-curr_rot)
                                rx = dx * math.cos(rad) - dz * math.sin(rad)
                                rz = dx * math.sin(rad) + dz * math.cos(rad)
                            if abs(rx) <= curr_r and abs(rz) <= curr_r:
                                if node.hollow and (abs(rx) < curr_r - node.wall_thickness and abs(rz) < curr_r - node.wall_thickness):
                                    continue
                                space.set_voxel(int(round(cx + dx)), y, int(round(cz + dz)), node.material)

    # -----------------------------------------------------------------------
    # CSG Booleans
    # -----------------------------------------------------------------------

    def _rasterize_union(self, node: CSGUnionNode, space: VoxelSpace) -> None:
        for child_spec in node.children:
            child_space = self.rasterize(child_spec)
            space.merge(child_space)

    def _rasterize_subtract(self, node: CSGSubtractNode, space: VoxelSpace) -> None:
        base_space = self.rasterize(node.base)
        for subtrahend_spec in node.subtrahends:
            subtrahend_space = self.rasterize(subtrahend_spec)
            base_space.subtract(subtrahend_space)
        space.merge(base_space)

    def _rasterize_intersect(self, node: CSGIntersectNode, space: VoxelSpace) -> None:
        if not node.children:
            return
        master_space = self.rasterize(node.children[0])
        for child_spec in node.children[1:]:
            child_space = self.rasterize(child_spec)
            master_space.intersect(child_space)
        space.merge(master_space)

    # -----------------------------------------------------------------------
    # Repetition Arrays
    # -----------------------------------------------------------------------

    def _rasterize_radial_array(self, node: RadialArrayNode, space: VoxelSpace) -> None:
        child_node = parse_geometry_spec(node.child)
        base_child_space = self.rasterize(child_node)

        count = max(1, node.count)
        step_angle = node.arc_angle / count
        cx, cy, cz = node.center[0], node.center[1], node.center[2]
        r = node.radius

        for i in range(count):
            ang_deg = node.start_angle + i * step_angle
            rad = math.radians(ang_deg)
            # Center offset
            dx = r * math.cos(rad)
            dz = r * math.sin(rad)

            # Rotation
            rot_y = 0.0
            if node.orient == "tangent":
                rot_y = -ang_deg + 90.0
            elif node.orient == "radial":
                rot_y = -ang_deg

            # Transform child space
            from minecraft_mcp.procedural.ir import TransformSpec
            t_spec = TransformSpec(
                translation=[cx + dx, cy, cz + dz],
                rotation_y=rot_y,
            )
            inst_space = transform_voxel_space(base_child_space, t_spec)
            space.merge(inst_space)

    def _rasterize_linear_array(self, node: LinearArrayNode, space: VoxelSpace) -> None:
        child_node = parse_geometry_spec(node.child)
        base_child_space = self.rasterize(child_node)

        sx, sy, sz = node.spacing[0], node.spacing[1], node.spacing[2]
        for i in range(node.count):
            offset = (int(round(i * sx)), int(round(i * sy)), int(round(i * sz)))
            space.merge(base_child_space, offset=offset)

    def _rasterize_grid_array(self, node: GridArrayNode, space: VoxelSpace) -> None:
        child_node = parse_geometry_spec(node.child)
        base_child_space = self.rasterize(child_node)

        for ix in range(node.count_x):
            for iz in range(node.count_z):
                offset = (int(round(ix * node.spacing_x)), 0, int(round(iz * node.spacing_z)))
                space.merge(base_child_space, offset=offset)

    def _rasterize_stack(self, node: StackNode, space: VoxelSpace) -> None:
        cur_y = 0
        for layer_spec in node.layers:
            layer_space = self.rasterize(layer_spec)
            bounds = layer_space.get_bounds()
            space.merge(layer_space, offset=(0, cur_y, 0))
            h = bounds["max"]["y"] - bounds["min"]["y"] + 1
            cur_y += h + int(round(node.spacing_y))

    def _rasterize_instance(self, node: TemplateInstanceNode, space: VoxelSpace) -> None:
        if node.template_name not in self.templates:
            raise ValueError(f"Template '{node.template_name}' not registered in procedural session")
        template_spec = self.templates[node.template_name].copy()
        # Parameter substitution if applicable
        inst_space = self.rasterize(template_spec)
        space.merge(inst_space)

