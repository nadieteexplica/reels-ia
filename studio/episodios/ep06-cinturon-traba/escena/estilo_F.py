"""Ficha de personajes del Ep. 6 (para ficha.jpg y el auditor): los 4 de pie en el camino de tierra, al lado del 4x4, con
la luz del episodio (sol bajo de costado). Piloto (RACE), caballero (castle.guard), el de la máscara antigás (GAS.MASK) y el
doctor (chad), de Mixamo With Skin. Uso: RES=1080x1920 SAMPLES=64 OUT=carpeta ASSETS=carpeta [POSE=fbx] python3 estilo_F.py"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bpy
from mathutils import Vector
import ep06 as E

env = lambda k, d: float(os.environ.get(k, d))
w, h = (int(v) for v in os.environ.get("RES", "1080x1920").split("x"))
out = os.environ.get("OUT", os.path.join(HERE, "out")); os.makedirs(out, exist_ok=True)
sc = E.escena("EstiloF", (w, h), int(os.environ.get("SAMPLES", 64)))
E.sol(sc, fuerza_cielo=env("CIELO", 0.22), sol=env("SOL", 4.0), az=env("SOL_AZ", 300))
sc.view_settings.exposure = env("EXPO", -0.3)
E.desierto(sc)
E.cerros(sc)
auto = E.auto(sc)
auto.location = (2.6, 1.5, 0); auto.rotation_euler = (0, 0, math.radians(20))
pose = os.environ.get("POSE")
reg = []
xs = {"piloto": -1.35, "caballero": -0.45, "mascara": 0.45, "doctor": 1.35}
for q, x in xs.items():
    if not os.path.exists(os.path.join(E.K.ASSETS, E.FBX[q])):
        reg.append(f"{q}: falta"); continue
    a = E.personaje(sc, q)
    ok = E.tiene_esqueleto(a)
    if ok and pose and os.path.isfile(pose):
        E.copiar_pose(a, pose, int(env("POSE_CUADRO", 30)))
    if ok:
        E.mirar_adelante(a, Vector((0, 1, 0)))     # mirando a la cámara (+y)
        bpy.context.view_layer.update()
        pie = (E.pos_hueso(a, "LeftFoot") + E.pos_hueso(a, "RightFoot")) / 2
        a.location += Vector((x, 0, 0)) - Vector((pie.x, pie.y, 0)) + Vector((0, 0, -min(E.pos_hueso(a, "LeftToeBase").z, E.pos_hueso(a, "RightToeBase").z) + 0.03))
        alto = E.pos_hueso(a, "Head", cola=True).z
        reg.append(f"{q}: ok, alto {alto:.2f} m")
    else:
        a.location = (x, 0, 0); reg.append(f"{q}: sin esqueleto Mixamo")
centro = Vector((0, 0, 1.0))
pos = Vector((env("CAM_X", 0.0), env("CAM_Y", 8.6), env("CAM_Z", 1.15)))
f = E.luz_area(sc, "Rebote", tuple(pos + Vector((-1.5, 0, 1.0))), tuple(centro), env("FILL", 30), (1.0, 0.9, 0.82), 2.0, spread=40)
f.visible_glossy = False
E.camara(sc, pos, centro + Vector((0, 0, 0.0)), lente=env("LENTE", 35), fstop=env("FSTOP", 8.0))
sc.render.filepath = os.path.join(out, os.environ.get("NOMBRE", "estilo_F_HD") + ".png")
bpy.ops.render.render(write_still=True)
open(os.path.join(out, "F_registro.txt"), "w").write("\n".join(reg) + "\n")
print("ok", sc.render.filepath, reg)
