"""Baja de una vez todas las fuentes de un guion y deja extractos para verificar (lo corre el workflow fuentes.yml).

  python3 tools/fuentes.py studio/episodios/<ep>/guion.md salida.md [--claves "capsaicin,thrasher,72"] [--extra URL ...]

Por fuente: estado HTTP, título y los párrafos que contienen alguna clave o alguna cifra del guion (máx. 14 párrafos de 700
caracteres): lo justo para comprobar cada afirmación, no el artículo entero. Las páginas que piden captcha (PMC) se leen
por la API de Europe PMC (resumen). El archivo no va al repo (es material de la auditoría): va a una prerelease.
"""
import argparse, json, re, sys
import requests

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36 nadieteexplica-verificador"}


def urls_del_guion(md):
    m = re.search(r"^##\s*Fuentes[^\n]*\n(.*?)(?=^##\s|\Z)", md, re.S | re.M)
    return re.findall(r"https?://[^\s)>\]]+", m.group(1) if m else "")


def cifras_del_guion(md):
    m = re.search(r"^##\s*Guion[^\n]*\n(.*?)(?=^##\s|\Z)", md, re.S | re.M)
    return sorted(set(re.findall(r"\d+(?:[.,]\d+)?", m.group(1) if m else "")))


def texto_html(html):
    try:
        import trafilatura
        t = trafilatura.extract(html, include_comments=False, include_tables=True, favor_recall=True)
        if t and len(t) > 300:
            return t
    except Exception:
        pass
    from bs4 import BeautifulSoup
    s = BeautifulSoup(html, "html.parser")
    for x in s(["script", "style", "nav", "footer", "header"]):
        x.decompose()
    return "\n".join(p.get_text(" ", strip=True) for p in s.find_all(["p", "li", "h1", "h2", "h3", "td", "blockquote", "meta"]))


def europepmc(pmcid):
    r = requests.get("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                     params={"query": f"PMCID:{pmcid}", "resultType": "core", "format": "json"}, headers=UA, timeout=30)
    res = r.json().get("resultList", {}).get("result", [])
    if not res:
        return r.status_code, "", ""
    x = res[0]
    return r.status_code, x.get("title", ""), f"{x.get('journalInfo', {}).get('journal', {}).get('title', '')} {x.get('pubYear', '')}\n{x.get('abstractText', '')}"


def bajar(u):
    m = re.search(r"pmc\.ncbi\.nlm\.nih\.gov/articles/(PMC\d+)", u)
    if m:
        return europepmc(m.group(1))
    r = requests.get(u, headers=UA, timeout=40, allow_redirects=True)
    ct = r.headers.get("content-type", "")
    if "pdf" in ct or u.lower().endswith(".pdf"):
        import io
        from pypdf import PdfReader
        txt = "\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(r.content)).pages[:12])
        return r.status_code, u.rsplit("/", 1)[-1], txt
    tit = re.search(r"<title[^>]*>(.*?)</title>", r.text, re.S | re.I)
    meta = " ".join(re.findall(r'<meta[^>]+(?:name|property)="(?:description|og:description|citation_abstract)"[^>]+content="([^"]+)"', r.text))
    return r.status_code, (tit.group(1).strip() if tit else ""), (meta + "\n" + texto_html(r.text))


def extractos(texto, claves, cifras, maxp=14, largo=700):
    pars = [p.strip() for p in re.split(r"\n\s*\n|\n", texto) if len(p.strip()) > 40]
    rx = re.compile("|".join([re.escape(c) for c in claves if c] + [r"\b" + re.escape(c) + r"\b" for c in cifras]), re.I) if (claves or cifras) else None
    sel = [p for p in pars if rx and rx.search(p)] or pars[:6]
    return [p[:largo] + ("…" if len(p) > largo else "") for p in sel[:maxp]]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("guion")
    ap.add_argument("salida")
    ap.add_argument("--claves", default="")
    ap.add_argument("--extra", nargs="*", default=[])
    a = ap.parse_args()
    md = open(a.guion).read()
    urls = urls_del_guion(md) + a.extra
    claves = [c.strip() for c in a.claves.split(",") if c.strip()]
    cifras = cifras_del_guion(md)
    L = [f"# Extractos de las fuentes de `{a.guion}`", "",
         "Bajados de una vez por el workflow `fuentes.yml`. Son extractos (párrafos con las claves o las cifras del guion), "
         "no los artículos completos. Si una fuente falló o el extracto no alcanza para verificar algo, dilo como problema.", "",
         f"Claves: {', '.join(claves) or '—'} · Cifras del guion: {', '.join(cifras) or '—'}", ""]
    resumen = []
    for i, u in enumerate(urls, 1):
        try:
            st, tit, txt = bajar(u)
            ex = extractos(txt, claves, cifras)
            ok = st == 200 and bool(ex)
        except Exception as e:
            st, tit, ex, ok = "error", str(e)[:200], [], False
        resumen.append({"n": i, "url": u, "estado": st, "ok": ok, "extractos": len(ex)})
        L += [f"## {i}. {tit or u}", f"- URL: {u}", f"- Estado: {st}" + ("" if ok else " · **FALLÓ o sin texto útil**"), ""]
        L += [f"> {p}" + "\n" for p in ex]
        L.append("")
    open(a.salida, "w").write("\n".join(L))
    json.dump(resumen, open(a.salida.rsplit(".", 1)[0] + ".json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps(resumen, ensure_ascii=False))
    sys.exit(0)
