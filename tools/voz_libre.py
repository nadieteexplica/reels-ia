"""Voz gratis y local con Qwen3-TTS (MLX, Apple Silicon). Candidata a reemplazar tools/eleven.py.

Licencia: Qwen3-TTS es Apache-2.0 (código y pesos), uso comercial OK.
Regla: sólo voces diseñadas desde texto o la voz de Tomás. Nunca clonar a otra persona.

Uso (con el entorno .venv-voz):
  # voz diseñada desde una descripción
  .venv-voz/bin/python tools/voz_libre.py diseno --texto guion.txt --voz "Hombre de 65 años..." --out salida.wav
  # clon de una voz de referencia (la de Tomás o una voz diseñada, para que suene igual en todos los videos)
  .venv-voz/bin/python tools/voz_libre.py clon --texto guion.txt --ref ref.wav --ref-texto "lo que dice ref.wav" --out salida.wav

El guion se parte por oraciones y se genera de a trozos (más estable que todo de una en 8 GB de RAM);
entre trozos se deja una pausa corta. Los subtítulos por palabra salen después con Whisper (tools/auditor/asr.py).
"""
import argparse, pathlib, re, sys, time

import numpy as np

MODELOS = {
    "diseno": "mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-8bit",
    "clon": "mlx-community/Qwen3-TTS-12Hz-1.7B-Base-8bit",
}
SR = 24000


def trozos(texto, max_chars=220):
    """Junta oraciones hasta ~max_chars para que cada trozo tenga contexto pero no se desborde."""
    oraciones = [o.strip() for o in re.split(r"(?<=[.!?…])\s+", texto.strip()) if o.strip()]
    out, cur = [], ""
    for o in oraciones:
        if cur and len(cur) + 1 + len(o) > max_chars:
            out.append(cur); cur = o
        else:
            cur = (cur + " " + o).strip()
    if cur:
        out.append(cur)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("modo", choices=["diseno", "clon"])
    ap.add_argument("--texto", required=True, help="archivo .txt con el guion, o el texto mismo")
    ap.add_argument("--voz", help="descripción de la voz (modo diseno)")
    ap.add_argument("--ref", help="wav de referencia (modo clon)")
    ap.add_argument("--ref-texto", help="transcripción exacta del wav de referencia (modo clon)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--modelo", help="otro checkpoint de mlx-community")
    ap.add_argument("--pausa", type=float, default=0.18, help="segundos de silencio entre trozos")
    ap.add_argument("--temperatura", type=float, default=None)
    ap.add_argument("--semilla", type=int, default=7)
    a = ap.parse_args()

    import mlx.core as mx
    import soundfile as sf
    from mlx_audio.tts.utils import load_model

    if not mx.metal.is_available():  # p. ej. una máquina virtual sin GPU: más lento, mismo resultado
        mx.set_default_device(mx.cpu)
        print("sin Metal: corre en CPU", file=sys.stderr)
    p = pathlib.Path(a.texto)
    texto = p.read_text() if p.exists() else a.texto
    mx.random.seed(a.semilla)
    t0 = time.time()
    model = load_model(a.modelo or MODELOS[a.modo])
    print(f"modelo cargado en {time.time() - t0:.1f}s", file=sys.stderr)

    partes, sil = [], np.zeros(int(SR * a.pausa), dtype=np.float32)
    for i, t in enumerate(trozos(texto)):
        t1 = time.time()
        if a.modo == "diseno":
            gen = model.generate_voice_design(text=t, instruct=a.voz, language="spanish", temperature=a.temperatura)
        else:
            gen = model.generate(text=t, ref_audio=a.ref, ref_text=a.ref_texto, lang_code="spanish", temperature=a.temperatura)
        audio = np.concatenate([np.array(r.audio, dtype=np.float32) for r in gen])
        partes += [audio, sil]
        print(f"trozo {i + 1}: {len(audio) / SR:.1f}s de audio en {time.time() - t1:.1f}s", file=sys.stderr)

    wav = np.concatenate(partes[:-1])
    pico = np.abs(wav).max()
    if pico > 0:
        wav = wav / pico * 0.89  # -1 dBFS
    pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    sf.write(a.out, wav, SR)
    print(f"{a.out}: {len(wav) / SR:.1f}s, total {time.time() - t0:.0f}s, mem pico {mx.get_peak_memory() / 1e9:.2f} GB", file=sys.stderr)


if __name__ == "__main__":
    main()
