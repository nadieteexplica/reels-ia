"""Escena del corte (a medida): el terreno partido frente a la escuela para ver cómo le meten las patas.

Fases (0..1 cada una, las da el plano): cavar (la tierra bajo el edificio baja y aparecen las columnas viejas),
patas (aparecen de a una, contador 1→198), cortar (chispas en las columnas y desaparecen), alzar (las patas se estiran).
El corte está en y = -7,2 (justo delante de la fachada); la cámara mira desde -y a la altura del suelo.
"""
import math, random
import bpy
from mathutils import Vector
import props as P
from edificio import _caja, _nodo, Edificio, recta

FOSO = 3.6     # profundidad de la excavación (m)


def mat_corte_tierra():
    """Cara del corte: capas horizontales con borde nítido (tierra vegetal, arcilla, arena, ripio) y piedritas."""
    m = bpy.data.materials.get("CorteTierra")
    if m:
        return m
    m = bpy.data.materials.new("CorteTierra")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    geo = _nodo(nt, "ShaderNodeNewGeometry", -1200, 0)        # posición en el mundo: las capas siguen la altura real
    sep = _nodo(nt, "ShaderNodeSeparateXYZ", -1000, 100)
    nt.links.new(geo.outputs["Position"], sep.inputs[0])
    noi = _nodo(nt, "ShaderNodeTexNoise", -1000, -150, Scale=0.25, Detail=3.0)
    nt.links.new(geo.outputs["Position"], noi.inputs["Vector"])
    ond = _nodo(nt, "ShaderNodeMath", -800, -150)
    ond.operation = "MULTIPLY_ADD"
    ond.inputs[1].default_value = 0.9
    ond.inputs[2].default_value = -0.45
    nt.links.new(noi.outputs["Fac"], ond.inputs[0])
    zz = _nodo(nt, "ShaderNodeMath", -650, 100)
    zz.operation = "ADD"
    nt.links.new(sep.outputs["Z"], zz.inputs[0])
    nt.links.new(ond.outputs[0], zz.inputs[1])
    mr = _nodo(nt, "ShaderNodeMapRange", -500, 100)
    mr.inputs["From Min"].default_value = -12.0
    mr.inputs["From Max"].default_value = 0.0
    nt.links.new(zz.outputs[0], mr.inputs["Value"])
    ramp = _nodo(nt, "ShaderNodeValToRGB", -300, 100)
    cr = ramp.color_ramp
    cr.interpolation = "CONSTANT"
    cr.elements[0].position = 0.0
    cr.elements[0].color = (0.50, 0.42, 0.33, 1)          # ripio (lo más hondo, bajo 8 m)
    cr.elements[1].position = 0.90
    cr.elements[1].color = (0.22, 0.13, 0.07, 1)          # tierra vegetal oscura (el primer metro)
    for pos, col in ((0.33, (0.66, 0.51, 0.32)), (0.62, (0.56, 0.31, 0.15))):   # arena · arcilla
        e = cr.elements.new(pos)
        e.color = (*col, 1)
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    vor = _nodo(nt, "ShaderNodeTexVoronoi", -500, -250, Scale=3.0)
    nt.links.new(geo.outputs["Position"], vor.inputs["Vector"])
    piedra = _nodo(nt, "ShaderNodeMath", -300, -250)
    piedra.operation = "LESS_THAN"
    piedra.inputs[1].default_value = 0.12
    nt.links.new(vor.outputs["Distance"], piedra.inputs[0])
    var = _nodo(nt, "ShaderNodeTexNoise", -500, -450, Scale=1.4, Detail=6.0)
    nt.links.new(geo.outputs["Position"], var.inputs["Vector"])
    mul = _nodo(nt, "ShaderNodeMix", -200, 250)
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs["Factor"].default_value = 0.35
    nt.links.new(ramp.outputs["Color"], mul.inputs[6])
    nt.links.new(var.outputs["Fac"], mul.inputs[7])
    mix = _nodo(nt, "ShaderNodeMix", -100, 100)
    mix.data_type = "RGBA"
    mix.inputs[7].default_value = (0.30, 0.27, 0.23, 1)
    nt.links.new(piedra.outputs[0], mix.inputs["Factor"])
    nt.links.new(mul.outputs[2], mix.inputs[6])
    nt.links.new(mix.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.95
    b.inputs["Specular IOR Level"].default_value = 0.2
    bump = _nodo(nt, "ShaderNodeBump", -100, -250, Strength=0.5, Distance=0.04)
    nt.links.new(piedra.outputs[0], bump.inputs["Height"])
    nt.links.new(bump.outputs[0], b.inputs["Normal"])
    return m


class Corte:
    def __init__(self, sc, ed=None):
        self.coll = P.collection("Corte")
        c = self.coll
        tierra = mat_corte_tierra()
        # el terreno delante del corte (cara visible en y = -7,2) y a los lados/atrás del foso
        _caja("TerrenoFondo", -120, 120, 30.5, 60, -30.0, 0.0, c, tierra)
        _caja("TerrenoIzq", -120, -24.5, -7.2, 30.5, -30.0, 0.0, c, tierra)
        _caja("TerrenoDer", 24.5, 120, -7.2, 30.5, -30.0, 0.0, c, tierra)
        _caja("FondoFoso", -24.5, 24.5, -7.2, 30.5, -30.0, -FOSO, c, tierra)
        # la tierra que se saca (baja de 0 a -FOSO)
        self.relleno = _caja("Relleno", -24.4, 24.4, -7.1, 30.4, -FOSO, 0.0, c, tierra)
        self.relleno.data.transform(__import__("mathutils").Matrix.Translation((0, 0, FOSO / 2)))
        self.relleno.location.z = -FOSO
        # columnas y zapatas viejas (cada 4 m, entre las patas)
        horm = P.mat("Hormigon", (0.42, 0.42, 0.41), rough=0.85)
        self.columnas = []
        rnd = random.Random(2)
        for (x0, x1, y0, y1) in [(-22, 22, -6, 6), (-6, 6, 6, 28)]:
            x = x0 + 2.0                 # columnas entre las patas (las patas van en x impares, -21, -19…)
            while x < x1 - 1:
                y = y0 + 2.0
                while y < y1 - 1:
                    if True:
                        col = _caja("Columna", x - 0.35, x + 0.35, y - 0.35, y + 0.35, -FOSO + 0.4, 0.0, c, horm)
                        zap = _caja("Zapata", x - 0.9, x + 0.9, y - 0.9, y + 0.9, -FOSO, -FOSO + 0.4, c, horm)
                        self.columnas.append((col, zap, Vector((x, y, -0.15))))
                    y += 4.0
                x += 4.0
        # chispas (malla de emisión que se enciende en la base del edificio)
        self.chispa_m = P.mat("Chispa", (1.0, 0.65, 0.15), emit=40.0)
        self.chispas = []
        for k in range(10):
            ch = P.prim("ico", f"Chispa{k}", c, self.chispa_m, sub=1, r=0.06)
            ch.hide_render = True
            self.chispas.append(ch)
        self.ed = ed or Edificio(sc)
        # todo lo de la calle que queda delante del corte o bajo el suelo se esconde (el mundo termina en y = -7,2)
        for ob in bpy.data.objects:
            if ob.name.startswith(("SueloObra", "Pavimento", "Cono", "Huella", "Monton", "Oficina", "VigaPila", "RejaIzq", "RejaDer", "Plancha", "Piedra", "Charco")):
                ob.hide_render = True

    def poner(self, f, cavar, patas, cortar, alzar, rnd_seed=0):
        """cavar, patas, cortar, alzar en 0..1."""
        rel = self.relleno
        rel.scale.z = max(0.001, 1 - cavar)
        rel.hide_render = cavar >= 0.999
        n = int(round(198 * patas))
        # el edificio: antes de alzar, el marco apoyado sobre las columnas (z cuerpo = 0)
        lift = 2.2 * alzar
        self.ed.poner(0.0, recta(0, 0, 0), alto=FOSO - 0.7 + lift, visibles=n, sin_pasos=True, suelo=-FOSO, marco=patas > 0)
        # columnas: se cortan (desaparecen de a grupos durante "cortar")
        rnd = __import__("random").Random(5)
        for i, (col, zap, p) in enumerate(self.columnas):
            umbral = (i * 0.618) % 1.0
            col.hide_render = cortar > umbral
        # chispas en las columnas que se están cortando
        activos = [p for i, (col, zap, p) in enumerate(self.columnas) if abs(cortar - (i * 0.618) % 1.0) < 0.08 and 0 < cortar < 1]
        r = __import__("random").Random(f)
        for k, ch in enumerate(self.chispas):
            if activos and k < 3 * len(activos[:3]):
                p = activos[k % len(activos[:3])]
                ch.hide_render = False
                ch.location = p + Vector((r.uniform(-0.6, 0.6), r.uniform(-0.6, 0.6), r.uniform(-0.3, 0.5)))
                ch.scale = (1 + r.random(),) * 3
            else:
                ch.hide_render = True
        return n
