"""Ep. 15 — "No te puedes hacer cosquillas" (por qué las de otro sí, si en los dos casos sabes que vienen). 2D de comedia por código (PIL).
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
_envp = os.path.join(AQUI, "envolvente.json")
ENV = json.load(open(_envp)) if os.path.exists(_envp) else []
FIN_VOZ = words[-1]["e"]
COLA = 0.9                                   # vuelta al cuadro 0 después de la última palabra (loop)
DUR = FIN_VOZ + COLA
FIN = int(round(DUR * FPS))


def tw(prefijo, desde=0.0):
    p = prefijo.lower()
    for w in words:
        if w["s"] >= desde - 0.01 and w["w"].lower().strip(".,;:…!?¡¿").startswith(p):
            return w["s"]
    raise KeyError(prefijo)


def te(prefijo, desde=0.0):
    p = prefijo.lower()
    for w in words:
        if w["s"] >= desde - 0.01 and w["w"].lower().strip(".,;:…!?¡¿").startswith(p):
            return w["e"]
    raise KeyError(prefijo)


def ts(frase, desde=0.0):
    """Inicio de la primera palabra de una frase (varias palabras seguidas)."""
    ps = [p.lower() for p in frase.split()]
    lim = lambda w: w["w"].lower().strip(".,;:…!?¡¿")
    for i in range(len(words) - len(ps) + 1):
        if words[i]["s"] >= desde - 0.01 and all(lim(words[i + j]) == ps[j] for j in range(len(ps))):
            return words[i]["s"]
    raise KeyError(frase)


T_NO = ts("No pasa nada")
T_NADA = tw("nada")
T_PERO = ts("Pero si te")
T_OTRO = tw("otro")
T_RETUER = tw("retuerces")
T_POR = ts("por qué")
T_DOS = tw("dos")
T_SABES = tw("sabes")
T_PARA = ts("Para mover")
T_CEREBRO = tw("cerebro")
T_ORDEN = tw("orden")
T_YSE = ts("Y se guarda")
T_COPIA = tw("copia")
T_CON = ts("Con ella")
T_CUANDO = tw("cuándo")
T_DONDE = tw("dónde")
T_TOCAR = tw("tocar")
T_YLE = ts("Y le baja")
T_BAJA = tw("baja")
T_PERO2 = ts("Pero de la")
T_OTRO2 = tw("otro", T_PERO2)
T_NOHAY = ts("no hay copia")
T_NADIE = tw("Nadie")
T_LA = ts("La prueba")
T_MUEVES = tw("mueves")
T_ROBOT = tw("robot")
T_HACE2 = tw("hace", T_ROBOT)
T_NO2 = ts("No pasa nada", T_ROBOT)
T_PERO3 = ts("Pero si se")
T_ATRASA = tw("atrasa")
T_FRACC = tw("fracción")
T_SITE = ts("sí te dan")
T_AUNQUE = tw("Aunque")
T_SEPAS = tw("sepas")
T_NOBASTA = ts("No basta")
T_TU2 = ts("tu cerebro tiene")
T_PREDIC = tw("predecirlas")

CORTES = [0.0, T_PERO - 0.08, T_POR - 0.1, T_PARA - 0.08, T_YSE - 0.06, T_CON - 0.06, T_YLE - 0.06, T_PERO2 - 0.08, T_NADIE - 0.06,
          T_LA - 0.08, T_NO2 - 0.06, T_PERO3 - 0.06, T_AUNQUE - 0.06, T_NOBASTA - 0.08, FIN_VOZ + 0.3, DUR]
T = {i + 1: (CORTES[i], CORTES[i + 1]) for i in range(len(CORTES) - 1)}
NP = len(T)
for _k, (_a, _b) in T.items():
    assert _b - _a >= 0.55, (_k, _a, _b)


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


def pp(t, t0):
    return pop(t - t0) if t >= t0 else 0.0


def lerp(a, b, u):
    return a + (b - a) * u


def lp(p, q, u):
    return (lerp(p[0], q[0], u), lerp(p[1], q[1], u))


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


def rayos(L, t, c1, c2, cx=540, cy=900):
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=c1)
    for i in range(14):
        an = i * math.pi / 7 + t * 0.4
        K.poligono(L, [(cx, cy), (cx + math.cos(an) * 2400, cy + math.sin(an) * 2400), (cx + math.cos(an + 0.22) * 2400, cy + math.sin(an + 0.22) * 2400)], c2)


def fondo_tipo(L, t):
    A.fondo_puntos(L, C["durazno"], C["durazno2"], t)


def fondo_cabeza(L, t):
    A.fondo_puntos(L, C["noche2"], C["noche3"], t)


# ------------------------------------------------------------------ el protagonista con su propia mano (cuadro 0 y cierre)
def auto_cosquillas(L, t, cara="aburrido", pild=1.0, cx=540, cy=520, r=190):
    """Se hace cosquillas en la axila con su propia mano; el otro brazo arriba, detrás de la cabeza."""
    pts = A.tipo(L, cx, cy, r, t, cara)
    # brazo izquierdo (el de la axila) levantado detrás de la cabeza
    A.brazo(L, pts["hom_d"], (cx + r * 1.6, cy - r * 1.0), C["polera"], 70, 0.3, 1)
    K.circulo(L, cx + r * 1.6, cy - r * 1.0, 42, C["piel"], TINTA, 6)
    # brazo derecho cruza y hace cosquillas en la axila
    w = (pts["axi_d"][0] - 60, pts["axi_d"][1] + 30)
    A.brazo(L, pts["hom_i"], w, C["polera"], 70, 0.34, 1)
    A.mano_cosq(L, w[0] + 20, w[1] - 6, -0.25, 1.05, t)
    K.pildora(L, "COSQUILLAS:", 540, 150, 70, C["coral"], C["blanco"], 1.0)
    if pild > 0:
        K.pildora(L, "NO PASA NADA", 540, 262, 84, C["blanco"], TINTA, pild)
    return pts


@dib
def p1(L, t, a, b):
    # "Hazte cosquillas. No pasa nada."
    fondo_tipo(L, t)
    auto_cosquillas(L, t, "aburrido", pild=pp(t, T_NO - 0.05))
    if t >= T_NADA:                                        # grillos: "cri cri"
        e = t - T_NADA
        txt(L, "cri cri", 900, 360 - (e * 20 % 30), 46 * pop(e), C["blanco"], borde=5, color_borde=TINTA)


@dib
def p2(L, t, a, b):
    # "Pero si te las hace otro, te retuerces de risa."
    risa = t >= T_RETUER - 0.05
    fondo_tipo(L, t) if not risa else rayos(L, t, C["amarillo"], (255, 228, 120), 540, 560)
    pts = A.tipo(L, 540, 520, 190, t, "risa" if risa else "sorpresa", temblor=1.0 if risa else 0.0)
    sh = math.sin(t * 40) * 18 if risa else 0
    for lado, k in ((-1, "hom_i"), (1, "hom_d")):          # sus brazos, arriba (se defiende)
        m = (540 + lado * 380 + sh, 300 + (abs(sh) if lado > 0 else -abs(sh)))
        A.brazo(L, pts[k], m, C["polera"], 70, 0.3, lado)
        K.circulo(L, m[0], m[1], 44, C["piel"], TINTA, 6)
    u = sale((t - T_OTRO + 0.25) / 0.45) if t >= T_OTRO - 0.25 else 0.0
    if u > 0:                                              # las manos de OTRO entran por los lados (manga morada)
        for lado, k in ((-1, "cos_i"), (1, "cos_d")):
            tgt = (pts[k][0] - lado * 10, pts[k][1] + 10)
            p = lp((540 + lado * 900, tgt[1] + 120), tgt, u)
            ang = math.pi if lado > 0 else 0.0
            K.miembro(L, [(540 + lado * 1200, p[1] + 60), (p[0] + lado * 60, p[1])], C["otro"], 80)
            A.manga(L, (p[0] + lado * 70, p[1]), ang, 1.1, C["otro2"])
            A.mano_cosq(L, p[0], p[1], ang, 1.05, t, 1.0, fase=lado)
        K.pildora(L, "OTRO", 860, 800, 80, C["otro"], C["blanco"], pp(t, T_OTRO))
    if risa:
        A.jaja(L, 540, 470, t, T_RETUER, 330, 5, 88)
    else:
        K.pildora(L, "¿Y SI ES OTRO?", 540, 170, 76, C["blanco"], TINTA, pp(t, a + 0.05))


def mini(L, t, cx, cara, otro):
    """Medio panel: el protagonista chico con su mano o con la de otro."""
    r = 120
    pts = A.tipo(L, cx, 640, r, t, cara, temblor=0.8 if cara == "risa" else 0)
    A.brazo(L, pts["hom_d"], (cx + r * 1.6, 640 - r * 1.0), C["polera"], 46, 0.3, 1)
    K.circulo(L, cx + r * 1.6, 640 - r * 1.0, 28, C["piel"], TINTA, 5)
    w = (pts["axi_d"][0] - 30, pts["axi_d"][1] + 20)
    if otro:
        A.brazo(L, pts["hom_i"], (cx - r * 1.6, 640 - r * 1.0), C["polera"], 46, 0.3, -1)
        K.circulo(L, cx - r * 1.6, 640 - r * 1.0, 28, C["piel"], TINTA, 5)
        K.miembro(L, [(cx + 330, w[1] + 40), (w[0] + 50, w[1])], C["otro"], 54)
        A.manga(L, (w[0] + 56, w[1]), math.pi, 0.75, C["otro2"])
        A.mano_cosq(L, w[0], w[1], math.pi, 0.7, t, 1.0)
    else:
        A.brazo(L, pts["hom_i"], w, C["polera"], 46, 0.34, 1)
        A.mano_cosq(L, w[0] + 12, w[1] - 4, -0.25, 0.7, t)


@dib
def p3(L, t, a, b):
    # "¿Por qué, si en los dos casos sabes que vienen?"
    A.fondo_puntos(L, C["durazno"], C["durazno2"], t)
    L.d.rectangle((L.S(540), 0, L.S(W), L.S(H)), fill=C["rosa"])
    for y in range(40, H, 120):
        for x in range(600, W, 120):
            K.circulo(L, x + (60 if (y // 120) % 2 else 0), y, 8, C["rosa2"])
    K.linea(L, [(540, 0), (540, H)], TINTA, 10)
    mini(L, t, 270, "aburrido", False)
    mini(L, t, 810, "risa", True)
    K.pildora(L, "TU MANO", 270, 1440, 64, C["polera"], C["blanco"], pp(t, a + 0.05))
    K.pildora(L, "LA DE OTRO", 810, 1440, 64, C["otro"], C["blanco"], pp(t, a + 0.15))
    if t >= T_DOS - 0.1:                                    # en los dos: "¡AHÍ VIENE!" con ✓
        for i, cx in enumerate((270, 810)):
            e = t - T_DOS + 0.1 - i * 0.12
            if e > 0:
                u = pop(e)
                A.globo(L, cx - 235 * u, 215, cx + 235 * u, 345, (cx - 40, 395), C["blanco"]) if u > 0.3 else None
                txt(L, "¡AHÍ VIENE!", cx, 280, 58 * u, TINTA)
                visto(L, cx + 215, 210, 42, pop(e - 0.1))
    if t >= T_SABES - 0.05:
        txt(L, "¿?", 540, 1640, 220 * pp(t, T_SABES - 0.05), C["rojo"], borde=12, color_borde=TINTA)


def cabeza_nervio(L, t, cb=(540, 430), hand=(680, 1400), mueve=0.0, cara="normal"):
    fondo_cabeza(L, t)
    path = [(cb[0], cb[1] + 200), (430, 760), (500, 1050), (hand[0] - 60, hand[1] - 90)]
    K.linea(L, path, (255, 214, 60, 110), 22)
    A.cerebro(L, cb[0], cb[1], 230, t, cara)
    K.miembro(L, [(1200, hand[1] + 220), (hand[0] + 80, hand[1] + 40)], C["polera"], 90)
    A.manga(L, (hand[0] + 70, hand[1] + 30), math.radians(220), 1.3, C["polera2"])
    A.mano_cosq(L, hand[0], hand[1], math.radians(220), 1.3, t, mueve)
    return path


@dib
def p4(L, t, a, b):
    # "Para mover la mano, tu cerebro manda una orden."
    mueve = clamp((t - T_ORDEN - 0.35) / 0.15)
    path = cabeza_nervio(L, t, mueve=mueve, cara="normal")
    K.pildora(L, "TU MANO", 330, 1430, 64, C["polera"], C["blanco"], pp(t, a + 0.05))
    if t >= T_ORDEN - 0.15:                                  # la ORDEN baja por el nervio
        u = suave((t - T_ORDEN + 0.15) / 0.5)
        seg = u * 3
        i = min(2, int(seg))
        p = lp(path[i], path[i + 1], seg - i)
        if u < 1:
            A.hoja(L, p[0], p[1], 0.6, "ORDEN", "MOVER MANO", 1.0)
        K.pildora(L, "ORDEN", 540, 160, 90, C["amarillo"], TINTA, pp(t, T_ORDEN - 0.1))
    else:
        K.pildora(L, "TU CEREBRO", 540, 160, 80, C["seso"], TINTA, pp(t, T_CEREBRO - 0.1) if t >= T_CEREBRO - 0.1 else 0)


@dib
def p5(L, t, a, b):
    # "Y se guarda una copia."
    cabeza_nervio(L, t, mueve=1.0, cara="feliz" if t >= T_COPIA else "normal")
    e = t - a
    A.hoja(L, 850, 330, 0.8, "ORDEN", "MOVER MANO", pop(e - 0.05), sello=clamp((t - T_COPIA + 0.05) / 0.15) if t >= T_COPIA - 0.05 else 0)
    K.flecha(L, 730, 410, 790, 370, C["amarillo"], 14, sale((e - 0.1) / 0.3))
    if t >= T_COPIA - 0.05:
        K.pildora(L, "SE GUARDA UNA COPIA", 540, 900 - 140, 64, C["rojo"], C["blanco"], pp(t, T_COPIA))


@dib
def p6(L, t, a, b):
    # "Con ella calcula cuándo y dónde te vas a tocar."
    fondo_cabeza(L, t)
    A.cerebro(L, 400, 430, 220, t, "confiado" if t > T_CUANDO - 0.2 else "normal", brillo=clamp((t - a - 0.2) / 0.3))
    A.hoja(L, 850, 400, 0.7, "ORDEN", "MOVER MANO", 1.0, sello=1.0)
    K.pildora(L, "CALCULA", 540, 150, 88, C["amarillo"], TINTA, pp(t, a + 0.1))
    for i, (que, tt, lab) in enumerate((("cuando", T_CUANDO, "CUÁNDO"), ("donde", T_DONDE, "DÓNDE"))):
        if t >= tt - 0.08:
            e = t - tt + 0.08
            x = 300 + i * 480
            A.icono(L, que, x, 780, 110 * pop(e))
            visto(L, x + 110, 680, 44, pop(e - 0.15))
    if t >= T_TOCAR - 0.1:                                   # dónde te vas a tocar: la axila marcada
        e = t - T_TOCAR + 0.1
        K.pildora(L, "AHORA, EN LA AXILA", 540, 1420, 64, C["blanco"], TINTA, pop(e))


@dib
def p7(L, t, a, b):
    # "Y le baja el volumen a las cosquillas."
    fondo_cabeza(L, t)
    u = 1 - 0.85 * suave((t - T_BAJA) / 0.6) if t >= T_BAJA else 1.0
    A.volumen(L, 540, 560, 1.1, u, t)
    K.pildora(L, "COSQUILLAS", 540, 300, 84, C["coral"], C["blanco"], pp(t, a + 0.05))
    if t >= T_BAJA:
        K.flecha(L, 960, 380, 960, 760, C["amarillo"], 22, sale((t - T_BAJA) / 0.35))
    A.cerebro(L, 280, 880, 130, t, "confiado")
    A.cara_tipo(L, 790, 880, 110, "aburrido" if u < 0.5 else "normal", t)


@dib
def p8(L, t, a, b):
    # "Pero de la mano de otro no hay copia."
    fondo_cabeza(L, t)
    A.cerebro(L, 540, 430, 230, t, "preocupado" if t >= T_NOHAY - 0.2 else "normal")
    K.caja_red(L, 760, 650, 1010, 730, 16, C["robot2"], TINTA, 6)          # bandeja de copias, vacía
    K.texto(L, "COPIAS", 885, 690, 34, C["blanco"])
    if t >= T_NOHAY - 0.1:
        equis(L, 885, 600, 56, pp(t, T_NOHAY - 0.1))
        K.pildora(L, "SIN COPIA", 540, 150, 88, C["rojo"], C["blanco"], pp(t, T_NOHAY))
    u = sale((t - a) / 0.4)
    for i, (x0, y0, ang) in enumerate(((-200, 1180, -0.3), (1280, 1500, math.pi + 0.3))):
        p = lp((x0, y0), (300 if i == 0 else 780, 1050 if i == 0 else 1420), u)
        far = (x0 - 200 if i == 0 else x0 + 200, p[1] + 60)
        K.miembro(L, [far, (p[0] - 60 * math.cos(ang), p[1] - 60 * math.sin(ang))], C["otro"], 84)
        A.manga(L, (p[0] - 70 * math.cos(ang), p[1] - 70 * math.sin(ang)), ang, 1.1, C["otro2"])
        A.mano_cosq(L, p[0], p[1], ang, 1.15, t, 1.0, fase=i * 2)
    K.pildora(L, "LA MANO DE OTRO", 540, 1720 - 300, 64, C["otro"], C["blanco"], pp(t, T_OTRO2 - 0.05))


@dib
def p9(L, t, a, b):
    # "Nadie le baja el volumen."
    rayos(L, t, C["amarillo"], (255, 228, 120), 540, 760)
    u = 0.15 + 0.85 * sale((t - a) / 0.3)
    pts = A.tipo(L, 540, 860, 150, t, "risa" if u > 0.9 else "sorpresa", temblor=1.0 if u > 0.9 else 0)
    for lado, k in ((-1, "hom_i"), (1, "hom_d")):
        m = (540 + lado * 330 + math.sin(t * 40) * 14, 760)
        A.brazo(L, pts[k], m, C["polera"], 56, 0.3, lado)
        K.circulo(L, m[0], m[1], 36, C["piel"], TINTA, 5)
    dx = math.sin(t * 50) * 8 if u > 0.97 else 0
    A.volumen(L, 540 + dx, 330, 1.0, u, t)
    if u > 0.97:
        A.estrella_golpe(L, 940, 170, 100 * pop(t - a - 0.3), C["rojo"], 10)
        txt(L, "MÁX", 940, 170, 50 * pop(t - a - 0.3), C["blanco"], borde=5, color_borde=TINTA)
        A.jaja(L, 540, 820, t, a + 0.3, 300, 5, 70)


def robot_escena(L, t, retraso=0.0, cara=None, risa=False, palanca_u=None):
    A.fondo_puntos(L, C["menta"], C["menta2"], t)
    cx, cy, r = 680, 600, 150
    pts = A.tipo(L, cx, cy, r, t, "risa" if risa else (cara or "normal"), temblor=0.9 if risa else 0, mira=-1)
    palma = (330, 880)                                        # palma derecha abierta hacia arriba, a la izquierda
    A.brazo(L, pts["hom_i"], (palma[0] + 40, palma[1] + 30), C["polera"], 56, 0.18, -1)
    K.elipse(L, palma[0], palma[1], 70, 40, C["piel"], TINTA, 6)
    for i in range(4):
        q0, q1 = (palma[0] - 40 - i * 4, palma[1] - 20 + i * 14), (palma[0] - 100 - i * 4, palma[1] - 30 + i * 16)
        K.linea(L, [q0, q1], TINTA, 28)
        K.linea(L, [q0, q1], C["piel"], 19)
    inc = math.sin(t * 7) if palanca_u is None else palanca_u
    top = A.palanca(L, 975, 905, 0.6, inc)                   # con la izquierda mueve la palanca
    A.brazo(L, pts["hom_d"], (top[0] - 4, top[1] + 10), C["polera"], 56, 0.22, 1)
    K.circulo(L, top[0] - 4, top[1] + 10, 34, C["piel"], TINTA, 5)
    inc_r = math.sin((t - retraso) * 7) if palanca_u is None else palanca_u
    A.robot(L, 190, 360, 0.7, t, "feliz" if risa else "normal", punta=(300 + inc_r * 60, 690), ang_pluma=math.radians(80 + inc_r * 12))
    return pts


@dib
def p10(L, t, a, b):
    # "La prueba: tú mueves un robot que te hace cosquillas."
    robot_escena(L, t, 0.0, "normal", palanca_u=0.0 if t < T_MUEVES else None)
    K.pildora(L, "LA PRUEBA", 540, 150, 88, C["amarillo"], TINTA, pp(t, a + 0.05))
    if t >= T_ROBOT - 0.05:
        A.estrella_golpe(L, 70, 160, 60 * pp(t, T_ROBOT - 0.05), C["amarillo"], 8)
    if t >= T_MUEVES - 0.05:
        K.pildora(L, "TÚ LO MUEVES", 860, 770 - 380, 56, C["polera"], C["blanco"], pp(t, T_MUEVES - 0.05))


@dib
def p11(L, t, a, b):
    # "No pasa nada."
    robot_escena(L, t, 0.0, "aburrido")
    K.pildora(L, "NO PASA NADA", 540, 150, 84, C["blanco"], TINTA, pp(t, a + 0.05))
    txt(L, "cri cri", 900, 330, 44 * pp(t, a + 0.3), C["blanco"], borde=5, color_borde=TINTA)


@dib
def p12(L, t, a, b):
    # "Pero si se atrasa una fracción de segundo, sí te dan."
    atr = t >= T_ATRASA - 0.1
    dan = t >= T_SITE - 0.05
    robot_escena(L, t, 0.45 if atr else 0.0, "tenso" if atr and not dan else "aburrido", risa=dan)
    if atr:
        e = t - T_ATRASA + 0.1
        A.cronometro(L, 940, 250, 85, clamp(e / 1.0) * 0.2)
        K.pildora(L, "+0,2 s", 745, 250, 60, C["coral"], C["blanco"], pop(e - 0.05))
    if dan:
        A.jaja(L, 680, 600, t, T_SITE, 215, 5, 62)
        K.pildora(L, "¡SÍ TE DAN!", 540, 1440, 80, C["verde2"], C["blanco"], pp(t, T_SITE))
    elif atr:
        K.pildora(L, "SE ATRASA", 540, 1440, 72, C["coral"], C["blanco"], pop(t - T_ATRASA + 0.1))


@dib
def p13(L, t, a, b):
    # "Aunque sepas que vienen."
    robot_escena(L, t, 0.45, risa=True)
    u = pp(t, a + 0.02)
    if u > 0.3:
        A.globo(L, 710 - 290 * u, 130, 710 + 290 * u, 300, (760, 360), C["blanco"])
    txt(L, "¡SÉ QUE VIENE!", 710, 215, 56 * u, TINTA)
    visto(L, 985, 140, 40, pp(t, T_SEPAS))


@dib
def p14(L, t, a, b):
    # "No basta con saberlo: tu cerebro tiene que predecirlas."
    rayos(L, t, C["noche2"], C["noche3"], 540, 640)
    pre = t >= T_TU2 - 0.05
    A.cerebro(L, 540, 470, 240, t, "confiado" if pre else "preocupado", brillo=1.0 if t >= T_PREDIC - 0.1 else 0.0)
    if not pre:
        K.pildora(L, "SABERLO NO BASTA", 540, 150, 76, C["blanco"], TINTA, pp(t, a + 0.05))
    else:
        A.bola(L, 540, 860, 140, t)
        K.pildora(L, "PREDECIRLAS", 540, 150, 92, C["amarillo"], TINTA, pp(t, T_PREDIC - 0.1) if t >= T_PREDIC - 0.1 else 0)


@dib
def p15(L, t, a, b):
    # cola: vuelve al cuadro 0 (loop)
    fondo_tipo(L, t)
    auto_cosquillas(L, t, "aburrido", pild=1.0)


FUN = {i: globals()[f"p{i}"] for i in range(1, NP + 1)}
assert len(FUN) == len(T)

# ------------------------------------------------------------------ subtítulos (palabra por palabra, 1–3 palabras)
FONT = K.FONT
AMARILLO = (255, 210, 63)
CLAVE = {"COSQUILLAS": (255, 150, 170), "CEREBRO": (255, 170, 190), "ROBOT": (150, 230, 200), "COPIA": (255, 120, 100)}
BOX = (120, 960, 1000, 1250)


def limpiar(w):
    for ch in ",.:;!¡\"…«»":
        w = w.replace(ch, "")
    return w.upper()


TOK = [limpiar(x["w"]) for x in words]
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
        e_show = min(e + 0.25, words[nxt[0]]["s"]) if nxt else e + 0.3
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
