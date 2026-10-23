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
SOL_ROT = float(os.environ.get("SOL_ROT", 170))
E.cielo_atardecer(sc, elev=2.5, rot=SOL_ROT, fuerza=0.35, sol=3.5)
E.salar(sc)
E.cerros(sc)
E.plataforma(sc)
Z0 = 0.08
piezas = E.iman_lab(sc, alto=1.25, r=0.42, r_hueco=0.017)
for p in piezas:
    p.location.z += Z0
BOCA = Z0 + 1.25 + 0.025
tubo = E.tubo(sc, "Tubo_acrilico", 0.0158, 0.0148, 0.11, (0, 0, BOCA - 0.01), verts=96, mat=E.mat_acrilico(), bisel=0.0004)
rana = E.rana(sc, 0.028)
rana.location = (0, 0, BOCA + 0.045)
rana.rotation_euler = (math.radians(6), math.radians(-6), math.radians(48))
bpy.context.view_layer.update()
E.gotitas(sc, rana, 10, (0.00015, 0.0003))
objetivo = rana.location.copy()
pos = Vector((0.035, -0.36, BOCA + 0.05))
# relleno suave desde el lado de la cámara (como un rebotador) para que se lea la cara con el sol detrás
E.luz_area(sc, "Rebote", (-0.25, -0.35, BOCA + 0.15), objetivo, 1.6, (1.0, 0.9, 0.82), 0.3)
E.camara(sc, pos, objetivo + Vector((0, 0, -0.008)), lente=100, fstop=5.6, foco=(objetivo - pos).length)
sc.render.filepath = os.path.join(out, os.environ.get("NOMBRE", "estilo_A_HD") + ".png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath)
