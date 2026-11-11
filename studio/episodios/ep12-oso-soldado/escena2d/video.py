"""Ep. 12 — "El oso que fue soldado" (Wojtek, Segunda Guerra Mundial). 2D de comedia, todo por código (PIL).
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



T_CON = tw("Con")
T_RANGO = tw("rango")
T_NUM = tw("número")
T_LIB = tw("libreta")
T_ERA = tw("Era")
T_UNOS = tw("unos")
T_ADOP = tw("adoptaron")
T_DICEN = tw("Dicen")
T_YQUE = tw("y", 7.9)
T_CERV = tw("cerveza")
T_PERO = tw("Pero")
T_YEL = tw("Y", 11.5)
T_LO = tw("Lo", 12)
T_YSE = tw("y", 13)
T_RASO_S = tw("Soldado", 14)
T_RASO = tw("raso")
T_YEN = tw("Y", 15.3)
T_ANTES = tw("antes")
T_SEPUSO = tw("se", 17.3)
T_NO = tw("No", 18.5)
T_CARG = tw("cargaba")
T_SEGUN = tw("Según")
T_CUAR = tw("cuarenta")
T_DOS = tw("dos", 23)
T_IMAG = tw("Imagínate")
T_ESTAR = tw("estar")
T_COMP = tw("compañero")
T_OSO2 = tw("oso", 26)
T_ASC = tw("Lo", 26.5)
T_CABO = tw("cabo")
T_YSU = tw("Y", 27.8)
T_INSIG = tw("insignia")
T_UNOSO = tw("un", 29.5)
T_AL = tw("Al")
T_RETIRO = tw("retiró")
T_ZOO = tw("zoológico")
T_SE = tw("Se", 33.8)
T_NOMBRE = tw("Vóitek")

CORTES = [0.0, T_CON - 0.06, T_ERA - 0.08, T_UNOS - 0.05, T_DICEN - 0.06, T_YQUE - 0.04, T_PERO - 0.08, T_YEL - 0.06, T_LO - 0.08, T_YSE - 0.04,
          T_RASO_S - 0.1, T_YEN - 0.08, T_NO - 0.1, T_CARG - 0.05, T_SEGUN - 0.08, T_IMAG - 0.06, tw("y", 25.2) - 0.04, T_ASC - 0.06, T_YSU - 0.06, T_AL - 0.1,
          T_SE - 0.08, DUR]
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
def rayos(L, t, c1, c2, cx=540, cy=900):
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=c1)
    for i in range(14):
        an = i * math.pi / 7 + t * 0.4
        K.poligono(L, [(cx, cy), (cx + math.cos(an) * 2400, cy + math.sin(an) * 2400), (cx + math.cos(an + 0.22) * 2400, cy + math.sin(an + 0.22) * 2400)], c2)


def placa(L, s, cx, cy, tam, u=1.0, fondo=None, tinta=None):
    """Placa grande (nombre / rango)."""
    if u <= 0:
        return
    w = (len(s) * tam * 0.66 + tam * 1.2) * u
    h = tam * 1.7 * u
    K.caja_red(L, cx - w / 2 + 8, cy - h / 2 + 12, cx + w / 2 + 8, cy + h / 2 + 12, 24, (0, 0, 0, 80))
    K.caja_red(L, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 24, fondo or C["oliva2"], TINTA, 8)
    txt(L, s, cx, cy, tam * u, tinta or C["amarillo"])


def heroe(L, t, saludo=1.0, nombre=0.0, pild_u=1.0):
    """Cuadro 0 y cierre: el oso enorme con gorra, haciendo el saludo, y un soldado chico que lo mira."""
    A.campamento(L, 1260, t)
    A.soldado(L, 900, 1840, alto=420, t=t, mira=-1, cara="feliz", brazo_der=150, gorro="boina")
    A.oso(L, 400, 1850, alto=1300, t=t, saludo=saludo, ojos="normal", boca=0.0)
    if nombre > 0:
        placa(L, "WOJTEK", 540, 300, 150, nombre)
    elif pild_u > 0:
        K.pildora(L, "SEGUNDA GUERRA MUNDIAL", 540, 250, 54, C["rojo"], C["blanco"], pild_u)


@dib
def p1(L, t, a, b):
    heroe(L, t, saludo=1.0)


def check(L, x, y, s, texto, u):
    if u <= 0:
        return
    K.circulo(L, x, y, 34 * s * u, C["verde"], TINTA, 6)
    K.linea(L, [(x - 16 * s * u, y), (x - 4 * s * u, y + 14 * s * u), (x + 18 * s * u, y - 14 * s * u)], C["blanco"], 10 * s * u)
    txt(L, texto, x + 54 * s, y, 50 * s * u, TINTA, ancla="lm")


@dib
def p2(L, t, a, b):
    # "Con rango, número y libreta militar."
    rayos(L, t, (236, 220, 170), (244, 232, 190), 540, 620)
    u = sale((t - a) / 0.25)
    ox, oy = A.libreta(L, 540, 560 + (1 - u) * 900, 1.3, t=t)
    for i, (tt, s) in enumerate(((T_RANGO, "RANGO"), (T_NUM, "NÚMERO"), (T_LIB, "LIBRETA"))):
        check(L, ox + 30, oy + 60 + i * 120 + (1 - u) * 900, 1.3, s, pop(t - tt + 0.05) if t >= tt - 0.05 else 0)
    A.oso(L, 540, 1860, alto=600, t=t, saludo=1.0, ojos="feliz")


def biberon(L, x, y, s=1.0, rot=0.6):
    def R(dx, dy):
        return (x + dx * math.cos(rot) - dy * math.sin(rot), y + dx * math.sin(rot) + dy * math.cos(rot))
    K.poligono(L, [R(-34 * s, 90 * s), R(-34 * s, -40 * s), R(-14 * s, -70 * s), R(-14 * s, -110 * s), R(14 * s, -110 * s), R(14 * s, -70 * s), R(34 * s, -40 * s), R(34 * s, 90 * s)],
               C["blanco"], TINTA, 5)
    K.poligono(L, [R(-14 * s, -110 * s), R(0, -140 * s), R(14 * s, -110 * s)], (240, 170, 120), TINTA, 4)


def corazon(L, x, y, r, color=None):
    c = color or C["rojo"]
    K.circulo(L, x - r * 0.5, y - r * 0.3, r * 0.62, TINTA); K.circulo(L, x + r * 0.5, y - r * 0.3, r * 0.62, TINTA)
    K.poligono(L, [(x - r * 1.12, y - r * 0.06), (x + r * 1.12, y - r * 0.06), (x, y + r * 1.2)], TINTA)
    K.circulo(L, x - r * 0.5, y - r * 0.3, r * 0.5, c); K.circulo(L, x + r * 0.5, y - r * 0.3, r * 0.5, c)
    K.poligono(L, [(x - r * 0.94, y - r * 0.08), (x + r * 0.94, y - r * 0.08), (x, y + r * 1.0)], c)


@dib
def p3(L, t, a, b):
    # "Era un cachorro huérfano,"
    A.iran(L, 1260, t)
    K.pildora(L, "IRÁN", 540, 300, 96, C["rojo"], C["blanco"], pop(t - a - 0.05))
    A.oso(L, 540, 1760, alto=440, t=t, gorra=False, cabezon=1.5, ojos="triste")
    for i in range(2):                                  # lagrimitas
        u = ((t - a) * 1.3 + i * 0.5) % 1.0
        K.circulo(L, 470 + i * 150, 1450 + u * 120, 14, (150, 214, 240), TINTA, 3)


@dib
def p4(L, t, a, b):
    # "y unos soldados polacos lo adoptaron en Irán."
    A.iran(L, 1260, t)
    e = t - a
    ad = t >= T_ADOP
    xi = -200 + sale(e / 0.6) * 430
    xd = W + 200 - sale(e / 0.6) * 430
    A.soldado(L, xi, 1850, alto=600, t=t, mira=1, cara="feliz", paso=math.sin(t * 10) * (1 - clamp(e / 0.6)), gorro="boina", brazo_der=70 if ad else 8)
    A.soldado(L, xd, 1850, alto=600, t=t + 1, mira=-1, cara="feliz", paso=math.sin(t * 10 + 1) * (1 - clamp(e / 0.6)), gorro="boina", brazo_der=60 if ad else 8)
    salto = abs(math.sin((t - T_ADOP) * 9)) * 40 * clamp(1 - (t - T_ADOP) / 1.0) if ad else 0
    A.oso(L, 540, 1780 - salto, alto=440, t=t, gorra=False, cabezon=1.5, ojos="feliz" if ad else "triste", boca=0.6 if ad else 0)
    if ad:
        biberon(L, 400, 1500, 1.0, 0.9)
        for i in range(3):
            u = ((t - T_ADOP) * 0.9 + i / 3) % 1.0
            corazon(L, 440 + i * 100 + math.sin(u * 6 + i) * 20, 1280 - u * 300 - 0, 34 * (1 - u * 0.5) * min(1, u * 6))
        K.pildora(L, "ADOPTADO", 540, 300, 96, C["verde2"], C["blanco"], pop(t - T_ADOP))
    else:
        K.pildora(L, "SOLDADOS POLACOS", 540, 300, 70, C["oliva2"], C["blanco"], pop(e - 0.1))


@dib
def p5(L, t, a, b):
    # "Dicen que jugaba a luchar con ellos"
    A.campamento(L, 1260, t)
    e = t - a
    sube = sale(e / 0.35)
    o = A.oso(L, 500, 1850, alto=1300, t=t, brazo_der=60 + 118 * sube, brazo_izq=60 + 118 * sube, ojos="feliz", boca=0.7, lengua=True)
    my = o["mano"][1]
    bam = math.sin(t * 7) * 0.12
    sx = 500 + math.sin(t * 7) * 46
    A.soldado(L, sx, my - 20 + abs(math.sin(t * 14)) * -24, alto=380, t=t, mira=1, cara="susto", brazo_der=150 + 20 * math.sin(t * 20), brazo_izq=150 - 20 * math.sin(t * 20),
              sudor=True, gorro="boina", tiembla=1.0)
    A.soldado(L, 930, 1850, alto=440, t=t, mira=-1, cara="feliz", brazo_der=150, gorro="boina")
    K.pildora(L, "DICEN QUE…", 840, 620, 64, C["blanco"], TINTA, pop(e - 0.05))


def jarra(L, x, y, s=1.0, t=0.0):
    K.caja_red(L, x + 70 * s, y - 150 * s, x + 150 * s, y - 30 * s, 30 * s, None, TINTA, 22 * s)
    K.caja_red(L, x + 70 * s, y - 150 * s, x + 150 * s, y - 30 * s, 30 * s, None, C["blanco"], 9 * s)
    K.caja_red(L, x - 90 * s, y - 190 * s, x + 90 * s, y, 16 * s, (250, 190, 60), TINTA, 7)
    for i in range(4):
        K.circulo(L, x - 70 * s + i * 46 * s, y - 196 * s + math.sin(t * 5 + i) * 6 * s, 40 * s, C["blanco"], TINTA, 6)
    K.caja_red(L, x - 84 * s, y - 200 * s, x + 84 * s, y - 170 * s, 10 * s, C["blanco"])
    for dx in (-40, 20):
        K.linea(L, [(x + dx * s, y - 140 * s), (x + dx * s, y - 40 * s)], (255, 226, 130), 12 * s)


@dib
def p6(L, t, a, b):
    # "y que le gustaba la cerveza."
    A.campamento(L, 1260, t)
    e = t - a
    brinda = 128 + 10 * math.sin(t * 6)
    o = A.oso(L, 320, 1850, alto=1300, t=t, brazo_der=brinda, brazo_izq=10, ojos="feliz", boca=0.5 + 0.3 * math.sin(t * 9))
    jarra(L, o["mano"][0] + 10, o["mano"][1] + 60, 1.0, t)
    A.soldado(L, 900, 1850, alto=440, t=t, mira=-1, cara="feliz", brazo_der=120 + 14 * math.sin(t * 6 + 1), gorro="boina")
    K.pildora(L, "DICEN QUE…", 230, 330, 64, C["blanco"], TINTA, 1.0)
    for i in range(4):
        u = (e * 0.8 + i / 4) % 1.0
        K.circulo(L, o["mano"][0] + 40 + math.sin(u * 9 + i) * 60, o["mano"][1] - 230 - u * 260, 16 + 10 * u, (255, 255, 255, int(230 * (1 - u))), TINTA, 3)


@dib
def p7(L, t, a, b):
    # "Pero a los soldados los mandaron a pelear a Italia."
    A.puerto(L, t)
    A.barco(L, 640, 1420, 0.95, t)
    A.muelle(L, 1560)
    e = t - a
    for i in range(4):
        x = -150 + e * 330 - i * 170 + 420
        if x < W + 100:
            A.soldado(L, x, 1850 - (i % 2) * 30, alto=440, t=t + i, mira=1, cara="normal", paso=math.sin(t * 10 + i), gorro="casco")
    K.pildora(L, "RUMBO A ITALIA", 540, 300, 84, C["rojo"], C["blanco"], pop(t - tw("mandaron") + 0.05) if t >= tw("mandaron") - 0.05 else 0)


@dib
def p8(L, t, a, b):
    # "¿Y el oso?"
    A.puerto(L, t)
    e = t - a
    A.barco(L, 640 + e * 60, 1420, 0.95, t)
    A.muelle(L, 1560)
    o = A.oso(L, 420, 1860, alto=600, t=t, gorra=False, ojos="triste", brazo_der=150 + 20 * math.sin(t * 8))
    for i in range(2):
        u = (e * 1.5 + i * 0.5) % 1.0
        K.circulo(L, o["cabeza"][0] - 60 + i * 150, o["cabeza"][1] + 20 + u * 150, 16, (150, 214, 240), TINTA, 3)
    txt(L, "?", 800, 600, 460 * pop(e - 0.05), C["rojo"], borde=12, color_borde=TINTA)


@dib
def p9(L, t, a, b):
    # "Lo enlistaron,"
    rayos(L, t, (236, 220, 170), (244, 232, 190), 540, 620)
    A.libreta(L, 540, 560, 1.3, t=t)
    e = t - (tw("enlistaron") - 0.02)
    if e > 0:
        A.sello(L, 660, 640, "ENLISTADO", 1.15, -0.16, u=clamp(e / 0.14))
        if e < 0.3:
            for i in range(8):
                an = i * math.pi / 4
                K.linea(L, [(660 + math.cos(an) * (340 + e * 500), 640 + math.sin(an) * (150 + e * 300)), (660 + math.cos(an) * (400 + e * 600), 640 + math.sin(an) * (190 + e * 380))], TINTA, 10)
    A.oso(L, 540, 1860, alto=600, t=t, gorra=e > 0.1, ojos="feliz" if e > 0.1 else "normal", saludo=clamp((e - 0.1) / 0.2), boca=0.5 if e > 0.1 else 0)


@dib
def p10(L, t, a, b):
    # "y se fue con ellos."
    A.puerto(L, t, mar_y=1300)
    e = t - a
    bx = 620 + e * 120
    by = 1720
    A.oso(L, bx - 390, 1560 + math.sin(t * 2) * 10, alto=900, t=t, ojos="feliz", brazo_der=150 + 25 * math.sin(t * 9), boca=0.5)
    A.barco(L, bx, by, 1.3, t)
    L.d.rectangle((0, L.S(1790), L.S(W), L.S(H)), fill=C["mar"])
    for i in range(3):
        y = 1800 + i * 44
        for j in range(5):
            x = (j * 260 + i * 90 - t * 120) % (W + 200) - 100
            L.d.arc((L.S(x), L.S(y), L.S(x + 120), L.S(y + 40)), 200, 340, fill=C["mar2"], width=int(L.S(7)))
    K.pildora(L, "¡A BORDO!", 540, 300, 96, C["verde2"], C["blanco"], pop(e - 0.05))


@dib
def p11(L, t, a, b):
    # "Soldado raso."
    rayos(L, t, C["oliva"], (142, 152, 98))
    A.oso(L, 540, 1880, alto=1300, t=t, saludo=sale((t - a) / 0.25), ojos="serio")
    placa(L, "SOLDADO RASO", 540, 300, 96, pop(t - T_RASO_S))


def dos_con_caja(L, x, y, t, anda=1.0):
    """Dos soldados cargando una caja entre los dos, sufriendo."""
    bob = abs(math.sin(t * 8)) * 14 * anda
    A.soldado(L, x - 190, y, alto=420, t=t, mira=1, cara="susto", paso=math.sin(t * 8) * anda, sudor=True, gorro="casco", brazo_der=62, brazo_izq=62, tiembla=0.6)
    A.soldado(L, x + 190, y, alto=420, t=t + 1, mira=-1, cara="susto", paso=math.sin(t * 8 + 2) * anda, sudor=True, gorro="casco", brazo_der=62, brazo_izq=62, tiembla=0.6)
    A.caja_muni(L, x, y - 230 + bob, 0.95, math.sin(t * 8) * 0.05)


@dib
def p12(L, t, a, b):
    # "Y en Italia, antes de una gran batalla, se puso a trabajar."
    A.batalla(L, 1260, t)
    e = t - a
    K.pildora(L, "ITALIA, 1944", 540, 280, 84, C["rojo"], C["blanco"], pop(e - 0.05))
    if t >= T_ANTES - 0.05:
        K.pildora(L, "ANTES DE LA BATALLA", 540, 400, 54, C["blanco"], TINTA, pop(t - T_ANTES + 0.05))
    dos_con_caja(L, 300 + e * 70, 1850, t)
    tra = t >= T_SEPUSO
    ox = W + 300 - sale((t - T_ANTES) / 0.6) * 560
    A.oso(L, ox, 1860, alto=600, t=t, ojos="serio" if tra else "normal", camina=1.0 if t < T_ANTES + 0.6 else 0, mira=-1,
          brazo_der=10 + (120 * abs(math.sin((t - T_SEPUSO) * 10)) if tra else 0), brazo_izq=10 + (120 * abs(math.cos((t - T_SEPUSO) * 10)) if tra else 0))
    if tra:
        K.pildora(L, "¡YO PUEDO!", 800, 1360 - 620, 60, C["amarillo"], TINTA, pop(t - T_SEPUSO))


def fusil(L, x, y, s=1.0):
    K.poligono(L, [(x - 260 * s, y - 10 * s), (x - 120 * s, y - 26 * s), (x - 120 * s, y + 30 * s), (x - 230 * s, y + 70 * s)], C["madera"], TINTA, 6)
    K.caja_red(L, x - 130 * s, y - 28 * s, x + 80 * s, y + 24 * s, 8 * s, C["madera"], TINTA, 6)
    K.caja_red(L, x + 60 * s, y - 22 * s, x + 300 * s, y + 4 * s, 8 * s, C["metal"], TINTA, 6)
    K.caja_red(L, x - 40 * s, y + 20 * s, x - 10 * s, y + 70 * s, 6 * s, C["metal2"], TINTA, 5)


@dib
def p13(L, t, a, b):
    # "No disparaba:"
    rayos(L, t, (240, 214, 150), (248, 226, 172), 540, 760)
    e = t - a
    fusil(L, 540, 620, 1.3)
    u = pop(e - 0.08)
    if u > 0:
        K.circulo(L, 540, 620, 330 * u, None, TINTA, 62)
        K.circulo(L, 540, 620, 330 * u, None, C["rojo"], 44)
        K.linea(L, [(540 - 232 * u, 620 - 232 * u), (540 + 232 * u, 620 + 232 * u)], TINTA, 62)
        K.linea(L, [(540 - 226 * u, 620 - 226 * u), (540 + 226 * u, 620 + 226 * u)], C["rojo"], 44)
    A.oso(L, 540, 1870, alto=600, t=t, ojos="normal", brazo_der=20 + 30 * math.sin(t * 9), brazo_izq=20 - 30 * math.sin(t * 9))


def camion_muni(L, x, y, s=1.0, n=2):
    K.caja_red(L, x - 300 * s, y - 250 * s, x + 300 * s, y - 80 * s, 10 * s, C["oliva2"], TINTA, 7)
    for i in range(n):
        A.caja_muni(L, x - 150 * s + i * 300 * s, y - 330 * s, 0.9 * s)
    for dx in (-190, 190):
        K.circulo(L, x + dx * s, y - 66 * s, 70 * s, (44, 40, 40), TINTA, 6)
        K.circulo(L, x + dx * s, y - 66 * s, 26 * s, C["metal"], TINTA, 4)


@dib
def p14(L, t, a, b):
    # "cargaba cajas de municiones."
    A.batalla(L, 1260, t)
    e = t - a
    camion_muni(L, 1080, 1840, 1.0, 1)
    ox = 230 + e * 70
    o = A.oso(L, ox, 1860, alto=1300, t=t, brazo_der=88, brazo_izq=88, camina=0.9, ojos="serio")
    A.caja_muni(L, o["mano"][0] - 70, o["mano"][1] - 90, 1.0, math.sin(t * 8) * 0.03)
    K.pildora(L, "MUNICIONES", 540, 280, 84, C["amarillo"], TINTA, pop(t - tw("municiones") + 0.05) if t >= tw("municiones") - 0.05 else 0)


@dib
def p15(L, t, a, b):
    # "Según un museo de Polonia, de cuarenta kilos, y en dos patas."
    A.batalla(L, 1260, t)
    e = t - a
    o = A.oso(L, 300 + math.sin(t * 2) * 10, 1860, alto=1300, t=t, brazo_der=88, brazo_izq=88, camina=0.55, ojos="serio")
    cx, cy = o["mano"][0] - 70, o["mano"][1] - 90
    A.caja_muni(L, cx, cy, 1.25, math.sin(t * 5) * 0.03)
    K.pildora(L, "SEGÚN EL MUSEO DE HISTORIA DE POLONIA", 540, 250, 38, C["blanco"], TINTA, pop(e - 0.05))
    if t >= T_CUAR - 0.05:
        K.pildora(L, "40 kg", 800, 560, 130, C["rojo"], C["blanco"], pop(t - T_CUAR + 0.05))
    if t >= T_DOS - 0.05:
        u = pop(t - T_DOS + 0.05)
        K.pildora(L, "EN DOS PATAS", 700, 1540, 66, C["amarillo"], TINTA, u)
        for px in (200, 400):
            K.linea(L, [(px + 190, 1620), (px + 60, 1760)], TINTA, 16 * u)
            K.linea(L, [(px + 190, 1620), (px + 60, 1760)], C["amarillo"], 8 * u)


@dib
def p16(L, t, a, b):
    # "Imagínate" — el viejo
    rayos(L, t, C["amarillo"], (255, 226, 110))
    K.viejo(L, 540, 2280, alto=1000, boca=boca(t), t=t, gesto="tazon", mira=1)
    txt(L, "IMAGÍNATE…", 540, 360, 130 * pop(t - a - 0.03), C["rojo"], borde=9, color_borde=TINTA)


@dib
def p17(L, t, a, b):
    # "estar en la guerra y que tu compañero sea un oso."
    A.batalla(L, 1100, t)
    e = t - a
    ve = t >= T_COMP
    # trinchera: sacos de arena adelante
    A.soldado(L, 190, 1770, alto=520, t=t, mira=1 if ve else -1, cara="susto" if t >= T_OSO2 - 0.15 else "normal", gorro="casco", sudor=t >= T_OSO2 - 0.15, tiembla=1.0 if t >= T_OSO2 - 0.15 else 0)
    K.pildora(L, "TÚ", 190, 880, 80, C["rojo"], C["blanco"], pop(e - 0.05))
    entra = sale((t - T_COMP + 0.25) / 0.35) if t >= T_COMP - 0.25 else 0
    o = A.oso(L, 1750 - entra * 850, 1900, alto=1300, t=t, mira=-1, ojos="feliz", brazo_der=40, brazo_izq=30, boca=0.4)
    if entra > 0:
        A.proyectil(L, o["mano"][0] - 30, o["mano"][1] - 60, 0.7, -0.25)
    for i in range(5):
        for j in range(2):
            x = -60 + i * 250 + j * 125
            K.caja_red(L, x, 1700 + j * 110, x + 240, 1700 + j * 110 + 104, 46, (196, 170, 120), TINTA, 7)
    L.d.rectangle((0, L.S(1910), L.S(W), L.S(H)), fill=(196, 170, 120))
    if t >= T_OSO2 - 0.1:
        A.estrella_golpe(L, 190, 600, 150 * pop(t - T_OSO2 + 0.1), C["amarillo"], 9)
        txt(L, "¡¿?!", 190, 600, 90 * pop(t - T_OSO2 + 0.1), C["rojo"], borde=5, color_borde=TINTA)


@dib
def p18(L, t, a, b):
    # "Lo ascendieron a cabo."
    rayos(L, t, C["oliva"], (142, 152, 98))
    e = t - (T_CABO - 0.25)
    A.oso(L, 540, 1880, alto=1300, t=t, saludo=sale((t - a) / 0.25), ojos="feliz" if e > 0 else "normal", galones=e > 0, boca=0.5 if e > 0 else 0)
    if 0 < e < 0.45:
        A.estrella_golpe(L, 720, 1140, 170 * pop(e), C["amarillo"], 10)
    placa(L, "CABO", 540, 300, 150, pop(e) if e > 0 else 0)


def insignia(L, cx, cy, r, t, u=1.0):
    r = r * u
    if r < 4:
        return
    for i in range(16):
        an = i * math.pi / 8 + t * 0.6
        K.poligono(L, [(cx, cy), (cx + math.cos(an) * r * 1.5, cy + math.sin(an) * r * 1.5), (cx + math.cos(an + 0.16) * r * 1.5, cy + math.sin(an + 0.16) * r * 1.5)], (255, 240, 170))
    K.circulo(L, cx, cy, r, C["oliva2"], TINTA, 10)
    K.circulo(L, cx, cy, r * 0.88, C["oliva"], C["amarillo"], 8)
    k = r / 400.0
    o = A.oso(L, cx - 40 * k, cy + 290 * k, alto=560 * k, t=0, gorra=False, brazo_der=92, brazo_izq=92, camina=0, tono={"oso": C["papel"], "oso2": (226, 214, 184), "oso3": C["papel"], "nariz": TINTA, "ojo": TINTA})
    A.proyectil(L, o["mano"][0] + 30 * k, o["mano"][1] - 50 * k, 0.7 * k, 0.5)


@dib
def p19(L, t, a, b):
    # "Y su compañía cambió su insignia: un oso cargando un proyectil."
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=(70, 82, 56))
    for i in range(9):
        L.d.line([L.pt(-200 + i * 190, 0), L.pt(200 + i * 190, H)], fill=(78, 92, 62), width=int(L.S(60)))
    e = t - a
    cambia = T_INSIG - 0.05
    if t < cambia:                                      # la insignia vieja (una estrella cualquiera) sale volando
        A.estrella_golpe(L, 540, 620, 300, C["amarillo"], 5, rot=-0.3 + e * 0.3)
        K.pildora(L, "INSIGNIA", 540, 1350, 84, C["blanco"], TINTA, pop(e - 0.05))
    else:
        f = t - cambia
        if f < 0.4:
            A.estrella_golpe(L, 540 + f * 2600, 620 - f * 1500, 300 * (1 - f), C["amarillo"], 5, rot=f * 9)
        insignia(L, 540, 620 + math.sin(t * 2.4) * 8, 400, t, pop(f, 0.35))
        K.pildora(L, "LA NUEVA INSIGNIA", 540, 1350, 70, C["amarillo"], TINTA, pop(f - 0.2) if f > 0.2 else 0)
    for i, x in enumerate((190, 890)):
        A.soldado(L, x, 1900, alto=420, t=t + i, mira=1 if i == 0 else -1, cara="feliz", brazo_der=150, gorro="boina")


@dib
def p20(L, t, a, b):
    # "Al terminar la guerra, se retiró a un zoológico de Escocia."
    A.pradera(L, 1260, t)
    e = t - a
    K.caja_red(L, 150, 220, 930, 420, 20, C["madera"], TINTA, 8)
    for px in (230, 850):
        K.caja_red(L, px - 14, 60, px + 14, 220, 4, C["madera"], TINTA, 6)
    txt(L, "ZOOLÓGICO", 540, 285, 84, C["blanco"])
    txt(L, "ESCOCIA", 540, 370, 60 * (pop(t - T_ZOO - 0.3) if t > T_ZOO + 0.3 else 0.01), C["amarillo"])
    o = A.oso(L, 540, 1820, alto=600, t=t, gorra=True, ojos="feliz", brazo_der=150 + 25 * math.sin(t * 8), boca=0.5, galones=True)
    for i in range(8):                                  # reja baja adelante
        x = 30 + i * 146
        K.caja_red(L, x, 1660, x + 30, 1920, 10, C["blanco"], TINTA, 6)
    for y in (1720, 1830):
        K.caja_red(L, -10, y, W + 10, y + 26, 8, C["blanco"], TINTA, 6)
    K.pildora(L, "RETIRADO", 240, 1500, 60, C["verde2"], C["blanco"], pop(t - T_RETIRO) if t >= T_RETIRO else 0)


@dib
def p21(L, t, a, b):
    # "Se llamaba Wojtek." → vuelve al cuadro 0 (loop)
    heroe(L, t, saludo=1.0, nombre=pop(t - T_NOMBRE + 0.08) if t >= T_NOMBRE - 0.08 else 0, pild_u=0)
    if t >= T_NOMBRE:
        confeti(L, t, T_NOMBRE)


FUN = {i: globals()[f"p{i}"] for i in range(1, NP + 1)}
assert len(FUN) == len(T)

# ------------------------------------------------------------------ subtítulos (palabra por palabra, 1–3 palabras)
FONT = K.FONT
AMARILLO = (255, 210, 63)
CLAVE = {"OSO": (255, 170, 80), "WOJTEK": (255, 170, 80)}
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
