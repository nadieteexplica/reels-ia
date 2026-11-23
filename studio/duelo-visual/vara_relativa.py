"""Vara viral RELATIVA (Tomás, 23-nov-2026): nuestro beat contra un viral, en el mismo tramo, a ciegas.
"Ganar o empatar contra los virales es el piso, no un 8 absoluto."

Los jueces ven VIDEO, no una hoja quieta: cuadros cada 0,25 s (con su segundo) del mismo tramo de los dos, y la
pista de audio DESCRITA (qué se dice y cuándo, golpes/efectos detectados, si hay música de fondo). Preguntas:
¿cuál se ve más profesional? ¿cuál deslizarías primero?

  python3 studio/duelo-visual/vara_relativa.py <salida> \
      --nuestro beat.mp4 beat.words.json 0 7.6 \
      --viral touchscreen <video> <watch-ref/touchscreen/datos.json> 0 7.6

Escribe <salida>/<X|Y>/ (cuadros-N.jpg + audio.md) y la clave aparte. La salida tiene que quedar FUERA del repo:
los cuadros y la transcripción del viral son de otros creadores y nunca se commitean.
"""
import argparse, json, random, subprocess, sys
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[2]
FUENTE = RAIZ / "studio/plantilla/fonts/Inter-ExtraBold.otf"
PASO = 0.25
ANCHO = 240                     # 8 por fila: una fila = 2 s de video
RECORTE_VIRAL = (0.12, 0.21, 0.13)   # quita la interfaz de Instagram de las grabaciones (arriba, abajo, derecha)
RECORTE_NUESTRO = (0.11, 0.18, 0.13)


def cuadro(video, t, recorte):
    png = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1", "-f", "image2pipe",
                          "-vcodec", "png", "-"], capture_output=True, check=True).stdout
    im = Image.open(BytesIO(png)).convert("RGB")
    w, h = im.size
    a, b, d = recorte
    im = im.crop((0, int(h * a), int(w * (1 - d)), int(h * (1 - b))))
    return im.resize((ANCHO, int(ANCHO * im.size[1] / im.size[0])))


def hojas(video, t0, t1, recorte, salida):
    f = ImageFont.truetype(str(FUENTE), 20)
    ts = list(np.arange(t0, t1 + 1e-6, PASO))
    ims = []
    for t in ts:
        im = cuadro(video, t, recorte)
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 64, 26], fill=(0, 0, 0))
        d.text((5, 3), f"{t - t0:.2f}", font=f, fill=(255, 230, 0))
        ims.append(im)
    tw, th = ims[0].size
    por_hoja = 16                                   # 2 filas de 8 = 4 s por hoja
    for n in range(0, len(ims), por_hoja):
        grupo = ims[n:n + por_hoja]
        filas = (len(grupo) + 7) // 8
        h = Image.new("RGB", (8 * tw + 7 * 4, filas * th + (filas - 1) * 4), (70, 70, 70))
        for i, im in enumerate(grupo):
            h.paste(im, ((i % 8) * (tw + 4), (i // 8) * (th + 4)))
        h.save(salida / f"cuadros-{n // por_hoja + 1}.jpg", quality=84)


def audio(video, t0, t1):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t0), "-t", str(t1 - t0), "-i", str(video), "-f", "f32le",
                          "-ac", "1", "-ar", "16000", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32)
    h = 400                                         # 25 ms
    n = len(x) // h
    rms = np.sqrt(np.mean(x[: n * h].reshape(n, h) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms / (rms.max() + 1e-9))
    golpes = [round(i * h / 16000, 2) for i in range(4, n) if db[i] - db[i - 4:i].mean() > 9 and db[i] > -14]
    limpio = []
    for g in golpes:                               # uno por golpe
        if not limpio or g - limpio[-1] > 0.2:
            limpio.append(g)
    piso = float(np.percentile(db, 15))
    return limpio, piso


def describir_audio(palabras, golpes, piso, t0, t1):
    lineas = ["# Pista de audio (descrita)", ""]
    lineas.append(f"- Fondo entre palabras: {'hay un colchón continuo (música o ambiente)' if piso > -38 else 'casi silencio'} "
                  f"(nivel del 15 % más bajo: {piso:.0f} dB bajo el pico).")
    lineas.append("- Subidas bruscas de volumen (pueden ser efectos de sonido o sílabas fuertes de la voz), en segundos: " + (", ".join(f"{g:.2f}" for g in golpes) or "ninguno"))
    lineas += ["", "## Lo que dice la voz (segundo de inicio de cada palabra)", ""]
    linea, ini = [], None
    for w in palabras:
        s = w["s"] - t0
        if s < 0 or w["s"] > t1:
            continue
        if ini is None:
            ini = s
        linea.append(w["w"])
        if len(linea) >= 6 or w["w"].rstrip()[-1:] in ".?!":
            lineas.append(f"- {ini:5.2f} s: {' '.join(linea)}")
            linea, ini = [], None
    if linea:
        lineas.append(f"- {ini:5.2f} s: {' '.join(linea)}")
    return "\n".join(lineas) + "\n"


def palabras_watch(datos):
    d = json.load(open(datos))
    out = []
    for p in d.get("palabras_detalle", []):
        w = p.get("w") or p.get("p") or p.get("palabra") or p.get("texto")
        s = p.get("s", p.get("ini"))
        if w and s is not None:
            out.append({"w": str(w).strip(), "s": float(s)})
    if not out:                                    # sólo segmentos: reparte por palabra
        for sg in d.get("segmentos", []):
            ws = sg["texto"].split()
            for i, w in enumerate(ws):
                out.append({"w": w, "s": sg["ini"] + (sg["fin"] - sg["ini"]) * i / max(1, len(ws))})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("salida")
    ap.add_argument("--nuestro", nargs=4, metavar=("VIDEO", "WORDS", "T0", "T1"), required=True)
    ap.add_argument("--viral", nargs=5, metavar=("NOMBRE", "VIDEO", "DATOS", "T0", "T1"), required=True)
    a = ap.parse_args()
    out = Path(a.salida)
    if str(RAIZ) in str(out.resolve()):
        sys.exit("la salida tiene que quedar FUERA del repo (material de otros creadores)")
    v_n, w_n, n0, n1 = a.nuestro
    nombre, v_v, datos, r0, r1 = a.viral
    fuentes = [("nuestro", Path(v_n), json.load(open(w_n)), float(n0), float(n1), RECORTE_NUESTRO),
               (nombre, Path(v_v).expanduser(), palabras_watch(datos), float(r0), float(r1), RECORTE_VIRAL)]
    letras = ["X", "Y"]
    random.shuffle(letras)
    clave = {}
    for letra, (nom, video, pals, t0, t1, rec) in zip(letras, fuentes):
        d = out / letra
        d.mkdir(parents=True, exist_ok=True)
        hojas(video, t0, t1, rec, d)
        golpes, piso = audio(video, t0, t1)
        (d / "audio.md").write_text(describir_audio(pals, golpes, piso, t0, t1))
        clave[letra] = nom
    (out.parent / f"{out.name}-clave.json").write_text(json.dumps(clave, indent=1))
    print("listo:", out, "· clave aparte")


if __name__ == "__main__":
    main()
