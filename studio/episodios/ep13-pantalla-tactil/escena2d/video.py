"""Ep. 13 — "Tu dedo le roba electricidad a tu pantalla" (cómo funciona la pantalla táctil). 2D de comedia por código (PIL).
Voz: escena2d/voz.wav + words.json (los deja prep.py). Lo que cambia es el contenido, no la cámara (regla 24).
Uso: python3 video.py <carpeta_salida> [cuadro_desde cuadro_hasta [paso]]      (cuadros 1..FIN, 30 fps, 1080×1920)
"""
import json, math, os, random, sys
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
EPI = os.path.abspath(os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)
import arte as A
import kit2d as K
from arte import C, TINTA, clamp, suave, sale, pop, rebote

W, H, FPS, SS = 1080, 1920, 30, 2
words = json.load(open(os.path.join(EPI, "words.json")))
ENV = json.load(open(os.path.join(AQUI, "envolvente.json")))
FIN_VOZ = words[-1]["e"]
DUR = FIN_VOZ + 1.0
FIN = int(round(DUR * FPS))


def tw(prefijo, desde=0.0):
    p = prefijo.lower()
    for w in words:
        if w["s"] >= desde - 0.01 and w["w"].lower().strip(".,;:…!?¡¿").startswith(p):
            return w["s"]
    raise KeyError(prefijo)


def boca(t):
    i = int(t * 60)
    return ENV[i] if 0 <= i < len(ENV) else 0.0




T_ROBA = tw("roba")
T_ELEC = tw("electricidad")
T_CADA = tw("Cada")
T_ASI = tw("Así")
T_YESO = tw("y", 5.8)
T_SALCH = tw("salchichas")
T_BAJO = tw("Bajo")
T_REJ = tw("rejilla")
T_CARG = tw("cargada")
T_YTU = tw("Y", 11.4)
T_DEJA = tw("deja")
T_CUANDO = tw("Cuando")
T_TOCAS = tw("tocas", 14)
T_LLEVA = tw("lleva")
T_JUSTO = tw("justo")
T_UN = tw("Un", 17.5)
T_FALTA = tw("falta")
T_AHI = tw("ahí")
T_NO = tw("No", 21)
T_APR = tw("aprietes")
T_POR = tw("Por", 23)
T_FALLA = tw("falla")
T_LANA2 = tw("la", 25)
T_AISLA = tw("aísla")
T_YUNA = tw("Y", 26)
T_PUEDE = tw("puede")
T_LO = [w["s"] for w in words if w["w"].startswith("¿Lo")][0]
T_INV = tw("Un", 29.4)
T_COREA = tw("Corea")
T_HUBO = tw("hubo")
T_SALCH2 = tw("salchichas", 31)
T_PARA1 = tw("Para", 32.8)
T_GUANTES = tw("guantes", 33.5)
T_PARA2 = tw("Para", 34.5)
T_UNA = tw("una", 35.5)
T_YTU2 = tw("y", 36)
T_SON = tw("son")
T_MISMO = tw("mismo")

CORTES = [0.0, T_CADA - 0.1, T_ASI - 0.1, T_BAJO - 0.1, T_YTU - 0.08, T_CUANDO - 0.08, T_UN - 0.1, T_NO - 0.08, T_POR - 0.08, T_YUNA - 0.08, T_LO - 0.06,
          T_INV - 0.06, T_PARA1 - 0.08, T_PARA2 - 0.08, DUR]
T = {i + 1: (CORTES[i], CORTES[i + 1]) for i in range(len(CORTES) - 1)}
NP = len(T)
for _k, (_a, _b) in T.items():
    assert _b - _a >= 0.6, (_k, _a, _b)


def plano_de(t):
    for k, (a, b) in T.items():
        if a <= t < b:
            return k
    return max(T)


def dib(fn):
    def envuelto(t, a, b):
        L = K.Lienzo(ss=SS)
        fn(L, t, a, b)
        return L.salida()
    return envuelto


def txt(L, s, x, y, tam=64, *a, **kw):
    if tam * SS >= 2:
        K.texto(L, s, x, y, tam, *a, **kw)


def pild(L, s, cx, cy, t, t0, tam=56, fondo=None, tinta=None):
    if t >= t0:
        K.pildora(L, s, cx, cy, tam, fondo or C["blanco"], tinta or TINTA, pop(t - t0))


def confeti(L, t, t0, n=44, semilla=4):
    if t < t0:
        return
    random.seed(semilla)
    cols = [C["rojo"], C["amarillo"], C["blanco"], C["verde"], C["cuello"]]
    for i in range(n):
        x = random.uniform(0, W)
        v = random.uniform(500, 1100)
        y = -60 + (t - t0) * v - random.uniform(0, 500)
        y = y % (H + 200) - 100
        a = t * random.uniform(3, 8) + i
        w = 26 * abs(math.cos(a)) + 6
        K.poligono(L, [(x - w, y - 12), (x + w, y - 12), (x + w, y + 12), (x - w, y + 12)], cols[i % 5], TINTA, 3)


# ------------------------------------------------------------------ planos
NX, NY = 5, 9


def rayos(L, t, c1, c2, cx=540, cy=900):
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=c1)
    for i in range(14):
        an = i * math.pi / 7 + t * 0.4
        K.poligono(L, [(cx, cy), (cx + math.cos(an) * 2400, cy + math.sin(an) * 2400), (cx + math.cos(an + 0.22) * 2400, cy + math.sin(an + 0.22) * 2400)], c2)


def lerp(a, b, u):
    return a + (b - a) * u


def lp(p, q, u):
    return (lerp(p[0], q[0], u), lerp(p[1], q[1], u))


def electrones(L, c, t, u=1.0, falta=None, sustos=None, cara="feliz", r=26):
    """Un electrón en cada cruce de la rejilla del celular `c`. falta = {(i, j): 0..1} (1 = ya no está). sustos = cruce cerca del que se asustan."""
    for j in range(NY):
        for i in range(NX):
            uu = clamp(u * 2.4 - (i + j) * 0.1)
            f = (falta or {}).get((i, j), 0.0)
            if uu <= 0 or f >= 1:
                continue
            x, y = c["punto"](i, j)
            cc = "susto" if sustos and abs(sustos[0] - i) + abs(sustos[1] - j) == 1 else cara
            A.electron(L, x, y, r * pop(uu, 1.0) * (1 - f), t, cc if uu > 0.7 else "nada", fase=i * 1.7 + j, brillo=0.5)


def anillo(L, x, y, t, r=74, color=None):
    rr = r + 9 * math.sin(t * 12)
    K.circulo(L, x, y, rr, None, TINTA, 22)
    K.circulo(L, x, y, rr, None, color or C["coral"], 13)


def tele(L, c, t, cara="normal", **kw):
    return A.celular(L, 540, 980, 700, 1380, cara=cara, t=t, n=(NX, NY), **kw)


def heroe(L, t, e):
    """Cuadro 0: el dedo con antifaz le saca un electrón al celular. e = tiempo desde el inicio del robo."""
    A.fondo_puntos(L, C["menta"], C["menta2"], t)
    roba = clamp((e - 0.55) / 0.9)
    huye = clamp((e - 2.3) / 1.1)
    c = A.celular(L, 400, 900, 540, 1060, cara="susto" if huye < 0.5 else "enojo", t=t, temblor=1.0 if e < 0.5 else 0.2, n=(NX, NY))
    toque = (575, 800)
    tip = lp(toque, (700, 720), suave(roba))
    tip = lp(tip, (1150, 500), suave(huye))
    if roba > 0:                                           # el electrón robado va en la punta
        A.electron(L, tip[0] - 60, tip[1] - 70 + math.sin(t * 20) * 6, 58, t, "susto")
        for i in range(3):
            K.linea(L, [(toque[0] - 10, toque[1] - 20 + i * 20), lp((toque[0] - 10, toque[1] - 20 + i * 20), (tip[0] - 90, tip[1] - 90 + i * 20), 0.5)], (255, 236, 150, 200), 7)
    A.dedo(L, tip[0], tip[1], ang=22, largo=760, antifaz=True, cara="malo", t=t)
    if e < 0.55:
        A.rayo(L, 610, 640 + math.sin(t * 30) * 10, 1.3, rot=0.2)
        A.rayo(L, 470, 690, 0.8, rot=-0.5)
    K.pildora(L, "¡LADRÓN!", 400, 230, 110, C["coral"], C["blanco"], 1.0 if e < 0.3 else 1 + 0.06 * math.sin(t * 10))


@dib
def p1(L, t, a, b):
    heroe(L, t, t)


@dib
def p2(L, t, a, b):
    # "Cada vez que la tocas."
    A.fondo_puntos(L, C["menta"], C["menta2"], t)
    golpes = [a + 0.12, a + 0.55, a + 0.98, a + 1.38]
    k = sum(1 for g in golpes if t >= g)
    ult = max([g for g in golpes if t >= g], default=None)
    e = (t - ult) if ult is not None else 9
    c = A.celular(L, 400, 900, 540, 1060, cara="susto" if e < 0.25 else "enojo", t=t, temblor=1.0 if e < 0.12 else 0, n=(NX, NY))
    toque = (575, 800)
    atras = (760, 700)
    u = clamp(e / 0.12) if ult is not None else 1
    tip = lp(toque, atras, suave(u))
    A.dedo(L, tip[0], tip[1], ang=22, largo=760, antifaz=True, cara="feliz", t=t)
    for i, g in enumerate(golpes):                         # cada toque saca un electrón que vuela a la bolsa
        ee = t - g
        if ee < 0:
            continue
        uu = clamp(ee / 0.45)
        x = lerp(toque[0], 860 + (i % 2) * 70, uu)
        y = lerp(toque[1], 330 + (i // 2) * 90, uu) - math.sin(uu * math.pi) * 220
        A.electron(L, x, y, 44, t, "susto", fase=i)
        if ee < 0.14:
            A.estrella_golpe(L, toque[0], toque[1], 120 * pop(ee, 0.14), C["elec"], 8)
    if k:
        K.pildora(L, f"−{k}", 400, 230, 120, C["coral"], C["blanco"], pop(e, 0.2))


@dib
def p3(L, t, a, b):
    # "Así funciona, y eso explica lo de las salchichas."
    A.fondo_puntos(L, C["menta"], C["menta2"], t)
    e = t - a
    sal = t >= T_YESO
    c = A.celular(L, 400, 900, 540, 1060, cara="feliz" if not sal else "normal", t=t, n=(NX, NY), mira=(60, 0) if sal else (0, 0))
    K.pildora(L, "ASÍ FUNCIONA", 420, 230, 84, C["morado"], C["blanco"], pop(e - 0.05))
    if sal:
        u = sale((t - T_YESO) / 0.35)
        x = W + 300 - u * 500
        A.dedo(L, x, 620 + math.sin(t * 8) * 16, ang=76 + math.sin(t * 8) * 5, largo=1500, tipo="salchicha", cara="feliz", t=t)
        if t >= T_SALCH - 0.05:
            ee = t - T_SALCH + 0.05
            A.estrella_golpe(L, 900, 380, 150 * pop(ee), C["elec"], 10, rot=0.2)
            txt(L, "¿?", 900, 380, 120 * pop(ee), C["coral"], borde=7, color_borde=TINTA)


@dib
def p4(L, t, a, b):
    # "Bajo el vidrio hay una rejilla que no ves, cargada de electricidad."
    A.fondo_puntos(L, C["morado"], C["morado2"], t)
    e = t - a
    ur = clamp((t - T_REJ + 0.1) / 0.7)
    c = tele(L, None, t, cara="nada", rejilla=ur, electrones=False)
    electrones(L, c, t, clamp((t - T_CARG + 0.05) / 0.9) if t >= T_CARG - 0.05 else 0)
    # el vidrio se levanta y se va
    v = sale((e - 0.25) / 0.7)
    x0, y0, x1, y1 = c["caja"]
    if v < 1:
        dy = -v * 1700
        K.caja_red(L, x0 - 8, y0 - 8 + dy, x1 + 8, y1 + 8 + dy, 60, (190, 232, 250, 150), TINTA, 7)
        K.linea(L, [(x0 + 90, y0 + 200 + dy), (x0 + 260, y0 + 60 + dy)], (255, 255, 255, 200), 22)
        K.linea(L, [(x0 + 150, y0 + 300 + dy), (x0 + 380, y0 + 100 + dy)], (255, 255, 255, 160), 12)
        if e > 0.1:
            K.pildora(L, "VIDRIO", 540, 230 + dy * 0.2, 90, C["blanco"], TINTA, pop(e - 0.1))
    if t >= T_REJ - 0.05 and t < T_CARG - 0.05:
        K.pildora(L, "REJILLA", 540, 200, 96, C["vidrio"], TINTA, pop(t - T_REJ + 0.05))
    if t >= T_CARG - 0.05:
        K.pildora(L, "CON ELECTRICIDAD", 540, 200, 80, C["elec"], TINTA, pop(t - T_CARG + 0.05))


@dib
def p5(L, t, a, b):
    # "Y tu piel deja pasar la electricidad."
    A.fondo_puntos(L, C["menta"], C["menta2"], t)
    e = t - a
    tip = (540, 470)
    A.dedo(L, tip[0], tip[1] + math.sin(t * 3) * 8, ang=90, largo=1700, s=1.7, cara="feliz", t=t)
    if t >= T_DEJA - 0.1:                                  # electrones bajando por dentro del dedo
        for i in range(6):
            u = ((t - T_DEJA) * 0.9 + i / 6) % 1.0
            x = 540 + math.sin(u * 9 + i) * 60
            y = 1120 + u * 760
            A.electron(L, x, y, 40, t, "feliz", fase=i, brillo=0.8)
    K.pildora(L, "TU PIEL", 540, 230, 100, C["coral"], C["blanco"], pop(e - 0.05))
    if t >= T_DEJA - 0.05:
        K.pildora(L, "DEJA PASAR", 540, 1330, 76, C["elec"], TINTA, pop(t - T_DEJA + 0.05))


MARCA = (2, 2)


@dib
def p6(L, t, a, b):
    # "Cuando tocas, tu dedo se lleva un poquito, justo en ese punto."
    A.fondo_puntos(L, C["morado"], C["morado2"], t)
    e = t - a
    c = tele(L, None, t, cara="nada", rejilla=1.0, electrones=False)
    px, py = c["punto"](*MARCA)
    f = clamp((t - T_LLEVA) / 0.35)
    electrones(L, c, t, 1.0, falta={MARCA: f}, sustos=MARCA if t >= T_TOCAS else None)
    llega = sale((t - a) / (T_TOCAS - a + 0.1))
    se_va = suave((t - T_LLEVA - 0.3) / 0.6)
    tip = lp((1250, 1500), (px + 44, py + 40), llega)
    tip = lp(tip, (px + 250, py + 190), se_va)
    if t >= T_JUSTO - 0.05:
        anillo(L, px, py, t)
        ee = t - T_JUSTO + 0.05
        K.pildora(L, "AQUÍ FALTA", 400, 200, 90, C["coral"], C["blanco"], pop(ee))
    if f > 0:                                              # el electrón se va pegado al dedo
        A.electron(L, tip[0] - 50, tip[1] - 56, 44 * min(1, f * 2), t, "susto")
    A.dedo(L, tip[0], tip[1], ang=45, largo=1200, cara="feliz" if f > 0 else "normal", t=t)
    if 0 <= t - T_TOCAS < 0.25:
        A.estrella_golpe(L, px, py, 120 * pop(t - T_TOCAS, 0.2), C["elec"], 8)


@dib
def p7(L, t, a, b):
    # "Un chip nota dónde falta, y dice: ahí está el dedo."
    A.fondo_puntos(L, C["morado"], C["morado2"], t)
    e = t - a
    c = tele(L, None, t, cara="nada", rejilla=1.0, electrones=False)
    px, py = c["punto"](*MARCA)
    electrones(L, c, t, 1.0, falta={MARCA: 1.0})
    encontro = t >= T_FALTA
    if encontro:
        anillo(L, px, py, t, color=C["coral"] if t < T_AHI else C["verde"])
    # la lupa barre la rejilla y se queda en el hueco
    u = clamp(e / (T_FALTA - a))
    fila = min(2, int(u * 3))
    barr = (u * 3) % 1.0 if u < 1 else 1
    p0, p1_ = c["punto"](0, fila), c["punto"](4, fila)
    lup = lp(p0, p1_, barr if fila % 2 == 0 else 1 - barr)
    if encontro:
        lup = lp(lup, (px, py), sale((t - T_FALTA) / 0.2))
    entra = sale(e / 0.3)
    A.chip(L, 230 - (1 - entra) * 500, 1470, 0.9, t, "feliz" if encontro else "normal", lupa=lup)
    if t >= T_AHI - 0.05:
        ee = t - T_AHI + 0.05
        A.globo(L, 430, 1310, 1040, 1560, (390, 1450))
        txt(L, "¡AHÍ ESTÁ!", 735, 1435, 96 * pop(ee), C["coral"])
    K.pildora(L, "EL CHIP", 540, 200, 96, C["chip"], C["elec"], pop(e - 0.05))


@dib
def p8(L, t, a, b):
    # "No importa cuánto aprietes."
    A.fondo_puntos(L, (255, 196, 170), (250, 172, 146), t)
    e = t - a
    aprieta = 14 * math.sin(t * 46)
    c = A.celular(L, 540, 1000 + abs(aprieta) * 0.6, 640, 1260, cara="dormido", t=t, n=(NX, NY), mira=(-120, 0))
    for i in range(3):                                     # Zzz
        u = (e * 0.7 + i / 3) % 1.0
        txt(L, "z", 150 - i * 30 - u * 30, 520 - i * 70 - u * 80, 70 + i * 26, C["blanco"], borde=5, color_borde=TINTA)
    A.dedo(L, 690 + aprieta * 0.4, 930 + abs(aprieta), ang=-58, largo=1300, s=1.15, cara="susto", t=t)
    for i in range(6):                                     # líneas de esfuerzo
        an = math.radians(200 + i * 28)
        r0, r1 = 130, 200 + 30 * math.sin(t * 30 + i)
        K.linea(L, [(680 + math.cos(an + 2.6) * r0, 960 + math.sin(an + 2.6) * r0), (680 + math.cos(an + 2.6) * r1, 960 + math.sin(an + 2.6) * r1)], TINTA, 12)
    for i in range(2):                                     # gotas de sudor
        u = (e * 1.6 + i * 0.5) % 1.0
        K.circulo(L, 900 + i * 90, 520 + u * 160, 20, (150, 214, 240), TINTA, 4)
    K.pildora(L, "APRETAR NO SIRVE", 540, 1400, 80, C["coral"], C["blanco"], pop(e - 0.05))


def equis(L, x, y, r, u=1.0):
    r = r * u
    if r < 4:
        return
    for sg in (-1, 1):
        K.linea(L, [(x - r, y - sg * r), (x + r, y + sg * r)], TINTA, r * 0.46)
    for sg in (-1, 1):
        K.linea(L, [(x - r, y - sg * r), (x + r, y + sg * r)], C["rojo"], r * 0.3)


def visto(L, x, y, r, u=1.0):
    r = r * u
    if r < 4:
        return
    K.circulo(L, x, y, r, C["verde"], TINTA, 8)
    K.linea(L, [(x - r * 0.46, y), (x - r * 0.1, y + r * 0.38), (x + r * 0.5, y - r * 0.36)], C["blanco"], r * 0.24)


@dib
def p9(L, t, a, b):
    # "Por eso falla con guantes de lana: la lana aísla."
    A.fondo_puntos(L, C["menta"], C["menta2"], t)
    e = t - a
    c = tele(L, None, t, cara="nada", rejilla=1.0, electrones=False)
    px, py = c["punto"](*MARCA)
    electrones(L, c, t, 1.0)
    golpes = [T_FALLA - 0.1, T_FALLA + 0.45, T_FALLA + 1.0, T_LANA2 + 0.2, T_LANA2 + 0.7]
    ult = max([g for g in golpes if t >= g], default=None)
    ee = (t - ult) if ult is not None else 9
    u = suave(clamp(ee / 0.16)) if ult is not None else 1
    llega = sale((t - a) / 0.3)
    tip = lp((px + 44, py + 40), (px + 150, py + 120), u)
    tip = lp((1250, 1500), tip, llega)
    A.dedo(L, tip[0], tip[1], ang=45, largo=1200, tipo="guante", cara="susto" if t > T_FALLA + 0.5 else "normal", t=t)
    if t >= T_FALLA:
        equis(L, 250, 520, 110, pop(t - T_FALLA))
    K.pildora(L, "GUANTE DE LANA", 540, 200, 80, C["lana"], C["blanco"], pop(e - 0.05))
    if t >= T_AISLA - 0.1:
        K.pildora(L, "AISLANTE", 540, 1400, 96, C["blanco"], TINTA, pop(t - T_AISLA + 0.1))


@dib
def p10(L, t, a, b):
    # "Y una gota de agua puede activarla sola."
    cae_t = T_PUEDE - 0.15
    cayo = t >= cae_t
    A.fondo_puntos(L, C["menta"], C["menta2"], t)
    e = t - a
    c = A.celular(L, 540, 1000, 640, 1260, cara="susto" if cayo else "normal", t=t, n=(NX, NY), loca=1.0 if cayo else 0, temblor=0.6 if cayo else 0, mira=(0, 0))
    u = clamp((t - a - 0.1) / (cae_t - a - 0.1))
    gy = lerp(-200, 1330, u * u)
    A.gota(L, 600, gy, 1.3 if not cayo else 1.3, t)
    if cayo:
        ee = t - cae_t
        for i in range(6):
            an = math.radians(200 + i * 28)
            K.circulo(L, 600 + math.cos(an) * (120 + ee * 300), 1330 + math.sin(an) * (80 + ee * 240) + ee * ee * 500, 22, C["agua"], TINTA, 4)
        K.pildora(L, "¿QUIÉN TOCÓ?", 540, 220, 90, C["coral"], C["blanco"], pop(ee))
    else:
        K.pildora(L, "UNA GOTA", 540, 220, 90, C["agua2"], C["blanco"], pop(e - 0.05))


@dib
def p11(L, t, a, b):
    # "¿Lo más raro?" — el viejo
    rayos(L, t, C["amarillo"], (255, 226, 110))
    K.viejo(L, 540, 1290, alto=760, boca=boca(t), t=t, gesto="tazon", mira=1)
    L.d.rectangle((0, L.S(1280), L.S(W), L.S(H)), fill=C["madera"])
    L.d.line([L.pt(0, 1280), L.pt(W, 1280)], fill=TINTA, width=int(L.S(8)))
    L.d.rectangle((0, L.S(1340), L.S(W), L.S(H)), fill=(150, 104, 60))
    txt(L, "¿LO MÁS RARO?", 540, 300, 112 * pop(t - a - 0.03), C["rojo"], borde=9, color_borde=TINTA)


def mano_guante(L, x, y, s=1.0):
    """Mitón de lana agarrando algo en (x, y)."""
    K.circulo(L, x, y, 150 * s, C["lana"], TINTA, 8)
    K.elipse(L, x - 130 * s, y - 40 * s, 60 * s, 90 * s, C["lana"], TINTA, 8)
    for i in range(4):
        K.linea(L, [(x - 90 * s + i * 60 * s, y - 60 * s), (x - 60 * s + i * 60 * s, y + 10 * s)], C["lana2"], 10 * s)
    K.caja_red(L, x - 150 * s, y + 110 * s, x + 150 * s, y + 200 * s, 30 * s, C["blanco"], TINTA, 7)


def escena_corea(L, t, e, toca=True):
    A.invierno(L, 1380, t)
    c = A.celular(L, 360, 760, 460, 900, cara="feliz", t=t, n=(NX, NY))
    px, py = 470, 700
    golpe = (t * 2.6) % 1.0
    u = suave(clamp(golpe / 0.2)) if toca else 1
    tip = lp((px, py), (px + 90, py + 60), u)
    bx, by = A.dedo(L, tip[0], tip[1], ang=52, largo=820, tipo="salchicha", cara="feliz", t=t)
    mano_guante(L, bx - 60, by - 60, 1.2)
    if toca and golpe < 0.2:
        A.estrella_golpe(L, px - 10, py - 10, 90, C["elec"], 8)
    A.nevada(L, t)
    return c


@dib
def p12(L, t, a, b):
    # "Un invierno, en Corea del Sur, hubo gente que usó salchichas."
    e = t - a
    escena_corea(L, t, e, toca=t >= T_HUBO)
    K.pildora(L, "COREA DEL SUR, 2010", 540, 200, 70, C["coral"], C["blanco"], pop(t - T_COREA + 0.1) if t >= T_COREA - 0.1 else 0)
    if t >= T_SALCH2 - 0.05:
        visto(L, 820, 460, 100, pop(t - T_SALCH2 + 0.05))


@dib
def p13(L, t, a, b):
    # "Para no quitarse los guantes."
    e = t - a
    escena_corea(L, t, e, toca=True)
    K.pildora(L, "SIN QUITARSE LOS GUANTES", 540, 200, 60, C["lana"], C["blanco"], pop(e - 0.05))
    visto(L, 820, 460, 100, 1.0)
    for i in range(3):                                     # vaho del frío
        u = (e * 0.6 + i / 3) % 1.0
        K.circulo(L, 900 + i * 30 + u * 60, 1500 - u * 160, 30 + 50 * u, (255, 255, 255, int(200 * (1 - u))))


@dib
def p14(L, t, a, b):
    # "Para tu pantalla, una salchicha y tu dedo son lo mismo." → vuelve al cuadro 0
    A.fondo_puntos(L, C["menta"], C["menta2"], t)
    e = t - a
    igual = t >= T_SON - 0.05
    c = A.celular(L, 540, 520, 380, 720, cara="amor" if igual else "feliz", t=t, n=(NX, NY))
    us = sale((t - T_UNA + 0.1) / 0.3) if t >= T_UNA - 0.1 else 0
    ud = sale((t - T_YTU2 + 0.1) / 0.3) if t >= T_YTU2 - 0.1 else 0
    bail = math.sin(t * 6) * 5
    if us > 0:
        A.dedo(L, 260, 1290 + (1 - us) * 900 + bail, ang=90 + bail * 0.4, largo=900, s=1.1, tipo="salchicha", cara="feliz", t=t)
    if ud > 0:
        A.dedo(L, 820, 1290 + (1 - ud) * 900 - bail, ang=90 - bail * 0.4, largo=900, s=1.1, cara="feliz", t=t, mira=-1)
    if igual:
        ee = t - T_SON + 0.05
        txt(L, "=", 540, 1520, 330 * pop(ee), C["blanco"], borde=14, color_borde=TINTA)
    if t >= T_MISMO:
        confeti(L, t, T_MISMO)


FUN = {i: globals()[f"p{i}"] for i in range(1, NP + 1)}
assert len(FUN) == len(T)

# ------------------------------------------------------------------ subtítulos (palabra por palabra, 1–3 palabras)
FONT = K.FONT
AMARILLO = (255, 210, 63)
CLAVE = {"SALCHICHA": (255, 150, 110), "SALCHICHAS": (255, 150, 110)}
BOX = (120, 960, 1000, 1250)


def limpiar(w):
    for ch in ",.:;!¡\"…«»":
        w = w.replace(ch, "")
    return w.upper()


TOK = ["WOJTEK" if limpiar(x["w"]) == "VÓITEK" else limpiar(x["w"]) for x in words]
grupos, g = [], []
for i, x in enumerate(words):
    g.append(i)
    fin = x["w"][-1] in ".,:;?!"
    sig_pausa = i + 1 < len(words) and words[i + 1]["s"] - x["e"] > 0.25
    largo = sum(len(TOK[j]) for j in g) + len(g) - 1
    prox = len(TOK[i + 1]) if i + 1 < len(words) else 0
    if fin or sig_pausa or len(g) == 3 or largo + 1 + prox > 16:
        grupos.append(g); g = []
if g:
    grupos.append(g)
# no dejar una palabra corta sola al final de frase si cabe con el grupo anterior
i = 1
while i < len(grupos):
    a_, b_ = grupos[i - 1], grupos[i]
    if len(b_) == 1 and len(a_) <= 2 and words[a_[-1]]["w"][-1] not in ".,:;?!" and sum(len(TOK[j]) for j in a_ + b_) + len(a_) <= 17 \
            and words[b_[0]]["s"] - words[a_[-1]]["e"] < 0.25:
        grupos[i - 1] = a_ + b_; del grupos[i]
    else:
        i += 1


def ancho_toks(f, toks):
    return sum(f.getlength(x) for x in toks) + f.getlength(" ") * 1.15 * (len(toks) - 1)


def subtitulos(im, t):
    g = None
    for gi, gg in enumerate(grupos):
        s, e = words[gg[0]]["s"], words[gg[-1]]["e"]
        nxt = grupos[gi + 1] if gi + 1 < len(grupos) else None
        e_show = min(e + 0.25, words[nxt[0]]["s"]) if nxt else e + 0.5
        if s - 0.03 <= t < e_show:
            g = gg
            break
    if g is None:
        return
    toks = [TOK[j] for j in g]
    maxw = BOX[2] - BOX[0] - 40
    for size in range(92, 59, -4):
        f = ImageFont.truetype(FONT, size)
        if ancho_toks(f, toks) <= maxw:
            break
    d = ImageDraw.Draw(im, "RGBA")
    y = (BOX[1] + BOX[3]) / 2 - f.size * 0.56
    x = W / 2 - ancho_toks(f, toks) / 2
    for j, tok in zip(g, toks):
        activo = words[j]["s"] - 0.02 <= t < max(words[j]["e"], words[j]["s"] + 0.12)
        col = CLAVE.get(tok.strip("¿?"), AMARILLO if activo else (255, 255, 255))
        d.text((x + 4, y + 7), tok, font=f, fill=(0, 0, 0, 120), stroke_width=7, stroke_fill=(0, 0, 0, 120))
        d.text((x, y), tok, font=f, fill=col, stroke_width=7, stroke_fill=(20, 16, 16))
        x += f.getlength(tok) + f.getlength(" ") * 1.15


_GRANO = {}


def cuadro(f):
    t = (f - 1) / FPS
    k = plano_de(t)
    a, b = T[k]
    im = FUN[k](t, a, b)
    if not _GRANO:
        _GRANO["g"] = Image.effect_noise((W, H), 14).convert("RGB")
    im = Image.blend(im, Image.composite(im, _GRANO["g"], Image.new("L", (W, H), 236)), 0.18)
    subtitulos(im, t)
    return im


if __name__ == "__main__":
    dst = sys.argv[1]
    os.makedirs(dst, exist_ok=True)
    a = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    b = int(sys.argv[3]) if len(sys.argv) > 3 else FIN
    paso = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    for f in range(a, b + 1, paso):
        cuadro(f).save(os.path.join(dst, f"{f:05d}.png"), compress_level=1)
    print("ok", a, b)
