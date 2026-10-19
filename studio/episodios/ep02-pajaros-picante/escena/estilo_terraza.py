"""Cuadro de estilo del set "terraza" del Ep. 2 (y cuadro 0 con el pájaro, si hay modelo).

Uso: PERSONAJE=.../personaje.blend MIXAMO_DIR=... [PAJARO=modelo.glb] [RES=720x1280] [SAMPLES=48] [TOMA=cuadro0|medio]
     OUT=carpeta python3 estilo_terraza.py
"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.abspath(os.path.join(HERE, "../../.."))
PJ = os.path.join(STUDIO, "personaje")
for p in (HERE, os.path.join(STUDIO, "plantilla"), PJ):
    sys.path.insert(0, p)
import bpy
from mathutils import Vector
import props as P
import props_ep02 as E
import anim
import pajaro as PA

OUT = os.environ.get("OUT", os.path.join(HERE, "out"))
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.environ.get("PERSONAJE", os.path.join(PJ, "out", "personaje.blend")))
sc = bpy.context.scene
res = tuple(int(v) for v in os.environ.get("RES", "720x1280").split("x"))
sc.render.engine = "CYCLES"
sc.cycles.device = os.environ.get("DEVICE", "CPU")
sc.cycles.samples = int(os.environ.get("SAMPLES", 48))
sc.cycles.use_adaptive_sampling = True
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 6
sc.cycles.transparent_max_bounces = 12
sc.render.resolution_x, sc.render.resolution_y = res
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Punchy"
sc.render.image_settings.file_format = "PNG"
if not sc.world:
    sc.world = bpy.data.worlds.new("Mundo")
sc.world.use_nodes = True
w = sc.world.node_tree.nodes["Background"]
w.inputs["Color"].default_value = (0.55, 0.78, 0.95, 1)
w.inputs["Strength"].default_value = 0.25

C = P.collection("Terraza")
H = E.terraza(C)
meson_y = float(os.environ.get("MESON_Y", -0.52))
for n in ("Meson", "MesonFrente"):
    bpy.data.objects[n].location.y = meson_y

rig = bpy.data.objects["Rig"]
act = anim.load_action(os.path.join(os.environ.get("MIXAMO_DIR", "/home/claude/work/mixamo"), "Happy Idle.fbx"), rig)
anim.assign(rig, act)
sc.frame_set(int(os.environ.get("FRAME_ANIM", 40)))

# expresión: llora con el picante (ojos apretados, cejas al centro, boca abierta) — sólo si la toma lo pide
TOMA = os.environ.get("TOMA", "cuadro0")
EXPR = {"cuadro0": {"eye-left-closure": .75, "eye-right-closure": .75, "eyebrows-left-inner-up": .9, "eyebrows-right-inner-up": .9,
                    "mouth-open": .55, "mouth-depression-retraction": .5, "nose-left-elevation": .4, "nose-right-elevation": .4},
        "medio": {"mouth-corner-puller": .25}}[TOMA]
for o in bpy.data.objects:
    if o.type == "MESH" and o.data.shape_keys:
        for k, v in EXPR.items():
            if k in o.data.shape_keys.key_blocks:
                o.data.shape_keys.key_blocks[k].value = v

# utilería sobre el mesón
top_z = H
pl = E.plato(coll=C)
pl.location = (0.16, meson_y - 0.02, top_z)
for i, (dx, dy, rz) in enumerate([(0.0, 0.0, 0.3), (0.025, 0.02, 1.9), (-0.02, 0.025, 3.6)]):
    a = E.aji(f"AjiPlato{i}", largo=0.11, grosor=0.015, coll=C, seed=10 + i)
    a.location = (0.16 + dx, meson_y - 0.02 + dy, top_z + 0.018)
    a.rotation_euler = (math.radians(90), 0, rz)
mac, ajies = E.maceta_aji(coll=C)
mac.location = (-0.42, meson_y + 0.12, top_z)
vaso = E.vaso_leche(coll=C)
vaso.location = (0.40, meson_y + 0.06, top_z)

# luces de estudio (R4): principal suave cálida, relleno frío, contorno
def area(name, loc, energy, size, color, target=(0, -0.3, 1.2)):
    L = bpy.data.lights.new(name, "AREA")
    L.energy, L.size, L.color, L.shape = energy, size, color, "DISK"
    ob = bpy.data.objects.new(name, L)
    sc.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return ob

area("Key", (-1.4, -2.2, 2.4), 200, 2.2, (1.0, 0.95, 0.88))
area("Fill", (1.8, -1.9, 1.5), 60, 2.6, (0.88, 0.94, 1.0))
area("Rim", (0.9, 0.9, 2.5), 160, 1.2, (1.0, 0.96, 0.9), target=(0, 0, 1.5))

# pájaro (si hay modelo)
pajaro = None
if os.environ.get("PAJARO"):
    pajaro = PA.importar(os.environ["PAJARO"], C, largo=float(os.environ.get("PAJARO_LARGO", 0.22)))
    pajaro.location = (0.07, meson_y - 0.12, top_z)
    pajaro.rotation_euler.z = math.radians(float(os.environ.get("PAJARO_ROT", -60)))
    pa = E.aji("AjiPajaro", largo=0.10, grosor=0.014, coll=C, seed=21)
    pa.location = (0.0, meson_y - 0.19, top_z + 0.016)
    pa.rotation_euler = (math.radians(90), 0, math.radians(20))

cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.sensor_fit = "VERTICAL"
cam.data.sensor_height = 24
if TOMA == "cuadro0":
    # primer plano a la altura del mesón: pájaro y ají nítidos, el protagonista llorando detrás (desenfocado)
    tgt = Vector((0.04, meson_y - 0.15, top_z + 0.07))
    cam.location = tgt + Vector((-0.10, -0.62, 0.10))
    cam.data.lens = 50
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = (tgt - cam.location).length
    cam.data.dof.aperture_fstop = 2.8
    look = tgt + Vector((0, 0, 0.16))
else:
    tgt = Vector((0.0, -0.2, 1.30))
    cam.location = Vector((-0.30, -2.5, 1.42))
    cam.data.lens = 32
    look = tgt
cam.rotation_euler = (look - cam.location).to_track_quat("-Z", "Y").to_euler()

sc.render.filepath = os.path.join(OUT, f"estilo_terraza_{TOMA}.png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath)
