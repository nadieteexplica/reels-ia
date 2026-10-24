"""Cuadro de estilo A (Ep. 6, E1, plano 1 = cuadro 0): dentro del 4x4 detenido en el camino de tierra, desde el tablero
mirando hacia atrás. El caballero (copiloto) ya va lanzado hacia la bolsa de papas del centro del tablero, con la cinta recta y
tensa; atrás, el doctor y el de la máscara; el piloto de perfil a la derecha del cuadro. El sol entra por la ventana del
copiloto (izquierda del cuadro), de costado.
Uso: RES=1080x1920 SAMPLES=64 OUT=carpeta ASSETS=carpeta [SENTADO=fbx] python3 estilo_A.py"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bpy
from mathutils import Vector
import ep06 as E

env = lambda k, d: float(os.environ.get(k, d))
w, h = (int(v) for v in os.environ.get("RES", "1080x1920").split("x"))
out = os.environ.get("OUT", os.path.join(HERE, "out")); os.makedirs(out, exist_ok=True)
sc = E.escena("EstiloA", (w, h), int(os.environ.get("SAMPLES", 64)))
E.sol(sc, fuerza_cielo=env("CIELO", 0.25), sol=env("SOL", 4.5))
sc.view_settings.exposure = env("EXPO", 0.0)
E.desierto(sc)
E.cerros(sc)
auto = E.auto(sc)
sentado_fbx = os.environ.get("SENTADO") or os.path.join(E.K.ASSETS, E.SENTADO_FBX)
reg = []
arms = {}
for q in ("caballero", "piloto", "mascara", "doctor"):
    if os.path.exists(os.path.join(E.K.ASSETS, E.FBX[q])):
        a = E.sentado(sc, q, sentado_fbx)
        arms[q] = a
        reg.append(f"{q}: {'ok' if a is not None and E.tiene_esqueleto(a) else 'sin esqueleto'}")
    else:
        E.placeholder(sc, q); reg.append(f"{q}: muñeco de prueba")
cab = arms.get("caballero")
if cab is not None and E.tiene_esqueleto(cab):
    E.lanzarse(cab, env("LANZA", 1.0))
for q, a in arms.items():
    if a is not None and E.tiene_esqueleto(a):
        E.cinturon_de(sc, a, q)
BOLSA = (env("BOLSA_X", 0.0), env("BOLSA_Y", -0.42), env("BOLSA_Z", 1.42))
E.bolsa(sc, BOLSA, rot=(math.radians(-80), 0, math.radians(15)))
# rebote suave del lado de la cámara (invisible en reflejos), como en el Ep. 5
f = E.luz_area(sc, "Rebote", (0.1, -0.55, 1.5), (-0.37, 0.30, 1.45), env("FILL", 4), (1.0, 0.9, 0.82), 0.3, spread=60)
f.visible_glossy = False
pos = Vector((env("CAM_X", -0.05), env("CAM_Y", -0.30), env("CAM_Z", 1.43)))
mira = Vector((env("MIRA_X", -0.36), env("MIRA_Y", 0.30), env("MIRA_Z", 1.38)))
E.camara(sc, pos, mira, lente=env("LENTE", 35), fstop=env("FSTOP", 5.6), foco=(Vector((-0.37, 0.15, 1.45)) - pos).length)
sc.render.filepath = os.path.join(out, os.environ.get("NOMBRE", "estilo_A_HD") + ".png")
bpy.ops.render.render(write_still=True)
open(os.path.join(out, "A_registro.txt"), "w").write("\n".join(reg) + "\n")
print("ok", sc.render.filepath, reg)
