"""Cuadro de estilo del interior "lengua" (cámara S): la molécula de capsaicina calza en la campanita y la hace sonar roja.

Uso: RES=720x1280 SAMPLES=64 OUT=carpeta [ESTADO=roja|reposo|naranja|celeste] python3 estilo_lengua.py
"""
import math, os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.abspath(os.path.join(HERE, "../../.."))
for p in (HERE, os.path.join(STUDIO, "plantilla")):
    sys.path.insert(0, p)
import bpy
from mathutils import Vector
import props as P
import lengua as LG

OUT = os.environ.get("OUT", os.path.join(HERE, "out"))
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
res = tuple(int(v) for v in os.environ.get("RES", "720x1280").split("x"))
sc.render.engine = "CYCLES"
sc.cycles.device = os.environ.get("DEVICE", "CPU")
sc.cycles.samples = int(os.environ.get("SAMPLES", 64))
sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = res
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Punchy"
sc.world = bpy.data.worlds.new("Boca")
sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.20, 0.03, 0.05, 1)
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.6
C = P.collection("Lengua")
LG.lengua(C)
# paladar al fondo (cueva rosada oscura)
pal = P.prim("sphere", "Paladar", C, P.mat("Paladar", (0.35, 0.05, 0.07), rough=0.5, sss=0.3), r=0.6)
pal.scale = (1.0, 1.4, 0.7)
pal.location = (0, 0.25, 0.05)
for p_ in pal.data.polygons:
    p_.flip()
ESTADO = os.environ.get("ESTADO", "roja")
col = {"roja": LG.ROJO, "naranja": LG.NARANJO, "celeste": LG.CELESTE, "reposo": None}[ESTADO]
rnd = random.Random(2)
# filas de sensores en reposo (blanco neutro)
for j in range(9):
    for i in range(-5, 6):
        x = i * 0.026 + (0.013 if j % 2 else 0) + rnd.uniform(-0.004, 0.004)
        y = 0.03 + j * 0.03 + rnd.uniform(-0.004, 0.004)
        if abs(x) < 0.03 and y < 0.07:
            continue
        z = -abs(x / 0.32) ** 2 * 0.35 * 0.32 * 0 - (x ** 2) * 1.1
        LG.cupula(f"Sensor{i}_{j}", (x, y, z), 0.0055, C)
camp, domo = LG.campana(C, loc=(0, 0.02, 0.0), r=0.035, color=col, brillo=1.2 if col else 0.0)
if col:
    LG.ondas(C, (0, 0.02, 0.045), 0.035, col)
    luz = bpy.data.lights.new("LuzCampana", "POINT")
    luz.energy, luz.color, luz.shadow_soft_size = 0.8, col, 0.02
    lo = bpy.data.objects.new("LuzCampana", luz)
    C.objects.link(lo)
    lo.location = (0, -0.03, 0.05)
if ESTADO == "roja":
    # la cabeza vanilílica (anillo con el OH) calza sobre la perilla de la campanita, de cara a la cámara;
    # la cadena se va hacia arriba a la izquierda (por donde entró). Nada atraviesa el domo: se apoya encima.
    ESC_MOL = float(os.environ.get("ESC_MOL", 0.0062))
    mol = LG.capsaicina(C, escala=ESC_MOL)
    mol.rotation_euler = (math.radians(90), math.radians(float(os.environ.get("MOL_INCL", -24))), 0)
    bpy.context.view_layer.update()
    oh = bpy.data.objects["Capsaicina_Oh"]
    r_at = 0.48 * ESC_MOL
    tope = Vector((0, 0.02, 0.035 * 1.30))                    # cima de la perilla (campana r=0.035 en (0, 0.02, 0))
    mol.location = mol.location + (tope + Vector((0, 0, r_at * 0.85)) - oh.matrix_world.translation)
    bpy.context.view_layer.update()
    # comprobación: ningún átomo dentro del domo (perfil de revolución) salvo el que toca la perilla
    def h_domo(rho, r=0.035):
        prof = [(r * 0.98, 0.0), (r * 0.95, r * 0.25), (r * 0.80, r * 0.55), (r * 0.55, r * 0.78), (r * 0.25, r * 0.88), (0.0, r * 0.9)]
        if rho >= prof[0][0]:
            return -1
        for (r0, z0), (r1, z1) in zip(prof, prof[1:]):
            if r1 <= rho <= r0:
                return r * 0.25 + z0 + (z1 - z0) * (r0 - rho) / (r0 - r1)
        return r * 0.25 + r * 0.9
    for a in mol.children:
        if "_e_" in a.name:
            continue
        w = a.matrix_world.translation - Vector((0, 0.02, 0))
        rho = Vector((w.x, w.y)).length
        assert w.z - r_at > h_domo(rho) - 1e-4 or a.name == "Capsaicina_Oh", ("átomo dentro del domo", a.name)
    print("molécula: ningún átomo atraviesa el domo")
if ESTADO == "naranja":
    LG.gota_sopa(C, (0.05, -0.01, 0.03), r=0.012)


def area(name, loc, energy, size, color, target=(0, 0.02, 0.03)):
    L = bpy.data.lights.new(name, "AREA")
    L.energy, L.size, L.color, L.shape = energy, size, color, "DISK"
    ob = bpy.data.objects.new(name, L)
    sc.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()

area("Key", (-0.25, -0.30, 0.35), 5, 0.35, (1.0, 0.92, 0.85))
area("Rim", (0.25, 0.35, 0.25), 7, 0.3, (1.0, 0.6, 0.6))
cam = bpy.data.objects.new("CamS", bpy.data.cameras.new("CamS"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.lens = 35
cam.data.sensor_fit = "VERTICAL"
cam.data.sensor_height = 24
cam.location = (0.0, -0.36, 0.13)            # cámara S: siempre la misma
tgt = Vector((0, 0.05, 0.035))
cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = (Vector((0, 0.02, 0.04)) - cam.location).length
cam.data.dof.aperture_fstop = 3.5
sc.render.filepath = os.path.join(OUT, os.environ.get("NOMBRE", f"estilo_lengua_{ESTADO}") + ".png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath)
