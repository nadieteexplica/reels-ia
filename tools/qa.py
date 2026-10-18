"""QA automático de un episodio (manual §9.1).

Uso: python3 tools/qa.py video.mp4 [carpeta_cuadros_sin_subtitulos] [subs_log.json]
Sale con código 1 si algo no pasa.
"""
import json, re, subprocess, sys, glob, os

vid = sys.argv[1]
raw_dir = sys.argv[2] if len(sys.argv) > 2 else None
subs = sys.argv[3] if len(sys.argv) > 3 else None
ok = True


def check(name, cond, detail=""):
    global ok
    ok &= bool(cond)
    print(("✅" if cond else "❌"), name, detail)


p = json.loads(subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", vid], capture_output=True, text=True).stdout)
v = next(s for s in p["streams"] if s["codec_type"] == "video")
dur = float(p["format"]["duration"])
size = int(p["format"]["size"]) / 1e6
fps = eval(v["r_frame_rate"])
check("duración 62–75 s", 62 <= dur <= 75, f"{dur:.2f} s")
check("1080×1920", (v["width"], v["height"]) == (1080, 1920), f"{v['width']}×{v['height']}")
check("30 fps", abs(fps - 30) < 0.01, f"{fps:.2f}")
check("H.264 yuv420p", v["codec_name"] == "h264" and v["pix_fmt"] == "yuv420p", f"{v['codec_name']} {v['pix_fmt']}")
check("pesa < 100 MB", size < 100, f"{size:.1f} MB")
e = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", vid, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", e)[-1])
TP = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", e)[-1])
check("volumen −14 ±1 LUFS", abs(I + 14) <= 1, f"{I} LUFS")
check("true peak ≤ −1 dBTP", TP <= -1.0, f"{TP} dBTP")
bd = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", vid, "-vf", "blackdetect=d=0.5:pix_th=0.08,freezedetect=n=0.001:d=0.5", "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
blacks = re.findall(r"black_start:([\d.]+)", bd)
freezes = re.findall(r"freeze_start: ([\d.]+)", bd)
check("sin negros > 0,5 s", not blacks, str(blacks))
check("sin congelados > 0,5 s", not freezes, str(freezes))
if raw_dir:
    from PIL import Image
    import numpy as np
    files = sorted(glob.glob(os.path.join(raw_dir, "*.png")))[::30]
    worst = 0
    for f in files:
        a = np.asarray(Image.open(f).convert("L"))
        worst = max(worst, float((a > 250).mean()))
    check("quemados < 3 % (sin subtítulos)", worst < 0.03, f"peor cuadro {worst * 100:.2f} %")
if subs:
    log = json.load(open(subs))
    bad = [r for r in log if r[2] < 115 or r[4] > 893 or r[3] < 995 or r[5] > 1255]
    check("subtítulos dentro de x 120–888 · y 1000–1250", not bad, f"{len(bad)} cajas fuera" if bad else f"{len(log)} cajas")
print("RESULTADO:", "PASA" if ok else "NO PASA")
sys.exit(0 if ok else 1)
