"""Movimientos de los personajes del Ep. 2 (sin keyframes: cada función deja la pose de un cuadro)."""
import math, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.abspath(os.path.join(HERE, "../../.."))
for p in (HERE, os.path.join(STUDIO, "plantilla")):
    if p not in sys.path:
        sys.path.insert(0, p)
import bpy
from mathutils import Vector, Euler, Matrix
import props as P
import personajes as PJ
import vfx as V
import ep02 as E2

R = math.radians


# ---------------- ratón ----------------
def cara_roja_animable(rt, lomo=(0.62, 0.07, 0.04), guata=(0.95, 0.52, 0.48)):
    """La cabeza del ratón pasa de su color al rojo de picante con un valor 0..1 (sin cambio de golpe).
    Devuelve una función poner(x)."""
    cab = rt["cabeza_malla"]
    base = cab.data.materials[0]
    m = base.copy()
    m.name = rt["nombre"] + "_pelaje_cara"
    nt = m.node_tree
    mix = [n for n in nt.nodes if n.type == "MIX" and getattr(n, "data_type", "") == "RGBA"][0]
    val = nt.nodes.new("ShaderNodeValue")
    val.outputs[0].default_value = 0.0
    for sock, rojo in (("A", lomo), ("B", guata)):
        orig = tuple(mix.inputs[sock].default_value)
        mm = nt.nodes.new("ShaderNodeMix")
        mm.data_type = "RGBA"
        mm.inputs["A"].default_value = orig
        mm.inputs["B"].default_value = (*rojo, 1)
        nt.links.new(val.outputs[0], mm.inputs["Factor"])
        nt.links.new(mm.outputs["Result"], mix.inputs[sock])
    cab.data.materials[0] = m

    def poner(x):
        val.outputs[0].default_value = E2.clamp(x)
    return poner


def parpados(pivotes, grados):
    """0 = cerrado · -30 media asta · -100 abierto · -115 muy abierto."""
    for pv in pivotes:
        for ch in pv.children:
            ch.rotation_euler.x = R(grados)


def parpadeo(f, f_parpadeo, base, dur=5):
    """Ángulo del párpado con un parpadeo que empieza en f_parpadeo (cierra y abre en `dur` cuadros)."""
    x = (f - f_parpadeo) / dur
    if 0 <= x <= 1:
        return base * (1 - math.sin(math.pi * x))
    return base


def mirar_a(pivote, punto, cuanto=1.0, limite=60):
    """Gira un pivote (cabeza) para que su -Y local apunte a `punto` (fracción `cuanto`, sin pasar de `limite` grados)."""
    padre = pivote.parent
    Mp = padre.matrix_world if padre else Matrix()
    loc_w = (Mp @ pivote.matrix_parent_inverse @ Matrix.Translation(pivote.location)).translation
    d = (Mp.inverted().to_3x3() @ (Vector(punto) - loc_w)).normalized()
    yaw = math.atan2(d.x, -d.y)
    pitch = -math.atan2(d.z, Vector((d.x, d.y)).length)      # rotar +X baja la cara (-Y): mirar hacia arriba es negativo
    yaw = max(-R(limite), min(R(limite), yaw)) * cuanto
    pitch = max(-R(limite), min(R(limite), pitch)) * cuanto
    return Euler((pitch, 0, yaw), "XYZ")


# ---------------- llama ----------------
class Llama:
    """La llama única del video (vfx.llamarada) con su parpadeo. f = cuadro de "fase" (el mismo f da la misma forma)."""

    def __init__(self, nombre=None, origen=None, direccion=None, coll=None, escala=1.7, seed=3, root=None):
        self.root = root or V.llamarada(nombre, origen, direccion, coll, escala=escala, seed=seed)
        nombre = self.root.name
        self.escala = escala
        self.hijos = []
        for ch in self.root.children:
            self.hijos.append((ch, ch.location.copy(), ch.rotation_euler.copy(), ch.scale.copy()))
        self.luz = bpy.data.objects.get(nombre + "_luz")
        self.luz_e = self.luz.data.energy if self.luz else 0
        self.base_rot = self.root.rotation_euler.copy()

    def poner(self, f, tam=1.0, doblar=0.0, lado=0.0):
        """tam: 0..1 (0 = apagada) · doblar: grados que la llama se dobla hacia arriba · lado: grados hacia el costado
        (sale por la comisura: la cara queda a la vista cuando el ratón mira a cámara)."""
        vis = tam > 0.02
        E2.oculto(self.root, not vis)
        if not vis:
            return
        s = tam * (1 + 0.06 * E2.ruido(f, 1, 1.6))
        self.root.scale = (s, s, s * (1 + 0.08 * E2.ruido(f, 2, 2.1)))
        self.root.rotation_euler = self.base_rot.copy()
        self.root.rotation_euler.rotate_axis("Y", R(lado))
        self.root.rotation_euler.rotate_axis("X", R(-doblar))
        for i, (ch, loc, rot, sca) in enumerate(self.hijos):
            if "_chispa" in ch.name:
                # chispas: suben y vuelven a empezar (ciclo de 18 cuadros, desfasadas)
                ph = ((f + i * 7) % 18) / 18
                ch.location = loc + Vector((0.004 * math.sin(ph * 6 + i), 0.02 * ph * self.escala, 0.03 * ph * self.escala))
                ch.scale = sca * (1 - ph) if ph > 0.7 else sca
                continue
            if ch.type == "LIGHT":
                continue
            ch.rotation_euler = Euler((rot.x + 0.10 * E2.ruido(f, 10 + i, 1.9), rot.y + 0.12 * E2.ruido(f, 30 + i, 1.5), rot.z))
            k = 1 + 0.10 * E2.ruido(f, 50 + i, 2.3)
            ch.scale = (sca.x * (2 - k) ** 0.5, sca.y * (2 - k) ** 0.5, sca.z * k)
        if self.luz:
            self.luz.data.energy = self.luz_e * tam * (0.9 + 0.1 * E2.ruido(f, 7, 3))


class Bocanada:
    """Bocanada de humo de dibujo animado (bolitas grises que suben, crecen y se achican al final)."""

    def __init__(self, nombre, origen, direccion, coll, n=6, tam=0.012, seed=4):
        rnd = random.Random(seed)
        m = bpy.data.materials.get("HumoBocanada")
        if not m:
            m = P.mat("HumoBocanada", (0.86, 0.84, 0.82), rough=0.9, alpha=0.55)
            m.node_tree.nodes["Principled BSDF"].inputs["Transmission Weight"].default_value = 0.2
        self.bolas = []
        for k in range(n):
            b = P.prim("ico", f"{nombre}{k}", coll, m, r=1.0, sub=3)
            off = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))) * tam * 0.6
            self.bolas.append((b, off, rnd.uniform(0.7, 1.3), k / n * 0.35))
            b.hide_render = True
        self.o = Vector(origen)
        self.d = Vector(direccion).normalized()
        self.tam = tam

    def poner(self, x):
        """x: 0 (sale) → 1 (se disipó)."""
        for b, off, s, retraso in self.bolas:
            t = E2.clamp((x - retraso) / (1 - retraso))
            vis = 0 < t < 1
            b.hide_render = not vis
            if not vis:
                continue
            r = self.tam * s * (0.3 + 1.4 * E2.sale(t)) * (1 - E2.entra(E2.clamp((t - 0.6) / 0.4)))
            b.scale = (r, r, r)
            b.location = self.o + off + self.d * (self.tam * 4 * E2.sale(t)) + Vector((0, 0, self.tam * 5 * t))


# ---------------- pájaro ----------------
class Bulto:
    """Bulto que baja por el cuello al tragar ("glup"): una esfera del color de las plumas que sale apenas de la
    superficie del cuello y baja de la garganta al pecho."""

    def __init__(self, pj, coll, r=0.016):
        m = pj["cuerpo"].data.materials[0]
        self.b = P.prim("sphere", pj["root"].name + "_bulto", coll, m, r=1.0, u=32, v=16)
        self.b.parent = pj["root"]
        self.r = r
        # camino en coordenadas del pájaro (mira hacia -Y): bajo el pico → garganta → pecho (por dentro del cuello)
        self.camino = [Vector((0, -0.052, 0.118)), Vector((0, -0.051, 0.098)), Vector((0, -0.047, 0.080))]
        self.b.hide_render = True

    def poner(self, x):
        """x: 0 (antes) → 1 (ya pasó). El bulto crece al entrar al cuello y se achica al llegar al pecho."""
        vis = 0 < x < 1
        self.b.hide_render = not vis
        if not vis:
            return
        c = self.camino
        p = c[0].lerp(c[1], x * 2) if x < 0.5 else c[1].lerp(c[2], (x - 0.5) * 2)
        s = self.r * math.sin(math.pi * x) ** 0.6
        self.b.location = p
        self.b.scale = (s * 1.15, s, s)


def trago(x):
    """Curva de un trago en 0..1: la cabeza sube (0–0,35), traga (0,35–0,55) y baja (0,55–1)."""
    sube = E2.suave(E2.clamp(x / 0.35))
    baja = E2.suave(E2.clamp((x - 0.55) / 0.45))
    return sube * (1 - baja)
