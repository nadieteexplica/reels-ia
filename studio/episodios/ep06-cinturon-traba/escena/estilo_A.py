"""Cuadro de estilo A (Ep. 6, E1): el plano 1 tal como sale en el video (misma escena y cámara de planos_ep06), en HD:
el caballero lanzado por la bolsa del tablero, con la cinta roja tensa, y atrás los otros tres.
Uso: RES=1080x1920 SAMPLES=64 OUT=carpeta ASSETS=carpeta [CUADRO=16] [PIEZA=1] python3 estilo_A.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bpy
import ep06 as E
import planos_ep06 as PL

w, h = (int(v) for v in os.environ.get("RES", "1080x1920").split("x"))
out = os.environ.get("OUT", os.path.join(HERE, "out")); os.makedirs(out, exist_ok=True)
sc = E.escena("EstiloA", (w, h), int(os.environ.get("SAMPLES", 64)))
sc.render.fps = 30
pid = os.environ.get("PIEZA", "1")
pz = PL.PIEZAS[pid]
res = pz["fn"](sc, pz["a"], pz["b"])
cuadro = int(os.environ.get("CUADRO", 16))
sc.frame_set(cuadro)
res["actualizar"](cuadro)
sc.render.resolution_x, sc.render.resolution_y = w, h
reg = [f"{q}: {'ok' if E.tiene_esqueleto(o) else 'sin esqueleto'}" for q in ("caballero", "piloto", "mascara", "doctor")
       for o in [bpy.data.objects.get(q)] if o is not None]
# diagnóstico (los personajes sólo existen en Actions): dónde quedó cada hueso clave, en coordenadas del auto
from mathutils import Vector
inv = E.MARCO.inverted()
for q in ("caballero", "piloto", "mascara", "doctor"):
    o = bpy.data.objects.get(q)
    if o is None or not E.tiene_esqueleto(o):
        continue
    pos = {n: tuple(round(v, 2) for v in inv @ E.pos_hueso(o, n)) for n in ("Hips", "Spine2", "Head", "HeadTop_End", "LeftHand", "RightHand", "LeftFoot")
           if E.hueso(o, n) is not None}
    reg.append(f"{q} escala={tuple(round(v, 4) for v in o.scale)} rot={tuple(round(v, 2) for v in o.rotation_euler)} {pos}")
    mallas = [m for m in bpy.data.objects if m.type == "MESH" and m.get("personaje") == q]
    if mallas:
        import numpy as np
        dg = bpy.context.evaluated_depsgraph_get()
        pts = []
        for m in mallas:
            me = m.evaluated_get(dg).to_mesh()
            vs = list(me.vertices); pts += [tuple(inv @ (m.matrix_world @ v.co)) for v in vs[::50]]
            m.evaluated_get(dg).to_mesh_clear()
        P = np.array(pts)
        reg.append(f"  malla {q}: min {tuple(np.round(P.min(0), 2))} max {tuple(np.round(P.max(0), 2))} n={len(P)}")
open(os.path.join(out, "A_registro.txt"), "w").write("\n".join(reg) + "\n")
sc.render.filepath = os.path.join(out, os.environ.get("NOMBRE", "estilo_A_HD") + ".png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath, reg)
