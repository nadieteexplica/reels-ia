"""Cuadro de estilo B (Ep. 6, E3): el 4x4 trepando el cerro de roca a 30°, de 3/4 trasero desde el lado del copiloto
(el iluminado y el del precipicio). Sol bajo (3,5°) de costado a la derecha del cuadro; los cerros con neblina detrás.
Uso: RES=1080x1920 SAMPLES=64 OUT=carpeta ASSETS=carpeta python3 estilo_B.py"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bpy
from mathutils import Vector
import ep06 as E

env = lambda k, d: float(os.environ.get(k, d))
w, h = (int(v) for v in os.environ.get("RES", "1080x1920").split("x"))
out = os.environ.get("OUT", os.path.join(HERE, "out")); os.makedirs(out, exist_ok=True)
sc = E.escena("EstiloB", (w, h), int(os.environ.get("SAMPLES", 64)))
E.sol(sc, fuerza_cielo=env("CIELO", 0.2), sol=env("SOL", 4.0), az=env("SOL_AZ", E.SOL_AZ_CERRO), elev=env("SOL_ELEV", 4.0))
sc.view_settings.exposure = env("EXPO", -0.4)
E.desierto(sc)
E.cerros(sc)
PEND = env("PEND", 30)
zc = E.cerro_roca(sc, pendiente=PEND, origen=(0, -2.0, 0))
auto = E.auto(sc)
y0 = env("Y_AUTO", -9.0)
E.poner_auto(auto, PEND, y_contacto=y0, z_contacto=zc(y0))
centro = Vector((0, y0 - 1.2, zc(y0) + 1.6))
az = math.radians(env("CAM_AZ", 225))        # desde el centro del auto: 225° = atrás (+y) y al lado del copiloto (−x)
d = env("CAM_D", 14.0)
pos = centro + Vector((math.sin(az) * d, -math.cos(az) * d, env("CAM_Z", -1.0)))
E.camara(sc, pos, centro + Vector((0, 0, env("MIRA_DZ", 1.6))), lente=env("LENTE", 45), fstop=env("FSTOP", 8.0))
sc.render.filepath = os.path.join(out, os.environ.get("NOMBRE", "estilo_B_HD") + ".png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath, "cam", tuple(round(v, 2) for v in pos))
