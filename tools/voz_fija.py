"""Voz fija: clona la voz de referencia de voz/<nombre>.wav en varios guiones y mide si suena igual en todos.

El diseño desde texto (VoiceDesign) puede cambiar un poco de un video a otro. Con el modelo Base, cada trozo de
cada guion se genera copiando la misma referencia, así que la voz queda fija. Para comprobarlo se compara la
"huella de voz" (el codificador de hablante del propio Qwen3-TTS) de cada trozo contra la referencia:
similitud coseno 1 = idéntica.

  .venv-voz/bin/python tools/voz_fija.py jobs/voz-libre/<trabajo>.json

Trabajo: {"id": "fija-narrador", "voz": "narrador", "textos": {"ep07": "studio/voz-prueba/ep07.txt", ...},
          "comparar_con": {"ep07_disenada": "out/voz-libre/ep07/originales/B_narrador_doc.wav"}}   (opcional)
Deja en out/voz-libre/<id>/: <texto>_original.wav, <texto>.wav (pausas apretadas, tools/voz_ajustar.py) y
huella.json (similitud por trozo). Después: tools/voz_comparar.py <guion> <carpeta> para la pronunciación.
"""
import json, pathlib, re, subprocess, sys, time

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from voz_libre import SR, cargar, locutar  # noqa: E402


def main():
    import mlx.core as mx
    import soundfile as sf

    job = json.loads((ROOT / sys.argv[1]).read_text())
    voz = json.loads((ROOT / "voz" / f"{job['voz']}.json").read_text())
    ref = str(ROOT / "voz" / f"{job['voz']}.wav")
    out = ROOT / "out" / "voz-libre" / job["id"]
    out.mkdir(parents=True, exist_ok=True)

    model = cargar("clon")

    def huella(audio):
        e = np.array(model.extract_speaker_embedding(mx.array(audio.astype(np.float32)))).reshape(-1)
        return e / np.linalg.norm(e)

    ref_audio, sr = sf.read(ref, dtype="float32")
    assert sr == SR, f"la referencia tiene que estar a {SR} Hz"
    h_ref = huella(ref_audio)
    res = {"referencia": ref, "trozos": {}, "comparar_con": {}}

    for nombre, archivo in job["textos"].items():
        t0 = time.time()
        texto = (ROOT / archivo).read_text()
        wav, piezas = locutar(model, "clon", texto, ref=ref, ref_texto=voz["texto_ref"])
        crudo = out / f"{nombre}_original.wav"
        sf.write(crudo, wav, SR)
        palabras = len(re.findall(r"\w+", texto))
        subprocess.run([sys.executable, str(ROOT / "tools/voz_ajustar.py"), crudo, out / f"{nombre}.wav", "--palabras", str(palabras)], check=True)
        res["trozos"][nombre] = [round(float(huella(p) @ h_ref), 3) for p in piezas]
        print(f"{nombre}: {len(wav) / SR:.1f}s en {time.time() - t0:.0f}s, huella por trozo {res['trozos'][nombre]}", flush=True)

    # la voz diseñada original, trozo a trozo, como punto de comparación (¿variaba ya dentro de un mismo audio?)
    for nombre, archivo in job.get("comparar_con", {}).items():
        a, sr = sf.read(ROOT / archivo, dtype="float32")
        if sr != SR:
            continue
        n = int(10 * SR)
        res["comparar_con"][nombre] = [round(float(huella(a[i:i + n]) @ h_ref), 3) for i in range(0, len(a) - SR * 3, n)]

    (out / "huella.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    print(json.dumps(res, ensure_ascii=False))
    print(f"mem pico {mx.get_peak_memory() / 1e9:.2f} GB")


if __name__ == "__main__":
    main()
