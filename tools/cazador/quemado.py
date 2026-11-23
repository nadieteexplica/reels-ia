"""Filtro de quemado del cazador: ¿ya hay un video en ESPAÑOL de este tema con más de 500 mil vistas en los
últimos 6 meses? (regla de Tomás, 23-nov-2026). Si lo hay, la idea se descarta.

Lee la búsqueda pública de YouTube (sin cuenta ni API key), igual que una persona: videos y Shorts con sus vistas.
Para cada resultado sobre el umbral abre su página y lee la fecha de subida.

  python3 tools/cazador/quemado.py "cómo sabe la pistola de bencina que el tanque está lleno" ["otra forma de decirlo" ...]
  python3 tools/cazador/quemado.py --json salida.json "consulta 1" "consulta 2"

Conviene pasar 2–3 formas de decir lo mismo (como lo buscaría la gente). Veredicto: QUEMADO / LIBRE, con el video
más grande encontrado como evidencia.
"""
import argparse, datetime as dt, json, re, sys, time, urllib.parse, urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
UMBRAL = 500_000
DIAS = 183


def get(url):
    r = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "es-419,es;q=0.9"})
    with urllib.request.urlopen(r, timeout=30) as f:
        return f.read().decode("utf-8", "replace")


def vistas(txt):
    """'26,650 vistas' · '1.5 mil vistas' · '2,3 M de vistas' · 'mil vistas' → int."""
    if not txt:
        return 0
    t = txt.lower().replace("\xa0", " ")
    m = re.search(r"([\d.,]*)\s*(mil millones|millones|mill\.|m\b|mil|k\b)?", t)
    num, suf = (m.group(1) or "").strip(), (m.group(2) or "").strip()
    if not num and suf == "mil":
        return 1000
    if not num:
        return 0
    if suf:  # con sufijo, la coma o el punto es decimal
        n = float(num.replace(",", "."))
        mult = {"mil": 1e3, "k": 1e3, "m": 1e6, "mill.": 1e6, "millones": 1e6, "mil millones": 1e9}[suf]
        return int(n * mult)
    return int(re.sub(r"[.,]", "", num))


def buscar(q):
    h = get("https://www.youtube.com/results?hl=es&search_query=" + urllib.parse.quote(q))
    d = json.loads(re.search(r"var ytInitialData = (\{.*?\});</script>", h).group(1))
    res = []

    def walk(o):
        if isinstance(o, dict):
            if "videoRenderer" in o:
                v = o["videoRenderer"]
                res.append({"id": v["videoId"], "titulo": "".join(r["text"] for r in v["title"]["runs"]),
                            "vistas": vistas((v.get("viewCountText") or {}).get("simpleText")),
                            "hace": (v.get("publishedTimeText") or {}).get("simpleText", ""), "tipo": "video"})
            elif "shortsLockupViewModel" in o:
                v = o["shortsLockupViewModel"]
                acc = v.get("accessibilityText", "")
                m = re.match(r"(.*), ([^,]*vistas)", acc)
                vid = v.get("entityId", "").replace("shorts-shelf-item-", "")
                if m and vid:
                    res.append({"id": vid, "titulo": m.group(1), "vistas": vistas(m.group(2)), "hace": "", "tipo": "short"})
            for x in o.values():
                walk(x)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    walk(d)
    return res


def fecha(vid):
    h = get(f"https://www.youtube.com/watch?v={vid}&hl=es")
    m = re.search(r'"(?:uploadDate|publishDate)":"(\d{4}-\d{2}-\d{2})', h) or re.search(r'itemprop="datePublished" content="(\d{4}-\d{2}-\d{2})', h)
    return dt.date.fromisoformat(m.group(1)) if m else None


def revisar(consultas):
    vistos = {}
    for q in consultas:
        for r in buscar(q):
            vistos.setdefault(r["id"], r)
        time.sleep(1)
    grandes = sorted((r for r in vistos.values() if r["vistas"] >= UMBRAL), key=lambda r: -r["vistas"])
    hoy = dt.date.today()
    quemado = None
    for r in grandes[:8]:
        f = fecha(r["id"])
        r["fecha"] = f.isoformat() if f else None
        if f and (hoy - f).days <= DIAS:
            quemado = r
            break
        time.sleep(1)
    top = quemado or max(vistos.values(), key=lambda r: r["vistas"], default=None)
    return {"consultas": consultas, "veredicto": "QUEMADO" if quemado else "LIBRE",
            "evidencia": top, "grandes_antiguos": [r for r in grandes[:8] if top and r["id"] != top["id"] and r.get("fecha")],
            "resultados": len(vistos)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("consultas", nargs="+")
    ap.add_argument("--json")
    a = ap.parse_args()
    r = revisar(a.consultas)
    e = r["evidencia"] or {}
    print(f"{r['veredicto']}: {a.consultas[0]}")
    if e:
        print(f"  mayor: {e['vistas']:,} vistas · {e.get('fecha') or e.get('hace') or '?'} · {e['titulo'][:90]} · youtu.be/{e['id']}")
    for g in r["grandes_antiguos"]:
        print(f"  (>500 mil pero más viejo: {g['vistas']:,} · {g['fecha']} · {g['titulo'][:70]})")
    if a.json:
        json.dump(r, open(a.json, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    sys.exit(main())
