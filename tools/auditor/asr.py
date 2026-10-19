"""Transcribe las locuciones (out/tts/*.mp3) con Whisper para revisar la pronunciación contra el guion.
Corre en GitHub Actions (workflow asr.yml): el modelo se baja de Hugging Face, que no está permitido desde el espacio de trabajo.
Sin "initial_prompt": darle el guion a Whisper taparía justamente los errores de pronunciación.

  python tools/auditor/asr.py [ids...]   (sin ids: todas las locuciones que todavía no tienen out/asr/<id>.json)
"""
import glob, json, os, sys

from faster_whisper import WhisperModel

ids = sys.argv[1:] or [os.path.splitext(os.path.basename(p))[0] for p in sorted(glob.glob("out/tts/*.mp3"))
                       if not os.path.exists(f"out/asr/{os.path.splitext(os.path.basename(p))[0]}.json")]
if not ids:
    print("nada que transcribir")
    sys.exit(0)
modelo = os.environ.get("ASR_MODELO", "medium")
m = WhisperModel(modelo, device="cpu", compute_type="int8")
os.makedirs("out/asr", exist_ok=True)
for i in ids:
    segs, info = m.transcribe(f"out/tts/{i}.mp3", language="es", word_timestamps=True, beam_size=5, vad_filter=False,
                              condition_on_previous_text=False)
    pal, txt = [], []
    for s in segs:
        txt.append(s.text.strip())
        for w in s.words or []:
            pal.append({"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2), "p": round(w.probability, 3)})
    json.dump({"id": i, "modelo": f"faster-whisper {modelo} int8", "texto": " ".join(txt), "palabras": pal},
              open(f"out/asr/{i}.json", "w"), ensure_ascii=False, indent=0)
    print(i, len(pal), "palabras")
