"""Vigilante de bitácora (lección 73): anota un `chequeo` cada 15 min mientras un trabajo siga abierto.

  python3 tools/auditor/vigila.py <ep> --id "sesion ep05" [--cada 900] [--max 14400]

Sale solo cuando el último `trabajo` con ese id queda en `fin` o `caido`, o al llegar a --max segundos
(por defecto 4 h, el tope del video). Si se corta antes (límite de la herramienta), se relanza con el mismo id.
Para runs de Actions, --run <id> agrega el estado del run (gh run view) a cada chequeo.
"""
import argparse, json, os, subprocess, sys, time

sys.path.insert(0, os.path.dirname(__file__))
import bitacora


def abierto(ep, wid):
    est = None
    for l in bitacora.leer(ep):
        if l.get("tipo") == "trabajo" and l.get("id") == wid:
            est = l.get("estado")
    return est not in ("fin", "caido")


def estado_run(run):
    try:
        r = subprocess.run(["gh", "run", "view", str(run), "--json", "status,conclusion,jobs"],
                           capture_output=True, text=True, timeout=60)
        d = json.loads(r.stdout)
        jobs = d.get("jobs", [])
        listos = sum(1 for j in jobs if j.get("status") == "completed")
        return f"{d.get('status')}/{d.get('conclusion') or '-'} · {listos}/{len(jobs)} trabajos"
    except Exception as e:  # noqa: BLE001
        return f"no se pudo leer el run: {e}"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("ep")
    ap.add_argument("--id", required=True)
    ap.add_argument("--cada", type=int, default=900)
    ap.add_argument("--max", type=int, default=14400)
    ap.add_argument("--run")
    a = ap.parse_args()
    t0 = time.time()
    while time.time() - t0 < a.max:
        time.sleep(a.cada)
        if not abierto(a.ep, a.id):
            break
        est = "vivo (vigilante)" + (" · " + estado_run(a.run) if a.run else "")
        bitacora.anotar(a.ep, tipo="chequeo", id=a.id, estado=est)
        print(time.strftime("%H:%M"), a.id, est, flush=True)
