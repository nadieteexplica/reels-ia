"""Cuadro de estilo del set "desierto" (= cuadro 0 del Ep. 2): el cuitlacoche con un ají en el pico, tranquilo,
y el ratón detrás echando fuego por la boca, con lágrimas.

Uso: RES=720x1280 SAMPLES=64 [DEVICE=CPU|OPTIX] OUT=carpeta python3 estilo_desierto.py
"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.abspath(os.path.join(HERE, "../../.."))
for p in (HERE, os.path.join(STUDIO, "plantilla")):
    sys.path.insert(0, p)
import bpy
from mathutils import Vector, Euler
import props as P
import props_ep02 as E
import personajes as PJ
import desierto as D
import vfx as V

OUT = os.environ.get("OUT", os.path.join(HERE, "out"))
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
res = tuple(int(v) for v in os.environ.get("RES", "720x1280").split("x"))
sc.render.engine = "CYCLES"
sc.cycles.device = os.environ.get("DEVICE", "CPU")
sc.cycles.samples = int(os.environ.get("SAMPLES", 64))
sc.cycles.use_adaptive_sampling = True
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 8
sc.cycles.transparent_max_bounces = 16
sc.render.resolution_x, sc.render.resolution_y = res
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Punchy"
sc.render.image_settings.file_format = "PNG"
sc.world = bpy.data.worlds.new("Cielo")
sc.world.use_nodes = True

C = P.collection("Desierto")
S = D.armar(C)
TOP = S["top"]
D.cielo(sc, sol_elev=float(os.environ.get("SOL_ELEV", 12)), sol_azim=float(os.environ.get("SOL_AZIM", -150)),
        fuerza=float(os.environ.get("SOL", 3.0)))

# relleno frío desde cámara (el cielo) y un contorno cálido
def area(name, loc, energy, size, color, target):
    L = bpy.data.lights.new(name, "AREA")
    L.energy, L.size, L.color, L.shape = energy, size, color, "DISK"
    ob = bpy.data.objects.new(name, L)
    sc.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
area("Relleno", (-0.8, -1.4, 0.9), float(os.environ.get("FILL", 14)), 1.2, (0.75, 0.88, 1.0), (0.05, 0.0, TOP + 0.1))

# --- pájaro con el ají en el pico ---
CP = P.collection("Personajes")
pj = PJ.pajaro(CP)
pj["root"].location = (-0.02, -0.10, TOP)
pj["root"].rotation_euler.z = math.radians(float(os.environ.get("PAJ_ROT", -28)))
pj["cabeza"].rotation_euler = (math.radians(-6), 0, math.radians(8))
pj["mandibula"].rotation_euler.x = math.radians(9)
for pv in pj["parpados"]:
    for ch in pv.children:
        ch.rotation_euler.x = math.radians(float(os.environ.get("PARPADO", -30)))   # media asta: "ni lo siente"
bpy.context.view_layer.update()
piv = pj["pico"]
M = piv.matrix_world
centro_aji = M @ (piv.matrix_world.inverted() @ (pj["pico"].matrix_world @ Vector((0, -0.030, -0.009))))
aji = E.aji("AjiCuadro0", largo=0.12, grosor=0.0125, coll=CP, seed=5, curva=0.45)
# el ají cruza el pico de lado a lado (como un puro), con el tallo hacia la izquierda de la pantalla
eje_x = (M.to_3x3() @ Vector((1, 0, 0))).normalized()
aji.rotation_euler = (eje_x).to_track_quat("-Z", "Y").to_euler()
aji.location = centro_aji - eje_x * 0.050
aji.rotation_euler.rotate(Euler((0, 0, math.radians(180)), "XYZ"))
bpy.context.view_layer.update()

# --- ratón detrás, echando fuego ---
rt = PJ.raton(CP)
rt["root"].location = (0.17, 0.16, TOP)
rt["root"].rotation_euler.z = math.radians(float(os.environ.get("RAT_ROT", 22)))
rt["cabeza"].rotation_euler = (math.radians(-12), 0, 0)
rt["boca"].scale = (1.6, 1.4, 3.2)
for pv in rt["parpados"]:
    for ch in pv.children:
        ch.rotation_euler.x = math.radians(70)          # ojos apretados
for k, ob in enumerate(rt["orejas"]):
    ob.rotation_euler = (math.radians(35), 0, math.radians(18 * (1 if k else -1)))   # orejas hacia atrás
for k, br in enumerate(rt["brazos"]):
    br.rotation_euler = (math.radians(-55), 0, math.radians(30 * (1 if k else -1)))   # patitas arriba, sin tocar nada
bpy.context.view_layer.update()
boca_w = rt["boca"].matrix_world.translation
frente_rt = (rt["cabeza"].matrix_world.to_3x3() @ Vector((0, -1, 0.55))).normalized()
V.llamarada("Llamarada", boca_w + frente_rt * 0.004, frente_rt, CP, escala=float(os.environ.get("FUEGO", 1.1)))
for o in rt["ojos"]:
    ow = o.matrix_world.translation
    abajo = (rt["cabeza"].matrix_world.to_3x3() @ Vector((0, -0.3, -1))).normalized()
    V.lagrimas(o.name + "_lagr", ow + abajo * 0.010, abajo, CP, largo=0.028, seed=1)

# --- cámara ---
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.sensor_fit = "VERTICAL"
cam.data.sensor_height = 24
cam.data.lens = float(os.environ.get("LENS", 55))
foco = Vector((-0.03, -0.17, TOP + 0.14))
cam.location = foco + Vector(tuple(float(x) for x in os.environ.get("CAMOFF", "-0.10,-0.62,0.03").split(",")))
mira = foco + Vector(tuple(float(x) for x in os.environ.get("MIRA", "0.05,0.10,0.06").split(",")))
cam.rotation_euler = (mira - cam.location).to_track_quat("-Z", "Y").to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = (foco - cam.location).length
cam.data.dof.aperture_fstop = float(os.environ.get("FSTOP", 3.2))

sc.render.filepath = os.path.join(OUT, os.environ.get("NOMBRE", "estilo_desierto_cuadro0") + ".png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath)
