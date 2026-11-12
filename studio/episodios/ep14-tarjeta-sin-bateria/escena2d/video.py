"""Ep. 14 — "Tu tarjeta paga sin batería" (cómo paga una tarjeta sin contacto). 2D de comedia por código (PIL).
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





T_SIN = tw("sin")
T_NI = tw("Ni")
T_NADA = tw("nada")
T_LA = tw("La", 3.3)
T_PAGA2 = tw("paga", 4)
T_DE = [w["s"] for w in words if w["w"].startswith("¿De")][0]
T_SE = tw("Se", 7.3)
T_DENTRO = tw("Dentro")
T_ALAMBRE = tw("alambre")
T_ES = tw("Es", 10.8)
T_ANTENA = tw("antena")
T_CUANDO = tw("Cuando")
T_COBRAR = tw("cobrar")
T_ACTIVA = tw("activa")
T_CREA = tw("Crea")
T_CAMPO = tw("campo")
T_INVIS = tw("invisible")
T_TU = tw("Tú")
T_YEL = tw("y", 19)
T_ATRAPA = tw("atrapa")
T_PERO = tw("Pero")
T_CERCA = tw("cerca")
T_AUNOS = tw("a", 23.5)
T_CENT = tw("centímetros")
T_CON = tw("Con", 25)
T_PRENDE = tw("prende")
T_EN = tw("En", 27)
T_DESP = tw("despierta")
T_MANDA = tw("manda")
T_ESE = tw("Ese")
T_SOLA = tw("sola")
T_VEZ = tw("vez")
T_LAAL = tw("La", 32.6)
T_ALEJAS = tw("alejas")
T_QUEDA = tw("queda")
T_TUT = tw("Tu", 35)
T_APAG = tw("apagada")
T_SOLO2 = tw("Solo", 36.5)
T_DESP2 = tw("despierta", 37)
T_ACERCAS2 = tw("acercas", 38)

CORTES = [0.0, T_LA - 0.1, T_DE - 0.08, T_SE - 0.08, T_DENTRO - 0.08, T_CUANDO - 0.08, T_CREA - 0.1, T_TU - 0.1, T_PERO - 0.1, T_CON - 0.1, T_EN - 0.08,
          T_ESE - 0.06, T_LAAL - 0.06, T_TUT - 0.08, DUR]
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
def lerp(a, b, u):
    return a + (b - a) * u


def lp(p, q, u):
    return (lerp(p[0], q[0], u), lerp(p[1], q[1], u))


def rayos(L, t, c1, c2, cx=540, cy=900):
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=c1)
    for i in range(14):
        an = i * math.pi / 7 + t * 0.4
        K.poligono(L, [(cx, cy), (cx + math.cos(an) * 2400, cy + math.sin(an) * 2400), (cx + math.cos(an + 0.22) * 2400, cy + math.sin(an + 0.22) * 2400)], c2)


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


def heroe(L, t, bat=1.0, pil=0.0, nada=0.0, cara="dormido", pild=1.0):
    """Cuadro 0 y cierre: la tarjeta durmiendo y la batería tachada."""
    A.fondo_puntos(L, C["crema"], C["crema2"], t)
    A.tarjeta(L, 540, 800 + math.sin(t * 2) * 8, 800, cara=cara, t=t)
    if cara == "dormido":
        A.zzz(L, 900, 520, t, 0.8)
    if bat > 0:
        A.bateria(L, 190, 240, 1.0 * bat, nivel=0.7, tachada=1.0)
    if pild > 0:
        K.pildora(L, "SIN BATERÍA", 690, 240, 76, C["rojo"], C["blanco"], pild)
    if pil > 0:
        A.pila(L, 250, 1480, 1.0 * pil, tachada=1.0)
        K.pildora(L, "NI PILA", 520, 1480, 76, C["blanco"], TINTA, pil)
    if nada > 0:
        K.pildora(L, "NI NADA", 780, 1640, 84, C["cel"], C["blanco"], nada)


@dib
def p1(L, t, a, b):
    heroe(L, t, bat=1.0, pil=pop(t - T_NI + 0.05) if t >= T_NI - 0.05 else 0, nada=pop(t - T_NADA + 0.05) if t >= T_NADA - 0.05 else 0)


@dib
def p2(L, t, a, b):
    # "La acercas y paga igual."
    A.fondo_puntos(L, C["cielo4"], C["cielo5"], t)
    paga = t >= T_PAGA2
    A.maquina(L, 400, 1560, 1.0, t, "feliz" if paga else "normal", pantalla=C["verde"] if paga else None)
    u = sale((t - a) / (T_PAGA2 - a - 0.05))
    cx, cy = lerp(1350, 640, u), lerp(250, 740, u)
    A.mano(L, cx + 250, cy + 60, 0.9)
    A.tarjeta(L, cx, cy, 560, cara="dormido" if not paga else "feliz", t=t)
    if paga:
        e = t - T_PAGA2
        A.estrella_golpe(L, 250, 420, 190 * pop(e), C["elec"], 10, rot=-0.2)
        txt(L, "¡BIP!", 250, 420, 100 * pop(e), C["coral"], borde=6, color_borde=TINTA)
        visto(L, 110, 1400, 84, pop(e - 0.1))
    K.pildora(L, "PAGADO" if paga else "LA ACERCAS", 540, 190, 80, C["verde2"] if paga else C["blanco"], C["blanco"] if paga else TINTA, pop(t - (T_PAGA2 if paga else a) - 0.02))


@dib
def p3(L, t, a, b):
    # "¿De dónde saca la energía?" — el viejo
    rayos(L, t, C["amarillo"], (255, 226, 110))
    K.viejo(L, 540, 1290, alto=760, boca=boca(t), t=t, gesto="tazon", mira=1)
    L.d.rectangle((0, L.S(1280), L.S(W), L.S(H)), fill=C["madera"])
    L.d.line([L.pt(0, 1280), L.pt(W, 1280)], fill=TINTA, width=int(L.S(8)))
    L.d.rectangle((0, L.S(1340), L.S(W), L.S(H)), fill=(150, 104, 60))
    A.tarjeta(L, 540, 1600, 420, cara="dormido", t=t)
    A.zzz(L, 760, 1470, t, 0.6)
    A.rayo(L, 250, 330 + math.sin(t * 6) * 10, 1.6, rot=-0.2)
    txt(L, "¿?", 800, 330, 220 * pop(t - a - 0.03), C["rojo"], borde=10, color_borde=TINTA)


@dib
def p4(L, t, a, b):
    # "Se la presta la máquina."
    rayos(L, t, C["cielo4"], C["cielo5"], 540, 720)
    e = t - a
    A.maquina(L, 540, 760 + math.sin(t * 8) * 8, 1.25, t, "fuerte")
    for i, (x, y, r) in enumerate(((170, 420, -0.3), (910, 420, 0.3), (150, 900, 0.2), (930, 900, -0.2))):
        A.rayo(L, x, y + math.sin(t * 9 + i) * 14, 1.3 * pop(e - 0.05 - i * 0.06), rot=r) if e > 0.05 + i * 0.06 else None
    K.pildora(L, "LA MÁQUINA", 540, 1400, 100, C["maq"], C["elec"], pop(e - 0.05))


@dib
def p5(L, t, a, b):
    # "Dentro del plástico hay un alambre enrollado. Es una antena."
    A.fondo_puntos(L, C["morado"], C["morado2"], t)
    e = t - a
    rx = sale((e - 0.1) / 0.6)
    bob = clamp((t - T_ALAMBRE + 0.1) / 0.9)
    ant = t >= T_ANTENA - 0.05
    A.tarjeta(L, 540, 700, 940, cara="dormido" if rx <= 0 else "nada", t=t, rayosx=rx, bobina=bob, carga=0.0, chip="dormido")
    if ant:                                               # la bobina "late" como antena
        ee = t - T_ANTENA + 0.05
        for i in range(3):
            u = (ee * 1.2 + i / 3) % 1.0
            K.caja_red(L, 540 - 470 - u * 90, 700 - 296 - u * 90, 540 + 470 + u * 90, 700 + 296 + u * 90, 60 + u * 60, None, (255, 214, 60, int(220 * (1 - u))), 12)
        K.pildora(L, "ES UNA ANTENA", 540, 1400, 96, C["elec"], TINTA, pop(ee))
    elif t >= T_ALAMBRE - 0.1:
        K.pildora(L, "ALAMBRE ENROLLADO", 540, 1400, 76, C["cobre"], C["blanco"], pop(t - T_ALAMBRE + 0.1))
    K.pildora(L, "POR DENTRO", 540, 200, 90, C["blanco"], TINTA, pop(e - 0.05))


@dib
def p6(L, t, a, b):
    # "Cuando te van a cobrar, la máquina se activa."
    A.fondo_puntos(L, C["cielo4"], C["cielo5"], t)
    e = t - a
    act = t >= T_ACTIVA - 0.05
    A.maquina(L, 540, 600, 1.1, t, "fuerte" if act else "normal", pantalla=C["maqp"] if act else (120, 130, 140), temblor=0.6 if act and t < T_ACTIVA + 0.3 else 0,
              emite=clamp((t - T_ACTIVA) / 0.3) if act else 0)
    # el dedo del cajero aprieta el botón verde
    bx, by = 540 + 105 * 1.1, 248 + 553 * 1.1
    u = sale((t - a) / (T_COBRAR - a)) if t < T_COBRAR + 0.25 else 1 - suave((t - T_COBRAR - 0.25) / 0.3)
    tip = lp((1250, 1300), (bx + 16, by + 16), u)
    A.dedo(L, tip[0], tip[1], ang=25, largo=1200, cara="nada", t=t)
    if 0 <= t - T_COBRAR < 0.25:
        A.estrella_golpe(L, bx, by, 100 * pop(t - T_COBRAR, 0.2), C["elec"], 8)
    if act:
        K.pildora(L, "ACTIVADA", 540, 1430, 100, C["verde2"], C["blanco"], pop(t - T_ACTIVA + 0.05))
    else:
        K.pildora(L, "TE VAN A COBRAR", 540, 1430, 80, C["blanco"], TINTA, pop(e - 0.05))


@dib
def p7(L, t, a, b):
    # "Crea a su alrededor un campo invisible de energía."
    A.fondo_puntos(L, C["cielo4"], C["cielo5"], t)
    e = t - a
    A.ondas(L, 540, 1250, t, 1.3, 1.0, n=5, ang=(180, 360), alcance=640)
    A.maquina(L, 540, 1570, 1.0, t, "fuerte")
    if t >= T_CAMPO - 0.05:
        K.pildora(L, "CAMPO DE ENERGÍA", 540, 200, 84, C["elec"], TINTA, pop(t - T_CAMPO + 0.05))
    if t >= T_INVIS - 0.05:
        K.pildora(L, "(INVISIBLE)", 540, 320, 60, C["blanco"], TINTA, pop(t - T_INVIS + 0.05))
    for i in range(6):                                    # chispitas flotando en el campo
        u = (e * 0.5 + i / 6) % 1.0
        an = math.radians(200 + i * 28)
        r = 200 + u * 620
        A.electron(L, 540 + math.cos(an) * r, 1250 + math.sin(an) * r, 26 * (1 - u * 0.5), t, "nada", brillo=0.8)


def escena_campo(L, t, cy_tarj, carga, chip="dormido", w=700):
    A.fondo_puntos(L, C["cielo4"], C["cielo5"], t)
    A.ondas(L, 540, 1250, t, 1.3, 1.0, n=5, ang=(180, 360), alcance=640)
    A.maquina(L, 540, 1570, 1.0, t, "fuerte")
    return A.tarjeta(L, 540, cy_tarj, w, cara="nada", t=t, rayosx=1.0, bobina=1.0, carga=carga, chip=chip)


@dib
def p8(L, t, a, b):
    # "Tú acercas la tarjeta y el alambre atrapa parte de esa energía."
    u = sale((t - a) / (T_YEL - a))
    cy = lerp(-250, 640, u)
    carga = clamp((t - T_ATRAPA + 0.1) / 1.3)
    escena_campo(L, t, cy, carga)
    if t >= T_ATRAPA - 0.1:
        K.pildora(L, "LA ATRAPA", 540, 200, 96, C["elec"], TINTA, pop(t - T_ATRAPA + 0.1))
    else:
        K.pildora(L, "TÚ LA ACERCAS", 540, 200, 80, C["blanco"], TINTA, pop(t - a - 0.05))


@dib
def p9(L, t, a, b):
    # "Pero solo funciona muy cerca: a unos pocos centímetros."
    cerca = t >= T_CERCA - 0.25
    u = suave((t - T_CERCA + 0.25) / 0.35) if cerca else 0
    cy = lerp(400, 760, u)
    carga = clamp((t - T_CERCA - 0.05) / 0.5) if cerca else 0
    A.fondo_puntos(L, C["cielo4"], C["cielo5"], t)
    A.ondas(L, 540, 1250, t, 1.0, 1.0, n=4, ang=(180, 360), alcance=420)
    A.maquina(L, 540, 1570, 1.0, t, "fuerte")
    A.tarjeta(L, 540, cy, 520, cara="nada", t=t, rayosx=1.0, bobina=1.0, carga=carga, chip="dormido")
    if not cerca:
        e = t - a
        equis(L, 910, 400, 80, pop(e - 0.15))
        K.pildora(L, "LEJOS", 540, 110, 80, C["blanco"], TINTA, pop(e - 0.05))
    else:
        e = t - T_CERCA + 0.25
        visto(L, 900, 760, 80, pop(e - 0.4))
        K.pildora(L, "CERCA", 540, 500, 84, C["verde2"], C["blanco"], pop(e - 0.3))
    if t >= T_AUNOS - 0.05:                               # la distancia entre la tarjeta y la máquina
        ee = t - T_AUNOS + 0.05
        y0, y1 = 760 + 170, 1250
        x = 930
        K.linea(L, [(x, y0), (x, lerp(y0, y1, sale(ee / 0.25)))], TINTA, 14)
        for yy in (y0, lerp(y0, y1, sale(ee / 0.25))):
            K.linea(L, [(x - 36, yy), (x + 36, yy)], TINTA, 14)
        K.pildora(L, "POCOS cm", 905, 1318, 52, C["elec"], TINTA, pop(ee - 0.2) if ee > 0.2 else 0)


@dib
def p10(L, t, a, b):
    # "Con esa energía se prende el chip."
    pr = t >= T_PRENDE
    if pr:
        rayos(L, t, C["morado"], (124, 104, 210), 540, 680)
    else:
        A.fondo_puntos(L, C["morado2"], (64, 50, 130), t)
    e = t - a
    # la energía llega por el alambre desde la izquierda
    u = clamp((t - a) / (T_PRENDE - a))
    K.linea(L, [(-20, 680), (250, 680)], TINTA, 40)
    K.linea(L, [(-20, 680), (250, 680)], C["cobre"], 24)
    K.linea(L, [(-20, 680), (lerp(-20, 250, u), 680)], C["elec"], 26)
    if not pr:
        K.circulo(L, lerp(-20, 250, u), 680, 34 + 8 * math.sin(t * 30), C["blanco"], C["elec"], 8)
    salto = abs(math.sin((t - T_PRENDE) * 12)) * 30 * clamp(1 - (t - T_PRENDE) / 0.6) if pr else 0
    A.chip_cara(L, 540, 680 - salto, 300, t, "despierto" if pr else "dormido", brillo=1.0 if pr else 0)
    if not pr:
        A.zzz(L, 800, 380, t, 1.1)
        for i in range(3):
            A.rayo(L, 250 + i * 290, 1480 + math.sin(t * 7 + i * 2) * 22, 1.2, rot=(-0.2, 0.15, -0.1)[i])
    else:
        K.pildora(L, "¡DESPIERTA!", 540, 1420, 104, C["elec"], TINTA, pop(t - T_PRENDE))
    K.pildora(L, "EL CHIP", 540, 190, 96, C["oro"], TINTA, pop(e - 0.05))


@dib
def p11(L, t, a, b):
    # "En un segundo o dos, despierta y le manda un código a la máquina."
    A.fondo_puntos(L, C["morado"], C["morado2"], t)
    e = t - a
    A.maquina(L, 540, 1600, 0.95, t, "feliz" if t > T_MANDA + 1.0 else "normal")
    A.chip_cara(L, 330, 560, 190, t, "feliz" if t >= T_DESP else "despierto", brillo=1.0)
    A.cronometro(L, 830, 480, 150, clamp(e / (T_MANDA + 0.9 - a)) * 0.03 * 60 / 2)
    K.pildora(L, "1 o 2 s", 830, 720, 70, C["blanco"], TINTA, pop(e - 0.1))
    if t >= T_MANDA:
        u = suave((t - T_MANDA) / 0.95)
        x = lerp(420, 540, u)
        y = lerp(760, 1290, u) - math.sin(u * math.pi) * 60
        A.boleta(L, x, y, 1.1, u=pop(t - T_MANDA, 0.2) * (1 - 0.5 * clamp((u - 0.85) / 0.15)))
        if u >= 1 and t - T_MANDA - 0.95 < 0.3:
            A.estrella_golpe(L, 540, 1285, 90 * pop(t - T_MANDA - 0.95, 0.2), C["elec"], 8)


@dib
def p12(L, t, a, b):
    # "Ese código sirve una sola vez."
    A.fondo_puntos(L, C["crema"], C["crema2"], t)
    e = t - a
    usado = t >= T_SOLA + 0.25
    A.boleta(L, 540, 640 + math.sin(t * 3) * 8, 2.6, u=pop(e - 0.02, 0.25), tachada=clamp((t - T_SOLA - 0.25) / 0.25) if usado else 0)
    if t >= T_SOLA - 0.1:
        A.sello(L, 540, 1440, "1 SOLA VEZ", 1.7, -0.1, u=clamp((t - T_SOLA + 0.1) / 0.14), color=C["rojo"])


@dib
def p13(L, t, a, b):
    # "La alejas, y el chip se queda sin energía."
    u = suave((t - a) / (T_QUEDA - a))
    cy = lerp(640, 330, u)
    carga = 1 - clamp((t - T_ALEJAS) / (T_QUEDA - T_ALEJAS + 0.3))
    dorm = carga <= 0.02
    c = escena_campo(L, t, cy, carga, chip="dormido" if dorm else "feliz", w=640)
    if dorm:
        A.zzz(L, c["chip"][0] + 80, c["chip"][1] - 90, t, 0.6)
        K.pildora(L, "SIN ENERGÍA", 540, 760, 84, C["cel"], C["blanco"], pop(t - T_QUEDA - 0.25) if t > T_QUEDA + 0.25 else 0)


@dib
def p14(L, t, a, b):
    # "Tu tarjeta pasa la vida apagada. Solo despierta cuando la acercas." → vuelve al cuadro 0
    desp = T_DESP2 - 0.05 <= t < T_ACERCAS2 + 0.35
    fin = t >= T_ACERCAS2 + 0.35
    heroe(L, t, bat=pop(t - T_ACERCAS2 - 0.35) if fin else 0, cara="despierto" if desp else "dormido", pild=pop(t - T_ACERCAS2 - 0.35) if fin else 0)
    if not fin:
        if desp:
            A.estrella_golpe(L, 300, 330, 170 * pop(t - T_DESP2 + 0.05), C["elec"], 10)
            txt(L, "¡!", 300, 330, 130 * pop(t - T_DESP2 + 0.05), C["coral"], borde=6, color_borde=TINTA)
        else:
            K.pildora(L, "APAGADA", 480, 300, 100, C["cel"], C["blanco"], pop(t - T_APAG + 0.1) if t >= T_APAG - 0.1 else 0)


FUN = {i: globals()[f"p{i}"] for i in range(1, NP + 1)}
assert len(FUN) == len(T)

# ------------------------------------------------------------------ subtítulos (palabra por palabra, 1–3 palabras)
FONT = K.FONT
AMARILLO = (255, 210, 63)
CLAVE = {"TARJETA": (120, 230, 220), "CHIP": (255, 214, 60)}
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
