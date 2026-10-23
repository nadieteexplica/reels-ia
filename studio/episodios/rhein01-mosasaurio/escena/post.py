"""Post de Rhein 01: arma los cuadros finales (1080x1920) desde los renders de plano.py.

Uso: python3 post.py <carpeta_render> <salida>   (OUT=carpeta de datos, LISTA=cuadros opcionales, MUESTRAS=1 en pruebas)
- Contador "200 POLLOS" (plano 2), regla "12 M" (plano 5), brillo del radar y la energía (planos 18, 21, 29) y los
  subtítulos palabra por palabra (franja y 1000–1250). Las posiciones salen del meta de cada cuadro.
- Planos de metraje (30–36 y 38: tomas reales de Rhein): si METRAJE=<carpeta con los cuadros del video limpio de Rhein a
  30 fps> se usan esas tomas; si no, quedan en negro (así en Actions nunca se sube el video de Rhein al repo público).
- Escribe subs_log.json, graficos.json y rhein01_planos.json en OUT.
"""
import glob, json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "../../../plantilla")))
import rhein01 as E
import graficos as G

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
AMARILLO = (255, 210, 63)          # palabra activa (manual §6)
DORADO = (255, 170, 40)            # los pollos
VERDE_R = (60, 235, 110)           # el radar y la explosión (el verde de la portada)
ROJO = (236, 60, 48)
CLAVE = {"POLLOS": DORADO, "RADAR": VERDE_R, "MICRO": (255, 255, 255)}
METRAJE_PL = (30, 31, 32, 33, 34, 35, 38)
# plano → (segundo de inicio en el video limpio de Rhein); el plano 38 usa la placa del cierre (cierre_rhein.png)
FUENTE = {30: 9.40, 31: 3.65, 32: 12.75, 33: 11.30, 34: 0.60, 35: 15.40}
DIR_MET = os.environ.get("METRAJE")
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

# ---------------- subtítulos (palabra por palabra; cifras juntas) ----------------
NUMEROS = [("doscientos", "200")]


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
for _k in (32, 38):                     # planos de marca: el texto grande es la marca (silencio del título)
    _a, _b = E.FR(_k)
    SIN_SUBS.update(range(_a, _b))
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


def arco(im, cx, cy, r, ang0, col, ancho=12, largo=250):
    """Flecha curva (arco de `largo` grados) que gira con el remolino."""
    d = ImageDraw.Draw(im)
    a0, a1 = ang0, ang0 + largo
    d.arc((cx - r, cy - r, cx + r, cy + r), a0, a1, fill=col, width=ancho)
    ae = math.radians(a1)
    px, py = cx + r * math.cos(ae), cy + r * math.sin(ae)
    tx, ty = -math.sin(ae), math.cos(ae)          # tangente (sentido horario en pantalla)
    L = ancho * 2.6
    for s in (-1, 1):
        bx = px - L * (tx * math.cos(0.5) - s * ty * math.sin(0.5) * 0)
        d.line((px, py, px - L * tx + s * L * 0.55 * math.cos(ae), py - L * ty + s * L * 0.55 * math.sin(ae)), fill=col, width=ancho)
    G.registrar("flecha", (cx - r - ancho, cy - r - ancho, cx + r + ancho, cy + r + ancho))


def anillo(im, cx, cy, r, col, ancho=8):
    d = ImageDraw.Draw(im)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col, width=ancho)
    G.registrar("marca", (cx - r, cy - r, cx + r, cy + r))


def contador(im, f, k, hasta=200, texto="POLLOS"):
    a, b = FR[k]
    x = min(1.0, max(0.0, (f - a - 2) / max(1, (b - a) * 0.7)))
    n = int(round(hasta * (1 - (1 - x) ** 2)))
    pildora(im, f"{n} {texto}", 370, 370, fondo=DORADO, tinta=(40, 20, 0), tam=64, s=pop(edad(f, k) - 0.05), tipo="pildora")


def regla(im, f, k):
    pts = meta(k, f, "regla")
    if not pts:
        return
    (x0, y0), (x1, y1) = pts
    if abs(y1 - y0) > abs(x1 - x0):            # plano cenital: la regla va vertical, al lado de la micro
        x = max(80, min(1000, (x0 + x1) / 2))
        ya, yb = max(260, min(y0, y1)), min(980, max(y0, y1))
        p = sale(min(1.0, max(0.0, edad(f, k) - 0.35) / 0.4))
        if p <= 0:
            return
        ym = ya + (yb - ya) * p
        d = ImageDraw.Draw(im)
        d.line((x, ya, x, ym), fill=(255, 255, 255), width=8)
        for yy in (ya, ym):
            d.line((x - 24, yy, x + 24, yy), fill=(255, 255, 255), width=8)
        G.registrar("flecha", (x - 30, ya - 10, x + 30, ym + 10))
        if p > 0.9:
            xp = x + 130 if x < 540 else x - 130
            pildora(im, "12 M", xp, (ya + yb) / 2, tam=60, s=pop(edad(f, k) - 0.75))
        return
    y = max(300, min(600, (y0 + y1) / 2))
    x0, x1 = max(60, min(x0, x1)), min(1020, max(x0, x1))
    x = sale(min(1.0, max(0.0, edad(f, k) - 0.35) / 0.4))
    if x <= 0:
        return
    xm = x0 + (x1 - x0) * x
    d = ImageDraw.Draw(im)
    d.line((x0, y, xm, y), fill=(255, 255, 255), width=8)
    for xx in (x0, xm):
        d.line((xx, y - 24, xx, y + 24), fill=(255, 255, 255), width=8)
    G.registrar("flecha", (x0 - 10, y - 30, xm + 10, y + 30))
    if x > 0.9:
        pildora(im, "12 M", (x0 + x1) / 2, y - 80, tam=60, s=pop(edad(f, k) - 0.75))


def graficos(im, f, k):
    if k == 2:
        contador(im, f, k)
    elif k == 5:
        regla(im, f, k)


def metraje(f, k):
    a, b = FR[k]
    if k == 38:
        p = os.environ.get("CIERRE", "")          # la placa de Rhein no va al repo público: se pasa en local
        if not p or not os.path.exists(p):
            return Image.new("RGB", (W, H), (2, 0, 2))
        im = Image.open(p).convert("RGB")
        z = 1.0 + 0.05 * (f - a) / max(1, b - a)
        w2, h2 = int(W * z), int(H * z)
        im = im.resize((w2, h2), Image.LANCZOS).crop(((w2 - W) // 2, (h2 - H) // 2, (w2 - W) // 2 + W, (h2 - H) // 2 + H))
        return im
    if not DIR_MET:
        return Image.new("RGB", (W, H), (0, 0, 0))
    fs = int(round(FUENTE[k] * FPS)) + (f - a) + 1
    p = os.path.join(DIR_MET, f"{fs:05d}.png")
    if not os.path.exists(p):
        return Image.new("RGB", (W, H), (0, 0, 0))
    return Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS)


def procesar(f):
    G.cuadro(f)
    k = plano_de(f)
    a, b = FR[k]
    if k in METRAJE_PL:
        im = metraje(f, k)
    else:
        im = cuadro(f, a, b)
        if im is None:
            return False
        if k in (7, 11, 12, 13, 18, 21, 29):            # brillo en las flechas, las chispas y el radar
            im = bloom(im, umbral=0.80, fuerza=0.35 if k != 29 else 0.6)
        im = ImageEnhance.Color(im).enhance(1.12)
        im = ImageEnhance.Contrast(im).enhance(1.05)
        if k == 29:                                    # destello verde al final: estallido radial con rayos (no un fondo liso)
            x = max(0.0, (f - (b - 9)) / 9)
            if x > 0:
                yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
                cx, cy = W * 0.5, H * 0.46
                r = np.hypot(xx - cx, yy - cy) / H
                ang = np.arctan2(yy - cy, xx - cx)
                rayos = 0.55 + 0.45 * np.cos(ang * 14 + f * 0.7) ** 8
                inten = np.clip((1.2 * x) - r * (1.6 - x), 0, 1) * rayos
                base = np.asarray(im).astype(np.float32) / 255
                verde = np.array([0.55, 1.0, 0.62], np.float32)
                out = base * (1 - inten[..., None] * 0.9) + verde * inten[..., None] * 0.95
                im = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))
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
              open(os.path.join(OUT, "rhein01_planos.json"), "w"))
    print("ok post", len(list(cuadros)) - len(faltan), "cuadros; faltan", len(faltan), faltan[:20])
