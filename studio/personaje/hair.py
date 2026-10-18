"""Paso 5: pelo café en mechones (curvas de pelo, Cycles).

Corte casual: arriba más largo con un jopo hacia adelante y al lado, costados y nuca cortos.
Las hebras se agrupan en mechones que terminan en punta.
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import bpy
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

OUT = os.environ.get("OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"))
P = "mixamorig:"
N_STRANDS = int(os.environ.get("N_STRANDS", 26000))
N_GUIDES = int(os.environ.get("N_GUIDES", 1100))
K = 10
rng = np.random.default_rng(7)

bpy.ops.wm.open_mainfile(filepath=f"{OUT}/dressed.blend")
rig = bpy.data.objects["Rig"]
body = bpy.data.objects["Cuerpo"]
me = body.data
CO = np.array([v.co[:] for v in me.vertices])
EL = np.array([bpy.data.objects["Ojo.L"].matrix_world @ v.co for v in bpy.data.objects["Ojo.L"].data.vertices]).mean(0)
ER = np.array([bpy.data.objects["Ojo.R"].matrix_world @ v.co for v in bpy.data.objects["Ojo.R"].data.vertices]).mean(0)
EC = (EL + ER) / 2

# BVH de la cabeza para mantener las hebras sobre el cuero cabelludo
head_faces = [p for p in me.polygons if CO[list(p.vertices)].mean(0)[2] > 1.50]
hv = sorted({i for p in head_faces for i in p.vertices})
remap = {o: n for n, o in enumerate(hv)}
bvh = BVHTree.FromPolygons([Vector(CO[i]) for i in hv], [[remap[i] for i in p.vertices] for p in head_faces])


def hairline_ok(p):
    rel = p - EC
    az = np.arctan2(rel[:, 0], -(p[:, 1] - (EC[1] + 0.09)))
    hl = 0.068 * np.cos(az / 2) ** 2 - 0.06 * np.sin(az / 2) ** 2 + np.abs(np.sin(az)) ** 3 * 0.022
    return (rel[:, 2] - hl) > 0.004


# raíces: muestreo por área en los triángulos del cuero cabelludo
me.calc_loop_triangles()
tri = np.array([t.vertices[:] for t in me.loop_triangles])
T = CO[tri]
cen = T.mean(1)
keep = (cen[:, 2] > 1.5) & hairline_ok(cen)
T = T[keep]
area = 0.5 * np.linalg.norm(np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]), axis=1)
pick = rng.choice(len(T), size=N_STRANDS, p=area / area.sum())
u, v = rng.random(N_STRANDS), rng.random(N_STRANDS)
flip = u + v > 1
u[flip], v[flip] = 1 - u[flip], 1 - v[flip]
roots = T[pick, 0] + (T[pick, 1] - T[pick, 0]) * u[:, None] + (T[pick, 2] - T[pick, 0]) * v[:, None]
nrm = np.cross(T[pick, 1] - T[pick, 0], T[pick, 2] - T[pick, 0])
nrm /= np.linalg.norm(nrm, axis=1, keepdims=True)
out = (roots - (EC + [0, 0.08, 0.02])) @ np.eye(3)
nrm *= np.sign((nrm * out).sum(1))[:, None]  # normales hacia afuera

# zonas
topz = EC[2] + 0.06
top = np.clip((roots[:, 2] - (EC[2] + 0.03)) / 0.07, 0, 1)            # 1 arriba
front = np.clip(-(roots[:, 1] - (EC[1] + 0.06)) / 0.07, 0, 1)         # 1 adelante
side = np.clip((np.abs(nrm[:, 0]) - 0.45) / 0.4, 0, 1) * (1 - top * 0.7)
back = np.clip((nrm[:, 1] - 0.2) / 0.5, 0, 1) * (1 - top * 0.6)
L = 0.022 + 0.040 * top + 0.012 * top * front - 0.010 * side - 0.006 * back
L *= 0.9 + 0.2 * rng.random(N_STRANDS)
crown = EC + np.array([0.012, 0.135, 0.055])
sweep = np.array([-0.8, -0.35, 0.25])  # jopo hacia la derecha del personaje


def tangent(vec, n):
    return vec - n * (vec * n).sum(1, keepdims=True)


flow = tangent(roots - crown, nrm)
flow /= np.linalg.norm(flow, axis=1, keepdims=True) + 1e-9
grav = tangent(np.tile([0, 0, -1.0], (N_STRANDS, 1)), nrm)
grav /= np.linalg.norm(grav, axis=1, keepdims=True) + 1e-9
d = flow * (0.75 + 0.25 * top[:, None]) + grav * (side + back)[:, None] * 0.9 + sweep * (top * front * 0.45)[:, None]
d = tangent(d, nrm)
d /= np.linalg.norm(d, axis=1, keepdims=True) + 1e-9
lift = 0.25 + 0.2 * top
d0 = d + nrm * lift[:, None]
d0 /= np.linalg.norm(d0, axis=1, keepdims=True)
# jopo: el frente sube hacia adelante y se va al costado, sin tapar la frente
quiff = np.clip(top * front * 1.4, 0, 1)[:, None]
qdir = np.array([-0.45, -0.55, 0.70])
qdir /= np.linalg.norm(qdir)
d0 = d0 * (1 - quiff) + qdir * quiff
d0 /= np.linalg.norm(d0, axis=1, keepdims=True)

pts = np.zeros((N_STRANDS, K, 3))
pts[:, 0] = roots - nrm * 0.0015
for i in range(N_STRANDS):
    p = Vector(pts[i, 0])
    dd = Vector(d0[i])
    step = L[i] / (K - 1)
    hmax = 0.003 + 0.014 * top[i] + 0.016 * top[i] * front[i]
    lie = 0.35 * (1 - 0.95 * min(1.0, top[i] * front[i] * 1.4))
    for k in range(1, K):
        s = k / (K - 1)
        p = p + dd * step
        loc, n, _, _ = bvh.find_nearest(p)
        if loc is not None:
            h = (p - loc).dot(n)
            target = 0.0025 + hmax * s ** 0.8
            p = p + n * (target - h) * 0.55
            # la dirección se acuesta sobre la cabeza y cae con la gravedad
            dd = (dd - n * dd.dot(n) * lie + Vector((0, 0, -1)) * (0.02 + 0.28 * (side[i] + back[i])) * s + Vector((-0.06, -0.04, 0.0)) * top[i] * front[i] * s).normalized()
        pts[i, k] = p

# mechones: cada hebra se junta con su guía hacia la punta
gi = rng.choice(N_STRANDS, size=N_GUIDES, replace=False)
kd = KDTree(N_GUIDES)
for j, idx in enumerate(gi):
    kd.insert(Vector(roots[idx]), j)
kd.balance()
owner = np.array([kd.find(Vector(r))[1] for r in roots])
G = pts[gi][owner]
t = np.linspace(0, 1, K)[None, :, None]
strength = (0.55 + 0.2 * rng.random(N_STRANDS))[:, None, None]
clumped = G + (pts - G) * (1 - strength * t ** 0.75)
clumped = np.where(t == 0, pts, clumped)
# un poco de desorden natural
frizz = rng.normal(size=clumped.shape) * 0.0005 * t ** 1.5
clumped += frizz
# no atravesar la cabeza
for i in range(N_STRANDS):
    for k in range(1, K):
        p = Vector(clumped[i, k])
        loc, n, _, _ = bvh.find_nearest(p)
        if loc is not None and (p - loc).dot(n) < 0.0018:
            clumped[i, k] = loc + n * 0.0018

cv = bpy.data.hair_curves.new("Pelo")
cv.add_curves([K] * N_STRANDS)
cv.position_data.foreach_set("vector", clumped.reshape(-1).astype(np.float32))
rad = cv.attributes.get("radius") or cv.attributes.new("radius", "FLOAT", "POINT")
r = (0.00034 * (1 - np.linspace(0, 1, K)) ** 0.7 + 0.00005)
rad.data.foreach_set("value", np.tile(r, N_STRANDS).astype(np.float32))
hair = bpy.data.objects.new("Pelo", cv)
bpy.context.scene.collection.objects.link(hair)

mat = bpy.data.materials.new("PeloCafe")
mat.use_nodes = True
nt = mat.node_tree
for n in list(nt.nodes):
    if n.type != "OUTPUT_MATERIAL":
        nt.nodes.remove(n)
hb = nt.nodes.new("ShaderNodeBsdfHairPrincipled")
hb.parametrization = "MELANIN"
hb.inputs["Melanin"].default_value = 0.80
hb.inputs["Melanin Redness"].default_value = 0.38
hb.inputs["Roughness"].default_value = 0.34
hb.inputs["Radial Roughness"].default_value = 0.4
hb.inputs["Coat"].default_value = 0.15
hb.inputs["Random Roughness"].default_value = 0.15
info = nt.nodes.new("ShaderNodeHairInfo")
mr = nt.nodes.new("ShaderNodeMapRange")
mr.inputs["To Min"].default_value = 0.80
mr.inputs["To Max"].default_value = 0.90
nt.links.new(info.outputs["Random"], mr.inputs["Value"])
nt.links.new(mr.outputs["Result"], hb.inputs["Melanin"])
nt.links.new(hb.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
cv.materials.append(mat)

# sigue a la cabeza
mw = hair.matrix_world.copy()
hair.parent = rig
hair.parent_type = "BONE"
hair.parent_bone = P + "Head"
bpy.context.view_layer.update()
hair.matrix_world = mw
bpy.ops.wm.save_as_mainfile(filepath=f"{OUT}/personaje.blend")
print("ok pelo", N_STRANDS, "hebras")
