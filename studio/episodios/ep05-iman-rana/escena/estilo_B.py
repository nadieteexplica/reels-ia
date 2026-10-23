"""Cuadro de estilo B (Ep. 5, parte hipotética) — exterior: el imán gigante que haría falta para una persona, armado en
medio del salar al atardecer; los cables cruzan el salar hasta una central nuclear en el horizonte, y Pete flota adentro.
Todo a escala real (Pete 1,79 m, torres de ~150 m a 2,5 km).
Uso: RES=1080x1920 SAMPLES=64 OUT=carpeta ASSETS=carpeta [POSE=fbx de Mixamo] python3 estilo_B.py"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bpy
from mathutils import Vector
import ep05 as E

w, h = (int(v) for v in os.environ.get("RES", "1080x1920").split("x"))
out = os.environ.get("OUT", os.path.join(HERE, "out")); os.makedirs(out, exist_ok=True)
sc = E.escena("EstiloB", (w, h), int(os.environ.get("SAMPLES", 64)))
E.cielo_atardecer(sc, elev=float(os.environ.get("SOL_ELEV", 4)), rot=float(os.environ.get("SOL_ROT", 150)), fuerza=0.28, sol=4.5)
E.salar(sc)
E.cerros(sc)
E.central_nuclear(sc, pos=(-1150, 2080, 0))
boca = E.iman_gigante(sc)
pose = os.environ.get("POSE")
if os.path.exists(os.path.join(E.ASSETS, E.PETE_FBX)):
    pete = E.pete(sc, pose if pose and os.path.isfile(pose) else None, frame=int(os.environ.get("POSE_CUADRO", 40)))
    pete.location = (0.05, 0.0, boca + 0.45)
    base = pete.rotation_euler.copy()
    pete.rotation_euler = (base.x + math.radians(4), base.y + math.radians(-3), base.z + math.radians(-35))
    if not (pose and os.path.isfile(pose)):
        bpy.context.view_layer.update()
        E.pose_flotando(pete)
    open(os.path.join(out, "B_registro.txt"), "w").write(f"pose: {pose}\n")
else:
    E.cilindro(sc, "Persona_prueba", 0.22, 1.79, (0.05, 0, boca + 0.45), mat=E.mat_pintura("prueba", (0.7, 0.3, 0.1)))
centro = Vector((0.05, 0.0, boca + 1.2))
E.luz_area(sc, "RellenoPete", (6, -12, boca + 3), centro, 60, (1.0, 0.86, 0.75), 3.0, spread=30)
pos = Vector((7.0, -18.5, 1.5))
E.camara(sc, pos, Vector((0, 0, 3.4)), lente=35, fstop=8.0, foco=(centro - pos).length)
sc.render.filepath = os.path.join(out, os.environ.get("NOMBRE", "estilo_B_HD") + ".png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath)
