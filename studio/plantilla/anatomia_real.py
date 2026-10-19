"""Anatomía real (kit de Z-Anatomy) montada en la cabeza del personaje, con materiales animables.

Créditos: Z-Anatomy (CC BY-SA 4.0) y BodyParts3D, The Database Center for Life Science (CC BY-SA 2.1 JP).
Ver studio/plantilla/LICENCIAS_ANATOMIA.md.
"""
import json
import bpy, bmesh
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree


# ---------------------------------------------------------------- carga y alineación
def _eye_center(name):
    o = bpy.data.objects[name]
    dg = bpy.context.evaluated_depsgraph_get()
    oe = o.evaluated_get(dg)
    me = oe.to_mesh()
    c = sum((o.matrix_world @ v.co for v in me.vertices), Vector()) / len(me.vertices)
    oe.to_mesh_clear()
    return c


def _parent_bone(o, rig, bone):
    bpy.context.view_layer.update()
    mw = o.matrix_world.copy()
    o.parent, o.parent_type, o.parent_bone = rig, "BONE", bone
    bpy.context.view_layer.update()
    o.matrix_world = mw


def load(kit_path, rig, bone, coll, eyes=("Ojo.L", "Ojo.R"), offset=(0, 0.001, 0.001)):
    """Agrega el kit, lo alinea ojo con ojo (escala por distancia entre ojos) y lo cuelga del hueso de la cabeza."""
    meta = json.load(open(kit_path.replace(".blend", ".json")))
    with bpy.data.libraries.load(kit_path, link=False) as (src, dst):
        dst.objects = list(src.objects)
    kit = {}
    for o in dst.objects:
        coll.objects.link(o)
        kit[o.name.replace("Anat_", "")] = o
    prev = rig.data.pose_position
    rig.data.pose_position = "REST"
    bpy.context.view_layer.update()
    eL, eR = _eye_center(eyes[0]), _eye_center(eyes[1])
    E = (eL + eR) / 2
    s = (eL - eR).length / meta["distancia_ojos"]
    Ek = Vector(meta["ojos_centro"])
    T = Matrix.Translation(E + Vector(offset)) @ Matrix.Scale(s, 4) @ Matrix.Translation(-Ek)
    for o in kit.values():
        o.matrix_world = T
        _parent_bone(o, rig, bone)
    rig.data.pose_position = prev
    bpy.context.view_layer.update()
    return kit, {"E": E, "s": s, "T": T, "meta": meta}


def split_half(o):
    """Corta el objeto por el plano medio: devuelve (mitad x<0, mitad x>0) en coordenadas del atlas."""
    me2 = o.data.copy()
    o2 = o.copy()
    o2.data = me2
    o2.name = o.name + "_Izq"
    for c in o.users_collection:
        c.objects.link(o2)
    for m_, keep_neg in ((o.data, True), (me2, False)):
        bm = bmesh.new()
        bm.from_mesh(m_)
        kill = [f for f in bm.faces if (f.calc_center_median().x < 0) != keep_neg]
        bmesh.ops.delete(bm, geom=kill, context="FACES")
        bm.to_mesh(m_)
        bm.free()
    o.name = o.name + "_Der"
    return o, o2


# ---------------------------------------------------------------- materiales
def _nodes(m):
    m.use_nodes = True
    nt = m.node_tree
    return nt, nt.nodes["Principled BSDF"]


def _val(nt, name, v=0.0):
    n = nt.nodes.new("ShaderNodeValue")
    n.name = n.label = name
    n.outputs[0].default_value = v
    return n


def _math(nt, op, a, b=None):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation = op
    for i, x in enumerate((a, b)):
        if x is None:
            continue
        if isinstance(x, (int, float)):
            n.inputs[i].default_value = x
        else:
            nt.links.new(x, n.inputs[i])
    return n.outputs[0]


def _cut(nt, b, base_socket_or_col, cut_col):
    """Las caras traseras (el interior de una pieza cortada) se pintan con un color plano sin sombra,
    así el corte se lee como una sección rellena, igual que en las láminas de anatomía."""
    if isinstance(base_socket_or_col, tuple):
        b.inputs["Base Color"].default_value = (*base_socket_or_col, 1)
    else:
        nt.links.new(base_socket_or_col, b.inputs["Base Color"])
    out = nt.nodes["Material Output"]
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*cut_col, 1)
    em.inputs["Strength"].default_value = 0.85
    corte = _val(nt, "Corte", 0.0)        # 1 sólo en los planos de corte (si no, el interior de los huesos se ve plano)
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(_math(nt, "MULTIPLY", geo.outputs["Backfacing"], corte.outputs[0]), mix.inputs[0])
    nt.links.new(b.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])


def _emission(nt, b, strength_socket, color):
    b.inputs["Emission Color"].default_value = (*color, 1)
    nt.links.new(strength_socket, b.inputs["Emission Strength"])


def mat_cerebro(name, base, deep, cut=(0.80, 0.62, 0.60)):
    """Pliegues reales: los surcos más oscuros (Pointiness). Controles: 'Tibio' (naranja) y 'Activo' (amarillo)."""
    m = bpy.data.materials.new(name)
    nt, b = _nodes(m)
    b.inputs["Roughness"].default_value = 0.36
    b.inputs["Subsurface Weight"].default_value = 0.25
    b.inputs["Subsurface Radius"].default_value = (0.004, 0.002, 0.0015)
    b.inputs["Coat Weight"].default_value = 0.35
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position, ramp.color_ramp.elements[0].color = 0.42, (*deep, 1)
    ramp.color_ramp.elements[1].position, ramp.color_ramp.elements[1].color = 0.56, (*base, 1)
    nt.links.new(geo.outputs["Pointiness"], ramp.inputs["Fac"])
    _cut(nt, b, ramp.outputs["Color"], cut)
    tib, act = _val(nt, "Tibio"), _val(nt, "Activo")
    # emisión = tibio (naranja) + activo (amarillo): se mezcla el color según cuál pesa más
    mixc = nt.nodes.new("ShaderNodeMix")
    mixc.data_type = "RGBA"
    mixc.inputs["A"].default_value = (1.0, 0.42, 0.12, 1)
    mixc.inputs["B"].default_value = (1.0, 0.85, 0.2, 1)
    tot = _math(nt, "ADD", tib.outputs[0], act.outputs[0])
    nt.links.new(_math(nt, "DIVIDE", act.outputs[0], _math(nt, "MAXIMUM", tot, 1e-4)), mixc.inputs["Factor"])
    nt.links.new(mixc.outputs["Result"], b.inputs["Emission Color"])
    nt.links.new(tot, b.inputs["Emission Strength"])
    return m


def mat_simple(name, col, rough=0.4, sss=0.0, coat=0.0, cut=None, alpha=1.0):
    m = bpy.data.materials.new(name)
    nt, b = _nodes(m)
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Subsurface Weight"].default_value = sss
    b.inputs["Subsurface Radius"].default_value = (0.004, 0.002, 0.0015)
    b.inputs["Coat Weight"].default_value = coat
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
    if cut:
        _cut(nt, b, col, cut)
    return m


def mat_nervio(name, ganglio_atlas, base=(1.0, 0.70, 0.04)):
    """Nervio amarillo. Controles: 'Brillo' (todo el nervio) y 'Pulso' (distancia en m desde el ganglio de un anillo de luz)."""
    m = bpy.data.materials.new(name)
    nt, b = _nodes(m)
    b.inputs["Base Color"].default_value = (*base, 1)
    b.inputs["Roughness"].default_value = 0.35
    b.inputs["Coat Weight"].default_value = 0.4
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], sep.inputs[0])
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(_math(nt, "ABSOLUTE", sep.outputs["X"]), comb.inputs["X"])
    nt.links.new(sep.outputs["Y"], comb.inputs["Y"])
    nt.links.new(sep.outputs["Z"], comb.inputs["Z"])
    vd = nt.nodes.new("ShaderNodeVectorMath")
    vd.operation = "DISTANCE"
    nt.links.new(comb.outputs[0], vd.inputs[0])
    vd.inputs[1].default_value = (abs(ganglio_atlas[0]), ganglio_atlas[1], ganglio_atlas[2])
    br, pu = _val(nt, "Brillo", 0.25), _val(nt, "Pulso", -1.0)
    band = _math(nt, "SUBTRACT", 1.0, _math(nt, "MINIMUM", _math(nt, "DIVIDE", _math(nt, "ABSOLUTE", _math(nt, "SUBTRACT", vd.outputs["Value"], pu.outputs[0])), 0.012), 1.0))
    strength = _math(nt, "ADD", br.outputs[0], _math(nt, "MULTIPLY", band, 9.0))
    _emission(nt, b, strength, (1.0, 0.62, 0.05))
    return m


def mat_arteria(name, col=(0.78, 0.04, 0.05)):
    """Arteria roja. Control 'Late' (brillo rojo)."""
    m = bpy.data.materials.new(name)
    nt, b = _nodes(m)
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Roughness"].default_value = 0.28
    b.inputs["Subsurface Weight"].default_value = 0.2
    b.inputs["Coat Weight"].default_value = 0.6
    _emission(nt, b, _val(nt, "Late", 0.0).outputs[0], (1.0, 0.08, 0.05))
    return m


def mat_mucosa(name):
    """Paladar rosado. Controles: 'Escarcha' (0–1, cristales azules que se extienden) y 'Tibio' (brillo naranja)."""
    m = bpy.data.materials.new(name)
    nt, b = _nodes(m)
    b.inputs["Roughness"].default_value = 0.25
    b.inputs["Subsurface Weight"].default_value = 0.3
    b.inputs["Subsurface Radius"].default_value = (0.004, 0.002, 0.0015)
    b.inputs["Coat Weight"].default_value = 0.6
    esc, tib = _val(nt, "Escarcha"), _val(nt, "Tibio")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    vor = nt.nodes.new("ShaderNodeTexVoronoi")
    vor.feature = "DISTANCE_TO_EDGE"
    vor.inputs["Scale"].default_value = 260.0
    nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
    noi = nt.nodes.new("ShaderNodeTexNoise")
    noi.inputs["Scale"].default_value = 120.0
    nt.links.new(tc.outputs["Object"], noi.inputs["Vector"])
    cov = _math(nt, "GREATER_THAN", _math(nt, "ADD", esc.outputs[0], _math(nt, "MULTIPLY", _math(nt, "SUBTRACT", noi.outputs["Fac"], 0.5), 0.5)), 0.5)
    cov = _math(nt, "MULTIPLY", cov, _math(nt, "GREATER_THAN", esc.outputs[0], 0.02))
    veins = _math(nt, "SUBTRACT", 1.0, _math(nt, "MINIMUM", _math(nt, "DIVIDE", vor.outputs["Distance"], 0.06), 1.0))
    ice = nt.nodes.new("ShaderNodeMix")
    ice.data_type = "RGBA"
    ice.inputs["A"].default_value = (0.55, 0.80, 1.0, 1)
    ice.inputs["B"].default_value = (0.95, 0.98, 1.0, 1)
    nt.links.new(veins, ice.inputs["Factor"])
    mixc = nt.nodes.new("ShaderNodeMix")
    mixc.data_type = "RGBA"
    mixc.inputs["A"].default_value = (0.82, 0.30, 0.34, 1)
    nt.links.new(ice.outputs["Result"], mixc.inputs["B"])
    nt.links.new(cov, mixc.inputs["Factor"])
    _cut(nt, b, mixc.outputs["Result"], (0.70, 0.22, 0.26))
    emc = nt.nodes.new("ShaderNodeMix")
    emc.data_type = "RGBA"
    emc.inputs["A"].default_value = (0.5, 0.8, 1.0, 1)
    emc.inputs["B"].default_value = (1.0, 0.45, 0.1, 1)
    nt.links.new(_math(nt, "MINIMUM", tib.outputs[0], 1.0), emc.inputs["Factor"])
    nt.links.new(emc.outputs["Result"], b.inputs["Emission Color"])
    nt.links.new(_math(nt, "ADD", _math(nt, "MULTIPLY", cov, 0.6), _math(nt, "MULTIPLY", tib.outputs[0], 2.0)), b.inputs["Emission Strength"])
    return m


def skin_bvh(body):
    dg = bpy.context.evaluated_depsgraph_get()
    be = body.evaluated_get(dg)
    me = be.to_mesh()
    bvh = BVHTree.FromPolygons([body.matrix_world @ v.co for v in me.vertices], [list(p.vertices) for p in me.polygons])
    be.to_mesh_clear()
    return bvh


def nervio_superficial(name, rig, bone, body, guide_pts, mat, radius, coll, skin_from=2, depth=0.0035):
    """Curva de nervio que, desde el punto skin_from, se pega a la piel (bajo la superficie). Se crea en pose de descanso."""
    prev = rig.data.pose_position
    rig.data.pose_position = "REST"
    bpy.context.view_layer.update()
    bvh = skin_bvh(body)
    pts = list(guide_pts[:skin_from])
    for g in guide_pts[skin_from:]:
        loc, nor, _, _ = bvh.find_nearest(g)
        pts.append(loc - nor * depth)
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    sp = cu.splines.new("NURBS")
    sp.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        sp.points[i].co = (*p, 1)
    sp.use_endpoint_u, sp.order_u = True, 3
    cu.bevel_depth, cu.bevel_resolution, cu.use_fill_caps = radius, 3, True
    ob = bpy.data.objects.new(name, cu)
    coll.objects.link(ob)
    ob.data.materials.append(mat)
    _parent_bone(ob, rig, bone)
    rig.data.pose_position = prev
    bpy.context.view_layer.update()
    return ob


def paladar_medio(name, F, S, coll, mat, cap_mat, rig, bone, width=(0.011, 0.021, 0.018), vault=0.011, grosor=0.0045, n=18, m=8):
    """Paladar duro como sólido de media boca (x <= 0) con la cara de corte cerrada en x = 0.

    F: punto de adelante (detrás de los incisivos), S: punto de atrás (donde empieza el velo), en coordenadas de mundo en pose de descanso.
    """
    import math
    bm = bmesh.new()
    top, bot = [], []
    for i in range(n + 1):
        t = i / n
        y = F.y + (S.y - F.y) * t
        zb = F.z + (S.z - F.z) * t
        h = vault * math.sin(math.pi * min(1.0, t * 1.35)) ** 0.8          # la bóveda sube y se aplana hacia atrás
        w = width[0] + (width[1] - width[0]) * min(1, t * 2) - (width[1] - width[2]) * max(0, t - 0.5) * 2
        rt, rb = [], []
        for j in range(m + 1):
            u = j / m                      # 0 = línea media (x = 0), 1 = borde junto a los dientes
            x = -w * u
            z_top = zb + h * math.cos(u * math.pi / 2)
            rt.append(bm.verts.new((x, y, z_top)))
            rb.append(bm.verts.new((x, y, z_top - grosor * (1 - 0.5 * u))))
        top.append(rt)
        bot.append(rb)
    for i in range(n):
        for j in range(m):
            bm.faces.new((top[i][j], top[i + 1][j], top[i + 1][j + 1], top[i][j + 1]))
            bm.faces.new((bot[i][j], bot[i][j + 1], bot[i + 1][j + 1], bot[i + 1][j]))
        bm.faces.new((top[i][m], top[i + 1][m], bot[i + 1][m], bot[i][m]))
    for j in range(m):
        bm.faces.new((top[0][j], top[0][j + 1], bot[0][j + 1], bot[0][j]))
        bm.faces.new((top[n][j], bot[n][j], bot[n][j + 1], top[n][j + 1]))
    # cara de corte (x = 0): un polígono por franja para que quede plana y con su propio material
    cap_faces = []
    for i in range(n):
        f = bm.faces.new((top[i][0], bot[i][0], bot[i + 1][0], top[i + 1][0]))
        f.material_index = 1
        cap_faces.append(f)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    me.materials.append(cap_mat)
    for p in me.polygons:
        p.use_smooth = p.material_index == 0
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    _parent_bone(ob, rig, bone)
    return ob
