"""Contorno de Chile (Natural Earth 1:10m, dominio público, vía el paquete npm world-atlas 2.0.2) → chile.json [[lon, lat], ...] por anillo.
Uso: python3 chile_contorno.py countries-10m.json chile.json"""
import json, sys

topo = json.load(open(sys.argv[1]))
tr = topo["transform"]
sx, sy = tr["scale"]; tx, ty = tr["translate"]
arcs = []
for arc in topo["arcs"]:
    x = y = 0
    pts = []
    for dx, dy in arc:
        x += dx; y += dy
        pts.append((x * sx + tx, y * sy + ty))
    arcs.append(pts)


def anillo(idx):
    pts = []
    for a in idx:
        seg = arcs[a] if a >= 0 else arcs[~a][::-1]
        pts.extend(seg if not pts else seg[1:])
    return pts


geo = next(g for g in topo["objects"]["countries"]["geometries"] if g.get("properties", {}).get("name") == "Chile")
polys = geo["arcs"] if geo["type"] == "MultiPolygon" else [geo["arcs"]]
rings = [anillo(p[0]) for p in polys]          # sólo el borde exterior de cada isla
rings = [r for r in rings if len(r) > 8]
rings.sort(key=len, reverse=True)
json.dump([[[round(x, 4), round(y, 4)] for x, y in r] for r in rings], open(sys.argv[2], "w"))
print(len(rings), "anillos;", sum(len(r) for r in rings), "puntos; el mayor", len(rings[0]))
