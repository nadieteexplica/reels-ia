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
sc.view_settings.exposure = env("EXPO", 0.3)
auto = None
if os.environ.get("CON_AUTO") == "1" and os.path.exists(os.path.join(E.K.ASSETS, E.AUTO_GLB)):
    auto = E.auto(sc)
# el mismo set que usan los planos de E2 (ep06.set_retractor): mecanismo, chapa del pilar angosta, cinta, luces, desierto
ret, RET = E.set_retractor(sc, giro=env("GIRO", 25), pestillo=env("PESTILLO", 0.0), bolita=env("BOLITA", 0.35),
                           palanca=env("PALANCA", 0.0), key=env("KEY", 2.5), rebote=env("REBOTE", 6.0))
# cámara macro desde adentro del auto, mirando al pilar en diagonal
pos = RET + Vector((env("CAM_DX", 0.62), env("CAM_DY", -0.42), env("CAM_Z", 0.02)))
E.camara(sc, pos, RET + Vector((0, 0, env("MIRA_DZ", -0.005))), lente=env("LENTE", 100), fstop=env("FSTOP", 5.6))
sc.render.filepath = os.path.join(out, os.environ.get("NOMBRE", "estilo_C_HD") + ".png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath)
