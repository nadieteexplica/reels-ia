"""Post del Ep. 2: arma los cuadros finales (1080x1920) desde los renders de plano.py.

Uso: python3 post.py <carpeta_render> <salida> [a-b]
- carpeta_render: NNNNN.png (planos), aux/<pieza>_NNNNN.png (lupas y recuadros), meta/<pieza>.json
- Compone los recuadros (14–16, 31), los "y si…" (23, 24), el marco REC (21–22), el whip (28), píldoras, contador,
  marcas ✓ ✕ y los subtítulos palabra por palabra (franja y 1000–1250). Escribe subs_log.json y ep02_planos.json en OUT.
"""
import glob, json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ep02 as E2

EPI = E2.EPI
OUT = os.environ.get("OUT", os.path.join(HERE, "out"))
src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)
os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
words = E2.palabras()
FR = {k: E2.FR(k) for k in E2.T}
END = E2.FIN
FONTS = os.path.abspath(os.path.join(HERE, "../../../plantilla/fonts"))
FONT = os.path.join(FONTS, "Inter-Black.otf")
FONT_B = os.path.join(FONTS, "Inter-ExtraBold.otf")
AMARILLO = (255, 210, 63)
ROJO = (236, 52, 38)
CANELA = (214, 140, 72)
CELESTE = (110, 200, 255)
CLAVE = {"CAPSAICINA": ROJO, "MAMÍFEROS": CANELA, "LECHE": CELESTE}
BOX = (120, 888, 1000, 1250)
META = {}
for p in glob.glob(os.path.join(src, "meta", "*.json")):
    d = json.load(open(p))
    META[d["pieza"]] = d


def plano_de(f):
    for k, (a, b) in FR.items():
        if a <= f < b:
            return k
    return 40


def t_de(f):
    return (f - 1) / FPS


def F(t):
    return E2.F(t)


def meta_cuadro(pieza, f, clave, defecto=None):
    m = META.get(pieza, {})
    c = m.get("cuadros", {})
    if str(f) in c and clave in c[str(f)]:
        return c[str(f)][clave]
    if c:   # el cuadro más cercano que tenga el dato
        ks = [int(k) for k, v in c.items() if clave in v]
        if ks:
            k = min(ks, key=lambda x: abs(x - f))
            return c[str(k)][clave]
    return m.get(clave, defecto)


_cache = {}


def cargar(path, size=(W, H)):
    if not os.path.exists(path):
        return None
    im = Image.open(path).convert("RGB")
    if size and im.size != size:
        im = im.resize(size, Image.LANCZOS)
    return im


def cuadro(f):
    return cargar(os.path.join(src, f"{f:05d}.png"))


def aux(pieza, f, size=None):
    p = os.path.join(src, "aux", f"{pieza}_{f:05d}.png")
    if not os.path.exists(p):   # muestras: el más cercano que exista
        cand = sorted(glob.glob(os.path.join(src, "aux", f"{pieza}_*.png")))
        if not cand:
            return None
        p = min(cand, key=lambda q: abs(int(q[-9:-4]) - f))
    return cargar(p, size)


def cuadro_cercano(f, a, b):
    """Para muestras: el cuadro renderizado más cercano dentro del plano."""
    im = cuadro(f)
    if im is not None:
        return im
    cand = [int(os.path.basename(q)[:5]) for q in glob.glob(os.path.join(src, "[0-9]" * 5 + ".png"))]
    cand = [c for c in cand if a <= c < b]
    if not cand:
        return None
    return cuadro(min(cand, key=lambda c: abs(c - f)))


# ---------------- brillo ----------------
def bloom(im, umbral=0.80, fuerza=0.55):
    a = np.asarray(im).astype(np.float32) / 255
    lum = a.max(axis=2)
    mask = np.clip((lum - umbral) / (1 - umbral), 0, 1)[..., None] * a
    g = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).resize((W // 4, H // 4)).filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BILINEAR)).astype(np.float32) / 255
    return Image.fromarray((np.clip(a + g * fuerza, 0, 1) * 255).astype(np.uint8))


# ---------------- recuadros circulares (14–16 pájaro, 31 tupaya) ----------------
def borde_recuadro(lay, cx, cy, r, tipo, s=1.0):
    d = ImageDraw.Draw(lay)
    if tipo == "plumas":
        c1, c2 = (92, 80, 70), (150, 136, 120)
    else:
        c1, c2 = (120, 102, 70), (170, 150, 112)
    n = 46
    for k in range(n):
        a = 2 * math.pi * k / n
        for j, (rr, col, L) in enumerate(((r + 14 * s, c1, 30), (r + 4 * s, c2, 22))):
            px, py = cx + rr * math.cos(a), cy + rr * math.sin(a)
            ang = a + (0.5 if tipo == "plumas" else 0.15) * (1 if k % 2 else -1)
            ex, ey = math.cos(ang) * L * s / 2, math.sin(ang) * L * s / 2
            if tipo == "plumas":
                # pluma: hoja alargada, tangente al círculo y un poco inclinada hacia afuera (se superponen como escamas)
                ta = a + math.pi / 2 + 0.45
                Lp, Wp = 48 * s, 17 * s
                pts = []
                for q in range(12):
                    u = q / 11 * 2 * math.pi
                    lx, ly = Lp / 2 * math.cos(u), Wp / 2 * math.sin(u) * (0.6 + 0.4 * math.cos(u))
                    pts.append((px + lx * math.cos(ta) - ly * math.sin(ta), py + lx * math.sin(ta) + ly * math.cos(ta)))
                d.polygon(pts, fill=(*col, 255), outline=(60, 50, 44, 255))
            else:
                d.line((px - ex, py - ey, px + ex, py + ey), fill=(*col, 255), width=int(6 * s))
    d.ellipse((cx - r - 4 * s, cy - r - 4 * s, cx + r + 4 * s, cy + r + 4 * s), outline=(*c1, 255), width=int(8 * s))
    # distintivo en la esquina: el ojo naranjo del cuitlacoche / la carita de la tupaya
    bx, by, br = cx + r * 0.74, cy - r * 0.74, 44 * s
    if tipo == "plumas":
        d.ellipse((bx - br, by - br, bx + br, by + br), fill=(110, 98, 88, 255), outline=(40, 34, 30, 255), width=int(5 * s))
        d.ellipse((bx - br * 0.62, by - br * 0.62, bx + br * 0.62, by + br * 0.62), fill=(250, 120, 20, 255))
        d.ellipse((bx - br * 0.26, by - br * 0.26, bx + br * 0.26, by + br * 0.26), fill=(10, 8, 6, 255))
        d.ellipse((bx - br * 0.36, by - br * 0.40, bx - br * 0.16, by - br * 0.20), fill=(255, 255, 255, 255))
    else:
        d.ellipse((bx - br, by - br, bx + br, by + br), fill=(150, 132, 96, 255), outline=(60, 50, 34, 255), width=int(5 * s))
        for sx in (-1, 1):
            d.ellipse((bx + sx * br * 0.36 - br * 0.17, by - br * 0.25, bx + sx * br * 0.36 + br * 0.17, by + br * 0.09), fill=(15, 12, 10, 255))
        d.ellipse((bx - br * 0.13, by + br * 0.28, bx + br * 0.13, by + br * 0.50), fill=(30, 22, 18, 255))


def recuadro(im, contenido, cx=540, cy=500, r=200, tipo="plumas", s=1.0):
    if contenido is None or s <= 0.02:
        return im
    rr = int(r * s)
    c = ImageEnhance.Color(ImageEnhance.Contrast(contenido).enhance(1.06)).enhance(1.10)
    L = min(c.size)
    c = c.crop(((c.size[0] - L) // 2, (c.size[1] - L) // 2, (c.size[0] + L) // 2, (c.size[1] + L) // 2)).resize((2 * rr, 2 * rr), Image.LANCZOS)
    c = bloom(c.resize((W, H))).resize((2 * rr, 2 * rr)) if False else c
    mk = Image.new("L", (2 * rr, 2 * rr), 0)
    ImageDraw.Draw(mk).ellipse((0, 0, 2 * rr - 1, 2 * rr - 1), fill=255)
    base = im.convert("RGBA")
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((cx - rr + 8, cy - rr + 16, cx + rr + 8, cy + rr + 16), fill=(0, 0, 0, 110))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    base.paste(c, (cx - rr, cy - rr), mk)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    borde_recuadro(lay, cx, cy, rr, tipo, s)
    base.alpha_composite(lay)
    return base.convert("RGB")


def pop(age, dur=0.35):
    """Escala de entrada con rebote (0 → 1)."""
    if age <= 0:
        return 0.0
    t = age
    if t > dur:
        return 1.0
    x = t / dur
    return min(1.12, 1 - math.exp(-6 * x) * math.cos(7 * x)) if x < 1 else 1.0


# ---------------- 23 y 24: "y si…" ----------------
def compone_lupa(cara, lupa, mx, my, cx, cy, D, zoom=0.55, tenue=1.0):
    im = cara.copy()
    L = lupa.size[0]
    rec = int(L * zoom)
    lz = lupa.crop(((L - rec) // 2, (L - rec) // 2, (L + rec) // 2, (L + rec) // 2)).resize((D, D), Image.LANCZOS)
    mask = Image.new("L", (D, D), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, D - 1, D - 1), fill=255)
    arr = np.asarray(im).astype(np.float32)
    fondo = np.median(arr[:, :20].reshape(-1, 3), axis=0)
    sil = (np.abs(arr - fondo).sum(axis=2) > 40).astype(np.float32)
    sil = np.asarray(Image.fromarray((sil * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(2))) / 255.0
    capa = Image.new("L", (W, H), 0)
    dc = ImageDraw.Draw(capa)
    r_m = 26
    ang = math.atan2(cy - my, cx - mx)
    for s in (-1, 1):
        a = ang + s * math.pi / 2
        dc.line(((mx + r_m * math.cos(a), my + r_m * math.sin(a)), (cx + D / 2 * math.cos(a), cy + D / 2 * math.sin(a))), fill=255, width=5)
    alfa = np.asarray(capa).astype(np.float32) / 255.0 * (1.0 - tenue * sil)
    im = Image.composite(Image.new("RGB", (W, H), (244, 242, 236)), im, Image.fromarray((alfa * 255).astype(np.uint8)))
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).ellipse((cx - D // 2 + 10, cy - D // 2 + 18, cx + D // 2 + 10, cy + D // 2 + 18), fill=140)
    im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, sh.filter(ImageFilter.GaussianBlur(18)))
    im.paste(lz, (cx - D // 2, cy - D // 2), mask)
    d = ImageDraw.Draw(im)
    d.ellipse((cx - D // 2, cy - D // 2, cx + D // 2, cy + D // 2), outline=(250, 246, 236), width=10)
    d.ellipse((mx - r_m, my - r_m, mx + r_m, my + r_m), outline=(250, 246, 236), width=6)
    return im


def marco_ysi(im, marca, mxy, age):
    m, r = int(W * 0.06), int(W * 0.08)
    x0, y0, x1, y1 = m, int(H * 0.16), W - m, int(H * 0.80)
    fuera = ImageEnhance.Brightness(im.filter(ImageFilter.GaussianBlur(W // 60))).enhance(0.45)
    mk = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mk).rounded_rectangle((x0, y0, x1, y1), radius=r, fill=255)
    im = Image.composite(im, fuera, mk)
    d = ImageDraw.Draw(im)
    paso, largo, g = int(W * 0.035), int(W * 0.02), 6
    col = (244, 242, 236)
    for x in range(x0 + r, x1 - r, paso):
        d.line((x, y0, min(x + largo, x1 - r), y0), fill=col, width=g)
        d.line((x, y1, min(x + largo, x1 - r), y1), fill=col, width=g)
    for y in range(y0 + r, y1 - r, paso):
        d.line((x0, y, x0, min(y + largo, y1 - r)), fill=col, width=g)
        d.line((x1, y, x1, min(y + largo, y1 - r)), fill=col, width=g)
    for (cx, cy, a0) in ((x0 + r, y0 + r, 180), (x1 - r, y0 + r, 270), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90)):
        for a in range(a0, a0 + 90, 30):
            d.arc((cx - r, cy - r, cx + r, cy + r), a, a + 15, fill=col, width=g)
    s = pop(age - 0.35)
    if s > 0.02:
        cx, cy = mxy
        k2 = int(W * 0.075 * s)
        if marca == "x":
            for c_, gg in (((25, 20, 22), int(W * 0.040 * s) + 1), ((244, 242, 236), int(W * 0.024 * s) + 1)):
                d.line((cx - k2, cy - k2, cx + k2, cy + k2), fill=c_, width=gg)
                d.line((cx - k2, cy + k2, cx + k2, cy - k2), fill=c_, width=gg)
        else:
            R_ = int(W * 0.065 * s)
            d.ellipse((cx - R_, cy - R_, cx + R_, cy + R_), fill=(40, 170, 80), outline=(20, 60, 30), width=5)
            k = int(R_ * 0.5)
            d.line((cx - k, cy, cx - k // 3, cy + int(k * 0.7), cx + k, cy - int(k * 0.6)), fill=(255, 255, 255), width=int(W * 0.018 * s) + 1)
    return im


def ysi(f, k):
    a, b = FR[k]
    age = (f - a) / FPS
    if k == 23:
        cara = cargar(os.path.join(src, f"{a:05d}.png"))
        if cara is None:
            return None
        cara = ImageOps.mirror(cara)           # el ratón mira a la derecha: las líneas de la lupa llegan por la nuca
        lupa = aux("23L", f)
        mej = META.get("23", {}).get("mejilla", [397, 818])
        mx, my = W - mej[0], mej[1]
        im = compone_lupa(cara, lupa, mx, my, 280, 515, 370, zoom=0.55, tenue=1.0) if lupa else cara
        im = marco_ysi(im, "x", (280, 702), age)
    else:
        fondo = cargar(os.path.join(src, f"{a:05d}.png"))
        if fondo is None:
            return None
        lupa = aux("24L", f)
        cu = META.get("24", {}).get("cuello", [520, 900])
        im = compone_lupa(fondo, lupa, cu[0], cu[1], 800, 515, 370, zoom=0.80, tenue=1.0) if lupa else fondo
        im = marco_ysi(im, "check", (800, 702), age)
    # push-in del recuadro entero
    z = 1 + 0.03 * E2.suave(age / max(0.1, (b - a) / FPS))
    if z > 1.001:
        w2, h2 = int(W * z), int(H * z)
        im = im.resize((w2, h2), Image.LANCZOS).crop(((w2 - W) // 2, (h2 - H) // 2, (w2 - W) // 2 + W, (h2 - H) // 2 + H))
    return im


# ---------------- REC (21–22) ----------------
def rec(im, f):
    d = ImageDraw.Draw(im, "RGBA")
    fnt = ImageFont.truetype(FONT_B, 46)
    if (f // 15) % 2 == 0:
        d.ellipse((128, 286, 166, 324), fill=(235, 30, 30, 255))
    d.text((180, 305), "REC", font=fnt, fill=(255, 255, 255), anchor="lm", stroke_width=3, stroke_fill=(0, 0, 0))
    seg = 6 * 3600 + 41 * 60 + 12 + (f - FR[21][0]) / FPS
    hh, mm, ss = int(seg // 3600), int(seg % 3600 // 60), int(seg % 60)
    d.text((880, 305), f"{hh:02d}:{mm:02d}:{ss:02d}", font=fnt, fill=(255, 255, 255), anchor="rm", stroke_width=3, stroke_fill=(0, 0, 0))
    col = (255, 255, 255, 200)
    for (x, y, sx, sy) in ((60, 240, 1, 1), (1020, 240, -1, 1), (60, 1680, 1, -1), (1020, 1680, -1, -1)):
        d.line((x, y, x + 80 * sx, y), fill=col, width=6)
        d.line((x, y, x, y + 80 * sy), fill=col, width=6)
    return im


def vigilancia(im):
    a = np.asarray(im).astype(np.float32)
    a[::4] *= 0.90
    g = a.mean(axis=2, keepdims=True)
    a = a * 0.82 + g * 0.18
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


# ---------------- whip (28) ----------------
def whip(im, f):
    a, b = FR[28]
    m = (a + b) // 2
    x = 1 - abs(f - m) / max(1, (b - a) / 2)          # 1 en el corte
    k = int(20 + 260 * max(0.0, x) ** 1.5)
    arr = np.asarray(im).astype(np.float32)
    ker = np.ones(k) / k
    out = np.empty_like(arr)
    for c in range(3):
        out[..., c] = np.apply_along_axis(lambda r: np.convolve(r, ker, mode="same"), 1, arr[..., c]) if k > 1 else arr[..., c]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def whip_rapido(im, f):
    """Desenfoque horizontal por cajas (rápido con cumsum)."""
    a, b = FR[28]
    m = (a + b) // 2
    x = 1 - abs(f - m) / max(1, (b - a) / 2)
    k = int(20 + 260 * max(0.0, x) ** 1.5)
    arr = np.asarray(im).astype(np.float32)
    pad = np.pad(arr, ((0, 0), (k, k), (0, 0)), mode="edge")
    cs = np.cumsum(pad, axis=1)
    out = (cs[:, 2 * k:] - cs[:, :-2 * k]) / (2 * k)
    out = out[:, :W]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


# ---------------- píldoras, marcas y contador ----------------
STY = {"blanca": ((255, 255, 255), (20, 24, 30)), "amarilla": (AMARILLO, (20, 24, 30)), "coral": ((255, 92, 75), (255, 255, 255)),
       "verde": ((60, 200, 120), (255, 255, 255)), "canela": (CANELA, (255, 255, 255)), "roja": (ROJO, (255, 255, 255))}


def pildora(im, texto, estilo, cx, cy, s=1.0, mezcla=None):
    if s <= 0.02:
        return
    bg, fg = STY[estilo]
    if mezcla:
        bg2, fg2 = STY[mezcla[0]]
        t = mezcla[1]
        bg = tuple(int(bg[i] + (bg2[i] - bg[i]) * t) for i in range(3))
        fg = tuple(int(fg[i] + (fg2[i] - fg[i]) * t) for i in range(3))
    fnt = ImageFont.truetype(FONT_B, max(8, int(56 * s)))
    tw = fnt.getlength(texto)
    pw, ph = tw + 70 * s, 100 * s
    x0, y0 = cx - pw / 2, cy - ph / 2
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x0 + 4, y0 + 8, x0 + pw + 4, y0 + ph + 8), radius=ph / 2, fill=(0, 0, 0, 80))
    d.rounded_rectangle((x0, y0, x0 + pw, y0 + ph), radius=ph / 2, fill=(*bg, 245))
    d.text((cx, cy), texto, font=fnt, fill=fg, anchor="mm")
    base = im.convert("RGBA")
    base.alpha_composite(lay)
    im.paste(base.convert("RGB"))


def marca_ok(im, cx, cy, s):
    if s <= 0.02:
        return
    d = ImageDraw.Draw(im)
    R_ = int(64 * s)
    d.ellipse((cx - R_, cy - R_, cx + R_, cy + R_), fill=(40, 170, 80), outline=(20, 60, 30), width=5)
    k = int(R_ * 0.5)
    d.line((cx - k, cy, cx - k // 3, cy + int(k * 0.7), cx + k, cy - int(k * 0.6)), fill=(255, 255, 255), width=int(18 * s) + 1)


PILDORAS = {}   # plano → función(im, f, edad)


def _pil(k, texto, estilo, y=None, desde=None, clave_y=None, pieza=None, mezcla=None):
    def fn(im, f, age):
        t0 = (F(desde) - FR[k][0]) / FPS if desde is not None else 0.2
        s = pop(age - t0)
        cy = y or 380
        if clave_y:
            v = meta_cuadro(pieza or str(k), f, clave_y)
            if v is not None:
                cy = max(300, min(460, v - 70))
        mz = mezcla(f) if mezcla else None
        pildora(im, texto, estilo, 540, cy, s, mz)
    return fn


T_MAMI = E2.t_palabra("mamíferos")
T_ARIZ = E2.t_palabra("arizona")
T_CHIL = E2.t_palabra("chiltepín")
PILDORAS[5] = _pil(5, "TÚ = RATÓN", "blanca", clave_y="orejas_y", pieza="5")
PILDORAS[6] = lambda im, f, age: pildora(im, "TÚ = RATÓN", "blanca", 540, 380, 1.0, ("canela", E2.suave((t_de(f) - T_MAMI) / 0.25)))
PILDORAS[12] = _pil(12, "¡FUEGO!", "coral", clave_y="baliza_y", pieza="12")
PILDORAS[13] = _pil(13, "NORMAL", "verde", clave_y="termo_y", pieza="13")
PILDORAS[18] = _pil(18, "ARIZONA", "amarilla", desde=T_ARIZ)
PILDORAS[30] = _pil(30, "TUPAYA · CHINA", "amarilla", clave_y="cabeza_y", pieza="30")
PILDORAS[37] = _pil(37, "CON GAS ×", "coral")          # × (U+00D7): Inter no trae ✕


def pildora_19(im, f, age):
    s = pop(age - (F(T_CHIL) - FR[19][0]) / FPS)
    p = meta_cuadro("19", f, "mata", [560, 760])
    pildora(im, "CHILTEPÍN", "amarilla", max(220, min(860, p[0])), max(300, min(900, p[1] - 90)), s)


PILDORAS[19] = pildora_19
PILDORAS[25] = lambda im, f, age: marca_ok(im, 540, 380, pop(age - 1.4))


def contador_35(im, f, age):
    n = meta_cuadro("35", f, "cuenta", 0) or 0
    if n <= 0:
        return
    d = ImageDraw.Draw(im)
    fnt = ImageFont.truetype(FONT, 150)
    fnt2 = ImageFont.truetype(FONT_B, 48)
    d.text((540, 360), str(int(n)), font=fnt, fill=(255, 255, 255), anchor="mm", stroke_width=10, stroke_fill=(20, 24, 30))
    d.text((540, 462), "PERSONAS", font=fnt2, fill=(255, 255, 255), anchor="mm", stroke_width=5, stroke_fill=(20, 24, 30))


PILDORAS[35] = contador_35
# mientras está la píldora que repite lo que dice la voz, el subtítulo se oculta (storyboard)
SIN_SUBS = set(range(F(T_ARIZ), FR[18][1])) | set(range(FR[30][0] + 6, FR[30][1]))


# ---------------- subtítulos (como el Ep. 1, con 3 palabras clave de color) ----------------
def limpiar(w):
    w = w.replace("...", "").replace("…", "")
    for ch in ",.:;!¡?¿\"":
        w = w.replace(ch, "")
    return w.upper()


def vis(w):
    """Como se muestra: mayúsculas, con los signos de pregunta (¿POR QUÉ?)."""
    w = w.replace("...", "").replace("…", "")
    for ch in ",.:;!¡\"":
        w = w.replace(ch, "")
    return w.upper()


grupos, cur = [], []
for i, w in enumerate(words):
    cur.append(i)
    raw = w["w"]
    fin = raw[-1] in ",.:;!?…" or raw.endswith("...")
    if len(cur) == 3 or fin or (i + 1 < len(words) and words[i + 1]["s"] - w["e"] > 0.3):
        grupos.append(cur)
        cur = []
if cur:
    grupos.append(cur)
g2 = []
for g in grupos:
    if any(len(limpiar(words[i]["w"])) >= 11 for i in g) and len(g) > 1:
        g2 += [[i] for i in g]
    else:
        g2.append(g)
grupos = g2


def gap(font, a, b):
    return font.getlength(" ") + 0.07 * (font.getlength(a) + font.getlength(b))


def tam(tok, font):
    return int(font.size * 1.10) if limpiar(tok) in CLAVE else font.size


def ancho(font, toks):
    return sum(ImageFont.truetype(FONT, tam(t, font)).getlength(t) for t in toks) + sum(gap(font, toks[i], toks[i + 1]) for i in range(len(toks) - 1))


def diagramar(g):
    toks = [vis(words[i]["w"]) for i in g]
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


SUB_LOG = []


def subtitulos(img, f):
    if f in SIN_SUBS:
        return
    t = t_de(f)
    g = None
    for gi, gg in enumerate(grupos):
        s = words[gg[0]]["s"]
        e = words[gg[-1]]["e"]
        nxt = grupos[gi + 1] if gi + 1 < len(grupos) else None
        e_show = min(e + 0.25, words[nxt[0]]["s"]) if nxt else e + 0.4
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
            wi = g[k]
            k += 1
            fb = ImageFont.truetype(FONT, tam(tok, font))
            yy = y - (fb.size - font.size) / 2
            activo = words[wi]["s"] - 0.02 <= t < max(words[wi]["e"], words[wi]["s"] + 0.12)
            tw = fb.getlength(tok)
            col = CLAVE.get(limpiar(tok), (255, 255, 255))
            if activo:
                age = t - words[wi]["s"]
                sc = 1.0 + 0.12 * max(0.0, 1 - abs(age - 0.06) / 0.06) if age < 0.12 else 1.0
                fnt = ImageFont.truetype(FONT, int(fb.size * sc))
                ox, oy = (fnt.getlength(tok) - tw) / 2, (fnt.size - fb.size) / 2
                d.text((x - ox + 3, yy - oy + 5), tok, font=fnt, fill=(0, 0, 0, 110))
                d.text((x - ox, yy - oy), tok, font=fnt, fill=AMARILLO if limpiar(tok) not in CLAVE else col, stroke_width=6, stroke_fill=(0, 0, 0))
                SUB_LOG.append((f, limpiar(tok), x - ox, yy - oy, x - ox + fnt.getlength(tok), yy - oy + fnt.size, wi))
            else:
                d.text((x + 3, yy + 5), tok, font=fb, fill=(0, 0, 0, 110))
                d.text((x, yy), tok, font=fb, fill=col, stroke_width=6, stroke_fill=(0, 0, 0))
                SUB_LOG.append((f, limpiar(tok), x, yy, x + tw, yy + fb.size, wi))
            x += tw + (gap(font, tok, line[ti + 1]) if ti + 1 < len(line) else 0)


# ---------------- armado de cada cuadro ----------------
INTERIOR = {7, 8, 9, 10, 11}


def procesar(f):
    k = plano_de(f)
    a, b = FR[k]
    age = (f - a) / FPS
    if k in (23, 24):
        im = ysi(f, k)
    elif k in (14, 15, 16):
        fondo = cuadro_cercano(f, a, b) if k == 14 else cuadro_cercano(FR[14][1] - 1, *FR[14])
        if fondo is None:
            return False
        if k != 14:          # el fondo queda quieto (último cuadro del 14) y un poco más oscuro: manda el recuadro
            fondo = ImageEnhance.Brightness(fondo.filter(ImageFilter.GaussianBlur(3))).enhance(0.8)
        cont = aux(f"{k}S", f)
        s = pop(age - 0.25) if k == 14 else 1.0
        im = recuadro(fondo, cont, 540, 500, 210 if k == 14 else 260, "plumas", s)
    elif k == 31:
        fondo = cargar(os.path.join(src, f"{a:05d}.png"))
        if fondo is None:
            return False
        fondo = ImageEnhance.Brightness(fondo.filter(ImageFilter.GaussianBlur(3))).enhance(0.8)
        im = recuadro(fondo, aux("31S", f), 540, 500, 260, "pelaje", pop(age - 0.05))
    else:
        im = cuadro_cercano(f, a, b) if os.environ.get("MUESTRAS") else cuadro(f)
        if im is None:
            return False
    if k in INTERIOR:
        im = ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(1.06)).enhance(1.10)
    im = bloom(im)
    if k in (21, 22):
        im = rec(vigilancia(im), f)
    if k == 28:
        im = whip_rapido(im, f)
    if k in PILDORAS:
        PILDORAS[k](im, f, age)
    subtitulos(im, f)
    im.save(os.path.join(dst, f"{f:05d}.png"), compress_level=1)
    return True


if __name__ == "__main__":
    cuadros = range(1, END)
    if len(sys.argv) > 3:
        x, y = (int(v) for v in sys.argv[3].split("-"))
        cuadros = range(x, y + 1)
    lista = os.environ.get("LISTA")
    if lista:
        cuadros = [int(v) for v in lista.split(",")]
    faltan = [f for f in cuadros if not procesar(f)]
    json.dump(SUB_LOG, open(os.path.join(OUT, "subs_log.json"), "w"))
    json.dump({"T": {str(k): list(v) for k, v in E2.T.items()}, "FR": {str(k): list(v) for k, v in FR.items()}, "END": END},
              open(os.path.join(OUT, "ep02_planos.json"), "w"))
    print("ok post", len(list(cuadros)) - len(faltan), "cuadros; faltan", len(faltan), faltan[:20])
