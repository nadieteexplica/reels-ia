"""Ep. 10 en 2D plano (7-nov-2026, pedido de Tomás: "no es necesario 3D… haz el video entero, viral").
Mismo guion y voz aprobados (53,7 s, 27 planos de tiempos.json). Todo se dibuja con studio/plantilla/kit2d.py (PIL):
fotos reales en collage sobre papel, mapas planos de Natural Earth, escenas de siluetas planas y el viejo como narrador.

Uso: python3 video2d.py <carpeta_salida> [cuadro_desde cuadro_hasta]   (cuadros 1..FIN, 30 fps, 1080×1920)
"""
import json, math, os, random, sys
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
EPI = os.path.abspath(os.path.join(AQUI, ".."))
sys.path.insert(0, os.path.abspath(os.path.join(AQUI, "../../../plantilla")))
import kit2d as K
from kit2d import P

W, H, FPS, SS = 1080, 1920, 30, 2
T = {int(k): tuple(v) for k, v in json.load(open(os.path.join(EPI, "tiempos.json"))).items()}
F = lambda t: int(round(t * FPS)) + 1
FIN = F(T[max(T)][1])
GEO = os.path.join(AQUI, "paises50.geojson")
TEX = os.path.join(EPI, "escena", "tex")
words = json.load(open(os.path.join(EPI, "words.json")))
ENV = None      # envolvente de la voz (para la boca del viejo)


def env_voz():
    global ENV
    if ENV is None:
        p = os.path.join(AQUI, "envolvente.json")
        ENV = json.load(open(p)) if os.path.exists(p) else []
    return ENV


def boca(t):
    e = env_voz()
    if not e:
        return 0.5 + 0.5 * math.sin(t * 18)
    i = int(t * 60)
    return e[i] if 0 <= i < len(e) else 0.0


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def suave(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def sale(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def pop(edad, dur=0.3):
    if edad <= 0:
        return 0.0
    if edad >= dur:
        return 1.0
    x = edad / dur
    return 1 + 0.18 * math.sin(math.pi * x) * (1 - x) * 2 - (1 - x) ** 3


def tw(prefijo, desde=0.0):
    p = prefijo.lower()
    for w in words:
        if w["s"] >= desde - 0.01 and w["w"].lower().strip(".,;:…!?¡¿").startswith(p):
            return w["s"]
    return desde


def plano_de(t):
    for k, (a, b) in T.items():
        if a <= t < b:
            return k
    return max(T)


# ------------------------------------------------------------------ fotos reales en collage
@lru_cache(maxsize=8)
def foto(nombre):
    return Image.open(os.path.join(TEX, nombre)).convert("RGB")


@lru_cache(maxsize=8)
def collage(nombre, ancho=980, rot=-1.5, fondo=None):
    """La foto impresa (con su borde) pegada con cinta sobre papel, en un lienzo 1,35× más grande que el cuadro (para mover la cámara)."""
    cw, ch = int(W * 1.35), int(H * 1.35)
    base = Image.new("RGB", (cw, ch), fondo or P["papel"])
    im = foto(nombre)
    k = ancho * 1.35 / im.width
    im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
    sombra = Image.new("RGBA", (im.width + 60, im.height + 60), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).rectangle((30, 30, im.width + 30, im.height + 30), fill=(0, 0, 0, 90))
    sombra = sombra.filter(ImageFilter.GaussianBlur(14)).rotate(rot, expand=True, resample=Image.BICUBIC)
    ri = im.convert("RGBA").rotate(rot, expand=True, resample=Image.BICUBIC)
    x, y = (cw - ri.width) // 2, (ch - ri.height) // 2
    base.paste(sombra, (x + 10, y + 16), sombra)
    base.paste(ri, (x, y), ri)
    d = ImageDraw.Draw(base, "RGBA")
    for cx, cy, a in ((x + 40, y + 30, -30), (x + ri.width - 40, y + ri.height - 30, -30)):   # dos cintas en esquinas opuestas
        cinta = Image.new("RGBA", (220, 64), (236, 226, 190, 200))
        cinta = cinta.rotate(a, expand=True)
        base.paste(cinta, (cx - cinta.width // 2, cy - cinta.height // 2), cinta)
    return base, (x, y, ri.width, ri.height)


def camara(lienzo, zoom, cx, cy):
    """Recorta del lienzo grande un cuadro 9:16 centrado en (cx, cy) con zoom (1 = todo el ancho del cuadro final)."""
    cw, ch = lienzo.size
    w = W * 1.35 / zoom
    h = w * H / W
    x0 = clamp(cx - w / 2, 0, cw - w); y0 = clamp(cy - h / 2, 0, ch - h)
    return lienzo.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, H), Image.LANCZOS), (x0, y0, w / W)


def a_pantalla(px, py, ventana):
    x0, y0, s = ventana
    return (px - x0) / s, (py - y0) / s


# ------------------------------------------------------------------ gráficos sobre el cuadro final (1080×1920)
def capa(im):
    L = K.Lienzo(ss=1)
    L.im = im
    L.d = ImageDraw.Draw(im, "RGBA")
    return L


def pildora_t(im, s, cx, cy, t0, t, tam=52, fondo=None, tinta=None, hasta=None):
    if t < t0 or (hasta is not None and t >= hasta):
        return
    K.pildora(capa(im), s, cx, cy, tam, fondo, tinta, pop(t - t0))


def etiqueta_real(im, t, t0):
    pildora_t(im, "FOTO REAL", 190, 300, t0, t, tam=34, fondo=(30, 32, 36), tinta=(255, 255, 255))


# ------------------------------------------------------------------ subtítulos (manual §6; mismos grupos que el post del Ep. 10)
FONT = K.FONT
AMARILLO = (255, 210, 63)
CLAVE = {"KAMIKAZE": (240, 80, 64), "KAMIKAZES": (240, 80, 64)}
BOX = (120, 888, 1000, 1250)


def limpiar(w):
    w = w.replace("...", "").replace("…", "")
    for ch in ",.:;!¡?¿\"":
        w = w.replace(ch, "")
    return w.upper()


TOK = []
_i = 0
while _i < len(words):
    if limpiar(words[_i]["w"]) == "DIECISIETE":
        TOK.append(("17", [_i]))
    else:
        TOK.append((limpiar(words[_i]["w"]), [_i]))
    _i += 1
GRUPOS_MANUAL = """ESTE KAMIKAZE | TIENE 17 AÑOS | LA FOTO ES | DE 1945 | EL DÍA ANTES | DE SU MISIÓN | JAPÓN ESTÁ PERDIENDO | LA GUERRA |
Y MANDA | A SUS PILOTOS | A NO VOLVER | OFICIALMENTE | SON VOLUNTARIOS | PERO DECIRLE QUE NO | A TU ESCUADRÓN | ES CASI IMPOSIBLE |
ANTES DE DESPEGAR | LE ESCRIBEN | A SU FAMILIA | Y LE PIDEN | PERDÓN | LOS ESTADOUNIDENSES | NO SABEN | CÓMO FRENAR | A ALGUIEN QUE |
NO QUIERE VOLVER | LLENAN EL CIELO | DE BALAS | Y DERRIBAN | A LA MAYORÍA | PERO EL QUE PASA | CASI SIEMPRE PEGA | EN OKINAWA MUEREN |
MÁS MARINEROS | QUE SOLDADOS | DEL EJÉRCITO | EN TIERRA | Y A ESTADOS UNIDOS | TODAVÍA LE FALTA | INVADIR JAPÓN | PERO JAPÓN JUNTA |
CASI TRECE MIL AVIONES | TODOS | PARA CHOCAR | EL PRESIDENTE TRUMAN | TEME REPETIR OKINAWA | AHORA EN JAPÓN | ESE MIEDO | ES UNA |
DE LAS RAZONES | PARA LANZAR | LA BOMBA ATÓMICA | Y EL DÍA QUE | JAPÓN SE RINDE | TODAVÍA DESPEGAN | KAMIKAZES"""
grupos, _j = [], 0
for g in [g.split() for g in GRUPOS_MANUAL.replace("\n", " ").split("|") if g.strip()]:
    idx = list(range(_j, _j + len(g)))
    assert [TOK[j][0] for j in idx] == g, (g, [TOK[j][0] for j in idx])
    grupos.append(idx)
    _j += len(g)
assert _j == len(TOK)


def s_tok(j):
    return words[TOK[j][1][0]]["s"]


def e_tok(j):
    return words[TOK[j][1][-1]]["e"]


def ancho_toks(f, toks):
    return sum(f.getlength(t) for t in toks) + f.getlength(" ") * 1.15 * (len(toks) - 1)


def subtitulos(im, t):
    g = None
    for gi, gg in enumerate(grupos):
        s, e = s_tok(gg[0]), e_tok(gg[-1])
        nxt = grupos[gi + 1] if gi + 1 < len(grupos) else None
        e_show = min(e + 0.25, s_tok(nxt[0])) if nxt else e + 0.4
        if s - 0.03 <= t < e_show:
            g = gg
            break
    if g is None:
        return
    toks = [TOK[j][0] for j in g]
    maxw = (BOX[1] - BOX[0]) / 1.12
    lineas = [toks]
    for size in range(84, 59, -4):
        f = ImageFont.truetype(FONT, size)
        if ancho_toks(f, toks) <= maxw:
            break
    else:
        c = (len(toks) + 1) // 2
        lineas = [toks[:c], toks[c:]]
        f = ImageFont.truetype(FONT, 76)
    d = ImageDraw.Draw(im, "RGBA")
    lh = f.size * 1.12
    y0 = (BOX[2] + BOX[3]) / 2 - lh * len(lineas) / 2
    k = 0
    for li, linea in enumerate(lineas):
        x = W / 2 - ancho_toks(f, linea) / 2
        y = y0 + li * lh
        for tok in linea:
            j = g[k]; k += 1
            activo = s_tok(j) - 0.02 <= t < max(e_tok(j), s_tok(j) + 0.12)
            col = CLAVE.get(tok, AMARILLO if activo else (255, 255, 255))
            d.text((x + 3, y + 5), tok, font=f, fill=(0, 0, 0, 110))
            d.text((x, y), tok, font=f, fill=col, stroke_width=6, stroke_fill=(0, 0, 0))
            x += f.getlength(tok) + f.getlength(" ") * 1.15


# ------------------------------------------------------------------ escenas
def fondo_papel():
    return Image.new("RGB", (W, H), P["papel"])


def dibujo(fn):
    """Decorador: la escena dibuja en un Lienzo con sobremuestreo y sale a 1080×1920."""
    def envuelto(t, a, b):
        L = K.Lienzo(ss=SS)
        fn(L, t, a, b)
        return L.salida()
    return envuelto


def foto_plano(nombre, t, a, b, z0, z1, c0, c1, rot=-1.5):
    lienzo, (x, y, w, h) = collage(nombre, rot=rot)
    u = suave((t - a) / (b - a))
    cx = x + w * (c0[0] + (c1[0] - c0[0]) * u)
    cy = y + h * (c0[1] + (c1[1] - c0[1]) * u)
    im, ven = camara(lienzo, z0 + (z1 - z0) * u, cx, cy)
    return im, ven, (x, y, w, h)


def p1(t, a, b):
    im, ven, (x, y, w, h) = foto_plano("foto_impresa.jpg", t, a, b, 1.0, 1.06, (0.5, 0.55), (0.52, 0.52))
    bx, by = a_pantalla(x + w * 0.54, y + h * 0.40, ven)
    pildora_t(im, "KAMIKAZE · 17 AÑOS", 540, 330, a + 0.25, t, tam=54)
    if t > a + 0.5:
        L = capa(im); K.flecha(L, 600, 385, bx + 10, by - 40, P["blanco"], 9, u=sale((t - a - 0.5) / 0.3))
    return im


def p2(t, a, b):
    im, ven, _ = foto_plano("foto_impresa.jpg", t, a, b, 1.06, 1.75, (0.52, 0.52), (0.57, 0.58))
    pildora_t(im, "26 DE MAYO DE 1945", 540, 440, tw("1945", a - 0.3) - 0.05, t, tam=50)
    etiqueta_real(im, t, a + 0.2)
    return im


def cielo_amanecer(L, y1=1150, sol_y=1000, sol_x=760, t=0.0):
    K.cielo_bandas(L, [P["cielo3"], (196, 150, 140), P["cielo2"], P["cielo1"], (246, 214, 168)], 0, y1)
    K.circulo(L, sol_x, sol_y - 30 * t, 130, P["sol"])


def lomas(L, base_y, alto, color, fase=0.0, borde=True):
    pts = [(-20, H + 10)]
    for i in range(0, 1121, 20):
        x = i - 20
        yy = base_y - alto * (0.55 + 0.3 * math.sin(x / 170 + fase) + 0.15 * math.sin(x / 61 + 2 * fase))
        pts.append((x, yy))
    pts.append((W + 20, H + 10))
    K.poligono(L, pts, color, P["tinta"] if borde else None, 4)


def pista_suelo(L, y0=1150):
    L.d.rectangle((0, L.S(y0), L.S(W), L.S(H)), fill=(156, 140, 98))
    K.poligono(L, [(380, y0), (700, y0), (1200, H), (-120, H)], (186, 166, 122), P["tinta"], 3)
    for i in range(6):
        yy = y0 + 40 + i * i * 22
        L.d.line([L.pt(540 - 6 - i * 4, yy), L.pt(540 + 6 + i * 4, yy)], fill=(240, 230, 200), width=int(L.S(4 + i)))


def barraca(L, x, y, w=260, h=110):
    K.caja_red(L, x, y - h, x + w, y, 4, (128, 104, 80), P["tinta"], 4)
    K.poligono(L, [(x - 14, y - h), (x + w / 2, y - h - 46), (x + w + 14, y - h)], (90, 88, 84), P["tinta"], 4)
    for i in range(3):
        K.caja_red(L, x + 30 + i * 80, y - h + 30, x + 70 + i * 80, y - h + 64, 3, (60, 54, 46), P["tinta"], 3)


@dibujo
def p3(L, t, a, b):
    u = (t - a) / (b - a)
    cielo_amanecer(L, t=u)
    lomas(L, 1110, 230, (150, 128, 124), 0.3)
    lomas(L, 1160, 120, (118, 108, 92), 2.1)
    pista_suelo(L)
    barraca(L, 40, 1190)
    pan = -40 * u
    for i, x in enumerate((640, 860, 1080)):
        K.avion_lateral(L, x + pan + i * 0, 1215 - i * 18, largo=300 - i * 40, mira=-1)
    for i in range(3):
        K.persona(L, 250 + i * 120 + 30 * u, 1560, alto=260, ropa={"hachimaki": True}, pose={"paso": math.sin(t * 6 + i)}, mira=1, t=t + i)


def mapa_pacifico(L, t, centro, escala, perdidas_u=0.0, flechas_u=0.0):
    f = K.mapa(L, GEO, centro, escala, colores={"JPN": P["rojo"], "USA": P["azul2"]})
    islas = [("GUADALCANAL", -9.6, 160.1), ("NUEVA GUINEA", -5.5, 145.5), ("SAIPÁN", 15.2, 145.75), ("GUAM", 13.45, 144.8),
             ("LEYTE", 10.9, 124.9), ("LUZÓN", 16.0, 121.0), ("IWO JIMA", 24.78, 141.32)]
    for i, (n, la, lo) in enumerate(islas):
        x, y = f(lo, la)
        apagada = perdidas_u > (i + 1) / len(islas)
        K.circulo(L, x, y, 13, P["gris"] if apagada else P["rojo"], P["tinta"], 4)
    for (lo0, la0), (lo1, la1), d in (((163, -2), (143, 22), 0.0), ((129, 5), (128, 24), 0.3)):
        x0, y0 = f(lo0, la0); x1, y1 = f(lo1, la1)
        K.flecha(L, x0, y0, x1, y1, P["azul"], 20, u=sale((flechas_u - d) / 0.7))
    return f


@dibujo
def p4(L, t, a, b):
    u = suave((t - a) / (b - a))
    f = mapa_pacifico(L, t, (138 - 2 * u, 12 + 6 * u, 540, 960), 1650 + 450 * u, perdidas_u=(t - a) / 1.6, flechas_u=(t - a - 0.3) / 1.2)
    xj, yj = f(138.5, 37.5)
    K.pildora(L, "JAPÓN", xj, yj - 80, 46, escala=pop(t - a - 0.1))
    xs, ys = f(150, 5)
    if t - a > 1.1:
        K.pildora(L, "EE.UU.", min(900, xs), ys + 70, 42, fondo=P["azul"], tinta=P["blanco"], escala=pop(t - a - 1.1))
    K.viejo(L, 880, 1880, alto=420, boca=boca(t), t=t, gesto="apunta", mira=-1)


@dibujo
def p5(L, t, a, b):
    u = (t - a) / (b - a)
    cielo_amanecer(L, sol_x=820, t=0.4 + u * 0.3)
    lomas(L, 1110, 200, (150, 128, 124), 1.3)
    lomas(L, 1160, 110, (118, 108, 92), 0.7)
    pista_suelo(L)
    x = -150 + 1500 * u ** 1.6
    alt = max(0.0, (u - 0.45)) ** 1.5 * 900
    ang = min(12, (u - 0.45) * 40) if u > 0.45 else 0
    sub = K.Lienzo(w=700, h=300, ss=SS, fondo=(0, 0, 0))
    sub.im = Image.new("RGBA", (700 * SS, 300 * SS), (0, 0, 0, 0)); sub.d = ImageDraw.Draw(sub.im, "RGBA")
    K.avion_lateral(sub, 350, 150, largo=520, mira=1, helice_t=t)
    av = sub.im.rotate(ang, resample=Image.BICUBIC)
    L.im.paste(av, (int(L.S(x - 350)), int(L.S(1230 - alt - 150))), av)


def p6(t, a, b):
    im, ven, _ = foto_plano("foto_201.jpg", t, a, b, 1.55, 1.7, (0.35, 0.45), (0.62, 0.45), rot=1.2)
    etiqueta_real(im, t, a + 0.1)
    pildora_t(im, "VOLUNTARIOS", 540, 880, tw("voluntarios", a - 0.3), t, tam=60, fondo=P["ocre"])
    return im


def p7(t, a, b):
    im, ven, _ = foto_plano("foto_choshi.jpg", t, a, b, 1.5, 1.8, (0.42, 0.45), (0.56, 0.42), rot=-1.0)
    etiqueta_real(im, t, a + 0.1)
    return im


def p8(t, a, b):
    im, ven, _ = foto_plano("foto_teniente.jpg", t, a, b, 1.5, 2.6, (0.5, 0.5), (0.49, 0.33), rot=0.8)
    etiqueta_real(im, t, a + 0.1)
    return im


def p9(t, a, b):
    im, ven, _ = foto_plano("carta.jpg", t, a, b, 1.25, 1.45, (0.55, 0.35), (0.5, 0.62), rot=-2.0)
    pildora_t(im, "ÚLTIMA CARTA", 540, 560, a + 0.3, t, tam=60, fondo=P["ocre"])
    pildora_t(im, "RECREACIÓN", 880, 300, a, t, tam=34, fondo=(30, 32, 36), tinta=(255, 255, 255))
    return im


def p10(t, a, b):
    im, ven, _ = foto_plano("carta.jpg", t, a, b, 2.3, 2.0, (0.6, 0.5), (0.6, 0.5), rot=-2.0)
    pildora_t(im, "PERDÓN", 540, 560, tw("perdón", a - 0.3), t, tam=72, fondo=P["ocre"])
    pildora_t(im, "RECREACIÓN", 880, 300, a, t, tam=34, fondo=(30, 32, 36), tinta=(255, 255, 255))
    return im


# ---- el mar
def cielo_mar(L, oscuro=0.0):
    c = [(150, 170, 186), (166, 184, 196), (184, 198, 206), (200, 210, 214)]
    K.cielo_bandas(L, [tuple(int(v * (1 - 0.3 * oscuro)) for v in x) for x in c], 0, 1260)


def mar(L, y0=1260, t=0.0):
    L.d.rectangle((0, L.S(y0), L.S(W), L.S(H)), fill=P["mar2"])
    for i in range(7):
        yy = y0 + 40 + i * 90
        for j in range(5):
            xx = (j * 260 + i * 70 + t * 40 * (1 + i * 0.2)) % 1300 - 110
            L.d.line([L.pt(xx, yy), L.pt(xx + 90, yy)], fill=(176, 200, 206), width=int(L.S(5)))


def portaaviones(L, x, y, largo=1000, humo=0.0):
    k = largo / 1000
    gris, gris2 = (110, 116, 122), (88, 94, 100)
    K.poligono(L, [(x - 500 * k, y - 60 * k), (x + 520 * k, y - 60 * k), (x + 470 * k, y + 70 * k), (x - 440 * k, y + 70 * k)], gris2, P["tinta"], 5)
    K.poligono(L, [(x - 540 * k, y - 86 * k), (x + 560 * k, y - 86 * k), (x + 560 * k, y - 60 * k), (x - 540 * k, y - 60 * k)], (150, 128, 96), P["tinta"], 5)
    isx = x + 180 * k
    K.poligono(L, [(isx, y - 86 * k), (isx, y - 190 * k), (isx + 40 * k, y - 190 * k), (isx + 50 * k, y - 250 * k),
                   (isx + 90 * k, y - 250 * k), (isx + 100 * k, y - 190 * k), (isx + 150 * k, y - 190 * k), (isx + 160 * k, y - 86 * k)], gris, P["tinta"], 5)
    K.linea(L, [(isx + 70 * k, y - 250 * k), (isx + 70 * k, y - 340 * k)], P["tinta"], 7 * k)
    K.linea(L, [(isx + 40 * k, y - 310 * k), (isx + 100 * k, y - 310 * k)], P["tinta"], 6 * k)
    for i in range(9):    # cañones de la borda
        gx = x - 460 * k + i * 100 * k
        K.caja_red(L, gx, y - 60 * k, gx + 50 * k, y - 34 * k, 6 * k, gris, P["tinta"], 3)
        K.linea(L, [(gx + 25 * k, y - 58 * k), (gx + 50 * k, y - 96 * k)], P["tinta"], 5 * k)
    for i in range(3):
        K.caja_red(L, x - 300 * k + i * 160 * k, y - 20 * k, x - 260 * k + i * 160 * k, y, 4 * k, (60, 64, 70))


def marinero(L, x, y, alto=170, arriba=0.0, t=0.0, mira=-1):
    K.persona(L, x, y, alto=alto, ropa={"cabeza": "casco_m1", "torso": (122, 150, 188), "piernas": P["marino"], "botas": (50, 46, 42)},
              pose={"brazo_der": 10 + 140 * arriba, "brazo_izq": 10}, mira=mira, t=t)


def flak(L, t, t0, n=16, semilla=3, zona=(60, 100, 1020, 900)):
    random.seed(semilla)
    for i in range(n):
        x = random.uniform(zona[0], zona[2]); y = random.uniform(zona[1], zona[3])
        u = t - t0 - random.uniform(0, 1.4)
        if u <= 0:
            continue
        r = 14 + 22 * sale(u / 0.35) + 4 * u
        a = int(230 * clamp(1.6 - u * 0.5))
        K.circulo(L, x + 12 * u, y - 4 * u, r, (44, 40, 38, a))
        if u < 0.12:
            K.circulo(L, x, y, r * 0.6, (255, 220, 150, 230))


def trazadoras(L, t, n=26, semilla=4, desde_y=1200):
    random.seed(semilla)
    for i in range(n):
        x0 = random.uniform(60, 1020); dx = random.uniform(-220, 220); fase = random.uniform(0, 1); vel = random.uniform(1.4, 2.4)
        u = (t * vel + fase) % 1.0
        ya = desde_y - 1100 * u; yb = ya + 140
        xa = x0 + dx * u; xb = x0 + dx * (u - 0.13)
        K.linea(L, [(xb, yb), (xa, ya)], (255, 196, 110), 6)


def humo_estela(L, pts, r0=10, r1=34, color=(52, 48, 46)):
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        r = r0 + (r1 - r0) * i / max(1, n - 1)
        K.circulo(L, x, y, r, (*color, int(200 * (1 - i / n))))


def avion_frente(L, x, y, escala=1.0, inclina=0.0):
    """Avión que viene hacia la cámara (de frente, picando)."""
    k = escala
    c = (98, 112, 80)
    K.poligono(L, [(x - 260 * k, y - 10 * k + inclina * 60 * k), (x + 260 * k, y - 10 * k - inclina * 60 * k),
                   (x + 260 * k, y + 12 * k - inclina * 60 * k), (x - 260 * k, y + 12 * k + inclina * 60 * k)], c, P["tinta"], 5)
    K.circulo(L, x - 170 * k, y + inclina * 40 * k, 18 * k, P["rojo"], P["blanco"], 3)
    K.circulo(L, x + 170 * k, y - inclina * 40 * k, 18 * k, P["rojo"], P["blanco"], 3)
    K.circulo(L, x, y, 60 * k, (70, 74, 64), P["tinta"], 5)
    K.circulo(L, x, y, 30 * k, P["tinta"])
    K.poligono(L, [(x - 8 * k, y - 60 * k), (x + 8 * k, y - 60 * k), (x + 4 * k, y - 120 * k), (x - 4 * k, y - 120 * k)], c, P["tinta"], 4)
    hl = 90 * k
    K.linea(L, [(x - hl, y - hl * 0.3), (x + hl, y + hl * 0.3)], (80, 76, 70, 160), 10 * k)


@dibujo
def p11(L, t, a, b):
    u = (t - a) / (b - a)
    cielo_mar(L)
    flak(L, t, a + 0.6, n=6, zona=(80, 120, 1000, 500))
    mar(L, t=t)
    portaaviones(L, 540 - 60 * u, 1290, 1100)
    mira_arriba = sale((t - a - 0.2) / 0.5)
    for i, x in enumerate((220, 300, 380)):
        marinero(L, x - 60 * u, 1204, 150, arriba=mira_arriba if i == 1 else 0, t=t + i)
    if (t * 4) % 1 < 0.5:     # luces de alarma
        K.circulo(L, 760 - 60 * u, 1060, 14, (255, 80, 60))


@dibujo
def p12(L, t, a, b):
    u = clamp((t - a) / (b - a + 0.1))
    cielo_mar(L)
    flak(L, t, a - 0.8, n=10, semilla=5, zona=(60, 100, 1020, 1000))
    mar(L, 1500, t=t)
    portaaviones(L, 540, 1520, 700)
    esc = 0.15 + 0.85 * u ** 1.6
    x = 640 - 140 * u; y = 260 + 520 * u
    humo_estela(L, [(x + (i + 1) * 30 * esc, y - (i + 1) * 60 * esc) for i in range(10)], 10 * esc, 40 * esc)
    avion_frente(L, x, y, escala=esc, inclina=0.15 * math.sin(t * 3))


@dibujo
def p13(L, t, a, b):
    cielo_mar(L)
    trazadoras(L, t)
    flak(L, t, a - 1.2, n=22, semilla=8)
    mar(L, 1500, t=t)
    portaaviones(L, 540, 1520, 1300)


@dibujo
def p14(L, t, a, b):
    cielo_mar(L, 0.1)
    flak(L, t, a - 1.5, n=12, semilla=11)
    mar(L, 1250, t=t)
    for i, (x0, golpe) in enumerate(((260, a + 0.7), (760, a + 1.3))):
        u = clamp((t - (golpe - 1.3)) / 1.3)
        x = x0 + 120 * u; y = 200 + 1050 * u ** 1.5
        if t < golpe:
            humo_estela(L, [(x - 25 * j, y - 70 * j) for j in range(1, 12)], 10, 46)
            sub = K.Lienzo(w=500, h=240, ss=SS)
            sub.im = Image.new("RGBA", (500 * SS, 240 * SS), (0, 0, 0, 0)); sub.d = ImageDraw.Draw(sub.im, "RGBA")
            K.avion_lateral(sub, 250, 120, largo=300, mira=1)
            av = sub.im.rotate(-55 - 20 * u, resample=Image.BICUBIC)
            L.im.paste(av, (int(L.S(x - 250)), int(L.S(y - 120))), av)
        else:
            v = t - golpe
            alto = 260 * sale(v / 0.35) * (1 - 0.4 * clamp((v - 0.6) / 0.6))
            K.poligono(L, [(x - 70, 1262), (x - 26, 1262 - alto), (x, 1262 - alto * 1.1), (x + 26, 1262 - alto), (x + 70, 1262)], P["blanco"], P["tinta"], 4)


@dibujo
def p15(L, t, a, b):
    u = clamp((t - a + 0.1) / (b - a))
    cielo_mar(L, 0.15)
    for i, (dx, dy, r) in enumerate(((0, 0, 160), (-120, 40, 120), (130, 30, 130), (40, -90, 110), (-60, 110, 100))):
        K.circulo(L, 520 + dx + 6 * math.sin(t + i), 640 + dy, r, (60, 56, 54, 235))
    esc = 0.5 + 0.7 * u
    x = 520 + 260 * u; y = 640 + 380 * u
    if u > 0.12:
        humo_estela(L, [(x - (j + 1) * 40 * esc, y - (j + 1) * 50 * esc) for j in range(8)], 8 * esc, 30 * esc)
        sub = K.Lienzo(w=700, h=320, ss=SS)
        sub.im = Image.new("RGBA", (700 * SS, 320 * SS), (0, 0, 0, 0)); sub.d = ImageDraw.Draw(sub.im, "RGBA")
        K.avion_lateral(sub, 350, 160, largo=420 * esc, mira=1, helice_t=t)
        av = sub.im.rotate(-38, resample=Image.BICUBIC)
        L.im.paste(av, (int(L.S(x - 350)), int(L.S(y - 160))), av)
    mar(L, 1500, t=t)


@dibujo
def p16(L, t, a, b):
    u = clamp((t - a) / (b - a - 0.2))
    cielo_mar(L)
    mar(L, 1500, t=t)
    portaaviones(L, 540, 1520 + 300 * u, 1100 + 900 * u)
    esc = 0.6 + 2.6 * u ** 1.4
    avion_frente(L, 540, 760 + 240 * u, escala=esc, inclina=0.05)
    if t >= T[16][1] - 0.2:
        L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=(255, 255, 255, int(255 * clamp((t - (T[16][1] - 0.2)) / 0.08))))


@dibujo
def p17(L, t, a, b):
    u = (t - a) / (b - a)
    cielo_mar(L, 0.25)
    mar(L, 1300, t=t)
    portaaviones(L, 520, 1330, 900)
    random.seed(17)
    for i in range(16):
        h = (i * 60 + 70 * t) % 900
        r = 30 + h * 0.12
        K.circulo(L, 640 + h * 0.25 + 10 * math.sin(t + i), 1180 - h, r, (40, 38, 36, int(230 * (1 - h / 950))))
    for i in range(4):
        K.circulo(L, 620 + i * 18, 1230 - (t * 120 + i * 30) % 60, 20, (250, 150, 60, 220))


def mapa_japon(L, centro, escala, colores=None):
    return K.mapa(L, GEO, centro, escala, colores=colores or {"JPN": (224, 196, 164)})


@dibujo
def p18(L, t, a, b):
    u = suave((t - a) / (b - a))
    f = mapa_japon(L, (128.3, 24.6, 540, 760), 5200 + 400 * u)
    xo, yo = f(127.85, 26.45)
    K.circulo(L, xo, yo, 18, P["rojo"], P["tinta"], 4)
    K.texto(L, "OKINAWA", xo + 30, yo - 30, 40, ancla="lm", borde=6, color=P["blanco"])
    v = t - a - 0.15
    if v > 0:
        for i, (nom, val, col, x) in enumerate((("MARINEROS", 4907, P["azul"], 330), ("EJÉRCITO", 4675, P["verde"], 750))):
            uu = sale(min(1.0, v / (1.4 if i == 0 else 1.2)))
            hh = 330 * val / 4907 * uu
            K.caja_red(L, x - 95, 900 - hh, x + 95, 900, 10, col, P["tinta"], 5)
            K.texto(L, f"{int(val * uu):,}".replace(",", "."), x, 900 - hh - 44, 58, P["blanco"], borde=6)
            K.texto(L, nom, x, 940, 40, P["blanco"], borde=6)


@dibujo
def p19(L, t, a, b):
    u = suave((t - a) / (b - a))
    f = mapa_japon(L, (129 + 1.5 * u, 28.5 + 3 * u, 540, 900), 3600 - 600 * u)
    xo, yo = f(127.85, 26.45); xk, yk = f(130.6, 31.8)
    K.circulo(L, xo, yo, 16, P["azul"], P["tinta"], 4)
    for i, dx in enumerate((-50, 0, 50)):
        K.flecha(L, xo + dx, yo - 20, xk + dx * 0.4, yk + 40, P["azul"], 18, u=sale((t - a - 0.1 - 0.15 * i) / 1.6))
    if t > tw("invadir", a - 0.3) - 0.1:
        K.pildora(L, "INVASIÓN · 1 DE NOVIEMBRE", 540, 560, 50, fondo=P["azul"], tinta=P["blanco"], escala=pop(t - tw("invadir", a - 0.3) + 0.1))


def icono_avion(L, x, y, s=1.0, c=(98, 112, 80)):
    K.poligono(L, [(x - 6 * s, y - 30 * s), (x + 6 * s, y - 30 * s), (x + 6 * s, y + 30 * s), (x - 6 * s, y + 30 * s)], c)
    K.poligono(L, [(x - 34 * s, y - 6 * s), (x + 34 * s, y - 6 * s), (x + 34 * s, y + 6 * s), (x - 34 * s, y + 6 * s)], c)
    K.poligono(L, [(x - 14 * s, y + 22 * s), (x + 14 * s, y + 22 * s), (x + 14 * s, y + 30 * s), (x - 14 * s, y + 30 * s)], c)
    K.circulo(L, x - 22 * s, y, 4 * s, P["rojo"]); K.circulo(L, x + 22 * s, y, 4 * s, P["rojo"])


@dibujo
def p20(L, t, a, b):
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=P["papel"])
    t0 = tw("junta", a - 0.3)
    n = int(127 * sale((t - t0) / 1.7)) if t > t0 else 0
    cols = 9
    for i in range(n):
        r, c = divmod(i, cols)
        x = 80 + c * 115; y = 360 + r * 76
        if y > 1500:
            break
        icono_avion(L, x, y, 0.95)
    if t > t0:
        num = int(round(12700 * sale((t - t0) / 1.7) / 100.0)) * 100
        K.pildora(L, f"{num:,}".replace(",", ".") + " AVIONES", 540, 230, 68, fondo=P["ocre"], escala=pop(t - t0))
    K.texto(L, "CADA ÍCONO = 100 AVIONES", 400, 1560, 34, P["tinta"])
    K.viejo(L, 900, 1900, alto=380, boca=boca(t), t=t, gesto="tazon", mira=-1)


@dibujo
def p21(L, t, a, b):
    u = (t - a) / (b - a)
    cielo_amanecer(L, y1=1200, sol_y=980, sol_x=300, t=0.2)
    lomas(L, 1150, 160, (130, 116, 104), 2.7)
    L.d.rectangle((0, L.S(1200), L.S(W), L.S(H)), fill=(150, 136, 96))
    for i in range(5):
        x = 200 + i * 300 - 500 * u
        K.avion_lateral(L, x, 1300, largo=330, mira=-1)
        K.caja_red(L, x - 30, 1330, x + 50, 1356, 12, (60, 60, 56), P["tinta"], 4)      # la bomba colgada
        K.flecha(L, x + 10, 1500, x + 10, 1372, P["rojo"], 10, u=sale((t - a - 0.2 - 0.12 * i) / 0.3))


@dibujo
def p22(L, t, a, b):
    u = suave((t - a) / (b - a))
    f = mapa_japon(L, (130, 30, 540, 900), 3000 + 200 * u)
    xo, yo = f(127.85, 26.45)
    late = 0.55 + 0.45 * abs(math.sin((t - a) * math.pi * 1.1))
    K.circulo(L, xo, yo, 70 * late, (196, 64, 52, 150))
    K.texto(L, "OKINAWA", xo + 40, yo + 70, 40, P["blanco"], ancla="lm", borde=6)
    K.pildora(L, "PRESIDENTE TRUMAN", 540, 560, 54, fondo=P["azul"], tinta=P["blanco"], escala=pop(t - a - 0.1))


def manchas_japon(L, f, t, a, crece=True, apaga=1.0):
    u = t - a
    late = (0.6 + 0.4 * abs(math.sin(u * math.pi * 1.3))) * apaga
    xo, yo = f(127.85, 26.45)
    K.circulo(L, xo, yo, 40 * late, (196, 64, 52, int(160 * apaga)))
    for i, (lo, la) in enumerate(((130.9, 32.6), (132.45, 34.39), (136.0, 35.4), (139.69, 35.68), (140.5, 38.5))):
        v = sale((u - 0.2 - 0.3 * i) / 0.5) if crece else 1.0
        x, y = f(lo, la)
        K.circulo(L, x, y, 70 * v * late + 1, (196, 64, 52, int(150 * apaga)))


@dibujo
def p23(L, t, a, b):
    u = suave((t - a) / (b - a))
    f = mapa_japon(L, (133, 33, 540, 900), 2400 - 500 * u)
    manchas_japon(L, f, t, a)
    K.pildora(L, "¿OTRO OKINAWA?", 540, 330, 54, fondo=P["azul"], tinta=P["blanco"], escala=pop(t - a - 0.2))


@dibujo
def p24(L, t, a, b):
    u = suave((t - a) / (b - a))
    f = mapa_japon(L, (134, 33.5, 540, 900), 1900 - 200 * u)
    manchas_japon(L, f, T[23][0] + 3, T[23][0], crece=False, apaga=1 - u * 0.8)
    K.viejo(L, 900, 1900, alto=380, boca=boca(t), t=t, gesto="tazon", mira=-1)


@dibujo
def p25(L, t, a, b):
    f = mapa_japon(L, (134, 33.5, 540, 900), 1700)
    u = t - a
    for (lo, la, t1, txt, dy) in ((132.45, 34.39, 0.1, "6 DE AGOSTO", -80), (129.88, 32.75, 0.8, "9 DE AGOSTO", 80)):
        x, y = f(lo, la)
        v = (u - t1) / 0.8
        if 0 < v < 1:
            r = 40 + 360 * sale(v)
            K.circulo(L, x, y, r, (255, 250, 230, int(255 * math.exp(-v * 3))))
        if u > t1:
            K.circulo(L, x, y, 12, P["blanco"], P["tinta"], 4)
        if u > t1 + 0.1:
            K.texto(L, txt, x + 20, y + dy, 42, P["blanco"], ancla="lm", borde=6)


def p26(t, a, b):
    im, ven, _ = foto_plano("foto_rendicion.jpg", t, a, b, 1.5, 1.7, (0.45, 0.5), (0.55, 0.5), rot=-1.2)
    etiqueta_real(im, t, a + 0.1)
    pildora_t(im, "15 DE AGOSTO DE 1945", 540, 420, a + 0.1, t, tam=50)
    pildora_t(im, "JAPÓN SE RINDE", 540, 560, tw("rinde", a - 0.3), t, tam=64, fondo=P["ocre"])
    return im


@dibujo
def p27(L, t, a, b):
    u = (t - a) / (b - a)
    K.cielo_bandas(L, [(120, 84, 100), (170, 96, 92), (214, 120, 84), (240, 160, 92), (250, 196, 120)], 0, 1200)
    K.circulo(L, 540, 1120, 170, (252, 220, 150))
    lomas(L, 1180, 170, (60, 46, 52), 0.9, borde=False)
    L.d.rectangle((0, L.S(1200), L.S(W), L.S(H)), fill=(70, 54, 50))
    for i in range(3):
        v = clamp(u * 1.4 - i * 0.28)
        x = 200 + 900 * v ** 1.3
        y = 1210 - max(0.0, v - 0.35) ** 1.5 * 1100
        sub = K.Lienzo(w=500, h=240, ss=SS)
        sub.im = Image.new("RGBA", (500 * SS, 240 * SS), (0, 0, 0, 0)); sub.d = ImageDraw.Draw(sub.im, "RGBA")
        K.avion_lateral(sub, 250, 120, largo=300, mira=1, color=(40, 30, 32), sol_rojo=False, tinta=False)
        av = sub.im.rotate(min(14, max(0, (v - 0.35) * 40)), resample=Image.BICUBIC)
        L.im.paste(av, (int(L.S(x - 250)), int(L.S(y - 120))), av)


FUN = {1: p1, 2: p2, 3: p3, 4: p4, 5: p5, 6: p6, 7: p7, 8: p8, 9: p9, 10: p10, 11: p11, 12: p12, 13: p13, 14: p14, 15: p15,
       16: p16, 17: p17, 18: p18, 19: p19, 20: p20, 21: p21, 22: p22, 23: p23, 24: p24, 25: p25, 26: p26, 27: p27}
LOOP0 = F(T[27][1] - 0.30)
_GRANO = {}


def cuadro(f):
    t = (f - 1) / FPS
    if f >= LOOP0:                          # loop: vuelve la foto del cuadro 0
        k, tt = 1, T[1][0] + (f - LOOP0) / FPS
    else:
        k, tt = plano_de(t), t
    a, b = T[k]
    im = FUN[k](tt, a, b)
    if not _GRANO:
        _GRANO["g"] = Image.effect_noise((W, H), 18).convert("RGB")
    im = Image.blend(im, Image.composite(im, _GRANO["g"], Image.new("L", (W, H), 236)), 0.25)
    if k == 17 and f < LOOP0:
        pildora_t(im, "OKINAWA, 1945", 270, 330, a + 0.15, t, tam=50, fondo=P["azul"], tinta=P["blanco"])
    subtitulos(im, t)
    return im


if __name__ == "__main__":
    dst = sys.argv[1]
    os.makedirs(dst, exist_ok=True)
    a = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    b = int(sys.argv[3]) if len(sys.argv) > 3 else FIN - 1
    for f in range(a, b + 1):
        cuadro(f).save(os.path.join(dst, f"{f:05d}.png"), compress_level=1)
    print("ok", a, b)
