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


def _ss(e0, e1, v):
    t = np.clip((v - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def derm_mask(p):
    """R = zona del nervio oftálmico (V1: frente y dorso de la nariz), G = maxilar (V2: mejilla y labio de arriba), B = mandibular (V3: mentón y mandíbula)."""
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    front = 1 - _ss(E.y + 0.02, E.y + 0.05, y)
    nose = (1 - _ss(0.010, 0.018, np.abs(x))) * _ss(E.z - 0.035, E.z - 0.025, z) * (1 - _ss(E.z + 0.004, E.z + 0.016, z)) * (1 - _ss(E.y - 0.03, E.y - 0.01, y))
    v1 = np.maximum(_ss(E.z + 0.004, E.z + 0.016, z) * (1 - _ss(E.z + 0.11, E.z + 0.13, z)) * front, nose)
    v2 = _ss(E.z - 0.066, E.z - 0.054, z) * (1 - _ss(E.z + 0.004, E.z + 0.016, z)) * front * (1 - nose)
    v3 = _ss(E.z - 0.125, E.z - 0.110, z) * (1 - _ss(E.z - 0.066, E.z - 0.054, z)) * front * (1 - _ss(E.y - 0.005, E.y + 0.015, y))
    cerca = _ss(-0.004, 0.006, x)  # sólo el lado que mira a la cámara de perfil (+x): si no, las dos mejillas se suman
    yield np.c_[v1 * cerca, v2 * cerca, v3 * cerca], np.ones(len(p))


dimg = ub.rasterize(Pm[sel], Um[sel], 1024, derm_mask, np.zeros((1024, 1024, 3)))
Image.fromarray((np.flipud(np.clip(dimg, 0, 1)) * 255).astype(np.uint8)).save(os.path.join(OUT, "tex", "Dermatomas.png"))
derm_img = bpy.data.images.load(os.path.join(OUT, "tex", "Dermatomas.png"))
derm_img.colorspace_settings.name = "Non-Color"

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
shirt_cols = [(0.95, 0.95, 0.92), (0.05, 0.45, 0.85), (0.95, 0.75, 0.05), (0.2, 0.7, 0.3), (0.6, 0.2, 0.8), (0.95, 0.4, 0.6), (0.1, 0.6, 0.6)]
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
tbg = P.prim("cube", "TextoFondo", C_TXT, m=P.mat("TextoFondoMat", (0.003, 0.07, 0.11), rough=0.8))
tbg.location, tbg.scale = TXT_O + Vector((0, 3, 1)), (20, 0.1, 14)
tfl = P.prim("cube", "TextoPiso", C_TXT, m=P.mat("TextoPisoMat", (0.003, 0.05, 0.08), rough=0.8))
tfl.location, tfl.scale = TXT_O + Vector((0, 0, -0.05)), (20, 8, 0.1)
tlight = bpy.data.lights.new("TextoLuz", "AREA")
tlight.energy, tlight.size = 700, 4
tl = bpy.data.objects.new("TextoLuz", tlight)
P.link(tl, C_TXT)
tl.location = TXT_O + Vector((-2, -5, 5))
tl.rotation_euler = (math.radians(45), 0, math.radians(-20))
letters = []
ymat = P.mat("LetraAmarilla", (1.0, 0.66, 0.02), rough=0.3, coat=0.6, emit=0.2)
wmat = P.mat("LetraBlancaG", (1.0, 1.0, 1.0), rough=0.3, coat=0.6, emit=0.25)
LINES = (("GANGLIO", 2.45, ymat, 0), ("NEURALGIA", 1.85, ymat, 0), ("ESFENO", 1.12, wmat, 1), ("PALATINA", 0.52, wmat, 1))
SIZE, MAXW = 0.50, 2.30          # letras grandes; la línea más larga cabe en el cuadro
for li, (word, z, m, row) in enumerate(LINES):
    objs = []
    for k, ch in enumerate(word):
        t = P.text3d(f"Letra{li}_{k}", ch, size=SIZE, extrude=0.08, bevel_d=0.014, coll=C_TXT, m=m)
        t.rotation_euler = (math.pi / 2, 0, 0)
        objs.append(t)
    bpy.context.view_layer.update()
    wid = [max(o.dimensions.x, SIZE * 0.25) for o in objs]      # ancho real de cada letra (kerning proporcional)
    gapx = SIZE * 0.07
    total = sum(wid) + gapx * (len(wid) - 1)
    sc_ = min(1.0, MAXW / total)
    x = -total * sc_ / 2
    for k, (t, w_) in enumerate(zip(objs, wid)):
        t.scale = (sc_, sc_, sc_)
        # el origen de cada letra está en su centro
        t.location = TXT_O + Vector((x + w_ * sc_ / 2, 0, z))
        x += (w_ + gapx) * sc_
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
rmp.color_ramp.elements[0].color = (0.002, 0.006, 0.016, 1)   # azul noche: lo que brilla resalta
rmp.color_ramp.elements[1].color = (0.012, 0.045, 0.10, 1)
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
    # se ordenan y se juntan los intervalos pegados o repetidos: si no, el "ocultar" del final de un plano
    # puede pisar el "mostrar" del plano siguiente en el mismo cuadro (pasaba con el domo en el plano 15)
    merged = []
    for f0, f1 in sorted((int(a), int(b)) for a, b in intervals):
        if merged and f0 <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], f1)
        else:
            merged.append([f0, f1])
    for f0, f1 in merged:
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
    cd.dof.use_dof = fstop > 0          # fstop=0: todo nítido (interior: se tiene que entender)
    cd.dof.aperture_fstop = max(fstop, 0.1)
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
    22: (49.32, 52.85), 23: (52.85, 55.74), 24: (55.74, 56.84), 34: (56.84, 58.54), 25: (58.54, 60.55), 26: (60.55, 62.50),
    27: (62.50, 64.55), 35: (64.55, 66.10), 28: (66.10, 68.42), 29: (68.42, 70.90), 30: (70.90, 72.10),
}
FR = {k: (F(a), F(b)) for k, (a, b) in T.items()}
END = FR[30][1]
sc.frame_start, sc.frame_end = 1, END - 1
INTERIOR = [4, 10, 31, 13, 14, 15, 32, 21, 22, 25]
BITE = [1, 2, 9, 30]

# --- actuación por plano (pistas NLA) ---
plan = {
    1: ("Drinking", 95), 2: ("Drinking", 120), 3: ("Focus", 6), 4: ("Happy_Idle", 1), 5: ("Shrugging", 4),
    6: ("Happy_Idle", 1), 7: ("Happy_Idle", 1), 8: ("Arm_Gesture", 6), 9: ("Drinking", 70), 10: ("Happy_Idle", 1),
    11: ("Happy_Idle", 10), 12: ("Happy_Idle", 20), 13: ("Happy_Idle", 1), 14: ("Happy_Idle", 15), 15: ("Happy_Idle", 30),
    16: ("Focus", 12), 17: ("Happy_Idle", 1), 18: ("Happy_Idle", 1), 19: ("Happy_Idle", 1), 20: ("Happy_Idle", 1),
    21: ("Happy_Idle", 1), 22: ("Happy_Idle", 10), 23: ("Happy_Idle", 1), 24: ("Head_Nod_Yes", 10), 25: ("Happy_Idle", 5),
    26: ("Drinking", 112), 27: ("Relieved_Sigh", 1), 28: ("Thinking", 18), 29: ("Shaking_Head_No", 1), 30: ("Drinking", 92),
    31: ("Happy_Idle", 30), 32: ("Happy_Idle", 40), 33: ("Happy_Idle", 1), 34: ("Happy_Idle", 10), 35: ("Happy_Idle", 20),
}
speeds = {26: 0.6, 31: 0.5, 32: 0.5, 33: 0.5, 34: 0.6, 35: 0.6, 9: 1.9, 4: 0.5, 10: 0.5, 11: 0.5, 12: 0.5, 13: 0.5, 15: 0.5, 21: 0.5, 22: 0.5, 25: 0.5, 2: 0.5, 16: 0.25, 7: 0.8, 19: 0.5, 20: 0.5, 17: 0.5, 18: 0.5, 23: 0.5, 14: 0.5}
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
ik2.influence = 0.0   # la taza va en la mano (ver "objetos en la mano")
for c in (ik, ik2):
    pass
for fc in anim._fcurves(rig.animation_data.action) if rig.animation_data.action else []:
    for kp in fc.keyframe_points:
        kp.interpolation = "CONSTANT"

# --- objetos en la mano: vasos de los voluntarios y la taza quedan dentro del puño (entre el pulgar y los dedos) ---
def cup_matrix(rg, side="Left", inset=0.0):
    pb, M = rg.pose.bones, rg.matrix_world
    P_ = lambda n: M @ pb[B + side + "Hand" + n].head
    tips = [P_("Thumb2"), P_("Index2"), P_("Middle2"), P_("Ring2"), P_("Pinky2")]
    C = sum(tips, Vector()) / len(tips)
    A = (P_("Index1") - P_("Pinky1")).normalized()
    if A.z < 0:
        A = -A
    palm = (M @ pb[B + side + "Hand"].head)
    toward_palm = (palm - C)
    toward_palm -= A * toward_palm.dot(A)
    C = C + toward_palm.normalized() * inset if toward_palm.length > 1e-6 else C
    R = A.to_track_quat("Z", "Y").to_matrix().to_4x4()
    return Matrix.Translation(C) @ R, A


def reparent_to_hand(ob, rg, f, side="Left", z_off=0.0, inset=0.0, extra=Matrix(), upright=False):
    sc.frame_set(f)
    bpy.context.view_layer.update()
    Mw, A = cup_matrix(rg, side, inset)
    if upright:
        Mw = Matrix.Translation(Mw.translation)
    ob.parent = None
    ob.matrix_world = Mw @ Matrix.Translation((0, 0, z_off)) @ extra
    parent_bone(ob, rg, B + side + "Hand")


for i, r2 in enumerate(clones):
    a0_ = 40 + (i * 7) % 30
    f_hold = FR[17][0] + max(0, 50 - a0_) + 2
    gl = bpy.data.objects[f"Vaso{i}"]
    reparent_to_hand(gl, r2, f_hold, z_off=-0.01, inset=0.006)
    # meta en la boca del voluntario
    tgt = P.empty(f"BocaVol{i}", loc=r2.matrix_world @ (MOUTH + Vector((0.0, -0.035, -0.135))))
    parent_bone(tgt, r2, B + "Head")
    ikv = r2.pose.bones[B + "LeftHand"].constraints.new("IK")
    ikv.target, ikv.chain_count, ikv.use_tail = tgt, 3, False
    s0 = FR[17][0] + (112 - a0_)          # el sorbo en la animación "Drinking" (cuadros ~112-150)
    for f, v in ((1, 0.0), (s0 - 10, 0.0), (s0, 1.0), (s0 + 30, 1.0), (s0 + 42, 0.0)):
        ikv.influence = v
        ikv.keyframe_insert("influence", frame=f)
# taza: sube a los labios inclinada hacia la cara, sorbo, y baja; la mano la toma del asa (IK)
f26a, f26b = FR[26]
for f, loc, rx in ((f26a, (0, -0.06, -0.075), -8), (f26a + 14, (0, -0.028, -0.028), -35), (f26b - 14, (0, -0.028, -0.028), -38), (f26b - 1, (0, -0.06, -0.075), -8)):
    mug.location = loc
    mug.rotation_euler = (math.radians(rx), 0, 0)
    mug.keyframe_insert("location", frame=f)
    mug.keyframe_insert("rotation_euler", frame=f)
for k in sorted(FR):
    ik2.influence = 1.0 if k == 26 else 0.0
    ik2.keyframe_insert("influence", frame=FR[k][0])
for fc in anim._fcurves(rig.animation_data.action):
    for kp in fc.keyframe_points:
        kp.interpolation = "CONSTANT"
# cono en la mano (planos 8 y 29): derecho, con el barquillo dentro del puño
cone_h.parent = None
reparent_to_hand(cone_h, rig, FR[8][1] - 6, z_off=-0.075, upright=True)
# vapor: no se muestra (se veía como una línea recta cruzando la cara)
for st in steam:
    st.hide_render = True
for k_, st in enumerate([]):
    st.rotation_euler = (0, 0, 0)
    for f, rz in ((FR[26][0], 0.0), (FR[26][1], 2.5 + k_)):
        st.delta_rotation_euler = (0, 0, rz)
        st.keyframe_insert("delta_rotation_euler", frame=f)

# voluntarios distintos entre sí: color de pelo variado
hair_mat = hair.data.materials[0] if hair.data.materials else None
HAIR_VAR = [(0.35, 0.3), (0.55, 0.35), (0.97, 0.3), (0.5, 0.75), (0.2, 0.5)]
for i, r2 in enumerate(clones):
    hc_ = next((o for o in bpy.data.objects if o.type == "CURVES" and o.parent == r2), None)
    if hc_ is None or hair_mat is None:
        continue
    mel, red = HAIR_VAR[i % len(HAIR_VAR)]
    hm = bpy.data.materials.get(f"PeloVol{i % len(HAIR_VAR)}")
    if hm is None:
        hm = hair_mat.copy()
        hm.name = f"PeloVol{i % len(HAIR_VAR)}"
        for n_ in hm.node_tree.nodes:
            if "Melanin" in n_.inputs:
                n_.inputs["Melanin"].default_value = mel
            if "Melanin Redness" in n_.inputs:
                n_.inputs["Melanin Redness"].default_value = red
    hc_.material_slots[0].link = "OBJECT"
    hc_.material_slots[0].material = hm
# monitor del laboratorio: "lo midieron" (línea de pulso)
mon = P.prim("cube", "Monitor", C_LAB, m=P.mat("MonitorCaja", (0.05, 0.06, 0.08), rough=0.4))
mon.location, mon.scale = LAB_O + Vector((2.6, -0.2, 1.45)), (0.42, 0.04, 0.28)
mon.rotation_euler.z = math.radians(-20)
pie = P.prim("cyl", "MonitorPie", C_LAB, m=bpy.data.materials["MonitorCaja"], r=0.03, r2=0.03, h=1.3)
pie.location = LAB_O + Vector((2.6, -0.2, 0.6))
pts = []
for i in range(41):
    x = -0.36 + 0.72 * i / 40
    y = 0.0
    z = 0.06 * math.exp(-((i % 13) - 6) ** 2 / 1.5) * (1 if (i // 13) % 2 == 0 else -0.6)
    pts.append((x, -0.045, z))
pulse = P.tube("MonitorPulso", pts, 0.006, C_LAB, m=P.mat("PulsoVerde", (0.2, 1.0, 0.4), emit=4.0))
pulse.parent = mon
pulse.scale = (1 / 0.42, 1 / 0.04, 1 / 0.28)

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
    for df, sv in ((-1, 1.0), (1, 0.62), (8, 0.62), (10, 0.30), (17, 0.30), (19, 0.001)):   # tres mordiscos
        s_.scale = (sv, sv, sv * (0.85 if sv < 1 else 1))
        s_.keyframe_insert("scale", frame=fb + df)
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

# --- expresiones (grandes, sostenidas dentro del plano; claves por plano y desfase en cuadros) ---
OPEN = dict(eye_left_opened_up=0.18, eye_right_opened_up=0.18)          # ojos bien abiertos (no "a media asta")
EXPR = {
    1: [(0, dict(OPEN, eyebrows_left_up=0.6, eyebrows_right_up=0.6, mouth_open=0.6, eye_left_opened_up=0.4, eye_right_opened_up=0.4)),
        (24, dict(eyebrows_left_up=0.5, eyebrows_right_up=0.5, mouth_open=0.15, mouth_compression=0.4, eye_left_closure=0.25, eye_right_closure=0.25)),
        (44, dict(eyebrows_left_inner_up=0.6, eyebrows_right_inner_up=0.6, mouth_open=0.2, eye_left_slit=0.4, eye_right_slit=0.4))],
    2: [(0, dict(eye_left_closure=1.0, eye_right_closure=1.0, eyebrows_left_down=1.0, eyebrows_right_down=1.0, eyebrows_left_inner_up=0.5,
                 eyebrows_right_inner_up=0.5, mouth_retraction=0.9, mouth_upward_retraction=0.6, nose_compression=0.7, nose_left_elevation=0.6, nose_right_elevation=0.6))],
    3: [(0, dict(eye_left_closure=0.95, eye_right_closure=0.95, eyebrows_left_down=0.8, eyebrows_right_down=0.8, eyebrows_left_inner_up=0.6,
                 eyebrows_right_inner_up=0.6, mouth_retraction=0.7, nose_compression=0.5))],
    5: [(0, dict(OPEN, eyebrows_left_up=1.0, eyebrows_right_up=1.0, mouth_depression=0.5, eye_left_opened_up=0.35, eye_right_opened_up=0.35))],
    7: [(0, dict(OPEN, mouth_corner_puller=0.55))],
    8: [(0, dict(OPEN, mouth_corner_puller=0.8, eyebrows_left_up=0.6, eyebrows_right_up=0.6, eye_left_opened_up=0.4, eye_right_opened_up=0.4))],
    9: [(0, dict(eyebrows_left_down=0.8, eyebrows_right_down=0.8, eye_left_slit=0.6, eye_right_slit=0.6, mouth_open=0.4))],
    16: [(0, dict(eye_left_closure=0.85, eye_right_closure=0.85, eyebrows_left_inner_up=0.8, eyebrows_right_inner_up=0.8, mouth_depression_retraction=0.6, mouth_retraction=0.4))],
    17: [(0, dict(OPEN, mouth_pursing=0.5))],
    33: [(0, dict(eye_left_closure=0.95, eye_right_closure=0.95, eyebrows_left_down=0.8, eyebrows_right_down=0.8, eyebrows_left_inner_up=0.6,
                  eyebrows_right_inner_up=0.6, mouth_retraction=0.7, nose_compression=0.5))],
    24: [(0, dict(OPEN, mouth_compression=0.7, eyebrows_left_down=0.25, eyebrows_right_down=0.25)), (14, dict(OPEN, mouth_compression=0.7, eyebrows_left_up=0.5, eyebrows_right_up=0.5))],
    34: [(0, dict(OPEN, mouth_corner_puller=0.6, eyebrows_left_up=0.7, eyebrows_right_up=0.2))],
    26: [(0, dict(OPEN, mouth_pursing=0.5)), (30, dict(eye_left_closure=0.8, eye_right_closure=0.8, mouth_pursing=0.6))],
    27: [(0, dict(eye_left_closure=0.6, eye_right_closure=0.6, mouth_corner_puller=0.6, eyebrows_left_up=0.3, eyebrows_right_up=0.3)),
         (35, dict(OPEN, mouth_corner_puller=0.85, eyebrows_left_up=0.4, eyebrows_right_up=0.4))],
    35: [(0, dict(OPEN, mouth_corner_puller=0.9, eyebrows_left_up=0.4, eyebrows_right_up=0.4))],
    28: [(0, dict(OPEN, eyebrows_left_up=0.8, eyebrows_right_down=0.5, mouth_corner_puller=0.35, eye_right_slit=0.3))],
    29: [(0, dict(OPEN, eye_left_slit=0.45, eye_right_slit=0.45, mouth_corner_puller=0.9, eyebrows_left_up=0.5, eyebrows_right_up=0.2))],
    30: [(0, dict(OPEN, eyebrows_left_up=0.6, eyebrows_right_up=0.6, mouth_open=0.6, eye_left_opened_up=0.4, eye_right_opened_up=0.4))],
}
for k in sorted(FR):
    f0, f1 = FR[k]
    keys_ = EXPR.get(k, [(0, dict(OPEN))])
    for i_, (off, vals) in enumerate(keys_):
        expr(f0 + off, **vals)
        nxt = keys_[i_ + 1][0] if i_ + 1 < len(keys_) else f1 - f0 - 2
        expr(f0 + max(off + 2, nxt - 4), **vals)      # se sostiene hasta poco antes del cambio
# masticar en el plano 9 (boca que abre y cierra)
f = FR[9][0] + 4
while f + 6 < FR[9][1]:
    for df, mo in ((0, 0.55), (3, 0.08)):
        expr(f + df, eyebrows_left_down=0.8, eyebrows_right_down=0.8, eye_left_slit=0.6, eye_right_slit=0.6, mouth_open=mo, mouth_compression=0.5 if mo < 0.1 else 0.0)
    f += 7
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
# 0 entre el plano 3 y el 30 (antes subía sola durante todo el video y dejaba un punto azul en la frente).
# El plano 30 termina en 0,25 = valor del cuadro 1, para que el loop empalme.
for f, v in ((1, 0.25), (FR[1][1] - 2, 0.50), (FR[2][0] + 3, 0.78), (FR[3][0] - 1, 0.78), (FR[3][0], 0.0), (FR[30][0] - 1, 0.0), (FR[30][0], 0.06), (END, 0.25)):
    set_val(fs, f, v)
for fc in anim._fcurves(skin.node_tree.animation_data.action):
    if fc.data_path.endswith('nodes["Escarcha"].outputs[0].default_value'):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
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
    v = 1.0 if k in INTERIOR else 0.0
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
    qob.rotation_euler = (math.pi / 2, 0, math.pi / 2)  # de frente a la cámara de perfil (+x)
    for f, rz in ((FR[32][0], -0.3), (FR[32][1], 0.3)):  # vaivén
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
    flake.rotation_euler = (0.25 + r * 0.05, 1.35, r)   # de cara a la cámara de perfil (+x), girando
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
    tstart = F(t_g if row == 0 else t_e) - 6 + k * 1.2  # cae 8 cuadros y aterriza justo al empezar la palabra
    dz0 = 5.0 - (t.location.z - TXT_O.z)  # todas parten justo sobre el borde superior del cuadro
    for f, dz, s_ in ((1, dz0, 1.0), (int(tstart), dz0, 1.0), (int(tstart) + 8, 0.0, 1.0), (int(tstart) + 10, 0.06, 1.0), (int(tstart) + 13, 0.0, 1.0)):
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
        # dentro de la cabeza sólo queda la piel de vidrio: sin ropa
        key_vis(bpy.data.objects[n], frames_of(plaza_shots if n == "Cuerpo" else [k for k in plaza_shots if k not in INTERIOR]), END)
for n in ("Dientes", "Lengua"):
    key_vis(bpy.data.objects[n], frames_of([k for k in plaza_shots if k not in INTERIOR and k != 14]), END)
key_vis(hair, frames_of([k for k in plaza_shots if k not in INTERIOR]), END)
SHOW = {"cerebro": [], "paladar": [], "lengua": [], "vasos": [], "nervios": [], "arteria": []}  # reemplazados por la anatomía real
for key, ks in SHOW.items():
    grp = org[key] if isinstance(org[key], list) else [org[key]]
    for ob in grp:
        key_vis(ob, frames_of(ks), END)
key_vis(org["bocado"], frames_of([10, 31]), END)
for qob in org["preguntas"]:
    key_vis(qob, [], END)  # el "?" lo dibuja el post junto a la corteza (en 3D quedaba cortado arriba)
key_vis(flake, frames_of([4]), END)
key_vis(dome, frames_of(INTERIOR + [14]), END)
for L_ in (ikl, ikl2):
    for k in sorted(FR):
        L_.energy = (60 if L_ is ikl else 40) if k in INTERIOR + [14] else 0.0
        L_.keyframe_insert("energy", frame=FR[k][0])
SAG = []                    # sin cortes: cabeza de vidrio de perfil, se ve sólo lo que nombra la voz
FULL = list(INTERIOR)
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
        key_vis(o, frames_of([26]) if o not in steam else [], END)
# ================= anatomía real (Z-Anatomy) con animaciones de activación =================
import anatomia_real as AR
C_ANAT = P.collection("AnatomiaReal")
KIT = os.environ.get("ANAT_KIT", os.path.join(OUT, "anatomia_cabeza.blend"))
if not os.path.exists(KIT):
    KIT = os.path.join(STUDIO, "plantilla", "out", "anatomia_cabeza.blend")
kit, kinfo = AR.load(KIT, rig, B + "Head", C_ANAT)
TK = kinfo["T"]
# ganglio del trigémino (atlas): el extremo de atrás del nervio oftálmico
_v1 = [v.co.copy() for v in kit["TrigeminoV1"].data.vertices if v.co.x > 0]
G_ATLAS = max(_v1, key=lambda c: c.y)
mat = {
    "Cerebro": AR.mat_cerebro("CerebroReal", (0.93, 0.66, 0.64), (0.74, 0.44, 0.46)),   # porcelana rosada: surcos suaves
    "CortezaSensitiva": AR.mat_cerebro("CortezaSensitivaMat", (0.93, 0.66, 0.64), (0.74, 0.44, 0.46)),
    "Cerebelo": AR.mat_cerebro("CerebeloReal", (0.88, 0.58, 0.58), (0.70, 0.40, 0.42)),
    "TroncoEncefalico": AR.mat_simple("TroncoReal", (0.92, 0.75, 0.68), rough=0.4, sss=0.2, cut=(0.85, 0.70, 0.62)),
    "CraneoBase": AR.mat_simple("Hueso", (0.86, 0.80, 0.68), rough=0.55, sss=0.1, cut=(0.93, 0.86, 0.72)),
    "Boveda": AR.mat_simple("HuesoBoveda", (0.86, 0.80, 0.68), rough=0.55),
    "Dientes": AR.mat_simple("Esmalte", (0.95, 0.94, 0.88), rough=0.2, coat=0.6, cut=(0.92, 0.88, 0.78)),
    "Lengua": AR.mat_simple("LenguaReal", (0.80, 0.30, 0.33), rough=0.3, sss=0.3, coat=0.5, cut=(0.72, 0.24, 0.27)),
    "PaladarBlando": AR.mat_simple("PaladarBlandoReal", (0.85, 0.36, 0.40), rough=0.3, sss=0.3, coat=0.5, cut=(0.75, 0.28, 0.32)),
    "PaladarMucosa": AR.mat_mucosa("PaladarMucosaMat"),
    "Ojos": AR.mat_simple("OjoAtlas", (0.70, 0.74, 0.80), rough=0.3),  # ojo tenue: orienta, no se roba la mirada
    "TrigeminoV1": AR.mat_nervio("NervioV1", G_ATLAS),
    "TrigeminoV2": AR.mat_nervio("NervioV2", G_ATLAS),
    "TrigeminoV3": AR.mat_nervio("NervioV3", G_ATLAS),
    "TrigeminoRaiz": AR.mat_nervio("NervioRaiz", G_ATLAS),
    "Arterias": AR.mat_arteria("ArteriaReal"),
    "ArteriaCerebralAnterior": AR.mat_arteria("ArteriaACA", (0.85, 0.05, 0.05)),
}
mat["Mandibula"] = mat["CraneoBase"]
for k_, o_ in kit.items():
    o_.data.materials.clear()
    o_.data.materials.append(mat[k_])
    if k_ in ("Lengua", "PaladarBlando"):
        o_.modifiers.new("Sub", "SUBSURF").render_levels = 2
    if k_ == "PaladarMucosa":
        # sólo el techo de la boca: se botan los pedacitos sueltos (piso de la nariz, senos) que salían flotando
        import bmesh as _bm
        bmm_ = _bm.new()
        bmm_.from_mesh(o_.data)
        bmm_.faces.ensure_lookup_table()
        seen_, comps_ = set(), []
        for f0_ in bmm_.faces:
            if f0_.index in seen_:
                continue
            st_, comp_ = [f0_], []
            seen_.add(f0_.index)
            while st_:
                fa_ = st_.pop()
                comp_.append(fa_)
                for e_ in fa_.edges:
                    for fb_ in e_.link_faces:
                        if fb_.index not in seen_:
                            seen_.add(fb_.index)
                            st_.append(fb_)
            comps_.append(comp_)
        area_ = [sum(f_.calc_area() for f_ in c_) for c_ in comps_]
        amax_ = max(area_)
        kill_ = [f_ for c_, a_ in zip(comps_, area_) if a_ < 0.12 * amax_ for f_ in c_]
        _bm.ops.delete(bmm_, geom=kill_, context="FACES")
        bmm_.to_mesh(o_.data)
        bmm_.free()
        print("mucosa: componentes", len(comps_), "se quedan", sum(1 for a_ in area_ if a_ >= 0.12 * amax_))
        so_ = o_.modifiers.new("Grosor", "SOLIDIFY")
        so_.thickness, so_.offset = 0.0025 / kinfo["s"], -1
        o_.modifiers.new("Sub", "SUBSURF").render_levels = 1
# rama supraorbitaria (V1) desde la órbita hasta la frente, bajo la piel
E0 = kinfo["E"]
mat_supra = AR.mat_nervio("NervioSupra", TK @ G_ATLAS)
supra = []
for sx in (-1, 1):
    guide = [E0 + Vector((sx * x, y, z)) for (x, y, z) in ((0.025, 0.014, 0.010), (0.027, -0.006, 0.020), (0.027, -0.02, 0.034), (0.025, -0.02, 0.05), (0.022, -0.02, 0.066), (0.019, -0.02, 0.082))]
    supra.append(AR.nervio_superficial(f"Supraorbital{'LR'[sx > 0]}", rig, B + "Head", body, guide, mat_supra, 0.0013, C_ANAT))
# paladar duro sólido para el corte: de detrás de los incisivos hasta donde empieza el velo del paladar
inc = TK @ Vector(kinfo["meta"]["incisivos_sup"])
_vp = [TK @ v.co for v in kit["PaladarBlando"].data.vertices]
_front_soft = min(_vp, key=lambda c: c.y)
PAL_F = Vector((0, inc.y + 0.009, inc.z + 0.004))
PAL_S = Vector((0, _front_soft.y + 0.016, _front_soft.z + 0.002))  # se monta sobre el velo: techo continuo
cap_m = AR.mat_simple("PaladarCorte", (0.66, 0.20, 0.25), rough=0.5)
prev_ = rig.data.pose_position
rig.data.pose_position = "REST"
bpy.context.view_layer.update()
pal_solid = AR.paladar_medio("PaladarCorteSolido", PAL_F, PAL_S, C_ANAT, mat["PaladarMucosa"], cap_m, rig, B + "Head", vault=0.006)
# el helado queda bajo la bóveda, a un tercio del paladar
_t = 0.38
_pb = PAL_F.lerp(PAL_S, _t) + Vector((0, 0, 0.006 * 0.95 - 0.0045 - 0.0099 - 0.004))
bc_ = org["bocado"]
bc_.data.materials.clear()
bc_.data.materials.append(P.mat("BocadoVainilla", "vainilla", rough=0.35, coat=0.4, sss=0.2))  # la bola de arriba del cono; no se confunde con la lengua
bc_.parent = None
bc_.matrix_world = Matrix.Translation(_pb) @ Matrix.Diagonal((0.68, 0.68, 0.52, 1))
AR._parent_bone(bc_, rig, B + "Head")
rig.data.pose_position = prev_
bpy.context.view_layer.update()
# "arriba" del mundo expresado en el espacio del hueso de la cabeza (delta_location vive ahí, no en el mundo)
UPB = (rig.matrix_world.to_3x3() @ rig.data.bones[B + "Head"].matrix_local.to_3x3()).inverted() @ Vector((0, 0, 1))
if bc_.animation_data and bc_.animation_data.action:
    for fc in anim._fcurves(bc_.animation_data.action):
        if fc.data_path == "delta_location":
            fc.mute = True
bc_.delta_location = (0, 0, 0)
for f, dz in ((1, -0.010), (FR[10][0], -0.010), (FR[10][0] + 24, 0.0), (FR[31][1], 0.0)):
    bc_.delta_location = UPB * dz
    bc_.keyframe_insert("delta_location", frame=f)
# paladar duro limpio y completo (el sólido de media boca + espejo): la mucosa del atlas trae pedazos sueltos
pal_solid.data.materials[1] = mat["PaladarMucosa"]
mi_ = pal_solid.modifiers.new("Espejo", "MIRROR")
mi_.use_axis[0], mi_.use_mirror_merge, mi_.merge_threshold = True, True, 0.0004
pal_solid.modifiers.new("Sub", "SUBSURF").render_levels = 2
key_vis(pal_solid, frames_of(INTERIOR), END)
# Cabeza de vidrio de perfil (cámara a +x): sin cráneo, sin ojos, sin cortes. Siempre se ve el cerebro y la boca
# (lengua, paladar, dientes); nervios y arterias sólo cuando la voz los nombra, y sólo del lado que mira a la cámara.
NERV = ("TrigeminoV1", "TrigeminoV2", "TrigeminoV3", "TrigeminoRaiz")
LADO = NERV + ("Arterias", "ArteriaCerebralAnterior", "Ojos")
N_SHOTS = [13, 14, 15, 32, 22]
BOCA = [10, 31, 25]   # en los planos de la boca no se ve el cerebro: sólo boca, paladar, lengua y helado
SIN_BOCA = [k for k in INTERIOR if k not in BOCA]
VIS_INT = {"Cerebro": SIN_BOCA, "CortezaSensitiva": SIN_BOCA, "Cerebelo": SIN_BOCA, "TroncoEncefalico": SIN_BOCA,
           "Lengua": INTERIOR, "PaladarBlando": INTERIOR, "Ojos": INTERIOR,
           "Arterias": [22]}
for n_ in NERV:
    VIS_INT[n_] = N_SHOTS
halves = {}
for k_ in list(kit):
    ks_ = VIS_INT.get(k_, [])
    if k_ in LADO:
        halves[k_] = AR.split_half(kit[k_])
        key_vis(halves[k_][0], [], END)
        key_vis(halves[k_][1], frames_of(ks_), END)
    else:
        key_vis(kit[k_], frames_of(ks_), END)
key_vis(supra[0], [], END)
key_vis(supra[1], frames_of([13, 14, 15]), END)
# relleno plano del corte sólo en los planos de corte de la boca
for m_ in set(mat.values()) | {cap_m}:
    if m_.node_tree and "Corte" in m_.node_tree.nodes:
        sock = m_.node_tree.nodes["Corte"].outputs[0]
        for k in sorted(FR):
            sock.default_value = 1.0 if k in SAG else 0.0
            sock.keyframe_insert("default_value", frame=FR[k][0])
        for fc in anim._fcurves(m_.node_tree.animation_data.action):
            if 'nodes["Corte"]' in fc.data_path:
                for kp in fc.keyframe_points:
                    kp.interpolation = "CONSTANT"
# el helado y la lengua en el corte: la lengua real sube al paladar (25)
# la lengua baja mientras el helado toca el paladar (10, 31: así se ve el paladar) y sube a calentarlo (25)
o_ = kit["Lengua"]
for f, dz in ((1, -0.009), (FR[25][0], -0.009), (FR[25][0] + 25, 0.004), (FR[25][1], 0.004)):
    o_.delta_location = UPB * dz
    o_.keyframe_insert("delta_location", frame=f)


def keys(sock, pairs, interp="BEZIER"):
    for f, v in pairs:
        sock.default_value = v
        sock.keyframe_insert("default_value", frame=int(f))
    nt_ = sock.id_data
    if interp != "BEZIER" and nt_.animation_data and nt_.animation_data.action:
        nm = sock.node.name
        for fc in anim._fcurves(nt_.animation_data.action):
            if f'nodes["{nm}"]' in fc.data_path:
                for kp in fc.keyframe_points:
                    kp.interpolation = interp


def nv(m_, name):
    return m_.node_tree.nodes[name].outputs[0]


# cerebro tibio (4): el frío nunca lo tocó
keys(nv(mat["Cerebro"], "Tibio"), ((1, 0), (FR[4][0], 0.0), (FR[4][0] + 20, 0.45), (FR[4][1] - 1, 0.45), (FR[4][1], 0.0)))
# la corteza que siente la cara se enciende cuando el cerebro "se confunde" (32) y al sentir la frente (15)
cs_ = []
f = FR[32][0]
while f + 6 < FR[32][1]:
    cs_ += [(f, 0.6), (f + 4, 3.0)]
    f += 9
keys(nv(mat["CortezaSensitiva"], "Activo"), [(1, 0), (FR[15][0] + 40, 0.0), (FR[15][1] - 1, 1.5)] + cs_ + [(FR[32][1], 1.2), (FR[32][1] + 1, 0.0)])


def pulses(f0, f1, d0, d1, dur, gap=4):
    out, f = [(1, -1.0), (f0 - 1, -1.0)], f0
    while f + dur <= f1:
        out += [(f, d0), (f + dur, d1), (f + dur + 1, -1.0)]
        f += dur + gap
    return out + [(f1, -1.0)]


# nervios: el trigémino "detecta" (13: pulsos hacia el ganglio), siente toda la cara (14: pulsos hacia afuera),
# la rama V1 lleva la señal a la frente (15)
for nm_ in NERV:
    m_ = mat[nm_]
    br = [(1, 0.25), (FR[13][0], 0.25), (FR[13][0] + 15, 1.2), (FR[14][1], 1.2), (FR[15][0], 0.4 if nm_ != "TrigeminoV1" else 1.6),
          (FR[15][1], 0.4 if nm_ != "TrigeminoV1" else 1.6), (FR[32][0], 0.3), (FR[22][0], 0.6)]
    f = FR[22][0]
    while f + 10 < FR[22][1]:
        br += [(f + 5, 1.6), (f + 10, 0.6)]
        f += 10
    br += [(FR[22][1], 0.25)]
    keys(nv(m_, "Brillo"), br)
    pul = pulses(FR[13][0] + 8, FR[13][1], 0.11, 0.0, 22) + pulses(FR[14][0], FR[14][1], 0.0, 0.12, 24)[2:]
    if nm_ == "TrigeminoV1":
        pul += pulses(FR[15][0], FR[15][1], 0.0, 0.07, 22)[2:]
    keys(nv(m_, "Pulso"), sorted(pul), interp="LINEAR")
keys(nv(mat_supra, "Brillo"), ((1, 0.25), (FR[15][0], 1.6), (FR[15][1], 1.6), (FR[15][1] + 1, 0.25)))
keys(nv(mat_supra, "Pulso"), sorted(pulses(FR[15][0], FR[15][1], 0.0, 0.13, 22)), interp="LINEAR")
# dolor en la frente cuando llega la señal (15)
d_ = [(FR[15][0], 0.0), (FR[15][0] + 18, 0.0)]
f = FR[15][0] + 22
while f + 6 < FR[15][1]:
    d_ += [(f, 0.95), (f + 6, 0.45)]
    f += 26
keys(ps, d_ + [(FR[15][1] - 1, 0.4), (FR[15][1], 0.0)])
# zonas de la cara que siente el trigémino (14): frente, mejilla y mandíbula se encienden en orden
nt_s = skin.node_tree
dtex = nt_s.nodes.new("ShaderNodeTexImage")
dtex.image = derm_img
duv = nt_s.nodes.new("ShaderNodeUVMap")
duv.uv_map = "UV"
nt_s.links.new(duv.outputs["UV"], dtex.inputs["Vector"])
dsep = nt_s.nodes.new("ShaderNodeSeparateColor")
nt_s.links.new(dtex.outputs["Color"], dsep.inputs[0])
dsum = None
dvals = []
for i_, ch in enumerate(("Red", "Green", "Blue")):
    dv = nt_s.nodes.new("ShaderNodeValue")
    dv.name = dv.label = f"Derm{i_ + 1}"
    dvals.append(dv)
    mm = nt_s.nodes.new("ShaderNodeMath")
    mm.operation = "MULTIPLY"
    nt_s.links.new(dsep.outputs[ch], mm.inputs[0])
    nt_s.links.new(dv.outputs[0], mm.inputs[1])
    if dsum is None:
        dsum = mm.outputs[0]
    else:
        ad = nt_s.nodes.new("ShaderNodeMath")
        ad.operation = "ADD"
        nt_s.links.new(dsum, ad.inputs[0])
        nt_s.links.new(mm.outputs[0], ad.inputs[1])
        dsum = ad.outputs[0]
for i_, dv in enumerate(dvals):
    a_ = FR[14][0] + 6 + 14 * i_
    keys(dv.outputs[0], ((1, 0.0), (a_, 0.0), (a_ + 6, 1.6), (a_ + 18, 0.8), (FR[14][1] - 1, 0.8), (FR[14][1], 0.0)))
# piel fantasma más tenue (silueta tipo rayos X) + brillos de dolor y de zonas que se ven aunque sea transparente
fant = nt_s.nodes["Fantasma"]
for n_ in nt_s.nodes:
    if n_.type == "MAP_RANGE" and abs(n_.inputs["To Max"].default_value - 0.95) < 1e-6 and abs(n_.inputs["To Min"].default_value - 0.05) < 1e-6:
        n_.inputs["To Min"].default_value, n_.inputs["To Max"].default_value = 0.0, 0.45
    if n_.type == "BSDF_PRINCIPLED" and abs(n_.inputs["Emission Strength"].default_value - 0.35) < 1e-6:
        n_.inputs["Base Color"].default_value = (0.85, 0.92, 1.0, 1)
        n_.inputs["Emission Color"].default_value = (0.7, 0.85, 1.0, 1)
        n_.inputs["Emission Strength"].default_value = 0.15
dol_n = nt_s.nodes["Dolor"]
pm_node = next(n_ for n_ in nt_s.nodes if n_.type == "MATH" and n_.operation == "MULTIPLY" and n_.inputs[0].links and n_.inputs[0].links[0].from_node == dol_n)
outn = nt_s.nodes["Material Output"]
last = outn.inputs["Surface"].links[0].from_socket


def _m(op, a, b):
    n_ = nt_s.nodes.new("ShaderNodeMath")
    n_.operation = op
    for i_, x_ in enumerate((a, b)):
        if isinstance(x_, (int, float)):
            n_.inputs[i_].default_value = x_
        else:
            nt_s.links.new(x_, n_.inputs[i_])
    return n_.outputs[0]


e_red = nt_s.nodes.new("ShaderNodeEmission")
e_red.inputs["Color"].default_value = (1.0, 0.10, 0.04, 1)
nt_s.links.new(_m("MULTIPLY", _m("MULTIPLY", pm_node.outputs[0], 5.0), fant.outputs[0]), e_red.inputs["Strength"])
e_gold = nt_s.nodes.new("ShaderNodeEmission")
e_gold.inputs["Color"].default_value = (1.0, 0.68, 0.12, 1)
nt_s.links.new(_m("MULTIPLY", _m("MULTIPLY", dsum, 0.35), fant.outputs[0]), e_gold.inputs["Strength"])
a1 = nt_s.nodes.new("ShaderNodeAddShader")
nt_s.links.new(last, a1.inputs[0])
nt_s.links.new(e_red.outputs[0], a1.inputs[1])
a2 = nt_s.nodes.new("ShaderNodeAddShader")
nt_s.links.new(a1.outputs[0], a2.inputs[0])
nt_s.links.new(e_gold.outputs[0], a2.inputs[1])
nt_s.links.new(a2.outputs[0], outn.inputs["Surface"])
# paladar: se escarcha cuando lo toca el helado (10, 31) y se entibia con la lengua (25)
mu = mat["PaladarMucosa"]
keys(nv(mu, "Escarcha"), ((1, 0.0), (FR[10][0] + 30, 0.0), (FR[10][0] + 62, 1.0), (FR[25][0] + 8, 1.0), (FR[25][0] + 48, 0.0)))
keys(nv(mu, "Tibio"), ((1, 0.0), (FR[25][0] + 10, 0.0), (FR[25][0] + 40, 1.0), (FR[25][1] - 1, 1.0), (FR[25][1], 0.0)))
# vasos que rodean el cerebro "duelen" (22): las arterias laten
la = [(1, 0.0), (FR[22][0], 0.0)]
f = FR[22][0]
while f + 12 < FR[22][1]:
    la += [(f + 4, 2.2), (f + 12, 0.4)]
    f += 12
la += [(FR[22][1], 0.0)]
keys(nv(mat["Arterias"], "Late"), la)
keys(nv(mat["ArteriaCerebralAnterior"], "Late"), la)

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


cam_face(1, 0.95, 0.82, side=-0.30, up=0.04, frac=0.28)
cam_face(2, 0.72, 0.66, side=-0.16, up=0.03, frac=0.28, shake=(FR[2][0], FR[2][0] + 18, 2.0, 0.035))
cam_face(3, 1.45, 1.30, side=-0.35, up=0.05, lens=45, frac=0.42)
cam_face(5, 1.5, 1.3, side=0.25, up=0.05, down=0.32, lens=45)
cam_face(6, 1.5, 1.4, side=0.0, up=0.05, down=0.3, lens=45)
# 7: plano general de la plaza, grúa
f0, f1 = FR[7]
camera("Cam07", f0, f1, [(f0, (-2.3, -5.2, 2.8), (0.3, 0.7, 1.0)), (f1 - 1, (-1.9, -4.6, 1.7), (0.3, 0.7, 1.1))], lens=32, fstop=5.6)
f0, f1 = FR[8]
camera("Cam08", f0, f1, [(f0, (0.4, -2.8, 1.55), (-0.35, 0.5, 1.25)), (f1 - 1, (0.45, -2.5, 1.45), (0.0, 0.4, 1.2))], lens=40)
cam_face(9, 1.05, 0.92, side=0.15, up=0.0, frac=0.28, shake=(FR[9][0], FR[9][1], 6.0, 0.012))
# Interior: SIEMPRE de perfil desde +x (lado izquierdo del personaje; la cara mira a la izquierda del cuadro), con un leve
# 3/4 hacia adelante y un push-in lento. Lo que se explica queda sobre la franja de subtítulos (52–65 % del alto).
# plano: (distancia inicio, distancia fin, objetivo relativo a los ojos, altura de la cámara sobre el objetivo a 0,3 m)
ICAM = {
    4: (0.72, 0.60, (0, 0.04, -0.02), 0.0),        # cabeza entera: el cerebro tibio, el frío nunca lo tocó
    10: (0.44, 0.38, (0, 0.000, -0.075), -0.05),   # la boca: el helado toca el paladar
    31: (0.38, 0.33, (0, 0.004, -0.075), -0.05),   # el paladar se escarcha
    13: (0.46, 0.40, (0, 0.02, -0.045), 0.0),      # el trigémino detecta el cambio
    14: (0.62, 0.56, (0, 0.0, -0.035), 0.0),       # el nervio que siente toda la cara
    15: (0.56, 0.48, (0, -0.035, 0.030), 0.0),     # una rama llega a la frente
    32: (0.52, 0.47, (0, 0.05, 0.02), 0.02),       # el cerebro se confunde
    21: (0.56, 0.64, (0, 0.05, 0.0), 0.02),        # el cerebro no siente dolor
    22: (0.62, 0.55, (0, 0.04, -0.02), 0.0),       # lo que duele: vasos y nervios que lo rodean
    25: (0.42, 0.36, (0, 0.000, -0.075), -0.05),   # la lengua calienta el paladar
}
for k, (d0, d1, tg, dz) in ICAM.items():
    f0, f1 = FR[k]
    h0, h1 = head_world(f0), head_world(f1 - 1)
    t_ = Vector(tg)
    cpos = [t_ + Vector((d * 0.98, -0.20 * d, dz * d / 0.3)) for d in (d0, d1)]
    ef = P.empty(f"FocoInt{k}", loc=h0 + t_)
    ks_ = [(f0, h0 + cpos[0], h0 + t_), (f1 - 1, h1 + cpos[1], h1 + t_)]
    if k == 4:  # entrada a la cabeza: parte de frente (como el plano anterior) y gira a perfil mientras se ve el interior
        fm_ = f0 + 34
        hm_ = head_world(fm_)
        ks_ = [(f0, h0 + t_ + Vector((0.0, -d0, 0.03)), h0 + t_), (fm_, hm_ + t_ + Vector((d0 * 0.75, -d0 * 0.62, 0.02)), hm_ + t_)] + ks_[1:]
    camera(f"Cam{k:02d}", f0, f1, ks_, lens=50, fstop=0, focus_obj=ef)
cam_face(16, 1.1, 0.95, side=-0.2, up=0.03, lens=45, frac=0.45)
f0, f1 = FR[17]
camera("Cam17", f0, f1, [(f0, LAB_O + Vector((-2.5, -4.2, 1.8)), LAB_O + Vector((-0.8, 0.4, 1.3))), (f1 - 1, LAB_O + Vector((1.2, -4.0, 1.7)), LAB_O + Vector((0.6, 0.4, 1.3)))], lens=35, fstop=5.6, focus_obj=bpy.data.objects["RigVol6"])
f0, f1 = FR[18]
camera("Cam18", f0, f1, [(f0, LAB_O + Vector((-0.5, -1.75, 1.62)), LAB_O + Vector((0.1, 0.4, 1.5))), (f1 - 1, LAB_O + Vector((-0.2, -1.5, 1.6)), LAB_O + Vector((0.2, 0.4, 1.5)))], lens=40, fstop=4.0, focus_obj=bpy.data.objects["RigVol6"])
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
camera("Cam23", f0, f1, [(f0, TXT_O + Vector((0, -6.0, 1.55)), TXT_O + Vector((0, 0, 1.52))), (f1 - 1, TXT_O + Vector((0, -5.5, 1.55)), TXT_O + Vector((0, 0, 1.52)))], lens=30, fstop=8, focus_obj=et,
       shake=(f0, f1, 3.0, 0.008))
cam_face(24, 0.95, 0.90, side=0.0, up=0.0, frac=0.28)
cam_face(26, 1.2, 1.05, side=-0.25, up=0.02, frac=0.28)
cam_face(27, 1.55, 1.35, side=0.35, up=0.05, down=0.32, lens=45)
f0, f1 = FR[28]
camera("Cam28", f0, f1, [(f0, (-0.9, -1.9, 1.62), (0.2, 0.4, 1.35)), (f1 - 1, (-0.75, -1.6, 1.6), (0.2, 0.4, 1.38))], lens=40)
cam_face(29, 1.1, 0.9, side=0.2, up=0.03, down=0.25, lens=45)
cam_face(30, 0.95, 0.95, side=-0.30, up=0.04, frac=0.28, f_eval=FR[1][0])  # mismo encuadre que el plano 1 -> loop
foco6 = P.empty("FocoVoluntario", loc=bpy.data.objects["RigVol6"].matrix_world @ (E + Vector((0, -0.02, 0))))
parent_bone(foco6, bpy.data.objects["RigVol6"], B + "Head")
cam_face(33, 1.15, 1.0, side=-0.2, up=0.03, lens=50, frac=0.30, foco=foco6)
cam_face(34, 0.95, 0.85, side=0.18, up=0.02, frac=0.28)
cam_face(35, 1.0, 0.9, side=-0.22, up=0.02, frac=0.28)
sc.camera = cams[0]

# flechas de las píldoras: posición en pantalla (1080x1920) de lo que se nombra, a mitad de cada plano
from bpy_extras.object_utils import world_to_camera_view
_cs = [TK @ v.co for v in kit["CortezaSensitiva"].data.vertices if v.co.x > 0]
_xm = max(c.x for c in _cs)
_cs = [c for c in _cs if c.x > _xm - 0.012]
P_COR = sum(_cs, Vector()) / len(_cs)
P_PAL = PAL_F.lerp(PAL_S, 0.40)
P_GAN = TK @ G_ATLAS
flechas = {}
for k_, p_ in ((10, P_PAL), (31, P_PAL), (25, P_PAL), (13, P_GAN), (32, P_COR)):
    fm = (FR[k_][0] + FR[k_][1]) // 2
    cam_ = bpy.data.objects[f"Cam{k_:02d}"]
    w_ = head_world(fm, p_ - E)
    sc.frame_set(fm)
    v_ = world_to_camera_view(sc, cam_, w_)
    flechas[k_] = [round(v_.x * 1080), round((1 - v_.y) * 1920)]
print("flechas", flechas)
meta = {"FR": FR, "T": T, "END": END, "interior": INTERIOR, "flechas": flechas}
json.dump(meta, open(os.path.join(OUT, "ep01_planos.json"), "w"), indent=1)
# letras del plano 23: caída visible (key_vis las había dejado en CONSTANT y aparecían de golpe)
for t, row, k in letters:
    for fc in anim._fcurves(t.animation_data.action):
        if fc.data_path == "delta_location":
            kps = list(fc.keyframe_points)
            for j, kp in enumerate(kps):
                kp.interpolation = "BEZIER"
            if len(kps) >= 3:
                kps[1].interpolation, kps[1].easing = "QUAD", "EASE_IN"   # cae acelerando
                kps[2].interpolation = "BEZIER"                            # rebote chico
            fc.update()

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "ep01.blend"))
print("ok ep01", END, "cuadros")
