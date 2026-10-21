import os, sys, time, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.abspath(os.path.join(HERE, "../../../plantilla"))]
import bpy
import ep03 as E
import edificio as ED, calle as C
t0 = time.time()
sc = E.escena("prueba")
C.armar(sc)
C.cielo(sc)
ed = ED.Edificio(sc)
d = float(os.environ.get("DIST", "0.9"))
ed.poner(d, ED.recta(0, 0, 0))
cam = E.camara(sc, lens=float(os.environ.get("LENS", "24")))
pos = tuple(float(v) for v in os.environ.get("POS", "-34,-46,2.2").split(","))
tgt = tuple(float(v) for v in os.environ.get("TGT", "-4,0,9").split(","))
E.mirar(cam, pos, tgt)
cam.data.shift_y = float(os.environ.get("SHIFT", "0"))
w, h = (int(v) for v in os.environ.get("RES", "360x640").split("x"))
sc.render.resolution_x, sc.render.resolution_y = w, h
sc.cycles.samples = int(os.environ.get("SAMPLES", "16"))
sc.render.filepath = os.environ.get("OUT", "/tmp/claude-0/set.png")
bpy.context.view_layer.update()
for nom, pt in (("base", (-3, -6, 3.0)), ("pie", (-3, -6, 0.0)), ("techo", (-3, -6, 22.6)), ("esq_izq", (-22, -6, 12)), ("esq_der", (22, -6, 12))):
    print("PROBE", nom, E.pantalla(sc, cam, (pt[0] + d, pt[1], pt[2])))
print("armado", round(time.time() - t0, 1), "s", len(bpy.data.objects), "objetos")
if not os.environ.get("SOLO_PROBE"): bpy.ops.render.render(write_still=True)
print("render", round(time.time() - t0, 1), "s")
