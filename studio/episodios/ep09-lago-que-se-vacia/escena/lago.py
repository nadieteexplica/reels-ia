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
    # puerta 3 A1: la marca del nivel lleno es una línea nítida (por z casi sin ruido) con una franja oscura de restos
    zl = nt.nodes.new("ShaderNodeMath"); zl.operation = "MULTIPLY_ADD"; zl.inputs[1].default_value = 0.5
    nt.links.new(grande.outputs["Fac"], zl.inputs[0]); nt.links.new(z, zl.inputs[2])
    c2l = mezclar(rango(zl.outputs[0], 0.55, 0.85), c1, lavada.outputs[0])            # sobre el nivel lleno: franja lavada
    mk = nt.nodes.new("ShaderNodeMath"); mk.operation = "MULTIPLY"
    nt.links.new(rango(zl.outputs[0], 0.05, 0.3), mk.inputs[0]); nt.links.new(rango(zl.outputs[0], 1.1, 0.75), mk.inputs[1])
    mk2 = nt.nodes.new("ShaderNodeMath"); mk2.operation = "MULTIPLY"; mk2.inputs[1].default_value = 0.75
    nt.links.new(mk.outputs[0], mk2.inputs[0])
    marca = nt.nodes.new("ShaderNodeMix"); marca.data_type = "RGBA"
    nt.links.new(mk2.outputs[0], marca.inputs[0]); nt.links.new(c2l, marca.inputs[6]); marca.inputs[7].default_value = (0.045, 0.04, 0.036, 1)
    c2a = marca.outputs[2]
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
    alto_n = rango(zz, 600, 760)                                                      # nieve arriba, en lo menos empinado
    plano_n = rango(pend.outputs["Z"], 0.62, 0.82)
    kn0 = nt.nodes.new("ShaderNodeMath"); kn0.operation = "MULTIPLY"; kn0.use_clamp = True
    nt.links.new(alto_n, kn0.inputs[0]); nt.links.new(plano_n, kn0.inputs[1])
    aflo = K._ruido(nt, escala=0.012, detalle=10, estirar=(1.0, 1.0, 0.22))            # roca en la nieve: vetas que bajan por la pendiente
    kaf = rango(aflo.outputs["Fac"], 0.56, 0.5)
    kn = nt.nodes.new("ShaderNodeMath"); kn.operation = "MULTIPLY"; kn.use_clamp = True
    nt.links.new(kn0.outputs[0], kn.inputs[0]); nt.links.new(kaf, kn.inputs[1])
    c6 = mezclar(kn.outputs[0], c5b.outputs[2], nieve.outputs[0])
    nt.links.new(c6, b.inputs["Base Color"])
    camd = nt.nodes.new("ShaderNodeCameraData")
    kh = rango(camd.outputs["View Distance"], 300.0, 3800.0, 0.0, 0.62)
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = (0.5, 0.6, 0.76, 1); em.inputs[1].default_value = 0.45
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
    K._bump(nt, b, s.outputs[0], 0.22, 0.09)
    m["fase"] = 0.0
    return m


# ---------------------------------------------------------------- objetos del set
def terreno(sc, detalle=1.0, xmax=None):
    """Tres mallas: el fondo del lago y sus orillas (fino), el valle cercano y los cerros lejanos (con bruma)."""
    mv = mat_valle()
    n = int(560 * detalle)
    fx1 = 1600 if xmax is None else xmax
    fondo = malla_altura("Fondo", -1600, fx1, -260, 2200, int(n * 1.5 * (fx1 + 1600) / 3200), int(n * 1.1), altura_terreno, mv)
    vx1 = 6000 if xmax is None else xmax
    lejos = malla_altura("Valle", -6000, vx1, -14000, 9000, int(500 * detalle * (vx1 + 6000) / 12000), int(920 * detalle),
                         lambda x, y: np.where((np.abs(x) < 1580) & (y > -250) & (y < 2180), -60.0, altura_terreno(x, y)), mv)
    # cerros lejanos con bruma (formas grandes que llegan al suelo; ESTILO_REALISTA §4.3)
    def picos(x, y):
        d = np.sqrt(x ** 2 + (y - 1500) ** 2)
        base = 1500.0 * suave((d - 4000) / 3500) * (0.55 + 0.6 * cresta(x, y, 21, 2600.0, 6))
        z = base + 300 * fbm(x, y, 23, 1500.0, 5) * suave((d - 4000) / 2000)
        z = np.where(x > 0, z * 0.35, z)              # al este, cerros bajos: por ahí entra el sol de la mañana
        k = suave((d - 5200) / 1500)                  # adentro lo cubre el valle; sube de a poco (sin muro en el borde)
        return -300.0 + (z + 300.0) * k
    cer = malla_altura("Cerros", -20000, 20000, -14000, 26000, 420, 420, picos,
                       K.mat_lejano("cerros_bruma", (0.32, 0.33, 0.36), neblina=(0.55, 0.6, 0.7), k=0.5, color2=(0.75, 0.78, 0.84)))
    return fondo, lejos, cer


def sup_glaciar(x, y):
    """Altura de la superficie del glaciar (la misma de la malla "Glaciar")."""
    x = np.asarray(x, np.float32); y = np.asarray(y, np.float32)
    base = altura_terreno(x, y)
    frente = suave((-y - 18.0) / 6.0)
    transv = np.abs(np.sin((y + 18.0 * fbm(x, y, 49, 180.0, 3)) / 9.0)) ** 0.3
    serac = (14.0 * (cresta(x, y, 43, 55.0, 4) - 0.45) + 4.0 * fbm(x, y, 47, 12.0, 3)
             + 11.0 * (transv - 0.8) * (1 - 0.5 * suave((-y) / 1500.0)))
    zi = NIVEL_LLENO + 38.0 + 0.035 * (-y) + serac * (1 - 0.6 * suave((-y - 3000) / 3000))
    k = suave((ancho(y) * 1.35 - np.abs(x - eje_x(y))) / (ancho(y) * 0.35))
    z = np.where(zi > base, base + (zi - base) * k - 45.0 * (1 - k) ** 2, base - 45.0)
    return np.where(-y > 18.0, base + (z - base) * frente, base - 45.0)


def glaciar(sc, detalle=1.0, xmax=None):
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
    gx1 = 1300 if xmax is None else xmax
    g = malla_altura("Glaciar", -1300, gx1, -9000, 10, int(700 * detalle * (gx1 + 1300) / 2600), int(1100 * detalle), sup, mat_nieve_glaciar())
    # el muro del frente: una malla vertical aparte (los seracs, las grietas y las bandas se ven de frente)
    mx1 = 700 if xmax is None else xmax
    nx, nz = int(700 * detalle * (mx1 + 700) / 1400), int(160 * detalle)
    xs = np.linspace(-700, mx1, nx, dtype=np.float32)
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


def sueltos(sc, centro=(70, 380), radio=170.0, n_piedras=420, n_hielo=160, semilla=5, xmax=None):
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
        if xmax is not None and x > xmax:
            continue
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


def agua(sc, nivel=NIVEL_LLENO, xmax=None):
    x0, x1 = -950.0, (950.0 if xmax is None else xmax)
    bpy.ops.mesh.primitive_plane_add(size=1, location=((x0 + x1) / 2, 900, nivel))
    o = bpy.context.object
    o.name = "Agua"
    o.scale = (x1 - x0, 2400, 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    K.asignar(o, mat_agua_glaciar())
    o.visible_shadow = False
    return o


def nivel_agua(o, nivel):
    o.location.z = nivel


def valle(sc, nivel=NIVEL_LLENO, detalle=1.0, sol_elev=14.0, sol_rot=78.0, xmax=None):
    """Arma el set completo. Sol de la mañana desde el este (14°): cruza bajo sobre la ladera este (baja) y le pega de costado a los témpanos y al frente; desde un poco al norte para que la sombra del glaciar no caiga sobre el lago: pasa sobre la ladera este (más baja) y le pega de
    costado al frente del glaciar, que mira al norte. Nunca de frente ni detrás de la cámara (luz plana)."""
    w, sol, d = K.cielo_atardecer(sc, elev=sol_elev, rot=sol_rot, fuerza=0.14, sol=3.4, color_sol=(1.0, 0.82, 0.66))
    sky = next(n for n in w.node_tree.nodes if n.type == "TEX_SKY")
    sky.altitude = 400
    sky.aerosol_density = 2.2
    sky.sun_disc = False          # el disco del cielo físico suma un segundo sol (con el sol a 11–20° lo lavaba todo)
    t = terreno(sc, detalle, xmax)
    g, muro = glaciar(sc, detalle, xmax)
    tem = tempanos(sc)
    if xmax is not None:
        for o in tem:
            if o["x"] + max(o.dimensions) * 0.6 > xmax:
                o.hide_render = True
    su = sueltos(sc, xmax=xmax)
    ag = agua(sc, nivel, xmax)
    ubicar_tempanos(tem, nivel)
    return {"terreno": t, "glaciar": g, "muro": muro, "tempanos": tem, "sueltos": su, "agua": ag, "sol": sol}


# ================================================================ E2: la represa en corte
XC = 24.0                      # plano del corte (x), por el eje del valle junto a la represa
Y0C, Y1C = -420.0, 420.0       # tramo del valle que se abre
Y_FRENTE = -5.0                # el frente de hielo en el corte


def _perfil_hielo(y):
    """Techo del hielo en el corte (z), del glaciar real del set, con grietas en V (el glaciar se parte arriba)."""
    g = np.asarray(y, np.float32)
    x = np.full_like(g, XC)
    base = altura_terreno(x, g)
    serac = 14.0 * (cresta(x, g, 43, 55.0, 4) - 0.45) + 4.0 * fbm(x, g, 47, 12.0, 3)
    zi = sup_glaciar(x, np.minimum(g, -24.0)) + 0.5                      # la superficie real del glaciar en el plano del corte
    r = random.Random(17)
    grietas = np.zeros_like(g)
    yc = Y_FRENTE - 14.0
    while yc > Y0C:
        w, d = r.uniform(2.0, 4.5), r.uniform(10.0, 24.0)
        grietas = np.maximum(grietas, d * np.clip(1 - np.abs(g - yc) / w, 0, 1) ** 0.7)
        yc -= r.uniform(22.0, 48.0)
    return np.maximum(zi - grietas, base + 30.0)


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
    """Roca cortada: estratos ondulados grises y cafés con vetas claras y fracturas finas."""
    m, nt, b = K._nodos("roca_corte")
    m["corte"] = 1
    capas = K._ruido(nt, escala=0.09, detalle=8, estirar=(0.4, 0.4, 1.0))
    capas.inputs["Distortion"].default_value = 2.5
    r = nt.nodes.new("ShaderNodeValToRGB")
    els = r.color_ramp.elements
    els[0].position, els[0].color = 0.3, (0.05, 0.045, 0.04, 1)
    els[1].position, els[1].color = 0.72, (0.3, 0.27, 0.22, 1)
    e = els.new(0.47); e.color = (0.16, 0.13, 0.1, 1)
    e = els.new(0.55); e.color = (0.24, 0.23, 0.21, 1)
    nt.links.new(capas.outputs["Fac"], r.inputs[0])
    veta = K._ruido(nt, escala=0.25, detalle=6, estirar=(0.25, 0.25, 1.0))
    kv = K._mapa(nt, veta.outputs["Fac"], 0.0, 1.0); kv.inputs["From Min"].default_value = 0.66; kv.inputs["From Max"].default_value = 0.7
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
    k2 = nt.nodes.new("ShaderNodeMath"); k2.operation = "MULTIPLY"; k2.inputs[1].default_value = 0.6
    nt.links.new(kv.outputs[0], k2.inputs[0]); nt.links.new(k2.outputs[0], mx.inputs[0])
    nt.links.new(r.outputs[0], mx.inputs[6]); mx.inputs[7].default_value = (0.5, 0.48, 0.44, 1)
    gr = K._ruido(nt, escala=0.35, detalle=10)
    kg = K._mapa(nt, gr.outputs["Fac"], 0.55, 1.3)
    cg = nt.nodes.new("ShaderNodeCombineColor"); [nt.links.new(kg.outputs[0], cg.inputs[i]) for i in range(3)]
    mm = nt.nodes.new("ShaderNodeMix"); mm.data_type = "RGBA"; mm.blend_type = "MULTIPLY"; mm.inputs[0].default_value = 1.0
    nt.links.new(mx.outputs[2], mm.inputs[6]); nt.links.new(cg.outputs[0], mm.inputs[7])
    cl = nt.nodes.new("ShaderNodeTexVoronoi"); cl.inputs["Scale"].default_value = 0.9; cl.inputs["Randomness"].default_value = 1.0
    tcr = nt.nodes.new("ShaderNodeTexCoord"); nt.links.new(tcr.outputs["Object"], cl.inputs["Vector"])
    kcl = K._mapa(nt, cl.outputs["Distance"], 0.0, 1.0); kcl.inputs["From Min"].default_value = 0.0; kcl.inputs["From Max"].default_value = 0.35
    mcl = nt.nodes.new("ShaderNodeMix"); mcl.data_type = "RGBA"; mcl.blend_type = "MULTIPLY"
    kk = nt.nodes.new("ShaderNodeMath"); kk.operation = "SUBTRACT"; kk.inputs[0].default_value = 1.0; nt.links.new(kcl.outputs[0], kk.inputs[1])
    kk2 = nt.nodes.new("ShaderNodeMath"); kk2.operation = "MULTIPLY"; kk2.inputs[1].default_value = 0.45; nt.links.new(kk.outputs[0], kk2.inputs[0])
    nt.links.new(kk2.outputs[0], mcl.inputs[0]); nt.links.new(mm.outputs[2], mcl.inputs[6]); mcl.inputs[7].default_value = (0.45, 0.42, 0.38, 1)
    nt.links.new(mcl.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.9
    s = nt.nodes.new("ShaderNodeMath"); s.operation = "ADD"; nt.links.new(gr.outputs["Fac"], s.inputs[0]); nt.links.new(cl.outputs["Distance"], s.inputs[1])
    K._bump(nt, b, s.outputs[0], 0.8, 0.6)
    return m


def mat_till_corte():
    """La morrena de fondo bajo el hielo: ripio café."""
    m, nt, b = K._nodos("till_corte")
    m["corte"] = 1
    n = K._ruido(nt, escala=2.5, detalle=6)
    c = K._rampa(nt, n.outputs["Fac"], (0.12, 0.09, 0.06), (0.3, 0.24, 0.17))
    nt.links.new(c.outputs[0], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.95
    K._bump(nt, b, n.outputs["Fac"], 0.6, 0.2)
    return m


def mat_hielo_corte():
    """La cara del hielo cortado: blanco celeste arriba y azul cada vez más hondo hacia abajo (el hielo viejo y apretado es
    azul), moteado, con capas finas de polvo (años de nieve) y fracturas verticales finas."""
    m, nt, b = K._nodos("hielo_corte")
    m["corte"] = 1
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sp.inputs[0])
    prof = K._mapa(nt, sp.outputs["Z"], 0.0, 1.0); prof.inputs["From Min"].default_value = -36; prof.inputs["From Max"].default_value = 50
    r = nt.nodes.new("ShaderNodeValToRGB")
    els = r.color_ramp.elements
    els[0].position, els[0].color = 0.0, (0.04, 0.16, 0.32, 1)
    els[1].position, els[1].color = 1.0, (0.74, 0.81, 0.86, 1)
    e = els.new(0.3); e.color = (0.18, 0.38, 0.58, 1)
    e = els.new(0.65); e.color = (0.5, 0.66, 0.78, 1)
    nt.links.new(prof.outputs[0], r.inputs[0])
    mot = K._ruido(nt, escala=0.12, detalle=6)
    km = K._mapa(nt, mot.outputs["Fac"], 0.72, 1.25)
    cg = nt.nodes.new("ShaderNodeCombineColor"); [nt.links.new(km.outputs[0], cg.inputs[i]) for i in range(3)]
    m1 = nt.nodes.new("ShaderNodeMix"); m1.data_type = "RGBA"; m1.blend_type = "MULTIPLY"; m1.inputs[0].default_value = 1.0
    nt.links.new(r.outputs[0], m1.inputs[6]); nt.links.new(cg.outputs[0], m1.inputs[7])
    capas = K._ruido(nt, escala=0.45, detalle=6, estirar=(0.02, 0.02, 1.0))
    capas.inputs["Distortion"].default_value = 0.6
    kc = K._mapa(nt, capas.outputs["Fac"], 0.0, 1.0); kc.inputs["From Min"].default_value = 0.6; kc.inputs["From Max"].default_value = 0.66
    m2 = nt.nodes.new("ShaderNodeMix"); m2.data_type = "RGBA"
    f = nt.nodes.new("ShaderNodeMath"); f.operation = "MULTIPLY"; f.inputs[1].default_value = 0.7
    nt.links.new(kc.outputs[0], f.inputs[0]); nt.links.new(f.outputs[0], m2.inputs[0])
    nt.links.new(m1.outputs[2], m2.inputs[6]); m2.inputs[7].default_value = (0.2, 0.19, 0.18, 1)
    fr = K._ruido(nt, escala=0.35, detalle=4, estirar=(1.0, 1.0, 0.06))
    kf = K._mapa(nt, fr.outputs["Fac"], 0.0, 1.0); kf.inputs["From Min"].default_value = 0.68; kf.inputs["From Max"].default_value = 0.72
    m3 = nt.nodes.new("ShaderNodeMix"); m3.data_type = "RGBA"
    f2 = nt.nodes.new("ShaderNodeMath"); f2.operation = "MULTIPLY"; f2.inputs[1].default_value = 0.55
    nt.links.new(kf.outputs[0], f2.inputs[0]); nt.links.new(f2.outputs[0], m3.inputs[0])
    nt.links.new(m2.outputs[2], m3.inputs[6]); m3.inputs[7].default_value = (0.03, 0.12, 0.25, 1)
    nt.links.new(m3.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.35
    bub = K._ruido(nt, escala=3.0, detalle=4)
    s = nt.nodes.new("ShaderNodeMath"); s.operation = "ADD"; nt.links.new(bub.outputs["Fac"], s.inputs[0]); nt.links.new(fr.outputs["Fac"], s.inputs[1])
    K._bump(nt, b, s.outputs[0], 0.45, 0.25)
    return m


def mat_agua_corte(nombre="agua_corte", brillo=0.0):
    """El agua cortada: turquesa arriba y oscura abajo, con limo en suspensión y rayos de luz que bajan. El agua del túnel
    tiene estelas claras que corren (valor "fase" que se mueve por cuadro)."""
    m, nt, b = K._nodos(nombre)
    m["corte"] = 1
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping"); nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    mp.inputs["Scale"].default_value = (1.0, 0.05, 1.0)
    st = nt.nodes.new("ShaderNodeTexNoise"); st.inputs["Scale"].default_value = 0.7; st.inputs["Detail"].default_value = 3
    nt.links.new(mp.outputs[0], st.inputs["Vector"])
    m["mapping"] = mp.name
    sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sp.inputs[0])
    prof = K._mapa(nt, sp.outputs["Z"], 0.0, 1.0); prof.inputs["From Min"].default_value = -36; prof.inputs["From Max"].default_value = 1
    c = K._rampa(nt, prof.outputs[0], (0.006, 0.03, 0.05), (0.09, 0.34, 0.37), (0.05, 1.0))
    limo = K._ruido(nt, escala=0.08, detalle=6)
    kl = K._mapa(nt, limo.outputs["Fac"], 0.65, 1.35)
    rayos = K._ruido(nt, escala=0.05, detalle=2, estirar=(1.0, 1.0, 0.04))
    kr = K._mapa(nt, rayos.outputs["Fac"], 0.0, 1.0); kr.inputs["From Min"].default_value = 0.55; kr.inputs["From Max"].default_value = 0.75
    luz = nt.nodes.new("ShaderNodeMath"); luz.operation = "MULTIPLY"; nt.links.new(kr.outputs[0], luz.inputs[0]); nt.links.new(prof.outputs[0], luz.inputs[1])
    c2 = nt.nodes.new("ShaderNodeMix"); c2.data_type = "RGBA"; c2.blend_type = "MULTIPLY"; c2.inputs[0].default_value = 1.0
    nt.links.new(c.outputs[0], c2.inputs[6])
    cg = nt.nodes.new("ShaderNodeCombineColor"); [nt.links.new(kl.outputs[0], cg.inputs[i]) for i in range(3)]
    nt.links.new(cg.outputs[0], c2.inputs[7])
    c3 = nt.nodes.new("ShaderNodeMix"); c3.data_type = "RGBA"; c3.blend_type = "ADD"
    k3 = nt.nodes.new("ShaderNodeMath"); k3.operation = "MULTIPLY"; k3.inputs[1].default_value = 0.22
    nt.links.new(luz.outputs[0], k3.inputs[0]); nt.links.new(k3.outputs[0], c3.inputs[0])
    nt.links.new(c2.outputs[2], c3.inputs[6]); c3.inputs[7].default_value = (0.6, 0.9, 0.95, 1)
    est = K._mapa(nt, st.outputs["Fac"], 0.0, 1.0); est.inputs["From Min"].default_value = 0.52; est.inputs["From Max"].default_value = 0.75
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
    k = nt.nodes.new("ShaderNodeMath"); k.operation = "MULTIPLY"; k.inputs[1].default_value = 0.0 if not brillo else 0.45
    nt.links.new(est.outputs[0], k.inputs[0]); nt.links.new(k.outputs[0], mx.inputs[0])
    nt.links.new(c3.outputs[2], mx.inputs[6]); mx.inputs[7].default_value = (0.75, 0.93, 0.97, 1)
    nt.links.new(mx.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.15
    b.inputs["Emission Color"].default_value = (0.3, 0.75, 0.85, 1)
    ke = nt.nodes.new("ShaderNodeMath"); ke.operation = "MULTIPLY"; ke.inputs[1].default_value = 0.25
    nt.links.new(k.outputs[0], ke.inputs[0]); nt.links.new(ke.outputs[0], b.inputs["Emission Strength"])
    return m


def mat_hueco_tunel():
    """La pared del fondo del túnel (detrás del agua que corre): hielo azul oscuro en sombra."""
    m, nt, b = K._nodos("hueco_tunel")
    m["corte"] = 1
    n = K._ruido(nt, escala=0.12, detalle=3, estirar=(1.0, 0.3, 1.0))
    c = K._rampa(nt, n.outputs["Fac"], (0.005, 0.03, 0.07), (0.02, 0.09, 0.16))
    nt.links.new(c.outputs[0], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.25
    K._bump(nt, b, n.outputs["Fac"], 0.2, 0.3)
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


TOE = 28.0                     # el pie de hielo sumergido que entra en el lago (cuña): es lo que flota y se levanta


class Corte:
    """La represa abierta de costado, en el set del valle (geometría sólo hasta x = XC). estado(nivel, lift, lengua, radio,
    fase) la mueve por cuadro: nivel = nivel del lago (m) · lift = cuánto se despega el pie del hielo (m, un poco
    exagerado para que se vea) · lengua = hasta dónde llega el agua bajo el hielo (y) · radio = medio alto del túnel (m)
    · fase = corrida de las estelas. El frente tiene un pie sumergido en cuña (TOE m dentro del lago, ~7 m de hielo bajo
    ~25 m de agua): flota, como el témpano del plano 5, y es lo que se levanta. Encima de la cara cortada va una línea
    clara (capa de explicación: "esto es un corte")."""

    def __init__(self, sc, S):
        self.S = S
        self.ys = np.linspace(Y0C, Y1C, 1681).astype(np.float32)
        y = self.ys
        self.bed = altura_terreno(np.full_like(y, XC), y)
        techo = _perfil_hielo(y)
        cuna = np.clip((Y_FRENTE + TOE - y) / TOE, 0, 1)
        pie = self.bed + 3.0 + 7.0 * np.sqrt(cuna)
        self.techo = np.where(y <= Y_FRENTE, techo, np.where(y <= Y_FRENTE + TOE, pie, self.bed))
        self.hay_hielo = y <= Y_FRENTE + TOE
        z0 = np.full_like(y, -420.0)
        till = self.bed - 3.0 - 1.2 * fbm(np.full_like(y, 5.0), y, 71, 9.0, 3)
        self.roca = _franja("CorteRoca", y, z0, till, mat_roca_corte())
        self.till = _franja("CorteTill", y, till, self.bed, mat_till_corte(), x=XC + 0.02)
        self.hielo = _franja("CorteHielo", y, self.bed, self.techo, mat_hielo_corte())
        self.hueco = _franja("CorteHueco", y, self.bed, self.bed, mat_hueco_tunel(), x=XC - 0.6)
        self.tunel = _franja("CorteTunel", y, self.bed, self.bed, mat_agua_corte("agua_tunel", brillo=1), x=XC + 0.04)
        self.lado_lago = y > Y_FRENTE
        yl = y[self.lado_lago]
        self.lago = _franja("CorteLago", yl, self.bed[self.lado_lago], self.bed[self.lado_lago], mat_agua_corte())
        ml = K.mat_emision("linea_corte", (1.0, 0.82, 0.55), 2.2)
        self.sel_h = y <= Y_FRENTE - 0.5
        self.sel_l = y > Y_FRENTE + 0.5
        self.linea = _franja("CorteLinea", y[self.sel_h], self.bed[self.sel_h], self.bed[self.sel_h], ml, x=XC + 0.12)
        self.linea_l = _franja("CorteLineaLago", y[self.sel_l], self.bed[self.sel_l], self.bed[self.sel_l], ml, x=XC + 0.12)
        self.linea.visible_shadow = False; self.linea_l.visible_shadow = False

    def estado(self, nivel, lift=0.0, lengua=0.0, radio=0.0, fase=0.0):
        y, bed = self.ys, self.bed
        h = self.hay_hielo
        lev = lift * suave((y + 110.0) / 105.0) * h
        hl = np.where((y >= lengua) & h, 1.6, 0.0) * (lengua < 0)
        tun = radio * 2.0 * (0.85 + 0.15 * suave((y + 300) / 300)) * suave((Y_FRENTE + TOE * 0.6 - y) / 14.0)
        hueco = (lev + hl + tun) * h
        abajo = bed + hueco
        arriba = np.where(h, self.techo + lev * np.where(y > Y_FRENTE, 1.0, 0.3), bed)
        _mover_franja(self.hielo, abajo, arriba)
        agua_t = np.where(hueco > 0.05, bed + np.where(tun > 0.5, 0.62 * hueco, hueco), bed)
        _mover_franja(self.tunel, bed, agua_t)
        _mover_franja(self.hueco, bed - 1.0, np.where(hueco > 0.05, abajo + 1.5, bed - 1.0))
        fondo_lago = np.where(h, np.maximum(arriba, bed), bed)[self.lado_lago]
        _mover_franja(self.lago, fondo_lago, np.maximum(nivel, fondo_lago))
        _mover_franja(self.linea, arriba[self.sel_h] - 0.55, arriba[self.sel_h] + 0.05)
        tl = np.maximum(bed, nivel)[self.sel_l]
        _mover_franja(self.linea_l, tl - 0.55, tl + 0.05)
        self.linea_l.hide_render = nivel < float(np.min(bed[self.sel_l])) + 1.0
        self.S["agua"].location.z = nivel
        ubicar_tempanos(self.S["tempanos"], nivel)
        mt = bpy.data.materials["agua_tunel"].node_tree
        mt.nodes[bpy.data.materials["agua_tunel"]["mapping"]].inputs["Location"].default_value = (0.0, fase, 0.0)

    def contacto(self, y=-20.0):
        i = int(np.argmin(np.abs(self.ys - y)))
        return (XC, float(self.ys[i]), float(self.bed[i]))


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


# ================================================================ E2: un témpano flotando, en corte (P4: "el hielo flota")
def tempano_corte(sc, y0=38.0, y1=78.0, alto=26.0, nivel=NIVEL_LLENO):
    """Un témpano cortado por el plano del corte: ~1/8 sobre el agua y el resto abajo (el hielo flota)."""
    ys = np.linspace(y0, y1, 120).astype(np.float32)
    u = (ys - y0) / (y1 - y0)
    forma = np.sqrt(np.clip(np.sin(np.pi * u), 0, 1))
    rug = 0.8 * fbm(np.full_like(ys, 3.0), ys * 3, 91, 6.0, 3)
    arriba = nivel + (alto / 8.0) * forma * (0.8 + 0.3 * np.sin(u * 7.0)) + rug * forma
    abajo = nivel - (alto * 7.0 / 8.0) * forma * (0.85 + 0.15 * np.cos(u * 5.0)) + rug * forma
    o = _franja("TempanoCorte", ys, abajo, arriba, mat_hielo_corte(), x=XC + 0.08)
    return o


# ================================================================ E4: el río de abajo (la junta con el río grande)
RIO_NORMAL = -1.6
RIO_CRECIDA = 0.5


Y_HOCICO = -760.0               # el frente del glaciar Colonia en E4: de ahí sale el río que trae el agua del lago


def xt_rio(y):
    """Eje del afluente (el río que sale del glaciar)."""
    return 40.0 * np.sin(np.asarray(y, np.float32) / 160.0)


def altura_rio(x, y):
    """Valle ancho con una llanura de ripio: el río grande corre en x (de izquierda a derecha, río abajo = +x) y el
    afluente (el que trae el agua del lago) entra desde el sur (y < 0) en x ≈ 0; viene de un valle lateral que nace en
    el frente del glaciar (Y_HOCICO)."""
    xx = np.asarray(x, np.float32); yy = np.asarray(y, np.float32)
    lado = np.abs(yy - 30.0 * np.sin(xx / 400.0))
    llanura = 1.6 + 1.7 * fbm(xx, yy, 61, 90.0, 5) + 0.3 * fbm(xx, yy, 63, 9.0, 3)
    cauce = -6.0 * np.exp(-(lado / 75.0) ** 2)                                         # el río grande
    dx = xx - xt_rio(yy)
    an = 50.0 + 45.0 * suave((-yy - 450.0) / 250.0)
    trib = -8.0 * np.exp(-(dx / an) ** 2) * suave((-yy + 20.0) / 80.0) * suave((yy - Y_HOCICO + 40.0) / 30.0)   # el afluente
    trenzas = -1.2 * (cresta(xx * 0.5, yy, 65, 50.0, 3) > 0.62) * suave((-yy - 60.0) / 200.0) * (np.abs(xx) < 260)
    V = np.exp(-(dx / 260.0) ** 2) * suave((-yy - 250.0) / 300.0)                      # el valle lateral del glaciar
    terraza = 3.0 * suave((lado - 380.0) / 60.0) * (1 - V)
    ladera = 520.0 * suave((lado - 650.0) / 900.0) ** 1.3 + 90.0 * (cresta(xx, yy, 67, 300.0, 5) - 0.4) * suave((lado - 650.0) / 200.0)
    ladera = ladera * (1 - 0.9 * V)
    loma = 2.6 * np.exp(-(((xx - 655.0) / 70.0) ** 2 + ((yy + 222.0) / 45.0) ** 2))       # la lomita de las casas
    brazo = -3.6 * np.exp(-((yy + 150.0 - 0.1 * (xx - 650.0) + 14.0 * fbm(xx, yy, 103, 60.0, 3)) / 32.0) ** 2) * np.exp(-((xx - 650.0) / 420.0) ** 2)   # un brazo del río junto a las casas
    return loma + brazo + llanura + np.minimum(0.0, cauce + trib) + trenzas + terraza + ladera


def hocico(sc, detalle=1.0):
    """El frente del glaciar Colonia (vista E4): una lengua ancha de hielo que termina en un muro de ~32 m sobre el río,
    con seracs y grietas, y una boca oscura abajo al medio, por donde sale el agua del lago."""
    xs = np.linspace(-700, 760, int(380 * detalle) + 2, dtype=np.float32)
    # filas densas cerca del frente (el muro es casi vertical) y ralas atrás
    d = np.concatenate([np.linspace(-30, 40, int(70 * detalle) + 2), np.linspace(42, 2400, int(140 * detalle) + 2)[1:]]).astype(np.float32)
    X, Dd = np.meshgrid(xs, d)
    curva = 0.0022 * (X - 40.0) ** 2                                   # el frente es un lóbulo: los lados quedan atrás
    Y = Y_HOCICO - Dd - curva
    base = altura_rio(X, Y) + 20.0
    serac = 7.0 * (cresta(X, Y, 81, 40.0, 4) - 0.45) + 2.5 * fbm(X, Y, 83, 9.0, 3)
    transv = np.abs(np.sin((Y + 14.0 * fbm(X, Y, 85, 150.0, 3)) / 8.0)) ** 0.3
    serac = serac + 3.0 * (transv - 0.8)
    H = -6.0 + 40.0 * suave((Dd + 2.0) / 9.0) + 0.05 * np.maximum(Dd, 0) + serac * suave(Dd / 12.0)
    lado = np.abs(X - xt_rio(Y))
    k = suave((520.0 - lado) / 220.0)
    zi = 20.0 + H * k - 8.0 * (1 - k)
    Z = np.where(zi > base, zi, base - 4.0)
    xb0 = 40.0 * math.sin(Y_HOCICO / 160.0)
    hueco = (np.abs(X - xb0) < 19.0) & (Dd < 26.0)          # el túnel de la boca pasa por aquí (la cara de atrás queda detrás)
    Z = np.where(hueco, base - 4.0, Z)
    verts = np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)
    nx, ny = len(xs), len(d)
    idx = np.arange(nx * ny).reshape(ny, nx)
    a = idx[:-1, :-1].ravel(); b_ = idx[:-1, 1:].ravel(); c = idx[1:, 1:].ravel(); dd = idx[1:, :-1].ravel()
    caras = np.stack([a, dd, c, b_], 1)
    me = bpy.data.meshes.new("Hocico")
    me.vertices.add(len(verts)); me.vertices.foreach_set("co", verts.ravel())
    me.loops.add(len(caras) * 4); me.loops.foreach_set("vertex_index", caras.ravel())
    me.polygons.add(len(caras)); me.polygons.foreach_set("loop_start", np.arange(0, len(caras) * 4, 4)); me.polygons.foreach_set("loop_total", np.full(len(caras), 4))
    me.update(); me.validate()
    o = bpy.data.objects.new("Hocico", me); sc.collection.objects.link(o)
    for pgn in me.polygons:
        pgn.use_smooth = True
    K.asignar(o, mat_hielo("hielo_hocico", sucio=0.45))
    # el muro: malla vertical por delante del borde, con columnas y seracs, y un hueco en arco (la boca)
    xb = 40.0 * math.sin(Y_HOCICO / 160.0)
    R, Hb, P = 17.0, 15.0, 24.0
    xs3 = np.linspace(xb - 340, xb + 340, int(340 * detalle) + 2, dtype=np.float32)
    zs3 = np.linspace(10.0, 70.0, int(90 * detalle) + 2, dtype=np.float32)
    Xm, Zm = np.meshgrid(xs3, zs3)
    yfr = Y_HOCICO - 0.0022 * (Xm - 40.0) ** 2
    Ym = (yfr + 1.5 - 3.5 * (cresta(Xm, Zm * 0.12, 91, 11.0, 4) - 0.45) - 0.9 * fbm(Xm, Zm, 93, 6.0, 4))   # columnas verticales
    def sup_en(x, dd):
        yy = Y_HOCICO - dd - 0.0022 * (x - 40.0) ** 2
        bb = altura_rio(x, yy) + 20.0
        s_ = 7.0 * (cresta(x, yy, 81, 40.0, 4) - 0.45) + 2.5 * fbm(x, yy, 83, 9.0, 3)
        tv = np.abs(np.sin((yy + 14.0 * fbm(x, yy, 85, 150.0, 3)) / 8.0)) ** 0.3
        s_ = s_ + 6.0 * (tv - 0.8)
        hh = -6.0 + 40.0 * suave((dd + 2.0) / 9.0) + 0.05 * np.maximum(dd, 0) + s_ * suave(dd / 12.0)
        kk = suave((520.0 - np.abs(x - xt_rio(yy))) / 220.0)
        zz = 20.0 + hh * kk - 8.0 * (1 - kk)
        return np.where(zz > bb, zz, bb - 4.0), bb
    techo, piso = sup_en(xs3, np.full_like(xs3, 9.0))
    techo = techo - 1.0
    Zc = np.clip(Zm, piso[None, :] - 3.0, techo[None, :])
    Ym = np.where(Zm > techo[None, :] - 6.0, Ym - 6.0 * np.clip((Zm - techo[None, :] + 6.0) / 6.0, 0, 1), Ym)
    nx3, nz3 = len(xs3), len(zs3)
    verts = np.stack([Xm.ravel(), Ym.ravel(), Zc.ravel()], 1)
    idx = np.arange(nx3 * nz3).reshape(nz3, nx3)
    a_ = idx[:-1, :-1].ravel(); b_ = idx[:-1, 1:].ravel(); c_ = idx[1:, 1:].ravel(); d_ = idx[1:, :-1].ravel()
    cx = (Xm[:-1, :-1] + Xm[1:, 1:]).ravel() / 2; cz = (Zm[:-1, :-1] + Zm[1:, 1:]).ravel() / 2
    fuera = ((cx - xb) / R) ** 2 + ((cz - 17.0) / Hb) ** 2 > 1.0
    # los vértices del borde del hueco se llevan al óvalo (si no, el borde queda en escalera)
    vx, vz = verts[:, 0], verts[:, 2]
    e = ((vx - xb) / R) ** 2 + ((vz - 17.0) / Hb) ** 2
    dentro = (e < 1.35) & (vz > 12.0)
    s_ = 1.0 / np.sqrt(np.maximum(e, 1e-4))
    verts[dentro, 0] = xb + (vx[dentro] - xb) * s_[dentro]
    verts[dentro, 2] = 17.0 + (vz[dentro] - 17.0) * s_[dentro]
    caras = np.stack([a_, b_, c_, d_], 1)[fuera]
    me = bpy.data.meshes.new("MuroHocico")
    me.vertices.add(len(verts)); me.vertices.foreach_set("co", verts.ravel())
    me.loops.add(len(caras) * 4); me.loops.foreach_set("vertex_index", caras.ravel())
    me.polygons.add(len(caras)); me.polygons.foreach_set("loop_start", np.arange(0, len(caras) * 4, 4)); me.polygons.foreach_set("loop_total", np.full(len(caras), 4))
    me.update(); me.validate()
    mu = bpy.data.objects.new("MuroHocico", me); sc.collection.objects.link(mu)
    for pgn in me.polygons:
        pgn.use_smooth = True
    K.asignar(mu, mat_hielo("hielo_muro_rio", sucio=0.5))
    # la boca: túnel en medio óvalo que se mete P m en el hielo (oscuro adentro)
    yb = Y_HOCICO + 1.5
    n = 48
    ang = np.linspace(0, math.pi, n)
    verts, caras = [], []
    for j, prof in enumerate((0.0, 0.4, 1.0)):
        esc = (1.0, 0.85, 0.55)[j]
        for t_ in ang:
            verts.append((xb + R * esc * math.cos(t_), yb - prof * P, 17.0 + Hb * esc * math.sin(t_)))
    for j in range(2):
        for i in range(n - 1):
            caras.append((j * n + i, (j + 1) * n + i, (j + 1) * n + i + 1, j * n + i + 1))
    verts.append((xb, yb - P, 17.0))
    for i in range(n - 1):
        caras.append((2 * n + i, len(verts) - 1, 2 * n + i + 1))
    me = bpy.data.meshes.new("Boca"); me.from_pydata(verts, [], caras); me.update()
    bo = bpy.data.objects.new("Boca", me); sc.collection.objects.link(bo)
    for pgn in me.polygons:
        pgn.use_smooth = True
    m, nt, bs = K._nodos("boca")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ"); tcb = nt.nodes.new("ShaderNodeTexCoord"); nt.links.new(tcb.outputs["Object"], sp.inputs[0])
    pr = K._mapa(nt, sp.outputs["Y"], 0.0, 1.0); pr.inputs["From Min"].default_value = yb - P; pr.inputs["From Max"].default_value = yb - 2.0
    cc = K._rampa(nt, pr.outputs[0], (0.0, 0.004, 0.012), (0.05, 0.2, 0.36), (0.5, 0.97))
    nt.links.new(cc.outputs[0], bs.inputs["Base Color"])
    bs.inputs["Emission Color"].default_value = (0.05, 0.3, 0.6, 1)               # luz azul que pasa por el hielo, al fondo
    ke = K._mapa(nt, pr.outputs[0], 0.1, 0.0); nt.links.new(ke.outputs[0], bs.inputs["Emission Strength"])
    bs.inputs["Roughness"].default_value = 0.15
    est = K._ruido(nt, escala=0.3, detalle=6, estirar=(1.0, 1.0, 0.2))
    K._bump(nt, bs, est.outputs["Fac"], 0.6, 0.5)
    K.asignar(bo, m)
    # el borbollón: el agua sale empujando y se levanta en un domo de espuma café
    xs2 = np.linspace(xb - 60, xb + 60, int(90 * detalle) + 2, dtype=np.float32)
    ys2 = np.linspace(Y_HOCICO - 4, Y_HOCICO + 90, int(140 * detalle) + 2, dtype=np.float32)
    def domo(x, y):
        r2 = ((x - xb) / 24.0) ** 2 + ((y - Y_HOCICO - 14.0) / 26.0) ** 2
        return 2.4 * np.exp(-r2) * (0.7 + 0.6 * fbm(x, y, 87, 6.0, 3)) + 0.25 * fbm(x, y, 89, 3.0, 3) - 0.3
    bb = malla_altura("Borbollon", xs2[0], xs2[-1], ys2[0], ys2[-1], len(xs2), len(ys2), domo, mat_espuma())
    bb.location.z = 20.0 + RIO_NORMAL
    bb.visible_shadow = False
    return o, bb


def mat_espuma():
    """Agua café revuelta con espuma blanca (donde el agua sale a presión)."""
    m, nt, b = K._nodos("espuma")
    n = K._ruido(nt, escala=0.35, detalle=8)
    n2 = K._ruido(nt, escala=0.06, detalle=4)
    s = nt.nodes.new("ShaderNodeMath"); s.operation = "ADD"; nt.links.new(n.outputs["Fac"], s.inputs[0]); nt.links.new(n2.outputs["Fac"], s.inputs[1])
    c = K._rampa(nt, s.outputs[0], (0.2, 0.15, 0.1), (0.72, 0.68, 0.6), (0.95, 1.2))
    nt.links.new(c.outputs[0], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.35
    K._bump(nt, b, n.outputs["Fac"], 0.5, 0.4)
    tr = nt.nodes.new("ShaderNodeMapping")  # (marcador para mover la espuma)
    m["flujo"] = 1
    return m


def mat_agua_rio():
    """Agua del río grande (turquesa) con la mancha café del vaciamiento: café donde x está entre "arriba" y "abajo"
    (valores del material que se mueven por cuadro) o en el afluente."""
    m, nt, b = K._nodos("agua_rio")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(geo.outputs["Position"], sp.inputs[0])
    v_ar = nt.nodes.new("ShaderNodeValue"); v_ar.name = "arriba"; v_ar.outputs[0].default_value = 0.0
    v_ab = nt.nodes.new("ShaderNodeValue"); v_ab.name = "abajo"; v_ab.outputs[0].default_value = 0.0
    nz = K._ruido(nt, escala=0.012, detalle=4)
    def op(o, a, bb):
        n = nt.nodes.new("ShaderNodeMath"); n.operation = o
        for i, s in enumerate((a, bb)):
            if isinstance(s, (int, float)):
                n.inputs[i].default_value = s
            else:
                nt.links.new(s, n.inputs[i])
        return n.outputs[0]
    borde = op("MULTIPLY", op("SUBTRACT", nz.outputs["Fac"], 0.5), 420.0)
    xr = op("ADD", sp.outputs["X"], borde)
    k1 = op("MINIMUM", op("MAXIMUM", op("DIVIDE", op("SUBTRACT", xr, v_ar.outputs[0]), 90.0), 0.0), 1.0)
    k2 = op("MINIMUM", op("MAXIMUM", op("DIVIDE", op("SUBTRACT", v_ab.outputs[0], xr), 90.0), 0.0), 1.0)
    trib = op("LESS_THAN", sp.outputs["Y"], -40.0)
    k = op("MAXIMUM", op("MULTIPLY", k1, k2), op("MULTIPLY", trib, op("GREATER_THAN", v_ab.outputs[0], -500.0)))
    turq = K._rampa(nt, nz.outputs["Fac"], (0.03, 0.2, 0.24), (0.06, 0.3, 0.33))
    cafe = K._rampa(nt, nz.outputs["Fac"], (0.15, 0.095, 0.045), (0.29, 0.19, 0.09))
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
    nt.links.new(k, mx.inputs[0]); nt.links.new(turq.outputs[0], mx.inputs[6]); nt.links.new(cafe.outputs[0], mx.inputs[7])
    # estelas: ruido estirado a lo largo del afluente, que corre (nodo "flujo_y")
    tcs = nt.nodes.new("ShaderNodeTexCoord")
    fy = nt.nodes.new("ShaderNodeMapping"); fy.name = "flujo_y"; fy.inputs["Scale"].default_value = (1.0, 0.12, 1.0)
    nt.links.new(tcs.outputs["Object"], fy.inputs["Vector"])
    ns = nt.nodes.new("ShaderNodeTexNoise"); ns.inputs["Scale"].default_value = 0.06; ns.inputs["Detail"].default_value = 6
    nt.links.new(fy.outputs[0], ns.inputs["Vector"])
    ks = op("MULTIPLY", op("MINIMUM", op("MAXIMUM", op("DIVIDE", op("SUBTRACT", ns.outputs["Fac"], 0.55), 0.2), 0.0), 1.0), 0.25)
    xt = op("MULTIPLY", op("SINE", op("DIVIDE", sp.outputs["Y"], 160.0), 0), 40.0)
    en_trib = op("MULTIPLY", op("LESS_THAN", op("ABSOLUTE", op("SUBTRACT", sp.outputs["X"], xt), 0), 70.0), op("LESS_THAN", sp.outputs["Y"], -60.0))
    # al pie del glaciar el agua sale revuelta: espuma que se apaga a ~250 m
    dy = op("SUBTRACT", sp.outputs["Y"], -760.0)
    cerca = op("SUBTRACT", 1.0, op("MINIMUM", op("DIVIDE", op("ABSOLUTE", dy, 0), 300.0), 1.0))
    sp_ = op("ADD", op("MULTIPLY", ks, en_trib), op("MULTIPLY", op("MULTIPLY", cerca, cerca), op("MULTIPLY", en_trib, op("MINIMUM", op("MAXIMUM", op("DIVIDE", op("SUBTRACT", ns.outputs["Fac"], 0.42), 0.15), 0.0), 1.0))))
    esp = op("MULTIPLY", op("MINIMUM", sp_, 1.0), op("GREATER_THAN", v_ab.outputs[0], -500.0))
    mxe = nt.nodes.new("ShaderNodeMix"); mxe.data_type = "RGBA"
    nt.links.new(esp, mxe.inputs[0]); nt.links.new(mx.outputs[2], mxe.inputs[6]); mxe.inputs[7].default_value = (0.62, 0.58, 0.52, 1)
    nt.links.new(mxe.outputs[2], b.inputs["Base Color"])
    rg = nt.nodes.new("ShaderNodeMapRange"); nt.links.new(k, rg.inputs["Value"]); rg.inputs["To Min"].default_value = 0.12; rg.inputs["To Max"].default_value = 0.36
    nt.links.new(rg.outputs[0], b.inputs["Roughness"])
    on = K._ruido(nt, escala=0.08, detalle=6, estirar=(0.35, 1.0, 1.0))
    ch = K._ruido(nt, escala=0.6, detalle=8)
    so = nt.nodes.new("ShaderNodeMath"); so.operation = "MULTIPLY_ADD"; so.inputs[1].default_value = 0.6
    nt.links.new(ch.outputs["Fac"], so.inputs[0]); nt.links.new(on.outputs["Fac"], so.inputs[2])
    K._bump(nt, b, so.outputs[0], 0.45, 0.35)
    return m


def flecha_plana(sc, nombre, pos, largo=130.0, ancho=34.0, color=(0.6, 0.88, 1.0), fuerza=2.6):
    """Flecha plana sobre el agua (capa de explicación): apunta a +x (río abajo); girar 180° = río arriba."""
    L2, a2 = largo / 2, ancho / 2
    v = [(-L2, -a2 * 0.45, 0), (L2 * 0.25, -a2 * 0.45, 0), (L2 * 0.25, -a2, 0), (L2, 0, 0), (L2 * 0.25, a2, 0), (L2 * 0.25, a2 * 0.45, 0), (-L2, a2 * 0.45, 0)]
    me = bpy.data.meshes.new(nombre); me.from_pydata(v, [], [(0, 1, 5, 6), (2, 3, 4, 5, 1)]); me.update()
    o = bpy.data.objects.new(nombre, me); sc.collection.objects.link(o)
    o.location = pos
    K.asignar(o, K.mat_emision(nombre + "_m", color, fuerza))
    o.visible_shadow = False
    return o


def casa(sc, nombre, pos, giro=0.0, color=(0.55, 0.12, 0.08)):
    """Casa de campo patagónica (7 × 5 m): techo de zinc a dos aguas con aleros, chimenea, puerta y ventanas con marco."""
    x, y, z = pos
    c, s = math.cos(giro), math.sin(giro)
    def en(lx, ly, lz):
        return (x + lx * c - ly * s, y + lx * s + ly * c, z + lz)
    cuerpo = K.caja(sc, nombre, (7.0, 5.0, 3.0), en(0, 0, 1.5), mat=K.mat_pintura(nombre + "_m", color, sucio=0.55), rot=(0, 0, giro))
    K.caja(sc, nombre + "_zocalo", (7.1, 5.1, 0.5), en(0, 0, 0.1), mat=K.mat_concreto(nombre + "_zc"), rot=(0, 0, giro))
    # techo: dos planchas inclinadas (cumbrera a lo largo), con 0,5 m de alero
    zinc = K.mat_metal_cepillado(nombre + "_zinc", (0.36, 0.37, 0.39), rugo=(0.35, 0.75))
    for lado in (1, -1):
        ang = math.atan2(1.6, 3.1)
        K.caja(sc, f"{nombre}_techo{lado}", (8.0, math.hypot(3.1, 1.6) + 0.1, 0.12), en(0, lado * 1.55, 3.0 + 0.85),
               mat=zinc, rot=(-lado * ang, 0, giro))
    # hastiales (los triángulos de los extremos)
    for lx in (3.5, -3.5):
        v = [en(lx, -2.5, 3.0), en(lx, 2.5, 3.0), en(lx, 0, 4.6)]
        me = bpy.data.meshes.new(nombre + "_hast"); me.from_pydata(v, [], [(0, 1, 2)]); me.update()
        o = bpy.data.objects.new(nombre + "_hast", me); sc.collection.objects.link(o); K.asignar(o, bpy.data.materials[nombre + "_m"])
    K.caja(sc, nombre + "_chim", (0.6, 0.6, 1.6), en(-2.0, 0.9, 4.5), mat=K.mat_concreto(nombre + "_ch", (0.3, 0.29, 0.28)), rot=(0, 0, giro))
    oscuro = K.mat_pintura(nombre + "_vano", (0.06, 0.05, 0.045), sucio=0.2)
    vidrio = K.mat_vidrio(nombre + "_vidrio") if hasattr(K, "mat_vidrio") else oscuro
    marco = K.mat_pintura(nombre + "_marco", (0.85, 0.84, 0.8), sucio=0.3)
    for lado in (1, -1):
        for (lx, lz, ancho, alto, mat) in ((1.6, 1.05, 0.95, 2.0, oscuro), (-1.4, 1.7, 1.2, 0.95, vidrio), (-0.1, 1.7, 0.9, 0.95, vidrio)):
            K.caja(sc, f"{nombre}_mc{lado}{lx}", (ancho + 0.2, 0.06, alto + 0.2), en(lx, lado * 2.52, lz), mat=marco, rot=(0, 0, giro))
            K.caja(sc, f"{nombre}_v{lado}{lx}", (ancho, 0.08, alto), en(lx, lado * 2.54, lz), mat=mat if mat is oscuro else oscuro, rot=(0, 0, giro))
    return cuerpo


def cerca(sc, p0, p1, z_fn):
    """Cerca de campo: postes cada 3 m y dos alambres (da la escala)."""
    mat = K.mat_pintura("cerca_m", (0.22, 0.17, 0.12), sucio=0.6)
    n = int(math.dist(p0, p1) / 3.0) + 1
    for i in range(n):
        u = i / max(1, n - 1)
        xx, yy = p0[0] + (p1[0] - p0[0]) * u, p0[1] + (p1[1] - p0[1]) * u
        K.caja(sc, f"Poste{i}", (0.14, 0.14, 1.3), (xx, yy, z_fn(xx, yy) + 0.6), mat=mat, bisel=0)


def sirena(sc, x, y, z):
    """Sirena de alerta en un poste: dos bocinas grises hacia los lados y una baliza roja arriba."""
    K.cilindro(sc, "Poste", 0.16, 9.0, (x, y, z), verts=12, mat=K.mat_pintura("poste", (0.45, 0.46, 0.47), sucio=0.5))
    gris = K.mat_pintura("bocina", (0.8, 0.8, 0.78), sucio=0.3)
    for lado in (1, -1):
        bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=0.65, radius2=0.18, depth=1.3, location=(x + lado * 0.75, y, z + 8.4),
                                        rotation=(0, -lado * math.pi / 2, 0))
        o = bpy.context.object; o.name = f"Bocina{lado}"; K.asignar(o, gris)
    K.caja(sc, "CajaSirena", (0.5, 0.5, 0.6), (x, y, z + 8.4), mat=gris)
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.28, depth=0.45, location=(x, y, z + 9.2))
    luz = bpy.context.object; luz.name = "Baliza"
    K.asignar(luz, K.mat_emision("baliza", (1.0, 0.06, 0.03), 0.0))
    return luz


def mat_rio_suelo(nombre="suelo_rio"):
    """Llanura de ripio gris (bancos de piedra del río), pasto ralo en las terrazas, bosque oscuro y roca en las laderas.
    Por altura sobre el río (z mundo − 20)."""
    m, nt, b = K._nodos(nombre)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sp.inputs[0])
    grande = K._ruido(nt, escala=0.008, detalle=6)
    medio = K._ruido(nt, escala=0.08, detalle=8)
    zr = nt.nodes.new("ShaderNodeMath"); zr.operation = "MULTIPLY_ADD"; zr.inputs[1].default_value = 3.0
    nt.links.new(grande.outputs["Fac"], zr.inputs[0]); nt.links.new(sp.outputs["Z"], zr.inputs[2])
    zz = zr.outputs[0]
    def rango(e, a, b_, c=0.0, d=1.0):
        mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = a; mr.inputs["From Max"].default_value = b_
        mr.inputs["To Min"].default_value = c; mr.inputs["To Max"].default_value = d; nt.links.new(e, mr.inputs["Value"]); return mr.outputs[0]
    def mezclar(fac, a, bc):
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"; nt.links.new(fac, mx.inputs[0]); nt.links.new(a, mx.inputs[6]); nt.links.new(bc, mx.inputs[7]); return mx.outputs[2]
    ripio = K._rampa(nt, medio.outputs["Fac"], (0.16, 0.155, 0.15), (0.34, 0.33, 0.31), (0.3, 0.7))
    pasto = K._rampa(nt, medio.outputs["Fac"], (0.07, 0.08, 0.035), (0.16, 0.15, 0.07), (0.3, 0.7))
    bosque = K._rampa(nt, medio.outputs["Fac"], (0.012, 0.022, 0.01), (0.035, 0.05, 0.022), (0.35, 0.7))
    roca = K._rampa(nt, medio.outputs["Fac"], (0.06, 0.06, 0.062), (0.19, 0.19, 0.19))
    mojado = nt.nodes.new("ShaderNodeMix"); mojado.data_type = "RGBA"; mojado.blend_type = "MULTIPLY"
    kmj = nt.nodes.new("ShaderNodeMath"); kmj.operation = "MULTIPLY"
    nt.links.new(rango(sp.outputs["Z"], 18.0, 19.8), kmj.inputs[0]); nt.links.new(rango(sp.outputs["Z"], 22.4, 20.8), kmj.inputs[1])
    km2 = nt.nodes.new("ShaderNodeMath"); km2.operation = "MULTIPLY"; km2.inputs[1].default_value = 0.7; nt.links.new(kmj.outputs[0], km2.inputs[0])
    nt.links.new(km2.outputs[0], mojado.inputs[0]); nt.links.new(ripio.outputs[0], mojado.inputs[6]); mojado.inputs[7].default_value = (0.32, 0.27, 0.22, 1)
    c1 = mezclar(rango(zz, 21.5, 23.5), mojado.outputs[2], pasto.outputs[0])
    c2 = mezclar(rango(zz, 30.0, 45.0), c1, bosque.outputs[0])
    c3 = mezclar(rango(zz, 380.0, 480.0), c2, roca.outputs[0])
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = 15.0; ao.samples = 6
    kao = rango(ao.outputs["AO"], 0.0, 1.0, 0.3, 1.0)
    cg = nt.nodes.new("ShaderNodeCombineColor"); [nt.links.new(kao, cg.inputs[i]) for i in range(3)]
    mm = nt.nodes.new("ShaderNodeMix"); mm.data_type = "RGBA"; mm.blend_type = "MULTIPLY"; mm.inputs[0].default_value = 1.0
    nt.links.new(c3, mm.inputs[6]); nt.links.new(cg.outputs[0], mm.inputs[7])
    nt.links.new(mm.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.85
    fino = K._ruido(nt, escala=1.2, detalle=6)
    K._bump(nt, b, fino.outputs["Fac"], 0.5, 0.15)
    camd = nt.nodes.new("ShaderNodeCameraData")
    kh = rango(camd.outputs["View Distance"], 600.0, 7000.0, 0.0, 0.3)
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs[0].default_value = (0.52, 0.62, 0.78, 1); em.inputs[1].default_value = 0.42
    mxs = nt.nodes.new("ShaderNodeMixShader"); nt.links.new(kh, mxs.inputs[0])
    nt.links.new(b.outputs[0], mxs.inputs[1]); nt.links.new(em.outputs[0], mxs.inputs[2])
    nt.links.new(mxs.outputs[0], nt.nodes["Material Output"].inputs[0])
    return m


def arboles(sc, detalle=1.0, n=26000, semilla=11):
    """Bosque (lenga/ñirre de lejos): conos oscuros en manchas sobre las terrazas y laderas bajas, no en el ripio inundable,
    no sobre el glaciar ni encima de las casas. Da la escala a las tomas aéreas."""
    r = np.random.default_rng(semilla)
    # bosquecitos: centros al azar y ~40 árboles apretados alrededor de cada uno (de lejos se lee bosque, no puntos sueltos)
    cx = r.uniform(-2100, 2100, 4000).astype(np.float32); cy = r.uniform(-1900, 1300, 4000).astype(np.float32)
    hc = altura_rio(cx, cy)
    okc = (hc > 3.2) & (hc < 340) & (fbm(cx, cy, 101, 220.0, 3) > 0.0)
    cx, cy = cx[okc][:int(n / 32)], cy[okc][:int(n / 32)]
    m_ = 40
    x = (np.repeat(cx, m_) + r.normal(0, 32, len(cx) * m_)).astype(np.float32)
    y = (np.repeat(cy, m_) + r.normal(0, 32, len(cy) * m_)).astype(np.float32)
    h = altura_rio(x, y)
    hielo = (y < Y_HOCICO + 20) & (np.abs(x - xt_rio(y)) < 520)
    casas = np.hypot(x - 655, y + 220) < 40
    ok = (h > 3.0) & (h < 380) & ~hielo & ~casas
    x, y, h = x[ok][:n], y[ok][:n], h[ok][:n]
    alto = r.uniform(9, 18, len(x)).astype(np.float32); rad = alto * r.uniform(0.22, 0.32, len(x)).astype(np.float32)
    k = 7
    ang = np.linspace(0, 2 * np.pi, k, endpoint=False)
    vs = []
    for i in range(k):
        vs.append(np.stack([x + rad * np.cos(ang[i]), y + rad * np.sin(ang[i]), h + 20.0 + 0.6], 1))
    vs.append(np.stack([x, y, h + 20.0 + alto], 1))
    V = np.stack(vs, 1).reshape(-1, 3)
    base = (np.arange(len(x)) * (k + 1))[:, None]
    caras = np.concatenate([np.stack([base[:, 0] + i, base[:, 0] + (i + 1) % k, base[:, 0] + k], 1) for i in range(k)], 0)
    me = bpy.data.meshes.new("Arboles")
    me.vertices.add(len(V)); me.vertices.foreach_set("co", V.ravel())
    me.loops.add(len(caras) * 3); me.loops.foreach_set("vertex_index", caras.ravel())
    me.polygons.add(len(caras)); me.polygons.foreach_set("loop_start", np.arange(0, len(caras) * 3, 3)); me.polygons.foreach_set("loop_total", np.full(len(caras), 3))
    me.update(); me.validate()
    o = bpy.data.objects.new("Arboles", me); sc.collection.objects.link(o)
    m, nt, b = K._nodos("arbol")
    nz = K._ruido(nt, escala=0.02, detalle=3)
    c = K._rampa(nt, nz.outputs["Fac"], (0.018, 0.035, 0.014), (0.06, 0.075, 0.03))
    nt.links.new(c.outputs[0], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.85
    hoja = K._ruido(nt, escala=1.5, detalle=6)
    K._bump(nt, b, hoja.outputs["Fac"], 0.8, 0.5)
    K.asignar(o, m)
    return o


def rio(sc, detalle=1.0, sol_elev=15.0, sol_rot=78.0):     # sol a lo largo del valle (si no, los cerros lo tapan y la luz queda plana)
    w, sol, d = K.cielo_atardecer(sc, elev=sol_elev, rot=sol_rot, fuerza=0.14, sol=3.8, color_sol=(1.0, 0.82, 0.66))
    sky = next(n for n in w.node_tree.nodes if n.type == "TEX_SKY")
    sky.altitude = 300; sky.aerosol_density = 1.3; sky.sun_disc = False
    mv = mat_rio_suelo()
    n = int(520 * detalle)
    f = malla_altura("RioValle", -2200, 2200, -2000, 1400, n, int(n * 0.78), lambda x, y: altura_rio(x, y) + 20.0, mv)
    lej = malla_altura("RioLejos", -12000, 12000, -12000, 12000, 220, 220,
                       lambda x, y: np.where((np.abs(x) < 2150) & (y > -1950) & (y < 1350), -60.0, altura_rio(x, y) + 20.0 + 900 * suave((np.abs(y) - 1500) / 4000)), mv)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -300, RIO_NORMAL + 20.0))
    ag = bpy.context.object; ag.name = "AguaRio"; ag.scale = (4400, 3400, 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    K.asignar(ag, mat_agua_rio())
    ag.visible_shadow = False
    casas = [casa(sc, f"Casa{i}", (cx, cy, float(altura_rio(np.array([cx], np.float32), np.array([cy], np.float32))[0]) + 20.0), g, c)
             for i, (cx, cy, g, c) in enumerate(((644, -212, 0.3, (0.55, 0.12, 0.08)), (664, -222, 0.1, (0.82, 0.78, 0.66)),
                                                  (634, -230, 0.5, (0.2, 0.32, 0.45)), (674, -238, 0.2, (0.42, 0.4, 0.36))))]
    zfn = lambda xx, yy: float(altura_rio(np.array([xx], np.float32), np.array([yy], np.float32))[0]) + 20.0
    sirena(sc, 654.0, -204.0, zfn(654.0, -204.0))
    cerca(sc, (612.0, -196.0), (700.0, -206.0), zfn)
    arboles(sc, detalle)
    flechas = []
    for i, x in enumerate((-520.0, -330.0, -150.0, 250.0, 450.0)):
        yy = 30.0 * math.sin(x / 400.0)
        flechas.append(flecha_plana(sc, f"Flecha{i}", (x, yy, 20.0 + RIO_NORMAL + 0.6)))
    hielo, borb = hocico(sc, detalle)
    return {"agua": ag, "casas": casas, "flechas": flechas, "sol": sol, "hocico": hielo, "borbollon": borb}


def estado_rio(R, nivel, arriba, abajo):
    R["agua"].location.z = 20.0 + nivel
    R["borbollon"].location.z = 20.0 + nivel
    R["borbollon"].hide_render = abajo < -500.0
    nt = bpy.data.materials["agua_rio"].node_tree
    nt.nodes["arriba"].outputs[0].default_value = arriba
    nt.nodes["abajo"].outputs[0].default_value = abajo
