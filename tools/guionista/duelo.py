"""Duelo de deslizamiento de a pares (docs/GUIONISTA.md §5, paso 2). Sin personas: un "lector típico" elige
cuál desliza primero, con cada par en los dos órdenes (los LLM cambian de veredicto si se invierte el orden).

  python3 tools/guionista/duelo.py preparar <ep | carpeta> [--jueces 6] [--imagenes] [--con-anclas] [--semilla N]
  python3 tools/guionista/duelo.py contar   <ep | carpeta> [--imagenes]

preparar: lee <base>/candidatos.json (y las anclas si --con-anclas) y escribe <base>/duelo[_img]/juez<N>.md:
          todos los pares, cada uno con códigos al azar y la mitad de los jueces en orden A/B y la otra en B/A.
contar:   lee duelo[_img]/resultados/juez<N>.json ({"pares": [{"par": "P3", "desliza_primero": "XK", "razon": "..."}]})
          y escribe duelo[_img]/duelo.md y duelo.json: victorias por video (no deslizado), y por par si hay
          decisión (≥ 75 % de los votos y el mismo ganador en los dos órdenes) o empate.
"""
import argparse, itertools, json, random, shutil, string
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
MAX_PALABRAS = {"cuadro0": 45, "0_3s": 40}  # como las anclas: si el candidato se describe más lindo, gana por la prosa
ANCLAS = RAIZ / "tools/guionista/calibracion/anclas.json"

ENUNCIADO = """# Duelo de Shorts

Vas pasando YouTube Shorts con el pulgar. En este tipo de canal, 1 de cada 4 personas desliza antes de los 2 segundos.
Abajo hay {n} pares de videos. De cada video tienes SOLO lo que se ve y se oye en los primeros 3 segundos.
En cada par, elige cuál deslizarías primero (el que pierde tu atención antes). No hay empates.
Juzga como alguien cualquiera en un feed, no como experto: ¿en un vistazo entiendes qué estás viendo y te dan ganas de saber qué pasa?
Lo que se ve falso, genérico, de IA, lleno de letreros o como una clase, pierde.

Contesta SOLO con un JSON válido:
{{"pares": [{{"par": "<P1>", "desliza_primero": "<código>", "razon": "<una frase>"}}, ...]}}
"""


def base_de(arg):
    p = Path(arg)
    return p.resolve() if p.is_dir() else RAIZ / "studio/episodios" / arg / "guionista"


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
    fc = base / "candidatos.json"
    items = json.load(open(fc))["candidatos"] if fc.exists() else []
    if a.con_anclas:
        items += [dict(x, _ancla=True) for x in json.load(open(ANCLAS))["anclas"]]
    for x in items:
        for campo, tope in MAX_PALABRAS.items():
            if len(str(x.get(campo, "")).split()) > tope:
                raise SystemExit(f"{x['id']}: '{campo}' tiene más de {tope} palabras; descríbelo seco, como las anclas")
    if len(items) < 2:
        raise SystemExit("hacen falta 2 o más paquetes")
    out = base / ("duelo_img" if a.imagenes else "duelo")
    (out / "resultados").mkdir(parents=True, exist_ok=True)
    pares = [(x, y) for x, y in itertools.combinations(range(len(items)), 2)
             if not (items[x].get("_ancla") and items[y].get("_ancla"))]  # anclas entre sí ya están calibradas
    if not pares:
        pares = list(itertools.combinations(range(len(items)), 2))
    clave = {"items": [x["id"] for x in items], "jueces": {}}
    for j in range(1, a.jueces + 1):
        orden_pares = pares[:]
        rnd.shuffle(orden_pares)
        bloques, mapa = [], {}
        for k, (x, y) in enumerate(orden_pares, 1):
            invertir = ((j + pares.index((x, y))) % 2 == 0)  # cada par sale la mitad de las veces en cada orden
            primero, segundo = (y, x) if invertir else (x, y)
            cods = []
            for idx in (primero, segundo):
                c = "".join(rnd.choice(string.ascii_uppercase) for _ in range(2))
                while c in mapa:
                    c = "".join(rnd.choice(string.ascii_uppercase) for _ in range(2))
                mapa[c] = items[idx]["id"]
                cods.append(c)
            txt = []
            for c, idx in zip(cods, (primero, segundo)):
                img = None
                if a.imagenes:
                    p = items[idx]
                    src = Path(p["tira"]) if p.get("tira") else ANCLAS.parent / f"{p['id']}_0-3s.jpg"
                    src = src if src.is_absolute() else RAIZ / src
                    (out / "img").mkdir(exist_ok=True)
                    img = out / "img" / f"j{j}_{c}.jpg"
                    shutil.copy(src, img)
                txt.append(ficha(c, items[idx], img))
            bloques.append(f"## P{k}\n" + "\n".join(txt))
            clave["jueces"].setdefault(f"juez{j}", {})[f"P{k}"] = {"codigos": dict(zip(cods, [items[i]["id"] for i in (primero, segundo)])),
                                                                     "orden": [items[primero]["id"], items[segundo]["id"]]}
        (out / f"juez{j}.md").write_text(ENUNCIADO.format(n=len(orden_pares)) + "\n" + "\n".join(bloques))
    (out / "clave.json").write_text(json.dumps(clave, ensure_ascii=False, indent=1))
    print(f"{a.jueces} jueces × {len(pares)} pares en {out}")


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
            print("falta", f.name)
            continue
        r = {x["par"]: x for x in json.load(open(f))["pares"]}
        for p, info in pares.items():
            if p not in r:
                continue
            perdedor = info["codigos"].get(r[p]["desliza_primero"])
            if perdedor is None:
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
                v = contra.setdefault(c, {"gana": 0, "anclas_vencidas": 0, "anclas": 0})
                tot = d["votos"][c] + d["votos"][an]
                v["gana"] += d["votos"][c]
                v["anclas"] += 1
                if tot and d["votos"][c] * 2 > tot:
                    v["anclas_vencidas"] += 1
    filas = sorted(ids, key=lambda i: -(gana[i] / juega[i] if juega[i] else 0))
    md = ["# Duelo de deslizamiento", "", "| Video | Gana (no lo deslizan) | % |", "|---|---|---|"]
    for i in filas:
        md.append(f"| {i} | {gana[i]}/{juega[i]} | {round(100 * gana[i] / juega[i]) if juega[i] else '—'} % |")
    if contra:
        md += ["", "**Contra los ganchos reales del canal** (sigue si le gana a la mayoría; con 4 o más anclas perdidas, no sigue):", "",
               "| Candidato | Anclas vencidas | Sigue |", "|---|---|---|"]
        for c, v in sorted(contra.items(), key=lambda kv: -kv[1]["anclas_vencidas"]):
            md.append(f"| {c} | {v['anclas_vencidas']}/{v['anclas']} | {'sí' if v['anclas'] - v['anclas_vencidas'] < 4 else 'no'} |")
    md += ["", "| Par | Votos | Decisión |", "|---|---|---|"]
    decisiones = {}
    for (x, y), d in sorted(por_par.items()):
        tot = d["votos"][x] + d["votos"][y]
        lider = x if d["votos"][x] >= d["votos"][y] else y
        mismo = all(lider in v and v.count(lider) * 2 > len(v) for v in d["por_orden"].values()) if len(d["por_orden"]) == 2 else False
        dec = lider if tot and d["votos"][lider] / tot >= 0.75 and mismo else "empate"
        decisiones[f"{x} vs {y}"] = dec
        md.append(f"| {x} vs {y} | {d['votos'][x]}–{d['votos'][y]} | {dec} |")
    (out / "duelo.json").write_text(json.dumps({"gana": gana, "juega": juega, "decisiones": decisiones, "contra_anclas": contra}, ensure_ascii=False, indent=1))
    (out / "duelo.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("accion", choices=["preparar", "contar"])
    ap.add_argument("ep")
    ap.add_argument("--jueces", type=int, default=6)
    ap.add_argument("--imagenes", action="store_true")
    ap.add_argument("--con-anclas", action="store_true")
    ap.add_argument("--semilla", type=int, default=None)
    a = ap.parse_args()
    preparar(a) if a.accion == "preparar" else contar(a)


if __name__ == "__main__":
    main()
