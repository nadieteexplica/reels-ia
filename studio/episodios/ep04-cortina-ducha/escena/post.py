"""Post del Ep. 4: arma los cuadros finales (1080x1920) desde los renders de plano.py.

Uso: python3 post.py <carpeta_render> <salida>   (OUT=carpeta de datos, LISTA=cuadros opcionales, MUESTRAS=1 en pruebas)
- Píldoras (aire caliente, agua caliente/fría, baja presión, aire de afuera, cortina pesada), flechas del aire (cian:
  baja con el chorro; naranjas: el aire de afuera empuja), flecha curva que gira con el remolino, anillo del centro,
  brillo y los subtítulos palabra por palabra (franja y 1000–1250). Las posiciones salen del meta de cada cuadro
  (pantalla() de la escena), no de números fijos.
- Escribe subs_log.json, graficos.json y ep04_planos.json en OUT.
"""
import glob, json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "../../../plantilla")))
import ep04 as E
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
ROJO = (236, 60, 48)               # caliente
AZUL = (60, 140, 255)              # frío
CIAN = (40, 205, 255)              # el remolino / baja presión
NARANJO = (255, 140, 30)           # el aire de afuera que empuja
VERDE = (60, 200, 110)             # la solución
LILA = (190, 130, 255)             # fantasma
CLAVE = {"FANTASMA": LILA, "REMOLINO": CIAN, "PESADA": VERDE}
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
NUMEROS = []          # el guion del Ep. 4 no tiene cifras


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


def graficos(im, f, k):
    age = edad(f, k)
    if k == 6:          # "tampoco es solo el aire caliente"
        pildora(im, "¿AIRE CALIENTE?", 540, 380, fondo=ROJO, tinta=(255, 255, 255), s=pop(t_de(f) - tw("aire", 6.0) + 0.05))
        if t_de(f) > tw("caliente", 6.5) + 0.15:
            pildora(im, "NO SÓLO", 540, 500, fondo=(28, 30, 36), tinta=(255, 255, 255), tam=46, marca="x",
                    s=pop(t_de(f) - tw("caliente", 6.5) - 0.15))
    elif k == 7:        # "con agua caliente pasa más fuerte"
        pildora(im, "AGUA CALIENTE", 540, 380, fondo=ROJO, tinta=(255, 255, 255), s=pop(t_de(f) - tw("agua", 7.5)))
        if t_de(f) > tw("más", 8.5):
            pildora(im, "MÁS FUERTE", 540, 500, tam=46, s=pop(t_de(f) - tw("más", 8.5)))
    elif k == 8:        # "pero pasa hasta con agua fría"
        pildora(im, "AGUA FRÍA", 540, 380, fondo=AZUL, tinta=(255, 255, 255), s=pop(t_de(f) - tw("agua", 10.5)))
        if t_de(f) > tw("fría") + 0.1:
            pildora(im, "IGUAL PASA", 540, 500, tam=46, marca="v", s=pop(t_de(f) - tw("fría") - 0.1))
    elif k == 10:       # el chorro arrastra el aire hacia abajo
        cx, cy = meta(10, f, "chorro", (640, 520))
        if t_de(f) > tw("aire", 13.9):
            x = sale(min(1.0, (t_de(f) - tw("aire", 13.9)) / 0.5))
            flecha(im, cx + 150, cy - 120, cx + 150, cy - 120 + 330 * x, CIAN, ancho=14)
            pildora(im, "AIRE", cx + 150, cy - 190, fondo=CIAN, tinta=(10, 30, 40), tam=48, s=pop(t_de(f) - tw("aire", 13.9)))
    elif k in (12, 19):  # gira como una rueda
        cx, cy = meta(k, f, "centro", (540, 760))
        r = meta(k, f, "radio_px", 300) * 1.08
        ang = (t_de(f) * 140) % 360
        arco(im, cx, cy, r, -ang, CIAN, ancho=12)
        if k == 19:
            x0, y0 = meta(19, f, "cortina_alta", (250, 600))
            pildora(im, "CORTINA PESADA", 540, 380, fondo=VERDE, tinta=(255, 255, 255), marca="v", s=pop(age - 0.1))
    elif k == 13:       # el centro del remolino
        cx, cy = meta(13, f, "centro", (540, 760))
        r = 70 + 12 * math.sin(t_de(f) * 8)
        if t_de(f) > tw("centro") - 0.05:
            anillo(im, cx, cy, r * min(1.0, pop(t_de(f) - tw("centro") + 0.05)), CIAN)
    elif k == 14:       # la presión baja
        cx, cy = meta(14, f, "centro", (540, 760))
        anillo(im, cx, cy, 70 + 12 * math.sin(t_de(f) * 8), CIAN)
        if t_de(f) > tw("presión") - 0.05:
            pildora(im, "BAJA PRESIÓN", cx, max(330, cy - 190), fondo=CIAN, tinta=(10, 30, 40), s=pop(t_de(f) - tw("presión") + 0.05))
    elif k == 15:       # el aire de afuera empuja la cortina hacia el ojo del remolino (flechas que convergen)
        cx, cy = meta(15, f, "centro", (540, 720))
        anillo(im, cx, cy, 70, CIAN)
        t0 = tw("afuera") - 0.2
        if t_de(f) > t0:
            x = sale(min(1.0, (t_de(f) - t0) / 0.45))
            for sx in (-1, 1):
                x0 = cx + sx * 420
                x0 = min(1040, max(40, x0))
                flecha(im, x0, cy, x0 + (cx + sx * 95 - x0) * x, cy, NARANJO, ancho=18)
            pildora(im, "AIRE DE AFUERA", 540, 380, fondo=NARANJO, tinta=(255, 255, 255), s=pop(t_de(f) - t0))
        if t_de(f) > tw("empuja"):
            pildora(im, "EMPUJA MÁS", 540, 500, tam=46, s=pop(t_de(f) - tw("empuja")))
    elif k == 18:       # "una cortina más pesada"
        pildora(im, "CORTINA PESADA", 540, 380, fondo=VERDE, tinta=(255, 255, 255), marca="v", s=pop(t_de(f) - tw("cortina", 27.5)))


def procesar(f):
    G.cuadro(f)
    k = plano_de(f)
    a, b = FR[k]
    im = cuadro(f, a, b)
    if im is None:
        return False
    if k in (6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 19):      # brillo sólo en el corte (el aire cian); en el baño quemaba
        im = bloom(im, umbral=0.88, fuerza=0.25)
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
              open(os.path.join(OUT, "ep04_planos.json"), "w"))
    print("ok post", len(list(cuadros)) - len(faltan), "cuadros; faltan", len(faltan), faltan[:20])
