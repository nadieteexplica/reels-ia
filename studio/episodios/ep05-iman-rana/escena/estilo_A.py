"""Cuadro de estilo A (Ep. 5) — exterior: la rana (tamaño real, ~2,8 cm) flota dentro del tubo transparente en la boca del
imán, que está sobre una losa en medio del salar al atardecer. Es también el cuadro 0 del video.
Uso: RES=1080x1920 SAMPLES=64 OUT=carpeta ASSETS=carpeta python3 estilo_A.py"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bpy
from mathutils import Vector
import ep05 as E

w, h = (int(v) for v in os.environ.get("RES", "1080x1920").split("x"))
out = os.environ.get("OUT", os.path.join(HERE, "out")); os.makedirs(out, exist_ok=True)
sc = E.escena("EstiloA", (w, h), int(os.environ.get("SAMPLES", 64)))
SOL_ROT = float(os.environ.get("SOL_ROT", 10))
E.cielo_atardecer(sc, elev=2.5, rot=SOL_ROT, fuerza=0.35, sol=3.5)
E.salar(sc)
E.cerros(sc)
E.plataforma(sc)
Z0 = 0.08
piezas = E.iman_lab(sc, alto=1.25, r=0.42, r_hueco=0.017)
for p in piezas:
    p.location.z += Z0
BOCA = Z0 + 1.25 + 0.025
rana = E.rana(sc, 0.022)
rana.location = (0, 0, BOCA + 0.045)
rana.rotation_euler = (math.radians(6), math.radians(-6), math.radians(float(os.environ.get("RANA_GIRO", 78))))   # 3/4 hacia cámara: se ve un ojo
bpy.context.view_layer.update()
E.gotitas(sc, rana, 10, (0.00012, 0.00025))          # antes del tubo (si no, las gotitas quedan pegadas al vidrio)
tubo = E.tubo(sc, "Tubo_acrilico", 0.0158, 0.0148, 0.11, (0, 0, BOCA - 0.01), verts=96, mat=E.mat_acrilico(), bisel=0.0004)
objetivo = rana.location.copy()
DIST = float(os.environ.get("DIST", 0.22))
pos = Vector((0.035 * DIST / 0.36, -DIST, BOCA + 0.05))
# relleno suave desde el lado de la cámara (como un rebotador) para que se lea la cara con el sol detrás
E.luz_area(sc, "Rebote", (-0.22, -0.32, BOCA + 0.12), objetivo, 3.5, (1.0, 0.88, 0.78), 0.3)
foco = objetivo + Vector((float(os.environ.get("FOCO_X", -0.008)), -0.004, 0.002))      # foco en la cabeza (el ojo), no en el centro
E.camara(sc, pos, objetivo + Vector((0, 0, -0.008)), lente=100, fstop=float(os.environ.get("FSTOP", 8)), foco=(foco - pos).length)
sc.render.filepath = os.path.join(out, os.environ.get("NOMBRE", "estilo_A_HD") + ".png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath)
