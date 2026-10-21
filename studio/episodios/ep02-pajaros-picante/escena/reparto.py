"""Reparte las piezas del Ep. 2 en N trabajos parejos (por costo estimado) → matriz JSON para Actions.

Uso: python3 reparto.py N [piezas,separadas,por,coma] [muestras]
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import planos_ep02 as PL

# segundos por cuadro estimados a 720x1280 y 16 muestras en una máquina de Actions (medidos en los cuadros de estilo)
PESO = {"c0": 55, "desierto": 45, "lengua": 30, "aux": 18, "bosque": 65, "muelas": 20, "corte": 25}
C0 = {"1", "2", "14", "17", "40"}
LENGUA = {"7", "8", "9", "11"}
BOSQUE = {"28b", "29", "30", "31", "32"}
ARMADO = 70     # segundos de armar la escena de cada pieza


def costo(pid, pz, muestras):
    a, b = pz.get("rango") or (pz["a"], pz["b"])
    n = 1 if pz.get("fijo") else (b - a)
    pid = pz.get("base", pid)
    if muestras:
        n = min(n, muestras)
    if pid in C0:
        w = PESO["c0"]
    elif pid in LENGUA:
        w = PESO["lengua"]
    elif pz.get("aux"):
        w = PESO["aux"]
    elif pid in BOSQUE:
        w = PESO["bosque"]
    elif pid in ("23", "24"):
        w = PESO["muelas"]
    elif pid == "10":
        w = PESO["corte"]
    else:
        w = PESO["desierto"]
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
    # "29" pide todas sus partes (29@1, 29@2…)
    sel = [q for p in sel for q in ([p] if p in PL.PIEZAS else sorted(k for k in PL.PIEZAS if k.split("@")[0] == p))]
    mu = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] else 0
    m = repartir(n, sel, mu)
    print(json.dumps({"include": m}))
    print("estimado (min):", [round(x["seg"] / 60) for x in m], file=sys.stderr)
