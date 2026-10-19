"""Renderiza cuadros sueltos o un rango del Ep. 1.  FRAMES="a-b" o "1,5,9"  RES=WxH  SAMPLES=n  DIR=carpeta"""
import json, os, sys
import bpy
OUT = os.environ.get("OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"))
bpy.ops.wm.open_mainfile(filepath=os.environ.get("BLEND", os.path.join(OUT, "ep01.blend")))
sc = bpy.context.scene
w, h = (int(v) for v in os.environ.get("RES", "1080x1920").split("x"))
sc.render.resolution_x, sc.render.resolution_y = w, h
sc.cycles.samples = int(os.environ.get("SAMPLES", 24))
sc.render.use_persistent_data = True
dev = os.environ.get("DEVICE", "").upper()   # OPTIX o CUDA en la GPU arrendada (RunPod); vacío = CPU
if dev:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    ok = False
    for tipo in ([dev] + [t for t in ("OPTIX", "CUDA") if t != dev]):
        try:
            prefs.compute_device_type = tipo
            prefs.get_devices()
            gpus = [d for d in prefs.devices if d.type == tipo]
        except Exception:
            gpus = []
        if gpus:
            for d in prefs.devices:
                d.use = d.type == tipo
            sc.cycles.device = "GPU"
            sc.cycles.denoising_use_gpu = True
            print("dispositivo", tipo, [d.name for d in gpus], flush=True)
            ok = True
            break
    if not ok:
        print("dispositivo CPU (no se encontró GPU)", flush=True)
spec = os.environ["FRAMES"]
if "-" in spec and "," not in spec:
    a, b = (int(x) for x in spec.split("-"))
    frames = list(range(a, b + 1))
else:
    frames = [int(x) for x in spec.split(",")]
d = os.environ.get("DIR", os.path.join(OUT, "frames"))
os.makedirs(d, exist_ok=True)
skip = set(json.loads(os.environ.get("SKIP", "[]")))
for f in frames:
    if f in skip:
        continue
    p = os.path.join(d, f"{f:05d}.png")
    if os.path.exists(p) and not os.environ.get("FORCE"):
        continue
    sc.frame_set(f)
    sc.render.filepath = p
    bpy.ops.render.render(write_still=True)
print("ok frames", len(frames))
