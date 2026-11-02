"""Post del plano 0 (el mapa): píldoras CHILE y LAGO CACHET 2 · AYSÉN y los subtítulos, con el mismo código y el mismo
estilo de post.py (las funciones se toman de post.py tal cual, sin copiarlas a mano).
Uso: python3 intro_post.py <render_mapa> <mapa_meta.json> <asr_intro.json> <salida>   (VOZ0 = inicio de la voz, 0,10 s)"""
import ast, json, math, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = open(os.path.join(HERE, "post.py")).read()
arbol = ast.parse(SRC)
FPS = 30
VOZ0 = float(os.environ.get("VOZ0", 0.10))
render, meta_p, asr_p, dst = sys.argv[1:5]
os.makedirs(dst, exist_ok=True)
META = json.load(open(meta_p))
words = [{"w": p["w"], "s": round(p["s"] + VOZ0, 3), "e": round(p["e"] + VOZ0, 3)} for p in json.load(open(asr_p))["palabras"]]

class _G:                         # registro de gráficos de post.py (aquí no hace falta)
    @staticmethod
    def registrar(*a, **k):
        pass


ns = {"Image": Image, "ImageDraw": ImageDraw, "ImageFont": ImageFont, "math": math, "os": os, "words": words, "NUMEROS": [], "G": _G}
# constantes y funciones de post.py (mismas fuentes, colores, caja de subtítulos y píldoras)
for nodo in arbol.body:
    if isinstance(nodo, ast.Assign) and any(isinstance(t_, ast.Name) and t_.id in
                                            ("AMARILLO", "AZUL", "BOX", "CLAVE") for t_ in nodo.targets):
        exec(compile(ast.Module([nodo], []), "post.py", "exec"), ns)
ns["HERE"] = HERE
ns["FONTS"] = os.path.abspath(os.path.join(HERE, "../../../plantilla/fonts"))
ns["FONT"] = os.path.join(ns["FONTS"], "Inter-Black.otf")
ns["FONT_B"] = os.path.join(ns["FONTS"], "Inter-ExtraBold.otf")
for nodo in arbol.body:
    if isinstance(nodo, ast.FunctionDef) and nodo.name in ("limpiar", "pop", "pildora", "flecha", "sale", "suave", "s_tok", "e_tok",
                                                             "tam", "gap", "ancho", "diagramar", "subtitulos", "texto_sombra"):
        exec(compile(ast.Module([nodo], []), "post.py", "exec"), ns)
# el armado de los grupos de subtítulos (bloque de nivel de módulo de post.py, entre "TOK = []" y "SIN_SUBS")
a = SRC.index("TOK = []")
b = SRC.index("SIN_SUBS = set()")
exec(SRC[a:b], ns)
ns["SIN_SUBS"] = set()
ns["SUB_LOG"] = []
ns["t_de"] = lambda f: (f - 1) / FPS
ROJO = (225, 45, 40)


def tw(prefijo):
    return next(w["s"] for w in words if ns["limpiar"](w["w"]).startswith(prefijo.upper()))


T_CHILE, T_LAGO = tw("CHILE"), tw("LAGO")


def apunta(im, f, texto, t0, punto, fondo=(250, 250, 248), tinta=(24, 24, 28), tam=50, hasta=None, col=(255, 255, 255)):
    """Como apunta() de post.py: la píldora sobre lo que nombra, con flecha fina hacia abajo (nunca bajo los subtítulos)."""
    t = (f - 1) / FPS
    if t < t0 or (hasta is not None and t >= hasta):
        return
    px, py = META[str(f)][punto][:2]
    cx = max(330, min(750, px))
    cy = max(470, min(800, py - 230))
    s = ns["pop"](t - t0)
    if 0 < py < 960 and py - cy > 120 and s > 0.5:
        ns["flecha"](im, cx, cy + 46, px, py - 14, col, ancho=8)
    ns["pildora"](im, texto, cx, cy, fondo=fondo, tinta=tinta, s=s, tam=tam)


n = len(META)
for f in range(1, n + 1):
    im = Image.open(os.path.join(render, f"{f:05d}.png")).convert("RGB")
    im = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.06)).enhance(1.04)
    t = (f - 1) / FPS
    apunta(im, f, "CHILE", T_CHILE, "chile", hasta=T_LAGO - 0.05)
    late = 0.5 + 0.5 * math.sin(max(0.0, t - T_LAGO) * 9.0)
    rojo = tuple(int(ROJO[i] * (0.82 + 0.18 * late)) for i in range(3))
    apunta(im, f, "LAGO CACHET 2 · AYSÉN", T_LAGO, "lago", fondo=rojo, tinta=(255, 255, 255), tam=46)
    ns["subtitulos"](im, f)
    im.save(os.path.join(dst, f"{f:05d}.png"), compress_level=1)
json.dump(ns["SUB_LOG"], open(os.path.join(dst, "subs_log_intro.json"), "w"))
print("ok intro_post", n, "cuadros")
