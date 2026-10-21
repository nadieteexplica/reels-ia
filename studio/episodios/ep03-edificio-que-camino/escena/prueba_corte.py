import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.abspath(os.path.join(HERE, "../../../plantilla"))]
import bpy
import ep03 as E, edificio as ED, calle as C, corte as K
sc = E.escena("corte")
C.cielo(sc)
for o in list(bpy.data.objects):
    pass
import calle
S = calle.armar(sc)
for nom in ("SueloObra",):
    bpy.data.objects[nom].hide_render = True
K_ = K.Corte(sc)
ph = [float(v) for v in os.environ.get("FASES", "1,0.6,0.5,0").split(",")]
K_.poner(1, *ph)
cam = E.camara(sc, lens=float(os.environ.get("LENS", "20")))
E.mirar(cam, tuple(float(v) for v in os.environ.get("POS", "-8,-34,-1.0").split(",")), tuple(float(v) for v in os.environ.get("TGT", "-2,0,0.5").split(",")))
w, h = (int(v) for v in os.environ.get("RES", "540x960").split("x"))
sc.render.resolution_x, sc.render.resolution_y = w, h
sc.cycles.samples = int(os.environ.get("SAMPLES", "16"))
sc.render.filepath = os.environ.get("OUT", "/tmp/claude-0/corte.png")
bpy.context.view_layer.update()
print("PROBE base", E.pantalla(sc, cam, (-2, -6, 0)), "foso", E.pantalla(sc, cam, (-2, -7.2, -3.6)))
t0 = time.time(); bpy.ops.render.render(write_still=True); print("render", round(time.time() - t0, 1))
