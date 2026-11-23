"""QA del video a tamaño celular (skill qa-video). Dos pasos:

  python3 tools/qa_video.py preparar <ep> <video.mp4>
      → studio/episodios/<ep>/qa/: tecnico.json (tools/qa.py: duración, formato, volumen, cuadros negros),
        hook.jpg (0–3 s cada 0,5 s), hojas/hoja-N.jpg (1 cuadro por segundo a 405×720, con su segundo),
        subtitulos.md (qué dice la voz en cada segundo, desde words.json). Eso es lo único que ve auditor-final.
  (se lanza auditor-final con la carpeta qa/; su JSON se guarda en qa/auditor_final.json)
  python3 tools/qa_video.py cerrar <ep>
      → qa/qa.json con "aprobado": true sólo si tools/qa.py pasó y auditor-final aprobó (sin bloqueantes,
        notas ≥ 7, promedio ≥ 8). Guarda la huella (sha256) de las fuentes del episodio: si después se toca
        el guion, la voz, el sonido o el código de la escena, la aprobación deja de valer y el hook
        (tools/hooks/puertas.py) no deja renderizar el final.

qa.json lo escribe SÓLO este script (el hook bloquea escribirlo a mano).
"""
import hashlib, json, subprocess, sys, time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[1]
FUENTE = RAIZ / "studio/plantilla/fonts/Inter-ExtraBold.otf"
TW, TH = 405, 720  # tamaño celular (≈ el ancho real en pantalla de un teléfono)
# lo que define el video: si cambia algo de esto después del QA, hay que volver a pasarlo
PATRONES_FUENTE = ["escena2d/*.py", "escena/*.py", "words*.json", "guion.md", "storyboard.*", "sfx-plan.json", "voz/*", "*.wav"]


def ep_dir(ep):
    d = RAIZ / "studio/episodios" / ep
    if not d.is_dir():
        sys.exit(f"no existe {d}")
    return d


def huella(ep):
    d = ep_dir(ep)
    h = hashlib.sha256()
    archivos = sorted({p for pat in PATRONES_FUENTE for p in d.glob(pat) if p.is_file() and "/qa/" not in str(p)})
    for p in archivos:
        h.update(str(p.relative_to(d)).encode())
        h.update(p.read_bytes())
    return h.hexdigest(), [str(p.relative_to(d)) for p in archivos]


def cuadro(video, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1",
                          "-vf", f"scale={TW}:{TH}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    if len(raw) < TW * TH * 3:
        return Image.new("RGB", (TW, TH), (40, 0, 0))
    return Image.frombytes("RGB", (TW, TH), raw[: TW * TH * 3])


def rotular(im, txt):
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(str(FUENTE), 26)
    d.rectangle([0, 0, 110, 36], fill=(0, 0, 0))
    d.text((8, 4), txt, font=f, fill=(255, 230, 0))
    return im


def hoja(imgs, cols, filas):
    h = Image.new("RGB", (cols * TW + (cols - 1) * 8, filas * TH + (filas - 1) * 8), (90, 90, 90))
    for i, im in enumerate(imgs):
        h.paste(im, ((i % cols) * (TW + 8), (i // cols) * (TH + 8)))
    return h


def duracion(video):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)]))


def preparar(ep, video):
    d = ep_dir(ep)
    q = d / "qa"
    (q / "hojas").mkdir(parents=True, exist_ok=True)
    for f in (q / "hojas").glob("*.jpg"):
        f.unlink()
    for viejo in ("auditor_final.json", "qa.json"):
        (q / viejo).unlink(missing_ok=True)
    r = subprocess.run([sys.executable, str(RAIZ / "tools/qa.py"), str(video)], capture_output=True, text=True)
    dur = duracion(video)
    (q / "tecnico.json").write_text(json.dumps({"video": str(video), "duracion_s": round(dur, 2), "pasa": r.returncode == 0,
                                                 "detalle": r.stdout.strip().splitlines()}, ensure_ascii=False, indent=1))
    hook = [rotular(cuadro(video, t), f"{t:.1f}s") for t in [0, 0.5, 1, 1.5, 2, 2.5, 3]]
    hoja(hook + [Image.new("RGB", (TW, TH), (90, 90, 90))], 4, 2).save(q / "hook.jpg", quality=82)
    ts = [float(t) for t in range(int(dur) + 1)]
    for n in range(0, len(ts), 6):
        ims = [rotular(cuadro(video, min(t, dur - 0.05)), f"{t:.0f}s") for t in ts[n:n + 6]]
        hoja(ims, 3, 2).save(q / "hojas" / f"hoja-{n // 6 + 1:02d}.jpg", quality=80)
    words = next((p for p in [d / "words.json", *sorted(d.glob("words*.json"))] if p.exists()), None)
    lineas = ["# Qué dice la voz en cada segundo", ""]
    if words:
        por_seg = {}
        for w in json.load(open(words)):
            por_seg.setdefault(int(w["s"]), []).append(w["w"])
        lineas += [f"- {s:>2} s: {' '.join(ws)}" for s, ws in sorted(por_seg.items())]
    else:
        lineas.append("(no hay words.json en el episodio)")
    (q / "subtitulos.md").write_text("\n".join(lineas) + "\n")
    print(f"listo en {q}: técnico {'OK' if r.returncode == 0 else 'FALLA'}, {len(list((q / 'hojas').glob('*.jpg')))} hojas. "
          f"Ahora lanza auditor-final con la carpeta {q} y guarda su JSON en {q / 'auditor_final.json'}.")


def cerrar(ep):
    q = ep_dir(ep) / "qa"
    tec = json.load(open(q / "tecnico.json"))
    try:
        aud = json.load(open(q / "auditor_final.json"))
    except FileNotFoundError:
        sys.exit("falta qa/auditor_final.json (el veredicto de auditor-final)")
    notas = list(aud.get("notas", {}).values())
    aud_ok = bool(aud.get("aprobado")) and not aud.get("bloqueantes") and notas and min(notas) >= 7 and sum(notas) / len(notas) >= 8
    h, archivos = huella(ep)
    res = {"aprobado": bool(tec["pasa"] and aud_ok), "tecnico_pasa": tec["pasa"], "auditor_aprueba": aud_ok,
           "bloqueantes": aud.get("bloqueantes", []), "video": tec["video"], "fecha": time.strftime("%Y-%m-%d %H:%M"),
           "huella_fuentes": h, "fuentes": archivos}
    (q / "qa.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    print(("APROBADO" if res["aprobado"] else "NO APROBADO") + f" · técnico {tec['pasa']} · auditor {aud_ok}")
    sys.exit(0 if res["aprobado"] else 1)


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "preparar" and len(sys.argv) == 4:
        preparar(sys.argv[2], Path(sys.argv[3]))
    elif len(sys.argv) == 3 and sys.argv[1] == "cerrar":
        cerrar(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "huella":
        print(huella(sys.argv[2])[0])
    else:
        sys.exit(__doc__)
