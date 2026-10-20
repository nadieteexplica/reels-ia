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
import bmesh
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

import set_c0
globals().update(set_c0.armar(sc))

from bpy_extras.object_utils import world_to_camera_view as _w2c
bpy.context.view_layer.update()
def _pant(nombre, punto=None):
    w = punto if punto is not None else bpy.data.objects.get(nombre).matrix_world.translation
    v = _w2c(sc, cam, w)
    return round(v.x * 1080), round((1 - v.y) * 1920)
for _n in ("AjiMordido", "LentesCaidos", "MedallaCaida", "Cuitlacoche_piv_cabeza", "Raton_piv_cabeza", "AjiCuadro0"):
    if bpy.data.objects.get(_n):
        print("pantalla", _n, _pant(_n))
for _x in [float(t) for t in os.environ.get("PERFIL", "").split(",") if t]:
    print("perfil x", _x, [(round(_y, 2), round(cima(_x, _y), 3)) for _y in [i * 0.02 for i in range(-2, 16)]])
print("camara", tuple(round(c, 3) for c in cam.location))
for _p in [p_ for p_ in os.environ.get("PROBE", "").split(";") if p_]:
    print("probe", _p, "->", _pant(None, Vector(tuple(float(t) for t in _p.split(",")))))
if os.environ.get("RAYO_PIX"):
    # qué objeto se ve en cada píxel (coordenadas de 1080x1920): "x,y;x,y"
    _dg = bpy.context.evaluated_depsgraph_get()
    _fr = [cam.matrix_world @ v for v in cam.data.view_frame(scene=sc)]   # sup-der, inf-der, inf-izq, sup-izq
    for _p in os.environ["RAYO_PIX"].split(";"):
        _u, _v = (float(t) for t in _p.split(","))
        _u, _v = _u / 1080, _v / 1920
        _top = _fr[3].lerp(_fr[0], _u)
        _bot = _fr[2].lerp(_fr[1], _u)
        _q = _top.lerp(_bot, _v)
        _d = (_q - cam.location).normalized()
        _hit, _loc, _n, _i, _ob, _m = sc.ray_cast(_dg, cam.location, _d)
        print("pixel", _p, "->", _ob.name if _hit else None, tuple(round(c, 3) for c in _loc) if _hit else "")
if os.environ.get("SOLO_POS"):
    raise SystemExit
sc.render.filepath = os.path.join(OUT, os.environ.get("NOMBRE", "estilo_desierto_cuadro0") + ".png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath)
