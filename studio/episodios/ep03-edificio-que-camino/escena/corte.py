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
    m = bpy.data.materials.get("CorteTierra")
    if m:
        return m
    m = bpy.data.materials.new("CorteTierra")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = _nodo(nt, "ShaderNodeTexCoord", -1000, 0)
    wave = _nodo(nt, "ShaderNodeTexWave", -750, 100, Scale=0.45, Distortion=0.8, Detail=2.0)
    wave.bands_direction = "Z"
    nt.links.new(tc.outputs["Object"], wave.inputs["Vector"])
    ramp = _nodo(nt, "ShaderNodeValToRGB", -500, 100)
    cr = ramp.color_ramp
    cr.elements[0].color = (0.33, 0.19, 0.09, 1)
    cr.elements[1].color = (0.50, 0.33, 0.17, 1)
    e = cr.elements.new(0.5)
    e.color = (0.44, 0.27, 0.13, 1)
    nt.links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    noi = _nodo(nt, "ShaderNodeTexNoise", -750, -200, Scale=3.0, Detail=8.0)
    nt.links.new(tc.outputs["Object"], noi.inputs["Vector"])
    mix = _nodo(nt, "ShaderNodeMix", -250, 100)
    mix.data_type = "RGBA"
    mix.blend_type = "OVERLAY"
    mix.inputs["Factor"].default_value = 0.4
    nt.links.new(ramp.outputs["Color"], mix.inputs[6])
    nt.links.new(noi.outputs["Color"], mix.inputs[7])
    nt.links.new(mix.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.95
    bump = _nodo(nt, "ShaderNodeBump", -250, -250, Strength=0.6, Distance=0.08)
    nt.links.new(noi.outputs["Fac"], bump.inputs["Height"])
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
        horm = P.mat("Hormigon", (0.55, 0.54, 0.52), rough=0.85)
        self.columnas = []
        rnd = random.Random(2)
        for (x0, x1, y0, y1) in [(-22, 22, -6, 6), (-6, 6, 6, 28)]:
            x = x0 + 1.0
            while x < x1:
                y = y0 + 1.0
                while y < y1:
                    if (round(x) // 2 + round(y) // 2) % 2 == 0:
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
            if ob.name.startswith(("SueloObra", "Pavimento", "Cono", "Huella", "Monton", "Oficina", "VigaPila", "RejaIzq", "RejaDer")):
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
