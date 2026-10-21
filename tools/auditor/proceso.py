"""Auditor del PROCESO de un episodio (sin IA): cruza la bitácora con los runs de GitHub Actions y el presupuesto.

  python3 tools/auditor/proceso.py <ep> [--desde 2026-10-19T08:00-03:00] [--hasta ...] [--salida archivo.json]

Revisa:
  1. que exista bitácora;
  2. que cada hora prometida tenga el dato medido que la respalda y se haya cumplido (o avisado ANTES de la hora);
  3. que todo trabajo de más de 15 min tenga un chequeo cada 15 min (tolerancia 17) mientras corre;
  4. que cada run caído quede notado (chequeo o aviso) dentro de 20 min;
  5. que nunca haya más de 16 máquinas de Actions a la vez (las otras 4 son para Kling y RunPod);
  6. el gasto del episodio contra el presupuesto por video y lo que queda del mes;
  7. proceso v2 (21-oct-2026): rondas por puerta (máx. 2), revisores por ronda (máx. 2) y horas de trabajo del video (máx. 8)
     contra los topes de presupuesto.json → "proceso_v2".
"""
import glob
import argparse, datetime, json, os, re, sys
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(__file__))
import comun, bitacora

TZ = ZoneInfo("America/Santiago")
REPO = "nadieteexplica/reels-ia"
PRES = os.path.join(os.path.dirname(__file__), "presupuesto.json")


def api(path):
    r = comun.sh(["curl", "-sS", "-H", "Accept: application/vnd.github+json", f"https://api.github.com/repos/{REPO}/{path}"])
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {}


def ts(s):
    if not s:
        return None
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(TZ)


def runs_en(desde, hasta):
    out, page = [], 1
    while page <= 5:
        d = api(f"actions/runs?per_page=100&page={page}&created={desde.astimezone(datetime.timezone.utc):%Y-%m-%dT%H:%M:%SZ}..{hasta.astimezone(datetime.timezone.utc):%Y-%m-%dT%H:%M:%SZ}")
        rs = d.get("workflow_runs", [])
        out += rs
        if len(rs) < 100:
            break
        page += 1
    return out


def jobs(run_id):
    d = api(f"actions/runs/{run_id}/jobs?per_page=100&filter=all")
    return d.get("jobs", [])


def hm(t):
    return t.strftime("%d-%m %H:%M")


def auditar(ep, desde=None, hasta=None):
    r = {"fallas": [], "avisos": [], "datos": {}}
    f = lambda q, ev="", b=False: r["fallas"].append({"que": q, "evidencia": ev, "bloqueante": b})
    a = lambda q, ev="": r["avisos"].append({"que": q, "evidencia": ev})
    B = bitacora.leer(ep)
    ahora = datetime.datetime.now(TZ)
    if not B:
        f("no hay bitácora del proceso (auditoria/proceso.jsonl): no se puede comprobar ninguna hora prometida, "
          "ningún chequeo de 15 min ni el gasto", b=True)
    for e in B:
        e["_t"] = ts(e["ts"])
    desde = desde or (B[0]["_t"] if B else None)
    hasta = hasta or (max(B[-1]["_t"], ahora) if B else ahora)
    if not desde:
        r["datos"]["nota"] = "sin bitácora ni --desde: sólo se revisa la bitácora"
        return r

    # 2. promesas
    for p in [e for e in B if e["tipo"] == "promesa"]:
        if not p.get("dato") or not re.search(r"\d", p["dato"]):
            f(f"promesa n.º {p['n']} ('{p.get('que', '')}' a las {p['hora']}) sin dato medido que la respalde", p.get("dato", ""))
        hh = re.findall(r"(\d{1,2}):(\d{2})", str(p["hora"]))       # "18:40" o "21-oct 11:00"
        if not hh:
            a(f"promesa n.º {p['n']} con hora ilegible: '{p['hora']}'")
            continue
        h, m_ = (int(x) for x in hh[-1])
        limite = p["_t"].replace(hour=h, minute=m_, second=0)
        if limite < p["_t"]:
            limite += datetime.timedelta(days=1)
        cum = next((e for e in B if e["tipo"] == "cumplida" and str(e.get("id")) == str(p["n"])), None)
        avisos = [e for e in B if e["tipo"] == "aviso" and p["_t"] < e["_t"] <= limite]
        fin = cum["_t"] if cum else (ahora if ahora > limite + datetime.timedelta(minutes=10) else None)
        if fin and fin > limite + datetime.timedelta(minutes=10) and not avisos:
            f(f"promesa n.º {p['n']} ('{p.get('que', '')}' a las {p['hora']}) "
              + (f"se cumplió a las {fin:%H:%M}" if cum else "venció sin cumplirse") + " y no hubo aviso antes de la hora")

    # 3–4. trabajos: runs de GitHub + los anotados a mano
    trabajos = []
    for run in runs_en(desde, hasta):
        t0, t1 = ts(run.get("run_started_at") or run["created_at"]), ts(run["updated_at"])
        trabajos.append({"id": f"{run['name']} {run['id']}", "run": run["id"], "t0": t0, "t1": t1,
                         "estado": run.get("conclusion") or run["status"]})
    manual = {}
    for e in B:
        if e["tipo"] == "trabajo":
            w = manual.setdefault(e["id"], {"id": e["id"], "run": None, "t0": e["_t"], "t1": None, "estado": "?"})
            if e.get("estado") in ("fin", "caido"):
                w["t1"], w["estado"] = e["_t"], ("failure" if e["estado"] == "caido" else "success")
    for w in manual.values():
        w["t1"] = w["t1"] or ahora
        trabajos.append(w)
    r["datos"]["trabajos"] = [{"id": w["id"], "desde": hm(w["t0"]), "hasta": hm(w["t1"]), "estado": w["estado"]} for w in trabajos]
    chequeos = [e for e in B if e["tipo"] in ("chequeo", "aviso")]
    for w in trabajos:
        dur = (w["t1"] - w["t0"]).total_seconds() / 60
        clave = str(w["run"] or w["id"])
        marcas = sorted(e["_t"] for e in chequeos if clave in json.dumps({k: v for k, v in e.items() if k != "_t"}, ensure_ascii=False) and w["t0"] <= e["_t"] <= w["t1"] + datetime.timedelta(minutes=20))
        if dur > 15:
            puntos = [w["t0"]] + [m for m in marcas if m <= w["t1"]] + [w["t1"]]
            huecos = [(x, y) for x, y in zip(puntos, puntos[1:]) if (y - x).total_seconds() > 17 * 60]
            if huecos:
                f(f"'{w['id']}' corrió {dur:.0f} min y nadie lo revisó cada 15 min",
                  "; ".join(f"{x:%H:%M}–{y:%H:%M}" for x, y in huecos))
        if w["estado"] in ("failure", "cancelled", "timed_out") and w["run"]:
            if not any(w["t1"] - datetime.timedelta(minutes=2) <= m for m in marcas):
                a(f"'{w['id']}' terminó en {w['estado']} a las {w['t1']:%H:%M} sin chequeo ni aviso anotado")

    # 5. máquinas a la vez
    eventos = []
    for w in trabajos:
        if not w["run"]:
            continue
        for j in jobs(w["run"]):
            if j.get("started_at") and j.get("completed_at"):
                eventos += [(ts(j["started_at"]), 1), (ts(j["completed_at"]), -1)]
    eventos.sort()
    n = pico = 0
    t_pico = None
    for t, d in eventos:
        n += d
        if n > pico:
            pico, t_pico = n, t
    r["datos"]["maquinas_pico"] = pico
    if pico > 16:
        f(f"{pico} máquinas de Actions corriendo a la vez a las {t_pico:%H:%M} (máx. 16: deja 4 libres para Kling y RunPod)", hm(t_pico))

    # 6. gasto
    pres = comun.leer(PRES, {})
    tope = pres.get("por_video", {})
    g = {}
    for e in B:
        if e["tipo"] == "gasto":
            g[e["servicio"]] = g.get(e["servicio"], 0) + e["monto"]
    r["datos"]["gasto"] = g
    for serv, clave in (("kling", "kling_unidades"), ("runpod", "runpod_usd"), ("eleven", "eleven_creditos")):
        if serv in g and clave in tope and g[serv] > tope[clave]:
            f(f"gasto de {serv}: {g[serv]:g} (tope por video {tope[clave]:g})")
    # 7. topes del proceso v2
    pv = pres.get("proceso_v2", {})
    if pv:
        base = os.path.join(comun.ep_dir(ep), "auditoria")
        rondas = {}
        for d in glob.glob(os.path.join(base, "*", "r*")):
            et = os.path.basename(os.path.dirname(d))
            if et in ("6-video", "7-paquete") or "ciclo" in et or not re.match(r"^r\d+$", os.path.basename(d)):   # proceso viejo / canceladas
                continue
            rondas.setdefault(et, []).append(d)
            n_enc = len(comun.leer(os.path.join(d, "encargos.json"), []) or [])
            if n_enc > pv.get("revisores_por_ronda", 2):
                f(f"{et}/{os.path.basename(d)} lanzó {n_enc} revisores (máx. {pv['revisores_por_ronda']})")
        r["datos"]["rondas"] = {k: len(v) for k, v in rondas.items()}
        for et, ds in rondas.items():
            if len(ds) > pv.get("rondas_por_puerta", 2):
                forz = any("--forzar" in json.dumps(comun.leer(os.path.join(d, "checks.json"), {}), ensure_ascii=False) for d in ds)
                (a if forz else f)(f"{et}: {len(ds)} rondas (máx. {pv['rondas_por_puerta']})" + (" con --forzar" if forz else ""))
        if B:
            horas = (B[-1]["_t"] - B[0]["_t"]).total_seconds() / 3600
            r["datos"]["horas_bitacora"] = round(horas, 1)
            if horas > pv.get("horas_por_video", 8):
                a(f"el video lleva {horas:.1f} h desde la primera anotación de la bitácora (tope {pv['horas_por_video']} h de trabajo; "
                  "descontar esperas de Tomás): si se pasó, tiene que haber un aviso a Tomás con opciones")
    kl = pres.get("paquetes", {}).get("kling")
    if kl:
        usado = kl.get("usado_antes_de_bitacora", 0) + sum(
            e["monto"] for ep_ in os.listdir(comun.EPIS) for e in bitacora.leer(ep_) if e["tipo"] == "gasto" and e.get("servicio") == "kling")
        queda = kl["total"] - usado
        r["datos"]["kling_unidades_restantes"] = queda
        if queda < 15:
            a(f"quedan {queda:g} unidades de Kling (avisar a Tomás: usar sólo la biblioteca)")
    return r


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("ep")
    ap.add_argument("--desde")
    ap.add_argument("--hasta")
    ap.add_argument("--salida")
    x = ap.parse_args()
    res = auditar(x.ep, ts(x.desde), ts(x.hasta))
    if x.salida:
        comun.guardar(x.salida, res)
    print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    sys.exit(1 if res["fallas"] else 0)
