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


T_ECO = tw("eco")
T_BANG = tw("bang")
T_TE = ts("te acuerdas")
T_LLUVIA = tw("lluvia")
T_SENAL = tw("señal")
T_AHI = tw("ahí")
T_ESC = tw("escondido")
T_UNOS = ts("unos científicos")
T_COMO = ts("como la de")
T_GIG = tw("gigante")
T_CAPTABA = ts("captaba un ruido")
T_RUIDO = tw("ruido", T_CAPTABA)
T_NADA = tw("nada")
T_CULP = tw("culparon")
T_PALOMAS = tw("palomas")
T_LAS = ts("las sacaron")
T_LIMP = tw("limpiaron")
T_CACA = tw("caca")
T_PERO = ts("pero el ruido")
T_SEGUIA = tw("seguía")
T_ESE = ts("ese ruido")
T_LUZ = tw("luz", T_ESE)
T_ANTIGUA = tw("antigua")
T_YLLEGA = ts("y llega")
T_CIELO = tw("cielo")
T_POR = ts("por eso")
T_CAPT2 = tw("captaba", T_POR)
T_ERA = ts("era más")
T_UNO = ts("uno por ciento")
T_CUANDO = ts("cuando le pegabas")
T_PEGABAS = tw("pegabas")
T_LE2 = ts("le pegabas al")
T_BANG2 = tw("bang", T_LE2)

CORTES = [0.0, T_TE - 0.08, T_AHI - 0.06, T_UNOS - 0.08, T_CAPTABA - 0.06, T_CULP - 0.08, T_LAS - 0.06, T_PERO - 0.06, T_ESE - 0.08,
          T_YLLEGA - 0.06, T_POR - 0.06, T_ERA - 0.06, T_CUANDO - 0.08, T_LE2 - 0.06, FIN_VOZ + 0.3, DUR]
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


# ------------------------------------------------------------------ cuadro 0: la tele con el Big Bang adentro
def pantalla_bang(t, r=120, cara="feliz"):
    def f(L, x0, y0, x1, y1):
        B._lluvia(L, x0 + 4, y0 + 4, x1 - 4, y1 - 4, t, radio=56 * (x1 - x0) / 620, grano=7, oscuro=0.75)
        B.bang(L, (x0 + x1) / 2, (y0 + y1) / 2, r, t, cara)
    return f


def portada(L, t, r=120, pild=1.0):
    B.living(L, t)
    B.tele(L, 540, 650, 820, t, carpeta=True, pantalla=pantalla_bang(t, r))
    if pild > 0:
        K.pildora(L, "EL ECO DEL BIG BANG", 540, 110, 68, AMA, TINTA, pild)
        K.pildora(L, "EN TU TELE", 540, 212, 54, C["blanco"], TINTA, pild)


@dib
def p1(L, t, a, b):
    # "La tele de antes captaba el eco del Big Bang."
    portada(L, t, 110 + 22 * pp(t, T_BANG - 0.05))


@dib
def p2(L, t, a, b):
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
def p3(L, t, a, b):
    # "Ahí venía escondido." → la lluvia de cerca y un puntito que brilla
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=C16["madera"])
    K.caja_red(L, 40, 120, 1040, 980, 70, C16["bisel"], TINTA, 9)
    B._lluvia(L, 80, 160, 1000, 940, t, radio=60, grano=13, oscuro=0.85)
    if t >= a + 0.2:
        r = 10 + 66 * suave((t - a - 0.2) / 0.6)
        B.bang(L, 640, 520, r, t, "sorpresa" if t >= T_ESC else "feliz", chispas_n=6)
        B.chispas(L, 640, 520, r * 2.2, t, 5)


@dib
def p4(L, t, a, b):
    # "Unos científicos tenían una antena como la de la tele, pero gigante."
    B.noche(L, t)
    gig = t >= T_GIG - 0.1
    s_ = 0.62 + 0.33 * sale((t - T_GIG + 0.1) / 0.35) if gig else 0.62
    B.cuerno(L, 700, 600, s_, t)
    T_CIEN_ = tw("científicos")
    for i, (x_, m_, pelo_) in enumerate(((250, 1, "corto"), (900, -1, "pelado"))):            # entran al decir "científicos"
        u_ = sale((t - T_CIEN_ + 0.1 - 0.12 * i) / 0.35) if t >= T_CIEN_ - 0.1 + 0.12 * i else 0.0
        if u_ > 0:
            B.cientifico(L, x_ - m_ * 300 * (1 - u_), 960, 330, t, "sorpresa" if gig and i == 0 else "normal", m_,
                         "arriba" if gig and i == 0 else None, pelo=pelo_)
    if t >= T_COMO - 0.1:                                                                  # la tele chica, para comparar
        u = pp(t, T_COMO - 0.1)
        B.tele(L, 180, 300, 220 * u + 1, t, "sorpresa" if gig else "normal", ojos=True)
    K.pildora(L, "1964", 540, 130, 70, C["blanco"], TINTA, pp(t, a + 0.15))


@dib
def p5(L, t, a, b):
    # "Captaba un ruido que no se quitaba con nada."
    B.noche(L, t)
    B.cuerno(L, 860, 470, 0.6, t)
    nada = t >= T_NADA - 0.15
    B.cientifico(L, 430, 1000, 620, t, "molesto" if t >= T_RUIDO else "normal", 1, "oreja" if t >= T_RUIDO else None, audifonos=True)
    if t >= T_RUIDO - 0.1:
        B.ruido_txt(L, 620, 300, t, 1.1)
    if nada:                                                                               # una X roja sobre el ruido: no se quita
        r = 70 * pp(t, T_NADA - 0.15)
        for sg in (-1, 1):
            K.linea(L, [(780 - r, 640 - sg * r), (780 + r, 640 + sg * r)], TINTA, 34 * r / 70 + 1)
            K.linea(L, [(780 - r, 640 - sg * r), (780 + r, 640 + sg * r)], C["rojo"], 22 * r / 70 + 1)


@dib
def p6(L, t, a, b):
    # "Culparon a unas palomas que anidaban adentro."
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=(20, 22, 30))
    for k in range(7):
        u = k / 7
        K.poligono(L, [(0, 0), (W, 0), (W - 160 - 40 * u, 140 + 40 * u), (160 + 40 * u, 140 + 40 * u)], (60 + 18 * k, 66 + 18 * k, 78 + 18 * k))
    K.poligono(L, [(0, 0), (190, 180), (190, 980), (0, 1150)], C16["metal2"], TINTA, 6)
    K.poligono(L, [(W, 0), (W - 190, 180), (W - 190, 980), (W, 1150)], C16["metal3"], TINTA, 6)
    K.poligono(L, [(0, 1150), (190, 980), (W - 190, 980), (W, 1150)], C16["metal3"], TINTA, 6)
    L.d.rectangle((0, L.S(1150), L.S(W), L.S(H)), fill=C16["metal3"])
    for (x0, y0, x1, y1) in ((0, 0, W, 46), (0, 0, 46, 1150), (W - 46, 0, W, 1150)):         # el borde de la boca de la antena
        L.d.rectangle((L.S(x0), L.S(y0), L.S(x1), L.S(y1)), fill=C16["metal"], outline=TINTA, width=int(L.S(6)))
    for k in range(9):
        K.circulo(L, 23, 60 + k * 125, 9, C16["metal3"], TINTA, 3)
        K.circulo(L, W - 23, 60 + k * 125, 9, C16["metal3"], TINTA, 3)
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
def p7(L, t, a, b):
    # "Las sacaron y limpiaron la caca."
    B.noche(L, t)
    B.cuerno(L, 820, 520, 0.7, t)
    e = t - a
    for i, (x0, y0) in enumerate(((560, 640), (720, 650))):                               # se van volando
        u = sale(e / 1.0)
        B.paloma(L, x0 + 500 * u * (1 if i else 0.8), y0 - 640 * u, 1.1, t + i, 1, vuela=1.0)
    limp = clamp((t - T_LIMP) / max(0.3, b - T_LIMP - 0.15)) if t >= T_LIMP else 0.0
    for i, (cx_, cy_) in enumerate(((430, 920), (560, 940), (680, 915))):
        B.caca(L, cx_, cy_, 30, 1.0 - clamp(limp * 3 - i))
    B.cientifico(L, 300, 960, 420, t, "normal", 1, "escoba" if t >= T_LIMP - 0.2 else None)


@dib
def p8(L, t, a, b):
    # "Pero el ruido seguía."
    B.noche(L, t)
    B.cuerno(L, 820, 520, 0.7, t)
    B.cientifico(L, 300, 960, 420, t, "molesto", 1, "oreja")
    if not (T_SEGUIA - 0.12 <= t < T_SEGUIA + 0.25):                                       # no se encima con el timbre grande
        B.ruido_txt(L, 520, 440, t, 1.1)
    if t >= T_SEGUIA - 0.12:
        A.sello(L, 640, 250, "SIGUE", 1.0, -0.12, sale((t - T_SEGUIA + 0.12) / 0.18))


def contador(L, t, y=262):
    t0 = T_ESE + 0.15
    if t < t0:
        return
    u = clamp((t - t0) / 0.6)
    n = int(round(13800 * sale(u) / 100.0)) * 100
    s_ = f"{n:,}".replace(",", ".") + " MILLONES DE AÑOS"
    K.pildora(L, ("CASI " if u >= 1 else "") + s_, 540, y, 54, C["blanco"], TINTA, pp(t, t0))


@dib
def p9(L, t, a, b):
    # "Ese ruido era la luz más antigua del universo."
    B.cosmos(L, t, galaxias=False)
    e = t - a
    for i in range(4):
        f = (e * 0.7 + i / 4) % 1.0
        r = 180 + 520 * f
        al = int(170 * (1 - f))
        L.d.ellipse((L.S(540 - r), L.S(600 - r), L.S(540 + r), L.S(600 + r)), outline=(255, 220, 130, al), width=int(L.S(14)))
    B.bang(L, 540, 600, 160 * pp(t, a + 0.02), t, "feliz", chispas_n=14)
    contador(L, t, 262)
    K.pildora(L, "LA LUZ MÁS ANTIGUA", 540, 140, 68, AMA, TINTA, pp(t, T_LUZ - 0.1))


@dib
def p10(L, t, a, b):
    # "Y llega de todo el cielo."
    B.cosmos(L, t)
    B.tierra(L, 540, 560, 170, t)
    u = sale((t - a) / 0.9)
    for k in range(8):
        an = k * math.pi / 4 + 0.2
        B.onda(L, 540 + math.cos(an) * 620, 560 + math.sin(an) * 340, 540 + math.cos(an) * 230, 560 + math.sin(an) * 230, t, u, 20, 60, None, 11)
    if t < T_YLLEGA + 0.9:                                                                 # la cifra se queda para leerla
        contador(L, t, 150)


@dib
def p11(L, t, a, b):
    # "Por eso tu tele también la captaba."
    B.living(L, t)
    capt = t >= T_CAPT2 - 0.1
    B.tele(L, 540, 640, 760, t, "orgullo" if capt else "normal", carpeta=True, salto=0.5 if capt else 0.0)
    u = sale((t - a) / 0.8)
    for k, (x0, y0) in enumerate(((60, -40), (540, -120), (1020, -40))):
        B.onda(L, x0, y0, 400 + k * 140, 220, t, u, 16, 50, None, 9)
    if capt:
        B.chispas(L, 540, 600, 450, t, 7, semilla=4)


def pantalla_grilla(t, u):
    def f(L, x0, y0, x1, y1):
        L.d.rounded_rectangle((L.S(x0), L.S(y0), L.S(x1), L.S(y1)), L.S(50), fill=(28, 28, 32))
        m = 46
        B.grilla100(L, x0 + m, y0 + m * 0.7, x1 - m, y1 - m * 0.7, t, u, especial=(6, 4))
    return f


@dib
def p12(L, t, a, b):
    # "Era más o menos el uno por ciento de esa lluvia."
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=C16["madera"])
    K.caja_red(L, 30, 220, 1050, 1000, 70, C16["bisel"], TINTA, 9)
    u = clamp((t - a) / 0.7)
    pantalla_grilla(t, u)(L, 70, 260, 1010, 960)
    if t >= T_UNO - 0.15:
        K.pildora(L, "MÁS O MENOS 1 %", 540, 120, 76, AMA, TINTA, pp(t, T_UNO - 0.15))


@dib
def p13(L, t, a, b):
    # "Cuando le pegabas a la tele,"
    B.living(L, t)
    gol = t >= T_PEGABAS - 0.2
    B.tele(L, 620, 600, 760, t, "mareado" if gol else "normal", carpeta=True, temblor=1.0 if gol else 0.0)
    if gol:
        A.estrella_golpe(L, 400, 300, 110 * pp(t, T_PEGABAS - 0.2), None, 10, "PAF", 60 * pp(t, T_PEGABAS - 0.2))
        B.palma(L, 300, 300, 1.05, -0.35, manga=(200, 186, 160))
    else:
        u = clamp((t - a) / max(0.3, T_PEGABAS - a))
        B.palma(L, 120 + 120 * u, 120 + 160 * u, 1.05, -0.35, manga=(200, 186, 160))


@dib
def p14(L, t, a, b):
    # "le pegabas al Big Bang."
    B.living(L, t)
    B.tele(L, 540, 600, 820, t, carpeta=True, temblor=0.3, pantalla=pantalla_bang(t, 130, "ay"))
    if t >= T_BANG2 - 0.1:
        u = pp(t, T_BANG2 - 0.1)
        A.globo(L, 640, 150, 960, 290, (760, 380), C["blanco"])
        txt(L, "¡AY!", 800, 220, 80 * u, TINTA)


@dib
def p15(L, t, a, b):
    # cola: vuelve al cuadro 0 (loop)
    portada(L, t, 110)


FUN = {i: globals()[f"p{i}"] for i in range(1, NP + 1)}
assert len(FUN) == len(T)

# ------------------------------------------------------------------ subtítulos (palabra por palabra, 1–3 palabras)
FONT = K.FONT
AMARILLO = (255, 210, 63)
CLAVE = {"BIG": (255, 170, 80), "BANG": (255, 170, 80), "ECO": (255, 170, 80), "CIENTO": (255, 170, 80)}
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
