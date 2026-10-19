"""Post del Ep. 1: subtítulos palabra a palabra, etiquetas tipo píldora, rebobinado VHS y armado del video.

Uso: python3 post.py <carpeta_cuadros> <salida_cuadros>
Lee words.json y ep01_planos.json. Los cuadros que faltan del plano 6 se arman rebobinando los planos 1-5.
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
EPI = os.environ.get("EPI_DIR", os.path.abspath(os.path.join(HERE, "..")))
OUT = os.environ.get("OUT", os.path.join(HERE, "out"))  # en el repo se usa OUT fuera del árbol
src_dir, dst_dir = sys.argv[1], sys.argv[2]
os.makedirs(dst_dir, exist_ok=True)
W, H = 1080, 1920
FPS = 30
words = json.load(open(os.path.join(EPI, "words.json")))
meta = json.load(open(os.path.join(OUT, "ep01_planos.json")))
FR = {int(k): tuple(v) for k, v in meta["FR"].items()}
END = meta["END"]
FONTS = os.path.abspath(os.path.join(HERE, "../../../plantilla/fonts"))
FONT = os.path.join(FONTS, "Inter-Black.otf")
FONT_B = os.path.join(FONTS, "Inter-ExtraBold.otf")
YELLOW = (255, 210, 63)
CYAN = (92, 225, 230)
KEYWORDS = {"HELADO", "FRENTE", "CEREBRO", "CALOR", "CARRITO", "PALADAR", "VASOS", "SANGUÍNEOS", "CALIENTE", "TRIGÉMINO", "CARA",
            "HARVARD", "2012", "TRECE", "ARTERIA", "DOLOR", "NERVIOS", "LENGUA", "TIBIO", "PELIGROSO", "LENTO", "MINUTOS", "FRÍO"}
BOX = (120, 888, 1000, 1250)  # x0, x1, y0, y1 de la zona de subtítulos


def t_of(f):
    return (f - 1) / FPS


def shot_of(f):
    for k, (a, b) in FR.items():
        if a <= f < b:
            return k
    return max(FR)


# ---------- subtítulos: grupos de 1 a 3 palabras, cortados en la puntuación ----------
def clean(w):
    w = w.replace("...", "").replace("…", "")
    for ch in ",.:;!¡?¿\"":
        w = w.replace(ch, "")
    return w.upper()


groups, cur = [], []
for i, w in enumerate(words):
    cur.append(i)
    raw = w["w"]
    end_punct = raw[-1] in ",.:;!?…" or raw.endswith("...")
    if len(cur) == 3 or end_punct or (i + 1 < len(words) and words[i + 1]["s"] - w["e"] > 0.3):
        groups.append(cur)
        cur = []
if cur:
    groups.append(cur)
# palabras muy largas van solas
g2 = []
for g in groups:
    longw = [i for i in g if len(clean(words[i]["w"])) >= 11]
    if longw and len(g) > 1:
        for i in g:
            g2.append([i])
    else:
        g2.append(g)
groups = g2
# el nombre científico ya está en letras gigantes: sin subtítulos desde que se empieza a decir
_t_g = next(w["s"] for w in words if w["s"] >= 52.0 and w["w"].lower().startswith("gangli"))
NO_SUBS = set(range(int(round(_t_g * 30)) + 1, FR[23][1]))


def fit_font(texts, maxw, size=84, min_size=60):
    while size >= min_size:
        f = ImageFont.truetype(FONT, size)
        if all(f.getlength(t) <= maxw for t in texts):
            return f
        size -= 4
    return ImageFont.truetype(FONT, min_size)


def layout(g):
    toks = [clean(words[i]["w"]) for i in g]
    maxw = (BOX[1] - BOX[0]) / 1.12  # margen para el pop de 1,12 de la palabra activa (no salirse de la zona segura)
    f = fit_font([" ".join(toks)], maxw)
    lines = [toks]
    if f.getlength(" ".join(toks)) > maxw and len(toks) > 1:
        lines = [toks[:len(toks) // 2 + len(toks) % 2], toks[len(toks) // 2 + len(toks) % 2:]]
        f = fit_font([" ".join(l) for l in lines], maxw)
    return f, lines


SUB_LOG = []


def draw_subs(img, f):
    if f in NO_SUBS:
        return
    t = t_of(f)
    g = None
    for gg in groups:
        s = words[gg[0]]["s"]
        e = words[gg[-1]]["e"]
        nxt = groups[groups.index(gg) + 1] if groups.index(gg) + 1 < len(groups) else None
        e_show = min(e + 0.25, words[nxt[0]]["s"]) if nxt else e + 0.4
        if s - 0.03 <= t < e_show:
            g = gg
            break
    if g is None:
        return
    font, lines = layout(g)
    d = ImageDraw.Draw(img, "RGBA")
    lh = font.size * 1.12
    total_h = lh * len(lines)
    y0 = (BOX[2] + BOX[3]) / 2 - total_h / 2
    cx = (BOX[0] + BOX[1]) / 2
    flat = [i for i in g]
    k = 0
    for li, line in enumerate(lines):
        txt = " ".join(line)
        lw = font.getlength(txt)
        x = cx - lw / 2
        y = y0 + li * lh
        for tok in line:
            wi = flat[k]
            k += 1
            active = words[wi]["s"] - 0.02 <= t < max(words[wi]["e"], words[wi]["s"] + 0.12)
            tw = font.getlength(tok)
            if active:
                age = t - words[wi]["s"]
                sc = 1.0 + 0.12 * max(0.0, 1 - abs(age - 0.06) / 0.06) if age < 0.12 else 1.0
                fnt = ImageFont.truetype(FONT, int(font.size * sc))
                ox = (fnt.getlength(tok) - tw) / 2
                oy = (fnt.size - font.size) / 2
                # sombra suave
                d.text((x - ox + 3, y - oy + 5), tok, font=fnt, fill=(0, 0, 0, 110))
                d.text((x - ox, y - oy), tok, font=fnt, fill=YELLOW, stroke_width=6, stroke_fill=(0, 0, 0))
                SUB_LOG.append((f, tok, x - ox, y - oy, x - ox + fnt.getlength(tok), y - oy + fnt.size))
            else:
                d.text((x + 3, y + 5), tok, font=font, fill=(0, 0, 0, 110))
                d.text((x, y), tok, font=font, fill=CYAN if tok in KEYWORDS else (255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))
                SUB_LOG.append((f, tok, x, y, x + tw, y + font.size))
            x += tw + font.getlength(" ")


# ---------- píldoras ----------
PILLS = {  # plano: [(texto, estilo)]
    10: [("PALADAR", "blanca")], 11: [("VASOS SANGUÍNEOS", "blanca")], 13: [("NERVIO TRIGÉMINO", "amarilla")],
    17: [("HARVARD · 2012", "blanca")], 18: [("13 VOLUNTARIOS", "blanca")], 19: [("ARTERIA", "blanca")],
    21: [("0 RECEPTORES DE DOLOR", "coral")], 34: [("EL TRUCO", "amarilla")],
    27: [("DURA ≤ 2 MIN", "blanca")], 35: [("NO ES PELIGROSO", "verde")],
}
STY = {"blanca": ((255, 255, 255), (20, 24, 30)), "amarilla": (YELLOW, (20, 24, 30)), "coral": ((255, 92, 75), (255, 255, 255)), "verde": ((60, 200, 120), (255, 255, 255))}
PILL_FONT = ImageFont.truetype(FONT_B, 52)


def pill(img, text, style, cx, cy, s=1.0):
    bg, fg = STY[style]
    fnt = ImageFont.truetype(FONT_B, max(8, int(52 * s)))
    tw = fnt.getlength(text)
    pw, ph = tw + 64 * s, 92 * s
    x0, y0 = cx - pw / 2, cy - ph / 2
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x0 + 4, y0 + 8, x0 + pw + 4, y0 + ph + 8), radius=ph / 2, fill=(0, 0, 0, 70))
    d.rounded_rectangle((x0, y0, x0 + pw, y0 + ph), radius=ph / 2, fill=(*bg, 245))
    d.text((cx - tw / 2, cy - fnt.size * 0.58), text, font=fnt, fill=fg)
    img.alpha_composite(lay)


def draw_pills(img, f):
    k = shot_of(f)
    if k not in PILLS:
        return
    a, b = FR[k]
    age = (f - a) / FPS
    # entra con rebote a los 0,25 s y se va al final
    if age < 0.2:
        return
    t = age - 0.2
    s = 1.0 + 0.25 * math.exp(-t * 9) * math.cos(t * 22) if t < 0.5 else 1.0
    s = min(s, 1.25) * min(1.0, t / 0.08)
    for i, (txt, sty) in enumerate(PILLS[k]):
        pill(img, txt, sty, 504, 330 + i * 118, s)


def draw_pain_meter(img, f):
    """Medidor de dolor (planos 19-20): sube cuando la arteria se ensancha y baja cuando vuelve."""
    if not (FR[19][0] <= f < FR[20][1]):
        return
    a = FR[19][0]
    x = (f - a) / (FR[20][1] - a)
    lvl = np.interp(f, [FR[19][0], FR[19][0] + 40, FR[19][1], FR[20][0] + 25, FR[20][1]], [0.1, 0.92, 0.95, 0.12, 0.08])
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = 214, 470, 794, 530
    d.rounded_rectangle((x0, y0, x1, y1), radius=30, fill=(255, 255, 255, 235))
    fw = (x1 - x0 - 12) * lvl
    col = (int(80 + 175 * lvl), int(200 - 150 * lvl), 60)
    d.rounded_rectangle((x0 + 6, y0 + 6, x0 + 6 + max(fw, 40), y1 - 6), radius=24, fill=(*col, 255))
    fnt = ImageFont.truetype(FONT_B, 40)
    d.text((x0 + 4, y0 - 58), "DOLOR", font=fnt, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))
    img.alpha_composite(lay)


def draw_question(img, f):
    k = shot_of(f)
    if k != 5:
        return
    age = (f - FR[5][0]) / FPS
    s = min(1.0, age / 0.12) * (1 + 0.2 * math.exp(-age * 8))
    fnt = ImageFont.truetype(FONT, int(220 * s) + 1)
    d = ImageDraw.Draw(img, "RGBA")
    d.text((760, 360), "?", font=fnt, fill=YELLOW, stroke_width=10, stroke_fill=(0, 0, 0), anchor="mm")


# ---------- rebobinado (plano 6) ----------
def rewind_frame(f):
    a, b = FR[6]
    n = b - a
    src_f = int(round(np.interp(f - a, [0, n - 1], [FR[5][1] - 1, 2])))
    im = load(src_f)
    if im is None:
        return None
    arr = np.asarray(im.convert("RGB")).astype(np.float32)
    rng = np.random.default_rng(f)
    # bandas horizontales desplazadas
    for _ in range(6):
        y = rng.integers(0, H - 60)
        h = rng.integers(8, 60)
        arr[y:y + h] = np.roll(arr[y:y + h], rng.integers(-40, 40), axis=1)
    # aberración cromática
    arr[..., 0] = np.roll(arr[..., 0], 6, axis=1)
    arr[..., 2] = np.roll(arr[..., 2], -6, axis=1)
    # líneas de barrido y desaturado leve
    arr[::3] *= 0.82
    g = arr.mean(axis=2, keepdims=True)
    arr = arr * 0.75 + g * 0.25
    noise = rng.normal(0, 10, arr.shape[:2])[..., None]
    arr = np.clip(arr + noise, 0, 255)
    out = Image.fromarray(arr.astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(out)
    if (f // 8) % 2 == 0:  # ícono de rebobinar: dos triángulos
        for dx in (0, 70):
            tri = [(260 + dx, 250), (260 + dx, 370), (170 + dx, 310)]
            d.polygon([(x + 4, y + 6) for x, y in tri], fill=(0, 0, 0))
            d.polygon(tri, fill=(255, 255, 255), outline=(0, 0, 0))
    return out


_cache = {}


def load(f):
    p = os.path.join(src_dir, f"{f:05d}.png")
    if not os.path.exists(p):
        return None
    im = Image.open(p).convert("RGBA")
    if im.size != (W, H):
        im = im.resize((W, H), Image.LANCZOS)
    return im


def process(f):
    k = shot_of(f)
    if k == 6:
        im = rewind_frame(f)
    else:
        im = load(f)
    if im is None:
        return False
    draw_question(im, f)
    draw_pills(im, f)
    draw_pain_meter(im, f)
    draw_subs(im, f)
    im.convert("RGB").save(os.path.join(dst_dir, f"{f:05d}.png"), compress_level=1)
    return True


if __name__ == "__main__":
    frames = range(1, END)
    if len(sys.argv) > 3:
        a, b = (int(x) for x in sys.argv[3].split("-"))
        frames = range(a, b + 1)
    miss = [f for f in frames if not process(f)]
    json.dump(SUB_LOG, open(os.path.join(OUT, "subs_log.json"), "w"))
    print("ok post", len(frames) - len(miss), "cuadros; faltan", len(miss))
