"""Duelo de deslizamiento de a pares (docs/GUIONISTA.md §4–5). Sin personas: un "lector típico" elige cuál desliza
primero, con cada par en los dos órdenes (los LLM cambian de veredicto si se invierte el orden).

  python3 tools/guionista/duelo.py preparar <ep | carpeta> [--jueces 4] [--imagenes] [--con-anclas] [--semilla N]
  python3 tools/guionista/duelo.py contar   <ep | carpeta> [--imagenes]

Dos usos (revisión independiente del 1-nov-2026):
- **Antes de animar (paso 3): sólo los candidatos entre sí** (sin --con-anclas). Todos son escenas imaginadas, del mismo
  tema y descritas igual, así que la comparación es justa. Sirve para ordenar los ganchos, no para decir si son buenos.
- **Con cuadros reales (paso 8): --imagenes --con-anclas.** Cada juez compara UN candidato contra cada ancla (los cuadros
  reales de 0–3 s, a la misma resolución) y nunca ve el mismo tema repetido. Ahí sí vale el umbral contra las anclas.
  Con texto y --con-anclas se puede correr, pero queda sesgado a favor del candidato (una escena imaginada contra
  videos reales con sus defectos): sólo orienta.
- Sin candidatos y con --con-anclas: las anclas entre sí (calibración).

preparar: lee <base>/ganchos.json (o candidatos.json) y escribe <base>/duelo[_img]/juez<N>.md y clave.json.
contar:   lee duelo[_img]/resultados/juez<N>.json ({"pares": [{"par": "P3", "desliza_primero": "XK", "razon": "..."}]})
          y escribe duelo.md y duelo.json: victorias por video y por par (decisión con ≥ 75 % de los votos y el mismo
          ganador en los dos órdenes; si no, empate) y, con anclas, cuántas anclas vence cada candidato.
"""
import argparse, itertools, json, random, shutil, string, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ANCLAS = RAIZ / "tools/guionista/calibracion/anclas.json"
MAX_PALABRAS = {"cuadro0": 45, "0_3s": 40}  # objetivo ≤ 40/35: si el candidato se describe más lindo, gana por la prosa

ENUNCIADO = """# Duelo de Shorts

Vas pasando YouTube Shorts con el pulgar. En este tipo de canal, 1 de cada 4 personas desliza antes de los 2 segundos.
Abajo hay {n} pares de videos. De cada video tienes SOLO lo que se ve y se oye en los primeros 3 segundos.
En cada par, elige cuál deslizarías primero (el que pierde tu atención antes). No hay empates.
Juzga como alguien cualquiera en un feed, no como experto.

Contesta SOLO con un JSON válido:
{{"pares": [{{"par": "<P1>", "desliza_primero": "<código>", "razon": "<una frase>"}}, ...]}}
"""


def base_de(arg):
    """Carpeta de trabajo: una ruta (relativa al directorio actual o a la raíz del repo) o el nombre de un episodio."""
    for p in (Path(arg), RAIZ / arg):
        if p.is_dir():
            return p.resolve()
    return RAIZ / "studio/episodios" / arg / "guionista"


def leer_items(base):
    for nombre in ("ganchos.json", "candidatos.json"):
        f = base / nombre
        if f.exists():
            return json.load(open(f))["candidatos"]
    return []


def tira_de(p):
    src = Path(p["tira"]) if p.get("tira") else ANCLAS.parent / f"{p['id']}_0-3s.jpg"
    src = src if src.is_absolute() else RAIZ / src
    if not src.exists():
        raise SystemExit(f"{p['id']}: falta la tira de cuadros {src} (campo 'tira' en el paquete; 6 cuadros de 0–3 s, "
                         f"360 px de ancho cada uno: tools/guionista/tira.py)")
    return src


def ficha(cod, p, img):
    if img:
        vis = f"- Imagen de 0–3 s (míralo con Read; 6 cuadros en 0, 0,5, 1, 1,5, 2 y 3 s): `{img}`\n"
    else:
        vis = f"- Cuadro 0: {p['cuadro0']}\n- 0–3 s: {p['0_3s']}\n"
    return (f"**{cod}**\n{vis}- Texto en pantalla: {p.get('texto_pantalla_0_3s') or 'subtítulos'}\n"
            f"- Voz 0–3 s: \"{p['voz_0_3s']}\"\n")


def preparar(a):
    rnd = random.Random(a.semilla)
    base = base_de(a.ep)
    cand = leer_items(base)
    if not a.imagenes:
        for x in cand:
            for campo, tope in MAX_PALABRAS.items():
                if len(str(x.get(campo, "")).split()) > tope:
                    raise SystemExit(f"{x['id']}: '{campo}' tiene más de {tope} palabras; descríbelo seco, como las anclas")
    anclas = json.load(open(ANCLAS))["anclas"] if a.con_anclas else []
    out = base / ("duelo_img" if a.imagenes else "duelo")
    (out / "resultados").mkdir(parents=True, exist_ok=True)
    if a.imagenes:
        (out / "img").mkdir(exist_ok=True)
    if anclas and not cand:  # calibración: las anclas entre sí
        items = anclas
        juegos = [list(itertools.combinations(range(len(items)), 2))] * a.jueces
    elif anclas:  # cada juez: un candidato contra cada ancla (nunca el mismo tema repetido)
        items = cand + anclas
        juegos = [[(j % len(cand), len(cand) + k) for k in range(len(anclas))] for j in range(a.jueces)]
        if a.jueces % (2 * len(cand)):
            print(f"ojo: con {len(cand)} candidatos conviene --jueces múltiplo de {2 * len(cand)} "
                  f"(cada candidato en los dos órdenes)", file=sys.stderr)
    else:
        items = cand
        if len(items) < 2:
            raise SystemExit("hacen falta 2 o más ganchos")
        juegos = [list(itertools.combinations(range(len(items)), 2))] * a.jueces
    clave = {"items": [x["id"] for x in items], "jueces": {}}
    vistos = {}
    for j in range(1, a.jueces + 1):
        pares = juegos[j - 1][:]
        rnd.shuffle(pares)
        bloques, usados = [], set()
        for k, (x, y) in enumerate(pares, 1):
            n = vistos.get((x, y), 0)
            vistos[(x, y)] = n + 1
            primero, segundo = (y, x) if n % 2 else (x, y)  # cada par alterna de orden entre los jueces que lo ven
            cods = []
            for _ in (primero, segundo):
                c = "".join(rnd.choice(string.ascii_uppercase) for _ in range(2))
                while c in usados:
                    c = "".join(rnd.choice(string.ascii_uppercase) for _ in range(2))
                usados.add(c)
                cods.append(c)
            txt = []
            for c, idx in zip(cods, (primero, segundo)):
                img = None
                if a.imagenes:
                    img = out / "img" / f"j{j}_{c}.jpg"
                    shutil.copy(tira_de(items[idx]), img)
                txt.append(ficha(c, items[idx], img))
            bloques.append(f"## P{k}\n" + "\n".join(txt))
            clave["jueces"].setdefault(f"juez{j}", {})[f"P{k}"] = {
                "codigos": dict(zip(cods, [items[i]["id"] for i in (primero, segundo)])),
                "orden": [items[primero]["id"], items[segundo]["id"]]}
        (out / f"juez{j}.md").write_text(ENUNCIADO.format(n=len(pares)) + "\n" + "\n".join(bloques))
    (out / "clave.json").write_text(json.dumps(clave, ensure_ascii=False, indent=1))
    print(f"{a.jueces} jueces en {out}")


def contar(a):
    base = base_de(a.ep)
    out = base / ("duelo_img" if a.imagenes else "duelo")
    clave = json.load(open(out / "clave.json"))
    ids = clave["items"]
    gana = {i: 0 for i in ids}
    juega = {i: 0 for i in ids}
    por_par = {}
    for juez, pares in clave["jueces"].items():
        f = out / "resultados" / f"{juez}.json"
        if not f.exists():
            print("falta", f.name, file=sys.stderr)
            continue
        try:
            r = {x["par"]: x for x in json.load(open(f))["pares"]}
        except Exception as e:
            print(f"{f.name} no se pudo leer ({e}); se salta", file=sys.stderr)
            continue
        for p, info in pares.items():
            if p not in r:
                print(f"{juez} no contestó {p}", file=sys.stderr)
                continue
            perdedor = info["codigos"].get(r[p].get("desliza_primero"))
            if perdedor is None:
                print(f"{juez} {p}: código inválido {r[p].get('desliza_primero')!r}", file=sys.stderr)
                continue
            a_id, b_id = info["orden"]
            ganador = b_id if perdedor == a_id else a_id
            gana[ganador] += 1
            juega[a_id] += 1
            juega[b_id] += 1
            k = tuple(sorted((a_id, b_id)))
            d = por_par.setdefault(k, {"votos": {k[0]: 0, k[1]: 0}, "por_orden": {}})
            d["votos"][ganador] += 1
            d["por_orden"].setdefault(a_id, []).append(ganador)
    anclas_ids = {x["id"] for x in json.load(open(ANCLAS))["anclas"]}
    contra = {}
    for (x, y), d in por_par.items():
        for c, an in ((x, y), (y, x)):
            if c not in anclas_ids and an in anclas_ids:
                v = contra.setdefault(c, {"vence": 0, "empata": 0, "pierde": 0})
                cv, av = d["votos"][c], d["votos"][an]
                v["vence" if cv > av else "empata" if cv == av else "pierde"] += 1
    filas = sorted(ids, key=lambda i: (-(gana[i] / juega[i] if juega[i] else 0), i in anclas_ids))
    md = ["# Duelo de deslizamiento", "", "| Video | Gana (no lo deslizan) | % |", "|---|---|---|"]
    for i in filas:
        md.append(f"| {i} | {gana[i]}/{juega[i]} | {round(100 * gana[i] / juega[i]) if juega[i] else '—'} % |")
    if contra:
        md += ["", "**Contra los ganchos reales del canal** (no sigue si pierde contra más de la mitad de las anclas; "
                   "un empate no es derrota). Sólo vale con cuadros reales (`--imagenes`); con texto, orienta:", "",
               "| Candidato | Vence | Empata | Pierde | Sigue |", "|---|---|---|---|---|"]
        for c, v in sorted(contra.items(), key=lambda kv: (-kv[1]["vence"], kv[1]["pierde"])):
            n = v["vence"] + v["empata"] + v["pierde"]
            md.append(f"| {c} | {v['vence']} | {v['empata']} | {v['pierde']} | {'sí' if v['pierde'] * 2 <= n else 'no'} |")
    md += ["", "| Par | Votos | Decisión |", "|---|---|---|"]
    decisiones = {}
    for (x, y), d in sorted(por_par.items()):
        tot = d["votos"][x] + d["votos"][y]
        lider = x if d["votos"][x] >= d["votos"][y] else y
        ambos = len(d["por_orden"]) == 2
        mismo = ambos and all(v.count(lider) * 2 > len(v) for v in d["por_orden"].values())
        dec = lider if tot and d["votos"][lider] / tot >= 0.75 and mismo else ("empate" if ambos else "empate (un solo orden)")
        decisiones[f"{x} vs {y}"] = dec
        md.append(f"| {x} vs {y} | {d['votos'][x]}–{d['votos'][y]} | {dec} |")
    (out / "duelo.json").write_text(json.dumps({"gana": gana, "juega": juega, "decisiones": decisiones,
                                                "contra_anclas": contra}, ensure_ascii=False, indent=1))
    (out / "duelo.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("accion", choices=["preparar", "contar"])
    ap.add_argument("ep")
    ap.add_argument("--jueces", type=int, default=4)
    ap.add_argument("--imagenes", action="store_true")
    ap.add_argument("--con-anclas", action="store_true")
    ap.add_argument("--semilla", type=int, default=None)
    a = ap.parse_args()
    preparar(a) if a.accion == "preparar" else contar(a)


if __name__ == "__main__":
    main()
