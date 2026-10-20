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
S = BQ.armar_v2(C) if os.environ.get("BOSQUE", "v2") == "v2" else BQ.armar(C)
bpy.context.view_layer.update()
_r = S["rama"]
_me = bpy.data.meshes.new_from_object(_r.evaluated_get(bpy.context.evaluated_depsgraph_get()))
_rm = bpy.data.objects.new("RamaMalla", _me)
C.objects.link(_rm)
_rm.matrix_world = _r.matrix_world
_rm.hide_render = True
S["rama"] = _rm
(BQ.luz_bosque(sc) if os.environ.get("BOSQUE", "v2") == "v2" else BQ.cielo_bosque(sc))
tp = PJ.tupaya(C)
# parada ENCIMA de la rama: altura sacada con un rayo contra la rama (las patas apoyan, no cuelgan por delante)
bpy.context.view_layer.update()
_dg = bpy.context.evaluated_depsgraph_get()
_rama = S["rama"]
def sobre_rama(x, y):
    Mi = _rama.matrix_world.inverted()
    me = _rama.evaluated_get(_dg)
    hit, loc, *_ = me.ray_cast(Mi @ Vector((x, y, 1.0)), (Mi.to_3x3() @ Vector((0, 0, -1))).normalized())
    return (_rama.matrix_world @ loc).z if hit else 0.135
TX = float(os.environ.get("TUP_X", -0.02))
tp["root"].location = (TX, 0.0, sobre_rama(TX, 0.0) - 0.002)
tp["root"].rotation_euler.z = math.radians(float(os.environ.get("TUP_ROT", 72)))   # de costado (como la ficha), un poco hacia cámara
# luz manchada de sol entre las hojas (de lado, cálida) + contorno
def area(name, loc, energy, size, color, target=(0.0, 0.0, 0.22)):
    L = bpy.data.lights.new(name, "AREA")
    L.energy, L.size, L.color, L.shape = energy, size, color, "DISK"
    ob = bpy.data.objects.new(name, L)
    sc.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
if os.environ.get("BOSQUE", "v2") == "v2":
    area("Relleno", (0.4, -0.9, 0.5), float(os.environ.get("FILL", 6)), 0.8, (0.70, 0.85, 1.0))       # relleno frío y suave desde cámara
    area("Contorno", (-0.35, 0.45, 0.55), float(os.environ.get("RIM", 40)), 0.25, (1.0, 0.80, 0.50))  # borde cálido en la tupaya
    # mancha de sol sobre la tupaya y la rama (luz principal cálida que "se cuela" entre las hojas)
    Ls = bpy.data.lights.new("RayoSol", "SPOT")
    Ls.energy, Ls.color = float(os.environ.get("RAYO", 130)), (1.0, 0.84, 0.58)
    Ls.spot_size, Ls.spot_blend, Ls.shadow_soft_size = math.radians(22), 0.6, 0.02
    os_ = bpy.data.objects.new("RayoSol", Ls)
    sc.collection.objects.link(os_)
    os_.location = (-0.55, -0.35, 1.25)
    os_.rotation_euler = (Vector((0.0, 0.0, 0.20)) - os_.location).to_track_quat("-Z", "Y").to_euler()
    sc.cycles.volume_step_rate = 4.0
    sc.cycles.volume_max_steps = 256
else:
    area("Key", (-0.6, -0.7, 0.9), 22, 0.5, (1.0, 0.88, 0.65))
    area("Contorno", (0.5, 0.7, 0.6), 30, 0.4, (1.0, 0.85, 0.55))
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.lens = float(os.environ.get("LENS", 28))
cam.data.sensor_fit = "VERTICAL"
cam.data.sensor_height = 24
bpy.context.view_layer.update()
cab_w = tp["cabeza"].matrix_world.translation
tgt = cab_w + Vector(tuple(float(x) for x in os.environ.get("TGT", "-0.05,0.0,-0.035").split(",")))
cam.location = tgt + Vector(tuple(float(x) for x in os.environ.get("CAMOFF", "-0.05,-0.62,0.03").split(",")))
cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = (cab_w - cam.location).length
cam.data.dof.aperture_fstop = 2.8
# la tupaya mira a cámara (storyboard plano 30): giro de la cabeza calculado hacia la cámara
bpy.context.view_layer.update()
pc = tp["cabeza"]
loc_cam = (pc.parent.matrix_world.inverted() @ cam.location) - pc.location
yaw = math.atan2(loc_cam.x, -loc_cam.y) * float(os.environ.get("MIRA_CAM", 0.75))   # gira 3/4 de lo necesario: mira a cámara y el hocico largo se sigue viendo de lado
pitch = -math.atan2(loc_cam.z, Vector((loc_cam.x, loc_cam.y)).length)
pc.rotation_mode = "XYZ"   # R = Rz·Rx: primero cabecea, después gira
pc.rotation_euler = (pitch, 0, yaw)
print("tupaya cabeza yaw/pitch", round(math.degrees(yaw)), round(math.degrees(pitch)))
# los dos ojos miran a la cámara (en la ficha se ven negros; de lado el ojo lejano mostraba el blanco)
bpy.context.view_layer.update()
Rinv = pc.matrix_world.to_3x3().normalized().inverted()
for o in tp["ojos"]:
    d = Rinv @ (cam.location - o.matrix_world.translation)
    o.rotation_euler = d.to_track_quat("-Y", "Z").to_euler()
sc.render.filepath = os.path.join(OUT, os.environ.get("NOMBRE", "estilo_bosque") + ".png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath)
