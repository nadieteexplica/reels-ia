"""Reparte las piezas del Ep. 5 en N trabajos parejos (por costo estimado) → matriz JSON para Actions.

Uso: python3 reparto.py N [piezas,separadas,por,coma] [muestras]
Costo (s por cuadro a 540x960 y 8 muestras en Actions) estimado de los cuadros de estilo (1080x1920/64: A 245 s, B 207 s,
C 500 s → ~1/32 del costo): E1 ~9, E2 ~16, E3/E4/E5 ~8 (con el vapor de la central). Armar cada escena ~60–90 s.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import planos_ep05 as PL

PESO = {"E1": 9, "E2": 16, "E3": 8, "E4": 9, "E5": 9}
ARMADO = 90


def costo(pid, pz, muestras):
    a, b = pz.get("rango", (pz["a"], pz["b"]))
    n = b - a
    if muestras:
        n = min(n, muestras)
    w = PESO.get(PL.ESCENA.get(int(pid.split("@")[0]), "E1"), 12)
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
