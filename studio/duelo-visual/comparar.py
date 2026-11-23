"""Duelo visual a ciegas: arma, para dos videos del mismo beat, las mismas hojas de cuadros a tamaño celular
con letras al azar (X / Y) y guarda la clave aparte. Los jueces ven sólo las hojas.

  python3 studio/duelo-visual/comparar.py python.mp4 hyperframes.mp4 <salida>

Hojas por video: hook (0–3 s cada 0,5 s), beats (0,3 s después de cada palabra gatillo del storyboard),
golpe (cada 0,1 s alrededor del martillazo, para juzgar el movimiento) y todo el beat a 2 cuadros por segundo.
"""
import json, random, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "tools"))
from qa_video import cuadro, duracion, hoja, rotular  # noqa: E402

GATILLOS = ["Esto", "clavo.", "martillazo,", "entra.", "Pero", "veinte", "cincuenta", "¿Con", "pegas?"]


def main():
    a, b, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    words = json.load(open(RAIZ / "out/voz-libre/duelo-visual/beat.words.json"))
    t_gat = []
    for g in GATILLOS:
        w = next(x for x in words if x["w"] == g)
        t_gat.append(0.0 if g == "Esto" else round(w["s"] + 0.3, 2))
    t_golpe = next(x for x in words if x["w"] == "martillazo,")["s"]
    letras = ["X", "Y"]
    random.shuffle(letras)
    clave = {}
    for letra, video in zip(letras, (a, b)):
        d = out / letra
        d.mkdir(parents=True, exist_ok=True)
        dur = duracion(video)
        clave[letra] = video.name
        f = lambda t: rotular(cuadro(video, min(t, dur - 0.05)), f"{t:.1f}s")
        hoja([f(t) for t in [0, 0.5, 1, 1.5, 2, 2.5, 3]], 4, 2).save(d / "1-hook.jpg", quality=85)
        hoja([f(t) for t in t_gat] + [f(dur - 0.05)], 5, 2).save(d / "2-beats.jpg", quality=85)
        hoja([f(t_golpe - 0.2 + 0.1 * k) for k in range(8)], 4, 2).save(d / "3-golpe.jpg", quality=85)
        ts = [k * 0.5 for k in range(int(dur * 2) + 1)]
        for n in range(0, len(ts), 10):
            hoja([f(t) for t in ts[n:n + 10]], 5, 2).save(d / f"4-todo-{n // 10 + 1}.jpg", quality=80)
    (out.parent / f"{out.name}-clave.json").write_text(json.dumps(clave, indent=1))
    print("listo:", out, "· clave aparte en", out.parent / f"{out.name}-clave.json")


if __name__ == "__main__":
    main()
