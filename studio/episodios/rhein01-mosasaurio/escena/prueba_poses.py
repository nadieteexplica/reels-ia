"""Prueba de poses del niño (calibra los ejes de los huesos). POSE=n RES=... OUT=... python3 prueba_poses.py"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
from mathutils import Vector
import rhein01 as E
import nino as N

POSES = [
    dict(nombre="abajo", expr={"sonrisa": 1}),
    dict(nombre="apunta", brazoR=N.brazo("apunta"), expr={"picaro": 1}, cabeza=(0, 0, -10)),
    dict(nombre="arriba", brazoL=N.brazo("arriba"), brazoR=N.brazo("arriba"), expr={"grito": 1}),
    dict(nombre="sentado", sentado=1.0, brazoL=N.brazo("agarra"), brazoR=N.brazo("agarra"), expr={"susto": 1}),
    dict(nombre="jarra", brazoL=N.brazo("jarra"), brazoR=N.brazo("senal"), expr={"orgullo": 1}),
    dict(nombre="pulgar", brazoR=N.brazo("pulgar"), expr={"sonrisa": 1}, cabeza=(0, 0, 8)),
]
i = int(os.environ.get("POSE", "0"))
p = dict(POSES[i])
nombre = p.pop("nombre")
w, h = (int(v) for v in os.environ.get("RES", "270x480").split("x"))
sc = E.escena("Poses")
sc.render.resolution_x, sc.render.resolution_y = w, h
sc.cycles.samples = int(os.environ.get("SAMPLES", 10))
import mar as M
M.cielo(sc, sol_energia=2.5)
E.area(sc, "Key", (-1.5, -2.5, 2.4), 260, 1.6, (1, 0.96, 0.9), (0, 0, 0.8))
E.area(sc, "Fill", (2.0, -1.5, 1.2), 90, 2.0, (0.85, 0.92, 1.0), (0, 0, 0.8))
pj = N.cargar(sc, z=0.0)
N.pose(pj, 1, **p)
cam = E.camara(sc, lens=40)
E.mirar(cam, (0.9, -3.2, 1.0), (0, 0, 0.72))
out = os.environ.get("OUT", os.path.join(HERE, "out"))
os.makedirs(out, exist_ok=True)
sc.render.filepath = os.path.join(out, f"pose_{i}_{nombre}.png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath)
