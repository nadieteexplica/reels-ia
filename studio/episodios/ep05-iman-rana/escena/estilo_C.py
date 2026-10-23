"""Cuadro de estilo C (Ep. 5, mecánica): adentro de la rana, el agua. Moléculas de agua (con su ángulo real) entre células
del tejido; las líneas del imán suben desde abajo y cada molécula recibe un empujoncito hacia arriba (flechas naranjas).
Las líneas y las flechas son capa de explicación (estilizada); el mundo (moléculas, tejido, luz, lente) es realista."""
import math, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bpy
from mathutils import Vector
import ep05 as E

w, h = (int(v) for v in os.environ.get("RES", "1080x1920").split("x"))
out = os.environ.get("OUT", os.path.join(HERE, "out")); os.makedirs(out, exist_ok=True)
sc = E.escena("EstiloC", (w, h), int(os.environ.get("SAMPLES", 64)))
w_ = E.mundo(sc, "studio.hdr", 0.05)
bg = w_.node_tree.nodes["Background"]
# fondo: el interior húmedo y rojizo de la rana (un poco de color en el mundo)
mix = w_.node_tree.nodes.new("ShaderNodeMixRGB"); mix.blend_type = "MULTIPLY"; mix.inputs[0].default_value = 1.0
mix.inputs[2].default_value = (0.5, 0.12, 0.1, 1)
env = bg.inputs[0].links[0].from_node
w_.node_tree.links.new(env.outputs[0], mix.inputs[1]); w_.node_tree.links.new(mix.outputs[0], bg.inputs[0])
mats = (E.mat_molecula("oxigeno", (0.78, 0.07, 0.05)), E.mat_molecula("hidrogeno", (0.92, 0.93, 0.95), 0.12))
random.seed(11)
mols = []
for i in range(70):
    p = Vector((random.uniform(-3.2, 3.2), random.uniform(-1.5, 9.0), random.uniform(-2.5, 6.5)))
    if p.y < 0.4 and abs(p.x) < 0.9 and 0.8 < p.z < 3.2:
        continue
    mols.append(E.molecula_agua(sc, p, (random.uniform(0, 6.3), random.uniform(0, 6.3), random.uniform(0, 6.3)), 0.55, mats, f"H2O_{i}"))
heroe = E.molecula_agua(sc, (0.0, 0.0, 1.9), (math.radians(20), math.radians(-25), math.radians(35)), 1.0, mats, "H2O_heroe")
E.tejido(sc)
# líneas del campo: suben desde abajo y se abren (capa de explicación)
for i, x in enumerate((-2.4, -1.3, -0.4, 0.5, 1.4, 2.5)):
    y = 1.5 + 0.6 * (i % 3)
    pts = [(x * 0.35, y, -4.0), (x * 0.5, y, -1.0), (x * 0.8, y, 2.0), (x * 1.3, y, 5.0), (x * 2.0, y, 8.0)]
    E.linea_campo(sc, f"campo{i}", pts, 0.012, (0.15, 0.75, 1.0), 1.6)
# empujón: una flecha grande en la molécula héroe y flechas chicas en las cercanas
E.flecha(sc, "empujon_heroe", (0.0, 0.0, 2.75), 1.1, 0.055)
for m in mols:
    if m.location.y < 4.5 and abs(m.location.x) < 3:
        E.flecha(sc, f"emp_{m.name}", tuple(m.location + Vector((0, 0, 0.35))), 0.5, 0.025, fuerza=1.8)
E.luz_area(sc, "Llave", (-3.5, -4.0, 6.0), (0, 0, 1.9), 900, (1.0, 0.9, 0.82), 2.5)
E.luz_area(sc, "Contra", (2.5, 4.0, 4.5), (0, 0, 1.9), 600, (0.5, 0.8, 1.0), 1.5)
E.luz_punto(sc, "Brillo_abajo", (0, 1.5, -2.0), 300, (0.25, 0.8, 1.0), 1.0)
pos = Vector((1.3, -8.8, 2.7))
E.camara(sc, pos, Vector((0.0, 0.0, 2.1)), lente=50, fstop=2.2, foco=(Vector((0, 0, 1.9)) - pos).length)
sc.render.filepath = os.path.join(out, os.environ.get("NOMBRE", "estilo_C_HD") + ".png")
bpy.ops.render.render(write_still=True)
print("ok", sc.render.filepath)
