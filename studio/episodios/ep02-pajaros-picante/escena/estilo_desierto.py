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
D.cielo(sc, sol_elev=float(os.environ.get("SOL_ELEV", 16)), sol_azim=float(os.environ.get("SOL_AZIM", -55)),
        fuerza=float(os.environ.get("SOL", 3.0)))

# relleno frío desde cámara (el cielo) y un contorno cálido
def area(name, loc, energy, size, color, target):
    L = bpy.data.lights.new(name, "AREA")
    L.energy, L.size, L.color, L.shape = energy, size, color, "DISK"
    ob = bpy.data.objects.new(name, L)
    sc.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
area("Relleno", (0.9, -1.3, 0.8), float(os.environ.get("FILL", 10)), 1.2, (0.75, 0.88, 1.0), (0.05, 0.0, TOP + 0.1))
area("Contorno", (0.5, 1.1, 0.75), float(os.environ.get("RIM", 60)), 0.6, (1.0, 0.70, 0.40), (0.05, 0.0, TOP + 0.12))

# --- pájaro con el ají en el pico (se arma en el origen y después se ubica) ---
CP = P.collection("Personajes")
pj = PJ.pajaro(CP)
pj["mandibula"].rotation_euler.x = math.radians(float(os.environ.get("MANDIBULA", 20)))   # pico abierto: se ven las dos mitades, arriba y abajo del ají
bpy.context.view_layer.update()
pj["mandibula"].rotation_euler.x = math.radians(float(os.environ.get("PICO_ABRE", 22)))
bpy.context.view_layer.update()
# hueco real entre las mandíbulas a DIST del pivote del pico (medido en las mallas, coordenadas de la raíz del pájaro)
DIST = float(os.environ.get("PICO_DIST", 0.022))
def _verts(nombre):
    o = bpy.data.objects[nombre]
    dg = bpy.context.evaluated_depsgraph_get()
    ev = o.evaluated_get(dg)
    me = ev.to_mesh()
    Mi = pj["root"].matrix_world.inverted() @ o.matrix_world
    pts = [Mi @ v.co for v in me.vertices]
    ev.to_mesh_clear()
    return pts
pb_loc = pj["root"].matrix_world.inverted() @ pj["pico"].matrix_world.translation
y0 = pb_loc.y - DIST
sup_b = min(p.z for p in _verts("Cuitlacoche_pico_sup") if abs(p.y - y0) < 0.0015 and abs(p.x) < 0.004)
inf_t = max(p.z for p in _verts("Cuitlacoche_pico_inf") if abs(p.y - y0) < 0.0015 and abs(p.x) < 0.004)
hueco = sup_b - inf_t
print("pico: hueco", round(hueco * 1000, 1), "mm a", DIST * 1000, "mm de la base")
# el ají de props_ep02.aji tiene su radio máximo ~0,77·grosor a un 30 % de su largo: ese punto queda entre las mandíbulas,
# un 6 % más grueso que el hueco (las mandíbulas aprietan y lo hunden apenas)
GROS = hueco / 2 * 1.06 / 0.767
aji = E.aji("AjiCuadro0", largo=0.12, grosor=GROS, coll=CP, seed=5, curva=float(os.environ.get("AJI_CURVA", 0.12)))
aji.rotation_euler = (0, math.radians(-90), math.radians(8))
aji.location = (0.0, y0, (sup_b + inf_t) / 2)
bpy.context.view_layer.update()
eje = (aji.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()
aji.location -= eje * 0.12 * 0.30          # corre el ají para que su 30 % (lo más grueso) quede en el pico
aji.location = pj["root"].matrix_world @ aji.location if False else aji.location
PJ.colgar(aji, pj["pico"])
for pv in pj["parpados"]:
    for ch in pv.children:
        ch.rotation_euler.x = math.radians(float(os.environ.get("PARPADO", -30)))   # media asta: "ni lo siente"
pj["cabeza"].rotation_euler = (math.radians(-4), 0, math.radians(10))
pj["root"].location = (0.0, -0.16, TOP)
pj["root"].rotation_euler.z = math.radians(float(os.environ.get("PAJ_ROT", -8)))

# --- ratón detrás, en una roca más alta, echando fuego ---
roca2 = D.roca("RocaAtras", (0.12, 0.30, 0), (0.50, 0.30, 0.36), C, seed=3)
TOP2 = 0.36
rt = PJ.raton(CP)
rt["root"].scale = (1.15, 1.15, 1.15)
rt["boca"].scale = (1.6, 1.4, 3.2)
for pv in rt["parpados"]:
    for ch in pv.children:
        ch.rotation_euler.x = math.radians(-115)        # ojos muy abiertos (de susto)
PJ.cara_roja(rt)
for k, ob in enumerate(rt["orejas"]):
    ob.rotation_euler = (math.radians(30), 0, math.radians(15 * (1 if k else -1)))
for k, br in enumerate(rt["brazos"]):
    br.rotation_euler = (math.radians(-60), 0, math.radians(35 * (1 if k else -1)))   # patitas arriba, sin tocar nada
rt["cabeza"].rotation_euler = (math.radians(-16), 0, 0)
rt["root"].location = (0.19, 0.20, TOP2)          # tabla de utilería del storyboard
rt["root"].rotation_euler.z = math.radians(float(os.environ.get("RAT_ROT", -60)))
# causa de la llama: un ají mordido junto al ratón, y los lentes de sol caídos (detalle del loop)
aj_m = E.aji("AjiMordido", largo=0.10, grosor=0.012, coll=CP, seed=11, curva=0.3)
# acostado de lado (tallo a la izquierda): el mordisco queda en el costado que mira a la cámara y se lee
AJM = tuple(float(v) for v in os.environ.get("AJM", "0.235,0.235,-80").split(","))
aj_m.rotation_euler = (math.radians(90), 0, math.radians(AJM[2]))
aj_m.location = (AJM[0], AJM[1], 0.0)
E.mordisco_media_luna(aj_m, CP, t=0.55, lado=(0, 1, 0), r=0.0085)   # media luna en la silueta de arriba, con semillas
# la cámara mira la roca de atrás desde abajo: lo que queda tirado plano en la cima no se ve. Los lentes y la medalla
# quedan en el escalón delantero de la roca (z≈0,30, se ve desde la cámara y no lo tapa la cola), recostados hacia atrás.
# las pistas (ají mordido, lentes, medalla) van sobre dos piedras apiladas a los lados del ratón: quedan sobre la
# franja de subtítulos (y < 980 de 1920) y se leen; en la cima plana de la roca caían dentro de la franja
REP = [tuple(float(v) for v in t.split(",")) for t in os.environ.get("REPISAS", "0.300,0.225,0.19,0.11,0.085").split(";")]
repisas = [D.roca(f"Repisa{i}", (x, y, TOP2 - 0.01), (sx, sy, sz), C, seed=30 + i) for i, (x, y, sx, sy, sz) in enumerate(REP)]
bpy.context.view_layer.update()
def cima(x, y):
    """z de la superficie más alta (roca de atrás o repisas) en (x, y) (rayo sólo contra rocas, no contra personajes ni llama)."""
    dg = bpy.context.evaluated_depsgraph_get()
    best = None
    for ob in [roca2] + repisas:
        Mi = ob.matrix_world.inverted()
        hit, loc, *_ = ob.evaluated_get(dg).ray_cast(Mi @ Vector((x, y, 1.5)), (Mi.to_3x3() @ Vector((0, 0, -1))).normalized())
        if hit:
            z = (ob.matrix_world @ loc).z
            best = z if best is None else max(best, z)
    return best if best is not None else TOP2
aj_m.location.z = cima(AJM[0] + 0.05, AJM[1]) + 0.011
LX, LY = (float(v) for v in os.environ.get("LENTES_XY", "0.300,0.205").split(","))
MX, MY = (float(v) for v in os.environ.get("MEDALLA_XY", "0.343,0.215").split(","))
lc = PJ.lentes("LentesCaidos", (LX, LY, cima(LX, LY) + 0.0135), 0.05, CP, mirando=(-0.35, -1.0, 0.55))
mc = PJ.medalla("MedallaCaida", (MX, MY, cima(MX, MY) + 0.016), 0.017, CP)   # más grande: tiene que leerse en el celular
mc.rotation_euler = (math.radians(-35), 0, math.radians(-15))      # disco recostado hacia atrás, cinta apoyada

bpy.context.view_layer.update()
boca_w = rt["boca"].matrix_world.translation
frente_rt = (rt["cabeza"].matrix_world.to_3x3() @ Vector((0, -1, 0.0))).normalized()
frente_rt = (frente_rt + Vector((0, 0, float(os.environ.get("FUEGO_SUBE", 0.12))))).normalized()
V.llamarada("Llamarada", boca_w + frente_rt * float(os.environ.get("FUEGO_SALE", 0.022)), frente_rt, CP, escala=float(os.environ.get("FUEGO", 1.7)))
for o in rt["ojos"]:
    ow = o.matrix_world.translation
    abajo = (rt["cabeza"].matrix_world.to_3x3() @ Vector((0, -0.3, -1))).normalized()
    V.lagrimas(o.name + "_lagr", ow + abajo * 0.010, abajo, CP, largo=0.028, seed=1)

import random as _r
_rr = _r.Random(3)
pied = P.mat("Piedrita", (0.55, 0.30, 0.16), rough=0.8)
for k in range(40):
    pz = P.prim("ico", f"Piedrita{k}", C, pied, r=_rr.uniform(0.002, 0.007), sub=2)
    pz.scale = (1, _rr.uniform(0.7, 1.3), _rr.uniform(0.5, 0.8))
    x, y = _rr.uniform(-0.30, 0.30), _rr.uniform(-0.55, 0.05)
    if abs(x) < 0.06 and -0.22 < y < -0.10:
        continue
    _dg = bpy.context.evaluated_depsgraph_get()
    _rp = bpy.data.objects["RocaPrincipal"]
    _Mi = _rp.matrix_world.inverted()
    _hit, _loc, *_ = _rp.evaluated_get(_dg).ray_cast(_Mi @ Vector((x, y, 2.0)), (_Mi.to_3x3() @ Vector((0, 0, -1))).normalized())
    _z = (_rp.matrix_world @ _loc).z if _hit else TOP
    pz.location = (x, y, _z + pz.scale.z * 0.0045 * 0.75 - 0.0005)
# --- cámara ---
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.sensor_fit = "VERTICAL"
cam.data.sensor_height = 24
cam.data.lens = float(os.environ.get("LENS", 28))
bpy.context.view_layer.update()
foco = pj["cabeza"].matrix_world.translation + Vector((0, -0.03, 0.02))
cam.location = foco + Vector(tuple(float(x) for x in os.environ.get("CAMOFF", "-0.02,-0.66,-0.05").split(",")))
mira = foco + Vector(tuple(float(x) for x in os.environ.get("MIRA", "0.075,0.10,-0.01").split(",")))
cam.rotation_euler = (mira - cam.location).to_track_quat("-Z", "Y").to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = (foco - cam.location).length
cam.data.dof.aperture_fstop = float(os.environ.get("FSTOP", 9.0))

from bpy_extras.object_utils import world_to_camera_view as _w2c
bpy.context.view_layer.update()
def _pant(nombre, punto=None):
    o = bpy.data.objects.get(nombre)
    w = punto if punto is not None else o.matrix_world.translation
    v = _w2c(sc, cam, w)
    return round(v.x * 1080), round((1 - v.y) * 1920)
for _n in ("AjiMordido", "LentesCaidos", "MedallaCaida", "Cuitlacoche_piv_cabeza", "Raton_piv_cabeza", "AjiCuadro0"):
    if bpy.data.objects.get(_n):
        print("pantalla", _n, _pant(_n))
if os.environ.get("SOLO_POS"):
    raise SystemExit
sc.render.filepath = os.path.join(OUT, os.environ.get("NOMBRE", "estilo_desierto_cuadro0") + ".png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath)
