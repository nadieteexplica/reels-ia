"""Post del Ep. 3: arma los cuadros finales (1080x1920) desde los renders de plano.py.

Uso: python3 post.py <carpeta_render> <salida>   (OUT=carpeta de datos, LISTA=cuadros opcionales, MUESTRAS=1 en pruebas)
- Píldoras, contadores, ✕/✓, flechas de peso, huellas, rieles/curva/ángulo del mapa, barras "tú vs. edificio",
  barrido del 31, brillo y los subtítulos palabra por palabra (franja y 1000–1250).
- Las cifras dichas en palabras se muestran con dígitos ("ciento noventa y ocho" → 198): el bloque dura lo que duran
  sus palabras y se registra para cada una (subs_log.json → la tabla de subtítulos del auditor sigue calzando).
- Escribe subs_log.json, graficos.json y ep03_planos.json en OUT.
"""
import glob, json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "../../../plantilla")))
import ep03 as E
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
PATA_A = (255, 176, 0)             # grupo A (patas amarillas)
PATA_B = (70, 175, 255)            # grupo B (patas celestes)
ROJO = (236, 60, 48)
VERDE = (60, 200, 110)
CLAVE = {"CAMINANDO": PATA_B, "198": PATA_A, "18": ROJO, "DÍAS": ROJO}
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


def huella(im, cx, cy, col, izq=True, s=1.0):
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    k = -1 if izq else 1
    d.ellipse((cx - 34 * s, cy - 70 * s, cx + 34 * s, cy + 30 * s), fill=(*col, 235))
    d.ellipse((cx - 28 * s, cy + 40 * s, cx + 28 * s, cy + 92 * s), fill=(*col, 235))
    for j in range(5):
        d.ellipse((cx + k * (-30 + 14 * j) * s - 8 * s, cy - 96 * s - (6 - abs(j - 2) * 3) * s, cx + k * (-30 + 14 * j) * s + 8 * s, cy - 80 * s), fill=(*col, 235))
    im.paste(lay, (0, 0), lay)
    G.registrar("huella", (cx - 40 * s, cy - 100 * s, cx + 40 * s, cy + 95 * s))


def barra(im, y, texto, frac, col, etiqueta_der):
    d = ImageDraw.Draw(im, "RGBA")
    x0, x1, h = 130, 950, 84
    f = ImageFont.truetype(FONT, 60)
    d.text((x0, y - 78), texto, font=f, fill=(255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))
    d.rounded_rectangle((x0, y, x1, y + h), radius=h / 2, fill=(20, 20, 24, 200))
    if frac > 0.003:
        d.rounded_rectangle((x0, y, x0 + max(h, (x1 - x0) * frac), y + h), radius=h / 2, fill=(*col, 255))
    fr = ImageFont.truetype(FONT, 50)
    d.text((x1 - fr.getlength(etiqueta_der) - 24, y + 14), etiqueta_der, font=fr, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))
    G.registrar("barra", (x0, y - 80, x1, y + h))


def linea_puntos(im, pts, col, ancho=9, paso=34):
    d = ImageDraw.Draw(im)
    acc = 0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(L / paso * 2))
        for i in range(n):
            if (acc + i) % 2 == 0:
                a, b = i / n, (i + 1) / n
                d.line((x0 + (x1 - x0) * a, y0 + (y1 - y0) * a, x0 + (x1 - x0) * b, y0 + (y1 - y0) * b), fill=col, width=ancho)
        acc += n


def barrido(im, fuerza):
    """Barrido vertical (whip): mezcla copias corridas hacia abajo."""
    if fuerza <= 0.01:
        return im
    a = np.asarray(im).astype(np.float32)
    acc = np.zeros_like(a)
    n = 9
    for i in range(n):
        acc += np.roll(a, int(fuerza * 260 * i / n), axis=0)
    return Image.fromarray(np.clip(acc / n, 0, 255).astype(np.uint8))


# ---------------- subtítulos (palabra por palabra; cifras juntas) ----------------
NUMEROS = [("mil novecientos treinta y cinco", "1935"), ("siete mil seiscientas", "7.600"), ("dos mil veinte", "2020"),
           ("ciento noventa y ocho", "198"), ("veintiún", "21"), ("sesenta y dos", "62"), ("dieciocho", "18"),
           ("dos mil tres", "2003"), ("ochenta y cinco", "85")]


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


def graficos(im, f, k):
    age = edad(f, k)
    dur = E.T[k][1] - E.T[k][0]
    if k in (2, 3):                      # el guion lo promete: los pasos van acelerados
        pildora(im, "CÁMARA RÁPIDA", 540, 300, fondo=(28, 30, 36), tinta=(255, 255, 255), tam=40,
                s=pop(edad(f, 2, 0.15)) if k == 2 else 1.0)
    if k == 5:
        pildora(im, "ESCUELA LAGENA", 540, 360, s=pop(age - 0.1))
    elif k == 7:
        pildora(im, "SHANGHÁI · CHINA", 540, 340, s=pop(age - 0.05))
    elif k == 8:
        n = meta(8, f, "contador", 0) or 0
        pildora(im, f"{n:,}".replace(",", ".") + " t", 540, 390, s=pop(age), tam=96, tipo="contador")
    elif k == 9:
        pildora(im, "2020", 540, 340, fondo=(28, 30, 36), tinta=(255, 255, 255), s=pop(age - 0.05))
    elif k == 10:
        pildora(im, "OFICINAS + TIENDAS", 540, 360, fondo=(60, 140, 230), tinta=(255, 255, 255), s=pop(t_de(f) - E.t_palabra("oficinas", E.T[10][0] - 0.3)))
    elif k == 11:
        pildora(im, "DEMOLER", 540, 360, fondo=ROJO, tinta=(255, 255, 255), s=pop(age - 0.45), marca="x")
    elif k == 12:
        pildora(im, "MOVER", 540, 360, fondo=VERDE, tinta=(255, 255, 255), s=pop(age - 0.05), marca="v")
    elif k == 14:
        n = round(198 * E.sale(min(1.0, max(0.0, age - 0.05) / (0.68 * dur))))     # llega a 198 y se queda ~0,5 s
        pildora(im, f"{n} PATAS", 540, 390, fondo=PATA_A, tinta=(20, 18, 10), s=pop(age), tam=96, tipo="contador")
    elif k in (18, 19, 20, 21):
        sa = pop(edad(f, 18, 0.15)) if k == 18 else 1.0
        sb = pop(edad(f, 18, 0.95)) if k == 18 else 1.0
        if k == 21:                      # "luego cambian": el énfasis pasa de A a B
            w = min(1.0, max(0.0, (t_de(f) - E.t_palabra("cambian", E.T[21][0] - 0.5) + 0.12) / 0.24))
            fa, fb = 1.0 - 0.25 * w, 0.75 + 0.25 * w
        else:
            fa, fb = (0.75 if k == 19 else 1.0), (0.75 if k == 20 else 1.0)
        pildora(im, "GRUPO A", 330, 360, fondo=PATA_A, tinta=(20, 18, 10), s=sa * fa)
        pildora(im, "GRUPO B", 760, 360, fondo=PATA_B, tinta=(8, 20, 36), s=sb * fb)
        if k == 19:
            for (x, y) in (meta(19, f, "pies_b", []) or [])[:5]:
                if 230 < y < 960:
                    flecha(im, x, max(240, y - 230), x, y - 40, PATA_B, 11)
        if k in (20, 21):
            pies = meta(k, f, "pies_a" if k == 20 else "pies_b", []) or []
            col = PATA_A if k == 20 else PATA_B
            if k == 21 and t_de(f) < E.t_palabra("cambian", E.T[21][0] - 0.5):
                pies = []
            for (x, y) in pies[:5]:
                if 620 < y < 960 and x < 980:          # bajo las píldoras: ningún gráfico pisa a otro
                    flecha(im, x - 40, y - 150, x + 70, y - 150, col, 12)
    elif k == 22:
        fase = meta(22, f, "fase", 0.0) or 0.0
        izq = fase < 0.5
        huella(im, 430, 885, PATA_A if izq else (90, 90, 90), True, 0.85 if izq else 0.7)      # en el suelo, delante de las patas
        huella(im, 650, 865, PATA_B if not izq else (90, 90, 90), False, 0.85 if not izq else 0.7)
    elif k in (25, 26, 27):
        rie = meta(k, f, "rieles", None)
        cam = meta(k, f, "camino", None)
        d = ImageDraw.Draw(im)
        if rie:
            u = 1.0 if k > 25 else min(1.0, age / 0.8)
            for (a_, b_) in ((rie[0], rie[1]), (rie[2], rie[3])):
                x0, y0 = a_
                x1, y1 = b_
                d.line((x0, y0, x0 + (x1 - x0) * u, y0 + (y1 - y0) * u), fill=(205, 205, 210), width=12)
            G.registrar("rieles", (min(p[0] for p in rie), min(p[1] for p in rie), max(p[0] for p in rie), max(p[1] for p in rie)))
        if cam and k >= 26:
            u = 1.0 if k > 26 else min(1.0, age / 0.7)
            n = max(2, int(len(cam) * u))
            linea_puntos(im, cam[:n], (255, 255, 255), 10)
        if k == 26:
            pildora(im, "RIELES", 540, 360, fondo=ROJO, tinta=(255, 255, 255), s=pop(age - 0.75), marca="x")
        if k == 27:
            g = meta(27, f, "giro", 0.0) or 0.0
            c = meta(27, f, "centro", (540, 900))
            R_ = 230          # el ángulo real (21°), con dos rayas: el rumbo de partida y el de ahora
            for ang, col in ((-90, (255, 255, 255)), (-90 + g, PATA_A)):
                d.line((c[0], c[1], c[0] + R_ * 1.15 * math.cos(math.radians(ang)), c[1] + R_ * 1.15 * math.sin(math.radians(ang))), fill=col, width=8)
            if g > 0.3:
                d.arc((c[0] - R_, c[1] - R_, c[0] + R_, c[1] + R_), start=-90, end=-90 + g, fill=PATA_A, width=14)
            G.registrar("angulo", (c[0] - R_ * 1.2, c[1] - R_ * 1.2, c[0] + R_ * 1.2, c[1]))
            pildora(im, f"{round(g):d}°", 540, 360, fondo=PATA_A, tinta=(20, 18, 10), s=pop(age), tam=96, tipo="contador")
    elif k == 28:
        m = 62 * E.sale(min(1.0, max(0.0, age - 0.05) / (0.70 * dur)))     # llega a 62 m mientras se dice y se queda
        pildora(im, f"{min(62, round(m)):d} m", 540, 370, fondo=(255, 200, 40), tinta=(20, 18, 10), s=pop(age), tam=96, tipo="contador")
    elif k == 29:
        dia = meta(29, f, "dia", 1) or 1
        pildora(im, f"DÍA {dia}", 540, 370, fondo=(28, 30, 36), tinta=(255, 255, 255), s=pop(age), tam=96, tipo="contador")
    elif k == 30:
        a = max(0.0, age - 0.1)
        barra(im, 340, "TÚ", min(1.0, a / 0.8), VERDE, "< 1 MIN")
        barra(im, 560, "EL EDIFICIO", min(0.04, 0.04 * a / dur), ROJO, "18 DÍAS")
    elif k in (32, 33):
        pildora(im, "2003", 540, 340, fondo=(28, 30, 36), tinta=(255, 255, 255), s=pop(edad(f, 32, 0.1)) if k == 32 else 1.0)
    elif k == 35 and t_de(f) >= E.t_palabra("ochenta", E.T[35][0]) - 0.05:
        pildora(im, "85 AÑOS", 540, 360, fondo=PATA_A, tinta=(20, 18, 10), tam=80, tipo="contador",
                s=pop(t_de(f) - E.t_palabra("ochenta", E.T[35][0]) + 0.05))
    if k == 33:
        m = meta(33, f, "metros", 0.0) or 0.0
        pildora(im, f"{m:.0f} m".replace(".", ","), 540, 470, s=pop(age), tam=80, tipo="contador")


def procesar(f):
    G.cuadro(f)
    k = plano_de(f)
    a, b = FR[k]
    im = cuadro(f, a, b)
    if im is None:
        return False
    if k == 31:
        im = barrido(im, max(0.0, (t_de(f) - E.T[31][0]) / (E.T[31][1] - E.T[31][0]) - 0.45) * 1.8)
    if k == 32 and t_de(f) - E.T[32][0] < 0.2:
        im = barrido(im, 1 - (t_de(f) - E.T[32][0]) / 0.2)
    im = bloom(im)
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
              open(os.path.join(OUT, "ep03_planos.json"), "w"))
    print("ok post", len(list(cuadros)) - len(faltan), "cuadros; faltan", len(faltan), faltan[:20])
