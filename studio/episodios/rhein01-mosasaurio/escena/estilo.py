"""Cuadros de estilo de Rhein 01 (puerta 4): A gancho (racimo de pollos y sombra), B el niño, C el mosasaurio saltando.
Uso: CUADRO=A RES=540x960 SAMPLES=24 OUT=carpeta python3 estilo.py
"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
from mathutils import Vector, Euler
import rhein01 as E
import mar as M
import pj_rhein as PJ

cual = os.environ.get("CUADRO", "A")
w, h = (int(v) for v in os.environ.get("RES", "540x960").split("x"))
out = os.environ.get("OUT", os.path.join(HERE, "out", "estilo"))
os.makedirs(out, exist_ok=True)

sc = E.escena("Estilo" + cual)
sc.render.resolution_x, sc.render.resolution_y = w, h
sc.cycles.samples = int(os.environ.get("SAMPLES", 24))
coll = sc.collection
M.cielo(sc)
mar = M.mar(coll)
M.olas_t(mar, 2.0)
M.nubes(coll)
bote = M.bote(coll)
grua, tip = M.grua(coll, base=(0, 1.15, 0.30))
grua.parent = bote
rac, pollos = M.racimo(coll, tip + Vector((0, 0, -2.2)), n=60)
M.cable(coll, tip, tip + Vector((0, 0, -2.15)))
nino = PJ.nino(coll)
mosa = PJ.mosasaurio(coll)
cam = E.camara(sc, lens=30)

if cual == "A":
    # gancho: el racimo sobre el mar, la sombra gigante pasando por debajo
    nino.location = (0.25, -0.2, -0.20)
    nino.rotation_euler = (0, 0, math.radians(160))
    PJ.pose_nino(nino, cabeza=(-25, 0, 0), brazoL=(0, 0, 0), brazoR=(-150, 0, -10), boca=0.5, cejas=1)
    mosa.location = tip + Vector((1.0, 0.5, -3.6))
    mosa.location.z = -2.4
    mosa.rotation_euler = (0, 0, math.radians(-35))
    E.mirar(cam, tip + Vector((7.5, 9.5, 2.0)), tip + Vector((0, 0, -4.0)), lens=24)
elif cual in ("M", "M2"):
    nino.location = (0, 0, -0.2)
    mosa.location = (12, -10, 3.0)
    mosa.rotation_euler = (0, 0, math.radians(90 if cual == "M" else 140))
    bpy.data.objects["Mosa_mandibula"].rotation_euler = (math.radians(32), 0, 0)
    E.mirar(cam, (12 + (0 if cual == "M" else -9), -10 - (17 if cual == "M" else 12), 4.0), (12, -10, 2.6), lens=28 if cual == "M" else 35)
elif cual == "M3":
    nino.location = (0, 0, -0.2)
    mosa.location = (12, -10, 3.0)
    mosa.rotation_euler = (math.radians(-8), 0, math.radians(90))
    bpy.data.objects["Mosa_mandibula"].rotation_euler = (math.radians(34), 0, 0)
    E.mirar(cam, (22.5, -16.5, 4.6), (16.0, -10, 3.2), lens=32)
elif cual == "B2":
    nino.location = (0, -0.3, -0.20)
    nino.rotation_euler = (0, 0, math.radians(-20))
    PJ.pose_nino(nino, cabeza=(-5, 0, -8), brazoL=(0, 0, 25), brazoR=(-60, 0, -20), boca=0.35, cejas=0.6)
    mosa.location = (0, -60, -6)
    E.mirar(cam, (-0.45, -1.55, 0.95), (0, -0.3, 0.82), lens=50)
elif cual == "B":
    nino.location = (0, -0.3, -0.20)
    nino.rotation_euler = (0, 0, math.radians(-20))
    PJ.pose_nino(nino, cabeza=(-8, 0, -10), brazoL=(0, 0, 25), brazoR=(-60, 0, -20), boca=0.25, cejas=0.4)
    mosa.location = (0, -60, -6)
    E.mirar(cam, (-1.1, -2.4, 1.15), (0, -0.3, 0.80), lens=40)
else:
    nino.location = (0.25, -0.2, -0.20)
    nino.rotation_euler = (0, 0, math.radians(180))
    PJ.pose_nino(nino, cabeza=(-30, 0, 0), brazoL=(-170, 0, 20), brazoR=(-170, 0, -20), boca=1.0, cejas=1)
    mosa.location = tip + Vector((0.0, 1.5, -6.8))
    mosa.rotation_euler = (math.radians(-62), 0, math.radians(180))
    bpy.data.objects["Mosa_mandibula"].rotation_euler = (math.radians(38), 0, 0)
    E.mirar(cam, tip + Vector((9.0, -9.0, -1.2)), tip + Vector((0, 0, -3.0)), lens=24)

PJ.Ondula(mosa).aplicar(0.4, amp=0.35)
sc.render.filepath = os.path.join(out, f"estilo_{cual}.png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath)
