"""Cuadro de estilo A (Ep. 5): la rana flotando sobre la boca del imán del laboratorio. Es también el cuadro 0 del video.
Uso: RES=1080x1920 SAMPLES=64 OUT=carpeta ASSETS=carpeta python3 estilo_A.py"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bpy
from mathutils import Vector
import ep05 as E

w, h = (int(v) for v in os.environ.get("RES", "1080x1920").split("x"))
out = os.environ.get("OUT", os.path.join(HERE, "out")); os.makedirs(out, exist_ok=True)
sc = E.escena("EstiloA", (w, h), int(os.environ.get("SAMPLES", 64)))
E.mundo(sc, "machine.hdr", 0.08, rot=40)
E.laboratorio(sc, pared=(0.16, 0.27, 0.30))
E.iman_lab(sc)
R = 1.25 + 0.025                      # boca del hueco
rana = E.rana(sc, 0.085)
rana.location = (0, 0, R + 0.075)
rana.rotation_euler = (math.radians(-8), math.radians(-14), math.radians(-38))
bpy.context.view_layer.update()
E.gotitas(sc, rana, 14, (0.0004, 0.0009))
# luz: principal cálida y grande arriba a la izquierda (sombra suave de la rana sobre la tapa: se ve que flota),
# contraluz frío atrás a la derecha (brillo de piel mojada en el borde), relleno tenue
E.luz_area(sc, "Principal", (-0.75, -0.55, 1.75), (0, 0, R + 0.075), 160, (1.0, 0.84, 0.68), 0.45, spread=40)
E.luz_area(sc, "Contra", (0.5, 0.7, 1.5), (0, 0, R + 0.07), 70, (0.55, 0.78, 1.0), 0.25, spread=40)
E.luz_area(sc, "Relleno", (0.4, -1.4, 1.1), (0, 0, R + 0.07), 5, (0.8, 0.9, 1.0), 1.5)
objetivo = Vector((0.0, 0.0, R + 0.055))
pos = Vector((0.08, -0.40, R + 0.075))
E.camara(sc, pos, objetivo, lente=42, fstop=2.0, foco=(rana.location - pos).length)
sc.render.filepath = os.path.join(out, os.environ.get("NOMBRE", "estilo_A_HD") + ".png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath)
