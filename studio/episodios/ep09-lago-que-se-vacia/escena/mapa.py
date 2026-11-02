"""Ep. 9 · plano 0 (entrada pedida por Tomás, 2-nov): la Tierra de verdad (NASA Blue Marble Next Generation, dic-2004, con
relieve y batimetría; dominio público) gira, hace zoom a Chile (contorno de Natural Earth 1:10m, dominio público) y baja hasta
Aysén, donde una zona roja marca el lago Cachet 2. Voz: "¿Sabías que en Chile hay un lago que se vacía solo?".

Tres niveles de imagen en el mismo material (sin costuras: es la misma imagen de la NASA a más resolución):
  L0 mundo 5400×2700 (7,4 km/px) · L1 Sudamérica del 21600×10800 (1,85 km/px) · L2 Aysén del mosaico B2 de 500 m/px.
El zoom termina a ~600 km de altura (el L2 se ve nítido hasta ahí en 1080 px de ancho).

Uso: MAPAS=carpeta RES=1080x1920 SAMPLES=24 DIR=salida [CUADROS=a-b] python3 mapa.py
Escribe salida/NNNNN.png (cuadro 1 = t 0) y salida/mapa_meta.json (dónde cae en pantalla cada cosa, para las píldoras)."""
import os, sys, json, math
import bpy
import numpy as np
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
MAPAS = os.environ.get("MAPAS", HERE)
DIR = os.environ.get("DIR", os.path.join(HERE, "out_mapa"))
os.makedirs(DIR, exist_ok=True)
FPS = 30
DUR = float(os.environ.get("DUR", 3.0))
N = int(round(DUR * FPS))
R = 6.371                       # 1 unidad = 1.000 km
LAGO = (-47.20, -73.25)         # lago Cachet 2: margen norte del glaciar Colonia, borde oriental del Campo de Hielo Norte
L1 = (-100.0, -62.0, -20.0, 16.0)     # lon0, lat0, lon1, lat1 (recortes hechos con los mismos límites)
L2 = (-80.0, -53.0, -66.0, -40.0)


def xyz(lat, lon, r=R):
    la, lo = math.radians(lat), math.radians(lon)
    return Vector((r * math.cos(la) * math.cos(lo), r * math.cos(la) * math.sin(lo), r * math.sin(la)))


def norte(lat, lon):
    la, lo = math.radians(lat), math.radians(lon)
    return Vector((-math.sin(la) * math.cos(lo), -math.sin(la) * math.sin(lo), math.cos(la)))


# ---------------------------------------------------------------- escena
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.samples = int(os.environ.get("SAMPLES", 24))
sc.cycles.use_denoising = True
sc.cycles.denoiser = "OPENIMAGEDENOISE"
sc.cycles.max_bounces = 2
sc.cycles.diffuse_bounces = 1
sc.cycles.glossy_bounces = 1
sc.cycles.transparent_max_bounces = 6
w, h = (int(v) for v in os.environ.get("RES", "1080x1920").split("x"))
sc.render.resolution_x, sc.render.resolution_y = w, h
sc.render.resolution_percentage = 100
sc.render.fps = FPS
sc.view_settings.view_transform = "Standard"      # los colores de la NASA tal cual (AgX los lavaba)
sc.view_settings.look = "None"
sc.view_settings.exposure = 0.0
sc.render.image_settings.file_format = "PNG"
sc.render.use_persistent_data = True


def nodos(nombre):
    m = bpy.data.materials.new(nombre)
    m.use_nodes = True
    return m, m.node_tree


def op(nt, o, a, b=None):
    n = nt.nodes.new("ShaderNodeMath"); n.operation = o
    for i, s in enumerate((a, b)):
        if s is None:
            continue
        if isinstance(s, (int, float)):
            n.inputs[i].default_value = s
        else:
            nt.links.new(s, n.inputs[i])
    return n.outputs[0]


def imagen(nt, ruta, u, v):
    img = bpy.data.images.load(ruta)
    t = nt.nodes.new("ShaderNodeTexImage"); t.image = img; t.interpolation = "Linear"; t.extension = "EXTEND"
    cv = nt.nodes.new("ShaderNodeCombineXYZ"); nt.links.new(u, cv.inputs[0]); nt.links.new(v, cv.inputs[1])
    nt.links.new(cv.outputs[0], t.inputs["Vector"])
    return t.outputs["Color"]


def mascara(nt, uu, vv, borde=0.02):
    """1 dentro del recorte [0,1]², con borde suave (sin costura visible)."""
    def lado(x):
        a = op(nt, "MINIMUM", op(nt, "DIVIDE", x, borde), 1.0)
        b = op(nt, "MINIMUM", op(nt, "DIVIDE", op(nt, "SUBTRACT", 1.0, x), borde), 1.0)
        return op(nt, "MAXIMUM", op(nt, "MINIMUM", a, b), 0.0)
    return op(nt, "MULTIPLY", lado(uu), lado(vv))


# --- la Tierra
bpy.ops.mesh.primitive_uv_sphere_add(segments=512, ring_count=256, radius=R, location=(0, 0, 0))
tierra = bpy.context.object; tierra.name = "Tierra"
bpy.ops.object.shade_smooth()
m, nt = nodos("tierra")
b = nt.nodes["Principled BSDF"]
geo = nt.nodes.new("ShaderNodeNewGeometry")
nrm = nt.nodes.new("ShaderNodeVectorMath"); nrm.operation = "NORMALIZE"; nt.links.new(geo.outputs["Position"], nrm.inputs[0])
sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(nrm.outputs[0], sp.inputs[0])
lon = op(nt, "MULTIPLY", op(nt, "ARCTAN2", sp.outputs["Y"], sp.outputs["X"]), 180.0 / math.pi)     # grados
lat = op(nt, "MULTIPLY", op(nt, "ARCSINE", sp.outputs["Z"]), 180.0 / math.pi)
u0 = op(nt, "ADD", op(nt, "DIVIDE", lon, 360.0), 0.5)
v0 = op(nt, "ADD", op(nt, "DIVIDE", lat, 180.0), 0.5)
c0 = imagen(nt, os.path.join(MAPAS, "world.topo.bathy.200412.3x5400x2700.jpg"), u0, v0)
u1 = op(nt, "DIVIDE", op(nt, "SUBTRACT", lon, L1[0]), L1[2] - L1[0]); v1 = op(nt, "DIVIDE", op(nt, "SUBTRACT", lat, L1[1]), L1[3] - L1[1])
c1 = imagen(nt, os.path.join(MAPAS, "L1_sudamerica.jpg"), u1, v1)
u2 = op(nt, "DIVIDE", op(nt, "SUBTRACT", lon, L2[0]), L2[2] - L2[0]); v2 = op(nt, "DIVIDE", op(nt, "SUBTRACT", lat, L2[1]), L2[3] - L2[1])
c2 = imagen(nt, os.path.join(MAPAS, "L2_aysen.jpg"), u2, v2)
mx1 = nt.nodes.new("ShaderNodeMix"); mx1.data_type = "RGBA"
nt.links.new(mascara(nt, u1, v1, 0.03), mx1.inputs[0]); nt.links.new(c0, mx1.inputs[6]); nt.links.new(c1, mx1.inputs[7])
mx2 = nt.nodes.new("ShaderNodeMix"); mx2.data_type = "RGBA"
nt.links.new(mascara(nt, u2, v2, 0.06), mx2.inputs[0]); nt.links.new(mx1.outputs[2], mx2.inputs[6]); nt.links.new(c2, mx2.inputs[7])
col = mx2.outputs[2]
nt.links.new(col, b.inputs["Base Color"])
b.inputs["Roughness"].default_value = 0.85
# brillo propio: el relieve ya viene sombreado en la imagen; la luz del sol sólo redondea el globo
nt.links.new(col, b.inputs["Emission Color"])
b.inputs["Emission Strength"].default_value = 0.55
tierra.data.materials.append(m)

# --- atmósfera: halo azul en el borde del globo
bpy.ops.mesh.primitive_uv_sphere_add(segments=256, ring_count=128, radius=R * 1.022)
atm = bpy.context.object; atm.name = "Atmosfera"
bpy.ops.object.shade_smooth()
m, nt = nodos("atmosfera")
nt.nodes.remove(nt.nodes["Principled BSDF"])
lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.35
fac = op(nt, "POWER", lw.outputs["Facing"], 6.0)          # sólo el borde (antes velaba todo el disco)
em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = (0.35, 0.62, 1.0, 1); em.inputs[1].default_value = 1.8
tr = nt.nodes.new("ShaderNodeBsdfTransparent")
ms = nt.nodes.new("ShaderNodeMixShader"); nt.links.new(fac, ms.inputs[0]); nt.links.new(tr.outputs[0], ms.inputs[1]); nt.links.new(em.outputs[0], ms.inputs[2])
nt.links.new(ms.outputs[0], nt.nodes["Material Output"].inputs[0])
atm.data.materials.append(m)
atm.visible_shadow = False

# --- cielo: negro con estrellas finas
wd = bpy.data.worlds.new("espacio"); sc.world = wd; wd.use_nodes = True
nt = wd.node_tree
bg = nt.nodes["Background"]
tc = nt.nodes.new("ShaderNodeTexCoord")
vor = nt.nodes.new("ShaderNodeTexVoronoi"); vor.inputs["Scale"].default_value = 420.0
nt.links.new(tc.outputs["Generated"], vor.inputs["Vector"])
est = op(nt, "LESS_THAN", vor.outputs["Distance"], 0.05)
br = op(nt, "MULTIPLY", est, 1.2)
cg = nt.nodes.new("ShaderNodeCombineColor"); [nt.links.new(br, cg.inputs[i]) for i in range(3)]
nt.links.new(cg.outputs[0], bg.inputs["Color"])
bg.inputs["Strength"].default_value = 1.0

# --- sol: sobre el Atlántico al noreste de Chile (Chile de día, sombra suave hacia el Pacífico)
bpy.ops.object.light_add(type="SUN")
sol = bpy.context.object; sol.data.energy = 2.6; sol.data.angle = math.radians(1.0)
d = xyz(-18.0, -42.0).normalized()
sol.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()

# --- contorno de Chile (curvas que se dibujan en "Chile")
anillos = json.load(open(os.path.join(HERE, "chile.json")))
cu = bpy.data.curves.new("ChileContorno", "CURVE"); cu.dimensions = "3D"
cu.bevel_resolution = 2
cu.bevel_factor_mapping_end = "SPLINE"
for r_ in anillos:
    if len(r_) < 12:
        continue
    s = cu.splines.new("POLY"); s.points.add(len(r_) - 1)
    for i, (lo, la) in enumerate(r_):
        p = xyz(la, lo, R * 1.0004)
        s.points[i].co = (p.x, p.y, p.z, 1.0)
    s.use_cyclic_u = True
contorno = bpy.data.objects.new("ChileContorno", cu); sc.collection.objects.link(contorno)
m, nt = nodos("contorno")
nt.nodes.remove(nt.nodes["Principled BSDF"])
em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = (1.0, 0.93, 0.72, 1); em.inputs[1].default_value = 3.0
trc = nt.nodes.new("ShaderNodeBsdfTransparent")
msc = nt.nodes.new("ShaderNodeMixShader"); msc.name = "alfa"; msc.inputs[0].default_value = 1.0
nt.links.new(trc.outputs[0], msc.inputs[1]); nt.links.new(em.outputs[0], msc.inputs[2])
nt.links.new(msc.outputs[0], nt.nodes["Material Output"].inputs[0])
cu.materials.append(m)
contorno.visible_shadow = False

# --- la zona roja en el lago: casquete rojo translúcido + anillo que late
def casquete(nombre, radio_km, r_in_km=0.0, n=96, alto=1.0006):
    rho, rin = radio_km / 6371.0, r_in_km / 6371.0
    c = xyz(*LAGO, R * alto); nn = c.normalized(); e1 = norte(*LAGO); e2 = nn.cross(e1)
    vs, fs = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        dirv = e1 * math.cos(a) + e2 * math.sin(a)
        for rr in ((rin, rho) if r_in_km else (rho,)):
            vs.append(tuple((nn * math.cos(rr) + dirv * math.sin(rr)) * R * alto))
    if r_in_km:
        fs = [(2 * i, 2 * i + 1, 2 * ((i + 1) % n) + 1, 2 * ((i + 1) % n)) for i in range(n)]
    else:
        vs.append(tuple(c)); fs = [(i, (i + 1) % n, n) for i in range(n)]
    me = bpy.data.meshes.new(nombre); me.from_pydata(vs, [], fs); me.update()
    o = bpy.data.objects.new(nombre, me); sc.collection.objects.link(o)
    o.visible_shadow = False
    return o


def mat_rojo(nombre, alfa, fuerza):
    m, nt = nodos(nombre)
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = (1.0, 0.03, 0.02, 1); em.inputs[1].default_value = fuerza
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    ms = nt.nodes.new("ShaderNodeMixShader"); ms.name = "mezcla"; ms.inputs[0].default_value = alfa
    nt.links.new(tr.outputs[0], ms.inputs[1]); nt.links.new(em.outputs[0], ms.inputs[2])
    nt.links.new(ms.outputs[0], nt.nodes["Material Output"].inputs[0])
    return m


zona = casquete("ZonaRoja", 16.0)
zona.data.materials.append(mat_rojo("zona", 0.62, 1.8))
borde = casquete("ZonaBorde", 16.0, 13.6)
borde.data.materials.append(mat_rojo("zona_borde", 1.0, 3.5))
pulso = casquete("ZonaPulso", 16.0, 14.5)
pulso.data.materials.append(mat_rojo("zona_pulso", 1.0, 3.0))
punto = casquete("ZonaPunto", 2.6)
punto.data.materials.append(mat_rojo("zona_punto", 1.0, 5.0))
for o in (zona, borde, pulso, punto):
    o.parent = None

# ---------------------------------------------------------------- cámara: interpolación suave (PCHIP) de lat, lon, log(altura) e inclinación
K = [  # t (s), lat, lon, altura (km), inclinación (°, la cámara se va al sur y mira al norte)
    (-0.8, -12.0, -36.0, 22000.0, 0.0),
    (0.0, -19.0, -55.0, 17500.0, 0.0),
    (1.0, -37.5, -71.0, 5000.0, 4.0),
    (1.62, -46.3, -72.9, 1500.0, 12.0),
    (2.55, -47.15, -73.22, 720.0, 20.0),
    (DUR + 0.2, -47.2, -73.25, 600.0, 23.0),
]


def pchip(xs, ys, x):
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    hk = np.diff(xs); dk = np.diff(ys) / hk
    m_ = np.zeros_like(ys)
    for i in range(1, len(ys) - 1):
        if dk[i - 1] * dk[i] > 0:
            w1, w2 = 2 * hk[i] + hk[i - 1], hk[i] + 2 * hk[i - 1]
            m_[i] = (w1 + w2) / (w1 / dk[i - 1] + w2 / dk[i])
    m_[0], m_[-1] = dk[0], dk[-1]
    i = int(np.clip(np.searchsorted(xs, x) - 1, 0, len(xs) - 2))
    t = (x - xs[i]) / hk[i]
    h00, h10, h01, h11 = 2 * t**3 - 3 * t**2 + 1, t**3 - 2 * t**2 + t, -2 * t**3 + 3 * t**2, t**3 - t**2
    return h00 * ys[i] + h10 * hk[i] * m_[i] + h01 * ys[i + 1] + h11 * hk[i] * m_[i + 1]


def pose(t):
    ts = [k[0] for k in K]
    la = pchip(ts, [k[1] for k in K], t)
    lo = pchip(ts, [k[2] for k in K], t)
    alt = math.exp(pchip(ts, [math.log(k[3]) for k in K], t)) / 1000.0
    inc = math.radians(pchip(ts, [k[4] for k in K], t))
    # desde Chile hacia el lago, el punto que se sigue queda arriba del centro (~23 % del alto): el lago y su zona roja
    # terminan sobre los subtítulos (la mira se corre al sur lo que mide ese 23 % a esa altura)
    w_ = suave((t - 1.15) / 0.7)
    la = la - w_ * 0.23 * 1.03 * alt * 1000.0 / 111.0
    T = xyz(la, lo); nn = T.normalized(); N_ = norte(la, lo)
    pos = T + (nn * math.cos(inc) - N_ * math.sin(inc)) * (alt / max(math.cos(inc), 0.3))
    f = (T - pos).normalized(); r_ = f.cross(N_).normalized(); u = r_.cross(f)
    M = Matrix((r_, u, -f)).transposed()
    return pos, M.to_quaternion(), alt


cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 35; cam_d.sensor_fit = "VERTICAL"; cam_d.sensor_height = 36
cam_d.clip_start = 0.002; cam_d.clip_end = 200
cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
cam.rotation_mode = "QUATERNION"


def pantalla(p):
    from bpy_extras.object_utils import world_to_camera_view
    v = world_to_camera_view(sc, cam, Vector(p))
    return [round(v.x * w), round((1 - v.y) * h), round(v.z, 3)]


def suave(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)


VOZ0 = float(os.environ.get("VOZ0", 0.10))          # la voz parte a los 0,10 s
T_CHILE, T_LAGO = VOZ0 + 0.72, VOZ0 + 1.34          # "Chile" y "lago" en la toma t1


def actualizar(f):
    t = (f - 1) / FPS
    pos, q, alt = pose(t)
    cam.location = pos; cam.rotation_quaternion = q
    bpy.context.view_layer.update()
    # contorno: se dibuja en "Chile" y queda fino (grosor constante en pantalla)
    cu.bevel_depth = 0.00085 * alt
    cu.bevel_factor_end = suave((t - (T_CHILE - 0.25)) / 0.55)
    alfa_c = 1.0 - suave((t - 1.8) / 0.55)          # cerca de Aysén el contorno de los fiordos ensucia: se va
    bpy.data.materials["contorno"].node_tree.nodes["alfa"].inputs[0].default_value = alfa_c
    contorno.hide_render = cu.bevel_factor_end <= 0.001 or alfa_c <= 0.01
    # zona roja: aparece en "lago" con un rebote y el anillo late
    k = (t - T_LAGO + 0.05) / 0.35
    s = 0.0 if k <= 0 else (1.0 + 0.25 * math.sin(min(k, 1.0) * math.pi)) * suave(k)
    for o in (zona, borde, punto):
        o.hide_render = s <= 0.01
        o.scale = (1, 1, 1)
    c = xyz(*LAGO)
    for o in (zona, borde, punto):
        o.matrix_world = Matrix.Translation(c) @ Matrix.Diagonal((s, s, s, 1)) @ Matrix.Translation(-c)
    ph = ((t - T_LAGO) % 0.7) / 0.7 if t > T_LAGO else -1
    pulso.hide_render = ph < 0
    if ph >= 0:
        sp_ = 1.0 + 1.6 * ph
        pulso.matrix_world = Matrix.Translation(c) @ Matrix.Diagonal((sp_, sp_, sp_, 1)) @ Matrix.Translation(-c)
        bpy.data.materials["zona_pulso"].node_tree.nodes["mezcla"].inputs[0].default_value = 1.0 - ph
    return {"t": round(t, 3), "alt_km": round(alt * 1000), "chile": pantalla(xyz(-35.0, -71.2)), "lago": pantalla(xyz(*LAGO))}


rng = os.environ.get("CUADROS", "").strip()
cuadros = range(1, N + 1)
if rng:
    a, b_ = (int(v) for v in rng.split("-"))
    cuadros = [f for f in cuadros if a <= f <= b_]
meta_p = os.path.join(DIR, "mapa_meta.json")
meta = json.load(open(meta_p)) if os.path.exists(meta_p) else {}
for f in cuadros:
    meta[str(f)] = actualizar(f)
    sc.frame_set(f)
    sc.render.filepath = os.path.join(DIR, f"{f:05d}.png")
    if not os.environ.get("SOLO_META"):
        bpy.ops.render.render(write_still=True)
json.dump(meta, open(meta_p, "w"))
print("ok mapa", len(list(cuadros)), "cuadros")
