"""Ep. 10e — "Lo escondían detrás de una flor" (8-nov-2026). Idea central: la flor de cerezo.
Foto real de Chiran (12-abr-1945) como eje, pétalos todo el video, 15 planos largos y sin zoom (Tomás: "esos zoom cada dos
segundos, pésimos"). Voz out/tts/ep10e-kamikaze-cerezo.mp3 con 2 respiros agregados en la edición (PAUSAS).
Uso: python3 video.py <salida> [cuadro_desde cuadro_hasta]
"""
import json, math, os, random, sys
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
EPI = os.path.abspath(os.path.join(AQUI, ".."))
sys.path.insert(0, os.path.abspath(os.path.join(AQUI, "../../ep10-kamikazes/escena2d")))
import video2d as V
import kit2d as K
from kit2d import P

W, H, FPS = 1080, 1920, 30
TEX_E = os.path.join(AQUI, "tex")
TEX_10 = os.path.abspath(os.path.join(AQUI, "../../ep10-kamikazes/escena/tex"))
JP = os.path.abspath(os.path.join(AQUI, "../../../plantilla/fonts/YujiSyuku-Regular.ttf"))
clamp, suave, sale, pop = V.clamp, V.suave, V.sale, V.pop

PAUSAS = [(35.75, 0.5), (44.82, 0.6)]      # respiros que se meten en la voz (segundo original, duración)


def corre(t):
    return t + sum(d for p, d in PAUSAS if t >= p)


_raw = json.load(open(os.path.join(EPI, "words.json")))
words = [{"w": x["w"], "s": corre(x["s"]), "e": corre(x["e"])} for x in _raw]
FIN_VOZ = words[-1]["e"]
DUR = FIN_VOZ + 1.5
FIN = int(round(DUR * FPS))


def tw(prefijo, desde=0.0):
    p = prefijo.lower()
    for w in words:
        if w["s"] >= desde - 0.01 and w["w"].lower().strip(".,;:…!?¡¿").startswith(p):
            return w["s"]
    raise KeyError(prefijo)


CORTES = [0.0,
          tw("Esas") - 0.1,            # 2 detalle: las ramas
          tw("Son") - 0.1,             # 3 rama de cerezo
          tw("Y", 12.5) - 0.06,        # 4 pilotos (foto)
          tw("Que", 15.9) - 0.06,      # 5 escuadrón (foto)
          tw("Hasta") - 0.1,           # 6 bomba Ōka
          tw("Y", 21.0) - 0.06,        # 7 桜花
          tw("Y", 25.0) - 0.06,        # 8 Yasukuni
          tw("Por", 28.4) - 0.08,      # 9 sonriendo (foto)
          tw("Pero") - 0.1,            # 10 las chicas (foto)
          tw("Y", 33.0) - 0.06,        # 11 almohada
          tw("El", 36.0) - 0.4,        # 12 el piloto de esta foto
          tw("Antes") - 0.1,           # 13 cartas que arden
          tw("Y", 41.9) - 0.06,        # 14 la cita
          tw("No", 45.5) - 0.45,       # 15 cierre
          DUR]
T = {i + 1: (CORTES[i], CORTES[i + 1]) for i in range(len(CORTES) - 1)}
for k, (a, b) in T.items():
    assert b - a >= 1.5, (k, a, b)


def plano_de(t):
    for k, (a, b) in T.items():
        if a <= t < b:
            return k
    return max(T)


FONDO = (22, 20, 22)
ROSA, ROSA2, ROSA3 = (238, 164, 182), (248, 206, 216), (214, 120, 146)
CREMA = (238, 228, 206)


def dib(fn):
    def envuelto(t, a, b, **kw):
        L = K.Lienzo(ss=V.SS, fondo=FONDO)
        fn(L, t, a, b, **kw)
        return L.salida()
    return envuelto


# ------------------------------------------------------------------ fotos
@lru_cache(maxsize=16)
def foto_lista(ruta, crop, ancho, rot, borde):
    """Foto (recorte en fracciones) lista para pegar a ss: con borde crema si es recorte, sombra y giro."""
    im = Image.open(ruta).convert("RGB")
    if crop:
        x0, y0, x1, y1 = crop
        im = im.crop((int(x0 * im.width), int(y0 * im.height), int(x1 * im.width), int(y1 * im.height)))
    ss = V.SS
    w = int(ancho * ss)
    im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
    if borde:
        b = int(22 * ss)
        base = Image.new("RGB", (im.width + 2 * b, im.height + 2 * b), CREMA)
        base.paste(im, (b, b))
        im = base
    sh = Image.new("RGBA", (im.width + 80 * ss, im.height + 80 * ss), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((40 * ss, 52 * ss, im.width + 40 * ss, im.height + 52 * ss), fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(18 * ss))
    sh.paste(im, (40 * ss, 40 * ss))
    return sh.rotate(rot, expand=True, resample=Image.BICUBIC)


def pegar_foto(L, ruta, cx, cy, ancho, crop=None, rot=-0.8, borde=False):
    im = foto_lista(ruta, crop, ancho, rot, borde)
    L.im.paste(im, (int(L.S(cx) - im.width / 2), int(L.S(cy) - im.height / 2)), im)


def etiqueta(L, s, x, y, tam=30):
    K.pildora(L, s, x, y, tam, fondo=(16, 14, 16), tinta=CREMA)


def jp(L, s, x, y, tam, color, alfa=255, vertical=False):
    f = ImageFont.truetype(JP, int(L.S(tam)))
    if vertical:
        for i, ch in enumerate(s):
            L.d.text(L.pt(x, y + i * tam * 1.05), ch, font=f, fill=(*color, alfa), anchor="mm")
    else:
        L.d.text(L.pt(x, y), s, font=f, fill=(*color, alfa), anchor="mm")


# ------------------------------------------------------------------ pétalos y rama
random.seed(10)
PETALOS = [dict(x0=random.uniform(-100, W + 100), y0=random.uniform(0, 2300), v=random.uniform(70, 150), amp=random.uniform(20, 70),
                f=random.uniform(0.6, 1.4), rot=random.uniform(0, 6.28), vr=random.uniform(-2.5, 2.5), s=random.uniform(0.7, 1.5),
                dr=random.uniform(-40, -10), c=random.choice([ROSA, ROSA2, ROSA, ROSA3])) for _ in range(90)]
FORMA = [(0, -12), (4, -15), (9, -10), (10, 0), (6, 9), (0, 13), (-6, 9), (-10, 0), (-9, -10), (-4, -15)]


def petalo(L, x, y, s, ang, c, alfa=235, giro=1.0):
    ca, sa = math.cos(ang), math.sin(ang)
    pts = [(x + (px * giro * ca - py * sa) * s * 1.6, y + (px * giro * sa + py * ca) * s * 1.6) for px, py in FORMA]
    K.poligono(L, pts, (*c, alfa))


def petalos(L, t, n=50, alfa=230):
    for i, p in enumerate(PETALOS[:n]):
        y = (p["y0"] + t * p["v"]) % 2300 - 200
        x = (p["x0"] + p["amp"] * math.sin(t * p["f"] + i) + t * p["dr"]) % (W + 300) - 150
        ang = p["rot"] + t * p["vr"]
        petalo(L, x, y, p["s"], ang, p["c"], alfa, giro=0.35 + 0.65 * abs(math.cos(t * p["f"] * 1.7 + i)))


def flor(L, x, y, r, t=0.0, abierta=1.0, caidos=0, ang0=0.0):
    """Flor de cerezo de 5 pétalos (los primeros `caidos` ya no están)."""
    for j in range(caidos, 5):
        a = ang0 + j * 2 * math.pi / 5 + 0.05 * math.sin(t * 2 + x)
        px, py = x + math.cos(a) * r * 0.62 * abierta, y + math.sin(a) * r * 0.62 * abierta
        ca, sa = math.cos(a + math.pi / 2), math.sin(a + math.pi / 2)
        pts = [(px + (fx * ca - fy * sa) * r / 13, py + (fx * sa + fy * ca) * r / 13) for fx, fy in FORMA]
        K.poligono(L, pts, ROSA2 if j % 2 else ROSA, (180, 110, 128), 1.5)
    K.circulo(L, x, y, r * 0.22, (232, 120, 140))
    for j in range(6):
        a = j * math.pi / 3 + 0.3
        K.circulo(L, x + math.cos(a) * r * 0.33, y + math.sin(a) * r * 0.33, r * 0.06, (250, 220, 120))


RAMAS = [[(0, 0), (260, -120), (520, -170), (760, -300)], [(260, -120), (330, -300), (300, -420)], [(520, -170), (640, -60), (780, -40)],
         [(150, -60), (170, -200)], [(640, -230), (700, -420)]]
random.seed(4)
FLORES = []
for rama_ in RAMAS:
    for k in range(len(rama_) - 1):
        (x0, y0), (x1, y1) = rama_[k], rama_[k + 1]
        for u in (0.45, 1.0):
            nx, ny = -(y1 - y0), (x1 - x0)
            nn = math.hypot(nx, ny) or 1
            off = random.choice([-1, 1]) * random.uniform(14, 30)
            FLORES.append((x0 + (x1 - x0) * u + nx / nn * off, y0 + (y1 - y0) * u + ny / nn * off, random.uniform(24, 34), random.uniform(0, 6)))


def rama(L, x, y, s=1.0, t=0.0, espejo=1, t_cae=None):
    sw = math.sin(t * 0.9) * 4
    for r_ in RAMAS:
        pts = [(x + espejo * px * s + sw * (i / 3), y + py * s) for i, (px, py) in enumerate(r_)]
        K.miembro(L, pts, (30, 20, 18), 40 * s * (1.0 if r_ is RAMAS[0] else 0.6), tinta=False)
        K.miembro(L, pts, (92, 62, 52), 30 * s * (1.0 if r_ is RAMAS[0] else 0.6), tinta=False)
    for i, (fx, fy, r, a0) in enumerate(FLORES):
        cx, cy = x + espejo * fx * s + sw * 0.6, y + fy * s
        caidos = 0
        if t_cae is not None and t > t_cae and i % 3 == 0:
            e = t - t_cae - (i % 7) * 0.12
            caidos = min(5, max(0, int(e * 6)))
            for j in range(caidos):
                ee = e - j / 6
                if ee > 0:
                    petalo(L, cx + 40 * math.sin(ee * 2 + j) + ee * 30, cy + ee * 260 + ee * ee * 60, s * 1.1, ee * 3 + j, ROSA, 240)
        flor(L, cx, cy, r * s, t, 1.0, caidos, a0)


def rama_esquina(L, t):
    rama(L, -40, 1900, 0.9, t)


# ------------------------------------------------------------------ objetos dibujados
def ohka(L, x, y, largo, t, flor_u=1.0):
    k = largo / 1000
    gris = (150, 158, 146)
    K.poligono(L, [(x - 500 * k, y - 40 * k), (x + 330 * k, y - 62 * k), (x + 470 * k, y - 30 * k), (x + 500 * k, y), (x + 470 * k, y + 30 * k),
                   (x + 330 * k, y + 62 * k), (x - 500 * k, y + 46 * k)], gris, (30, 30, 30), 4)
    K.poligono(L, [(x + 330 * k, y - 62 * k), (x + 470 * k, y - 30 * k), (x + 500 * k, y), (x + 470 * k, y + 30 * k), (x + 330 * k, y + 62 * k)], (110, 112, 104), (30, 30, 30), 4)
    K.poligono(L, [(x - 120 * k, y + 10 * k), (x + 120 * k, y + 10 * k), (x + 60 * k, y + 50 * k), (x - 200 * k, y + 50 * k)], (120, 128, 118), (30, 30, 30), 4)
    L.d.chord((L.S(x - 300 * k), L.S(y - 110 * k), L.S(x - 120 * k), L.S(y - 10 * k)), 180, 360, fill=(170, 196, 206), outline=(30, 30, 30), width=int(L.S(4)))
    K.poligono(L, [(x - 500 * k, y - 40 * k), (x - 440 * k, y - 40 * k), (x - 470 * k, y - 170 * k), (x - 520 * k, y - 170 * k)], gris, (30, 30, 30), 4)
    for i in range(3):
        K.circulo(L, x - 505 * k, y - 10 * k + i * 26 * k, 12 * k, (60, 56, 52), (30, 30, 30), 2)
        if t > 0:
            K.elipse(L, x - 560 * k - 30 * k * math.sin(t * 30 + i), y - 10 * k + i * 26 * k, 50 * k, 10 * k, (255, 170, 80, 120))
    if flor_u > 0:
        flor(L, x + 230 * k, y, 70 * k * sale(flor_u), t)


def torii(L, cx, base, h, t):
    k = h / 1000
    rojo, osc = (186, 48, 38), (34, 26, 26)
    for s in (-1, 1):
        K.poligono(L, [(cx + s * 300 * k - 34 * k, base), (cx + s * 300 * k + 34 * k, base), (cx + s * 280 * k + 28 * k, base - 900 * k), (cx + s * 280 * k - 28 * k, base - 900 * k)], rojo, osc, 4)
        K.caja_red(L, cx + s * 300 * k - 46 * k, base - 50 * k, cx + s * 300 * k + 46 * k, base, 6, osc)
    K.caja_red(L, cx - 400 * k, base - 760 * k, cx + 400 * k, base - 700 * k, 6, rojo, osc, 4)
    K.caja_red(L, cx - 26 * k, base - 900 * k, cx + 26 * k, base - 760 * k, 4, rojo, osc, 3)
    K.poligono(L, [(cx - 520 * k, base - 960 * k), (cx + 520 * k, base - 960 * k), (cx + 470 * k, base - 900 * k), (cx - 470 * k, base - 900 * k)], rojo, osc, 4)
    K.poligono(L, [(cx - 580 * k, base - 1030 * k), (cx + 580 * k, base - 1030 * k), (cx + 520 * k, base - 960 * k), (cx - 520 * k, base - 960 * k)], osc, osc, 2)


def cerezo(L, x, base, h, t, semilla=1):
    random.seed(semilla)
    K.poligono(L, [(x - 26, base), (x + 26, base), (x + 12, base - h * 0.55), (x - 12, base - h * 0.55)], (54, 38, 34))
    for i in range(46):
        a = random.uniform(0, 6.28); r = random.uniform(0, h * 0.42)
        K.circulo(L, x + math.cos(a) * r * 1.2, base - h * 0.62 + math.sin(a) * r * 0.6, random.uniform(40, 90),
                  random.choice([(214, 128, 150, 210), (236, 166, 184, 210), (246, 200, 212, 200)]))


def cuarto_noche(L, t, t0):
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=(14, 18, 30))
    K.poligono(L, [(-200, 0), (420, 0), (1200, 1920), (300, 1920)], (70, 86, 120, 60))
    K.caja_red(L, -20, 1260, 1100, 1960, 30, (40, 46, 64), (8, 10, 16), 6)
    # almohada vista desde arriba: esquinas en punta y bordes curvos
    cx0, cy0, aw, ah = 540, 720, 400, 270
    pts = []
    for lado in range(4):
        for j in range(12):
            u = j / 12
            if lado == 0:
                x, y = -aw + 2 * aw * u, -ah + 34 * math.sin(math.pi * u)
            elif lado == 1:
                x, y = aw - 34 * math.sin(math.pi * u), -ah + 2 * ah * u
            elif lado == 2:
                x, y = aw - 2 * aw * u, ah - 34 * math.sin(math.pi * u)
            else:
                x, y = -aw + 34 * math.sin(math.pi * u), ah - 2 * ah * u
            pts.append((cx0 + x, cy0 + y))
    K.poligono(L, [(x + 10, y + 26) for x, y in pts], (6, 8, 12, 160))
    K.poligono(L, pts, (204, 210, 222), (8, 10, 16), 6)
    K.elipse(L, cx0, cy0 + 10, aw * 0.72, ah * 0.62, (220, 226, 236))
    for s_ in (-1, 1):
        L.d.line([L.pt(cx0 + s_ * aw * 0.92, cy0 - ah * 0.9), L.pt(cx0 + s_ * aw * 0.7, cy0 - ah * 0.6)], fill=(160, 166, 180), width=int(L.S(4)))
        L.d.line([L.pt(cx0 + s_ * aw * 0.92, cy0 + ah * 0.9), L.pt(cx0 + s_ * aw * 0.7, cy0 + ah * 0.6)], fill=(160, 166, 180), width=int(L.S(4)))
    K.poligono(L, [(-20, 1000), (1100, 960), (1100, 1960), (-20, 1960)], (58, 66, 96), (8, 10, 16), 6)
    for i in range(4):
        L.d.line([L.pt(80 + i * 260, 1000), L.pt(140 + i * 260, 1900)], fill=(46, 52, 78), width=int(L.S(6)))
    random.seed(3)
    for i in range(8):
        e = clamp((t - t0 - 0.22 * i) / 1.8)
        if e > 0:
            x, y = random.uniform(380, 700), random.uniform(600, 820)
            K.elipse(L, x, y, 40 + 90 * e, 22 + 50 * e, (110, 118, 142, int(210 * e)))
    for i in range(3):
        u = ((t - t0) * 0.7 + i / 3) % 1.0
        K.circulo(L, 470 + i * 70, 640 + 300 * u, 10, (170, 190, 220, int(230 * (1 - u))))


def carta(L, cx, cy, w, h, ang, quema, t, semilla):
    """Hoja con trazos de escritura vertical; `quema` 0..1 = cuánto se quemó desde abajo."""
    ca, sa = math.cos(ang), math.sin(ang)

    def P_(px, py):
        return (cx + px * ca - py * sa, cy + px * sa + py * ca)
    lim = h / 2 - quema * h * 1.05
    K.poligono(L, [P_(-w / 2, -h / 2), P_(w / 2, -h / 2), P_(w / 2, max(-h / 2, lim)), P_(-w / 2, max(-h / 2, lim))], CREMA, (60, 50, 40), 3)
    random.seed(semilla)
    for c in range(6):
        px = w / 2 - 40 - c * (w - 80) / 5.5
        y = -h / 2 + 50
        while y < min(h / 2 - 40, lim - 20):
            l = random.uniform(20, 60)
            K.linea(L, [P_(px, y), P_(px + random.uniform(-6, 6), min(y + l, lim - 20))], (40, 34, 30), 5)
            y += l + random.uniform(8, 20)
    if 0 < quema < 1.02:
        pts_b = []
        for i in range(13):
            px = -w / 2 + i * w / 12
            py = lim + 14 * math.sin(i * 1.7 + t * 9)
            pts_b.append(P_(px, py))
        K.linea(L, pts_b, (40, 20, 10), 22)
        K.linea(L, pts_b, (230, 120, 40), 8)
        for i in range(12):
            px = -w / 2 + (i + 0.5) * w / 12
            hh = 50 + 40 * math.sin(t * 13 + i * 2.1)
            b = P_(px, lim); tp = P_(px + 10 * math.sin(t * 7 + i), lim - hh)
            l1 = P_(px - 26, lim); l2 = P_(px + 26, lim)
            K.poligono(L, [l1, tp, l2], (255, 150, 40, 200))
            K.poligono(L, [P_(px - 12, lim), P_(px + 3 * math.sin(t * 9 + i), lim - hh * 0.55), P_(px + 12, lim)], (255, 230, 120, 230))


def brasas(L, t, n=40):
    random.seed(8)
    for i in range(n):
        x0, v, f = random.uniform(100, 980), random.uniform(80, 200), random.uniform(1, 3)
        y = 1900 - ((t * v + i * 97) % 1900)
        x = x0 + 30 * math.sin(t * f + i)
        K.circulo(L, x, y, random.uniform(3, 7), (255, random.randint(120, 200), 60, int(200 * (y / 1900))))


# ------------------------------------------------------------------ planos
CHIRAN = os.path.join(TEX_E, "foto_chiran.jpg")


@dib
def p1(L, t, a, b):
    pegar_foto(L, CHIRAN, 540, 640, 1110, rot=-0.8)
    etiqueta(L, "FOTO REAL · CHIRAN, JAPÓN · 12 DE ABRIL DE 1945", 540, 205, 26)
    rama_esquina(L, t)
    petalos(L, t, 55)


@dib
def p2(L, t, a, b):
    pegar_foto(L, CHIRAN, 540, 640, 1040, crop=(0.24, 0.17, 0.72, 0.62), rot=0.6, borde=True)
    rama_esquina(L, t)
    petalos(L, t, 60)


@dib
def p3(L, t, a, b):
    jp(L, "桜", 540, 1560, 520, (56, 38, 44), 255)
    rama(L, -60, 960, 1.35, t, t_cae=tw("cae") - 0.1)
    petalos(L, t, 25)


@dib
def p4(L, t, a, b):
    pegar_foto(L, os.path.join(TEX_10, "foto_teniente.jpg"), 540, 640, 1060, rot=0.7)
    etiqueta(L, "FOTO REAL", 150, 230, 26)
    rama_esquina(L, t)
    petalos(L, t, 40)


@dib
def p5(L, t, a, b):
    pegar_foto(L, os.path.join(TEX_10, "foto_choshi.jpg"), 540, 640, 1060, rot=-0.6)
    etiqueta(L, "FOTO REAL", 150, 230, 26)
    rama_esquina(L, t)
    petalos(L, t, 45)


@dib
def p6(L, t, a, b):
    ohka(L, 560, 760, 900, t, flor_u=(t - tw("flores", 19) + 0.1) / 0.35)
    jp(L, "桜", 880, 1500, 300, (60, 40, 46), 255)
    petalos(L, t, 18)


@dib
def p7(L, t, a, b):
    tf = tw("Flor", 23.5)
    u = clamp((t - tf + 0.15) / 0.5)
    jp(L, "桜花", 540, 640, 330, (238, 164, 182), int(255 * u))
    if u > 0.3:
        K.texto(L, "ŌKA = «FLOR DE CEREZO»", 540, 900, 50, CREMA)
    ohka(L, 540, 1500, 560, t, flor_u=1.0)
    petalos(L, t, 22)


@dib
def p8(L, t, a, b):
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=(26, 22, 30))
    td = tw("dioses")
    luz = clamp((t - td + 0.3) / 0.6)
    if luz > 0:
        for i in range(14):
            ang = -math.pi / 2 + (i - 6.5) * 0.12
            K.poligono(L, [(540, 760), (540 + 1500 * math.cos(ang - 0.03), 760 + 1500 * math.sin(ang - 0.03)),
                           (540 + 1500 * math.cos(ang + 0.03), 760 + 1500 * math.sin(ang + 0.03))], (255, 214, 140, int(60 * luz)))
        K.circulo(L, 540, 760, 220, (255, 220, 150, int(120 * luz)))
    cerezo(L, 120, 1500, 900, t, 2)
    cerezo(L, 960, 1500, 860, t, 5)
    torii(L, 540, 1500, 1000, t)
    L.d.rectangle((0, L.S(1500), L.S(W), L.S(H)), fill=(34, 30, 34))
    jp(L, "靖国神社", 960, 300, 64, CREMA, 220, vertical=True)
    K.texto(L, "YASUKUNI", 540, 1640, 44, CREMA)
    petalos(L, t, 45)


@dib
def p9(L, t, a, b):
    pegar_foto(L, os.path.join(TEX_10, "foto_impresa.jpg"), 540, 620, 740, rot=1.0)
    etiqueta(L, "FOTO REAL", 200, 200, 26)
    petalos(L, t, 30)


@dib
def p10(L, t, a, b):
    pegar_foto(L, os.path.join(TEX_10, "foto_alumna.jpg"), 540, 650, 1060, rot=-0.7)
    etiqueta(L, "FOTO REAL · LAS CHICAS DE CHIRAN", 540, 205, 26)
    petalos(L, t, 20)


@dib
def p11(L, t, a, b):
    cuarto_noche(L, t, a + 0.3)


@dib
def p12(L, t, a, b):
    pegar_foto(L, CHIRAN, 540, 640, 1040, crop=(0.5, 0.06, 0.94, 0.47), rot=-0.5, borde=True)
    if t > a + 0.5:
        etiqueta(L, "TOSHIO ANAZAWA · 23 AÑOS", 540, 1290, 34)
    petalos(L, t, 25)


@dib
def p13(L, t, a, b):
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=(18, 14, 14))
    q = clamp((t - a - 0.2) / (b - a + 1.2))
    carta(L, 380, 820, 420, 640, -0.12, q * 0.9, t, 1)
    carta(L, 700, 900, 420, 640, 0.10, q, t, 2)
    brasas(L, t, int(10 + 40 * q))
    if t > tw("novia") - 0.1:
        etiqueta(L, "LAS CARTAS DE SU NOVIA", 540, 1300, 32)


@dib
def p14(L, t, a, b):
    L.d.rectangle((0, 0, L.S(W), L.S(H)), fill=(18, 14, 14))
    brasas(L, t, 50)
    lineas = [("«Mientras ardían,", tw("mientras", 42)), ("se me estremeció", tw("se", 43.5)), ("el corazón.»", tw("el", 44.3))]
    f = ImageFont.truetype(JP, int(L.S(104)))
    for i, (s, ts) in enumerate(lineas):
        u = clamp((t - ts + 0.05) / 0.35)
        if u > 0:
            L.d.text(L.pt(540, 700 + i * 160), s, font=f, fill=(255, 244, 226, int(255 * u)), anchor="mm", stroke_width=int(L.S(1)), stroke_fill=(255, 244, 226, int(255 * u)))
    if t > tw("corazón", 44) + 0.3:
        K.texto(L, "— TOSHIO ANAZAWA", 540, 1240, 40, ROSA)


@dib
def p15(L, t, a, b):
    pegar_foto(L, CHIRAN, 540, 640, 1110, rot=-0.8)
    rama_esquina(L, t)
    petalos(L, t, 70)
    tf = tw("flor", 47)
    if t > tf:
        u = sale((t - tf) / 0.5)
        flor(L, 540, 1470, 120 * u, t)


FUN = {i: globals()[f"p{i}"] for i in range(1, 16)}
assert len(FUN) == len(T)

# ------------------------------------------------------------------ subtítulos
def limpiar(w):
    for ch in ",.:;!¡?¿\"…«»":
        w = w.replace(ch, "")
    return w.upper()


TOK = [(limpiar(x["w"]), [i], x["w"][-1] in ".,:;?…") for i, x in enumerate(words)]
GRUPOS = """ESTAS CHICAS DESPIDEN | A UN PILOTO KAMIKAZE | QUE VA A MORIR | Y LO DESPIDEN | CON FLORES | ESAS FLORES EXPLICAN |
POR QUÉ LOS KAMIKAZES | PARECÍAN NO TENERLE | MIEDO A LA MUERTE | SON RAMAS DE CEREZO | UNA FLOR QUE SE CAE | CUANDO ESTÁ MÁS LINDA |
Y JAPÓN LES ENSEÑÓ | A SUS SOLDADOS | QUE ELLOS ERAN | ESA FLOR | QUE LO MÁS HERMOSO | ERA CAER JÓVENES | POR SU PAÍS |
HASTA PINTABAN | FLORES DE CEREZO | EN SUS BOMBAS | Y A UNA BOMBA | CON PILOTO | LA LLAMARON ASÍ | FLOR DE CEREZO |
Y LES PROMETIERON | UN PREMIO | AL MORIR | SE CONVERTIRÍAN | EN DIOSES | POR ESO SUBÍAN | A SUS AVIONES | SONRIENDO |
PERO ESTAS MISMAS | CHICAS | LES LAVABAN LA ROPA | Y SUS FUNDAS | DE ALMOHADA | ESTABAN EMPAPADAS | DE LÁGRIMAS |
EL PILOTO | DE ESTA FOTO | TENÍA VEINTITRÉS AÑOS | ANTES DE DESPEGAR | QUEMÓ SUS CARTAS | LAS ÚLTIMAS | ERAN DE SU NOVIA |
Y ESCRIBIÓ | MIENTRAS ARDÍAN | SE ME ESTREMECIÓ | EL CORAZÓN | NO ES QUE NO | TUVIERAN MIEDO | LO ESCONDÍAN | DETRÁS DE UNA FLOR"""
grupos, _j = [], 0
for g in [g.split() for g in GRUPOS.replace("\n", " ").split("|") if g.strip()]:
    idx = list(range(_j, _j + len(g)))
    assert [TOK[j][0] for j in idx] == g, (g, [TOK[j][0] for j in idx])
    grupos.append(idx); _j += len(g)
assert _j == len(TOK), (_j, len(TOK))
V.TOK, V.grupos, V.words = TOK, grupos, words
V.CLAVE.update({w: ROSA for w in ("FLOR", "FLORES", "CEREZO", "LÁGRIMAS", "DIOSES", "MIEDO")})


def cuadro(f):
    t = (f - 1) / FPS
    k = plano_de(t)
    a, b = T[k]
    im = FUN[k](t, a, b)
    if not V._GRANO:
        V._GRANO["g"] = Image.effect_noise((W, H), 22).convert("RGB")
    im = Image.blend(im, Image.composite(im, V._GRANO["g"], Image.new("L", (W, H), 230)), 0.3)
    if k != 14 or t < tw("mientras", 42) - 0.05:
        V.subtitulos(im, t)
    return im


if __name__ == "__main__":
    dst = sys.argv[1]
    os.makedirs(dst, exist_ok=True)
    a = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    b = int(sys.argv[3]) if len(sys.argv) > 3 else FIN
    for f in range(a, b + 1):
        cuadro(f).save(os.path.join(dst, f"{f:05d}.png"), compress_level=1)
    print("ok", a, b)
