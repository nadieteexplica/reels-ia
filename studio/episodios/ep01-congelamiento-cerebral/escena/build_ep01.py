"""Arma el Ep. 1 completo (escenas, actuación, cámaras) -> out/ep01.blend

Uso: python3 build_ep01.py   (variables: PERSONAJE, MIXAMO_DIR, OUT)
"""
import json, math, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.abspath(os.path.join(HERE, "../../.."))
PJ = os.environ.get("PERSONAJE_DIR", os.path.join(STUDIO, "personaje"))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(STUDIO, "plantilla"))
sys.path.insert(0, PJ)
import bpy
from mathutils import Vector, Matrix, Euler, Quaternion
import props as P
import anatomy
import anim
import uvbake as ub

OUT = os.environ.get("OUT", os.path.join(HERE, "out"))  # en el repo se usa OUT fuera del árbol
MIX = os.environ.get("MIXAMO_DIR", "/home/claude/work/mixamo")
EPI = os.environ.get("EPI_DIR", os.path.abspath(os.path.join(HERE, "..")))
os.makedirs(OUT, exist_ok=True)
FPS = 30
B = "mixamorig:"

_PJB = [os.environ.get("PERSONAJE", ""), os.path.join(OUT, "personaje.blend"), os.path.join(PJ, "out", "personaje.blend")]
bpy.ops.wm.open_mainfile(filepath=next(p for p in _PJB if p and os.path.exists(p)))  # Actions deja el personaje en OUT
sc = bpy.context.scene
sc.render.fps = FPS
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = 24
sc.cycles.use_adaptive_sampling = True
sc.cycles.adaptive_threshold = 0.03
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 5
sc.cycles.transparent_max_bounces = 12
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Punchy"
sc.render.image_settings.file_format = "PNG"
if not sc.world:
    sc.world = bpy.data.worlds.new("Mundo")
sc.world.use_nodes = True

rig = bpy.data.objects["Rig"]
body = bpy.data.objects["Cuerpo"]
hair = bpy.data.objects["Pelo"]
skin = bpy.data.materials["Piel"]
words = json.load(open(os.path.join(EPI, "words.json")))


def F(t):
    return int(round(t * FPS)) + 1


# ---------------- sets ----------------
C_PLAZA = P.collection("Plaza")
C_LAB = P.collection("Lab")
C_ART = P.collection("ArteriaSet")
C_TXT = P.collection("TextoSet")
C_ORG = P.collection("Organos")
C_UTIL = P.collection("Utileria")
P.sun_and_sky()
P.plaza(C_PLAZA)
cart = P.cart(C_PLAZA, loc=(1.15, 0.85, 0), rot_z=math.radians(-18))
board, xl_cone = P.menu_board(C_PLAZA, loc=(-1.25, 0.75, 0))
board.rotation_euler.z = math.radians(25)
for ob in [o for o in list(C_PLAZA.all_objects) if o is not None]:
    pass

E = Vector(np.array([bpy.data.objects["Ojo.L"].matrix_world @ v.co for v in bpy.data.objects["Ojo.L"].data.vertices]).mean(0))
E = (E + Vector(np.array([bpy.data.objects["Ojo.R"].matrix_world @ v.co for v in bpy.data.objects["Ojo.R"].data.vertices]).mean(0))) / 2
MOUTH = Vector((0, -0.158, 1.594))
FOREHEAD = Vector((0, -0.150, 1.715))
org = anatomy.build(rig, E, C_ORG)
ghost = anatomy.ghost_skin(skin)

# máscara de escarcha/dolor en UV (R = distancia al centro de la frente, G = cristales, B = frente suave)
def frost_mask(p):
    d = np.linalg.norm((p - np.array(FOREHEAD)) * [1.0, 1.4, 1.2], axis=1)
    n = ub.vnoise(p, 1500, 5)
    n2 = ub.vnoise(p, 4200, 6)
    front = (p[:, 1] < -0.06).astype(float)
    r = np.clip(d / 0.09, 0, 1)
    g = np.clip(0.55 + 0.6 * (n - 0.5) + 0.5 * (n2 - 0.5), 0, 1) * front
    b = (1 - ub.smoothstep(0.03, 0.075, d)) * front
    yield np.c_[r, g, b], np.ones(len(p))


Pm, Um = ub.mesh_triangles(body)
sel = Pm.mean(axis=1)[:, 2] > 1.45
mimg = ub.rasterize(Pm[sel], Um[sel], 1024, frost_mask, np.tile(np.array([1.0, 0.0, 0.0]), (1024, 1024, 1)))
from PIL import Image
os.makedirs(os.path.join(OUT, "tex"), exist_ok=True)
Image.fromarray((np.flipud(np.clip(mimg, 0, 1)) * 255).astype(np.uint8)).save(os.path.join(OUT, "tex", "Escarcha.png"))
mask_img = bpy.data.images.load(os.path.join(OUT, "tex", "Escarcha.png"))
frost, pain = anatomy.frost_layer(skin, mask_img)

# foco de cámara en los ojos
focus = P.empty("FocoCara", loc=E + Vector((0, -0.02, 0)))
anatomy.parent_head(focus, rig)

# ---------------- conos ----------------
def head_mat(f):
    sc.frame_set(f)
    return rig.matrix_world @ rig.pose.bones[B + "Head"].matrix


# pivote del helado en la boca (sigue a la cabeza); el eje Z del pivote apunta del cono hacia la boca
pivot = P.empty("PivoteBoca", loc=MOUTH + Vector((0, -0.028, -0.036)))
axis = Vector((0, -0.78, -0.62)).normalized()  # desde la boca hacia abajo-adelante (donde queda la mano)
q = Vector((0, 0, 1)).rotation_difference(-axis)
pivot.rotation_euler = q.to_euler()
anatomy.parent_head(pivot, rig)
cone_m, cone_m_wafer, cone_m_scoops = P.cone("ConoBoca", scale=1.0)
cone_m.parent = pivot
# el tope de la bola de arriba queda en la boca: el cono se corre hacia atrás por el eje
top = 0.15 + 0.018 + sum((0.046 - 0.004 * i) * 1.45 for i in range(3)) - 0.012 - 0.055
cone_m.location = (0, 0, -top)
grip = P.empty("AgarreBoca", loc=(0, 0, 0.06))
grip.parent = cone_m

cone_h, _, cone_h_scoops = P.cone("ConoMano", scale=1.0)
hand_parent = rig.pose.bones[B + "LeftHand"]
cone_h.parent = rig
cone_h.parent_type = "BONE"
cone_h.parent_bone = B + "LeftHand"
cone_h.location = (0.02, 0.05, -0.03)    # en espacio del hueso (cola del hueso)
cone_h.rotation_euler = (math.radians(-80), 0, 0)
cone_cart, _, _ = P.cone("ConoCarrito", scale=1.15)
cone_cart.parent = cart
cone_cart.location = (0.25, -0.2, 1.06)

# IK de la mano izquierda al agarre del cono (sólo en mordidas)
ik = rig.pose.bones[B + "LeftHand"].constraints.new("IK")
ik.target = grip
ik.chain_count = 3
ik.use_tail = True
ik.influence = 0.0

# taza tibia (plano 26) en la boca
mug_piv = P.empty("PivoteTaza", loc=MOUTH + Vector((0, -0.02, -0.01)))
anatomy.parent_head(mug_piv, rig)
mug = P.prim("cyl", "Taza", C_UTIL, m=P.mat("TazaBlanca", "blanco", rough=0.25, coat=0.5), r=0.042, r2=0.045, h=0.10)
mug.parent = mug_piv
mug.location = (0, -0.06, -0.085)
mug.scale = (0.8, 0.8, 0.8)
mug.rotation_euler = (math.radians(40), 0, 0)
handle = P.prim("torus", "TazaAsa", C_UTIL, m=bpy.data.materials["TazaBlanca"], R=0.03, r=0.008)
handle.parent = mug
handle.location = (0.045, 0, 0)
handle.rotation_euler = (math.radians(90), 0, 0)
tea = P.prim("cyl", "TazaTe", C_UTIL, m=P.mat("Te", (0.35, 0.12, 0.03), rough=0.1), r=0.038, r2=0.038, h=0.005)
tea.parent = mug
tea.location = (0, 0, 0.04)
steam = []
for k in range(3):
    st = P.tube(f"Vapor{k}", [(0, 0, 0.05), (0.01 * (k - 1), 0.0, 0.09), (-0.01 * (k - 1), 0.0, 0.13), (0.008 * (k - 1), 0, 0.17)], 0.0035, C_UTIL,
                m=P.mat("Vapor", (1, 1, 1), rough=0.5, alpha=0.08))
    st.parent = mug
    steam.append(st)
grip_mug = P.empty("AgarreTaza", loc=(0.05, 0, -0.01))
grip_mug.parent = mug

# ---------------- set de laboratorio: 13 voluntarios ----------------
LAB_O = Vector((-40, 0, 0))
lab_floor = P.prim("cube", "LabPiso", C_LAB, m=P.mat("LabBlanco", (0.30, 0.34, 0.38), rough=0.5))
lab_floor.location, lab_floor.scale = LAB_O + Vector((0, 2, -0.05)), (20, 14, 0.1)
lab_wall = P.prim("cube", "LabMuro", C_LAB, m=P.mat("LabMuroMat", (0.02, 0.25, 0.32), rough=0.7))
lab_wall.location, lab_wall.scale = LAB_O + Vector((0, 3.2, 2)), (20, 0.1, 6)
for k in range(6):
    st = P.prim("cube", f"LabFranja{k}", C_LAB, m=P.mat("LabFranjaMat", (0.9, 0.95, 0.95), rough=0.4, emit=0.6))
    st.location, st.scale = LAB_O + Vector((-7.5 + k * 3, 3.1, 3.3)), (1.6, 0.05, 0.08)
lab_light = bpy.data.lights.new("LabLuz", "AREA")
lab_light.energy, lab_light.size = 900, 6
ll = bpy.data.objects.new("LabLuz", lab_light)
P.link(ll, C_LAB)
ll.location = LAB_O + Vector((0, -3, 5))
ll.rotation_euler = (math.radians(35), 0, 0)
def parent_bone(ob, rig_, bone):
    bpy.context.view_layer.update()
    mw = ob.matrix_world.copy()
    ob.parent = rig_
    ob.parent_type = "BONE"
    ob.parent_bone = bone
    bpy.context.view_layer.update()
    ob.matrix_world = mw


clone_parts = ["Cuerpo", "Polera", "Jeans", "Zapatillas", "Ojo.L", "Ojo.R", "Dientes", "Lengua"]
shirt_cols = [(1.0, 0.16, 0.10), (0.05, 0.45, 0.85), (0.95, 0.75, 0.05), (0.2, 0.7, 0.3), (0.6, 0.2, 0.8), (0.95, 0.4, 0.6), (0.1, 0.6, 0.6)]
clones = []
glass_m = P.mat("Vidrio", (0.95, 0.98, 1.0), rough=0.02, transmission=1.0)
water_m = P.mat("Agua", (0.75, 0.9, 1.0), rough=0.0, transmission=1.0)
ice_m = P.mat("Hielo", (0.9, 0.97, 1.0), rough=0.08, transmission=0.9)
straw_m = P.stripes_mat("Bombilla", "coral", "blanco", n=14, mode="z")
for i in range(13):
    x = (i - 6) * 0.62
    r2 = rig.copy()
    r2.name = f"RigVol{i}"
    r2.animation_data_clear()
    P.link(r2, C_LAB)
    r2.location = LAB_O + Vector((x, 0.4 + 0.15 * abs(i - 6) * 0.2, 0))
    for part in clone_parts:
        src = bpy.data.objects[part]
        o = src.copy()
        o.name = f"{part}Vol{i}"
        o.parent = r2
        P.link(o, C_LAB)
        for m in o.modifiers:
            if m.type == "ARMATURE":
                m.object = r2
            if m.type == "SUBSURF":
                m.render_levels = 0
                m.levels = 0
        if part == "Polera":
            o.material_slots[0].link = "OBJECT"
            pm = bpy.data.materials.get(f"PoleraVol{i % 7}")
            if pm is None:
                pm = P.mat(f"PoleraVol{i % 7}", shirt_cols[i % 7], rough=0.85)
            o.material_slots[0].material = pm
    # mismo pelo que el protagonista (los datos de curvas se comparten: Cycles los instancia)
    bpy.context.view_layer.update()
    hc = hair.copy()
    P.link(hc, C_LAB)
    hc.parent = None
    hc.matrix_world = r2.matrix_world @ hair.matrix_world
    parent_bone(hc, r2, B + "Head")
    # vaso con hielo y bombilla en la mano izquierda
    gl = P.prim("cyl", f"Vaso{i}", C_LAB, m=glass_m, r=0.035, r2=0.03, h=0.11)
    hb_ = r2.data.bones[B + "LeftHand"]
    gl.matrix_world = r2.matrix_world @ hb_.matrix_local @ Matrix.Translation((0.0, 0.07, -0.045)) @ Euler((math.radians(-90), 0, 0)).to_matrix().to_4x4()
    parent_bone(gl, r2, B + "LeftHand")
    gl.modifiers.new("S", "SOLIDIFY").thickness = 0.003
    wt = P.prim("cyl", f"AguaVaso{i}", C_LAB, m=water_m, r=0.031, r2=0.027, h=0.08)
    wt.parent, wt.location = gl, (0, 0, -0.012)
    for k in range(3):
        ic = P.prim("cube", f"Hielo{i}_{k}", C_LAB, m=ice_m)
        ic.parent, ic.location, ic.scale = gl, (0.012 * (k - 1), 0.008 * (k % 2), 0.02 + 0.006 * k), (0.018, 0.018, 0.018)
        ic.rotation_euler = (0.3 * k, 0.5, 0.2 * k)
        P.bevel(ic, 0.003, 2)
    sw = P.prim("cyl", f"Bombilla{i}", C_LAB, m=straw_m, r=0.004, r2=0.004, h=0.2)
    sw.parent, sw.location, sw.rotation_euler = gl, (0.008, 0, 0.07), (0.25, 0, 0)
    clones.append(r2)

# ---------------- set de la arteria ----------------
ART_O = Vector((40, 0, 0))
abg = P.prim("cube", "ArteriaFondo", C_ART, m=P.mat("FondoCarne", (0.06, 0.006, 0.012), rough=0.7))
abg.location, abg.scale = ART_O + Vector((0, 2.5, 0)), (12, 0.1, 12)
artery_big = P.tube("ArteriaGrande", [ART_O + Vector((x, 0.0, 0.25 * math.sin(x * 0.8))) for x in np.linspace(-3, 3, 9)], 0.32, C_ART,
                    m=P.mat("ArteriaPared", (0.95, 0.35, 0.38), rough=0.25, sss=0.5, alpha=0.35, coat=1.0))
artery_big.data.bevel_resolution = 8
cells = []
for k in range(26):
    cell = P.prim("cyl", f"Globulo{k}", C_ART, m=P.mat("Globulo", (0.85, 0.02, 0.03), rough=0.3, sss=0.3), r=0.06, r2=0.06, h=0.025)
    P.bevel(cell, 0.01, 3)
    cells.append(cell)
alight = bpy.data.lights.new("ArteriaLuz", "AREA")
alight.energy, alight.size = 900, 3
al = bpy.data.objects.new("ArteriaLuz", alight)
P.link(al, C_ART)
al.location = ART_O + Vector((0, -4, 3))
al.rotation_euler = (math.radians(55), 0, 0)

# ---------------- set macro del paladar (planos 11-12) ----------------
PAL_O = Vector((0, -40, 0))
C_PAL = P.collection("PaladarSet")
import bmesh as _bm
bmp = _bm.new()
rowsP = []
for i in range(40):
    y = -1.6 + 3.2 * i / 39
    row = []
    for j in range(40):
        x = -1.6 + 3.2 * j / 39
        z = 1.6 + 0.35 * math.cos(x * 0.9) * math.cos(y * 0.5) + 0.04 * math.sin(x * 9 + y * 3)  # bóveda con arrugas
        row.append(bmp.verts.new(PAL_O + Vector((x, y, z))))
    rowsP.append(row)
for i in range(39):
    for j in range(39):
        bmp.faces.new((rowsP[i][j], rowsP[i][j + 1], rowsP[i + 1][j + 1], rowsP[i + 1][j]))
pal_macro = P.mesh_obj("PaladarMacro", bmp, C_PAL, m=P.mat("PaladarMacroMat", (0.80, 0.30, 0.33), rough=0.25, sss=0.4, coat=0.8))
pal_macro.modifiers.new("Sub", "SUBSURF").render_levels = 1
pal_vessels = []
vm_ = bpy.data.materials["Vaso"]
for k in range(5):
    x0 = -1.2 + k * 0.6
    pts = [PAL_O + Vector((x0 + 0.15 * math.sin(t * 4 + k), -1.6 + 3.2 * t, 1.6 + 0.35 * math.cos((x0) * 0.9) * math.cos((-1.6 + 3.2 * t) * 0.5) - 0.06)) for t in np.linspace(0, 1, 9)]
    v_ = P.tube(f"VasoMacro{k}", pts, 0.07 if k % 2 == 0 else 0.045, C_PAL, m=vm_)
    pal_vessels.append(v_)
pal_light = bpy.data.lights.new("PaladarLuz", "AREA")
pal_light.energy, pal_light.size, pal_light.color = 600, 3, (1.0, 0.9, 0.85)
plo = bpy.data.objects.new("PaladarLuz", pal_light)
P.link(plo, C_PAL)
plo.location = PAL_O + Vector((1.5, -2.0, -0.5))
plo.rotation_euler = (Vector(PAL_O + Vector((0, 0, 1.5))) - plo.location).to_track_quat("-Z", "Y").to_euler()
pal_bg = P.prim("sphere", "PaladarFondo", C_PAL, m=P.mat("BocaFondo", (0.12, 0.012, 0.025), rough=0.8), r=5.0)
pal_bg.location = PAL_O + Vector((0, 0, 1.0))

# ---------------- set del texto gigante ----------------
TXT_O = Vector((0, 40, 0))
tbg = P.prim("cube", "TextoFondo", C_TXT, m=P.mat("TextoFondoMat", (0.005, 0.16, 0.24), rough=0.8))
tbg.location, tbg.scale = TXT_O + Vector((0, 3, 1)), (20, 0.1, 14)
tfl = P.prim("cube", "TextoPiso", C_TXT, m=P.mat("TextoPisoMat", (0.005, 0.12, 0.18), rough=0.8))
tfl.location, tfl.scale = TXT_O + Vector((0, 0, -0.05)), (20, 8, 0.1)
tlight = bpy.data.lights.new("TextoLuz", "AREA")
tlight.energy, tlight.size = 700, 4
tl = bpy.data.objects.new("TextoLuz", tlight)
P.link(tl, C_TXT)
tl.location = TXT_O + Vector((-2, -5, 5))
tl.rotation_euler = (math.radians(45), 0, math.radians(-20))
letters = []
ymat = P.mat("LetraAmarilla", "amarillo", rough=0.35, coat=0.6)
wmat = P.mat("LetraBlancaG", "blanco", rough=0.35, coat=0.6)
LINES = (("GANGLIO", 2.35, ymat, 0), ("NEURALGIA", 1.85, ymat, 0), ("ESFENO", 1.20, wmat, 1), ("PALATINA", 0.70, wmat, 1))
for li, (word, z, m, row) in enumerate(LINES):
    xs = (np.arange(len(word)) - (len(word) - 1) / 2) * 0.25
    for k, ch in enumerate(word):
        t = P.text3d(f"Letra{li}_{k}", ch, size=0.36, extrude=0.07, bevel_d=0.012, coll=C_TXT, m=m)
        t.location = TXT_O + Vector((xs[k], 0, z))
        t.rotation_euler = (math.pi / 2, 0, 0)
        letters.append((t, row, k + (7 if li in (1, 3) and row == 0 else 0) + (6 if li == 3 else 0)))

# ---------------- domo para los planos del interior de la cabeza ----------------
dome = P.prim("sphere", "DomoInterior", C_UTIL, r=2.5, u=48, v=24)
dm = P.mat("DomoMat", (0.02, 0.32, 0.42), rough=1.0)
nt_, lk_, b_ = P.nodes(dm)
for n_ in list(nt_):
    if n_.type not in ("OUTPUT_MATERIAL",):
        nt_.remove(n_)
emi = nt_.new("ShaderNodeEmission")
tc_ = nt_.new("ShaderNodeTexCoord")
sep_ = nt_.new("ShaderNodeSeparateXYZ")
rmp = nt_.new("ShaderNodeValToRGB")
rmp.color_ramp.elements[0].color = (0.005, 0.08, 0.12, 1)
rmp.color_ramp.elements[1].color = (0.03, 0.42, 0.55, 1)
lk_.new(tc_.outputs["Generated"], sep_.inputs[0])
lk_.new(sep_.outputs["Z"], rmp.inputs["Fac"])
lk_.new(rmp.outputs["Color"], emi.inputs["Color"])
emi.inputs["Strength"].default_value = 1.0
lk_.new(emi.outputs[0], nt_["Material Output"].inputs["Surface"])
dome.data.materials.append(dm)
for p in dome.data.polygons:
    p.use_smooth = True
dome.location = E
dome.visible_shadow = False
ikl = bpy.data.lights.new("LuzInterior", "AREA")
ikl.energy, ikl.size, ikl.color = 60, 0.8, (1.0, 0.95, 0.9)
ilo = bpy.data.objects.new("LuzInterior", ikl)
P.link(ilo, C_UTIL)
ilo.location = E + Vector((0.8, -0.9, 0.7))
ilo.rotation_euler = (Vector(E) - ilo.location).to_track_quat("-Z", "Y").to_euler()
ikl2 = bpy.data.lights.new("LuzInteriorRim", "AREA")
ikl2.energy, ikl2.size, ikl2.color = 40, 0.6, (0.7, 0.9, 1.0)
ilo2 = bpy.data.objects.new("LuzInteriorRim", ikl2)
P.link(ilo2, C_UTIL)
ilo2.location = E + Vector((-0.6, 0.8, 0.5))
ilo2.rotation_euler = (Vector(E) - ilo2.location).to_track_quat("-Z", "Y").to_euler()

# ---------------- utilidades de animación ----------------
def key_vis(obj, intervals, total):
    """Visible sólo en los intervalos [f0, f1)."""
    obj.hide_render = True
    obj.keyframe_insert("hide_render", frame=1)
    for f0, f1 in intervals:
        obj.hide_render = False
        obj.keyframe_insert("hide_render", frame=f0)
        obj.hide_render = True
        obj.keyframe_insert("hide_render", frame=f1)
    if obj.animation_data and obj.animation_data.action:
        for fc in anim._fcurves(obj.animation_data.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"


def set_val(sock, f, v, interp="LINEAR"):
    sock.default_value = v
    sock.keyframe_insert("default_value", frame=f)


SK_OBJS = [o for o in bpy.data.objects if o.type == "MESH" and o.data.shape_keys and not o.name.endswith(tuple(f"Vol{i}" for i in range(13)))]
SK_NAMES = sorted({k.name for o in SK_OBJS for k in o.data.shape_keys.key_blocks[1:]})


def expr(f, **vals):
    """Expresión completa en el cuadro f (lo no indicado vuelve a 0)."""
    for o in SK_OBJS:
        kb = o.data.shape_keys.key_blocks
        for n in SK_NAMES:
            if n in kb:
                kb[n].value = vals.get(n.replace("-", "_"), 0.0)
                kb[n].keyframe_insert("value", frame=f)


ACTS = {}


def act(name):
    if name not in ACTS:
        ACTS[name] = anim.load_action(os.path.join(MIX, name + ".fbx"), rig)
    return ACTS[name]


rig.animation_data_create()
rig.animation_data.action = None
tracks = [rig.animation_data.nla_tracks.new(), rig.animation_data.nla_tracks.new()]
track = tracks[0]


def strip(f0, f1, name, a0, speed=1.0, repeat=1.0, rig_=None, trk=None):
    a = act(name)
    t = trk or track
    if trk is None:
        t = tracks[strip.n % 2]
        strip.n += 1
    s = t.strips.new(f"{name}_{f0}", int(f0), a)
    if hasattr(s, "action_slot") and a.slots:
        s.action_slot = a.slots[0]
    length = (f1 - f0) * speed / repeat
    s.action_frame_start = a0
    s.action_frame_end = a0 + length
    s.scale = 1.0 / speed
    s.repeat = repeat
    s.extrapolation = "NOTHING"
    s.blend_in = s.blend_out = 0
    return s


strip.n = 0
cams = []


def camera(name, f0, f1, keys, lens=50, fstop=2.8, focus_obj=None, shake=None):
    """keys: lista de (f, loc, target)."""
    cd = bpy.data.cameras.new(name)
    cd.lens, cd.sensor_fit, cd.sensor_height = lens, "VERTICAL", 24.0
    cd.dof.use_dof = True
    cd.dof.aperture_fstop = fstop
    cd.dof.focus_object = focus_obj or focus
    cam = bpy.data.objects.new(name, cd)
    P.link(cam)
    for f, loc, tgt in keys:
        cam.location = loc
        cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
    if cam.animation_data:
        for fc in anim._fcurves(cam.animation_data.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"
                kp.easing = "AUTO"
            if shake and fc.data_path == "rotation_euler":
                mod = fc.modifiers.new("NOISE")
                mod.scale, mod.strength = shake[2], shake[3]
                mod.use_restricted_range = True
                mod.frame_start, mod.frame_end = shake[0], shake[1]
                mod.blend_in, mod.blend_out = 1, 6
    m = sc.timeline_markers.new(name, frame=f0)
    m.camera = cam
    cams.append(cam)
    return cam


def head_world(f, off=(0, 0, 0)):
    sc.frame_set(f)
    M = rig.matrix_world @ rig.pose.bones[B + "Head"].matrix
    return M @ (rig.data.bones[B + "Head"].matrix_local.inverted() @ (E + Vector(off)))


def front_cam(f, dist, side=0.0, up=0.0, aim_down=0.0):
    """Cámara frente a la cara del personaje (que mira a -Y)."""
    h = head_world(f)
    loc = h + Vector((side, -dist, up))
    tgt = h + Vector((0, 0, -aim_down))
    return loc, tgt


# ---------------- PLANOS ----------------
T = {  # (inicio, fin) en segundos, según words.json
    1: (0.00, 1.94), 2: (1.94, 2.83), 3: (2.83, 4.17), 4: (4.17, 6.62), 5: (6.62, 7.70), 6: (7.70, 8.74),
    7: (8.74, 9.86), 8: (9.86, 12.10), 9: (12.10, 14.98), 10: (14.98, 16.85), 31: (16.85, 18.86), 11: (18.86, 21.48),
    12: (21.48, 24.62), 13: (24.62, 27.31), 14: (27.31, 30.12), 15: (30.12, 32.05), 32: (32.05, 33.65), 16: (33.65, 35.65),
    17: (35.65, 37.90), 18: (37.90, 40.69), 33: (40.69, 42.04), 19: (42.04, 44.27), 20: (44.27, 46.64), 21: (46.64, 49.32),
    22: (49.32, 52.13), 23: (52.13, 55.74), 24: (55.74, 56.84), 34: (56.84, 58.54), 25: (58.54, 60.55), 26: (60.55, 62.50),
    27: (62.50, 64.55), 35: (64.55, 66.10), 28: (66.10, 68.42), 29: (68.42, 70.90), 30: (70.90, 72.10),
}
FR = {k: (F(a), F(b)) for k, (a, b) in T.items()}
END = FR[30][1]
sc.frame_start, sc.frame_end = 1, END - 1
INTERIOR = [4, 10, 31, 13, 15, 32, 21, 22, 25]
BITE = [1, 2, 9, 30]

# --- actuación por plano (pistas NLA) ---
plan = {
    1: ("Drinking", 95), 2: ("Drinking", 120), 3: ("Focus", 6), 4: ("Happy_Idle", 1), 5: ("Shrugging", 4),
    6: ("Happy_Idle", 1), 7: ("Happy_Idle", 1), 8: ("Arm_Gesture", 6), 9: ("Drinking", 70), 10: ("Happy_Idle", 1),
    11: ("Happy_Idle", 10), 12: ("Happy_Idle", 20), 13: ("Happy_Idle", 1), 14: ("Happy_Idle", 15), 15: ("Happy_Idle", 30),
    16: ("Focus", 12), 17: ("Happy_Idle", 1), 18: ("Happy_Idle", 1), 19: ("Happy_Idle", 1), 20: ("Happy_Idle", 1),
    21: ("Happy_Idle", 1), 22: ("Happy_Idle", 10), 23: ("Happy_Idle", 1), 24: ("Head_Nod_Yes", 10), 25: ("Happy_Idle", 5),
    26: ("Drinking", 80), 27: ("Relieved_Sigh", 1), 28: ("Thinking", 18), 29: ("Shaking_Head_No", 1), 30: ("Drinking", 92),
    31: ("Happy_Idle", 30), 32: ("Happy_Idle", 40), 33: ("Happy_Idle", 1), 34: ("Happy_Idle", 10), 35: ("Happy_Idle", 20),
}
speeds = {31: 0.5, 32: 0.5, 33: 0.5, 34: 0.6, 35: 0.6, 9: 1.9, 4: 0.5, 10: 0.5, 11: 0.5, 12: 0.5, 13: 0.5, 15: 0.5, 21: 0.5, 22: 0.5, 25: 0.5, 2: 0.5, 16: 0.25, 7: 0.8, 19: 0.5, 20: 0.5, 17: 0.5, 18: 0.5, 23: 0.5, 14: 0.5}
for k, (name, a0) in sorted(plan.items(), key=lambda kv: FR[kv[0]][0]):
    f0, f1 = FR[k]
    sp = speeds.get(k, 1.0)
    rep = 1.0
    if name in ("Happy_Idle",) and (f1 - f0) * sp > 55:
        rep = math.ceil((f1 - f0) * sp / 55)
        a_len = (f1 - f0) * sp / rep
        s = strip(f0, f1, name, a0, speed=sp, repeat=rep)
    elif k == 9:
        s = strip(f0, f1, name, 70, speed=sp, repeat=2.0)
    else:
        s = strip(f0, f1, name, a0, speed=sp)
# clones del lab: tomando agua desfasados
for i, r2 in enumerate(clones):
    r2.animation_data_create()
    tr = r2.animation_data.nla_tracks.new()
    if i == 6:  # el del centro: toma agua y después le duele (plano 33)
        strip(FR[17][0], FR[18][1], "Drinking", 40 + (i * 7) % 30, speed=1.0, rig_=r2, trk=tr)
        strip(FR[33][0], FR[33][1], "Focus", 8, speed=0.6, rig_=r2, trk=tr)
    else:
        strip(FR[17][0], FR[33][1], "Drinking", 40 + (i * 7) % 30, speed=1.0, rig_=r2, trk=tr)

# --- IK de mordida ---
for k in sorted(FR):
    f0, f1 = FR[k]
    ik.influence = 1.0 if k in BITE else 0.0
    ik.keyframe_insert("influence", frame=f0)
ik.target = grip
# taza: segundo IK
ik2 = rig.pose.bones[B + "LeftHand"].constraints.new("IK")
ik2.target, ik2.chain_count, ik2.use_tail = grip_mug, 3, True
for k in sorted(FR):
    ik2.influence = 1.0 if k == 26 else 0.0
    ik2.keyframe_insert("influence", frame=FR[k][0])
for c in (ik, ik2):
    pass
for fc in anim._fcurves(rig.animation_data.action) if rig.animation_data.action else []:
    for kp in fc.keyframe_points:
        kp.interpolation = "CONSTANT"

# mordidas: el pivote del cono se aleja y vuelve (plano 9) y las bolas desaparecen
def key_loc(ob, f, loc):
    ob.location = loc
    ob.keyframe_insert("location", frame=f)


f0, f1 = FR[1]
Z0 = -top
key_loc(cone_m, 1, (0, 0, Z0))
f9a, f9b = FR[9]
cyc = (f9b - f9a) / 2
for c in range(2):
    a = f9a + c * cyc
    key_loc(cone_m, int(a), (0, 0, Z0 - 0.09))
    key_loc(cone_m, int(a + cyc * 0.45), (0, 0, Z0))
    key_loc(cone_m, int(a + cyc * 0.7), (0, 0, Z0 - 0.05))
key_loc(cone_m, FR[30][0], (0, 0, Z0 - 0.05))
key_loc(cone_m, FR[30][0] + 10, (0, 0, Z0))
# bolas: plano 9 se come 2 de 3 (la de arriba, luego la del medio)
for s_, fb in ((cone_m_scoops[2], int(f9a + cyc * 0.45)), (cone_m_scoops[1], int(f9a + cyc * 1.45))):
    s_.scale = (1, 1, 1)
    s_.keyframe_insert("scale", frame=fb - 1)
    s_.scale = (0.001, 0.001, 0.001)
    s_.keyframe_insert("scale", frame=fb + 1)
    s_.scale = (1, 1, 1)
    s_.keyframe_insert("scale", frame=FR[30][0])
for s_ in cone_m_scoops:
    if s_.animation_data:
        for fc in anim._fcurves(s_.animation_data.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"

# cono que aparece en la mano (plano 8) con "pop"
f8a, f8b = FR[8]
pop_f = f8b - 16
for f, s_ in ((1, 0.001), (pop_f, 0.001), (pop_f + 4, 1.15), (pop_f + 7, 1.0)):
    cone_h.scale = (s_, s_, s_)
    cone_h.keyframe_insert("scale", frame=f)
# el XL del cartel brilla
xl_glow = P.mat("BrilloXL", "amarillo", emit=0.0)
for f, e in ((f8a, 0.0), (f8a + 18, 0.0), (f8a + 24, 3.0), (f8a + 34, 0.8), (f8a + 44, 3.0), (f8b, 0.5)):
    pass

# --- expresiones ---
expr(FR[1][0], eye_left_closure=0.55, eye_right_closure=0.55, mouth_open=0.45, eyebrows_left_up=0.2, eyebrows_right_up=0.2)
expr(FR[1][0] + 40, eye_left_closure=0.7, eye_right_closure=0.7, mouth_open=0.45, eyebrows_left_inner_up=0.5, eyebrows_right_inner_up=0.5)
expr(FR[2][0], eye_left_opened_up=0.25, eye_right_opened_up=0.25, eyebrows_left_up=1.0, eyebrows_right_up=1.0, mouth_open=0.55)
expr(FR[3][0], eye_left_closure=0.85, eye_right_closure=0.85, eyebrows_left_inner_up=0.7, eyebrows_right_inner_up=0.7, eyebrows_left_down=0.5,
     eyebrows_right_down=0.5, mouth_depression_retraction=0.65, nose_left_elevation=0.5, nose_right_elevation=0.5)
expr(FR[4][0], eyebrows_left_up=0.2, eyebrows_right_up=0.2)
expr(FR[5][0], eyebrows_left_up=0.9, eyebrows_right_up=0.9, mouth_depression=0.4)
expr(FR[7][0], mouth_corner_puller=0.35)
expr(FR[8][0], mouth_corner_puller=0.5, eyebrows_left_up=0.4, eyebrows_right_up=0.4)
expr(FR[9][0], eyebrows_left_down=0.6, eyebrows_right_down=0.6, eye_left_slit=0.5, eye_right_slit=0.5, mouth_open=0.5)
expr(FR[10][0], mouth_open=0.3)
expr(FR[14][0])
expr(FR[16][0], eye_left_closure=0.8, eye_right_closure=0.8, eyebrows_left_inner_up=0.7, eyebrows_right_inner_up=0.7, mouth_depression_retraction=0.5)
expr(FR[17][0], mouth_pursing=0.5, eye_left_slit=0.2, eye_right_slit=0.2)
expr(FR[33][0], eye_left_closure=0.85, eye_right_closure=0.85, eyebrows_left_inner_up=0.7, eyebrows_right_inner_up=0.7, eyebrows_left_down=0.5,
     eyebrows_right_down=0.5, mouth_depression_retraction=0.65)
expr(FR[34][0], mouth_compression=0.6, eyebrows_left_down=0.3, eyebrows_right_down=0.3, eye_left_slit=0.3, eye_right_slit=0.3)
expr(FR[35][0], mouth_corner_puller=0.7, eyebrows_left_up=0.3, eyebrows_right_up=0.3)
expr(FR[24][0], eye_left_slit=0.25, eye_right_slit=0.25, mouth_compression=0.4)
expr(FR[26][0], eye_left_closure=0.4, eye_right_closure=0.4, mouth_pursing=0.3)
expr(FR[27][0], eye_left_closure=0.5, eye_right_closure=0.5, mouth_corner_puller=0.45, eyebrows_left_up=0.2, eyebrows_right_up=0.2)
expr(FR[27][0] + 40, mouth_corner_puller=0.6, eyebrows_left_up=0.3, eyebrows_right_up=0.3)
expr(FR[28][0], eyebrows_left_up=0.5, eyebrows_right_down=0.4, mouth_corner_puller=0.25, eye_left_slit=0.2, eye_right_slit=0.2)
expr(FR[29][0], eye_left_slit=0.35, eye_right_slit=0.35, mouth_corner_puller=0.4)
expr(FR[30][0], eye_left_closure=0.55, eye_right_closure=0.55, mouth_open=0.45, eyebrows_left_up=0.2, eyebrows_right_up=0.2)
# parpadeos en planos largos
for fb in (FR[7][0] + 20, FR[8][0] + 30, FR[27][0] + 70, FR[28][0] + 25):
    for o in SK_OBJS:
        kb = o.data.shape_keys.key_blocks
        for side in ("left", "right"):
            n = f"eye-{side}-closure"
            if n in kb:
                for df, v in ((-1, kb[n].value), (1, 1.0), (4, 0.0)):
                    kb[n].value = v
                    kb[n].keyframe_insert("value", frame=fb + df)

# --- materiales animados: escarcha, dolor, fantasma ---
fs = frost.outputs[0]
for f, v in ((1, 0.25), (FR[1][1] - 2, 0.50), (FR[2][0] + 3, 0.78), (FR[3][0], 0.78), (FR[3][0] + 1, 0.0), (FR[30][0], 0.25), (END, 0.40)):
    set_val(fs, f, v)
ps = pain.outputs[0]
set_val(ps, 1, 0.0)
for k_ in (3, 16, 33):
    a_, b_ = FR[k_]
    set_val(ps, a_ - 1, 0.0)
    f = a_
    while f + 6 < b_ - 2:
        set_val(ps, f, 0.9)
        set_val(ps, f + 6, 0.35)
        f += 12
    set_val(ps, b_ - 1, 0.3)
    set_val(ps, b_, 0.0)
gs = ghost.outputs[0]
for k in sorted(FR):
    v = 1.0 if k in INTERIOR else (0.55 if k == 14 else 0.0)
    set_val(gs, FR[k][0], v)
for fc in anim._fcurves(skin.node_tree.animation_data.action):
    if "Fantasma" in fc.data_path:
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT"

# vasos: se encogen (11) y se abren (12); color azul -> rojo
vm = bpy.data.materials["Vaso"]
vb = vm.node_tree.nodes["Principled BSDF"]
for ob in org["vasos"]:
    r0 = ob.data.bevel_depth
    for f, k in ((FR[10][0], 1.0), (FR[11][0] + 5, 1.0), (FR[11][0] + 30, 0.45), (FR[12][0], 0.45), (FR[12][0] + 8, 1.7), (FR[12][1], 1.5), (FR[22][0], 1.0)):
        ob.data.bevel_depth = r0 * k
        ob.data.keyframe_insert("bevel_depth", frame=f)
for ob in pal_vessels:
    r0 = ob.data.bevel_depth
    for f, k in ((FR[11][0], 1.0), (FR[11][0] + 12, 1.0), (FR[11][0] + 45, 0.4), (FR[12][0], 0.4), (FR[12][0] + 8, 1.8), (FR[12][1], 1.55)):
        ob.data.bevel_depth = r0 * k
        ob.data.keyframe_insert("bevel_depth", frame=f)
for f, col, em in ((FR[10][0], (0.75, 0.03, 0.04), 0.0), (FR[11][0] + 30, (0.25, 0.25, 0.7), 0.0), (FR[12][0], (0.25, 0.25, 0.7), 0.0),
                   (FR[12][0] + 8, (0.95, 0.05, 0.03), 2.5), (FR[12][1], (0.85, 0.04, 0.03), 0.8), (FR[22][0], (0.85, 0.04, 0.03), 1.5), (FR[22][1], (0.85, 0.04, 0.03), 0.3)):
    vb.inputs["Base Color"].default_value = (*col, 1)
    vb.inputs["Base Color"].keyframe_insert("default_value", frame=f)
    vb.inputs["Emission Color"].default_value = (*col, 1)
    vb.inputs["Emission Color"].keyframe_insert("default_value", frame=f)
    vb.inputs["Emission Strength"].default_value = em
    vb.inputs["Emission Strength"].keyframe_insert("default_value", frame=f)
# paladar: se escarcha (10) y se entibia con la lengua (25)
pb = bpy.data.materials["PaladarMat"].node_tree.nodes["Principled BSDF"]
for f, col, em, ec in ((1, (0.78, 0.26, 0.30), 0.0, (1, 0.5, 0.2)), (FR[10][0] + 40, (0.78, 0.26, 0.30), 0.0, (1, 0.5, 0.2)), (FR[10][0] + 70, (0.75, 0.88, 1.0), 0.6, (0.6, 0.85, 1.0)),
                       (FR[11][1], (0.75, 0.88, 1.0), 0.6, (0.6, 0.85, 1.0)), (FR[25][0], (0.75, 0.88, 1.0), 0.6, (0.6, 0.85, 1.0)), (FR[25][0] + 45, (0.95, 0.45, 0.25), 1.5, (1.0, 0.45, 0.1)), (FR[25][1], (0.85, 0.35, 0.30), 0.6, (1.0, 0.45, 0.1))):
    pb.inputs["Base Color"].default_value = (*col, 1)
    pb.inputs["Base Color"].keyframe_insert("default_value", frame=f)
    pb.inputs["Emission Color"].default_value = (*ec, 1)
    pb.inputs["Emission Color"].keyframe_insert("default_value", frame=f)
    pb.inputs["Emission Strength"].default_value = em
    pb.inputs["Emission Strength"].keyframe_insert("default_value", frame=f)
# lengua sube al paladar (25)
lg = org["lengua"]
for f, dz in ((FR[25][0], 0.0), (FR[25][0] + 25, 0.014), (FR[25][1], 0.014)):
    lg.location = lg.location
    lg.delta_location = (0, 0, dz)
    lg.keyframe_insert("delta_location", frame=f)
# bocado toca el paladar (10)
bc = org["bocado"]
for f, dz in ((FR[10][0], -0.012), (FR[10][0] + 30, 0.004), (FR[10][1], 0.004)):
    bc.delta_location = (0, 0, dz)
    bc.keyframe_insert("delta_location", frame=f)
# trigémino se enciende (13) y la rama V1 pulsa hacia la frente (15)
nmat = bpy.data.materials["Nervio"]
nb = nmat.node_tree.nodes["Principled BSDF"]
nb.inputs["Emission Color"].default_value = (1.0, 0.8, 0.2, 1)
for f, e in ((1, 0.0), (FR[13][0], 0.0), (FR[13][0] + 20, 4.0), (FR[13][0] + 40, 1.5), (FR[15][0], 1.5), (FR[15][0] + 15, 5.0), (FR[15][0] + 30, 1.5),
             (FR[15][0] + 45, 5.0), (FR[15][1], 1.5), (FR[22][0], 2.5), (FR[22][1], 1.0)):
    set_val(nb.inputs["Emission Strength"], f, e)
# signos de interrogación giran sobre el cerebro (15)
for i, qob in enumerate(org["preguntas"]):
    qob.delta_rotation_euler = (0, 0, 0)
    for f, s_ in ((FR[32][0], 0.001), (FR[32][0] + 5 + 3 * i, 1.2), (FR[32][0] + 10 + 3 * i, 1.0)):
        qob.scale = (s_, s_, s_)
        qob.keyframe_insert("scale", frame=f)
    for f, rz in ((FR[32][0], 0), (FR[32][1], 4.0)):
        qob.delta_rotation_euler = (0, 0, rz)
        qob.keyframe_insert("delta_rotation_euler", frame=f)
# cerebro "tibio" (4)
bm_ = bpy.data.materials["CerebroLMat"].node_tree.nodes["Principled BSDF"]
for name in ("CerebroLMat", "CerebroRMat", "CereboloMat"):
    pass
for mname in ("CerebroLMat", "CerebroRMat"):
    b_ = bpy.data.materials[mname].node_tree.nodes["Principled BSDF"]
    b_.inputs["Emission Color"].default_value = (1.0, 0.45, 0.2, 1)
    for f, e in ((1, 0.0), (FR[4][0], 0.6), (FR[4][1], 0.6), (FR[5][0], 0.0), (FR[21][0], 0.25), (FR[22][0], 0.0)):
        set_val(b_.inputs["Emission Strength"], f, e)

# copo de nieve que rebota en la frente (4)
import bmesh
bmf = bmesh.new()
for a in range(6):
    ang = a * math.pi / 3
    for (x0, y0, x1, y1) in ((0, 0, 1.0, 0.0), (0.55, 0.0, 0.8, 0.25), (0.55, 0.0, 0.8, -0.25)):
        pts = []
        for (x, y) in ((x0, y0), (x1, y1)):
            pts.append((x * math.cos(ang) - y * math.sin(ang), x * math.sin(ang) + y * math.cos(ang)))
        dx, dy = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
        L = math.hypot(dx, dy)
        nx, ny = -dy / L * 0.07, dx / L * 0.07
        vs = [bmf.verts.new((pts[0][0] + nx, pts[0][1] + ny, 0)), bmf.verts.new((pts[1][0] + nx, pts[1][1] + ny, 0)),
              bmf.verts.new((pts[1][0] - nx, pts[1][1] - ny, 0)), bmf.verts.new((pts[0][0] - nx, pts[0][1] - ny, 0))]
        bmf.faces.new(vs)
flake = P.mesh_obj("Copo", bmf, C_UTIL, smooth=False, m=P.mat("CopoMat", (0.85, 0.95, 1.0), rough=0.1, emit=0.8))
flake.modifiers.new("S", "SOLIDIFY").thickness = 0.08
flake.visible_shadow = False
flake.scale = (0.03, 0.03, 0.03)
f4a, f4b = FR[4]
hw = head_world(f4a)
for f, off in ((f4a, (0.05, -0.55, 0.25)), (f4a + 28, (0.0, -0.035, 0.07)), (f4a + 50, (-0.12, -0.35, 0.3)), (f4b, (-0.25, -0.6, 0.45))):
    flake.location = hw + Vector(off)
    flake.keyframe_insert("location", frame=f)
for f, r in ((f4a, 0), (f4b, 9)):
    flake.rotation_euler = (1.2, r, r * 0.3)
    flake.keyframe_insert("rotation_euler", frame=f)

# cristales de hielo que estallan (2)
rng = np.random.default_rng(3)
shards = []
for k in range(22):
    sh = P.prim("ico", f"Cristal{k}", C_UTIL, m=P.mat("CristalHielo", (0.70, 0.88, 1.0), rough=0.15, emit=1.2, coat=1.0), sub=1, r=0.0025)
    for p in sh.data.polygons:
        p.use_smooth = False
    sh.visible_shadow = False
    sh.location = FOREHEAD + Vector(((rng.random() - 0.5) * 0.08, 0.0, (rng.random() - 0.5) * 0.05))
    anatomy.parent_head(sh, rig)
    d = Vector(((rng.random() - 0.5) * 2.4, -0.25 - 0.2 * rng.random(), 0.3 + rng.random() * 1.4)).normalized()
    f2 = FR[2][0]
    for f, s_, mv in ((1, 0.001, 0), (f2, 0.001, 0), (f2 + 1, 1.0 + rng.random(), 0.0), (f2 + 14, 0.6, 0.12 + 0.08 * rng.random()), (f2 + 22, 0.001, 0.2)):
        sh.scale = (s_, s_, s_)
        sh.keyframe_insert("scale", frame=f)
        sh.delta_location = d * mv
        sh.keyframe_insert("delta_location", frame=f)
    shards.append(sh)

# arteria del estudio: se ensancha (19) y vuelve (20); glóbulos fluyendo
for f, r in ((1, 0.30), (FR[19][0], 0.30), (FR[19][0] + 40, 0.55), (FR[19][1], 0.58), (FR[20][0] + 25, 0.30), (FR[20][1], 0.30)):
    artery_big.data.bevel_depth = r
    artery_big.data.keyframe_insert("bevel_depth", frame=f)
for k, cell in enumerate(cells):
    x0 = -3.2 + (k % 13) * 0.5
    yz = ((k // 13) - 0.5) * 0.25
    for f, dx in ((FR[19][0], 0), (FR[20][1], 3.5)):
        x = ((x0 + dx + 3.2) % 6.4) - 3.2 if f != FR[19][0] else x0
        cell.location = ART_O + Vector((x0 + dx * (1 if f != FR[19][0] else 0), yz, 0.25 * math.sin(x0 * 0.8) + yz * 0.5))
        cell.rotation_euler = (k, k * 0.5, 0)
        cell.keyframe_insert("location", frame=f)

# letras que caen y rebotan (23)
f23 = FR[23][0]
wt = [w for w in words if w["s"] >= 52.0 and w["s"] < 56.0]
t_g = next(w["s"] for w in wt if w["w"].lower().startswith("gangli"))
t_e = next(w["s"] for w in wt if w["w"].lower().startswith("esfeno"))
for t, row, k in letters:
    pass
for t, row, k in letters:
    base = t.location.copy()
    tstart = F(t_g if row == 0 else t_e) + k * 1.2
    for f, dz, s_ in ((1, 3.0, 1.0), (int(tstart), 3.0, 1.0), (int(tstart) + 6, 0.0, 1.0), (int(tstart) + 8, 0.06, 1.0), (int(tstart) + 11, 0.0, 1.0)):
        t.delta_location = (0, 0, dz)
        t.keyframe_insert("delta_location", frame=f)

# --- visibilidad por plano ---
def frames_of(ks):
    return [FR[k] for k in ks]


ALL = list(FR)
plaza_shots = [k for k in ALL if k not in (11, 12, 17, 18, 33, 19, 20, 23)]
for ob in [o for o in list(C_PLAZA.all_objects) if o is not None]:
    if ob.type in ("MESH", "CURVE", "FONT"):
        key_vis(ob, frames_of([k for k in plaza_shots if k not in INTERIOR]), END)
for ob in [o for o in list(C_LAB.all_objects) if o is not None]:
    key_vis(ob, frames_of([17, 18, 33]), END)
for ob in [o for o in list(C_ART.all_objects) if o is not None]:
    key_vis(ob, frames_of([19, 20]), END)
for ob in [o for o in list(C_TXT.all_objects) if o is not None]:
    key_vis(ob, frames_of([23]), END)
for ob in [o for o in list(C_PAL.all_objects) if o is not None]:
    key_vis(ob, frames_of([11, 12]), END)
char_parts = ["Cuerpo", "Polera", "Jeans", "Zapatillas", "Ojo.L", "Ojo.R"]
for n in char_parts:
    if not n.startswith("Ojo"):
        key_vis(bpy.data.objects[n], frames_of(plaza_shots), END)
for n in ("Dientes", "Lengua"):
    key_vis(bpy.data.objects[n], frames_of([k for k in plaza_shots if k not in INTERIOR and k != 14]), END)
key_vis(hair, frames_of([k for k in plaza_shots if k not in INTERIOR]), END)
SHOW = {
    "cerebro": [4, 15, 32, 21, 22], "paladar": [10, 31, 13, 25], "lengua": [10, 31, 25], "vasos": [10, 31, 22],
    "nervios": [13, 14, 15, 32], "arteria": [22],
}
for key, ks in SHOW.items():
    grp = org[key] if isinstance(org[key], list) else [org[key]]
    for ob in grp:
        key_vis(ob, frames_of(ks), END)
key_vis(org["bocado"], frames_of([10, 31]), END)
for qob in org["preguntas"]:
    key_vis(qob, frames_of([32]), END)
key_vis(flake, frames_of([4]), END)
key_vis(dome, frames_of(INTERIOR + [14]), END)
for L_ in (ikl, ikl2):
    for k in sorted(FR):
        L_.energy = (60 if L_ is ikl else 40) if k in INTERIOR + [14] else 0.0
        L_.keyframe_insert("energy", frame=FR[k][0])
for n in ("Ojo.L", "Ojo.R"):
    key_vis(bpy.data.objects[n], frames_of([k for k in plaza_shots if k not in INTERIOR]), END)
for sh in shards:
    key_vis(sh, frames_of([2]), END)
for o in [cone_m] + [c for c in cone_m.children_recursive]:
    if o.type in ("MESH", "CURVE"):
        key_vis(o, frames_of(BITE), END)
for o in [cone_h] + [c for c in cone_h.children_recursive]:
    if o.type in ("MESH", "CURVE"):
        key_vis(o, frames_of([8, 29]), END)
for o in [cone_cart] + [c for c in cone_cart.children_recursive]:
    if o.type in ("MESH", "CURVE"):
        key_vis(o, frames_of([7, 28]), END)
for o in [mug] + list(mug.children_recursive):
    if o.type in ("MESH", "CURVE"):
        key_vis(o, frames_of([26]), END)
# luz del sol sólo en la plaza
sun = bpy.data.objects["Sol"]
for k in sorted(FR):
    sun.data.energy = (3.3 if k not in INTERIOR else 0.0) if k in plaza_shots else 0.4
    sun.data.keyframe_insert("energy", frame=FR[k][0])

# --- cámaras ---
def cam_face(k, d0, d1, side=0.0, up=0.02, down=None, lens=50, fstop=4.0, shake=None, f_eval=None, frac=0.32, foco=None):
    """Cámara que sigue la cara: ojos en el tercio superior (frac desde arriba) pase lo que pase con la animación."""
    f0, f1 = FR[k]
    H0, H1 = d0 * 24.0 / lens, d1 * 24.0 / lens
    fo = foco or focus
    aim = P.empty(f"Mira{k:02d}")
    c = aim.constraints.new("COPY_LOCATION")
    c.target, c.use_offset = fo, True
    for f, H in ((f0, H0), (f1 - 1, H1)):
        aim.location = (0, 0, -(0.5 - frac) * H)
        aim.keyframe_insert("location", frame=f)
    cd = bpy.data.cameras.new(f"Cam{k:02d}")
    cd.lens, cd.sensor_fit, cd.sensor_height = lens, "VERTICAL", 24.0
    cd.dof.use_dof, cd.dof.aperture_fstop, cd.dof.focus_object = True, fstop, fo
    cam = bpy.data.objects.new(f"Cam{k:02d}", cd)
    P.link(cam)
    cl = cam.constraints.new("COPY_LOCATION")
    cl.target, cl.use_offset = fo, True
    tr = cam.constraints.new("DAMPED_TRACK")
    tr.target, tr.track_axis = aim, "TRACK_NEGATIVE_Z"
    for f, d, sd in ((f0, d0, side), (f1 - 1, d1, side * 0.8)):
        cam.location = (sd, -d, up)
        cam.keyframe_insert("location", frame=f)
    cam.rotation_euler = (math.pi / 2, 0, 0)
    if shake:
        for fc in anim._fcurves(aim.animation_data.action):
            mod = fc.modifiers.new("NOISE")
            mod.scale, mod.strength = shake[2], shake[3] * d0 * 2
            mod.use_restricted_range = True
            mod.frame_start, mod.frame_end = shake[0], shake[1]
            mod.blend_in, mod.blend_out = 1, 6
    m = sc.timeline_markers.new(f"Cam{k:02d}", frame=f0)
    m.camera = cam
    cams.append(cam)
    return cam


cam_face(1, 0.66, 0.54, side=-0.30, up=0.04)
cam_face(2, 0.42, 0.38, side=-0.16, up=0.03, shake=(FR[2][0], FR[2][0] + 18, 2.0, 0.035))
cam_face(3, 1.45, 1.30, side=-0.35, up=0.05, lens=45, frac=0.42)
cam_face(5, 1.5, 1.3, side=0.25, up=0.05, down=0.32, lens=45)
cam_face(6, 1.5, 1.4, side=0.0, up=0.05, down=0.3, lens=45)
# 7: plano general de la plaza, grúa
f0, f1 = FR[7]
camera("Cam07", f0, f1, [(f0, (-2.3, -5.2, 2.8), (0.3, 0.7, 1.0)), (f1 - 1, (-1.9, -4.6, 1.7), (0.3, 0.7, 1.1))], lens=32, fstop=5.6)
f0, f1 = FR[8]
camera("Cam08", f0, f1, [(f0, (0.4, -2.6, 1.55), (-0.45, 0.5, 1.2)), (f1 - 1, (0.25, -2.1, 1.5), (-0.4, 0.4, 1.25))], lens=40)
cam_face(9, 0.75, 0.62, side=0.15, up=0.0, down=0.12, shake=(FR[9][0], FR[9][1], 6.0, 0.012))
ICAM = {  # plano: (cámara inicio, objetivo inicio, cámara fin, objetivo fin) relativos a los ojos (E), lente
    4: ((-0.06, -0.48, 0.14), (0, 0.02, 0.06), (-0.04, -0.36, 0.12), (0, 0.04, 0.06), 50),
    10: ((0.30, -0.24, -0.02), (0, 0.025, -0.05), (0.26, -0.20, -0.03), (0, 0.025, -0.05), 50),
    31: ((0.16, -0.10, -0.035), (0, 0.03, -0.052), (0.13, -0.08, -0.04), (0, 0.03, -0.052), 50),
    32: ((0.30, -0.30, 0.20), (0, 0.08, 0.08), (0.26, -0.26, 0.24), (0, 0.08, 0.09), 50),
    13: ((0.22, -0.26, 0.0), (0.0, 0.03, -0.03), (0.34, -0.40, 0.04), (0.0, 0.03, -0.02), 50),
    15: ((0.30, -0.34, 0.10), (0, 0.03, 0.03), (0.26, -0.34, 0.20), (0, 0.04, 0.05), 50),
    21: ((0.34, -0.30, 0.16), (0, 0.09, 0.04), (0.40, -0.12, 0.20), (0, 0.09, 0.04), 50),
    22: ((-0.38, -0.20, 0.12), (0, 0.08, 0.02), (-0.32, -0.30, 0.16), (0, 0.08, 0.03), 50),
    25: ((0.28, -0.22, -0.03), (0, 0.025, -0.055), (0.22, -0.18, -0.04), (0, 0.025, -0.055), 50),
}
for k, (c0, t0, c1, t1, lens) in ICAM.items():
    f0, f1 = FR[k]
    h0, h1 = head_world(f0), head_world(f1 - 1)
    ef = P.empty(f"FocoInt{k}", loc=h0 + Vector(t0))
    camera(f"Cam{k:02d}", f0, f1, [(f0, h0 + Vector(c0), h0 + Vector(t0)), (f1 - 1, h1 + Vector(c1), h1 + Vector(t1))], lens=lens, fstop=5.6, focus_obj=ef)
cam_face(14, 0.55, 0.50, side=0.30, up=0.02, fstop=8.0, frac=0.42)
cam_face(16, 1.1, 0.95, side=-0.2, up=0.03, lens=45, frac=0.45)
f0, f1 = FR[17]
camera("Cam17", f0, f1, [(f0, LAB_O + Vector((-2.5, -4.2, 1.8)), LAB_O + Vector((-0.8, 0.4, 1.3))), (f1 - 1, LAB_O + Vector((1.2, -4.0, 1.7)), LAB_O + Vector((0.6, 0.4, 1.3)))], lens=35, fstop=5.6, focus_obj=bpy.data.objects["RigVol6"])
f0, f1 = FR[18]
camera("Cam18", f0, f1, [(f0, LAB_O + Vector((-0.6, -1.3, 1.62)), LAB_O + Vector((0.2, 0.4, 1.45))), (f1 - 1, LAB_O + Vector((-0.2, -1.05, 1.6)), LAB_O + Vector((0.3, 0.4, 1.45)))], lens=45, fstop=2.8, focus_obj=bpy.data.objects["RigVol6"])
for k, (a, b) in {19: ((ART_O + Vector((-0.6, -3.8, 0.3)), ART_O), (ART_O + Vector((-0.2, -3.0, 0.2)), ART_O)), 20: ((ART_O + Vector((0.3, -3.0, 0.1)), ART_O), (ART_O + Vector((0.6, -3.8, 0.2)), ART_O))}.items():
    f0, f1 = FR[k]
    e_ = P.empty(f"FocoArteria{k}", loc=ART_O)
    camera(f"Cam{k:02d}", f0, f1, [(f0, *a), (f1 - 1, *b)], lens=40, fstop=4.0, focus_obj=e_)
for k, (a, b) in {11: (((0.9, -1.4, 0.15), (0, 0.2, 1.55)), ((0.6, -1.1, 0.25), (0, 0.2, 1.55))), 12: (((-0.5, -1.2, 0.3), (0.1, 0.3, 1.55)), ((-0.8, -1.5, 0.2), (0.1, 0.3, 1.55)))}.items():
    f0, f1 = FR[k]
    ef = P.empty(f"FocoPal{k}", loc=PAL_O + Vector((0, 0.2, 1.55)))
    camera(f"Cam{k:02d}", f0, f1, [(f0, PAL_O + Vector(a[0]), PAL_O + Vector(a[1])), (f1 - 1, PAL_O + Vector(b[0]), PAL_O + Vector(b[1]))], lens=28, fstop=4.0, focus_obj=ef,
           shake=(f0 + 40, f1, 4.0, 0.004) if k == 12 else None)
f0, f1 = FR[23]
et = P.empty("FocoTexto", loc=TXT_O + Vector((0, 0, 1.5)))
camera("Cam23", f0, f1, [(f0, TXT_O + Vector((0, -5.4, 1.55)), TXT_O + Vector((0, 0, 1.52))), (f1 - 1, TXT_O + Vector((0, -4.9, 1.55)), TXT_O + Vector((0, 0, 1.52)))], lens=30, fstop=8, focus_obj=et,
       shake=(f0, f1, 3.0, 0.008))
cam_face(24, 0.62, 0.58, side=0.0, up=0.0, down=0.10)
cam_face(26, 0.9, 0.78, side=-0.25, up=0.02, down=0.15)
cam_face(27, 1.55, 1.35, side=0.35, up=0.05, down=0.32, lens=45)
f0, f1 = FR[28]
camera("Cam28", f0, f1, [(f0, (-0.9, -1.9, 1.62), (0.2, 0.4, 1.35)), (f1 - 1, (-0.75, -1.6, 1.6), (0.2, 0.4, 1.38))], lens=40)
cam_face(29, 1.1, 0.9, side=0.2, up=0.03, down=0.25, lens=45)
cam_face(30, 0.66, 0.66, side=-0.30, up=0.04, f_eval=FR[1][0])  # mismo encuadre que el plano 1 -> loop
foco6 = P.empty("FocoVoluntario", loc=bpy.data.objects["RigVol6"].matrix_world @ (E + Vector((0, -0.02, 0))))
parent_bone(foco6, bpy.data.objects["RigVol6"], B + "Head")
cam_face(33, 0.85, 0.70, side=-0.2, up=0.03, lens=50, frac=0.40, foco=foco6)
cam_face(34, 0.60, 0.52, side=0.18, up=0.02)
cam_face(35, 0.70, 0.62, side=-0.22, up=0.02)
sc.camera = cams[0]

meta = {"FR": FR, "T": T, "END": END, "interior": INTERIOR}
json.dump(meta, open(os.path.join(OUT, "ep01_planos.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "ep01.blend"))
print("ok ep01", END, "cuadros")
