"""Renderiza una o varias piezas de planos del Ep. 2.

Uso: PIEZAS=1,2,23L RES=720x1280 SAMPLES=16 DIR=carpeta [MUESTRAS=3] [CUADROS=a-b] [DEVICE=OPTIX] python3 plano.py
- Cada pieza (planos_ep02.PIEZAS) arma su escena desde cero en un proceso nuevo y renderiza sus cuadros.
- Las piezas principales escriben DIR/NNNNN.png (cuadro global); las auxiliares (lupas, recuadros) DIR/aux/<pieza>_NNNNN.png.
- MUESTRAS=n renderiza sólo n cuadros repartidos en cada pieza (revisión rápida).
- Escribe DIR/meta/<pieza>.json con datos para el post (posiciones en pantalla, etc.).
"""
import json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))

if os.environ.get("_PIEZA") is None:
    # proceso padre: una pieza por proceso (cada escena empieza limpia)
    piezas = [p.strip() for p in os.environ["PIEZAS"].split(",") if p.strip()]
    falla = 0
    for p in piezas:
        t0 = time.time()
        r = subprocess.run([sys.executable, os.path.abspath(__file__)], env=dict(os.environ, _PIEZA=p))
        print(f"pieza {p}: {'ok' if r.returncode == 0 else 'FALLA'} en {time.time() - t0:.0f} s", flush=True)
        falla |= r.returncode != 0
    sys.exit(1 if falla else 0)

sys.path.insert(0, HERE)
import bpy
import ep02 as E2
import planos_ep02 as PL

pid = os.environ["_PIEZA"]
pz = PL.PIEZAS[pid]
a, b = pz["a"], pz["b"]
sc = E2.escena(f"pieza_{pid}")
res = pz["fn"](sc, a, b)
act = res["actualizar"]
w, h = (int(v) for v in os.environ.get("RES", "720x1280").split("x"))
if pz.get("cuadrado"):
    w = h = int(pz.get("lado", 0.75) * w)
sc.render.resolution_x, sc.render.resolution_y = w, h
sc.render.resolution_percentage = 100
sc.cycles.samples = int(os.environ.get("SAMPLES", 16)) if not pz.get("muestras_extra") else int(int(os.environ.get("SAMPLES", 16)) * pz["muestras_extra"])
sc.render.use_persistent_data = True
dev = os.environ.get("DEVICE", "").upper()
if dev:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for tipo in [dev] + [t for t in ("OPTIX", "CUDA") if t != dev]:
        try:
            prefs.compute_device_type = tipo
            prefs.get_devices()
            if [d for d in prefs.devices if d.type == tipo]:
                for d in prefs.devices:
                    d.use = d.type == tipo
                sc.cycles.device = "GPU"
                break
        except Exception:
            pass
d = os.environ.get("DIR", os.path.join(HERE, "out", "frames"))
aux = pz.get("aux")
dst = os.path.join(d, "aux") if aux else d
os.makedirs(dst, exist_ok=True)
os.makedirs(os.path.join(d, "meta"), exist_ok=True)
cuadros = list(range(a, b))
if pz.get("fijo"):
    cuadros = [a]
rng = os.environ.get("CUADROS", "").strip()
if rng:
    x, y = (int(v) for v in rng.split("-"))
    cuadros = [f for f in cuadros if x <= f <= y]
n = int(os.environ.get("MUESTRAS", "0") or 0)
if n and len(cuadros) > n:
    cuadros = sorted({cuadros[round(i * (len(cuadros) - 1) / (n - 1))] for i in range(n)}) if n > 1 else [cuadros[len(cuadros) // 2]]
meta = {"pieza": pid, "a": a, "b": b, "cuadros": {}}
t0 = time.time()
for f in cuadros:
    out = os.path.join(dst, (f"{pid}_" if aux else "") + f"{f:05d}.png")
    if os.path.exists(out) and not os.environ.get("FORCE"):
        continue
    info = act(f) or {}
    sc.frame_current = f
    bpy.context.view_layer.update()
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    if info:
        meta["cuadros"][str(f)] = info
meta.update(res.get("meta", {}))
json.dump(meta, open(os.path.join(d, "meta", f"{pid}.json"), "w"))
print(f"ok pieza {pid}: {len(cuadros)} cuadros en {time.time() - t0:.0f} s", flush=True)
