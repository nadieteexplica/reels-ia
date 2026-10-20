"""Cuadro de estilo del plano 23 ("y si…"): la mejilla del ratón de perfil con una ventanita translúcida que deja ver
sus muelas moliendo semillas. Sin hueso, sin cráneo, sin cortar la piel: la piel se vuelve transparente en un círculo.
El borde punteado del recuadro y la ✕ se agregan en 2D (post)."""
import math, os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.abspath(os.path.join(HERE, "../../.."))
for p in (HERE, os.path.join(STUDIO, "plantilla")):
    sys.path.insert(0, p)
import bpy
from mathutils import Vector
import props as P
import personajes as PJ

OUT = os.environ.get("OUT", os.path.join(HERE, "out"))
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
res = tuple(int(v) for v in os.environ.get("RES", "720x1280").split("x"))
sc.render.engine = "CYCLES"
sc.cycles.device = os.environ.get("DEVICE", "CPU")
sc.cycles.samples = int(os.environ.get("SAMPLES", 64))
sc.cycles.use_denoising = True
sc.cycles.transparent_max_bounces = 16
sc.render.resolution_x, sc.render.resolution_y = res
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Punchy"
sc.world = bpy.data.worlds.new("Fondo")
sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.20, 0.42, 0.55, 1)
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.7
C = P.collection("Muelas")
rt = PJ.raton(C)
# de perfil: el ratón mira hacia -Y y la cámara lo ve desde +X
bpy.context.view_layer.update()
cab = rt["cabeza_malla"]
# párpados del color del lomo (de perfil, la máscara de guata los pintaba blancos)
lomo_m = PJ.mat_simple("LomoParpado", (0.42, 0.20, 0.08), rough=0.7, sheen=0.9)
for pv in rt["parpados"]:
    for ch in pv.children:
        ch.data.materials.clear()
        ch.data.materials.append(lomo_m)
# ventanita: en la mejilla, bajo el ojo y detrás del hocico, la piel pasa a ser transparente dentro de un círculo
# chico (coordenadas del objeto = mundo, el ratón se arma en el origen). Borde con un anillo crema para que se lea "ventana".
centro_loc = Vector((0.0165, -0.037, 0.131))   # delante del cuello (el cuello tapaba la muela de atrás)
R_VEN = float(os.environ.get("R_VEN", 0.0112))
m = cab.data.materials[0].copy()
m.name = "PelajeVentana"
nt = m.node_tree
b = nt.nodes["Principled BSDF"]
out = nt.nodes["Material Output"]
for nd in nt.nodes:                                    # de perfil la guata dejaba una franja blanca ojo→cuello: se acota
    if nd.type == "MAP_RANGE" and abs(nd.inputs["From Min"].default_value - 0.72) < 1e-6:
        nd.inputs["From Min"].default_value = 0.86
tc = nt.nodes.new("ShaderNodeTexCoord")
# distancia en el plano Y-Z (la cámara mira desde +X): cilindro, así el círculo se ve redondo
sep = nt.nodes.new("ShaderNodeSeparateXYZ")
nt.links.new(tc.outputs["Object"], sep.inputs[0])
comb = nt.nodes.new("ShaderNodeCombineXYZ")
nt.links.new(sep.outputs["Y"], comb.inputs["Y"])
nt.links.new(sep.outputs["Z"], comb.inputs["Z"])
dist = nt.nodes.new("ShaderNodeVectorMath")
dist.operation = "DISTANCE"
dist.inputs[1].default_value = (0, centro_loc.y, centro_loc.z)
nt.links.new(comb.outputs["Vector"], dist.inputs[0])
# sólo el lado que mira a la cámara (x > 0): el otro lado de la cabeza queda con piel
lado = nt.nodes.new("ShaderNodeMath")
lado.operation = "GREATER_THAN"
lado.inputs[1].default_value = 0.004
nt.links.new(sep.outputs["X"], lado.inputs[0])
dentro_c = nt.nodes.new("ShaderNodeMapRange")          # 1 dentro de la ventana, 0 fuera
dentro_c.inputs["From Min"].default_value = R_VEN
dentro_c.inputs["From Max"].default_value = R_VEN * 0.62
dentro_c.inputs["To Max"].default_value = 0.92          # la piel no desaparece del todo: se ve "de vidrio"
nt.links.new(dist.outputs["Value"], dentro_c.inputs["Value"])
anillo_a = nt.nodes.new("ShaderNodeMapRange")          # 1 dentro del borde exterior del anillo
anillo_a.inputs["From Min"].default_value = R_VEN * 1.10
anillo_a.inputs["From Max"].default_value = R_VEN * 1.02
anillo_a.inputs["To Max"].default_value = float(os.environ.get("ANILLO", 0.75))   # anillo fino crema: se lee "ventana" y no hoyo
nt.links.new(dist.outputs["Value"], anillo_a.inputs["Value"])
ven = nt.nodes.new("ShaderNodeMath"); ven.operation = "MULTIPLY"
nt.links.new(dentro_c.outputs["Result"], ven.inputs[0]); nt.links.new(lado.outputs[0], ven.inputs[1])
ani = nt.nodes.new("ShaderNodeMath"); ani.operation = "MULTIPLY"
nt.links.new(anillo_a.outputs["Result"], ani.inputs[0]); nt.links.new(lado.outputs[0], ani.inputs[1])
transp = nt.nodes.new("ShaderNodeBsdfTransparent")
transp.inputs["Color"].default_value = (1.0, 0.97, 0.95, 1)
borde = nt.nodes.new("ShaderNodeBsdfPrincipled")
borde.inputs["Base Color"].default_value = (0.98, 0.93, 0.82, 1)
borde.inputs["Roughness"].default_value = 0.35
borde.inputs["Coat Weight"].default_value = 0.6
mix1 = nt.nodes.new("ShaderNodeMixShader")             # piel → anillo
nt.links.new(ani.outputs[0], mix1.inputs["Fac"])
nt.links.new(b.outputs[0], mix1.inputs[1])
nt.links.new(borde.outputs[0], mix1.inputs[2])
mix2 = nt.nodes.new("ShaderNodeMixShader")             # → transparente dentro
nt.links.new(ven.outputs[0], mix2.inputs["Fac"])
nt.links.new(mix1.outputs[0], mix2.inputs[1])
nt.links.new(transp.outputs[0], mix2.inputs[2])
nt.links.new(mix2.outputs[0], out.inputs["Surface"])
cab.data.materials.clear()
cab.data.materials.append(m)
# interior: todo cabe dentro de la cabeza (x 0.000–0.012) y dentro del círculo de la ventana
diente = P.mat("Muela", (0.97, 0.94, 0.86), rough=0.22, coat=0.6, emit=float(os.environ.get("BRILLO", 0.12)))
encia = P.mat("Encia", (0.82, 0.34, 0.40), rough=0.5, sss=0.4)
semilla = P.mat("Semilla", (0.95, 0.76, 0.36), rough=0.45)
miga_m = P.mat("Miga", (0.92, 0.70, 0.34), rough=0.6)
M = cab.matrix_world
X_M = 0.0070                                           # plano de las muelas, bien adentro de la piel
# fondo del interior: una cápsula oscura (azul noche, como la "cabeza de vidrio") que tapa el revés de la piel
fondo_m = P.mat("InteriorFondo", (0.03, 0.05, 0.10), rough=0.8)
cavidad = P.prim("sphere", "MejillaDentro", C, fondo_m, r=1.0)
cavidad.scale = (0.0040, 0.0150, 0.0100)   # cabe entera dentro de la mejilla (no asoma bajo el mentón)
cavidad.location = Vector((0.0005, centro_loc.y, centro_loc.z))
def muela(name, centro, ancho, alto, arriba):
    """Muela de roedor: corona redondeada con 4 cúspides (una sola malla orgánica)."""
    cx, cy, cz = centro
    sg = -1 if arriba else 1                          # las cúspides miran hacia la otra fila
    el = [((cx, cy, cz), (ancho * 0.42, ancho * 0.50, alto * 0.50), (0, 0, 0))]
    for dy in (-1, 1):
        for dx in (-1, 1):
            el.append(((cx + dx * ancho * 0.16, cy + dy * ancho * 0.22, cz + sg * alto * 0.42), (ancho * 0.20, ancho * 0.22, alto * 0.24), (0, 0, 0)))
    ob = PJ.blob(name, el, C, voxel=0.00018, suave=6)
    ob.data.materials.append(diente)
    return ob
ANCHO, ALTO, GAP = 0.0047, 0.0040, 0.0020
for fila, arriba in (("sup", True), ("inf", False)):
    zc = centro_loc.z + (1 if arriba else -1) * (GAP / 2 + ALTO / 2)
    zg = zc + (1 if arriba else -1) * (ALTO / 2 + 0.0006)
    base = PJ.blob(f"Encia_{fila}", [((X_M - 0.0008, centro_loc.y, zg), (0.0028, 0.0085, 0.0020), (0, 0, 0))], C, voxel=0.0002, suave=4)
    base.data.materials.append(encia)
    for k in range(3):
        muela(f"Muela_{fila}{k}", (X_M, centro_loc.y - ANCHO * 1.05 + ANCHO * 1.05 * k, zc), ANCHO, ALTO, arriba)
rnd = random.Random(1)
# semillas enteras entrando por delante (hacia el hocico) y migas saliendo por detrás, entre las dos filas
for k in range(2):
    g = P.prim("sphere", f"Semilla{k}", C, semilla, r=0.0024)
    g.scale = (0.55, 1.15, 0.42)
    g.location = Vector((X_M + 0.0008, centro_loc.y - 0.0072 + 0.0030 * k, centro_loc.z))
    g.rotation_euler.x = math.radians(rnd.uniform(-20, 20))
for k in range(10):
    g = P.prim("ico", f"Miga{k}", C, miga_m, r=rnd.uniform(0.00045, 0.0008), sub=1)
    g.location = Vector((X_M + 0.0010, centro_loc.y + 0.0030 + rnd.uniform(0, 0.0055), centro_loc.z + rnd.uniform(-0.0007, 0.0007)))
luz_in = bpy.data.lights.new("LuzMejilla", "POINT")
luz_in.energy, luz_in.color, luz_in.shadow_soft_size = 0.04, (1.0, 0.88, 0.78), 0.004
lo_in = bpy.data.objects.new("LuzMejilla", luz_in)
sc.collection.objects.link(lo_in)
lo_in.location = M @ Vector((0.013, centro_loc.y - 0.002, centro_loc.z + 0.004))
L = bpy.data.lights.new("Key", "AREA")
L.energy, L.size = 25, 0.5
lo = bpy.data.objects.new("Key", L)
sc.collection.objects.link(lo)
lo.location = (0.6, -0.5, 0.6)
lo.rotation_euler = (Vector((0, 0, 0.13)) - lo.location).to_track_quat("-Z", "Y").to_euler()
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
sc.collection.objects.link(cam)
sc.camera = cam
cam.data.lens = 65
cam.data.sensor_fit = "VERTICAL"
cam.data.sensor_height = 24
tgt = M @ (centro_loc + Vector((0.0, float(os.environ.get("TGT_Y", -0.012)), float(os.environ.get("TGT_Z", 0.010)))))
cam.location = tgt + Vector(tuple(float(x) for x in os.environ.get("CAMOFF", "0.36,-0.03,0.02").split(",")))
cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.filepath = os.path.join(OUT, os.environ.get("NOMBRE", "estilo_muelas") + ".png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath)
