"""Biblioteca gratis del estilo realista (docs/BIBLIOTECA.md).

  python3 tools/biblioteca.py catalogos studio/biblioteca   # metadatos de Poly Haven, ambientCG y Smithsonian 3D (lo corre biblioteca.yml)
  python3 tools/biblioteca.py packs packs                   # packs CC0 de animaciones (Quaternius UAL 1 y 2)
  python3 tools/biblioteca.py sonda sonda                   # respuestas crudas (Smithsonian) y links de Sonniss, para depurar
  python3 tools/biblioteca.py hojas hojas [model|hdri|texture]  # hojas de miniaturas de Poly Haven para elegir el kit
  python3 tools/biblioteca.py buscar "concrete,rust" [hdri|texture|model|material|3d]   # busca en los catálogos del repo
  python3 tools/biblioteca.py bajar polyhaven <id> [2k] [carpeta]                         # baja un asset por nombre (en Actions)
  python3 tools/biblioteca.py bajar ambientcg <id> [2K-JPG] [carpeta]

Los catálogos son sólo metadatos (todo CC0): el render baja cada asset por nombre en el momento, así no se guarda nada pesado.
Poly Haven pide que quede claro que sus assets vienen de ahí: se acredita en la descripción del video cuando se usan.
La red del espacio de trabajo de Claude no llega a estos sitios: `catalogos`, `packs` y `bajar` corren en GitHub Actions.
"""
import json, os, re, sys, time, zipfile
import requests

UA = {"User-Agent": "nadieteexplica-biblioteca/1.0 (+https://github.com/nadieteexplica/reels-ia)"}
TIPOS_PH = {0: "hdri", 1: "texture", 2: "model"}


def _get(url, **kw):
    for i in range(3):
        try:
            r = requests.get(url, headers=UA, timeout=kw.pop("timeout", 60), **kw)
            if r.status_code == 200:
                return r
            print(f"  {r.status_code} {url}")
        except Exception as e:
            print(f"  error {e} {url}")
        time.sleep(3 * (i + 1))
    return None


def polyhaven():
    r = _get("https://api.polyhaven.com/assets")
    if not r:
        return None
    out = {}
    for k, a in r.json().items():
        out[k] = {"tipo": TIPOS_PH.get(a.get("type"), a.get("type")), "nombre": a.get("name"),
                  "categorias": a.get("categories", []), "tags": a.get("tags", []),
                  "res_max": a.get("max_resolution"), "dim_mm": a.get("dimensions"),
                  "poligonos": a.get("polycount"), "autores": list((a.get("authors") or {}).keys()),
                  "fecha": a.get("date_published")}
    return out


def ambientcg():
    out, offset = {}, 0
    while True:
        r = _get("https://ambientcg.com/api/v2/full_json", params={"limit": 250, "offset": offset, "include": "tagData,displayData"})
        if not r:
            break
        found = r.json().get("foundAssets", [])
        if not found:
            break
        for a in found:
            out[a["assetId"]] = {"tipo": a.get("dataType"), "nombre": a.get("displayName"),
                                 "categoria": a.get("displayCategory"), "tags": a.get("tags", [])}
        offset += len(found)
        if offset > 20000:
            break
    return out or None


def smithsonian():
    """Escaneos 3D del Smithsonian Open Access (CC0). Usa la llave pública DEMO_KEY de api.data.gov (pocas consultas por hora)."""
    out, start = {}, 0
    while start < 10000:
        r = _get("https://api.si.edu/openaccess/api/v1.0/search",
                 params={"q": 'online_media_type:"3D Images"', "rows": 1000, "start": start, "api_key": "DEMO_KEY"})
        if not r:
            break
        rows = r.json().get("response", {}).get("rows", [])
        if not rows:
            break
        for x in rows:
            c = x.get("content", {})
            dn = c.get("descriptiveNonRepeating", {})
            medios = []
            for m in (dn.get("online_media", {}) or {}).get("media", []) or []:
                for rec in m.get("resources", []) or []:
                    if rec.get("url"):
                        medios.append({"url": rec["url"], "label": rec.get("label")})
                if m.get("content"):
                    medios.append({"url": m["content"], "label": m.get("type")})
            out[x.get("id")] = {"titulo": x.get("title"), "unidad": x.get("unitCode"),
                                "cc0": (dn.get("metadata_usage") or {}).get("access") == "CC0",
                                "ficha": dn.get("record_link") or dn.get("guid"), "medios": medios[:12]}
        start += len(rows)
        time.sleep(1)
    return out or None


def catalogos(destino):
    os.makedirs(destino, exist_ok=True)
    resumen = {}
    for nombre, f in (("polyhaven", polyhaven), ("ambientcg", ambientcg), ("smithsonian", smithsonian)):
        print("→", nombre)
        try:
            d = f()
        except Exception as e:
            print("  falló:", e)
            d = None
        if d:
            json.dump(d, open(f"{destino}/{nombre}.json", "w"), ensure_ascii=False, separators=(",", ":"))
            tipos = {}
            for v in d.values():
                t = str(v.get("tipo", "3d"))
                tipos[t] = tipos.get(t, 0) + 1
            resumen[nombre] = {"total": len(d), "por_tipo": tipos}
        else:
            resumen[nombre] = {"total": 0, "error": "no respondió (ver el log del workflow)"}
        print(" ", resumen[nombre])
    resumen["fecha"] = time.strftime("%Y-%m-%d")
    json.dump(resumen, open(f"{destino}/resumen.json", "w"), ensure_ascii=False, indent=1)


PACKS = [  # (página, nombre local, licencia)
    ("https://opengameart.org/content/universal-animation-library", "quaternius_UAL1", "CC0 (Quaternius)"),
    ("https://opengameart.org/content/universal-animation-library-2", "quaternius_UAL2", "CC0 (Quaternius)"),
]


def packs(destino):
    from bs4 import BeautifulSoup
    os.makedirs(destino, exist_ok=True)
    leeme = ["Packs CC0 de la biblioteca realista (docs/BIBLIOTECA.md). Origen y licencia:"]
    for pagina, nombre, lic in PACKS:
        r = _get(pagina)
        if not r:
            leeme.append(f"- {nombre}: FALLÓ la página {pagina}")
            continue
        links = sorted({a["href"] for a in BeautifulSoup(r.text, "html.parser").find_all("a", href=True)
                        if re.search(r"\.(zip|7z|rar)$", a["href"], re.I)})
        if not links:
            leeme.append(f"- {nombre}: sin archivos en {pagina}")
        for u in links:
            u = requests.compat.urljoin(pagina, u)
            f = f"{destino}/{nombre}__{os.path.basename(u)}"
            z = _get(u, timeout=600)
            if not z:
                leeme.append(f"- {nombre}: FALLÓ {u}")
                continue
            open(f, "wb").write(z.content)
            info = ""
            if f.lower().endswith(".zip"):
                try:
                    nn = zipfile.ZipFile(f).namelist()
                    info = f" ({len(nn)} archivos; {sum(n.lower().endswith(('.fbx', '.glb', '.gltf', '.blend')) for n in nn)} fbx/glb/blend)"
                except Exception as e:
                    info = f" (zip ilegible: {e})"
            leeme.append(f"- {os.path.basename(f)} — {lic} — {u}{info}")
            print(leeme[-1])
    open(f"{destino}/LEEME.txt", "w").write("\n".join(leeme) + "\n")


def sonda(destino):
    """Respuestas crudas para depurar fuentes nuevas (Smithsonian) y los links de descarga de Sonniss (sin bajar nada)."""
    from bs4 import BeautifulSoup
    os.makedirs(destino, exist_ok=True)
    pruebas = {
        "si_openaccess_q": ("https://api.si.edu/openaccess/api/v1.0/search", {"q": 'online_media_type:"3D Images"', "rows": 5, "api_key": "DEMO_KEY"}),
        "si_openaccess_3d": ("https://api.si.edu/openaccess/api/v1.0/search", {"q": "3d", "rows": 5, "api_key": "DEMO_KEY"}),
        "si_3dapi_glb": ("https://3d-api.si.edu/api/v1.0/content/file/search", {"file_type": "glb", "rows": 5}),
    }
    for n, (u, p) in pruebas.items():
        try:
            r = requests.get(u, params=p, headers=UA, timeout=60)
            open(f"{destino}/{n}.txt", "w").write(f"{r.status_code} {r.url}\n\n{r.text[:20000]}")
        except Exception as e:
            open(f"{destino}/{n}.txt", "w").write(f"error {e}")
    links = []
    for pagina in ("https://sonniss.com/gameaudiogdc", "https://gdc.sonniss.com/"):
        r = _get(pagina)
        if not r:
            links.append({"pagina": pagina, "error": "no respondió"})
            continue
        for a in BeautifulSoup(r.text, "html.parser").find_all("a", href=True):
            h = requests.compat.urljoin(pagina, a["href"])
            if re.search(r"(\.zip|\.torrent|\.rar|\.7z|download|gdc)", h, re.I):
                links.append({"pagina": pagina, "url": h, "texto": a.get_text(" ", strip=True)[:120]})
    for l in links:
        if l.get("url", "").lower().endswith((".zip", ".rar", ".7z")):
            try:
                h = requests.head(l["url"], headers=UA, timeout=30, allow_redirects=True)
                l["estado"], l["bytes"] = h.status_code, int(h.headers.get("content-length", 0))
            except Exception as e:
                l["estado"] = f"error {e}"
    json.dump(links, open(f"{destino}/sonniss_links.json", "w"), ensure_ascii=False, indent=1)


def hojas(destino, catalogo="studio/biblioteca/polyhaven.json", tipo="model", por_hoja=48):
    """Hojas de miniaturas de Poly Haven (para elegir el kit mirando, no a ciegas)."""
    import io
    from PIL import Image, ImageDraw
    os.makedirs(destino, exist_ok=True)
    d = json.load(open(catalogo))
    ids = sorted([k for k, v in d.items() if v["tipo"] == tipo], key=lambda k: (d[k]["categorias"][:1], k))
    for h in range(0, len(ids), por_hoja):
        tiles = []
        for k in ids[h:h + por_hoja]:
            try:
                im = Image.open(io.BytesIO(_get(f"https://cdn.polyhaven.com/asset_img/thumbs/{k}.png?width=256&height=256", timeout=30).content)).convert("RGB").resize((256, 256))
            except Exception:
                im = Image.new("RGB", (256, 256), (60, 60, 60))
            dr = ImageDraw.Draw(im)
            dr.rectangle((0, 226, 256, 256), fill=(0, 0, 0))
            dr.text((4, 230), k[:40], fill=(255, 255, 0))
            dr.text((4, 242), ",".join(d[k]["categorias"][:2])[:40], fill=(255, 255, 255))
            tiles.append(im)
        cols = 8
        sheet = Image.new("RGB", (cols * 256, -(-len(tiles) // cols) * 256), (20, 20, 20))
        for i, t in enumerate(tiles):
            sheet.paste(t, ((i % cols) * 256, (i // cols) * 256))
        sheet.save(f"{destino}/hoja_polyhaven_{tipo}_{h // por_hoja + 1:02d}.jpg", quality=82)


def buscar(palabras, tipo=None, carpeta="studio/biblioteca"):
    pal = [p.strip().lower() for p in palabras.split(",") if p.strip()]
    res = []
    for fuente in ("polyhaven", "ambientcg", "smithsonian"):
        p = f"{carpeta}/{fuente}.json"
        if not os.path.exists(p):
            continue
        for k, v in json.load(open(p)).items():
            if tipo and str(v.get("tipo", "3d")).lower() != tipo.lower():
                continue
            txt = " ".join([k, str(v.get("nombre") or v.get("titulo") or ""), " ".join(v.get("tags", []) or []),
                            " ".join(v.get("categorias", []) or []), str(v.get("categoria") or "")]).lower()
            n = sum(p_ in txt for p_ in pal)
            if n:
                res.append((n, fuente, k, v.get("tipo", "3d"), v.get("nombre") or v.get("titulo")))
    res.sort(key=lambda r: -r[0])
    for r in res[:80]:
        print(f"{r[1]:11s} {str(r[3]):9s} {r[2]:40s} {r[4]}")
    return res


def bajar(fuente, ident, res=None, carpeta="assets_bib"):
    os.makedirs(carpeta, exist_ok=True)
    if fuente == "polyhaven":
        res = res or "2k"
        files = _get(f"https://api.polyhaven.com/files/{ident}").json()
        hechos = []
        if "hdri" in files:  # cielo
            u = files["hdri"][res]["exr"]["url"]
            hechos.append(_guardar(u, carpeta))
        elif "blend" in files:  # modelo o textura: el .blend trae sus texturas en "include"
            b = files["blend"][res]["blend"]
            hechos.append(_guardar(b["url"], carpeta))
            for rel, inc in (b.get("include") or {}).items():
                hechos.append(_guardar(inc["url"], carpeta, rel))
        return hechos
    if fuente == "ambientcg":
        res = res or "2K-JPG"
        f = _guardar(f"https://ambientcg.com/get?file={ident}_{res}.zip", carpeta, f"{ident}_{res}.zip")
        zipfile.ZipFile(f).extractall(f"{carpeta}/{ident}")
        return [f"{carpeta}/{ident}"]
    raise SystemExit(f"fuente desconocida: {fuente}")


def _guardar(url, carpeta, rel=None):
    rel = rel or os.path.basename(url.split("?")[0])
    p = os.path.join(carpeta, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if not os.path.exists(p):
        r = _get(url, timeout=600)
        if not r:
            raise SystemExit(f"no se pudo bajar {url}")
        open(p, "wb").write(r.content)
    return p


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
    elif a[0] == "catalogos":
        catalogos(a[1] if len(a) > 1 else "studio/biblioteca")
    elif a[0] == "packs":
        packs(a[1] if len(a) > 1 else "packs")
    elif a[0] == "sonda":
        sonda(a[1] if len(a) > 1 else "sonda")
    elif a[0] == "hojas":
        hojas(a[1] if len(a) > 1 else "hojas", tipo=a[2] if len(a) > 2 else "model")
    elif a[0] == "buscar":
        buscar(a[1], a[2] if len(a) > 2 else None)
    elif a[0] == "bajar":
        print(bajar(a[1], a[2], a[3] if len(a) > 3 else None, a[4] if len(a) > 4 else "assets_bib"))
    else:
        print(__doc__)
