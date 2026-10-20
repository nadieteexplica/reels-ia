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
sc.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.82, 0.55, 0.32, 1)
sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.7
C = P.collection("Muelas")
rt = PJ.raton(C)
# de perfil: el ratón mira hacia -Y y la cámara lo ve desde +X
bpy.context.view_layer.update()
cab = rt["cabeza_malla"]
# ventanita: en la mejilla, la piel pasa a ser casi transparente dentro de un círculo (coordenadas del objeto)
centro_loc = Vector((0.020, -0.040, 0.138))          # mejilla izquierda del ratón (lado que mira a la cámara)
m = cab.data.materials[0].copy()
m.name = "PelajeVentana"
nt = m.node_tree
b = nt.nodes["Principled BSDF"]
out = nt.nodes["Material Output"]
tc = nt.nodes.new("ShaderNodeTexCoord")
dist = nt.nodes.new("ShaderNodeVectorMath")
dist.operation = "DISTANCE"
dist.inputs[1].default_value = centro_loc
nt.links.new(tc.outputs["Object"], dist.inputs[0])
mr = nt.nodes.new("ShaderNodeMapRange")
mr.inputs["From Min"].default_value = 0.0150
mr.inputs["From Max"].default_value = 0.0185
nt.links.new(dist.outputs["Value"], mr.inputs["Value"])
vid = nt.nodes.new("ShaderNodeBsdfGlass")
vid.inputs["Roughness"].default_value = 0.05
vid.inputs["IOR"].default_value = 1.05
vid.inputs["Color"].default_value = (1.0, 0.92, 0.88, 1)
mix = nt.nodes.new("ShaderNodeMixShader")
nt.links.new(mr.outputs["Result"], mix.inputs["Fac"])
nt.links.new(vid.outputs[0], mix.inputs[1])
nt.links.new(b.outputs[0], mix.inputs[2])
nt.links.new(mix.outputs[0], out.inputs["Surface"])
cab.data.materials.clear()
cab.data.materials.append(m)
# muelas y semillas dentro (en coordenadas de la cabeza)
diente = P.mat("Muela", (0.95, 0.92, 0.84), rough=0.3, coat=0.4)
encia = P.mat("Encia", (0.75, 0.30, 0.35), rough=0.5, sss=0.4)
semilla = P.mat("Semilla", (0.92, 0.80, 0.50), rough=0.5)
M = cab.matrix_world
for fila, dz in (("sup", 0.006), ("inf", -0.006)):
    base = P.prim("cube", f"Encia_{fila}", C, encia)
    base.scale = (0.006, 0.030, 0.004)
    base.location = M @ (centro_loc + Vector((-0.008, 0.0, dz * 2.1)))
    for k in range(3):
        d = P.prim("cube", f"Muela_{fila}{k}", C, diente)
        d.scale = (0.0055, 0.0075, 0.0055)
        d.location = M @ (centro_loc + Vector((-0.008, -0.009 + 0.009 * k, dz)))
        P.bevel(d, 0.0022, 4)
# interior de la mejilla: fondo rosado iluminado (no un hueco oscuro)
dentro = P.prim("sphere", "MejillaDentro", C, P.mat("MejillaDentro", (0.85, 0.40, 0.42), rough=0.6, sss=0.5, emit=0.25), r=0.017)
dentro.location = M @ (centro_loc + Vector((-0.033, 0.0, 0.0)))
luz_in = bpy.data.lights.new("LuzMejilla", "POINT")
luz_in.energy, luz_in.color, luz_in.shadow_soft_size = 0.05, (1.0, 0.85, 0.75), 0.005
lo_in = bpy.data.objects.new("LuzMejilla", luz_in)
sc.collection.objects.link(lo_in)
lo_in.location = M @ (centro_loc + Vector((0.004, -0.004, 0.006)))
rnd = random.Random(1)
for k in range(5):      # semillas enteras entrando por un lado y migas saliendo por el otro
    entera = k < 2
    g = P.prim("sphere", f"Semilla{k}", C, semilla, r=0.0034 if entera else 0.0016)
    g.scale = (1.0, 1.3, 0.45) if entera else (1, 1, 1)
    g.location = M @ (centro_loc + Vector((-0.002, -0.014 + 0.007 * k, rnd.uniform(-0.0012, 0.0012))))
for k in range(10):
    g = P.prim("ico", f"Miga{k}", C, semilla, r=0.0011, sub=1)
    g.location = M @ (centro_loc + Vector((-0.002 + rnd.uniform(-0.002, 0.002), 0.008 + rnd.uniform(0, 0.008), rnd.uniform(-0.004, 0.004))))
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
tgt = M @ (centro_loc + Vector((0.0, 0.0, 0.004)))
cam.location = tgt + Vector((0.42, 0.0, 0.04))
cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.filepath = os.path.join(OUT, os.environ.get("NOMBRE", "estilo_muelas") + ".png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath)
