"""Post del Ep. 6 (copiado del Ep. 5): arma los cuadros finales (1080x1920) desde los renders de plano.py.

Uso: python3 post.py <carpeta_render> <salida>   (OUT=carpeta de datos, LISTA=cuadros opcionales, MUESTRAS=1 en pruebas)
- Gradación común (grado.py), píldoras (SIN HILOS, IMÁN, AGUA, UN POQUITO, MILES DE VECES, SIMULACIÓN fija en la parte
  hipotética, ≈ 40 TESLAS, MÁS DEL DOBLE, ≈ 1 GIGAVATIO, 1 REACTOR NUCLEAR), flechas de fuerza al lado de la rana (gris =
  gravedad, naranja = imán) y del imán del refri, y los subtítulos palabra por palabra (franja y 1000–1250). Las
  posiciones salen del meta de cada cuadro (pantalla() de la escena).
- Escribe subs_log.json, graficos.json y ep05_planos.json en OUT.
"""
import glob, json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "../../../plantilla")))
import kit5 as E
import graficos as G
from grado import grado

OUT = os.environ.get("OUT", os.path.join(HERE, "out"))
src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
words = E.palabras()
FR = {k: E.FR(k) for k in E.T}
END = E.FIN
FONTS = os.path.abspath(os.path.join(HERE, "../../../plantilla/fonts"))
FONT = os.path.join(FONTS, "Inter-Black.otf")
FONT_B = os.path.join(FONTS, "Inter-ExtraBold.otf")
AMARILLO = (255, 210, 63)          # palabra activa (manual §6) y SIMULACIÓN
ROJO = (235, 60, 45)               # rápido / se traba (CLAC)
VERDE = (70, 200, 110)             # lento / te deja
CIAN = (40, 205, 255)              # el sensor del auto (la bolita)
NARANJO = (255, 140, 30)           # fuerzas (flechas)
AMBAR = (245, 170, 40)             # 12–27°: puede trabarse
GRIS = (150, 156, 166)
CLAVE = {"RÁPIDO": ROJO, "LENTO": VERDE, "27": ROJO, "CLAC": ROJO}
BOX = (120, 888, 1000, 1250)
META = {}
for p in sorted(glob.glob(os.path.join(src, "meta", "*.json"))):
    d = json.load(open(p))
    META.setdefault(str(d["pieza"]), {"cuadros": {}})["cuadros"].update(d.get("cuadros", {}))


def plano_de(f):
    for k, (a, b) in FR.items():
        if a <= f < b:
            return k
    return max(FR)


def t_de(f):
    return (f - 1) / FPS


def meta(k, f, clave, defecto=None):
    c = META.get(str(k), {}).get("cuadros", {})
    if str(f) in c and clave in c[str(f)]:
        return c[str(f)][clave]
    ks = [int(x) for x, v in c.items() if clave in v]
    if ks:
        return c[str(min(ks, key=lambda x: abs(x - f)))][clave]
    return defecto


def cargar(path):
    if not os.path.exists(path):
        return None
    im = Image.open(path).convert("RGB")
    return im.resize((W, H), Image.LANCZOS) if im.size != (W, H) else im


def cuadro(f, a, b):
    im = cargar(os.path.join(src, f"{f:05d}.png"))
    if im is not None or not os.environ.get("MUESTRAS"):
        return im
    cand = [int(os.path.basename(q)[:5]) for q in glob.glob(os.path.join(src, "[0-9]" * 5 + ".png"))]
    cand = [c for c in cand if a <= c < b]
    return cargar(os.path.join(src, f"{min(cand, key=lambda c: abs(c - f)):05d}.png")) if cand else None


def bloom(im, umbral=0.82, fuerza=0.45):
    a = np.asarray(im).astype(np.float32) / 255
    lum = a.max(axis=2)
    mask = np.clip((lum - umbral) / (1 - umbral), 0, 1)[..., None] * a
    g = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).resize((W // 4, H // 4)).filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BILINEAR)).astype(np.float32) / 255
    return Image.fromarray((np.clip(a + g * fuerza, 0, 1) * 255).astype(np.uint8))


def pop(age, dur=0.3):
    if age <= 0:
        return 0.0
    if age >= dur:
        return 1.0
    x = age / dur
    return 1 + 0.18 * math.sin(math.pi * x) * (1 - x) * 2 - (1 - x) ** 3


# ---------------- gráficos ----------------
def pildora(im, texto, cx, cy, fondo=(250, 250, 248), tinta=(24, 24, 28), s=1.0, tam=58, marca=None, tipo="pildora"):
    if s <= 0.02:
        return
    f = ImageFont.truetype(FONT, int(tam * s))
    tw = f.getlength(texto)
    extra = int(tam * 1.0 * s) if marca else 0
    w, h = tw + 64 * s + extra, tam * 1.45 * s
    x0, y0 = cx - w / 2, cy - h / 2
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x0 + 4, y0 + 7, x0 + w + 4, y0 + h + 7), radius=h / 2, fill=(0, 0, 0, 90))
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), radius=h / 2, fill=(*fondo, 245))
    tx = x0 + 32 * s + extra
    d.text((tx, cy - f.size * 0.60), texto, font=f, fill=tinta)
    if marca:
        mx, my, r = x0 + 32 * s + extra * 0.42, cy, tam * 0.34 * s
        if marca == "x":
            for dx in (-1, 1):
                d.line((mx - r, my - r * dx, mx + r, my + r * dx), fill=tinta, width=int(9 * s))
        else:
            d.line((mx - r, my, mx - r * 0.25, my + r * 0.75, mx + r, my - r * 0.8), fill=tinta, width=int(9 * s), joint="curve")
    im.paste(lay, (0, 0), lay)
    G.registrar(tipo, (x0, y0, x0 + w, y0 + h))


def flecha(im, x0, y0, x1, y1, col, ancho=10):
    d = ImageDraw.Draw(im)
    d.line((x0, y0, x1, y1), fill=col, width=ancho)
    a = math.atan2(y1 - y0, x1 - x0)
    L = ancho * 2.6
    for s in (-1, 1):
        d.line((x1, y1, x1 - L * math.cos(a + s * 0.5), y1 - L * math.sin(a + s * 0.5)), fill=col, width=ancho)
    G.registrar("flecha", (min(x0, x1) - 12, min(y0, y1) - 12, max(x0, x1) + 12, max(y0, y1) + 12))




def sale(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def suave(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)

# ---------------- subtítulos (palabra por palabra; cifras juntas) ----------------
NUMEROS = [("veintisiete", "27")]        # "27° GRADOS" repetía el grado (puerta 6 r1, B10)


def limpiar(w):
    w = w.replace("...", "").replace("…", "")
    for ch in ",.:;!¡?¿\"":
        w = w.replace(ch, "")
    return w.upper()


TOK = []          # [(texto en pantalla, [índices de palabras], fin de frase)]
i = 0
while i < len(words):
    hecho = False
    for frase, cifra in NUMEROS:
        n = len(frase.split())
        bloque = [limpiar(x["w"]).lower() for x in words[i:i + n]]
        if bloque == [limpiar(x).lower() for x in frase.split()]:
            TOK.append((cifra, list(range(i, i + n)), words[i + n - 1]["w"][-1] in ",.:;!?…"))
            i += n
            hecho = True
            break
    if not hecho:
        TOK.append((limpiar(words[i]["w"]), [i], words[i]["w"][-1] in ",.:;!?…" or words[i]["w"].endswith("...")))
        i += 1

grupos, cur = [], []
for j, (tx, idx, fin) in enumerate(TOK):
    cur.append(j)
    nxt = TOK[j + 1][1][0] if j + 1 < len(TOK) else None
    if len(cur) == 3 or fin or (nxt is not None and words[nxt]["s"] - words[idx[-1]]["e"] > 0.3):
        grupos.append(cur)
        cur = []
if cur:
    grupos.append(cur)
g2 = []
for g in grupos:
    if any(len(TOK[j][0]) >= 11 for j in g) and len(g) > 1:
        g2 += [[j] for j in g]
    else:
        g2.append(g)
grupos = g2
SIN_SUBS = set()
SUB_LOG = []


def s_tok(j):
    return words[TOK[j][1][0]]["s"]


def e_tok(j):
    return words[TOK[j][1][-1]]["e"]


def tam(tok, font):
    return int(font.size * 1.10) if tok in CLAVE else font.size


def gap(font, a, b):
    return font.getlength(" ") + 0.07 * (font.getlength(a) + font.getlength(b))


def ancho(font, toks):
    return sum(ImageFont.truetype(FONT, tam(t, font)).getlength(t) for t in toks) + sum(gap(font, toks[i], toks[i + 1]) for i in range(len(toks) - 1))


def diagramar(g):
    toks = [TOK[j][0] for j in g]
    maxw = (BOX[1] - BOX[0]) / 1.12
    splits = [[toks]]
    if len(toks) > 1:
        c = len(toks) // 2 + len(toks) % 2
        splits.append([toks[:c], toks[c:]])
    for lo in (76, 60):
        for lines in splits:
            for size in range(84, lo - 1, -4):
                f = ImageFont.truetype(FONT, size)
                if all(ancho(f, l) <= maxw for l in lines):
                    return f, lines
    return ImageFont.truetype(FONT, 60), splits[-1]


def subtitulos(img, f):
    if f in SIN_SUBS:
        return
    t = t_de(f)
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
    font, lines = diagramar(g)
    d = ImageDraw.Draw(img, "RGBA")
    lh = font.size * 1.12
    y0 = (BOX[2] + BOX[3]) / 2 - lh * len(lines) / 2
    cx = (BOX[0] + BOX[1]) / 2
    k = 0
    for li, line in enumerate(lines):
        x = cx - ancho(font, line) / 2
        y = y0 + li * lh
        for ti, tok in enumerate(line):
            j = g[k]
            k += 1
            fb = ImageFont.truetype(FONT, tam(tok, font))
            yy = y - (fb.size - font.size) / 2
            activo = s_tok(j) - 0.02 <= t < max(e_tok(j), s_tok(j) + 0.12)
            tw = fb.getlength(tok)
            col = CLAVE.get(tok, (255, 255, 255))
            if activo:
                age = t - s_tok(j)
                sc = 1.0 + 0.12 * max(0.0, 1 - abs(age - 0.06) / 0.06) if age < 0.12 else 1.0
                fnt = ImageFont.truetype(FONT, int(fb.size * sc))
                ox, oy = (fnt.getlength(tok) - tw) / 2, (fnt.size - fb.size) / 2
                d.text((x - ox + 3, yy - oy + 5), tok, font=fnt, fill=(0, 0, 0, 110))
                d.text((x - ox, yy - oy), tok, font=fnt, fill=AMARILLO if tok not in CLAVE else col, stroke_width=6, stroke_fill=(0, 0, 0))
                caja = (x - ox, yy - oy, x - ox + fnt.getlength(tok), yy - oy + fnt.size)
            else:
                d.text((x + 3, yy + 5), tok, font=fb, fill=(0, 0, 0, 110))
                d.text((x, yy), tok, font=fb, fill=col, stroke_width=6, stroke_fill=(0, 0, 0))
                caja = (x, yy, x + tw, yy + fb.size)
            for wi in TOK[j][1]:
                SUB_LOG.append((f, limpiar(words[wi]["w"]), *caja, wi))
            x += tw + (gap(font, tok, line[ti + 1]) if ti + 1 < len(line) else 0)


# ---------------- gráficos por plano ----------------
def edad(f, k, desde=0.0):
    return t_de(f) - E.T[k][0] - desde


def tw(prefijo, desde=0.0):
    return E.t_palabra(prefijo, desde)


def inclinometro(im, grados, cx=250, cy=380, r=120, bandas=False, s=1.0):
    """Dial del inclinómetro (vista de costado del auto que se inclina). Con bandas: 12–27° ámbar (PUEDE) y más de 27°
    rojo (SE TRABA), como pidió la puerta 3."""
    if s <= 0.02:
        return
    r = r * s
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.ellipse((cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10), fill=(18, 18, 22, 200))
    def arco(g0, g1, col, w):
        d.arc((cx - r, cy - r, cx + r, cy + r), start=180 + g0 * 2, end=180 + g1 * 2, fill=col, width=int(w))
    arco(0, 12, (200, 200, 205, 255), 14 * s)
    if bandas:
        arco(12, 27, (*AMBAR, 255), 18 * s); arco(27, 45, (*ROJO, 255), 22 * s)
        fb = ImageFont.truetype(FONT, int(30 * s))
        d.text((cx - r * 0.95, cy + r * 0.28), "PUEDE", font=fb, fill=(*AMBAR, 255))
        d.text((cx - r * 0.10, cy + r * 0.28), "SE TRABA", font=fb, fill=(*ROJO, 255))
    else:
        arco(12, 45, (200, 200, 205, 120), 10 * s)
    a = math.radians(180 + grados * 2)
    d.line((cx, cy, cx + math.cos(a) * r * 0.92, cy + math.sin(a) * r * 0.92), fill=(255, 255, 255, 255), width=int(9 * s))
    d.ellipse((cx - 12 * s, cy - 12 * s, cx + 12 * s, cy + 12 * s), fill=(255, 255, 255, 255))
    f = ImageFont.truetype(FONT, int(54 * s))
    txt = f"{int(round(grados))}°"
    d.text((cx - f.getlength(txt) / 2, cy - r * 0.62), txt, font=f, fill=(255, 255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0, 255))
    im.paste(lay, (0, 0), lay)
    G.registrar("contador", (cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10))


def graficos(im, f, k):
    t = t_de(f)
    if k == 3:
        t0 = T0(3) + 0.8
        if t > t0:
            pildora(im, "LENTO", 300, 360, fondo=VERDE, tinta=(255, 255, 255), s=pop(t - t0))
    elif k == 5:
        t0 = tw("carrete", 6.0)
        if t > t0:
            pildora(im, "CARRETE", 540, 425, s=pop(t - t0))
    elif k == 7:
        t0 = T0(7) + 0.2
        if t > t0:
            L = 140 + 60 * suave(min(1, (t - t0) / 1.2))
            flecha(im, 860, 640, 860, 640 - L, ROJO, ancho=14)
    elif k == 8:
        t0 = T0(8) + 0.6
        if t > t0:
            pildora(im, "FUERZA DEL GIRO", 540, 425, fondo=NARANJO, tinta=(255, 255, 255), s=pop(t - t0))
            L = 150 * sale(min(1, (t - t0) / 0.4))
            flecha(im, 640, 760, 640 + L, 760 - L * 0.4, NARANJO, ancho=14)
    elif k == 11:
        t0 = T0(11) + 0.2
        if t > t0:
            flecha(im, 860, 640, 860, 640 - 70 * sale(min(1, (t - t0) / 0.3)), VERDE, ancho=8)
    elif k in (13, 21):
        g = meta(k, f, "inclinacion", 0.0) or 0.0
        inclinometro(im, max(0.0, g), cx=250, cy=400, r=95)
    elif k == 17:
        t0 = tw("bolita", 22.0)
        if t > t0:
            pildora(im, "BOLITA DE ACERO", 540, 425, fondo=CIAN, tinta=(10, 30, 40), s=pop(t - t0))
    elif k == 18:
        pildora(im, "TAMBIÉN EN FRENADAS", 540, 390, tam=40, s=pop(t - T0(18)))
        t0 = T0(18) + 0.6
        if t > t0:
            flecha(im, 420, 900, 420, 900 - 110 * sale(min(1, (t - t0) / 0.3)), CIAN, ancho=12)
    elif k == 19:
        tv = tw("veintisiete", 26.0)
        g = 12 + 15 * suave(min(1, (t - T0(19)) / max(0.3, tv - T0(19)))) if t < tv else 27 + 3 * suave(min(1, (t - tv) / 0.5))
        inclinometro(im, g, cx=540, cy=470, r=150, bandas=True)
    elif k == 22:
        t0 = T0(22) + 0.4
        if t > t0:
            flecha(im, 420, 520, 420 - 70 * sale(min(1, (t - t0) / 0.3)), 520 - 70 * sale(min(1, (t - t0) / 0.3)), VERDE, ancho=10)
    elif k == 23:
        pildora(im, "LENTO", 540, 310, fondo=VERDE, tinta=(255, 255, 255), s=pop(t - T0(23)))


def T0(k):
    return E.T[k][0]


def procesar(f):
    G.cuadro(f)
    k = plano_de(f)
    a, b = FR[k]
    im = cuadro(f, a, b)
    if im is None:
        return False
    im = grado(im)                                            # la misma gradación de los cuadros de estilo (grado.py)
    graficos(im, f, k)
    subtitulos(im, f)
    im.save(os.path.join(dst, f"{f:05d}.png"), compress_level=1)
    return True


if __name__ == "__main__":
    cuadros = range(1, END)
    lista = os.environ.get("LISTA")
    if lista:
        cuadros = [int(v) for v in lista.split(",")]
    faltan = [f for f in cuadros if not procesar(f)]
    json.dump(SUB_LOG, open(os.path.join(OUT, "subs_log.json"), "w"))
    G.guardar(os.path.join(OUT, "graficos.json"))
    json.dump({"T": {str(k): list(v) for k, v in E.T.items()}, "FR": {str(k): list(v) for k, v in FR.items()}, "END": END},
              open(os.path.join(OUT, "ep06_planos.json"), "w"))
    print("ok post", len(list(cuadros)) - len(faltan), "cuadros; faltan", len(faltan), faltan[:20])
