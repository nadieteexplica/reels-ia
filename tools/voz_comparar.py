"""Compara locuciones contra el guion, sin saber cuál es cuál (para la prueba ciega de voz).

Transcribe cada audio con faster-whisper (sin darle el guion, para no tapar errores) y mide:
  - error de palabras (WER) contra el guion, y qué palabras salieron distintas,
  - duración, palabras por segundo,
  - pausas largas (> 0,7 s) y palabras estiradas (> 1,2 s),
  - palabras que Whisper entendió con poca seguridad (p < 0,5): pista de pronunciación rara.

  .venv/bin/python tools/voz_comparar.py guion.txt carpeta_con_audios/ [--modelo medium]
Escribe <carpeta>/metricas.json y muestra una tabla.
"""
import argparse, difflib, json, pathlib, re, subprocess, unicodedata


def norm(t):
    t = unicodedata.normalize("NFKD", t.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.findall(r"[a-zñ0-9]+", t)


def duracion(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("guion")
    ap.add_argument("carpeta")
    ap.add_argument("--modelo", default="medium")
    a = ap.parse_args()
    from faster_whisper import WhisperModel

    ref = norm(pathlib.Path(a.guion).read_text())
    m = WhisperModel(a.modelo, device="cpu", compute_type="int8")
    res = {}
    for f in sorted(pathlib.Path(a.carpeta).iterdir()):
        if f.suffix.lower() not in (".wav", ".mp3", ".m4a"):
            continue
        segs, _ = m.transcribe(str(f), language="es", word_timestamps=True, beam_size=5, vad_filter=False,
                               condition_on_previous_text=False)
        pal = [w for s in segs for w in (s.words or [])]
        hyp = norm(" ".join(w.word for w in pal))
        sm = difflib.SequenceMatcher(a=ref, b=hyp, autojunk=False)
        errores, dif = 0, []
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op != "equal":
                errores += max(i2 - i1, j2 - j1)
                dif.append(f"{' '.join(ref[i1:i2]) or '∅'} → {' '.join(hyp[j1:j2]) or '∅'}")
        dur = duracion(f)
        pausas = [round(b.start - a_.end, 2) for a_, b in zip(pal, pal[1:]) if b.start - a_.end > 0.7]
        estiradas = [w.word.strip() for w in pal if w.end - w.start > 1.2]
        dudosas = [w.word.strip() for w in pal if w.probability < 0.5]
        res[f.name] = {
            "duracion_s": round(dur, 1),
            "pal_por_s": round(len(ref) / dur, 2),
            "wer_%": round(100 * errores / len(ref), 1),
            "diferencias": dif,
            "pausas_largas": pausas,
            "estiradas": estiradas,
            "dudosas": dudosas,
        }
    out = pathlib.Path(a.carpeta) / "metricas.json"
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1))
    print(f"{'audio':<14}{'dur':>6}{'pal/s':>7}{'WER%':>6}{'pausas>0,7':>11}{'dudosas':>9}")
    for k, v in res.items():
        print(f"{k:<14}{v['duracion_s']:>6}{v['pal_por_s']:>7}{v['wer_%']:>6}{len(v['pausas_largas']):>11}{len(v['dudosas']):>9}")
        for d in v["diferencias"]:
            print("     ", d)


if __name__ == "__main__":
    main()
