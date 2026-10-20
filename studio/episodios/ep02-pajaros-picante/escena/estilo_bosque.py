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
tp["cabeza"].rotation_euler = (math.radians(14), 0, math.radians(-35))
# luz manchada de sol entre las hojas (de lado, cálida) + contorno
def area(name, loc, energy, size, color, target=(0.0, 0.0, 0.22)):
    L = bpy.data.lights.new(name, "AREA")
    L.energy, L.size, L.color, L.shape = energy, size, color, "DISK"
    ob = bpy.data.objects.new(name, L)
    sc.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
area("Key", (-0.6, -0.7, 0.9), 22, 0.5, (1.0, 0.88, 0.65))
area("Contorno", (0.5, 0.7, 0.6), 30, 0.4, (1.0, 0.85, 0.55))
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.lens = 40
cam.data.sensor_fit = "VERTICAL"
cam.data.sensor_height = 24
tgt = Vector((0.04, 0.0, 0.26))
cam.location = tgt + Vector((-0.20, -0.62, -0.02))
cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = (Vector((0.0, 0.0, 0.22)) - cam.location).length
cam.data.dof.aperture_fstop = 2.8
# la tupaya mira a cámara (storyboard plano 30): giro de la cabeza calculado hacia la cámara
bpy.context.view_layer.update()
pc = tp["cabeza"]
loc_cam = (pc.parent.matrix_world.inverted() @ cam.location) - pc.location
yaw = math.atan2(loc_cam.x, -loc_cam.y) + math.radians(float(os.environ.get("TUP_34", 10)))   # tres cuartos: mira a cámara y se le ve el hocico
pitch = -math.atan2(loc_cam.z, Vector((loc_cam.x, loc_cam.y)).length)
pc.rotation_mode = "XYZ"   # R = Rz·Rx: primero cabecea, después gira
pc.rotation_euler = (pitch, 0, yaw)
print("tupaya cabeza yaw/pitch", round(math.degrees(yaw)), round(math.degrees(pitch)))
sc.render.filepath = os.path.join(OUT, os.environ.get("NOMBRE", "estilo_bosque") + ".png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath)
