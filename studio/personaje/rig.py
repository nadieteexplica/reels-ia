"""Paso 3: rig propio con nombres y orientación del esqueleto de Mixamo.

1. Arma un esqueleto 'mixamorig:*' en las articulaciones de MakeHuman (pose A).
2. Pesos automáticos y shape keys de expresión (unidades FACS de MakeHuman).
3. Lleva la malla a la pose T de Mixamo (alinea cada hueso a la dirección del esqueleto fuente) y la fija como reposo.
4. Copia la orientación (roll) de cada hueso de Mixamo, así las FBX 'Without Skin' se aplican tal cual.
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import bpy
from mathutils import Matrix, Vector

OUT = os.environ.get("OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"))
SRC_FBX = os.environ.get("MIXAMO_DIR", "/home/claude/work/mixamo") + "/Focus.fbx"
J = {k: Vector(v) for k, v in json.load(open(f"{OUT}/joints.json")).items()}

bpy.ops.wm.open_mainfile(filepath=os.environ.get("IN_BLEND", f"{OUT}/body.blend"))
scene = bpy.context.scene

# ---------- esqueleto fuente (Mixamo) ----------
bpy.ops.import_scene.fbx(filepath=SRC_FBX)
src = [o for o in scene.objects if o.type == "ARMATURE"][0]
src.name = "MixamoFuente"
src.animation_data.action = None
for pb in src.pose.bones:
    pb.matrix_basis = Matrix()
bpy.context.view_layer.update()
SW = src.matrix_world
SRC_REST = {b.name: (SW @ b.matrix_local) for b in src.data.bones}
SRC_HEAD = {b.name: SW @ b.head_local for b in src.data.bones}
SRC_TAIL = {b.name: SW @ b.tail_local for b in src.data.bones}
SRC_PARENT = {b.name: (b.parent.name if b.parent else None) for b in src.data.bones}
ORDER = [b.name for b in src.data.bones]  # padres antes que hijos

P = "mixamorig:"


def spine_points():
    hips = (J["pelvis"] + J["spine-4"]) * 0.5
    neck = J["neck"]
    sh = [SRC_HEAD[P + n].z for n in ("Hips", "Spine", "Spine1", "Spine2", "Neck")]
    fr = [(z - sh[0]) / (sh[-1] - sh[0]) for z in sh]
    # curva de la espalda desde las articulaciones de MakeHuman
    zs = np.array([J[k].z for k in ("pelvis", "spine-4", "spine-3", "spine-2", "spine-1", "neck")])
    ys = np.array([J[k].y for k in ("pelvis", "spine-4", "spine-3", "spine-2", "spine-1", "neck")])
    pts = []
    for f in fr:
        z = hips.z + (neck.z - hips.z) * f
        pts.append(Vector((0.0, float(np.interp(z, zs, ys)), z)))
    return pts


hips, spine, spine1, spine2, neck = spine_points()
HEAD = {P + "Hips": hips, P + "Spine": spine, P + "Spine1": spine1, P + "Spine2": spine2,
        P + "Neck": neck, P + "Head": J["head"], P + "HeadTop_End": J["head-2"]}
for S, s in (("Left", "l"), ("Right", "r")):
    HEAD.update({
        P + f"{S}Shoulder": J[f"{s}-clavicle"], P + f"{S}Arm": J[f"{s}-shoulder"],
        P + f"{S}ForeArm": J[f"{s}-elbow"], P + f"{S}Hand": J[f"{s}-hand"],
        P + f"{S}UpLeg": J[f"{s}-upper-leg"], P + f"{S}Leg": J[f"{s}-knee"],
        P + f"{S}Foot": J[f"{s}-ankle"], P + f"{S}ToeBase": J[f"{s}-foot-1"], P + f"{S}Toe_End": J[f"{s}-foot-2"],
    })
    for i, fn in enumerate(("Thumb", "Index", "Middle", "Ring", "Pinky"), start=1):
        for k in range(1, 5):
            HEAD[P + f"{S}Hand{fn}{k}"] = J[f"{s}-finger-{i}-{k}"]
assert set(HEAD) == set(ORDER), set(ORDER) ^ set(HEAD)
CHILDREN = {n: [c for c in ORDER if SRC_PARENT[c] == n] for n in ORDER}
MAIN_CHILD = {}
for n in ORDER:
    cs = CHILDREN[n]
    if not cs:
        continue
    pref = [c for c in cs if c.endswith(("Spine", "Spine1", "Spine2", "Neck", "Head", "HeadTop_End", "Arm", "ForeArm", "Hand",
                                         "Leg", "Foot", "ToeBase", "Toe_End", "Middle1")) or c[-1] in "234"]
    MAIN_CHILD[n] = (pref or cs)[0]

# ---------- esqueleto propio en pose A ----------
arm_data = bpy.data.armatures.new("Rig")
rig = bpy.data.objects.new("Rig", arm_data)
scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode="EDIT")
for n in ORDER:
    eb = arm_data.edit_bones.new(n)
    eb.head = HEAD[n]
    if n in MAIN_CHILD:
        eb.tail = HEAD[MAIN_CHILD[n]]
    else:  # hojas: misma dirección que en la fuente, largo proporcional
        d = SRC_TAIL[n] - SRC_HEAD[n]
        par = SRC_PARENT[n]
        L = (HEAD[n] - HEAD[par]).length * 0.6 if par else 0.1
        eb.tail = HEAD[n] + d.normalized() * max(L, 0.01)
    if (eb.tail - eb.head).length < 1e-4:
        eb.tail = eb.head + Vector((0, 0, 0.02))
for n in ORDER:
    if SRC_PARENT[n]:
        eb = arm_data.edit_bones[n]
        eb.parent = arm_data.edit_bones[SRC_PARENT[n]]
        eb.use_connect = False
bpy.ops.object.mode_set(mode="OBJECT")

# ---------- pesos automáticos ----------
body = bpy.data.objects["Cuerpo"]
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.parent_set(type="ARMATURE_AUTO")
print("grupos con peso:", len(body.vertex_groups))

# Cabeza rígida: la cara, ojos y dientes se mueven juntos (evita que los dientes o los ojos se salgan)
head_vg = body.vertex_groups.get(P + "Head")
jaw_z = J["jaw"].z
for v in body.data.vertices:
    co = v.co
    w = max(0.0, min(1.0, (co.z - (jaw_z - 0.045)) / 0.05))
    if co.y > J["head"].y + 0.02:  # nuca: la transición parte más arriba
        w = max(0.0, min(1.0, (co.z - jaw_z) / 0.05))
    if w <= 0:
        continue
    for g in list(v.groups):
        if g.group != head_vg.index:
            body.vertex_groups[g.group].add([v.index], g.weight * (1 - w), "REPLACE")
    cur = next((g.weight for g in v.groups if g.group == head_vg.index), 0.0)
    head_vg.add([v.index], cur * (1 - w) + w, "REPLACE")

# Cuello: reparte el giro (suavizado de pesos Spine2/Neck/Head en la zona del cuello)
import bmesh
NECK_G = [P + "Spine2", P + "Neck", P + "Head", P + "LeftShoulder", P + "RightShoulder"]
gid = {n: body.vertex_groups[n].index for n in NECK_G if n in body.vertex_groups}
CO_ = np.array([v.co[:] for v in body.data.vertices])
zone = np.where((CO_[:, 2] > J["neck"].z - 0.10) & (CO_[:, 2] < jaw_z - 0.035) & (np.abs(CO_[:, 0]) < 0.11))[0]
nb = {}
for e in body.data.edges:
    a, b = e.vertices
    nb.setdefault(a, []).append(b)
    nb.setdefault(b, []).append(a)
W = {i: {n: 0.0 for n in gid} for i in range(len(CO_))}
for v in body.data.vertices:
    for g in v.groups:
        for n, gi in gid.items():
            if g.group == gi:
                W[v.index][n] = g.weight
zs = set(zone.tolist())
for _ in range(25):
    newW = {}
    for i in zone:
        acc = {n: 0.0 for n in gid}
        for j in nb.get(i, []):
            for n in gid:
                acc[n] += W[j][n]
        k = max(len(nb.get(i, [])), 1)
        newW[i] = {n: W[i][n] * 0.5 + acc[n] / k * 0.5 for n in gid}
    W.update(newW)
for i in zone:
    tot = sum(W[i].values())
    other = sum(g.weight for g in body.data.vertices[i].groups if g.group not in gid.values())
    scale = max(0.0, 1.0 - other) / tot if tot > 0 else 0
    for n, gi in gid.items():
        body.vertex_groups[gi].add([int(i)], W[i][n] * scale, "REPLACE")
# zona para el suavizado correctivo
cs_vg = body.vertex_groups.new(name="SuaveCuello")
for i in range(len(CO_)):
    z_ = CO_[i, 2]
    f = max(0.0, min(1.0, (z_ - (J["neck"].z - 0.16)) / 0.06)) * max(0.0, min(1.0, ((jaw_z - 0.02) - z_) / 0.03))
    if f > 0 and abs(CO_[i, 0]) < 0.2:
        cs_vg.add([i], f, "REPLACE")

# Partes rígidas de la cabeza
for name in ("Dientes", "Lengua", "Ojo.L", "Ojo.R", "Pestanas"):
    ob = bpy.data.objects.get(name)
    if not ob:
        continue
    vg = ob.vertex_groups.new(name=P + "Head")
    vg.add(range(len(ob.data.vertices)), 1.0, "REPLACE")
    ob.parent = rig
    m = ob.modifiers.new("Armature", "ARMATURE")
    m.object = rig

# ---------- shape keys de expresión (antes de cambiar de pose) ----------
units = np.load(f"{OUT}/expr_units.npz")


def add_units(ob):
    idx = ob.get("mh_index")
    if idx is None:
        return 0
    pos = {int(m): i for i, m in enumerate(idx)}
    if not ob.data.shape_keys:
        ob.shape_key_add(name="Basis")
    base = np.array([v.co[:] for v in ob.data.vertices])
    n = 0
    for name in units.files:
        arr = units[name]
        sel = [(pos[int(r[0])], r[1:]) for r in arr if int(r[0]) in pos]
        if not sel:
            continue
        co = base.copy()
        for i, o in sel:
            co[i] += np.array([o[0], -o[2], o[1]]) * 0.1
        k = ob.shape_key_add(name=name, from_mix=False)
        k.data.foreach_set("co", co.ravel())
        n += 1
    return n


for name in ("Cuerpo", "Dientes", "Lengua", "Pestanas"):
    ob = bpy.data.objects.get(name)
    if ob:
        print(name, "shape keys:", add_units(ob))

# ---------- llevar a pose T de Mixamo ----------
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode="POSE")


def rot_between(a, b):
    return a.normalized().rotation_difference(b.normalized()).to_matrix().to_4x4()


def frame_rot(y_from, s_from, y_to, s_to):
    def frame(y, s):
        y = y.normalized()
        x = (s - y * s.dot(y)).normalized()
        z = x.cross(y)
        return Matrix((x, y, z)).transposed()
    return (frame(y_to, s_to) @ frame(y_from, s_from).inverted()).to_4x4()


def posed_head(n):
    return rig.pose.bones[n].head.copy()


KEEP = {P + n for n in ("Hips", "Spine", "Spine1", "Spine2", "Neck", "Head", "HeadTop_End")}  # postura natural de MakeHuman
for n in ORDER:
    if n in KEEP:
        continue
    pb = rig.pose.bones[n]
    bpy.context.view_layer.update()
    M = pb.matrix.copy()
    y_cur = M.col[1].xyz
    y_tgt = (SRC_TAIL[n] - SRC_HEAD[n])
    if n in MAIN_CHILD:
        y_tgt = SRC_HEAD[MAIN_CHILD[n]] - SRC_HEAD[n]
        y_cur = posed_head(MAIN_CHILD[n]) - posed_head(n)
    side = "Left" if "Left" in n else "Right"
    R = None
    if n.endswith(("ForeArm", "Hand")):
        # giro de la mano: vector índice -> meñique igual que en la fuente
        s_cur = posed_head(P + f"{side}HandPinky1") - posed_head(P + f"{side}HandIndex1")
        s_tgt = SRC_HEAD[P + f"{side}HandPinky1"] - SRC_HEAD[P + f"{side}HandIndex1"]
        R = frame_rot(y_cur, s_cur, y_tgt, s_tgt)
    elif n.endswith("Arm") and not n.endswith("ForeArm"):
        # plano del codo: el pliegue queda mirando al frente
        a = posed_head(P + f"{side}ForeArm") - posed_head(n)
        b = posed_head(P + f"{side}Hand") - posed_head(P + f"{side}ForeArm")
        nrm = a.cross(b)
        tgt = Vector((0, 0, 1 if nrm.z >= 0 else -1))
        R = frame_rot(y_cur, nrm, y_tgt, tgt)
    if R is None:
        R = rot_between(y_cur, y_tgt)
    head = M.translation.copy()
    M2 = R @ Matrix.Translation(-head) @ M
    M2.translation = head
    pb.matrix = M2
bpy.context.view_layer.update()
bpy.ops.object.mode_set(mode="OBJECT")


def bake_pose(ob):
    """Aplica la deformación actual a la malla y a cada shape key."""
    dg = bpy.context.evaluated_depsgraph_get()
    keys = ob.data.shape_keys.key_blocks if ob.data.shape_keys else []
    vals = [k.value for k in keys]
    res = {}
    names = [k.name for k in keys] or ["__base__"]
    for i, nm in enumerate(names):
        for k in keys:
            k.value = 0.0
        if keys and i > 0:
            keys[i].value = 1.0
        bpy.context.view_layer.update()
        ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
        res[nm] = np.array([v.co[:] for v in ev.data.vertices])
    if keys:
        for k, nm in zip(keys, names):
            k.data.foreach_set("co", res[nm].ravel())
        for k in keys[1:]:
            k.value = 0.0
    ob.data.vertices.foreach_set("co", res[names[0]].ravel())
    ob.data.update()


arm_objs = [o for o in scene.objects if o.type == "MESH" and any(m.type == "ARMATURE" and m.object == rig for m in o.modifiers)]
for ob in arm_objs:
    for m in ob.modifiers:
        if m.type == "ARMATURE":
            m.show_viewport = True
    bake_pose(ob)
    for m in ob.modifiers:
        if m.type == "ARMATURE":
            m.show_viewport = False
            m.show_render = False

bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode="POSE")
bpy.ops.pose.select_all(action="SELECT")
bpy.ops.pose.armature_apply(selected=False)
bpy.ops.object.mode_set(mode="EDIT")
for n in ORDER:
    eb = arm_data.edit_bones[n]
    L, h = eb.length, eb.head.copy()
    R = SRC_REST[n].to_3x3().normalized().to_4x4()
    R.translation = h
    eb.matrix = R
    eb.length = L
bpy.ops.object.mode_set(mode="OBJECT")
for ob in arm_objs:
    for m in ob.modifiers:
        if m.type == "ARMATURE":
            m.show_viewport = m.show_render = True

cs = body.modifiers.new("SuaveCuello", "CORRECTIVE_SMOOTH")
cs.vertex_group = "SuaveCuello"
cs.factor, cs.iterations, cs.rest_source = 0.6, 8, "ORCO"

# cadera de la fuente para escalar la traslación de las animaciones
rig["src_hips_z"] = SRC_HEAD[P + "Hips"].z
rig["hips_z"] = arm_data.bones[P + "Hips"].head_local.z
bpy.data.objects.remove(src)
for a in list(bpy.data.actions):
    bpy.data.actions.remove(a)
bpy.ops.wm.save_as_mainfile(filepath=os.environ.get("OUT_BLEND", f"{OUT}/rigged.blend"))
print("ok rig")
