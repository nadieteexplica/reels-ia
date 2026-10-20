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
# llega hasta la cámara (abajo no queda el borde oscuro); corrida a la izquierda para que el borde derecho de la lengua
# entre al cuadro, y con el surco central marcado (puerta 4 c2 r2: se leía como un tapete de goma)
XL = float(os.environ.get("LENGUA_X", -0.055))
LG.lengua(C, largo=1.0, y0=-0.62, ancho=float(os.environ.get("LENGUA_ANCHO", 0.27)), x0=XL, surco=float(os.environ.get("SURCO", 0.016)))
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
# papilas (sensores en reposo) por toda la lengua, también en primer plano; cada una apoyada con un rayo en la superficie
bpy.context.view_layer.update()
_lg = bpy.data.objects["Lengua"]
_dg = bpy.context.evaluated_depsgraph_get()
_Mi = _lg.matrix_world.inverted()
def _sobre(x, y):
    hit, loc, nor, _ = _lg.evaluated_get(_dg).ray_cast(_Mi @ Vector((x, y, 0.5)), Vector((0, 0, -1)))
    return (loc.z, nor) if hit else (None, None)
# papilas sueltas (no en grilla): muchas chicas y unas pocas grandes y más rojas; ninguna dentro del surco ni pegada a la campana
chica = P.mat("SensorReposo", (0.95, 0.62, 0.62), rough=0.5, coat=0.12)     # mate: brillantes se leían como gotas de agua
grande = P.mat("PapilaGrande", (0.90, 0.42, 0.46), rough=0.45, coat=0.15)
rp = random.Random(5)
puestas, intentos = [], 0
N_PAP = int(os.environ.get("N_PAP", 420))
while len(puestas) < N_PAP and intentos < 40000:
    intentos += 1
    x, y = rp.uniform(XL - 0.15, XL + 0.15), rp.uniform(-0.34, 0.32)
    big = rp.random() < 0.07
    r = rp.uniform(0.0062, 0.0080) if big else rp.uniform(0.0026, 0.0048)
    if (x ** 2 + (y - 0.02) ** 2) ** 0.5 < 0.05 or abs(x - XL) < 0.011:
        continue
    if any((x - a) ** 2 + (y - b) ** 2 < (r + c + 0.0035) ** 2 for a, b, c in puestas):
        continue
    z, nor = _sobre(x, y)
    if z is None or nor.z < 0.55:                       # ni en el borde que cae
        continue
    puestas.append((x, y, r))
    cp = LG.cupula(f"Sensor{len(puestas)}", (x, y, z - 0.0006), r, C, m=grande if big else chica)
    cp.rotation_euler = Vector(nor).to_track_quat("Z", "Y").to_euler()
    cp.scale = (1, 1, 0.65)                             # bultitos bajos, no gotas
print("papilas", len(puestas))
# la campana se apoya en la superficie (la lengua corrida baja bajo x=0): todo lo de la campana y la cámara S baja con ella
ZC = _sobre(0, 0.02)[0] - 0.0008
# la campanita es plateada (neutra) siempre; cuando suena, lo dicen la luz y las ondas del color del estímulo (puerta 4 c2: rojo sobre rojo no se leía)
camp, domo = LG.campana(C, loc=(0, 0.02, ZC), r=0.035, color=None)
if col:
    LG.ondas(C, (0, 0.02, 0.050 + ZC), 0.040, col, tope_izq=float(os.environ.get("TOPE_IZQ", 8)))
    luz = bpy.data.lights.new("LuzCampana", "POINT")
    luz.energy, luz.color, luz.shadow_soft_size = float(os.environ.get("LUZ", 0.9)), col, 0.02
    lo = bpy.data.objects.new("LuzCampana", luz)
    C.objects.link(lo)
    lo.location = tuple(float(v) for v in os.environ.get("LUZ_POS", "0,-0.035,0.014").split(",")); lo.location.z += ZC   # c3: baja, junto a la lengua: tiñe la lengua y no se refleja como parche blanco en el frente de la campana
if ESTADO == "roja":
    # la cabeza vanilílica (anillo con el OH) calza sobre la perilla de la campanita, de cara a la cámara;
    # la cadena se va hacia arriba a la izquierda (por donde entró). Nada atraviesa el domo: se apoya encima.
    ESC_MOL = float(os.environ.get("ESC_MOL", 0.0050))
    mol = LG.capsaicina(C, escala=ESC_MOL)
    mol.rotation_euler = (math.radians(90 + float(os.environ.get("MOL_X", 0))), math.radians(float(os.environ.get("MOL_INCL", -100))), math.radians(float(os.environ.get("MOL_Z", 0))))
    bpy.context.view_layer.update()
    oh = bpy.data.objects["Capsaicina_Oh"]
    r_at = 0.48 * ESC_MOL
    # se apoya ENCIMA de la campana: cada átomo se compara con la superficie real (rayo hacia abajo contra la campana)
    piezas = [o for o in bpy.data.objects if o.name.startswith("Campanita") and o.type == "MESH"]
    dg = bpy.context.evaluated_depsgraph_get()
    def techo(p):
        best = None
        for o in piezas:
            Mi = o.matrix_world.inverted()
            hit, loc, *_ = o.evaluated_get(dg).ray_cast(Mi @ Vector((p.x, p.y, 1.0)), (Mi.to_3x3() @ Vector((0, 0, -1))).normalized())
            if hit:
                z = (o.matrix_world @ loc).z
                best = z if best is None else max(best, z)
        return best
    perilla_w = bpy.data.objects["Campanita_perilla"].matrix_world.translation
    mol.location = mol.location + (perilla_w + Vector((0, 0, 0.035 * 0.13 + r_at * 0.85)) - oh.matrix_world.translation)
    bpy.context.view_layer.update()
    atomos = [a for a in mol.children if "_e_" not in a.name]
    alza, quien = 0.0, None
    for a in atomos:
        w = a.matrix_world.translation
        for dx, dy in ((0, 0), (r_at * 0.7, 0), (-r_at * 0.7, 0), (0, r_at * 0.7), (0, -r_at * 0.7)):
            t = techo(w + Vector((dx, dy, 0)))
            if t is not None and t + r_at * 0.9 - w.z > alza:
                alza, quien = t + r_at * 0.9 - w.z, (a.name, round(t, 4))
    mol.location.z += alza
    bpy.context.view_layer.update()
    print("molécula alzada", round(alza * 1000, 2), "mm: apoyada sobre la campana, sin atravesarla", quien)
if ESTADO == "naranja":
    LG.gota_sopa(C, (0.05, -0.01, 0.03 + ZC), r=0.012)


def area(name, loc, energy, size, color, target=(0, 0.02, 0.03)):
    L = bpy.data.lights.new(name, "AREA")
    L.energy, L.size, L.color, L.shape = energy, size, color, "DISK"
    ob = bpy.data.objects.new(name, L)
    sc.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()

area("Key", (-0.25, -0.30, 0.35 + ZC), float(os.environ.get("KEY", 4)), 0.35, (1.0, 0.92, 0.85), target=(0, 0.02, 0.03 + ZC))
area("Rim", (0.25, 0.35, 0.25 + ZC), 7, 0.3, (1.0, 0.6, 0.6), target=(0, 0.02, 0.03 + ZC))
cam = bpy.data.objects.new("CamS", bpy.data.cameras.new("CamS"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.lens = float(os.environ.get("LENS", 30))
cam.data.sensor_fit = "VERTICAL"
cam.data.sensor_height = 24
cam.location = Vector(tuple(float(x) for x in os.environ.get("CAM", "0.0,-0.36,0.17").split(","))) + Vector((0, 0, ZC))   # cámara S: siempre la misma (respecto de la campana)
tgt = Vector(tuple(float(x) for x in os.environ.get("TGT", "0,0.05,-0.023").split(","))) + Vector((0, 0, ZC))
cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = (Vector((0, 0.02, 0.04 + ZC)) - cam.location).length
cam.data.dof.aperture_fstop = 3.5
sc.render.filepath = os.path.join(OUT, os.environ.get("NOMBRE", f"estilo_lengua_{ESTADO}") + ".png")
if not os.environ.get("SOLO_POSE"):
    bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath)
