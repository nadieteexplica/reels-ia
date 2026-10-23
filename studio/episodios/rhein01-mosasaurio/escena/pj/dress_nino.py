"""Rhein 01 — ropa del niño pescador: impermeable amarillo largo, jeans y botas de goma verdes (adaptado de studio/personaje/dress.py: alturas desde las articulaciones del niño).

Todo se genera desde la malla del cuerpo en pose T, así la ropa hereda los pesos del cuerpo.
"""
import heapq, json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "personaje"))
import bpy
from mathutils import Vector
import escena, uvbake as ub

OUT = os.environ.get("OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"))
P = "mixamorig:"
bpy.ops.wm.open_mainfile(filepath=f"{OUT}/rigged.blend")
for n in ("CascoPelo", "Malla"):
    if n in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[n])
rig = bpy.data.objects["Rig"]
body = bpy.data.objects["Cuerpo"]
B = {b.name[len(P):]: b for b in rig.data.bones}
J = {k: np.array(v) for k, v in json.load(open(f"{OUT}/joints.json")).items()}  # cabeza y torso no cambian entre pose A y T

me = body.data
CO = np.array([v.co[:] for v in me.vertices])
NO = np.array([v.normal[:] for v in me.vertices])
EDGES = np.array([e.vertices[:] for e in me.edges])
NBR = [[] for _ in range(len(CO))]
for a, b in EDGES:
    L = float(np.linalg.norm(CO[a] - CO[b]))
    NBR[a].append((b, L))
    NBR[b].append((a, L))


def dist_from_boundary(region):
    """Distancia por la malla desde el borde de la región (Dijkstra)."""
    inr = np.zeros(len(CO), bool)
    inr[region] = True
    dist = np.full(len(CO), np.inf)
    pq = []
    for i in np.where(inr)[0]:
        if any(not inr[j] for j, _ in NBR[i]):
            dist[i] = 0.0
            pq.append((0.0, i))
    heapq.heapify(pq)
    while pq:
        d, i = heapq.heappop(pq)
        if d > dist[i]:
            continue
        for j, L in NBR[i]:
            if inr[j] and d + L < dist[j]:
                dist[j] = d + L
                heapq.heappush(pq, (d + L, j))
    dist[~inr] = -1.0
    return dist


def relax_borders(md, iters=40, pull=0.0):
    """Alisa los bordes abiertos (cuello, basta, mangas) a lo largo del borde."""
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(md)
    bverts = [v for v in bm.verts if v.is_boundary]
    nb = {v: [e.other_vert(v) for e in v.link_edges if e.is_boundary] for v in bverts}
    for _ in range(iters):
        new = {}
        for v, ns in nb.items():
            if len(ns) == 2:
                new[v] = v.co * 0.5 + (ns[0].co + ns[1].co) * 0.25
        for v, c in new.items():
            v.co = c
    # el anillo vecino sigue al borde para que no quede un escalón
    for _ in range(6):
        for v in bverts:
            for e in v.link_edges:
                w = e.other_vert(v)
                if not w.is_boundary:
                    w.co = w.co * 0.7 + (v.co + sum((x.co for x in [e2.other_vert(w) for e2 in w.link_edges]), Vector()) / max(len(w.link_edges), 1)) * 0.15
    bm.to_mesh(md)
    bm.free()


def garment(name, region, offset, smooth=(0.6, 12), thick=0.0035, mat=None):
    """Copia la región del cuerpo, la infla según 'offset' (m por vértice) y la suaviza."""
    ob = body.copy()
    ob.data = body.data.copy()
    ob.name = ob.data.name = name
    bpy.context.scene.collection.objects.link(ob)
    ob.shape_key_clear()
    for m in list(ob.modifiers):
        ob.modifiers.remove(m)
    md = ob.data
    co = CO + NO * offset[:, None]
    md.vertices.foreach_set("co", co.ravel())
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(md)
    bm.verts.ensure_lookup_table()
    keep = np.zeros(len(CO), bool)
    keep[region] = True
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not keep[v.index]], context="VERTS")
    bm.to_mesh(md)
    bm.free()
    if smooth:
        sm = ob.modifiers.new("Suave", "SMOOTH")
        sm.factor, sm.iterations = smooth
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.modifier_apply(modifier="Suave")
    relax_borders(md)
    arm = ob.modifiers.new("Armature", "ARMATURE")
    arm.object = rig
    if thick:
        so = ob.modifiers.new("Grosor", "SOLIDIFY")
        so.thickness, so.offset, so.use_rim = thick, 1.0, True
    sub = ob.modifiers.new("Sub", "SUBSURF")
    sub.levels, sub.render_levels = 1, 2
    ob.parent = rig
    if mat:
        md.materials.clear()
        md.materials.append(mat)
    return ob


x, y, z = CO[:, 0], CO[:, 1], CO[:, 2]
ax = np.abs(x)
sh_x = B["LeftArm"].head_local.x
neck = J["neck"]

# ---------- polera ----------
hem_z = J["pelvis"][2] - 0.035
sleeve_x = B["LeftHand"].head_local.x - 0.012
collar = (z > neck[2] - 0.055) & (np.hypot(x, (y - neck[1]) * 1.1) < 0.078 + np.clip((y - neck[1]) * 0.6, -0.01, 0.02))
head = (z > neck[2] - 0.035)
shirt_r = np.where((z >= hem_z) & (ax <= sleeve_x) & ~collar & ~head)[0]
PEL = J["pelvis"][2]
belly = np.clip(1 - np.abs(z - (PEL + 0.06)) / 0.14, 0, 1)
low_c = np.clip((PEL - z) / 0.2, 0, 1)
off = 0.016 + 0.010 * belly + 0.006 * low_c + 0.003 * np.clip((ax - sh_x) / 0.1, 0, 1)
coral = escena.material("Impermeable", (1.0, 0.62, 0.0), rough=0.32, sheen=0.0)
coral.node_tree.nodes["Principled BSDF"].inputs["Coat Weight"].default_value = 0.6
shirt = garment("Polera", shirt_r, off, mat=coral, thick=0.004)
# la polera no sigue a la cabeza: el peso de 'Head' pasa al cuello
hvg, nvg = shirt.vertex_groups.get(P + "Head"), shirt.vertex_groups.get(P + "Neck")
for v in shirt.data.vertices:
    for g in v.groups:
        if g.group == hvg.index and g.weight > 0:
            nvg.add([v.index], g.weight, "ADD")
            g.weight = 0.0

# ---------- jeans ----------
pants_r = np.where((z <= PEL + 0.07) & (z >= 0.08) & (ax < 0.25))[0]
low = np.clip((PEL - 0.15 - z) / 0.3, 0, 1)
off_p = 0.007 + 0.009 * low
denim = escena.material("Denim", (0.03, 0.07, 0.17), rough=0.9, sheen=0.2)
pants = garment("Jeans", pants_r, off_p, thick=0.003, mat=denim)

# ---------- zapatillas ----------
import bmesh
shoe_r = np.where(z < 0.29)[0]
sme = bpy.data.meshes.new("Zapatillas")
bm = bmesh.new()
for sgn in (1, -1):
    idx = shoe_r[np.sign(x[shoe_r]) == sgn]
    pts = CO[idx] + NO[idx] * 0.014
    vs = [bm.verts.new(p) for p in pts]
    res_ = bmesh.ops.convex_hull(bm, input=vs)
    junk = {g for g in res_["geom_interior"] + res_["geom_unused"] if isinstance(g, bmesh.types.BMVert)}
    bmesh.ops.delete(bm, geom=list(junk), context="VERTS")
bm.to_mesh(sme)
bm.free()
shoe = bpy.data.objects.new("Zapatillas", sme)
bpy.context.scene.collection.objects.link(shoe)
rm = shoe.modifiers.new("Remesh", "REMESH")
rm.mode, rm.voxel_size = "VOXEL", 0.006
bpy.context.view_layer.objects.active = shoe
bpy.ops.object.modifier_apply(modifier="Remesh")
sc = np.array([v.co[:] for v in sme.vertices])
zmin = sc[:, 2].min()
sc[:, 2] = np.where(sc[:, 2] < zmin + 0.02, zmin - 0.006, sc[:, 2])
sme.vertices.foreach_set("co", sc.ravel())
sm2 = shoe.modifiers.new("Suave", "SMOOTH"); sm2.factor, sm2.iterations = 0.5, 4
bpy.ops.object.modifier_apply(modifier="Suave")
sc = np.array([v.co[:] for v in sme.vertices])
for p in sme.polygons:
    p.use_smooth = True
for vgb in body.vertex_groups:
    shoe.vertex_groups.new(name=vgb.name)
dt = shoe.modifiers.new("Pesos", "DATA_TRANSFER")
dt.object = body
dt.use_vert_data = True
dt.data_types_verts = {"VGROUP_WEIGHTS"}
dt.vert_mapping = "POLYINTERP_NEAREST"
dt.layers_vgroup_select_src = "ALL"
dt.layers_vgroup_select_dst = "NAME"
bpy.ops.object.modifier_apply(modifier="Pesos")
arm = shoe.modifiers.new("Armature", "ARMATURE"); arm.object = rig
sub = shoe.modifiers.new("Sub", "SUBSURF"); sub.levels, sub.render_levels = 1, 1
shoe.parent = rig

m = bpy.data.materials.new("Zapatilla")
m.use_nodes = True
nt = m.node_tree
bsdf = nt.nodes["Principled BSDF"]
bsdf.inputs["Roughness"].default_value = 0.3
bsdf.inputs["Coat Weight"].default_value = 0.5
ramp = nt.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.interpolation = "CONSTANT"
els = ramp.color_ramp.elements
els[0].position, els[0].color = 0.0, (0.03, 0.04, 0.03, 1)
els[1].position, els[1].color = 0.10, (0.05, 0.36, 0.12, 1)
e3 = els.new(0.97); e3.color = (0.04, 0.28, 0.09, 1)
mr = nt.nodes.new("ShaderNodeMapRange")
mr.inputs["From Min"].default_value = zmin - 0.006
mr.inputs["From Max"].default_value = zmin + 0.30
attr_gen = nt.nodes.new("ShaderNodeAttribute")
attr_gen.attribute_name = "rest_z"
nt.links.new(attr_gen.outputs["Fac"], mr.inputs["Value"])
nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
sme.materials.append(m)
ra = sme.attributes.new("rest_z", "FLOAT", "POINT")
ra.data.foreach_set("value", sc[:, 2].astype(np.float32))

# ---------- ocultar piel bajo la ropa ----------
hide = set()
for reg, margin in ((shirt_r, 0.035), (pants_r, 0.03), (shoe_r, 0.0)):
    d = dist_from_boundary(reg)
    hide.update(np.where(d > margin)[0].tolist())
hide.update(np.where(z < 0.10)[0].tolist())
vg = body.vertex_groups.new(name="Oculto")
vg.add(sorted(hide), 1.0, "REPLACE")
mk = body.modifiers.new("Ocultar", "MASK")
mk.vertex_group, mk.invert_vertex_group = "Oculto", True

# ---------- piel: textura pintada en UV ----------
def obj_center(name):
    o = bpy.data.objects[name]
    pts = np.array([o.matrix_world @ v.co for v in o.data.vertices])
    return pts.mean(axis=0), float(np.linalg.norm(pts - pts.mean(axis=0), axis=1).mean())
EL, ER_ = obj_center("Ojo.L")[0], obj_center("Ojo.R")[0]
EC = (EL + ER_) / 2
MOUTH = J["mouth"]
SKIN = np.array([0.58, 0.31, 0.19])     # piel clara-trigueña (lineal)
BROW = np.array([0.045, 0.025, 0.016])
LIP = np.array([0.42, 0.17, 0.13])
HAIRBASE = np.array([0.06, 0.035, 0.022])


def skin_features(p):
    n1 = ub.vnoise(p, 60, 1)
    n2 = ub.vnoise(p, 260, 2)
    base = SKIN * (0.92 + 0.12 * n1[:, None] + 0.05 * (n2[:, None] - 0.5))
    yield base, np.ones(len(p))
    # rubor suave en mejillas
    for s in (1, -1):
        c = EC + np.array([0.045 * s, -0.02, -0.035])
        d = np.linalg.norm((p - c) * [1, 0.6, 1.2], axis=1)
        yield np.array([0.5, 0.2, 0.14]), 0.25 * (1 - ub.smoothstep(0.0, 0.03, d))
    # pecas en las mejillas y la nariz
    rng = np.random.RandomState(4)
    for k in range(34):
        s_ = 1 if k % 2 else -1
        c = EC + np.array([s_ * rng.uniform(0.012, 0.06), -0.03 + rng.uniform(-0.01, 0.01), -0.028 + rng.uniform(-0.016, 0.012)])
        d = np.linalg.norm((p - c) * [1, 0.5, 1], axis=1)
        yield np.array([0.30, 0.13, 0.06]), 0.55 * (1 - ub.smoothstep(0.0012, 0.0024, d)) * (p[:, 1] < EC[1])
    # labios
    rel = p - MOUTH
    front = p[:, 1] < MOUTH[1] + 0.02
    e = (rel[:, 0] / 0.024) ** 2 + ((rel[:, 2] + 0.001) / 0.0105) ** 2
    yield LIP, 0.55 * (1 - ub.smoothstep(0.55, 1.0, e)) * front
    # cejas
    for E, s in ((EL, 1), (ER_, -1)):
        rel = p - E
        dx = rel[:, 0] * s          # >0 hacia afuera
        t = np.clip((dx + 0.018) / 0.05, 0, 1)
        h = 0.0215 + 0.006 * np.sin(np.pi * np.clip(t * 1.15, 0, 1)) - 0.004 * t
        th = 0.0085 * (1 - t) + 0.0040 * t
        dz = rel[:, 2] - h
        inside = (1 - ub.smoothstep(th * 0.35, th * 0.6, np.abs(dz)))
        ends = ub.smoothstep(-0.02, -0.014, dx) * (1 - ub.smoothstep(0.03, 0.036, dx))
        strokes = 0.85 + 0.15 * np.sin((dx * 700 + dz * 1300))
        yield BROW, 0.92 * inside * ends * strokes * (p[:, 1] < E[1] + 0.025)
    # base oscura del pelo en el cuero cabelludo
    rel = p - EC
    az = np.arctan2(rel[:, 0], -(p[:, 1] - (EC[1] + 0.09)))  # 0 = frente
    hl = 0.068 * np.cos(az / 2) ** 2 + (-0.06) * np.sin(az / 2) ** 2
    side = np.abs(np.sin(az)) ** 3 * 0.022
    m = ub.smoothstep(-0.006, 0.006, rel[:, 2] - (hl + side)) * (p[:, 2] > EC[2] - 0.14)
    yield HAIRBASE, 0.9 * m


RES = 2048
P_, U_ = ub.mesh_triangles(body)
base = np.tile(SKIN, (RES, RES, 1))
head_tri = P_.mean(axis=1)[:, 2] > neck[2] - 0.05
img = ub.rasterize(P_[~head_tri], U_[~head_tri], RES, lambda p: [(SKIN * (0.94 + 0.1 * ub.vnoise(p, 40, 3)[:, None]), np.ones(len(p)))], base)
img = ub.rasterize(P_[head_tri], U_[head_tri], RES, skin_features, img)
skin_img = ub.to_image("PielColor", img)

skin = bpy.data.materials.new("Piel")
skin.use_nodes = True
nt = skin.node_tree
bs = nt.nodes["Principled BSDF"]
tex = nt.nodes.new("ShaderNodeTexImage")
tex.image = skin_img
uvn = nt.nodes.new("ShaderNodeUVMap")
uvn.uv_map = "UV"
nt.links.new(uvn.outputs["UV"], tex.inputs["Vector"])
nt.links.new(tex.outputs["Color"], bs.inputs["Base Color"])
bs.inputs["Roughness"].default_value = 0.48
bs.inputs["Subsurface Weight"].default_value = 0.22
bs.inputs["Subsurface Radius"].default_value = (1.0, 0.45, 0.25)
bs.inputs["Subsurface Scale"].default_value = 0.01
bs.inputs["Specular IOR Level"].default_value = 0.4
noise = nt.nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 900
bump = nt.nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.06
nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
me.materials.clear()
me.materials.append(skin)
body.modifiers.new("Sub", "SUBSURF").render_levels = 2

# ---------- ojos ----------
eye = bpy.data.materials.new("Ojo")
eye.use_nodes = True
nt = eye.node_tree
bs = nt.nodes["Principled BSDF"]
uvn = nt.nodes.new("ShaderNodeUVMap")
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
nt.links.new(uvn.outputs["UV"], sep.inputs[0])
ramp = nt.nodes.new("ShaderNodeValToRGB")
els = ramp.color_ramp.elements
els[0].position, els[0].color = 0.0, (0.82, 0.79, 0.75, 1)     # esclera
els[1].position, els[1].color = 0.815, (0.80, 0.76, 0.72, 1)
for pos, col in ((0.828, (0.05, 0.025, 0.012, 1)), (0.84, (0.22, 0.11, 0.04, 1)), (0.905, (0.12, 0.055, 0.02, 1)),
                 (0.918, (0.004, 0.003, 0.002, 1)), (1.0, (0.0, 0.0, 0.0, 1))):
    e = els.new(pos); e.color = col
nt.links.new(sep.outputs["Y"], ramp.inputs["Fac"])
nt.links.new(ramp.outputs["Color"], bs.inputs["Base Color"])
bs.inputs["Roughness"].default_value = 0.25
bs.inputs["Coat Weight"].default_value = 1.0
bs.inputs["Coat Roughness"].default_value = 0.02
for s in ("L", "R"):
    o = bpy.data.objects[f"Ojo.{s}"]
    o.data.materials.clear()
    o.data.materials.append(eye)

for name, col, rough in (("Dientes", (0.80, 0.77, 0.70), 0.3), ("Lengua", (0.45, 0.12, 0.12), 0.4), ("Pestanas", (0.02, 0.012, 0.008), 0.6)):
    o = bpy.data.objects.get(name)
    if o:
        o.data.materials.clear()
        o.data.materials.append(escena.material(name + "Mat", col, rough=rough))

# ---------- estampado: estrella amarilla en el pecho ----------
STAR = np.array([1.0, 0.62, 0.04])
chest = np.array([0.0, 0.0, 1.27])


def star_poly(R_out=0.058, R_in=0.024, rot=0.0):
    pts = []
    for i in range(10):
        r = R_out if i % 2 == 0 else R_in
        a = rot + i * np.pi / 5
        pts.append((r * np.sin(a), r * np.cos(a)))
    return np.array(pts)


def inside_poly(q, poly):
    x, y = q[:, 0], q[:, 1]
    ins = np.zeros(len(q), bool)
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        c = ((y1 > y) != (y2 > y)) & (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1)
        ins ^= c
    return ins


def star_mask(p):
    front = p[:, 1] < -0.02
    q = np.c_[p[:, 0] - chest[0], p[:, 2] - chest[2]]
    yield STAR, inside_poly(q, star_poly()).astype(float) * front * 0.0


Ps, Us = ub.mesh_triangles(body)
sel = (Ps.mean(axis=1)[:, 2] > 1.15) & (Ps.mean(axis=1)[:, 2] < 1.40) & (np.abs(Ps.mean(axis=1)[:, 0]) < 0.12)
simg = ub.rasterize(Ps[sel], Us[sel], 1024, star_mask, np.tile(np.array([1.0, 0.62, 0.0]), (1024, 1024, 1)))
star_img = ub.to_image("PoleraColor", simg)
nt = coral.node_tree
tex = nt.nodes.new("ShaderNodeTexImage")
tex.image = star_img
uvn = nt.nodes.new("ShaderNodeUVMap")
uvn.uv_map = "UV"
nt.links.new(uvn.outputs["UV"], tex.inputs["Vector"])
nt.links.new(tex.outputs["Color"], coral.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
# arrugas suaves de tela
for mat, sc_ in ((coral, 18.0), (denim, 22.0)):
    nt = mat.node_tree
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = sc_
    nz.inputs["Detail"].default_value = 3
    bp = nt.nodes.new("ShaderNodeBump")
    bp.inputs["Strength"].default_value = 0.12
    weave = nt.nodes.new("ShaderNodeTexNoise")
    weave.inputs["Scale"].default_value = 1400
    mix = nt.nodes.new("ShaderNodeMath")
    mix.operation = "MULTIPLY_ADD"
    mix.inputs[1].default_value = 0.15
    nt.links.new(weave.outputs["Fac"], mix.inputs[0])
    nt.links.new(nz.outputs["Fac"], mix.inputs[2])
    nt.links.new(mix.outputs["Value"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], nt.nodes["Principled BSDF"].inputs["Normal"])

bpy.ops.wm.save_as_mainfile(filepath=f"{OUT}/dressed.blend")
print("ok dress")
