"""Cuadro de estilo C (Ep. 6, E2): el retractor por dentro, a escala real (~8 cm), en el pilar del copiloto con el plástico
vuelto transparente (capa de explicación encima del mundo real). Carrete con la cinta, rueda dentada, anillo dentado con el
pestillo, y abajo la tacita con la bolita de acero y la palanquita. Luz cálida de costado (el sol que entra por la ventana del
copiloto, a la izquierda del cuadro) + un rebote frío; atrás, el interior del auto desenfocado.
Uso: RES=1080x1920 SAMPLES=64 OUT=carpeta ASSETS=carpeta python3 estilo_C.py"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bpy
from mathutils import Vector
import ep06 as E

env = lambda k, d: float(os.environ.get(k, d))
w, h = (int(v) for v in os.environ.get("RES", "1080x1920").split("x"))
out = os.environ.get("OUT", os.path.join(HERE, "out")); os.makedirs(out, exist_ok=True)
sc = E.escena("EstiloC", (w, h), int(os.environ.get("SAMPLES", 64)))
E.sol(sc, fuerza_cielo=env("CIELO", 0.15), sol=env("SOL", 3.0))
sc.view_settings.exposure = env("EXPO", -0.2)
auto = None
if os.environ.get("CON_AUTO") == "1" and os.path.exists(os.path.join(E.K.ASSETS, E.AUTO_GLB)):
    auto = E.auto(sc)
E.desierto(sc)
# el retractor en el pilar del copiloto, a la altura del asiento
RET = Vector(E.RETRACTOR)
ret = E.retractor(sc, tuple(RET), giro_carrete=env("GIRO", 25), pestillo=env("PESTILLO", 0.0), bolita=env("BOLITA", 0.35), palanca=env("PALANCA", 0.0))
ret.rotation_euler = (0, 0, math.radians(env("RET_GIRO", 0)))
# adentro del pilar: la chapa de la carrocería detrás (primer gris con óxido en los bordes) y el borde del plástico cortado
E.caja(sc, "ChapaPilar", (0.004, 0.32, 0.5), tuple(RET + Vector((-0.06, 0.0, 0.08))), mat=E.K.mat_acero_industrial("chapa_pilar", (0.2, 0.21, 0.22), sucio=0.6), bisel=0.002)
E.caja(sc, "ChapaPilar2", (0.12, 0.004, 0.5), tuple(RET + Vector((0.0, 0.12, 0.08))), mat=E.K.mat_acero_industrial("chapa_pilar2", (0.2, 0.21, 0.22), sucio=0.6), bisel=0.002)
# carcasa de plástico del pilar alrededor, casi transparente
car = E.caja(sc, "CarcasaPilar", (0.11, 0.06, 0.15), tuple(RET + Vector((0.01, 0, 0.01))), mat=E.mat_plastico_pilar(alfa=env("ALFA", 0.05)), bisel=0.006)
# la cinta que sube desde el carrete hacia la guía del hombro
E.cinta(sc, [RET + Vector((0.0, -0.017, 0.012)), RET + Vector((0.0, -0.022, 0.08)), RET + Vector((0.0, -0.02, 0.5)), Vector(E.PILAR_GUIA["caballero"])],
        [Vector((1, 0, 0))] * 4, nombre="CintaSube")
# luz: el sol entra por la ventana del copiloto (izquierda del cuadro) + rebote frío suave del otro lado
E.luz_area(sc, "SolVentana", tuple(RET + Vector((-0.5, -0.35, 0.25))), tuple(RET), env("KEY", 18.0), (1.0, 0.72, 0.5), 0.25, spread=40)
E.luz_area(sc, "Rebote", tuple(RET + Vector((0.4, 0.3, 0.1))), tuple(RET), env("FILL", 0.6), (0.6, 0.75, 1.0), 0.4)
# cámara macro desde adentro del auto, mirando al pilar en diagonal
pos = RET + Vector((env("CAM_DX", 0.62), env("CAM_DY", -0.42), env("CAM_Z", 0.14)))
E.camara(sc, pos, RET + Vector((0, 0, env("MIRA_DZ", -0.005))), lente=env("LENTE", 100), fstop=env("FSTOP", 8.0))
sc.render.filepath = os.path.join(out, os.environ.get("NOMBRE", "estilo_C_HD") + ".png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath)
