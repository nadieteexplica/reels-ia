"""words.json (subtítulos por palabra) desde cualquier locución, con Whisper. Reemplaza a tools/words.py (que
necesitaba los tiempos de ElevenLabs).

  python tools/voz_palabras.py voz.wav guion.txt words.json [--modelo medium] [--verdad words_elevenlabs.json]

- Las palabras salen del GUION (con su puntuación, tal como van en pantalla); de Whisper sólo se toman los tiempos.
  Así "quince" sigue diciendo "quince" aunque Whisper escriba "15".
- Guion y transcripción se alinean palabra a palabra (sin tildes ni mayúsculas). Donde no calzan (números,
  palabras que Whisper no oyó), el tramo se reparte por largo de palabra o se interpola entre vecinas.
- Los bordes se ajustan con la energía del audio: ninguna palabra se come un silencio (Whisper tiende a
  estirar el final de la palabra dentro de la pausa).
- Con --verdad compara contra un words.json conocido (p. ej. el de ElevenLabs) y muestra el error en ms.
Formato de salida: igual que tools/words.py, lista de {"w", "s", "e"} en segundos.
"""
import argparse, difflib, json, re, subprocess, unicodedata

import numpy as np

SR = 16000


def norm(t):
    t = unicodedata.normalize("NFKD", t.lower())
    return "".join(c for c in t if not unicodedata.combining(c) and (c.isalnum() or c == "ñ"))


def leer(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)


def silencios(x, umbral_db=-38, minimo=0.12):
    h = SR // 100
    n = len(x) // h
    rms = np.sqrt(np.mean(x[: n * h].reshape(n, h) ** 2, axis=1) + 1e-12)
    bajo = 20 * np.log10(rms / (np.abs(x).max() + 1e-9)) < umbral_db
    out, i = [], 0
    while i < n:
        if bajo[i]:
            j = i
            while j < n and bajo[j]:
                j += 1
            if (j - i) / 100 >= minimo:
                out.append((i / 100, j / 100))
            i = j
        else:
            i += 1
    return out


def alinear(guion, hyp):
    """guion: lista de palabras de pantalla; hyp: lista de (palabra, s, e) de Whisper. Devuelve [{w, s, e}]."""
    a = [norm(w) for w in guion]
    b = [norm(w) for w, _, _ in hyp]
    res = [None] * len(guion)
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            for k in range(i2 - i1):
                res[i1 + k] = [hyp[j1 + k][1], hyp[j1 + k][2]]
        elif op == "replace":
            s, e = hyp[j1][1], hyp[j2 - 1][2]
            largos = np.array([max(1, len(a[i])) for i in range(i1, i2)], float)
            cortes = s + (e - s) * np.concatenate([[0], np.cumsum(largos) / largos.sum()])
            for k in range(i2 - i1):
                res[i1 + k] = [cortes[k], cortes[k + 1]]
        # "delete" (palabra del guion que Whisper no oyó) queda en None y se interpola abajo
    # interpolar huecos entre vecinas conocidas
    i = 0
    while i < len(res):
        if res[i] is None:
            j = i
            while j < len(res) and res[j] is None:
                j += 1
            s = res[i - 1][1] if i > 0 else 0.0
            e = res[j][0] if j < len(res) else s + 0.3 * (j - i)
            paso = (e - s) / (j - i)
            for k in range(i, j):
                res[k] = [s + paso * (k - i), s + paso * (k - i + 1)]
            i = j
        else:
            i += 1
    return [{"w": w, "s": float(s), "e": float(e)} for w, (s, e) in zip(guion, res)]


def ajustar_bordes(words, sil):
    """Ninguna palabra empieza ni termina dentro de un silencio."""
    for w in words:
        for a, b in sil:
            if w["s"] < a < w["e"] and w["e"] - a < (w["e"] - w["s"]) * 0.6:
                w["e"] = a  # el final se metió en la pausa
            if a <= w["s"] < b and b < w["e"]:
                w["s"] = b  # empezó en la pausa
    for x, y in zip(words, words[1:]):  # orden y sin solapes
        if y["s"] < x["s"]:
            y["s"] = x["s"]
        if x["e"] > y["s"]:
            x["e"] = y["s"]
    for w in words:
        w["e"] = max(w["e"], w["s"] + 0.04)
        w["s"], w["e"] = round(w["s"], 3), round(w["e"], 3)
    return words


def errores(words, verdad):
    if len(words) != len(verdad):
        return {"error": f"{len(words)} palabras contra {len(verdad)}"}
    ds = np.array([abs(w["s"] - v["s"]) for w, v in zip(words, verdad)]) * 1000
    de = np.array([abs(w["e"] - v["e"]) for w, v in zip(words, verdad)]) * 1000
    peores = sorted(zip(ds, [w["w"] for w in words]), reverse=True)[:5]
    return {"inicio_ms": {"media": round(ds.mean()), "p90": round(np.percentile(ds, 90)), "max": round(ds.max())},
            "fin_ms": {"media": round(de.mean()), "p90": round(np.percentile(de, 90)), "max": round(de.max())},
            "inicios_a_mas_de_1_cuadro": int((ds > 1000 / 30).sum()), "peores_inicios": [[w, round(d)] for d, w in peores]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("guion")
    ap.add_argument("salida")
    # Medido el 23-nov contra los tiempos de ElevenLabs del Ep. 7: medium llega ~40 ms tarde y large-v3-turbo
    # ~59 ms temprano; el promedio de los dos queda sin sesgo (inicio: media 38 ms, p90 82, peor 167).
    ap.add_argument("--modelo", default="medium,large-v3-turbo", help="uno o varios separados por coma (se promedian)")
    ap.add_argument("--verdad")
    a = ap.parse_args()
    from faster_whisper import WhisperModel

    guion = open(a.guion, encoding="utf-8").read().split()
    x = leer(a.audio)
    por_modelo = []
    for nombre in a.modelo.split(","):
        m = WhisperModel(nombre, device="cpu", compute_type="int8")
        segs, _ = m.transcribe(x, language="es", word_timestamps=True, beam_size=5, vad_filter=False,
                               condition_on_previous_text=False)
        hyp = [(w.word.strip(), w.start, w.end) for s in segs for w in (s.words or []) if w.word.strip()]
        por_modelo.append(alinear(guion, hyp))
        del m
    crudo = [{"w": ws[0]["w"], "s": float(np.mean([w["s"] for w in ws])), "e": float(np.mean([w["e"] for w in ws]))}
             for ws in zip(*por_modelo)]
    words = ajustar_bordes([dict(w) for w in crudo], silencios(x))
    json.dump(words, open(a.salida, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    largas = [w["w"] for w in words if w["e"] - w["s"] > 1.2]
    print(f"{a.salida}: {len(words)} palabras · {words[-1]['e']:.2f} s de {len(x) / SR:.2f} s"
          + (f" · OJO palabras > 1,2 s: {largas}" if largas else ""))
    if a.verdad:
        verdad = json.load(open(a.verdad, encoding="utf-8"))
        r = {"con_bordes": errores(words, verdad), "sin_bordes": errores(ajustar_bordes([dict(w) for w in crudo], []), verdad)}
        print("contra la verdad:", json.dumps(r, ensure_ascii=False))
        json.dump(r, open(re.sub(r"\.json$", "", a.salida) + "_error.json", "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
