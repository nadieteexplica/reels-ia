"""Cuadro de estilo B (Ep. 5, parte hipotética): Pete flotando dentro del imán gigante que haría falta para una persona.
Uso: RES=1080x1920 SAMPLES=64 OUT=carpeta ASSETS=carpeta [POSE=fbx de Mixamo] python3 estilo_B.py"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bpy
from mathutils import Vector
import ep05 as E

w, h = (int(v) for v in os.environ.get("RES", "1080x1920").split("x"))
out = os.environ.get("OUT", os.path.join(HERE, "out")); os.makedirs(out, exist_ok=True)
sc = E.escena("EstiloB", (w, h), int(os.environ.get("SAMPLES", 64)))
E.mundo(sc, "warehouse.hdr", 0.45, rot=120)
E.nave(sc)
boca = E.iman_gigante(sc)
pose = os.environ.get("POSE")
if os.path.exists(os.path.join(E.ASSETS, E.PETE_FBX)):
    pete = E.pete(sc, pose if pose and os.path.isfile(pose) else None, frame=int(os.environ.get("POSE_CUADRO", 40)))
    pete.location = (0.05, 0.0, boca + 0.45)
    pete.rotation_euler = (math.radians(4), math.radians(-3), math.radians(-35))
    # flotando: brazos un poco abiertos y relajados
    for lado, sg in (("LeftArm", 1), ("RightArm", -1)):
        try:
            E.girar_hueso(pete, lado, (0, 0, 1), 12 * sg)
        except StopIteration:
            pass
    centro = Vector((0.05, 0.0, boca + 1.2))
else:                                   # sin el personaje (prueba local): un cilindro del alto de una persona
    E.cilindro(sc, "Persona_prueba", 0.22, 1.79, (0.05, 0, boca + 0.45), mat=E.mat_pintura("prueba", (0.7, 0.3, 0.1)))
    centro = Vector((0.05, 0.0, boca + 1.2))
# luz: cenital fría grande (techo de la nave), lámparas de sodio cálidas a los lados, contraluz sobre Pete
E.luz_area(sc, "Cenital", (0, -2, 16), (0, 0, 0), 1800, (0.82, 0.9, 1.0), 8)
E.luz_area(sc, "Sodio1", (-9, 6, 7), (0, 0, 2), 1500, (1.0, 0.58, 0.28), 2, spread=60)
E.luz_area(sc, "Sodio2", (10, 4, 6), (0, 0, 2), 1000, (1.0, 0.6, 0.3), 2, spread=60)
E.luz_area(sc, "ContraPete", (-1.5, 5, boca + 3), (0, 0, boca + 1.3), 700, (0.7, 0.85, 1.0), 1.0, spread=30)
E.luz_area(sc, "LlavePete", (5, -6, boca + 4), (0, 0, boca + 1.3), 450, (1.0, 0.9, 0.8), 1.5, spread=30)
pos = Vector((5.0, -10.5, 4.9))
E.camara(sc, pos, centro + Vector((0, 0, -1.6)), lente=24, fstop=5.6, foco=(centro - pos).length)
sc.render.filepath = os.path.join(out, os.environ.get("NOMBRE", "estilo_B_HD") + ".png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath)
