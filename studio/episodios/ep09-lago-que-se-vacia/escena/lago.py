"""Set del Ep. 9 (el lago que se vacía): valle patagónico con un lago represado por un glaciar, estilo REALISTA.

Todo procedural y a escala real (m). Eje del valle = Y. El frente del glaciar (la represa) está en y≈0 y mira a +Y; el lago va
de y=0 a y≈1.900. El nivel del lago es un parámetro (NIVEL_LLENO = 0 → NIVEL_VACIO ≈ −29 m: quedan charcos en los bajos).
- terreno(): el valle (fondo del lago de barro, laderas con la marca del nivel del agua, cerros con nieve)
- glaciar(): la lengua de hielo que cierra el valle, con el frente de seracs y grietas
- tempanos(): bloques de hielo que flotan con el lago lleno y quedan varados en el barro con el lago vacío
- agua(): la superficie del lago (gris turquesa de harina glaciar)
- corte(): la represa abierta de costado (E2): roca, hielo, agua, la lengua de agua bajo el hielo y el túnel
- vaso(): un vaso con agua y un cubo de hielo en una roca de la orilla (E3)
"""
import math, random
import numpy as np
import bpy
from mathutils import Vector
import ep09 as K

NIVEL_LLENO = 0.0
NIVEL_VACIO = -30.2
LARGO = 1900.0          # largo del lago (y)
ANCHO = 360.0           # medio ancho del fondo del valle en el lago (x)
PROF = 33.0             # profundidad máxima del fondo, junto a la represa


# ---------------------------------------------------------------- ruido (numpy, determinista)
def _ruido_valor(x, y, semilla, escala):
    rng = np.random.RandomState(semilla)
    g = rng.rand(258, 258).astype(np.float32)
    u = x / escala + 1000.3
    v = y / escala + 1000.7
    i = np.floor(u).astype(np.int64)
    j = np.floor(v).astype(np.int64)
    fu = u - i
    fv = v - j
    fu = fu * fu * (3 - 2 * fu)
    fv = fv * fv * (3 - 2 * fv)
    i0, j0 = i % 256, j % 256
    i1, j1 = (i0 + 1) % 256, (j0 + 1) % 256
    a = g[i0, j0] * (1 - fu) + g[i1, j0] * fu
    b = g[i0, j1] * (1 - fu) + g[i1, j1] * fu
    return a * (1 - fv) + b * fv


def fbm(x, y, semilla=1, escala=100.0, oct=5, gan=0.5):
    s = np.zeros_like(x, dtype=np.float32)
    amp, tot = 1.0, 0.0
    for o in range(oct):
        s += amp * (_ruido_valor(x, y, semilla + o * 17, escala / (2 ** o)) - 0.5)
        tot += amp
        amp *= gan
    return s / tot * 2.0          # ~[-1, 1]


def cresta(x, y, semilla=1, escala=100.0, oct=5):
    """Ruido de crestas (cerros con aristas, seracs)."""
    s = np.zeros_like(x, dtype=np.float32)
    amp, tot = 1.0, 0.0
    for o in range(oct):
        n = _ruido_valor(x, y, semilla + o * 31, escala / (2 ** o))
        s += amp * (1 - np.abs(2 * n - 1)) ** 2
        tot += amp
        amp *= 0.5
    return s / tot


def suave(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


# ---------------------------------------------------------------- formas del valle
def eje_x(y):
    """El valle serpentea un poco (no es un canal recto)."""
    return 60.0 * np.sin(y / 700.0) + 25.0 * np.sin(y / 260.0 + 1.3)


def ancho(y):
    return ANCHO * (0.85 + 0.25 * np.sin(y / 520.0 + 0.4)) * (1.0 - 0.35 * suave((y - 1500) / 600))


def altura_terreno(x, y):
    """Altura del terreno (m). Fondo del lago bajo 0; la orilla llena en ~0; laderas que suben a 900–1.300 m."""
    xc = x - eje_x(y)
    w = ancho(y)
    u = np.abs(xc) / w
    # profundidad: máxima junto a la represa y casi nada en la cabecera
    prof = PROF * (1.0 - 0.6 * np.clip(y / 1900.0, 0, 1)) * (1.0 - 0.4 * suave((-y) / 300.0))
    fondo = -prof * np.clip(1 - u ** 2, 0, 1) ** 0.6
    # laderas fuera del fondo: suben empinadas
    lad = np.clip(u - 1.0, 0, None) * w
    alto_lado = np.where(xc > 0, 45.0, 950.0)                 # la ladera este es más baja: entra el sol de la mañana
    pared = np.where(xc > 0, 0.18, 0.45) * np.minimum(lad, 300.0) + alto_lado * suave(lad / 1100.0) ** 1.4
    z = np.where(u < 1.0, fondo, pared)
    # cabecera (norte) sube suave hacia el valle de arriba
    z += 22.0 * suave((y - 1700) / 500.0)
    # relieve: lomas suaves en el fondo (charcos y canales), roca grande en las laderas
    det_fondo = 1.6 * fbm(x, y, 3, 90.0, 4) + 0.5 * fbm(x, y, 9, 18.0, 3)
    canal = -2.6 * np.exp(-((xc + 30 * np.sin(y / 140.0)) / 22.0) ** 2) * suave((1700 - y) / 400.0) * (u < 1.0)
    det_lad = (70.0 * fbm(x, y, 5, 600.0, 6) * suave(lad / 120.0) + 140.0 * (cresta(x, y, 11, 900.0, 5) - 0.4) * suave(lad / 500.0)
               + (40.0 * (cresta(x, y, 13, 120.0, 4) - 0.4) + 38.0 * (cresta(x * 0.22, y * 1.6, 17, 80.0, 4) - 0.4)
                  + 7.0 * fbm(x, y, 15, 22.0, 3)) * suave(lad / 60.0))
    det_lad = det_lad * np.where(xc > 0, 0.35, 1.0)
    return z + np.where(u < 1.0, det_fondo + canal, det_fondo * 0.3 + det_lad)


def malla_altura(nombre, x0, x1, y0, y1, nx, ny, fn, mat=None):
    xs = np.linspace(x0, x1, nx, dtype=np.float32)
    ys = np.linspace(y0, y1, ny, dtype=np.float32)
    X, Y = np.meshgrid(xs, ys)
    Z = fn(X, Y).astype(np.float32)
    verts = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)
    idx = np.arange(nx * ny).reshape(ny, nx)
    a = idx[:-1, :-1].ravel(); b = idx[:-1, 1:].ravel(); c = idx[1:, 1:].ravel(); d = idx[1:, :-1].ravel()
    caras = np.stack([a, b, c, d], 1)
    me = bpy.data.meshes.new(nombre)
    me.vertices.add(len(verts)); me.vertices.foreach_set("co", verts.ravel())
    me.loops.add(len(caras) * 4); me.loops.foreach_set("vertex_index", caras.ravel())
    me.polygons.add(len(caras)); me.polygons.foreach_set("loop_start", np.arange(0, len(caras) * 4, 4)); me.polygons.foreach_set("loop_total", np.full(len(caras), 4))
    me.update(); me.validate()
    ob = bpy.data.objects.new(nombre, me)
    bpy.context.scene.collection.objects.link(ob)
    for p in me.polygons:
        p.use_smooth = True
    if mat:
        K.asignar(ob, mat)
    return ob


# ---------------------------------------------------------------- materiales
def mat_valle(nombre="valle"):
    """Un solo material por altura (z mundo): barro del fondo recién vaciado (café gris, mojado en los bajos, con ondulitas y
    grietas), la franja lavada sin vegetación sobre el nivel lleno (la marca del agua), bosque oscuro en las laderas bajas,
    roca donde es empinado y nieve arriba de ~900 m. Todo con manchas grandes (nada parejo)."""
    m, nt, b = K._nodos(nombre)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sep.inputs[0])
    z = sep.outputs["Z"]
    grande = K._ruido(nt, escala=0.006, detalle=6)
    medio = K._ruido(nt, escala=0.05, detalle=8)
    fino = K._ruido(nt, escala=0.9, detalle=6)
    onda = K._ruido(nt, escala=6.0, detalle=4)                                    # grumos del barro (~15 cm)
    vor = nt.nodes.new("ShaderNodeTexVoronoi"); vor.feature = "DISTANCE_TO_EDGE"; vor.inputs["Scale"].default_value = 0.35
    nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
    manchas = K._ruido(nt, escala=0.35, detalle=6)
    barro = K._rampa(nt, manchas.outputs["Fac"], (0.05, 0.049, 0.047), (0.16, 0.152, 0.142), (0.3, 0.72))
    limo = K._rampa(nt, grande.outputs["Fac"], (0.17, 0.16, 0.145), (0.27, 0.255, 0.23))
    lavada = K._rampa(nt, medio.outputs["Fac"], (0.13, 0.125, 0.115), (0.24, 0.23, 0.21))
    bosque = K._rampa(nt, fino.outputs["Fac"], (0.012, 0.02, 0.01), (0.035, 0.05, 0.022), (0.35, 0.7))
    roca = K._rampa(nt, medio.outputs["Fac"], (0.055, 0.056, 0.058), (0.2, 0.2, 0.2))
    nieve = K._rampa(nt, fino.outputs["Fac"], (0.7, 0.74, 0.8), (0.9, 0.92, 0.95))
    pend = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Normal"], pend.inputs[0])

    def mezclar(fac, a, bcol):
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
        nt.links.new(fac, mx.inputs[0]); nt.links.new(a, mx.inputs[6]); nt.links.new(bcol, mx.inputs[7])
        return mx.outputs[2]

    def rango(entrada, a, b_, c=0.0, d=1.0):
        mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = a; mr.inputs["From Max"].default_value = b_
        mr.inputs["To Min"].default_value = c; mr.inputs["To Max"].default_value = d
        nt.links.new(entrada, mr.inputs["Value"])
        return mr.outputs[0]

    zr = nt.nodes.new("ShaderNodeMath"); zr.operation = "ADD"
    nz = nt.nodes.new("ShaderNodeMath"); nz.operation = "MULTIPLY"; nz.inputs[1].default_value = 6.0
    nt.links.new(grande.outputs["Fac"], nz.inputs[0]); nt.links.new(z, zr.inputs[0]); nt.links.new(nz.outputs[0], zr.inputs[1])
    zz = zr.outputs[0]
    c1 = mezclar(rango(zz, -26, -14), barro.outputs[0], limo.outputs[0])            # fondo: barro → limo en las lomas
    c2a = mezclar(rango(zz, 0.5, 3.0), c1, lavada.outputs[0])                         # sobre el nivel lleno: franja lavada
    c2 = mezclar(rango(zz, 8.0, 18.0), c2a, roca.outputs[0])                           # más arriba, roca y pasto ralo
    manchas_b = K._ruido(nt, escala=0.02, detalle=14)
    kb1 = rango(zz, 14.0, 26.0); kb3 = rango(zz, 330.0, 200.0); kb2 = rango(manchas_b.outputs["Fac"], 0.44, 0.47)
    kb0 = nt.nodes.new("ShaderNodeMath"); kb0.operation = "MULTIPLY"; nt.links.new(kb1, kb0.inputs[0]); nt.links.new(kb3, kb0.inputs[1])
    kb1 = kb0.outputs[0]
    kb = nt.nodes.new("ShaderNodeMath"); kb.operation = "MULTIPLY"; nt.links.new(kb1, kb.inputs[0]); nt.links.new(kb2, kb.inputs[1])
    c3 = mezclar(kb.outputs[0], c2, bosque.outputs[0])                                # manchas de bosque desde ~15 m sobre el lleno
    emp = rango(pend.outputs["Z"], 0.34, 0.2)
    c4 = mezclar(emp, c3, roca.outputs[0])                                            # roca en lo empinado
    c5 = mezclar(rango(zz, 380, 560), c4, roca.outputs[0])                            # sobre el bosque, roca
    arb = nt.nodes.new("ShaderNodeTexVoronoi"); arb.inputs["Scale"].default_value = 0.22
    nt.links.new(tc.outputs["Object"], arb.inputs["Vector"])
    ka = rango(arb.outputs["Distance"], 0.0, 0.35, 0.45, 1.0)                          # copas: puntos más oscuros
    c5a = nt.nodes.new("ShaderNodeMix"); c5a.data_type = "RGBA"; c5a.blend_type = "MULTIPLY"
    nt.links.new(kb.outputs[0], c5a.inputs[0]); nt.links.new(c5, c5a.inputs[6])
    cg = nt.nodes.new("ShaderNodeCombineColor"); nt.links.new(ka, cg.inputs[0]); nt.links.new(ka, cg.inputs[1]); nt.links.new(ka, cg.inputs[2])
    nt.links.new(cg.outputs[0], c5a.inputs[7])
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = 18.0; ao.samples = 6
    kao = rango(ao.outputs["AO"], 0.0, 1.0, 0.25, 1.0)
    c5b = nt.nodes.new("ShaderNodeMix"); c5b.data_type = "RGBA"; c5b.blend_type = "MULTIPLY"; c5b.inputs[0].default_value = 1.0
    nt.links.new(c5a.outputs[2], c5b.inputs[6])
    cg2 = nt.nodes.new("ShaderNodeCombineColor"); nt.links.new(kao, cg2.inputs[0]); nt.links.new(kao, cg2.inputs[1]); nt.links.new(kao, cg2.inputs[2])
    nt.links.new(cg2.outputs[0], c5b.inputs[7])
    alto_n = rango(zz, 640, 760)                                                      # nieve arriba, en lo menos empinado
    plano_n = rango(pend.outputs["Z"], 0.45, 0.7)
    kn = nt.nodes.new("ShaderNodeMath"); kn.operation = "MULTIPLY"; kn.use_clamp = True
    nt.links.new(alto_n, kn.inputs[0]); nt.links.new(plano_n, kn.inputs[1])
    c6 = mezclar(kn.outputs[0], c5b.outputs[2], nieve.outputs[0])
    nt.links.new(c6, b.inputs["Base Color"])
    camd = nt.nodes.new("ShaderNodeCameraData")
    kh = rango(camd.outputs["View Distance"], 250.0, 5000.0, 0.0, 0.55)
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = (0.52, 0.62, 0.78, 1); em.inputs[1].default_value = 0.42
    mxs = nt.nodes.new("ShaderNodeMixShader"); nt.links.new(kh, mxs.inputs[0])
    nt.links.new(b.outputs[0], mxs.inputs[1]); nt.links.new(em.outputs[0], mxs.inputs[2])
    nt.links.new(mxs.outputs[0], nt.nodes["Material Output"].inputs[0])
    # brillo: barro mojado en los bajos (0,22) y en las grietas; limo y laderas mates
    rug = rango(zz, -31.0, -22.0, 0.16, 0.55)
    rug2 = nt.nodes.new("ShaderNodeMath"); rug2.operation = "MAXIMUM"
    nt.links.new(rug, rug2.inputs[0]); nt.links.new(rango(zz, -2, 6, 0.0, 0.92), rug2.inputs[1])
    nt.links.new(rug2.outputs[0], b.inputs["Roughness"])
    # relieve: ondulitas + grietas del barro (sólo abajo) + grano
    vgr = nt.nodes.new("ShaderNodeTexVoronoi"); vgr.inputs["Scale"].default_value = 9.0; vgr.feature = "SMOOTH_F1"
    nt.links.new(tc.outputs["Object"], vgr.inputs["Vector"])
    s1 = nt.nodes.new("ShaderNodeMath"); s1.operation = "ADD"; nt.links.new(onda.outputs["Fac"], s1.inputs[0]); nt.links.new(vgr.outputs["Distance"], s1.inputs[1])
    s2 = nt.nodes.new("ShaderNodeMath"); s2.operation = "ADD"; nt.links.new(s1.outputs[0], s2.inputs[0]); nt.links.new(fino.outputs["Fac"], s2.inputs[1])
    copa = K._ruido(nt, escala=0.25, detalle=4)                                  # copas del bosque (~4 m)
    s3 = nt.nodes.new("ShaderNodeMath"); s3.operation = "MULTIPLY_ADD"; s3.inputs[1].default_value = 3.0
    nt.links.new(copa.outputs["Fac"], s3.inputs[0]); nt.links.new(s2.outputs[0], s3.inputs[2])
    K._bump(nt, b, s3.outputs[0], 0.35, 0.05)
    return m


def mat_hielo(nombre="hielo", limpio=0.0, sucio=0.5):
    """Hielo de glaciar: blanco azulado arriba, azul profundo en las grietas (oclusión), bandas de polvo, subsuperficie azul."""
    m, nt, b = K._nodos(nombre)
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = 6.0; ao.samples = 8
    grieta = K._rampa(nt, ao.outputs["AO"], (0.03, 0.17, 0.33), (0.62, 0.74, 0.82), (0.15, 0.85))
    # bandas de polvo horizontales (capas del glaciar) y manchas de morrena
    bandas = K._ruido(nt, escala=0.08, detalle=6, estirar=(0.15, 0.15, 3.0))
    kb = K._mapa(nt, bandas.outputs["Fac"], 0.0, 1.0); kb.inputs["From Min"].default_value = 0.5; kb.inputs["From Max"].default_value = 0.68
    sucia = nt.nodes.new("ShaderNodeMix"); sucia.data_type = "RGBA"; sucia.blend_type = "MULTIPLY"
    f = nt.nodes.new("ShaderNodeMath"); f.operation = "MULTIPLY"; f.inputs[1].default_value = sucio
    nt.links.new(kb.outputs[0], f.inputs[0]); nt.links.new(f.outputs[0], sucia.inputs[0])
    nt.links.new(grieta.outputs[0], sucia.inputs[6]); sucia.inputs[7].default_value = (0.42, 0.37, 0.32, 1)
    nt.links.new(sucia.outputs[2], b.inputs["Base Color"])
    b.inputs["Subsurface Weight"].default_value = 0.25
    b.inputs["Subsurface Radius"].default_value = (0.3, 0.8, 1.5)
    b.inputs["Subsurface Scale"].default_value = 0.08
    rr = K._ruido(nt, escala=0.6, detalle=5)
    rg = K._mapa(nt, rr.outputs["Fac"], 0.1 - 0.06 * limpio, 0.45 - 0.25 * limpio)
    nt.links.new(rg.outputs[0], b.inputs["Roughness"])
    # relieve: estrías verticales (el hielo se parte en columnas) + grano fino
    est = K._ruido(nt, escala=0.25, detalle=8, estirar=(1.0, 1.0, 0.12))
    bp = K._ruido(nt, escala=1.5, detalle=6)
    s = nt.nodes.new("ShaderNodeMath"); s.operation = "ADD"
    nt.links.new(est.outputs["Fac"], s.inputs[0]); nt.links.new(bp.outputs["Fac"], s.inputs[1])
    K._bump(nt, b, s.outputs[0], 0.7, 0.6)
    return m


def mat_nieve_glaciar(nombre="glaciar_sup"):
    """Superficie del glaciar: hielo blanco grisáceo con franjas de morrena oscuras a lo largo del flujo y grietas azules."""
    m, nt, b = K._nodos(nombre)
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = 8.0; ao.samples = 8
    base = K._rampa(nt, ao.outputs["AO"], (0.05, 0.2, 0.36), (0.78, 0.8, 0.83), (0.2, 0.8))
    mor = K._ruido(nt, escala=0.004, detalle=6, estirar=(1.0, 0.08, 1.0))
    km = K._mapa(nt, mor.outputs["Fac"], 0.0, 1.0); km.inputs["From Min"].default_value = 0.55; km.inputs["From Max"].default_value = 0.62
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
    nt.links.new(km.outputs[0], mx.inputs[0]); nt.links.new(base.outputs[0], mx.inputs[6]); mx.inputs[7].default_value = (0.13, 0.12, 0.11, 1)
    sucio = K._ruido(nt, escala=0.03, detalle=8)
    ks = K._mapa(nt, sucio.outputs["Fac"], 0.0, 0.35); ks.inputs["From Min"].default_value = 0.5; ks.inputs["From Max"].default_value = 0.75
    mx2 = nt.nodes.new("ShaderNodeMix"); mx2.data_type = "RGBA"
    nt.links.new(ks.outputs[0], mx2.inputs[0]); nt.links.new(mx.outputs[2], mx2.inputs[6]); mx2.inputs[7].default_value = (0.3, 0.28, 0.25, 1)
    nt.links.new(mx2.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.6
    b.inputs["Subsurface Weight"].default_value = 0.15
    b.inputs["Subsurface Radius"].default_value = (0.4, 0.9, 1.5)
    bp = K._ruido(nt, escala=0.12, detalle=8)
    K._bump(nt, b, bp.outputs["Fac"], 0.5, 0.6)
    return m


def mat_agua_glaciar(nombre="agua_lago"):
    """Agua de lago glaciar: turquesa grisáceo opaco (harina de roca en suspensión), reflejo nítido y ondas finas."""
    m, nt, b = K._nodos(nombre)
    col = K._ruido(nt, escala=0.004, detalle=4)
    c = K._rampa(nt, col.outputs["Fac"], (0.035, 0.1, 0.11), (0.07, 0.16, 0.165))
    nt.links.new(c.outputs[0], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.035
    b.inputs["IOR"].default_value = 1.33
    b.inputs["Subsurface Weight"].default_value = 0.2
    b.inputs["Subsurface Radius"].default_value = (0.2, 0.5, 0.55)
    on = K._ruido(nt, escala=0.25, detalle=6, estirar=(1.0, 2.5, 1.0))
    on2 = K._ruido(nt, escala=1.6, detalle=4)
    s = nt.nodes.new("ShaderNodeMath"); s.operation = "ADD"
    nt.links.new(on.outputs["Fac"], s.inputs[0]); nt.links.new(on2.outputs["Fac"], s.inputs[1])
    K._bump(nt, b, s.outputs[0], 0.12, 0.06)
    m["fase"] = 0.0
    return m


# ---------------------------------------------------------------- objetos del set
def terreno(sc, detalle=1.0):
    """Tres mallas: el fondo del lago y sus orillas (fino), el valle cercano y los cerros lejanos (con bruma)."""
    mv = mat_valle()
    n = int(560 * detalle)
    fondo = malla_altura("Fondo", -1600, 1600, -260, 2200, int(n * 1.5), int(n * 1.1), altura_terreno, mv)
    lejos = malla_altura("Valle", -6000, 6000, -4500, 9000, int(300 * detalle), int(330 * detalle),
                         lambda x, y: np.where((np.abs(x) < 1580) & (y > -250) & (y < 2180), -60.0, altura_terreno(x, y)), mv)
    # cerros lejanos con bruma (formas grandes que llegan al suelo; ESTILO_REALISTA §4.3)
    def picos(x, y):
        d = np.sqrt(x ** 2 + (y - 1500) ** 2)
        base = 1500.0 * suave((d - 4000) / 3500) * (0.55 + 0.6 * cresta(x, y, 21, 2600.0, 6))
        z = base + 300 * fbm(x, y, 23, 1500.0, 5) * suave((d - 4000) / 2000)
        z = np.where(x > 0, z * 0.35, z)              # al este, cerros bajos: por ahí entra el sol de la mañana
        return np.where(d < 5200, -300.0, z)         # adentro lo cubre el valle (si no, queda de techo sobre el lago)
    cer = malla_altura("Cerros", -20000, 20000, -14000, 26000, 260, 260, picos,
                       K.mat_lejano("cerros_bruma", (0.32, 0.33, 0.36), neblina=(0.55, 0.6, 0.7), k=0.5, color2=(0.75, 0.78, 0.84)))
    return fondo, lejos, cer


def glaciar(sc, detalle=1.0):
    """Lengua de hielo que cierra el valle en y<0. Frente (el muro) de ~65–75 m sobre el fondo, con seracs y grietas."""
    def sup(x, y):
        base = altura_terreno(x, y)
        espesor = 70.0 + 0.018 * (-y) + 25.0 * fbm(x, y, 41, 400.0, 4)
        frente = suave((-y - 18.0) / 6.0)                       # el borde (la malla "Muro" lo cubre por delante)
        transv = np.abs(np.sin((y + 18.0 * fbm(x, y, 49, 180.0, 3)) / 9.0)) ** 0.3       # grietas transversales (~28 m)
        serac = (14.0 * (cresta(x, y, 43, 55.0, 4) - 0.45) + 4.0 * fbm(x, y, 47, 12.0, 3)
                 + 11.0 * (transv - 0.8) * (1 - 0.5 * suave((-y) / 1500.0)))
        zi = NIVEL_LLENO + 38.0 + 0.035 * (-y) + serac * (1 - 0.6 * suave((-y - 3000) / 3000))
        k = suave((ancho(y) * 1.35 - np.abs(x - eje_x(y))) / (ancho(y) * 0.35))     # el hielo se adelgaza hacia las laderas
        z = np.where(zi > base, base + (zi - base) * k - 45.0 * (1 - k) ** 2, base - 45.0)
        return np.where(-y > 18.0, base + (z - base) * frente, base - 45.0)
    g = malla_altura("Glaciar", -1300, 1300, -9000, 10, int(700 * detalle), int(1100 * detalle), sup, mat_nieve_glaciar())
    # el muro del frente: una malla vertical aparte (los seracs, las grietas y las bandas se ven de frente)
    nx, nz = int(700 * detalle), int(160 * detalle)
    xs = np.linspace(-700, 700, nx, dtype=np.float32)
    zs = np.linspace(-40, 80, nz, dtype=np.float32)
    X, Z = np.meshgrid(xs, zs)
    # el muro va por delante del borde del glaciar (y de −14 a +3): seracs, columnas y grietas verticales
    techo = np.array([sup(np.array([x], np.float32), np.array([-30.0], np.float32))[0] for x in xs], np.float32)
    # columnas y seracs: relieve estirado en vertical, por delante del borde del glaciar (y de −16 a +3)
    Yp = (-7.0 + 6.0 * (cresta(X, Z * 0.35, 51, 22.0, 4) - 0.45) + 2.0 * fbm(X, Z, 53, 9.0, 4)
          - 3.0 * (cresta(X * 2.2, Z * 0.25, 57, 16.0, 3) - 0.45))
    Yp = np.clip(Yp, -16.0, 3.0)
    arriba = np.clip((Z - (techo[None, :] - 14.0)) / 14.0, 0, 1)
    Yp = Yp * (1 - arriba) + (-27.0) * arriba                     # arriba se va hacia atrás y se junta con la superficie
    piso = altura_terreno(xs, np.full_like(xs, 2.0)) - 1.0
    Zc = np.clip(Z, piso[None, :], techo[None, :] - 0.5)
    verts = np.stack([X.ravel(), Yp.ravel(), Zc.ravel()], 1)
    idx = np.arange(nx * nz).reshape(nz, nx)
    a = idx[:-1, :-1].ravel(); b_ = idx[:-1, 1:].ravel(); c = idx[1:, 1:].ravel(); d = idx[1:, :-1].ravel()
    caras = np.stack([a, b_, c, d], 1)
    me = bpy.data.meshes.new("Muro")
    me.vertices.add(len(verts)); me.vertices.foreach_set("co", verts.ravel())
    me.loops.add(len(caras) * 4); me.loops.foreach_set("vertex_index", caras.ravel())
    me.polygons.add(len(caras)); me.polygons.foreach_set("loop_start", np.arange(0, len(caras) * 4, 4)); me.polygons.foreach_set("loop_total", np.full(len(caras), 4))
    me.update(); me.validate()
    muro = bpy.data.objects.new("Muro", me)
    sc.collection.objects.link(muro)
    for p in me.polygons:
        p.use_smooth = True
    K.asignar(muro, mat_hielo("hielo_muro", sucio=0.55))
    return g, muro


def roca_hielo(sc, nombre, tam, semilla, mat):
    """Un témpano: icosfera deformada con caras planas grandes (fracturas) y aristas."""
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5, radius=1.0)
    o = bpy.context.object
    o.name = nombre
    r = random.Random(semilla)
    planos = [(Vector((r.uniform(-1, 1), r.uniform(-1, 1), r.uniform(-0.6, 1))).normalized(), r.uniform(0.55, 0.85)) for _ in range(7)]
    for v in o.data.vertices:
        p = v.co.copy()
        for n, dcut in planos:            # corta con planos: caras de fractura
            k = p.dot(n) - dcut
            if k > 0:
                p -= n * k
        p *= 1.0 + 0.06 * math.sin(p.x * 7 + semilla) * math.cos(p.y * 5 - semilla)
        v.co = p
    o.scale = tam
    bpy.ops.object.transform_apply(scale=True)
    tx = bpy.data.textures.new(f"tex_{nombre}", "CLOUDS"); tx.noise_scale = 0.6
    dm = o.modifiers.new("det", "DISPLACE"); dm.texture = tx; dm.strength = 0.18 * max(tam)
    tx2 = bpy.data.textures.new(f"tex2_{nombre}", "VORONOI"); tx2.noise_scale = 0.25      # cuencos del derretimiento
    dm2 = o.modifiers.new("cuencos", "DISPLACE"); dm2.texture = tx2; dm2.strength = -0.035 * max(tam); dm2.texture_coords = "LOCAL"
    K.liso(o, 60)
    K.asignar(o, mat)
    return o


TEMPANOS = [  # (x, y, tamaño xyz, giro, inclinación vacía) — cerca del frente, donde caen del glaciar
    (66, 405, (15, 11, 9), 35, 7),      # el del cuadro 0 (a ~40 m de la cámara)
    (-60, 70, (14, 10, 7), 20, 9), (30, 140, (9, 12, 6), 70, -6), (95, 60, (18, 13, 8), -15, 4),
    (-130, 190, (8, 7, 5), 40, 12), (150, 230, (11, 8, 6), 5, -10), (-20, 300, (7, 9, 5), 100, 7),
    (60, 380, (12, 9, 6), -40, -5), (-90, 450, (6, 5, 4), 10, 14), (200, 120, (6, 8, 4), 60, 8),
    (-200, 90, (10, 7, 6), -70, -9), (10, 40, (22, 14, 10), 30, 3), (-40, 610, (8, 6, 5), 80, -11),
]


def tempanos(sc):
    mt = mat_hielo("hielo_tempano", limpio=0.6, sucio=0.3)
    bs = mt.node_tree.nodes["Principled BSDF"]
    bs.inputs["Subsurface Scale"].default_value = 0.35
    bs.inputs["Subsurface Weight"].default_value = 0.45
    out = []
    for i, (x, y, t, giro, incl) in enumerate(TEMPANOS):
        o = roca_hielo(sc, f"Tempano{i}", t, 100 + i, mt)
        zb = float(altura_terreno(np.array([x], np.float32), np.array([y], np.float32))[0])
        o["x"], o["y"], o["giro"], o["incl"], o["alto"], o["fondo"] = x, y, giro, incl, t[2], zb
        out.append(o)
    return out


def ubicar_tempanos(tem, nivel, deriva=0.0):
    """Con agua: flotan con ~1/8 sobre el agua (el hielo flota). Sin agua: varados y ladeados en el barro."""
    for o in tem:
        flota_z = nivel - o["alto"] * 0.62
        varado_z = o["fondo"] + o["alto"] * 0.18
        z = max(flota_z, varado_z)
        k = 1.0 if flota_z <= varado_z else 0.0
        o.location = (o["x"] + deriva * math.sin(o["giro"]), o["y"] + deriva * math.cos(o["giro"]), z)
        o.rotation_euler = (math.radians(o["incl"] * k), math.radians(o["incl"] * 0.5 * k), math.radians(o["giro"] + deriva * 0.3))


def sueltos(sc, centro=(70, 380), radio=170.0, n_piedras=420, n_hielo=160, semilla=5):
    """Piedras y trozos de hielo sueltos en el barro (lo que deja el agua al irse). Más densos cerca del centro."""
    r = random.Random(semilla)
    mp = K.mat_concreto("piedra", (0.2, 0.19, 0.18), escala=6.0)
    mh = mat_hielo("hielo_trozos", limpio=0.8, sucio=0.15)
    base_p = roca_hielo(sc, "PiedraBase", (1, 0.8, 0.6), 7, mp)
    base_h = roca_hielo(sc, "TrozoBase", (1, 0.9, 0.7), 9, mh)
    out = []
    for i in range(n_piedras + n_hielo):
        hielo = i >= n_piedras
        d = radio * r.random() ** 1.6
        a = r.uniform(0, 2 * math.pi)
        x, y = centro[0] + d * math.cos(a), centro[1] + d * math.sin(a)
        s = r.uniform(0.12, 0.5) if not hielo else r.uniform(0.3, 1.4)
        zb = float(altura_terreno(np.array([x], np.float32), np.array([y], np.float32))[0])
        o = (base_h if hielo else base_p).copy()
        sc.collection.objects.link(o)
        o.location = (x, y, zb - s * 0.25)
        o.scale = (s * r.uniform(0.7, 1.3), s * r.uniform(0.7, 1.3), s * r.uniform(0.4, 0.8))
        o.rotation_euler = (r.uniform(-0.4, 0.4), r.uniform(-0.4, 0.4), r.uniform(0, 6.3))
        o["suelto_hielo"] = int(hielo)
        out.append(o)
    base_p.hide_render = base_h.hide_render = True
    return out


def agua(sc, nivel=NIVEL_LLENO):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 900, nivel))
    o = bpy.context.object
    o.name = "Agua"
    o.scale = (1900, 2400, 1)
    K.asignar(o, mat_agua_glaciar())
    o.visible_shadow = False
    return o


def nivel_agua(o, nivel):
    o.location.z = nivel


def valle(sc, nivel=NIVEL_LLENO, detalle=1.0, sol_elev=11.0, sol_rot=105.0):
    """Arma el set completo. Sol de la mañana desde el este-sureste (11°, el de noviembre en Aysén): cruza bajo sobre la ladera este (baja) y deja a contraluz de costado los témpanos y el frente: pasa sobre la ladera este (más baja) y le pega de
    costado al frente del glaciar, que mira al norte. Nunca de frente ni detrás de la cámara (luz plana)."""
    w, sol, d = K.cielo_atardecer(sc, elev=sol_elev, rot=sol_rot, fuerza=0.14, sol=3.0, color_sol=(1.0, 0.84, 0.7))
    sky = next(n for n in w.node_tree.nodes if n.type == "TEX_SKY")
    sky.altitude = 400
    sky.aerosol_density = 2.2
    t = terreno(sc, detalle)
    g, muro = glaciar(sc, detalle)
    tem = tempanos(sc)
    su = sueltos(sc)
    ag = agua(sc, nivel)
    ubicar_tempanos(tem, nivel)
    return {"terreno": t, "glaciar": g, "muro": muro, "tempanos": tem, "sueltos": su, "agua": ag, "sol": sol}


# ================================================================ E2: la represa en corte
XC = 24.0                      # plano del corte (x), por el eje del valle junto a la represa
Y0C, Y1C = -420.0, 420.0       # tramo del valle que se abre
Y_FRENTE = -5.0                # el frente de hielo en el corte


def _perfil_hielo(y):
    """Techo del hielo en el corte (z), del glaciar real del set."""
    g = np.asarray(y, np.float32)
    x = np.full_like(g, XC)
    base = altura_terreno(x, g)
    serac = 14.0 * (cresta(x, g, 43, 55.0, 4) - 0.45) + 4.0 * fbm(x, g, 47, 12.0, 3)
    zi = NIVEL_LLENO + 38.0 + 0.035 * np.maximum(-g, 20.0) + serac
    return np.maximum(zi, base + 30.0)


def recortar(sc, excepto=()):
    """Hace transparente todo lo que queda delante del corte (x > XC, Y0C < y < Y1C) en los materiales del set: así se
    ve la cara del corte y, detrás, el valle real."""
    hechos = set()
    for o in sc.objects:
        if o.type != "MESH" or o.name in excepto:
            continue
        for s in o.material_slots:
            m = s.material
            if not m or m.name in hechos or m.get("corte"):
                continue
            hechos.add(m.name)
            nt = m.node_tree
            out = nt.nodes.get("Material Output") or next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
            if not out.inputs[0].links:
                continue
            src = out.inputs[0].links[0].from_socket
            geo = nt.nodes.new("ShaderNodeNewGeometry")
            sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(geo.outputs["Position"], sp.inputs[0])
            gx = nt.nodes.new("ShaderNodeMath"); gx.operation = "GREATER_THAN"; gx.inputs[1].default_value = XC
            nt.links.new(sp.outputs["X"], gx.inputs[0])
            ya = nt.nodes.new("ShaderNodeMath"); ya.operation = "GREATER_THAN"; ya.inputs[1].default_value = Y0C
            yb = nt.nodes.new("ShaderNodeMath"); yb.operation = "LESS_THAN"; yb.inputs[1].default_value = Y1C
            nt.links.new(sp.outputs["Y"], ya.inputs[0]); nt.links.new(sp.outputs["Y"], yb.inputs[0])
            m1 = nt.nodes.new("ShaderNodeMath"); m1.operation = "MULTIPLY"; nt.links.new(gx.outputs[0], m1.inputs[0]); nt.links.new(ya.outputs[0], m1.inputs[1])
            m2 = nt.nodes.new("ShaderNodeMath"); m2.operation = "MULTIPLY"; nt.links.new(m1.outputs[0], m2.inputs[0]); nt.links.new(yb.outputs[0], m2.inputs[1])
            tr = nt.nodes.new("ShaderNodeBsdfTransparent")
            mx = nt.nodes.new("ShaderNodeMixShader")
            nt.links.new(m2.outputs[0], mx.inputs[0]); nt.links.new(src, mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2])
            nt.links.new(mx.outputs[0], out.inputs[0])


def mat_roca_corte():
    m, nt, b = K._nodos("roca_corte")
    m["corte"] = 1
    capas = K._ruido(nt, escala=0.05, detalle=6, estirar=(0.08, 0.08, 1.0))
    c = K._rampa(nt, capas.outputs["Fac"], (0.16, 0.14, 0.12), (0.36, 0.33, 0.29), (0.3, 0.7))
    gr = K._ruido(nt, escala=1.2, detalle=6)
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = 0.25
    nt.links.new(c.outputs[0], mx.inputs[6]); nt.links.new(gr.outputs["Color"], mx.inputs[7])
    nt.links.new(mx.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.9
    K._bump(nt, b, gr.outputs["Fac"], 0.4, 0.3)
    return m


def mat_hielo_corte():
    """La cara del hielo cortado: blanco azulado con capas (años de nieve apretada) y burbujas; más azul en lo profundo."""
    m, nt, b = K._nodos("hielo_corte")
    m["corte"] = 1
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sp.inputs[0])
    prof = K._mapa(nt, sp.outputs["Z"], 0.0, 1.0); prof.inputs["From Min"].default_value = -30; prof.inputs["From Max"].default_value = 60
    base = K._rampa(nt, prof.outputs[0], (0.04, 0.2, 0.42), (0.5, 0.68, 0.84), (0.0, 1.0))
    capas = K._ruido(nt, escala=0.12, detalle=6, estirar=(0.05, 0.05, 1.0))
    kc = K._mapa(nt, capas.outputs["Fac"], 0.0, 1.0); kc.inputs["From Min"].default_value = 0.48; kc.inputs["From Max"].default_value = 0.6
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; mx.blend_type = "MULTIPLY"
    f = nt.nodes.new("ShaderNodeMath"); f.operation = "MULTIPLY"; f.inputs[1].default_value = 0.6
    nt.links.new(kc.outputs[0], f.inputs[0]); nt.links.new(f.outputs[0], mx.inputs[0])
    nt.links.new(base.outputs[0], mx.inputs[6]); mx.inputs[7].default_value = (0.4, 0.37, 0.34, 1)
    nt.links.new(mx.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.35
    b.inputs["Subsurface Weight"].default_value = 0.2
    b.inputs["Subsurface Radius"].default_value = (0.3, 0.8, 1.5)
    b.inputs["Subsurface Scale"].default_value = 0.3
    bub = K._ruido(nt, escala=3.0, detalle=4)
    K._bump(nt, b, bub.outputs["Fac"], 0.25, 0.1)
    return m


def mat_agua_corte(nombre="agua_corte", brillo=0.0):
    """El agua cortada: azul verdoso translúcido con limo, más oscura abajo; el agua del túnel tiene estelas que corren
    (valor "fase" que se mueve por cuadro)."""
    m, nt, b = K._nodos(nombre)
    m["corte"] = 1
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping"); nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    mp.inputs["Scale"].default_value = (1.0, 0.04, 1.0)
    st = nt.nodes.new("ShaderNodeTexNoise"); st.inputs["Scale"].default_value = 3.0; st.inputs["Detail"].default_value = 3
    nt.links.new(mp.outputs[0], st.inputs["Vector"])
    m["mapping"] = mp.name
    sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sp.inputs[0])
    prof = K._mapa(nt, sp.outputs["Z"], 0.0, 1.0); prof.inputs["From Min"].default_value = -34; prof.inputs["From Max"].default_value = 2
    c = K._rampa(nt, prof.outputs[0], (0.02, 0.09, 0.12), (0.1, 0.34, 0.38), (0.0, 1.0))
    est = K._mapa(nt, st.outputs["Fac"], 0.0, 1.0); est.inputs["From Min"].default_value = 0.55; est.inputs["From Max"].default_value = 0.7
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
    k = nt.nodes.new("ShaderNodeMath"); k.operation = "MULTIPLY"; k.inputs[1].default_value = 0.0 if not brillo else 0.6
    nt.links.new(est.outputs[0], k.inputs[0]); nt.links.new(k.outputs[0], mx.inputs[0])
    nt.links.new(c.outputs[0], mx.inputs[6]); mx.inputs[7].default_value = (0.55, 0.82, 0.88, 1)
    nt.links.new(mx.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.12
    b.inputs["Emission Color"].default_value = (0.3, 0.75, 0.85, 1)
    nt.links.new(k.outputs[0], b.inputs["Emission Strength"])
    return m


def _franja(nombre, ys, abajo, arriba, mat, x=XC):
    """Malla plana en el plano x: franja entre dos curvas z(y) (quads de a pares de puntos)."""
    n = len(ys)
    verts = []
    for y, a, b_ in zip(ys, abajo, arriba):
        verts += [(x, float(y), float(a)), (x, float(y), float(max(b_, a)))]
    caras = [(2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1) for i in range(n - 1)]
    me = bpy.data.meshes.new(nombre); me.from_pydata(verts, [], caras); me.update()
    o = bpy.data.objects.new(nombre, me)
    bpy.context.scene.collection.objects.link(o)
    K.asignar(o, mat)
    return o


def _mover_franja(o, abajo, arriba):
    co = np.empty(len(o.data.vertices) * 3, np.float32)
    o.data.vertices.foreach_get("co", co)
    co = co.reshape(-1, 2, 3)
    co[:, 0, 2] = abajo
    co[:, 1, 2] = np.maximum(arriba, abajo)
    o.data.vertices.foreach_set("co", co.ravel())
    o.data.update()


class Corte:
    """La represa abierta de costado, en el set del valle. estado(nivel, lift, lengua, radio, fase) la mueve por cuadro:
    nivel = nivel del lago (m) · lift = cuánto se despega el pie del hielo (m, exagerado para que se vea) · lengua = hasta
    dónde llega el agua bajo el hielo (y, de 0 a Y0C) · radio = medio alto del túnel (m) · fase = corrida de las estelas."""

    def __init__(self, sc, S):
        self.S = S
        self.ys = np.linspace(Y0C, Y1C, 841).astype(np.float32)
        self.bed = altura_terreno(np.full_like(self.ys, XC), self.ys)
        self.techo = _perfil_hielo(self.ys)
        self.hielo_y = self.ys <= Y_FRENTE
        z0 = np.full_like(self.ys, -160.0)
        self.roca = _franja("CorteRoca", self.ys, z0, self.bed, mat_roca_corte())
        yh = self.ys[self.hielo_y]
        self.yh = yh
        self.hielo = _franja("CorteHielo", yh, self.bed[self.hielo_y], self.techo[self.hielo_y], mat_hielo_corte())
        self.tunel = _franja("CorteTunel", yh, self.bed[self.hielo_y], self.bed[self.hielo_y], mat_agua_corte("agua_tunel", brillo=1))
        yl = self.ys[~self.hielo_y]
        self.yl = yl
        self.lago = _franja("CorteLago", yl, self.bed[~self.hielo_y], self.bed[~self.hielo_y], mat_agua_corte())
        for o in S["tempanos"]:
            if abs(o["x"] - XC) < 30:
                o.hide_render = True
        recortar(sc)

    def estado(self, nivel, lift=0.0, lengua=0.0, radio=0.0, fase=0.0):
        bh = self.bed[self.hielo_y]
        y = self.yh
        lev = lift * suave((y + 110.0) / 105.0)                         # el pie del hielo se despega (más cerca del frente)
        hl = np.where(y >= lengua, 1.6, 0.0) * (lengua < 0)              # la lengua de agua bajo el hielo
        tun = radio * 2.0 * (0.85 + 0.15 * suave((y + 300) / 300))       # el túnel (un poco más ancho cerca del lago)
        hueco = np.maximum(lev, 0) + np.maximum(hl, 0) + tun
        _mover_franja(self.hielo, bh + hueco, self.techo[self.hielo_y] + 0.3 * lev)
        agua_t = np.where(hueco > 0.05, bh + np.minimum(hueco, np.maximum(hueco * 0.9, 0)), bh)
        _mover_franja(self.tunel, bh, agua_t)
        bl = self.bed[~self.hielo_y]
        _mover_franja(self.lago, bl, np.full_like(bl, nivel))
        self.S["agua"].location.z = nivel
        ubicar_tempanos(self.S["tempanos"], nivel)
        mt = bpy.data.materials["agua_tunel"].node_tree
        mt.nodes[bpy.data.materials["agua_tunel"]["mapping"]].inputs["Location"].default_value = (0.0, fase, 0.0)


# ================================================================ E3: el vaso con hielo en la orilla
def orilla(y=520.0, lado=1):
    """x de la orilla (nivel lleno) a esa y, del lado este (lado=1) u oeste (−1)."""
    xs = np.linspace(eje_x(y), eje_x(y) + lado * 700, 1400, dtype=np.float32)
    z = altura_terreno(xs, np.full_like(xs, y))
    i = int(np.argmax(z > 0.35))
    return float(xs[i]), float(z[i])


def vaso(sc, pos):
    """Vaso de vidrio con agua y un cubo de hielo flotando, sobre una roca plana de la orilla. Medidas reales (8 cm de
    diámetro, 12 cm de alto, cubo de 3 cm)."""
    x, y, z = pos
    piedra = roca_hielo(sc, "PiedraVaso", (0.45, 0.35, 0.22), 21, K.mat_concreto("piedra_vaso", (0.22, 0.21, 0.2), escala=9.0))
    piedra.location = (x, y, z + 0.05)
    piedra.rotation_euler = (0, 0, 0.6)
    top = z + 0.05 + 0.22 * 0.82
    v = K.tubo(sc, "Vaso", 0.04, 0.0375, 0.12, (x, y, top), mat=K.mat_acrilico("vidrio_vaso"))
    fondo = K.cilindro(sc, "VasoFondo", 0.0385, 0.008, (x, y, top), mat=K.mat_acrilico("vidrio_vaso_f"))
    m, nt, b = K._nodos("agua_vaso")
    b.inputs["Transmission Weight"].default_value = 1.0
    b.inputs["IOR"].default_value = 1.33
    b.inputs["Roughness"].default_value = 0.0
    b.inputs["Base Color"].default_value = (0.86, 0.95, 0.97, 1)
    ag = K.cilindro(sc, "AguaVaso", 0.0374, 0.08, (x, y, top + 0.008), mat=m)
    bpy.ops.mesh.primitive_cube_add(size=0.03, location=(x, y, top + 0.008 + 0.08 - 0.0125))
    cubo = bpy.context.object; cubo.name = "Cubito"
    bv = cubo.modifiers.new("bisel", "BEVEL"); bv.width = 0.004; bv.segments = 4
    mh, nth, bh = K._nodos("hielo_cubo")
    bh.inputs["Transmission Weight"].default_value = 0.85
    bh.inputs["IOR"].default_value = 1.31
    bh.inputs["Base Color"].default_value = (0.92, 0.97, 1.0, 1)
    rr = K._ruido(nth, escala=40, detalle=6)
    rg = K._mapa(nth, rr.outputs["Fac"], 0.05, 0.3)
    nth.links.new(rg.outputs[0], bh.inputs["Roughness"])
    K._bump(nth, bh, rr.outputs["Fac"], 0.3, 0.001)
    K.asignar(cubo, mh)
    return {"vaso": v, "agua": ag, "cubo": cubo, "piedra": piedra, "z_agua": top + 0.088}
