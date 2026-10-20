"""Cuadro de estilo del bosque de China: la tupaya en la rama, junto a las espigas picantes de Piper."""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.abspath(os.path.join(HERE, "../../.."))
for p in (HERE, os.path.join(STUDIO, "plantilla")):
    sys.path.insert(0, p)
import bpy
from mathutils import Vector
import props as P
import personajes as PJ
import bosque as BQ

OUT = os.environ.get("OUT", os.path.join(HERE, "out"))
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
res = tuple(int(v) for v in os.environ.get("RES", "720x1280").split("x"))
sc.render.engine = "CYCLES"
sc.cycles.device = os.environ.get("DEVICE", "CPU")
sc.cycles.samples = int(os.environ.get("SAMPLES", 64))
sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = res
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Punchy"
sc.world = bpy.data.worlds.new("Bosque")
sc.world.use_nodes = True
C = P.collection("Bosque")
S = BQ.armar(C)
BQ.cielo_bosque(sc)
tp = PJ.tupaya(C)
tp["root"].location = (0.0, 0.0, 0.135)
tp["root"].rotation_euler.z = math.radians(float(os.environ.get("TUP_ROT", 40)))
tp["cabeza"].rotation_euler = (math.radians(12), 0, math.radians(-10))
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.lens = 40
cam.data.sensor_fit = "VERTICAL"
cam.data.sensor_height = 24
tgt = Vector((0.04, 0.0, 0.24))
cam.location = tgt + Vector((-0.12, -0.75, 0.02))
cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = (Vector((0.0, 0.0, 0.22)) - cam.location).length
cam.data.dof.aperture_fstop = 2.8
sc.render.filepath = os.path.join(OUT, os.environ.get("NOMBRE", "estilo_bosque") + ".png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath)
