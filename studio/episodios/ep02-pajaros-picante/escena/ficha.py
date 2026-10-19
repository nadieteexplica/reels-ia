"""Ficha de personajes del Ep. 2 (y pruebas de modelado): render de estudio de cada personaje.

Uso: QUIEN=pajaro|raton|ambos VISTAS=3q,frente,perfil RES=540x960 SAMPLES=32 OUT=carpeta python3 ficha.py
"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.abspath(os.path.join(HERE, "../../.."))
for p in (HERE, os.path.join(STUDIO, "plantilla")):
    sys.path.insert(0, p)
import bpy
from mathutils import Vector
import props as P
import personajes as PJ

OUT = os.environ.get("OUT", os.path.join(HERE, "out"))
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
res = tuple(int(v) for v in os.environ.get("RES", "540x960").split("x"))
sc.render.engine = "CYCLES"
sc.cycles.device = os.environ.get("DEVICE", "CPU")
sc.cycles.samples = int(os.environ.get("SAMPLES", 32))
sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = res
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Punchy"
sc.world = bpy.data.worlds.new("Mundo")
sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.25, 0.62, 0.70, 1)
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
C = P.collection("Ficha")
piso = P.prim("cyl", "Piso", C, P.mat("PisoFicha", (0.80, 0.55, 0.32), rough=0.8), r=1.6, r2=1.6, h=0.02, seg=64)
piso.location = (0, 0, -0.01)

QUIEN = os.environ.get("QUIEN", "pajaro")
if QUIEN == "elenco":
    # ficha del episodio: todos los personajes en fila (lo que usa el auditor para comparar)
    pj = PJ.pajaro(C)
    pj["root"].location = (-0.33, 0.0, 0)
    pj["root"].rotation_euler.z = math.radians(-15)
    rt = PJ.raton(C)
    rt["root"].location = (-0.12, 0.02, 0)
    rata = PJ.raton(C, "Rata", lomo=(0.20, 0.17, 0.14), guata=(0.62, 0.58, 0.52), oreja=0.019, hocico=1.35)
    rata["root"].scale = (1.3, 1.3, 1.3)
    rata["root"].location = (0.08, 0.06, 0)
    inm = PJ.raton(C, "RatonInmune")
    inm["root"].location = (0.30, 0.02, 0)
    bpy.context.view_layer.update()
    for o in inm["ojos"]:
        pass
    cab = inm["cabeza"]
    lt = PJ.lentes("LentesInmune", cab.matrix_world @ Vector((0, -0.045, 0.040)), 0.05, C)
    PJ.colgar(lt, cab)
    md = PJ.medalla("MedallaInmune", (0.30, -0.035, 0.085), 0.012, C)
    tp = PJ.tupaya(C)
    tp["root"].location = (0.52, 0.04, 0)
    tp["root"].rotation_euler.z = math.radians(35)
    gd = PJ.aji_guardia(C)
    gd["root"].location = (0.74, 0.08, 0)

if QUIEN in ("pajaro", "ambos"):
    pj = PJ.pajaro(C)
    if QUIEN == "ambos":
        pj["root"].location.x = -0.12
    for pv in pj["parpados"]:
        pv.rotation_euler.x += math.radians(float(os.environ.get("PARPADO", 0)))
if QUIEN in ("raton", "ambos") and hasattr(PJ, "raton"):
    rt = PJ.raton(C)
    if QUIEN == "ambos":
        rt["root"].location.x = 0.14


def area(name, loc, energy, size, color, target=(0, 0, 0.10)):
    L = bpy.data.lights.new(name, "AREA")
    L.energy, L.size, L.color, L.shape = energy, size, color, "DISK"
    ob = bpy.data.objects.new(name, L)
    sc.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()

area("Key", (-0.9, -1.1, 1.1), 55, 0.9, (1.0, 0.90, 0.78))
area("Fill", (1.0, -0.9, 0.5), 18, 1.2, (0.80, 0.90, 1.0))
area("Rim", (0.5, 0.9, 0.9), 45, 0.6, (1.0, 0.92, 0.80))

cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.lens = 60
cam.data.sensor_fit = "VERTICAL"
cam.data.sensor_height = 24
tgt = {"ambos": Vector((0.01, -0.01, 0.10)), "elenco": Vector((0.20, 0.0, 0.12))}.get(QUIEN, Vector((0, -0.01, 0.12)))
dist = float(os.environ.get("DIST", {"ambos": 1.25, "elenco": 2.6}.get(QUIEN, 0.95)))
VISTAS = {"3q": (-35, 8), "frente": (0, 6), "perfil": (-90, 4), "atras": (150, 12)}
for v in os.environ.get("VISTAS", "3q,frente,perfil").split(","):
    az, el = VISTAS[v]
    d = Vector((math.sin(math.radians(az)), -math.cos(math.radians(az)), math.tan(math.radians(el))))
    cam.location = tgt + d.normalized() * dist
    cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(OUT, f"ficha_{QUIEN}_{v}.png")
    bpy.ops.render.render(write_still=True)
    print("ok", sc.render.filepath)
