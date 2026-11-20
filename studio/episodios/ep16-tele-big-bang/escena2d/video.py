"""Ep. 16 — "La tele de antes captaba el Big Bang" (la lluvia de la tele y la luz más antigua del universo). 2D de comedia por código (PIL).
Voz: escena2d/voz.wav + words.json (los deja prep.py). Lo que cambia es el contenido, no la cámara (regla 24).
Uso: python3 video.py <carpeta_salida> [cuadro_desde cuadro_hasta [paso]]      (cuadros 1..FIN, 30 fps, 1080×1920)
"""
import json, math, os, random, sys
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
EPI = os.path.abspath(os.path.join(AQUI, ".."))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.abspath(os.path.join(AQUI, "../../../plantilla")))
import arte as A
import arte16 as B
import kit2d as K
from arte import C, TINTA, clamp, suave, sale, pop, rebote
from arte16 import C16

W, H, FPS, SS = 1080, 1920, 30, 2
words = json.load(open(os.path.join(EPI, "words.json")))
_envp = os.path.join(AQUI, "envolvente.json")
ENV = json.load(open(_envp)) if os.path.exists(_envp) else []
FIN_VOZ = words[-1]["e"]
COLA = 0.9                                   # vuelta al cuadro 0 después de la última palabra (loop)
DUR = FIN_VOZ + COLA
FIN = int(round(DUR * FPS))


def _lim(w):
    return w["w"].lower().strip(".,;:…!?¡¿")


def tw(prefijo, desde=0.0):
    p = prefijo.lower()
    for w in words:
        if w["s"] >= desde - 0.01 and _lim(w).startswith(p):
            return w["s"]
    raise KeyError(prefijo)


def te(prefijo, desde=0.0):
    p = prefijo.lower()
    for w in words:
        if w["s"] >= desde - 0.01 and _lim(w).startswith(p):
            return w["e"]
    raise KeyError(prefijo)


def ts(frase, desde=0.0):
    """Inicio de la primera palabra de una frase (varias palabras seguidas)."""
    ps = [p.lower() for p in frase.split()]
    for i in range(len(words) - len(ps) + 1):
        if words[i]["s"] >= desde - 0.01 and all(_lim(words[i + j]) == ps[j] for j in range(len(ps))):
            return words[i]["s"]
    raise KeyError(frase)


T_BANG = tw("bang")
T_BUENO = tw("bueno")
T_ECO = tw("eco")
T_TE = ts("te acuerdas")
T_LLUVIA = tw("lluvia")
T_SENAL = tw("señal")
T_UNOS = ts("unos científicos")
T_CIEN_ = tw("científicos")
T_GIG = tw("gigante")
T_RUIDO = tw("ruido")
T_SACAR = tw("sacar")
T_CULP = tw("culparon")
T_PALOMAS = tw("palomas")
T_LAS = ts("las sacaron")
T_LIMP = tw("limpiaron")
T_SEGUIA = tw("seguía")
T_DONDE = ts("de dónde")
T_DEL = ts("del principio")
T_UNI1 = ts("el universo recién")
T_SOPA = tw("sopa")
T_LALUZ = ts("la luz no")
T_CHOCA = tw("chocaba")
T_NIEB = tw("neblina")
T_ALENF = ts("al enfriarse")
T_ATOMOS = tw("átomos")
T_DISP = tw("disparada")
T_PERO2 = ts("pero el universo")
T_TANTO = tw("tanto")
T_MICRO = tw("microondas")
T_PRIMAS = tw("primas")
T_ESE = ts("ese era")
T_ANTENA2 = tw("antena", T_ESE)
T_YLOS = ts("y los de")
T_NOBEL = tw("nobel")
T_LLENA = tw("llena")
T_YTU = ts("y tu antena")
T_CAPT2 = tw("captaba", T_YTU)
T_MAS = ts("más o menos")
T_UNO = ts("uno por ciento")
T_ERA = ts("era el universo")
T_LIVING = tw("living")

CORTES = [0.0, T_BUENO - 0.06, T_TE - 0.08, T_UNOS - 0.08, T_CULP - 0.08, T_LAS - 0.06, T_DONDE - 0.08, T_DEL - 0.06, T_UNI1 - 0.06,
          T_LALUZ - 0.06, T_ALENF - 0.06, T_PERO2 - 0.06, T_TANTO - 0.06, T_ESE - 0.06, T_YLOS - 0.06, T_LLENA - 0.06, T_YTU - 0.06,
          T_MAS - 0.06, T_ERA - 0.08, FIN_VOZ + 0.3, DUR]
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


def boca(t):
    if not ENV:
        return 0.0
    i = int(t * 60)
    return ENV[i] if 0 <= i < len(ENV) else 0.0


AMA = C["amarillo"]


# ------------------------------------------------------------------ piezas que se repiten
def pantalla_bang(t, r=120, cara="feliz", eco=0.0, chupe=False):
    def f(L, x0, y0, x1, y1):
        B._lluvia(L, x0 + 4, y0 + 4, x1 - 4, y1 - 4, t, radio=56 * (x1 - x0) / 620, grano=7, oscuro=0.75)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if eco > 0:                                                                       # el eco: anillos que se van
            for i in range(4):
                f_ = (t * 0.9 + i / 4) % 1.0
                rr = r * (1.1 + 2.2 * f_)
                L.d.ellipse((L.S(cx - rr), L.S(cy - rr), L.S(cx + rr), L.S(cy + rr)), outline=(255, 220, 130, int(200 * (1 - f_) * eco)), width=int(L.S(8)))
        B.bang(L, cx, cy, r, t, cara, chispas_n=8)
        if chupe:
            B.chupete(L, cx, cy, r)
    return f


def golpe_tele(L, t, t_golpe, pild=True):
    """La mano del viejo le pega a la tele y adentro el Big Bang dice ay (cuadro 0 y cola)."""
    B.living(L, t)
    e = t - t_golpe
    gol = e >= 0
    B.tele(L, 600, 650, 780, t, carpeta=True, temblor=1.0 if gol and e < 0.6 else 0.15,
           pantalla=pantalla_bang(t, 118, "ay" if gol else "feliz"))
    if gol:
        A.estrella_golpe(L, 360, 380, 105 * (pop(e) if e < 0.28 else 1.0), None, 10, "PAF", 58)
        B.palma(L, 270, 380, 1.05, -0.35, manga=(200, 186, 160))
    else:
        u = clamp(1 + e / 0.25)
        B.palma(L, 120 + 150 * u, 200 + 180 * u, 1.05, -0.35, manga=(200, 186, 160))
    if pild:
        K.pildora(L, "LE PEGABAS AL BIG BANG", 540, 110, 64, AMA, TINTA, 1.0)
        K.pildora(L, "BUENO, A SU ECO", 540, 205, 50, C["blanco"], TINTA, 1.0)


def noche_antena(L, t, s_=0.95, x=700, y=600):
    B.noche(L, t)
    B.cuerno(L, x, y, s_, t)


# ------------------------------------------------------------------ planos
@dib
def p1(L, t, a, b):
    # "Pegarle a la tele era pegarle al Big Bang."  (el golpe ya está pasando en el cuadro 0)
    golpe_tele(L, t, -0.3)


@dib
def p2(L, t, a, b):
    # "Bueno, a su eco."
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=C16["madera"])
    K.caja_red(L, 40, 120, 1040, 980, 70, C16["bisel"], TINTA, 9)
    u = sale((t - a) / 0.5)
    pantalla_bang(t, 160 - 70 * u, "sorpresa", eco=pp(t, T_ECO - 0.1))(L, 80, 160, 1000, 940)
    if t >= T_ECO - 0.1:
        K.pildora(L, "SU ECO", 540, 860, 70, AMA, TINTA, pp(t, T_ECO - 0.1))


@dib
def p3(L, t, a, b):
    # "¿Te acuerdas de la lluvia de puntitos cuando no había señal?"
    B.living(L, t)
    B.tele(L, 700, 560, 640, t, "aburrido" if t < T_LLUVIA else "normal", carpeta=True, mira=(-0.6, 0))
    B.sillon_atras(L, 250, 1160, 0.95)
    K.viejo(L, 250, 1110, 560, 0.0, t, "tazon", 1)
    B.sillon_frente(L, 250, 1190, 0.95)
    if t >= T_SENAL - 0.15:
        u = pp(t, T_SENAL - 0.15)
        K.flecha(L, 700, 175, 700, 300, AMA, 20, u)
        K.pildora(L, "SIN SEÑAL", 700, 120, 66, C["blanco"], TINTA, u)


@dib
def p4(L, t, a, b):
    # "Unos científicos tenían una antena gigante con un ruido imposible de sacar."
    gig = t >= T_GIG - 0.1
    s_ = 0.62 + 0.33 * sale((t - T_GIG + 0.1) / 0.35) if gig else 0.62
    noche_antena(L, t, s_)
    ruido = t >= T_RUIDO - 0.1
    for i, (x_, m_, pelo_) in enumerate(((250, 1, "corto"), (900, -1, "pelado"))):
        u_ = sale((t - T_CIEN_ + 0.1 - 0.12 * i) / 0.35) if t >= T_CIEN_ - 0.1 + 0.12 * i else 0.0
        if u_ > 0:
            B.cientifico(L, x_ - m_ * 300 * (1 - u_), 960, 330, t, "molesto" if ruido else ("sorpresa" if gig else "normal"), m_,
                         "oreja" if ruido else ("arriba" if gig and i == 0 else None), pelo=pelo_, audifonos=(i == 0))
    if ruido:
        B.ruido_txt(L, 560, 330, t, 1.0)
    if t >= T_SACAR - 0.15:
        r = 70 * pp(t, T_SACAR - 0.15)
        for sg in (-1, 1):
            K.linea(L, [(780 - r, 380 - sg * r), (780 + r, 380 + sg * r)], TINTA, 34 * r / 70 + 1)
            K.linea(L, [(780 - r, 380 - sg * r), (780 + r, 380 + sg * r)], C["rojo"], 22 * r / 70 + 1)
    K.pildora(L, "1964", 540, 130, 70, C["blanco"], TINTA, pp(t, a + 0.15))


def adentro_antena(L, t):
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=(20, 22, 30))
    for k in range(7):
        u = k / 7
        K.poligono(L, [(0, 0), (W, 0), (W - 160 - 40 * u, 140 + 40 * u), (160 + 40 * u, 140 + 40 * u)], (60 + 18 * k, 66 + 18 * k, 78 + 18 * k))
    K.poligono(L, [(0, 0), (190, 180), (190, 980), (0, 1150)], C16["metal2"], TINTA, 6)
    K.poligono(L, [(W, 0), (W - 190, 180), (W - 190, 980), (W, 1150)], C16["metal3"], TINTA, 6)
    K.poligono(L, [(0, 1150), (190, 980), (W - 190, 980), (W, 1150)], C16["metal3"], TINTA, 6)
    L.d.rectangle((0, L.S(1150), L.S(W), L.S(H)), fill=C16["metal3"])
    for (x0, y0, x1, y1) in ((0, 0, W, 46), (0, 0, 46, 1150), (W - 46, 0, W, 1150)):
        L.d.rectangle((L.S(x0), L.S(y0), L.S(x1), L.S(y1)), fill=C16["metal"], outline=TINTA, width=int(L.S(6)))
    for k in range(9):
        K.circulo(L, 23, 60 + k * 125, 9, C16["metal3"], TINTA, 3)
        K.circulo(L, W - 23, 60 + k * 125, 9, C16["metal3"], TINTA, 3)


@dib
def p5(L, t, a, b):
    # "Culparon a unas palomas que anidaban adentro."
    adentro_antena(L, t)
    K.pildora(L, "DENTRO DE LA ANTENA", 540, 120, 50, C["blanco"], TINTA, pp(t, a + 0.05) if t < T_PALOMAS - 0.15 else 0)
    pal = t >= T_PALOMAS - 0.15
    B.nido(L, 660, 880, 1.25)
    B.paloma(L, 580, 870, 1.5, t, -1 if not pal else 1, "inocente" if pal else "normal")
    B.paloma(L, 770, 870, 1.5, t + 0.7, -1, "inocente" if pal else "normal")
    B.cientifico(L, 230, 1240, 660, t, "molesto", 1, "apunta" if pal else None)
    for i, (x_, y_) in enumerate(((480, 930), (860, 940))):
        B.caca(L, x_, y_, 24, pp(t, a + 0.3 + 0.2 * i))
    if pal:
        K.pildora(L, "¿LAS PALOMAS?", 660, 560, 66, C["blanco"], TINTA, pp(t, T_PALOMAS - 0.15))


@dib
def p6(L, t, a, b):
    # "Las sacaron, limpiaron la caca, y el ruido seguía."
    noche_antena(L, t, 0.7, 820, 520)
    e = t - a
    for i, (x0, y0) in enumerate(((560, 640), (720, 650))):
        u = sale(e / 1.0)
        B.paloma(L, x0 + 500 * u * (1 if i else 0.8), y0 - 640 * u, 1.1, t + i, 1, vuela=1.0)
    sig = t >= T_SEGUIA - 0.12
    limp = clamp((t - T_LIMP) / max(0.3, T_SEGUIA - T_LIMP - 0.25)) if t >= T_LIMP else 0.0
    for i, (cx_, cy_) in enumerate(((430, 920), (560, 940), (680, 915))):
        B.caca(L, cx_, cy_, 30, 1.0 - clamp(limp * 3 - i))
    B.cientifico(L, 300, 960, 420, t, "molesto" if sig else "normal", 1, "oreja" if sig else ("escoba" if t >= T_LIMP - 0.2 else None))
    if sig:
        A.sello(L, 640, 250, "SIGUE", 1.0, -0.12, sale((t - T_SEGUIA + 0.12) / 0.18))
        if t >= T_SEGUIA + 0.25:
            B.ruido_txt(L, 520, 440, t, 1.1)


@dib
def p7(L, t, a, b):
    # "¿De dónde venía?"
    noche_antena(L, t, 0.7, 820, 520)
    B.cientifico(L, 300, 960, 420, t, "sorpresa", 1, "oreja")
    B.cientifico(L, 860, 960, 420, t, "sorpresa", -1, None, pelo="pelado")
    for i, (x_, y_) in enumerate(((300, 330), (860, 330), (580, 230))):
        u = pp(t, a + 0.1 + 0.15 * i)
        txt(L, "?", x_, y_ + math.sin(t * 6 + i) * 10, 120 * u, AMA, borde=8, color_borde=TINTA)


@dib
def p8(L, t, a, b):
    # "Del principio de todo."  (rebobinar hasta el Big Bang)
    B.cosmos(L, t, galaxias=False)
    u = sale((t - a) / max(0.4, b - a - 0.2))
    for i in range(6):                                                                    # las galaxias se juntan hacia el centro
        an = i * math.pi / 3 + 0.3
        d = 520 * (1 - u) + 40
        K.elipse(L, 540 + math.cos(an) * d, 600 + math.sin(an) * d, 60 * (1 - u) + 6, 22 * (1 - u) + 3, (190, 160, 255, 160))
    B.bang(L, 540, 600, 30 + 140 * u, t, "feliz", chispas_n=10)
    n = int(round(13800 * u / 100.0)) * 100
    K.pildora(L, "HACE " + f"{n:,}".replace(",", ".") + " MILLONES DE AÑOS", 540, 140, 52, C["blanco"], TINTA, pp(t, a + 0.05))


@dib
def p9(L, t, a, b):
    # "El universo recién nacido era una sopa ardiente y espesa."
    B.sopa(L, t, niebla=0.5)
    B.particulas(L, t, 14, 1.0)
    B.termometro(L, 980, 760, 420, 1.0)
    if t >= T_SOPA - 0.1:
        K.pildora(L, "SOPA ARDIENTE", 540, 130, 70, AMA, TINTA, pp(t, T_SOPA - 0.1))


@dib
def p10(L, t, a, b):
    # "La luz no avanzaba: chocaba con todo, como en una neblina."
    B.sopa(L, t, niebla=0.25 + 0.75 * sale((t - T_NIEB + 0.3) / 0.5) if t >= T_NIEB - 0.3 else 0.25)
    B.particulas(L, t, 14, 1.0)
    # la luz rebota de partícula en partícula (zigzag)
    pts = [(170, 300), (430, 820), (700, 260), (900, 760), (540, 520), (240, 880), (820, 400)]
    e = (t - a) * 2.6
    i = int(e) % (len(pts) - 1)
    f = e - int(e)
    x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f
    y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f
    if f < 0.18 and t >= T_CHOCA - 0.2:
        A.estrella_golpe(L, pts[i][0], pts[i][1], 60, C["blanco"], 8, "TOC", 34)
    B.foton(L, x, y, 64, t, "mareado" if t >= T_NIEB else "sorpresa")
    K.pildora(L, "LA LUZ", x, y - 120, 50, AMA, TINTA, pp(t, a + 0.05) if t < T_CHOCA else 0)


@dib
def p11(L, t, a, b):
    # "Al enfriarse, se armaron los primeros átomos, y la luz salió disparada."
    enf = sale((t - a) / 0.8)
    atom = sale((t - T_ATOMOS + 0.5) / 0.6) if t >= T_ATOMOS - 0.5 else 0.0
    disp = t >= T_DISP - 0.1
    B.sopa(L, t, niebla=0.8 * (1 - atom), enfria=enf)
    B.particulas(L, t, 12, 1.0 - 0.7 * enf, atomos=atom)
    B.termometro(L, 980, 760, 420, 1.0 - 0.75 * enf)
    if disp:
        u = sale((t - T_DISP + 0.1) / 0.6)
        B.foton(L, 300 + 900 * u, 560 - 120 * u, 66, t, "feliz", estela=-0.13)
    else:
        B.foton(L, 300 + math.sin(t * 20) * 8, 560, 60, t, "sorpresa")
    if t >= T_ATOMOS - 0.4:
        K.pildora(L, "LOS PRIMEROS ÁTOMOS", 540, 130, 62, C["blanco"], TINTA, pp(t, T_ATOMOS - 0.4))
        K.pildora(L, "380.000 AÑOS DESPUÉS", 540, 232, 48, AMA, TINTA, pp(t, T_ATOMOS - 0.2))


@dib
def p12(L, t, a, b):
    # "Pero el universo se estiró, y esa luz se estiró con él."
    B.cosmos(L, t, galaxias=False)
    est = sale((t - a) / max(0.6, b - a - 0.2))
    B.grilla_espacio(L, est)
    def mez(c1, c2, u):
        return tuple(int(c1[i] + (c2[i] - c1[i]) * u) for i in range(3))
    col = mez(C16["luz"], (230, 80, 70), clamp(est * 1.4)) if est < 0.7 else mez((230, 80, 70), (150, 190, 255), (est - 0.7) / 0.3)
    B.onda_estirada(L, 50, 920, 560, t, 50 + 240 * est, 70, col, 20)
    K.pildora(L, "EL UNIVERSO SE ESTIRA", 540, 140, 58, C["blanco"], TINTA, pp(t, a + 0.1))
    for sg in (-1, 1):                                                                    # flechas: el espacio se estira
        K.flecha(L, 540 + sg * 160, 900, 540 + sg * 420, 900, C["blanco"], 18, pp(t, a + 0.1))


@dib
def p13(L, t, a, b):
    # "Tanto, que hoy son microondas: primas de las ondas de la tele."
    B.cosmos(L, t, galaxias=False)
    B.onda_estirada(L, 40, 820, 440, t, 300, 60, (150, 190, 255), 18)
    if t >= T_MICRO - 0.15:
        K.pildora(L, "MICROONDAS", 400, 280, 58, (150, 190, 255), TINTA, pp(t, T_MICRO - 0.15))
        K.pildora(L, "-270 °C", 840, 280, 46, C["blanco"], TINTA, pp(t, T_MICRO + 0.1))
    if t >= T_PRIMAS - 0.2:
        u = pp(t, T_PRIMAS - 0.2)
        B.onda_estirada(L, 40, 780, 760, t + 0.3, 200, 60, (140, 220, 140), 18)
        K.pildora(L, "ONDAS DE LA TELE", 400, 900, 54, (140, 220, 140), TINTA, u)
        B.tele(L, 950, 760, 180 * u + 1, t, "feliz")
        K.pildora(L, "PRIMAS", 540, 600, 66, AMA, TINTA, pp(t, T_PRIMAS))


@dib
def p14(L, t, a, b):
    # "Ese era el ruido de la antena."
    noche_antena(L, t, 0.8, 760, 560)
    u = sale((t - a) / 0.8)
    B.onda(L, 1080, 120, 1080 - 380 * u - 1, 120 + 300 * u + 1, t, 1.0, 22, 120, (150, 190, 255), 12, cabeza=True)
    aha = t >= T_ANTENA2 - 0.2
    B.cientifico(L, 260, 960, 420, t, "feliz" if aha else "sorpresa", 1, "arriba" if aha else "oreja")
    if aha:
        B.bombilla(L, 260, 330, 0.9, pp(t, T_ANTENA2 - 0.2))


@dib
def p15(L, t, a, b):
    # "Y los de las palomas se ganaron el Nobel."
    A.fondo_puntos(L, C["crema"], C["crema2"], t)
    e = t - T_NOBEL + 0.1
    B.cientifico(L, 330, 1000, 560, t, "feliz", 1, "arriba" if e > 0.3 else None, medalla=sale(e / 0.4) if e > 0 else 0.0)
    B.cientifico(L, 760, 1000, 560, t, "feliz", -1, None, pelo="pelado", medalla=sale((e - 0.15) / 0.4) if e > 0.15 else 0.0)
    u = pp(t, a + 0.1)                                                                   # las palomas, en la cabeza
    B.paloma(L, 330, 380 - (1 - u) * 300, 0.9, t, 1, "inocente")
    B.paloma(L, 760, 380 - (1 - u) * 300, 0.9, t + 0.4, -1)
    K.pildora(L, "NOBEL 1978", 540, 150, 76, AMA, TINTA, pp(t, T_NOBEL - 0.1))
    B.confeti(L, t, T_NOBEL - 0.05, 40)


@dib
def p16(L, t, a, b):
    # "Llena todo el universo: por eso llega de todas partes."
    B.cosmos(L, t)
    B.tierra(L, 540, 560, 170, t)
    u = sale((t - a) / 0.9)
    for k in range(8):
        an = k * math.pi / 4 + 0.2
        B.onda(L, 540 + math.cos(an) * 620, 560 + math.sin(an) * 340, 540 + math.cos(an) * 230, 560 + math.sin(an) * 230, t, u, 20, 60, (150, 190, 255), 11)


@dib
def p17(L, t, a, b):
    # "Y tu antena de conejo también la captaba."
    B.living(L, t)
    capt = t >= T_CAPT2 - 0.1
    B.tele(L, 540, 640, 760, t, "orgullo" if capt else "normal", carpeta=True, salto=0.5 if capt else 0.0)
    u = sale((t - a) / 0.8)
    for k, (x0, y0) in enumerate(((60, -40), (540, -120), (1020, -40))):
        B.onda(L, x0, y0, 400 + k * 140, 220, t, u, 16, 50, (150, 190, 255), 9)
    if capt:
        B.chispas(L, 540, 600, 450, t, 7, semilla=4)


def pantalla_grilla(t, u):
    def f(L, x0, y0, x1, y1):
        L.d.rounded_rectangle((L.S(x0), L.S(y0), L.S(x1), L.S(y1)), L.S(50), fill=(28, 28, 32))
        m = 46
        B.grilla100(L, x0 + m, y0 + m * 0.7, x1 - m, y1 - m * 0.7, t, u, especial=(6, 4))
    return f


@dib
def p18(L, t, a, b):
    # "Más o menos el uno por ciento de esa lluvia."
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=C16["madera"])
    K.caja_red(L, 30, 220, 1050, 1000, 70, C16["bisel"], TINTA, 9)
    u = clamp((t - a) / 0.7)
    pantalla_grilla(t, u)(L, 70, 260, 1010, 960)
    if t >= T_UNO - 0.15:
        K.pildora(L, "MÁS O MENOS 1 %", 540, 120, 76, AMA, TINTA, pp(t, T_UNO - 0.15))


@dib
def p19(L, t, a, b):
    # "Era el universo recién nacido, en el living de tu casa."
    B.living(L, t)
    B.tele(L, 700, 560, 640, t, carpeta=True, pantalla=pantalla_bang(t, 100, "feliz", chupe=True))
    B.sillon_atras(L, 250, 1160, 0.95)
    K.viejo(L, 250, 1110, 560, 0.0, t, "tazon", 1)
    B.sillon_frente(L, 250, 1190, 0.95)
    if t >= T_LIVING - 0.2:
        u = pp(t, T_LIVING - 0.2)
        for i, (x_, y_) in enumerate(((430, 420), (470, 330), (520, 250))):              # corazones del viejo
            hh = 26 * u * (1 + 0.15 * math.sin(t * 6 + i))
            K.circulo(L, x_ - hh * 0.5, y_, hh * 0.62, C["coral"], TINTA, 3)
            K.circulo(L, x_ + hh * 0.5, y_, hh * 0.62, C["coral"], TINTA, 3)
            K.poligono(L, [(x_ - hh * 1.08, y_ + hh * 0.15), (x_ + hh * 1.08, y_ + hh * 0.15), (x_, y_ + hh * 1.3)], C["coral"])
    K.pildora(L, "EL UNIVERSO RECIÉN NACIDO", 540, 1290 - 1190, 50, C["blanco"], TINTA, pp(t, a + 0.1))


@dib
def p20(L, t, a, b):
    # cola: vuelve al cuadro 0 (loop)
    golpe_tele(L, t, b + 0.05)


FUN = {i: globals()[f"p{i}"] for i in range(1, NP + 1)}
assert len(FUN) == len(T)

# ------------------------------------------------------------------ subtítulos (palabra por palabra, 1–3 palabras)
FONT = K.FONT
AMARILLO = (255, 210, 63)
CLAVE = {"BIG": (255, 170, 80), "BANG": (255, 170, 80), "ECO": (255, 170, 80), "CIENTO": (255, 170, 80), "MICROONDAS": (150, 190, 255)}
BOX = (120, 960, 888, 1250)


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
    for size in range(80, 59, -4):
        f = ImageFont.truetype(FONT, size)
        if ancho_toks(f, toks) <= maxw:
            break
    d = ImageDraw.Draw(im, "RGBA")
    y = (BOX[1] + BOX[3]) / 2 - f.size * 0.56
    x = (BOX[0] + BOX[2]) / 2 - ancho_toks(f, toks) / 2
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
