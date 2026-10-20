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
import set_bosque
globals().update(set_bosque.armar(sc))

if os.environ.get("RAYO_PIX"):
    # qué objeto se ve en cada píxel (coordenadas de 1080x1920): "x,y;x,y"
    bpy.context.view_layer.update()
    _dg2 = bpy.context.evaluated_depsgraph_get()
    _fr = [cam.matrix_world @ v for v in cam.data.view_frame(scene=sc)]
    for _p in os.environ["RAYO_PIX"].split(";"):
        _u, _v = (float(t) for t in _p.split(","))
        _q = _fr[3].lerp(_fr[0], _u / 1080).lerp(_fr[2].lerp(_fr[1], _u / 1080), _v / 1920)
        _o, _d = cam.location.copy(), (_q - cam.location).normalized()
        for _k in range(8):                                   # atraviesa la caja de niebla y el gobo
            _hit, _loc, _n, _i, _ob, _m = sc.ray_cast(_dg2, _o, _d)
            if not _hit or not (_ob.name.startswith("CajaNiebla") or _ob.name.startswith("Copa")):
                break
            _o = _loc + _d * 1e-4
        print("pixel", _p, "->", _ob.name if _hit else None, [m.name for m in _ob.data.materials] if _hit and _ob.type == "MESH" else "")
    if os.environ.get("SOLO_POS"):
        raise SystemExit
sc.render.filepath = os.path.join(OUT, os.environ.get("NOMBRE", "estilo_bosque") + ".png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath)
