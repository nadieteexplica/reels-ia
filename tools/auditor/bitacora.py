"""Bitácora del proceso de un episodio: lo que el auditor de proceso cruza con GitHub y los saldos.
Se escribe MIENTRAS se trabaja, una línea por hecho, en studio/episodios/<ep>/auditoria/proceso.jsonl.

  python3 tools/auditor/bitacora.py <ep> promesa  --hora 18:40 --que "video completo" --dato "progreso.txt 540/2160 en 12 min = 1,33 s/cuadro"
  python3 tools/auditor/bitacora.py <ep> aviso    --que "se atrasa a 19:10: el pod va a 1,8 s/cuadro"   (cada aviso a Tomás)
  python3 tools/auditor/bitacora.py <ep> cumplida --id 3                                            (la promesa n.º 3 se cumplió ahora)
  python3 tools/auditor/bitacora.py <ep> trabajo  --id "render-gpu 39290639291" --estado inicio|fin|caido
  python3 tools/auditor/bitacora.py <ep> chequeo  --id "render-gpu 39290639291" --estado "vivo, 812/2160"
  python3 tools/auditor/bitacora.py <ep> gasto    --servicio kling|runpod|eleven --monto 4 --nota "p3_frente_b"
     (kling en unidades, runpod en USD, eleven en créditos)

Los runs de GitHub Actions se ven solos; los trabajos que GitHub no ve (pods, subagentes) se anotan con 'trabajo'.
"""
import argparse, datetime, json, os, sys
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(__file__))
import comun

TZ = ZoneInfo("America/Santiago")


def ruta(ep):
    return os.path.join(comun.ep_dir(ep), "auditoria", "proceso.jsonl")


def leer(ep):
    p = ruta(ep)
    if not os.path.exists(p):
        return []
    return [json.loads(l) for l in open(p) if l.strip()]


def anotar(ep, **kw):
    p = ruta(ep)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    previas = leer(ep)
    kw = {k: v for k, v in kw.items() if v is not None}
    kw["n"] = len(previas) + 1
    kw["ts"] = datetime.datetime.now(TZ).isoformat(timespec="seconds")
    with open(p, "a") as f:
        f.write(json.dumps(kw, ensure_ascii=False) + "\n")
    return kw


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("ep")
    ap.add_argument("tipo", choices=["promesa", "aviso", "cumplida", "trabajo", "chequeo", "gasto"])
    ap.add_argument("--hora")
    ap.add_argument("--que")
    ap.add_argument("--dato")
    ap.add_argument("--id")
    ap.add_argument("--estado")
    ap.add_argument("--servicio")
    ap.add_argument("--monto", type=float)
    ap.add_argument("--nota")
    a = ap.parse_args()
    if a.tipo == "promesa" and not (a.hora and a.dato):
        sys.exit("una promesa necesita --hora y --dato (la medición que la respalda)")
    if a.tipo == "gasto" and not (a.servicio and a.monto is not None):
        sys.exit("un gasto necesita --servicio y --monto")
    e = anotar(a.ep, tipo=a.tipo, hora=a.hora, que=a.que, dato=a.dato, id=a.id, estado=a.estado,
               servicio=a.servicio, monto=a.monto, nota=a.nota)
    print(json.dumps(e, ensure_ascii=False))
