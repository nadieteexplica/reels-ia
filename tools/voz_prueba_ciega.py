"""Prueba ciega de voz: Qwen3-TTS (voces diseñadas) contra la locución publicada de ElevenLabs.

  .venv-voz/bin/python tools/voz_prueba_ciega.py jobs/voz-libre/<trabajo>.json

Trabajo (JSON):
  {"id": "ep07", "guion": "studio/voz-prueba/ep07.txt",
   "voces": "studio/voz-prueba/voces.json",              # nombre -> descripción
   "referencia": "out/tts/ep07-rascacielos-encoge-v2.mp3", # lo publicado (ElevenLabs)
   "clon": {"ref": "...wav", "ref_texto": "..."}}          # opcional: la voz de Tomás

Deja en out/voz-libre/<id>/:
  originales/<nombre>.wav     (con nombre, tal como sale de Qwen)
  ajustadas/<nombre>.wav      (pausas > 0,3 s acortadas y hasta 1,2× más rápida: tools/voz_ajustar.py; así se usaría en un video)
  ciega/A.mp3, B.mp3, ...     (mismo volumen, orden al azar: para escuchar sin saber cuál es cuál)
  clave.json                  (qué letra es cuál: NO abrir antes de votar)
  ciega/metricas.json         (Whisper contra el guion, por letra; ver tools/voz_comparar.py)
"""
import json, pathlib, random, re, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = sys.executable


def sh(*cmd):
    print("+", " ".join(map(str, cmd))[:200], flush=True)
    subprocess.run(list(map(str, cmd)), check=True, cwd=ROOT)


def main():
    job = json.loads((ROOT / sys.argv[1]).read_text())
    out = ROOT / "out" / "voz-libre" / job["id"]
    orig, ciega = out / "originales", out / "ciega"
    for d in (orig, ciega):
        d.mkdir(parents=True, exist_ok=True)

    voces = json.loads((ROOT / job["voces"]).read_text())
    for nombre, desc in voces.items():
        destino = orig / f"{nombre}.wav"
        if not destino.exists():
            sh(PY, "tools/voz_libre.py", "diseno", "--texto", job["guion"], "--voz", desc, "--out", destino)
    if job.get("clon"):
        destino = orig / "clon_tomas.wav"
        if not destino.exists():
            c = job["clon"]
            sh(PY, "tools/voz_libre.py", "clon", "--texto", job["guion"], "--ref", c["ref"], "--ref-texto", c["ref_texto"], "--out", destino)
    shutil.copy(ROOT / job["referencia"], orig / ("elevenlabs" + pathlib.Path(job["referencia"]).suffix))

    # Qwen deja pausas de hasta 1,4 s: se aprietan como en producción (ElevenLabs va tal como se publicó).
    ajust = out / "ajustadas"
    ajust.mkdir(exist_ok=True)
    palabras = len(re.findall(r"\w+", (ROOT / job["guion"]).read_text()))
    for f in sorted(orig.glob("*.wav")):
        sh(PY, "tools/voz_ajustar.py", f, ajust / f.name, "--palabras", palabras)
    shutil.copy(orig / ("elevenlabs" + pathlib.Path(job["referencia"]).suffix), ajust)

    # Orden al azar y mismo volumen percibido (-16 LUFS), para que nadie gane por sonar más fuerte.
    for f in ciega.glob("*.mp3"):
        f.unlink()
    fuentes = sorted(ajust.iterdir())
    random.Random(job["id"]).shuffle(fuentes)  # mismo orden si se vuelve a correr
    clave = {}
    for letra, f in zip("ABCDEFGH", fuentes):
        sh("ffmpeg", "-y", "-v", "error", "-i", f, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "44100", "-b:a", "192k", ciega / f"{letra}.mp3")
        clave[letra] = f.stem
    (out / "clave.json").write_text(json.dumps(clave, ensure_ascii=False, indent=1))
    print("listo:", ", ".join(sorted(clave)), "→ clave en", out / "clave.json")


if __name__ == "__main__":
    main()
