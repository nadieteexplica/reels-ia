"""Filtro de quemado del cazador: ¿ya hay un video en ESPAÑOL de este tema con más de 500 mil vistas en los
últimos 6 meses? (regla de Tomás, 23-nov-2026). Si lo hay, la idea se descarta.

Lee la búsqueda pública de YouTube (sin cuenta ni API key), igual que una persona: videos y Shorts con sus vistas.
Para cada resultado sobre el umbral abre su página y lee la fecha de subida.

  python3 tools/cazador/quemado.py "cómo sabe la pistola de bencina que el tanque está lleno" ["otra forma de decirlo" ...]
  python3 tools/cazador/quemado.py --json salida.json "consulta 1" "consulta 2"

Conviene pasar 2–3 formas de decir lo mismo (como lo buscaría la gente). Correr de a una idea (en paralelo YouTube corta).
Veredicto: QUEMADO (video del tema, en español, > 500 mil, < 6 meses) · REVISAR (hay videos grandes y recientes en
español cuyo título no calza con las palabras de la búsqueda: lee los títulos y decide tú; las palabras solas se
equivocan en los dos sentidos) · LIBRE. Además avisa si el tema está saturado (> 5 M en 12 meses) y descarta lo que no
está en español (inglés, portugués).
"""
import argparse, datetime as dt, json, re, sys, time, unicodedata, urllib.parse, urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
UMBRAL = 500_000
DIAS = 183


def get(url, intentos=4):
    """Con reintentos: en paralelo YouTube corta conexiones (SSL, página vacía). Correr de a una consulta."""
    for k in range(intentos):
        try:
            r = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "es-419,es;q=0.9"})
            with urllib.request.urlopen(r, timeout=30) as f:
                h = f.read().decode("utf-8", "replace")
            if "ytInitialData" in h or "/watch" not in url and len(h) > 50000 or "/watch" in url:
                return h
        except Exception:
            pass
        time.sleep(2 * (k + 1))
    raise RuntimeError(f"YouTube no respondió tras {intentos} intentos: {url[:80]}")


VACIAS = set("de la el los las un una y en que por para con del al se su sus es como qué que cómo como lo le tu te mi".split())
ES = set("el la los las de que y en un una por para con del al es se como qué cómo porqué por qué sabías esto este esta".split())
NO_ES = set("the and of to is how why what this that with you your from é não com uma para os das".split())


def norm(t):
    t = unicodedata.normalize("NFKD", t.lower())
    return [w for w in re.findall(r"[a-zñ0-9]+", "".join(c for c in t if not unicodedata.combining(c))) if w not in VACIAS]


def es_espanol(titulo):
    ws = re.findall(r"[a-záéíóúñü]+", titulo.lower())
    return sum(w in ES for w in ws) >= sum(w in NO_ES for w in ws) and not any(w in ("the", "how", "why", "não", "você") for w in ws)


def del_tema(titulo, consultas, minimo=2):
    """¿El título comparte al menos `minimo` palabras con alguna consulta? (si no, es otro tema que salió en la búsqueda)."""
    t = set(norm(titulo))
    t |= {w[:5] for w in t}
    for q in consultas:
        qs = set(norm(q))
        if len({w for w in qs if w in t or w[:5] in t}) >= min(minimo, len(qs)):
            return True
    return False


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
        time.sleep(1.5)
    for r in vistos.values():
        r["espanol"] = es_espanol(r["titulo"])
        r["del_tema"] = del_tema(r["titulo"], consultas)
    # todo lo grande en español, del tema o no: el tema lo confirma quien lee (las palabras solas se equivocan)
    grandes = sorted((r for r in vistos.values() if r["espanol"] and r["vistas"] >= UMBRAL), key=lambda r: -r["vistas"])[:10]
    hoy = dt.date.today()
    for r in grandes:
        f = fecha(r["id"])
        r["fecha"] = f.isoformat() if f else None
        r["reciente"] = bool(f and (hoy - f).days <= DIAS)
        time.sleep(1)
    quemado = [r for r in grandes if r["reciente"] and r["del_tema"]]
    revisar_ = [r for r in grandes if r["reciente"] and not r["del_tema"]]
    saturado = [r for r in grandes if r.get("fecha") and r["vistas"] >= 5_000_000 and (hoy - dt.date.fromisoformat(r["fecha"])).days <= 365]
    veredicto = "QUEMADO" if quemado else "REVISAR" if revisar_ else "LIBRE"
    return {"consultas": consultas, "veredicto": veredicto, "quemado_por": quemado[:3], "revisar_a_mano": revisar_,
            "aviso_saturado": saturado[:2], "grandes_viejos": [r for r in grandes if not r["reciente"]][:5],
            "resultados": len(vistos)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("consultas", nargs="+")
    ap.add_argument("--json")
    a = ap.parse_args()
    r = revisar(a.consultas)
    linea = lambda x: f"{x['vistas']:,} · {x.get('fecha') or '?'} · {x['titulo'][:85]} · youtu.be/{x['id']}"
    print(f"{r['veredicto']}: {a.consultas[0]}")
    for x in r["quemado_por"]:
        print("  QUEMA (del tema, < 6 meses): " + linea(x))
    for x in r["revisar_a_mano"]:
        print("  REVISAR ¿es del tema? (< 6 meses): " + linea(x))
    for x in r["aviso_saturado"]:
        print("  AVISO saturado (> 5 M en 12 meses): " + linea(x))
    for x in r["grandes_viejos"]:
        print("  (> 500 mil pero de hace más de 6 meses: " + linea(x) + ")")
    if a.json:
        json.dump(r, open(a.json, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    sys.exit(main())
