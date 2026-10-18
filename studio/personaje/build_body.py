"""Paso 1: cuerpo base del protagonista desde MakeHuman (CC0) -> body.blend + joints.json"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import mh
import bpy

OUT = os.environ.get("OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"))
os.makedirs(OUT, exist_ok=True)

RACE = {"caucasian": 0.5, "asian": 0.3, "african": 0.2}  # rasgos mestizos, neutros para Latam
v0, uvs, faces, groups = mh.load_obj()
v = v0.copy()
mh.apply_macros(v, gender=1.0, age_years=21, muscle=0.6, weight=0.47, race=RACE, height=0.62, proportions=0.65)

# Rasgos propios: cara amable y legible en vertical (ojos algo más grandes, nariz y mentón suaves)
FACE = {
    "eyes/l-eye-scale-incr.target": 0.45, "eyes/r-eye-scale-incr.target": 0.45,
    "head/head-age-decr.target": 0.5, "head/head-fat-incr.target": 0.25, "head/head-oval.target": 0.3,
    "head/head-scale-vert-decr.target": 0.12,
    "cheek/l-cheek-volume-incr.target": 0.5, "cheek/r-cheek-volume-incr.target": 0.5,
    "nose/nose-scale-horiz-decr.target": 0.15, "nose/nose-scale-vert-decr.target": 0.12,
    "chin/chin-prominent-decr.target": 0.25, "chin/chin-height-decr.target": 0.15,
    "mouth/mouth-upperlip-volume-incr.target": 0.35, "mouth/mouth-lowerlip-volume-incr.target": 0.3,
    "mouth/mouth-angles-up.target": 0.25, "mouth/mouth-scale-horiz-incr.target": 0.1,
    "neck/neck-scale-horiz-incr.target": 0.35, "neck/neck-scale-vert-decr.target": 0.2,
}
for rel, w in FACE.items():
    if os.path.exists(os.path.join(mh.MH, "targets", rel)):
        mh.add(v, rel, w)
    else:
        print("sin target:", rel)

joints = mh.joint_positions(v, faces, groups)


def to_bl(p):
    p = np.asarray(p)
    return np.stack([p[..., 0], -p[..., 2], p[..., 1]], axis=-1) * 0.1


ground = joints["ground"]
def to_world(p):
    return to_bl(np.asarray(p) - np.array([0, ground[1], 0]))

json.dump({k: to_world(p).tolist() for k, p in joints.items()}, open(f"{OUT}/joints.json", "w"), indent=0)
np.save(f"{OUT}/verts_mh.npy", v)


def make_mesh(name, keep_groups):
    sel = [(f, g) for f, g in zip(faces, groups) if g in keep_groups]
    used = sorted({i for (vi, _), _ in sel for i in vi})
    remap = {o: n for n, o in enumerate(used)}
    me = bpy.data.meshes.new(name)
    co = to_world(v[used])
    me.from_pydata(co.tolist(), [], [[remap[i] for i in vi] for (vi, _), _ in sel])
    uvl = me.uv_layers.new(name="UV")
    loop = 0
    for (vi, ti), _ in sel:
        for t in ti:
            if t >= 0:
                uvl.data[loop].uv = uvs[t]
            loop += 1
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob["mh_index"] = used  # índice original de MakeHuman por vértice (para targets de expresión)
    return ob, used


bpy.ops.wm.read_factory_settings(use_empty=True)
body, body_idx = make_mesh("Cuerpo", {"body"})
teeth, _ = make_mesh("Dientes", {"helper-upper-teeth", "helper-lower-teeth"})
tongue, _ = make_mesh("Lengua", {"helper-tongue"})
hair_cap, _ = make_mesh("CascoPelo", {"helper-hair"})
tights, _ = make_mesh("Malla", {"helper-tights"})
# lashes, _ = make_mesh("Pestanas", {g for g in set(groups) if g and "eyelashes" in g})

# Ojos: esferas en el centro de los helpers
for side in ("l", "r"):
    idx = mh.group_vertices(faces, groups, f"helper-{side}-eye")
    pts = to_world(v[idx])
    c = pts.mean(axis=0)
    r = float(np.linalg.norm(pts - c, axis=1).mean())
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=c.tolist(), segments=48, ring_count=24)
    eye = bpy.context.active_object
    eye.name = f"Ojo.{side.upper()}"
    eye.rotation_euler = (np.pi / 2, 0, 0)  # polo de la esfera mirando al frente (-Y)
    bpy.ops.object.shade_smooth()

# Targets de expresión como datos (se convierten en shape keys en el paso de rig)
units = mh.expression_units(RACE)
np.savez_compressed(f"{OUT}/expr_units.npz", **{k: np.concatenate([i[:, None], o], 1) for k, (i, o) in units.items()})
json.dump(body_idx, open(f"{OUT}/body_idx.json", "w"))

h = to_world(v[body_idx])[:, 2]
print("altura (m):", round(float(h.max() - h.min()), 3), "pies en z:", round(float(h.min()), 3))
bpy.ops.wm.save_as_mainfile(filepath=f"{OUT}/body.blend")
