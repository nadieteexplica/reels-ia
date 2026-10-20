"""Base común de los planos del Ep. 2: tiempos, escena, cámara y funciones de movimiento.

Cada plano (planos_ep02.py) arma su escena y devuelve una función actualizar(f) que pone todo en su lugar para el
cuadro global f (sin keyframes: la pose se calcula). plano.py la llama cuadro a cuadro y renderiza.
"""
import json, math, os, random
import bpy
from mathutils import Vector, Quaternion

FPS = 30
HERE = os.path.dirname(os.path.abspath(__file__))
EPI = os.path.abspath(os.path.join(HERE, ".."))

# tiempos (s) de cada plano, sacados del storyboard v3.1 (aprobado en la puerta 3) = words.json
T = {1: (0.00, 1.71), 2: (1.71, 3.11), 3: (3.11, 4.83), 4: (4.83, 5.91), 5: (5.91, 8.74), 6: (8.74, 9.64),
     7: (9.64, 11.51), 8: (11.51, 13.10), 9: (13.10, 15.08), 10: (15.08, 16.71), 11: (16.71, 18.60), 12: (18.60, 20.17),
     13: (20.17, 21.83), 14: (21.83, 23.56), 15: (23.56, 25.46), 16: (25.46, 26.90), 17: (26.90, 27.79), 18: (27.79, 29.30),
     19: (29.30, 31.62), 20: (31.62, 33.12), 21: (33.12, 35.11), 22: (35.11, 36.75), 23: (36.75, 39.54), 24: (39.54, 41.37),
     25: (41.37, 43.77), 26: (43.77, 46.61), 27: (46.61, 48.83), 28: (48.83, 49.88), 29: (49.88, 52.66), 30: (52.66, 54.49),
     31: (54.49, 56.20), 32: (56.20, 58.42), 33: (58.42, 59.44), 34: (59.44, 61.84), 35: (61.84, 63.91), 36: (63.91, 66.19),
     37: (66.19, 68.42), 38: (68.42, 71.11), 39: (71.11, 72.28), 40: (72.28, 73.99)}


def F(t):
    """Cuadro global (1 = t 0) del instante t."""
    return int(round(t * FPS)) + 1


def FR(k):
    """Cuadros [a, b) del plano k."""
    a, b = T[k]
    return F(a), F(b)


FIN = FR(40)[1]          # primer cuadro después del último


def palabras():
    return json.load(open(os.path.join(EPI, "words.json")))


def t_palabra(prefijo, desde=0.0):
    """Segundo en que empieza la primera palabra que empieza con `prefijo` (sin tildes ni signos) desde `desde`."""
    for w in palabras():
        if w["s"] >= desde - 1e-6 and w["w"].lower().strip("¡!¿?.,:;…").startswith(prefijo.lower()):
            return w["s"]
    raise KeyError(prefijo)


# ---------------- curvas ----------------
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lin(f, f0, f1):
    """0→1 lineal entre los cuadros f0 y f1 (fuera, se queda en 0 o 1)."""
    if f1 == f0:
        return 1.0 if f >= f1 else 0.0
    return clamp((f - f0) / (f1 - f0))


def suave(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def suave2(x):
    x = clamp(x)
    return x * x * x * (x * (6 * x - 15) + 10)


def sale(x):              # ease-out
    x = clamp(x)
    return 1 - (1 - x) ** 3


def entra(x):             # ease-in
    x = clamp(x)
    return x ** 3


def rebote(x, s=1.70158):  # ease-out con un poquito de rebote (back)
    x = clamp(x)
    x -= 1
    return x * x * ((s + 1) * x + s) + 1


def resorte(t, frec=3.0, amort=6.0):
    """Respuesta de resorte: 0 en t=0, oscila y se asienta en 1 (t en segundos)."""
    if t <= 0:
        return 0.0
    return 1 - math.exp(-amort * t) * math.cos(2 * math.pi * frec * t)


def mezcla(a, b, x):
    if isinstance(a, (int, float)):
        return a + (b - a) * x
    return Vector(a).lerp(Vector(b), x)


def ruido(f, seed=0, vel=1.0):
    """Ruido suave en [-1, 1] (suma de senos con fases fijas)."""
    r = random.Random(seed)
    s = 0.0
    for k in range(3):
        s += math.sin(f * vel * r.uniform(0.15, 0.5) * (k + 1) + r.uniform(0, 6.28)) / (k + 1)
    return s / 1.83


def tramo(f, claves):
    """Interpola por tramos suaves: claves = [(cuadro, valor), ...] ordenadas."""
    if f <= claves[0][0]:
        return claves[0][1]
    for (fa, va), (fb, vb) in zip(claves, claves[1:]):
        if f <= fb:
            return mezcla(va, vb, suave(lin(f, fa, fb)))
    return claves[-1][1]


# ---------------- escena ----------------
def escena(nombre="Ep02"):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.name = nombre
    sc.render.fps = FPS
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 16
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.03
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6
    sc.cycles.transparent_max_bounces = 16
    sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Punchy"
    sc.render.image_settings.file_format = "PNG"
    sc.world = bpy.data.worlds.new("Mundo")
    sc.world.use_nodes = True
    return sc


def area(sc, name, loc, energy, size, color, target, volumen=False, brillo=True):
    L = bpy.data.lights.new(name, "AREA")
    L.energy, L.size, L.color, L.shape = energy, size, color, "DISK"
    ob = bpy.data.objects.new(name, L)
    sc.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    ob.visible_volume_scatter = volumen
    ob.visible_glossy = brillo
    return ob


def camara(sc, nombre="Cam", lens=35, fstop=None):
    cam = bpy.data.objects.new(nombre, bpy.data.cameras.new(nombre))
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.data.sensor_fit = "VERTICAL"
    cam.data.sensor_height = 24
    cam.data.lens = lens
    cam.data.clip_start = 0.005
    cam.data.clip_end = 2000
    cam.rotation_mode = "QUATERNION"
    if fstop:
        cam.data.dof.use_dof = True
        cam.data.dof.aperture_fstop = fstop
    return cam


def mirar(cam, pos, tgt, lens=None, foco=None, giro=0.0):
    """Pone la cámara en pos mirando a tgt (con giro en grados alrededor del eje de vista)."""
    cam.location = Vector(pos)
    q = (Vector(tgt) - Vector(pos)).to_track_quat("-Z", "Y")
    if giro:
        q = q @ Quaternion((0, 0, 1), math.radians(giro))
    cam.rotation_quaternion = q
    if lens:
        cam.data.lens = lens
    if cam.data.dof.use_dof:
        cam.data.dof.focus_distance = ((Vector(foco) if foco is not None else Vector(tgt)) - Vector(pos)).length


def empujar(cam, f, f0, f1, pos, tgt, cuanto=0.06, lens=None, foco=None, curva=None):
    """Push-in: avanza `cuanto` (fracción de la distancia) hacia tgt entre f0 y f1, con ease."""
    x = (curva or suave)(lin(f, f0, f1))
    p = Vector(pos).lerp(Vector(tgt), cuanto * x)
    mirar(cam, p, tgt, lens, foco)


def pantalla(sc, cam, punto):
    """Punto del mundo → píxel en 1080x1920 (y hacia abajo)."""
    from bpy_extras.object_utils import world_to_camera_view
    v = world_to_camera_view(sc, cam, Vector(punto))
    return round(v.x * 1080), round((1 - v.y) * 1920)


def oculto(ob, si=True):
    ob.hide_render = si
    for ch in ob.children_recursive:
        ch.hide_render = si


def hijos(ob):
    return [ob] + list(ob.children_recursive)
