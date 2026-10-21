"""Reparte las piezas del Ep. 3 en N trabajos parejos (por costo estimado) → matriz JSON para Actions.

Uso: python3 reparto.py N [piezas,separadas,por,coma] [muestras]
Costo medido en local (2 núcleos, 540x960, 16 muestras): obra ~31 s/cuadro, corte ~26 s; en Actions a 720x1280 ~1,7×.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import planos_ep03 as PL

PESO = {"E1": 55, "E2": 55, "E3": 45, "E4": 50, "E5": 50, "E6": 40, "E7": 55, "E8": 45, "E9": 55}
ARMADO = 25


def costo(pid, pz, muestras):
    a, b = pz["a"], pz["b"]
    n = b - a
    if muestras:
        n = min(n, muestras)
    w = PESO.get(PL.ESCENA.get(int(pid.split("@")[0]), "E1"), 55)
    return ARMADO + n * w


def repartir(n, piezas, muestras):
    items = sorted(((costo(p, PL.PIEZAS[p], muestras), p) for p in piezas), reverse=True)
    bins = [[0, []] for _ in range(n)]
    for c, p in items:
        b = min(bins, key=lambda x: x[0])
        b[0] += c
        b[1].append(p)
    return [{"parte": i, "piezas": ",".join(b[1]), "seg": int(b[0])} for i, b in enumerate(bins) if b[1]]


if __name__ == "__main__":
    n = int(sys.argv[1])
    sel = [p for p in (sys.argv[2] if len(sys.argv) > 2 else "").split(",") if p.strip()] or list(PL.PIEZAS)
    mu = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] else 0
    m = repartir(n, sel, mu)
    print(json.dumps({"include": m}))
    print("estimado (min):", [round(x["seg"] / 60) for x in m], file=sys.stderr)
