"""Cliente mínimo de la API oficial de Kling (image-to-video) para los planos donde Kling suma (manos con objetos,
reacciones, entrada a la cabeza). Kling nunca inventa anatomía ni cambia el personaje: parte (y puede terminar) en cuadros
renderizados por nosotros. Términos (§6.4): uso comercial no restringido.

Uso:
  KLING_API_KEY=… python kling.py pedido <pedido.json> <carpeta_salida>
El pedido es una lista de clips:
  [{"nombre": "p26_taza", "inicio": "ruta/o/url.png", "final": "opcional", "prompt": "…",
    "modelo": "kling-3.0", "duracion": 5, "resolucion": "1080p"}]
Las rutas relativas se resuelven desde la carpeta del pedido. La clave sólo se lee del entorno y nunca se imprime.
"""
import base64, json, os, sys, time, urllib.request, urllib.error

BASE = "https://api-singapore.klingai.com"


def _key():
    k = os.environ.get("KLING_API_KEY", "").strip()
    if not k:
        sys.exit("falta KLING_API_KEY")
    return k


def _req(method, path, body=None, timeout=120):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method,
                               headers={"Authorization": f"Bearer {_key()}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        msg = e.read().decode(errors="replace")[:600]
        raise RuntimeError(f"HTTP {e.code} en {path}: {msg}") from None


def _img(ref, base_dir):
    if ref.startswith("http://") or ref.startswith("https://"):
        return ref
    p = ref if os.path.isabs(ref) else os.path.join(base_dir, ref)
    return base64.b64encode(open(p, "rb").read()).decode()


def crear(clip, base_dir):
    contents = [{"type": "prompt", "text": clip["prompt"]}, {"type": "first_frame", "url": _img(clip["inicio"], base_dir)}]
    if clip.get("final"):
        contents.append({"type": "last_frame", "url": _img(clip["final"], base_dir)})
    modelo = clip.get("modelo", "kling-3.0")
    settings = {"resolution": clip.get("resolucion", "1080p"), "duration": int(clip.get("duracion", 5))}
    if modelo != "kling-3.0-turbo":
        settings["audio"] = "off"
    if modelo.startswith("kling-3.0") and modelo != "kling-3.0-turbo":
        settings["multi_shot"] = False
    body = {"contents": contents, "settings": settings,
            "options": {"external_task_id": f"{clip['nombre']}-{int(time.time())}", "watermark_info": {"enabled": False}}}
    r = _req("POST", f"/image-to-video/{modelo}", body)
    if r.get("code") not in (0, None):
        raise RuntimeError(f"Kling rechazó {clip['nombre']}: {r.get('code')} {r.get('message')}")
    return r["data"]["id"]


def consultar(task_ids):
    r = _req("GET", "/tasks?task_ids=" + ",".join(task_ids))
    return {t["id"]: t for t in r.get("data", [])}


def bajar(url, dst):
    with urllib.request.urlopen(url, timeout=300) as resp, open(dst, "wb") as f:
        f.write(resp.read())


def pedido(path, out):
    base_dir = os.path.dirname(os.path.abspath(path))
    clips = json.load(open(path))
    os.makedirs(out, exist_ok=True)
    ids = {}
    for c in clips:
        tid = crear(c, base_dir)
        ids[tid] = c
        print(f"enviado {c['nombre']} → tarea {tid}", flush=True)
    pend, t0, res = set(ids), time.time(), []
    while pend and time.time() - t0 < 40 * 60:
        time.sleep(15)
        st = consultar(sorted(pend))
        for tid, t in st.items():
            s = t.get("status")
            if s in ("succeeded", "failed"):
                pend.discard(tid)
                c = ids[tid]
                item = {"nombre": c["nombre"], "tarea": tid, "estado": s, "mensaje": t.get("message"), "cobro": t.get("billing")}
                if s == "succeeded":
                    vids = [o for o in t.get("outputs", []) if o.get("type") == "video" and o.get("url")]
                    dst = os.path.join(out, f"{c['nombre']}.mp4")
                    bajar(vids[0]["url"], dst)
                    item["archivo"] = os.path.basename(dst)
                print(json.dumps(item, ensure_ascii=False), flush=True)
                res.append(item)
    for tid in pend:
        res.append({"nombre": ids[tid]["nombre"], "tarea": tid, "estado": "timeout"})
    json.dump(res, open(os.path.join(out, "kling_resultados.json"), "w"), indent=1, ensure_ascii=False)
    malos = [r for r in res if r["estado"] != "succeeded"]
    print(f"listo: {len(res) - len(malos)} ok, {len(malos)} con problema")
    return 1 if malos and len(malos) == len(res) else 0


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "pedido":
        sys.exit(pedido(sys.argv[2], sys.argv[3]))
    sys.exit(__doc__)
