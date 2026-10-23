"""Ficha de personajes de Rhein 01 (la usa el auditor): el niño pescador (cuerpo y cara) y el mosasaurio.
QUE=nino|cara|mosa RES=540x960 SAMPLES=16 OUT=... python3 ficha.py"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
from mathutils import Vector
import rhein01 as E
import mar as M
import nino as N
import pj_rhein as PJ

que = os.environ.get("QUE", "nino")
w, h = (int(v) for v in os.environ.get("RES", "540x960").split("x"))
sc = E.escena("Ficha")
sc.render.resolution_x, sc.render.resolution_y = w, h
sc.cycles.samples = int(os.environ.get("SAMPLES", 16))
M.cielo(sc, sol_energia=3.0)
E.area(sc, "Key", (-1.8, -2.6, 2.6), 300, 1.8, (1, 0.96, 0.9), (0, 0, 0.8))
E.area(sc, "Fill", (2.0, -1.8, 1.4), 120, 2.0, (0.85, 0.92, 1.0), (0, 0, 0.9))
cam = E.camara(sc, lens=40)
if que in ("nino", "cara"):
    pj = N.cargar(sc)
    N.pose(pj, 1, expr={"sonrisa": 1}, brazoR=N.brazo("pulgar"), cabeza=(0, 0, 6))
    if que == "nino":
        E.mirar(cam, (0.8, -3.3, 0.95), (0, 0, 0.70), lens=40)
    else:
        bpy.context.view_layer.update()
        H = pj["rig"].matrix_world @ pj["pb"]["mixamorig:Head"].head + Vector((0, 0, 0.07))
        E.mirar(cam, H + Vector((-0.25, -0.95, 0.02)), H, lens=60)
else:
    mosa = PJ.mosasaurio(sc.collection)
    mosa.location = (0, 0, 2.0)
    mosa.rotation_euler = (math.radians(-6), 0, math.radians(120))
    bpy.data.objects["Mosa_mandibula"].rotation_euler = (math.radians(30), 0, 0)
    E.mirar(cam, (9.0, 7.2, 3.1), (3.2, 1.9, 2.0), lens=30)
out = os.environ.get("OUT", os.path.join(HERE, "out"))
os.makedirs(out, exist_ok=True)
sc.render.filepath = os.path.join(out, f"ficha_{que}.png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath)
