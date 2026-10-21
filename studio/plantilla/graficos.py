"""Gráficos del post (lupas, recuadros, píldoras, marcas): registro de dónde quedó cada uno y ubicación sin tapar caras.

En el post de cada episodio:
    import graficos as G
    G.cuadro(f)                                   # al empezar cada cuadro
    G.registrar("lupa", (x0, y0, x1, y1))         # cada vez que se dibuja algo encima de la imagen
    G.guardar(os.path.join(OUT, "graficos.json")) # al final → lo lee tools/auditor/chequeo_planos.py

Para ubicar un gráfico sin tapar ojos (lección 47: la lupa fija del plano 14 terminó sobre el ojo al re-encuadrar):
    cx, cy = G.lugar_libre(ancho, alto, ojos, preferidos=[(330, 420), (750, 420)])
`ojos` sale del meta del plano (`"ojos"` que escribe plano.py con `caras.py`). La zona permitida para gráficos es
y 230–960 (arriba de la franja de subtítulos y bajo la barra de la app) y x 40–1040.
"""
import json

ZONA = (40, 230, 1040, 960)        # x0, y0, x1, y1 permitidos para gráficos
MARGEN_OJO = 40                     # píxeles de aire alrededor de cada ojo

_F = [None]
_LOG = []


def cuadro(f):
    _F[0] = f


def registrar(tipo, caja, f=None):
    f = _F[0] if f is None else f
    if f is None:
        return
    x0, y0, x1, y1 = (int(round(v)) for v in caja)
    _LOG.append([int(f), tipo, x0, y0, x1, y1])


def guardar(path):
    with open(path, "w") as fh:
        json.dump(_LOG, fh)


def tapa(caja, ojos, margen=MARGEN_OJO):
    """Ojos (de la lista [[x, y, r, nombre], ...]) que quedan dentro de la caja, con margen."""
    x0, y0, x1, y1 = caja
    return [o for o in (ojos or []) if x0 - margen - o[2] <= o[0] <= x1 + margen + o[2] and y0 - margen - o[2] <= o[1] <= y1 + margen + o[2]]


def lugar_libre(ancho, alto, ojos, preferidos=None, zona=ZONA, paso=30):
    """Centro (cx, cy) para un gráfico de ancho×alto que no tape ningún ojo y quede dentro de la zona.
    Prueba primero los lugares preferidos (en orden) y después una grilla, del más cercano al primer preferido al más lejano."""
    zx0, zy0, zx1, zy1 = zona
    cand = list(preferidos or [])
    ref = cand[0] if cand else ((zx0 + zx1) / 2, zy0 + alto / 2)
    grilla = [(x, y) for x in range(int(zx0 + ancho / 2), int(zx1 - ancho / 2) + 1, paso)
              for y in range(int(zy0 + alto / 2), int(zy1 - alto / 2) + 1, paso)]
    grilla.sort(key=lambda p: (p[0] - ref[0]) ** 2 + (p[1] - ref[1]) ** 2)
    for cx, cy in cand + grilla:
        caja = (cx - ancho / 2, cy - alto / 2, cx + ancho / 2, cy + alto / 2)
        if caja[0] < zx0 or caja[1] < zy0 or caja[2] > zx1 or caja[3] > zy1:
            continue
        if not tapa(caja, ojos):
            return int(cx), int(cy)
    return None          # no cabe sin tapar: hay que cambiar el encuadre del plano, no el gráfico
