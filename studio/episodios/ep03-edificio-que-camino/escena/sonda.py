"""Sonda de encuadre: para cada plano, dónde cae el edificio (caja en pantalla 1080x1920) en el cuadro inicial, medio y final."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.abspath(os.path.join(HERE, "../../../plantilla"))]
import bpy
from mathutils import Vector
import ep03 as E, planos_ep03 as PL
for k in [int(x) for x in sys.argv[1].split(",")]:
    pz = PL.PIEZAS[str(k)]
    sc = E.escena(f"s{k}")
    res = pz["fn"](sc, pz["a"], pz["b"])
    out = []
    for f in (pz["a"], (pz["a"] + pz["b"]) // 2, pz["b"] - 1):
        res["actualizar"](f)
        bpy.context.view_layer.update()
        ed = bpy.data.objects.get("Edificio")
        if ed is None or ed.hide_render:
            out.append("sin edificio"); continue
        M = ed.matrix_world
        pts = [E.pantalla(sc, sc.camera, M @ Vector((x, y, z))) for x in (-22, 22) for y in (-6, 28) for z in (0.0, 20.5)]
        pies = [E.pantalla(sc, sc.camera, M @ Vector((x, -6, -3.0))) for x in (-22, 0, 22)]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        out.append(f"x {min(xs)}..{max(xs)} y {min(ys)}..{max(ys)} pies_y {[p[1] for p in pies]}")
    print(f"P{k}:", " | ".join(out), flush=True)
