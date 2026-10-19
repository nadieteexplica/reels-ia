"""Pone clips de Kling en lugar de los cuadros de Blender de ciertos planos, antes del post (subtítulos y etiquetas
van encima igual que en cualquier cuadro).

Uso: python kling_insert.py <kling/planos.json> <carpeta_clips> <carpeta_cuadros> <*_planos.json>
kling/planos.json: [{"plano": 26, "clip": "p26_taza.mp4", "desde": 0.3, "velocidad": 1.0}]
  desde: segundo del clip donde parte el plano · velocidad: 1 = tiempo real (0,8 = más lento)
"""
import json, os, subprocess, sys, tempfile

mapa, clips, cuadros, planos = sys.argv[1:5]
FR = {int(k): v for k, v in json.load(open(planos))["FR"].items()}
for it in json.load(open(mapa)):
    k = int(it["plano"])
    f0, f1 = FR[k]
    n = f1 - f0
    src = os.path.join(clips, it["clip"])
    if not os.path.exists(src):
        sys.exit(f"falta el clip {src}")
    vel = float(it.get("velocidad", 1.0))
    desde = float(it.get("desde", 0.0))
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                               capture_output=True, text=True).stdout)
    if desde + n / 30 * vel > dur + 0.05:
        sys.exit(f"plano {k}: el clip dura {dur:.2f} s y el plano necesita {desde + n / 30 * vel:.2f} s")
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{desde:.3f}", "-i", src, "-vf",
                        f"setpts=PTS/{vel},fps=30,scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920",
                        "-frames:v", str(n), "-start_number", str(f0), os.path.join(tmp, "%05d.png")], check=True)
        hechos = 0
        for f in range(f0, f1):
            p = os.path.join(tmp, f"{f:05d}.png")
            if os.path.exists(p):
                os.replace(p, os.path.join(cuadros, f"{f:05d}.png"))
                hechos += 1
    print(f"plano {k}: {hechos}/{n} cuadros desde {it['clip']} (desde {desde} s, x{vel})")
    if hechos < n:
        sys.exit(f"plano {k}: faltaron cuadros")
