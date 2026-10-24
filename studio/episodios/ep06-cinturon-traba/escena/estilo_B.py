"""Cuadro de estilo B (Ep. 6, E3): el plano 19 tal como sale en el video (misma escena y cámara de planos_ep06), en HD:
el 4x4 subiendo la ladera de 30° al atardecer, con el llano de abajo como referencia.
Uso: RES=1080x1920 SAMPLES=64 OUT=carpeta ASSETS=carpeta [CUADRO=800] [PIEZA=19@1] python3 estilo_B.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bpy
import ep06 as E
import planos_ep06 as PL

w, h = (int(v) for v in os.environ.get("RES", "1080x1920").split("x"))
out = os.environ.get("OUT", os.path.join(HERE, "out")); os.makedirs(out, exist_ok=True)
sc = E.escena("EstiloA", (w, h), int(os.environ.get("SAMPLES", 64)))
sc.render.fps = 30
pid = os.environ.get("PIEZA", "19@1")
pz = PL.PIEZAS[pid]
res = pz["fn"](sc, pz["a"], pz["b"])
cuadro = int(os.environ.get("CUADRO", 800))
sc.frame_set(cuadro)
res["actualizar"](cuadro)
sc.render.resolution_x, sc.render.resolution_y = w, h
reg = [f"{q}: {'ok' if E.tiene_esqueleto(o) else 'sin esqueleto'}" for q in ("caballero", "piloto", "mascara", "doctor")
       for o in [bpy.data.objects.get(q)] if o is not None]
open(os.path.join(out, "B_registro.txt"), "w").write("\n".join(reg) + "\n")
sc.render.filepath = os.path.join(out, os.environ.get("NOMBRE", "estilo_B_HD") + ".png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath, reg)
