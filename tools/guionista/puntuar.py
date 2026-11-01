"""Junta las respuestas de los espectadores simulados y dice (1) si el simulador se puede creer hoy y (2) cómo
quedan los candidatos contra los videos reales (docs/GUIONISTA.md §5).

  python3 tools/guionista/puntuar.py <ep | carpeta> [--imagenes]

Lee studio/episodios/<ep>/guionista/prueba/clave.json y resultados/panel<N>.json (la respuesta JSON de cada
espectador). Escribe prueba/puntaje.json y prueba/puntaje.md.

Por video (ancla o candidato):
  quedan_2s   % de espectadores que no deslizó en 2 s            -> se compara con "se quedó" de YouTube
  entero      promedio de lo_ve_entero_pct                        -> se compara con % visto
  manda       % que lo mandaría                                    -> envíos
  borda       puesto promedio en el orden de cada espectador (0 = primero, 1 = último)
Calibración (sólo anclas): correlación de rangos (Spearman) de quedan_2s contra yt_se_quedo e ig_pasa_3s,
de borda contra las vistas, y si el peor ancla real (ep05) quedó en el último tercio.
El simulador se puede usar para DESCARTAR si pasa las tres; si no, sus números sólo son orientación.
"""
import json, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


def rangos(xs):
    orden = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(orden):
        j = i
        while j + 1 < len(orden) and xs[orden[j + 1]] == xs[orden[i]]:
            j += 1
        for k in range(i, j + 1):
            r[orden[k]] = (i + j) / 2
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = rangos(a), rangos(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    va = sum((x - ma) ** 2 for x in ra) ** 0.5
    vb = sum((y - mb) ** 2 for y in rb) ** 0.5
    return cov / (va * vb) if va and vb else 0.0


def main():
    ep = sys.argv[1]
    sub = "prueba_img" if "--imagenes" in sys.argv else "prueba"
    base = (Path(ep) if Path(ep).is_dir() else RAIZ / "studio/episodios" / ep / "guionista") / sub
    clave = json.load(open(base / "clave.json"))
    anclas = {a["id"]: a for a in json.load(open(RAIZ / "tools/guionista/calibracion/anclas.json"))["anclas"]}
    acc = {}
    paneles = 0
    for panel, mapa in clave.items():
        f = base / "resultados" / f"{panel}.json"
        if not f.exists():
            print(f"falta {f.name}")
            continue
        r = json.load(open(f))
        paneles += 1
        orden = r.get("orden", [])
        for v in r["videos"]:
            m = mapa.get(v["codigo"])
            if not m:
                continue
            d = acc.setdefault(m["id"], {"tipo": m["tipo"], "q": [], "e": [], "m": [], "b": [], "se_va": [], "por_que": []})
            d["q"].append(1 if v.get("se_queda_2s") else 0)
            d["e"].append(float(v.get("lo_ve_entero_pct", 0)) if v.get("se_queda_2s") else 0.0)
            d["m"].append(1 if v.get("lo_manda") else 0)
            d["se_va"].append(v.get("se_va_en", ""))
            d["por_que"].append(v.get("por_que_2s", ""))
            if v["codigo"] in orden and len(orden) > 1:
                d["b"].append(orden.index(v["codigo"]) / (len(orden) - 1))
    if not acc:
        raise SystemExit("sin resultados")
    tabla = {}
    for i, d in acc.items():
        prom = lambda xs: round(100 * sum(xs) / len(xs), 1) if xs else None
        tabla[i] = {"tipo": d["tipo"], "quedan_2s": prom(d["q"]), "entero": round(sum(d["e"]) / len(d["e"]), 1),
                    "manda": prom(d["m"]), "borda": round(sum(d["b"]) / len(d["b"]), 3) if d["b"] else None,
                    "se_va_en": d["se_va"], "por_que_2s": d["por_que"]}
    ids = [i for i in tabla if tabla[i]["tipo"] == "ancla" and i in anclas]
    cal = {}
    if len(ids) >= 4:
        q = [tabla[i]["quedan_2s"] for i in ids]
        cal["rho_quedan_vs_yt_se_quedo"] = round(spearman(q, [anclas[i]["real"]["yt_se_quedo"] for i in ids]), 2)
        cal["rho_quedan_vs_ig_pasa_3s"] = round(spearman(q, [anclas[i]["real"]["ig_pasa_3s"] for i in ids]), 2)
        cal["rho_borda_vs_yt_vistas"] = round(spearman([-tabla[i]["borda"] for i in ids],
                                                       [anclas[i]["real"]["yt_vistas"] for i in ids]), 2)
        peor_real = min(ids, key=lambda i: anclas[i]["real"]["yt_se_quedo"])
        orden_q = sorted(ids, key=lambda i: tabla[i]["quedan_2s"])
        cal["peor_real"] = peor_real
        cal["peor_real_en_ultimo_tercio"] = orden_q.index(peor_real) < max(1, len(ids) // 3)
        cal["se_puede_usar_para_descartar"] = (cal["rho_quedan_vs_ig_pasa_3s"] >= 0.5 and
                                               cal["rho_borda_vs_yt_vistas"] >= 0.5 and
                                               cal["peor_real_en_ultimo_tercio"])
    res = {"paneles": paneles, "calibracion": cal, "videos": tabla}
    (base / "puntaje.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    filas = sorted(tabla.items(), key=lambda kv: (kv[1]["borda"] if kv[1]["borda"] is not None else 9))
    md = [f"# Prueba de deslizamiento — {ep} ({paneles} espectadores)", "",
          "| Puesto | Video | Tipo | Se quedan 2 s | Lo ve entero | Lo manda | Borda (0 = mejor) | Real (YT se quedó · vistas) |",
          "|---|---|---|---|---|---|---|---|"]
    for k, (i, t) in enumerate(filas, 1):
        real = anclas[i]["real"] if i in anclas else None
        rtxt = f"{real['yt_se_quedo']} % · {real['yt_vistas']}" if real else "—"
        md.append(f"| {k} | {i} | {t['tipo']} | {t['quedan_2s']} % | {t['entero']} % | {t['manda']} % | {t['borda']} | {rtxt} |")
    md += ["", "## Calibración", "```", json.dumps(cal, ensure_ascii=False, indent=1), "```"]
    if cal and not cal.get("se_puede_usar_para_descartar"):
        md.append("\n**El simulador NO reprodujo los resultados reales en esta corrida: sus números son orientación, no veredicto.**")
    (base / "puntaje.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
