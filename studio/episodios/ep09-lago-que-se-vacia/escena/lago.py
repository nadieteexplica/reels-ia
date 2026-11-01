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
NIVEL_VACIO = -31.0
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
    pared = 0.45 * lad + 950.0 * suave(lad / 1100.0) ** 1.4
    z = np.where(u < 1.0, fondo, pared)
    # cabecera (norte) sube suave hacia el valle de arriba
    z += 22.0 * suave((y - 1700) / 500.0)
    # relieve: lomas suaves en el fondo (charcos y canales), roca grande en las laderas
    det_fondo = 1.6 * fbm(x, y, 3, 90.0, 4) + 0.5 * fbm(x, y, 9, 18.0, 3)
    canal = -2.6 * np.exp(-((xc + 30 * np.sin(y / 140.0)) / 22.0) ** 2) * suave((1700 - y) / 400.0) * (u < 1.0)
    det_lad = 70.0 * fbm(x, y, 5, 600.0, 6) * suave(lad / 120.0) + 140.0 * (cresta(x, y, 11, 900.0, 5) - 0.4) * suave(lad / 500.0)
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
    onda = K._ruido(nt, escala=2.2, detalle=3, estirar=(1.0, 0.18, 1.0))         # ondulitas del barro (corriente)
    vor = nt.nodes.new("ShaderNodeTexVoronoi"); vor.feature = "DISTANCE_TO_EDGE"; vor.inputs["Scale"].default_value = 0.35
    nt.links.new(tc.outputs["Object"], vor.inputs["Vector"])
    barro = K._rampa(nt, medio.outputs["Fac"], (0.11, 0.095, 0.075), (0.25, 0.215, 0.17), (0.3, 0.75))
    limo = K._rampa(nt, grande.outputs["Fac"], (0.27, 0.25, 0.22), (0.4, 0.37, 0.33))
    lavada = K._rampa(nt, medio.outputs["Fac"], (0.2, 0.19, 0.17), (0.36, 0.34, 0.31))
    bosque = K._rampa(nt, fino.outputs["Fac"], (0.018, 0.03, 0.014), (0.06, 0.085, 0.035), (0.35, 0.7))
    roca = K._rampa(nt, medio.outputs["Fac"], (0.06, 0.058, 0.056), (0.17, 0.165, 0.155))
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
    c2 = mezclar(rango(zz, 0.5, 3.0), c1, lavada.outputs[0])                          # sobre el nivel lleno: franja lavada
    c3 = mezclar(rango(zz, 14.0, 26.0), c2, bosque.outputs[0])                        # bosque desde ~15 m sobre el lleno
    emp = rango(pend.outputs["Z"], 0.42, 0.28)
    c4 = mezclar(emp, c3, roca.outputs[0])                                            # roca en lo empinado
    c5 = mezclar(rango(zz, 380, 560), c4, roca.outputs[0])                            # sobre el bosque, roca
    alto_n = rango(zz, 950, 1100)
    plano_n = rango(pend.outputs["Z"], 0.5, 0.78)
    kn = nt.nodes.new("ShaderNodeMath"); kn.operation = "MULTIPLY"; kn.use_clamp = True
    nt.links.new(alto_n, kn.inputs[0]); nt.links.new(plano_n, kn.inputs[1])
    c6 = mezclar(kn.outputs[0], c5, nieve.outputs[0])
    nt.links.new(c6, b.inputs["Base Color"])
    # brillo: barro mojado en los bajos (0,22) y en las grietas; limo y laderas mates
    rug = rango(zz, -31, -22, 0.24, 0.62)
    rug2 = nt.nodes.new("ShaderNodeMath"); rug2.operation = "MAXIMUM"
    nt.links.new(rug, rug2.inputs[0]); nt.links.new(rango(zz, -2, 6, 0.0, 0.92), rug2.inputs[1])
    nt.links.new(rug2.outputs[0], b.inputs["Roughness"])
    # relieve: ondulitas + grietas del barro (sólo abajo) + grano
    s1 = nt.nodes.new("ShaderNodeMath"); s1.operation = "MULTIPLY"; s1.inputs[1].default_value = 0.6; nt.links.new(onda.outputs["Fac"], s1.inputs[0])
    s2 = nt.nodes.new("ShaderNodeMath"); s2.operation = "ADD"; nt.links.new(s1.outputs[0], s2.inputs[0]); nt.links.new(fino.outputs["Fac"], s2.inputs[1])
    K._bump(nt, b, s2.outputs[0], 0.6, 0.06)
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
    c = K._rampa(nt, col.outputs["Fac"], (0.07, 0.17, 0.18), (0.12, 0.26, 0.26))
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
    fondo = malla_altura("Fondo", -900, 900, -260, 2200, n, int(n * 1.35), altura_terreno, mv)
    lejos = malla_altura("Valle", -6000, 6000, -4500, 9000, int(300 * detalle), int(330 * detalle),
                         lambda x, y: np.where((np.abs(x) < 880) & (y > -250) & (y < 2180), -60.0, altura_terreno(x, y)), mv)
    # cerros lejanos con bruma (formas grandes que llegan al suelo; ESTILO_REALISTA §4.3)
    def picos(x, y):
        d = np.sqrt(x ** 2 + (y - 1500) ** 2)
        base = 1500.0 * suave((d - 4000) / 3500) * (0.55 + 0.6 * cresta(x, y, 21, 2600.0, 6))
        z = base + 300 * fbm(x, y, 23, 1500.0, 5) * suave((d - 4000) / 2000)
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
        z = np.maximum(base, NIVEL_LLENO + 38.0 + 0.035 * (-y)) + serac * (1 - 0.6 * suave((-y - 3000) / 3000))
        return np.where(-y > 18.0, base + (z - base) * frente, base - 2.0)
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
          - 3.0 * np.abs(np.sin(X / 6.0 + 2.5 * fbm(X, Z * 0.3, 57, 40.0, 2))) ** 0.5)
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
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=1.0)
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
    dm = o.modifiers.new("det", "DISPLACE"); dm.texture = tx; dm.strength = 0.25 * max(tam)
    K.liso(o, 35)
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


def valle(sc, nivel=NIVEL_LLENO, detalle=1.0, sol_elev=11.0, sol_rot=38.0):
    """Arma el set completo. Sol de la mañana desde el noreste (11°): pasa sobre la ladera este y le pega de costado al
    frente del glaciar, que mira al norte (en el fondo del valle, con el sol más bajo, todo queda en sombra)."""
    w, sol, d = K.cielo_atardecer(sc, elev=sol_elev, rot=sol_rot, fuerza=0.3, sol=4.2, color_sol=(1.0, 0.7, 0.5))
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
