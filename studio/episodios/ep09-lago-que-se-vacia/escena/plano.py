"""Renderiza una o varias piezas de planos del Ep. 5.

Uso: PIEZAS=1,2,23L RES=720x1280 SAMPLES=16 DIR=carpeta [MUESTRAS=3] [CUADROS=a-b] [DEVICE=OPTIX] python3 plano.py
- Cada pieza (planos_ep07.PIEZAS) arma su escena desde cero en un proceso nuevo y renderiza sus cuadros.
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
import ep07 as E2
import planos_ep07 as PL
import caras            # studio/plantilla/caras.py (planos_ep07 deja studio/plantilla en sys.path)

pid = os.environ["_PIEZA"]
pz = PL.PIEZAS[pid]
a, b = pz["a"], pz["b"]
sc = E2.escena(f"pieza_{pid}", (720, 1280), 16)
sc.render.fps = 30
sc.cycles.volume_step_rate = 4.0           # vapor de la central: pasos más largos (barato, se ve igual de lejos)
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
if pz.get("rango"):
    cuadros = [f for f in cuadros if pz["rango"][0] <= f < pz["rango"][1]]
rng = os.environ.get("CUADROS", "").strip()
if rng:
    x, y = (int(v) for v in rng.split("-"))
    cuadros = [f for f in cuadros if x <= f <= y]
n = int(os.environ.get("MUESTRAS", "0") or 0)
if n and len(cuadros) > n:
    cuadros = sorted({cuadros[round(i * (len(cuadros) - 1) / (n - 1))] for i in range(n)}) if n > 1 else [cuadros[len(cuadros) // 2]]
meta = {"pieza": pz.get("base", pid), "a": a, "b": b, "cuadros": {}}
t0 = time.time()
for f in cuadros:
    out = os.path.join(dst, (f"{pid}_" if aux else "") + f"{f:05d}.png")
    if os.path.exists(out) and not os.environ.get("FORCE"):
        continue
    info = act(f) or {}
    sc.frame_current = f
    bpy.context.view_layer.update()
    if not aux:          # dónde quedan los ojos en pantalla → chequeo automático "cara tapada" (tools/auditor/chequeo_planos.py)
        # el tubo de vidrio no tapa los ojos de la rana (se ve a través): se saca de los rayos sólo para esta medición
        vidrios = [o for o in sc.objects if o.get("no_tapa_ojos")]
        for o in vidrios:
            o.hide_viewport = True
        bpy.context.view_layer.update()
        ojos = caras.ojos_en_pantalla(sc)
        for o in vidrios:
            o.hide_viewport = False
        bpy.context.view_layer.update()
        if ojos:
            info = dict(info, ojos=ojos)
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    if info:
        meta["cuadros"][str(f)] = info
meta.update(res.get("meta", {}))
json.dump(meta, open(os.path.join(d, "meta", f"{pid}.json"), "w"))
print(f"ok pieza {pid}: {len(cuadros)} cuadros en {time.time() - t0:.0f} s", flush=True)
