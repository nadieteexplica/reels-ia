"""Cuadro de estilo B (Ep. 5, parte hipotética) — exterior: el imán gigante que haría falta para una persona, armado en
medio del salar al atardecer; los cables cruzan el salar hasta una central nuclear en el horizonte, y Pete flota sobre la
boca negra del imán. Todo a escala real (Pete 1,79 m, imán de 5 m de diámetro, torres de ~150 m a 2,4 km).
v2 (puerta 4 r1): sol bajo (12°) y de costado, como en A (un lado del imán en sombra, sombras largas), cámara más alta para
que se vea la boca, Pete a 0,8 m sobre ella y más grande en cuadro, central entera y despegada del imán.
Uso: RES=1080x1920 SAMPLES=64 OUT=carpeta ASSETS=carpeta [POSE=fbx de Mixamo] python3 estilo_B.py"""
import math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bpy
from mathutils import Vector
import ep05 as E

env = lambda k, d: float(os.environ.get(k, d))
w, h = (int(v) for v in os.environ.get("RES", "1080x1920").split("x"))
out = os.environ.get("OUT", os.path.join(HERE, "out")); os.makedirs(out, exist_ok=True)
sc = E.escena("EstiloB", (w, h), int(os.environ.get("SAMPLES", 64)))
E.cielo_atardecer(sc, elev=env("SOL_ELEV", 5), rot=env("SOL_ROT", 60), fuerza=env("CIELO", 0.12), sol=env("SOL", 4.0))
sc.view_settings.exposure = env("EXPO", -0.5)
E.salar(sc)
E.cerros(sc)
PLANTA = (-1150, 2080, 0)
E.central_nuclear(sc, pos=PLANTA)
boca = E.iman_gigante(sc)
ALTO = env("PETE_ALTO", 0.8)                 # botas sobre la boca
pose = os.environ.get("POSE")
if os.path.exists(os.path.join(E.ASSETS, E.PETE_FBX)):
    pete = E.pete(sc, pose if pose and os.path.isfile(pose) else None, frame=int(os.environ.get("POSE_CUADRO", 40)))
    pete.location = (0.0, 0.0, boca + ALTO)
    base = pete.rotation_euler.copy()
    pete.rotation_euler = (base.x + math.radians(4), base.y + math.radians(-3), base.z + math.radians(env("PETE_GIRO", -28)))
    if not (pose and os.path.isfile(pose)):
        bpy.context.view_layer.update()
        E.pose_flotando(pete)
    open(os.path.join(out, "B_registro.txt"), "w").write(f"pose: {pose}\n")
else:
    E.cilindro(sc, "Persona_prueba", 0.22, 1.79, (0.0, 0, boca + ALTO), mat=E.mat_pintura("prueba", (0.7, 0.3, 0.1)))
centro = Vector((0.0, 0.0, boca + ALTO + 0.9))
# relleno muy suave desde el lado de la cámara (el cielo ya rellena; sin esto la cara queda negra)
az = math.radians(env("CAM_AZ", -28))
d = env("CAM_D", 15.0)
pos = Vector((-math.sin(az) * d, -math.cos(az) * d, env("CAM_Z", 6.6)))
E.luz_area(sc, "RellenoPete", tuple(pos + Vector((-2, 0, 1.5))), centro, 25, (1.0, 0.9, 0.82), 2.0, spread=30)
mira = Vector((0, 0, env("MIRA_Z", 4.7)))
E.camara(sc, pos, mira, lente=env("LENTE", 50), fstop=env("FSTOP", 8.0), foco=(centro - pos).length)
sc.render.filepath = os.path.join(out, os.environ.get("NOMBRE", "estilo_B_HD") + ".png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath)
