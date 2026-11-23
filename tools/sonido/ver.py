"""Dibuja una mezcla para revisarla con los ojos (cuando no se puede escuchar): onda, espectrograma, eventos y palabras.

Uso:
    .venv/bin/python tools/sonido/ver.py <salida>.reporte.json [--desde 0] [--hasta 15] [--png salida.png]

Lee el reporte que deja mezclar.py. Si la mezcla se hizo con --guardar-ref, la onda de la voz+música sin efectos
se dibuja en gris oscuro encima de la mezcla (naranja): lo naranja que asoma es lo que aportan los efectos.
Líneas verticales: verde = evento que se oye, rojo = evento importante que no se oye, gris = opcional.
La franja de color arriba de cada línea es la ventana donde se midió la audibilidad.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import medir  # noqa: E402

SR = medir.SR
ANCHO, MARGEN = 1800, 70
FONDO, TINTA, GRILLA = (18, 18, 22), (230, 230, 230), (60, 60, 70)
COLOR = {"ok": (80, 210, 120), "NO SE OYE": (240, 70, 70), "opcional": (150, 150, 160)}


def fuente(t):
    for ruta in ("/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(ruta):
            return ImageFont.truetype(ruta, t)
    try:
        return ImageFont.load_default(size=t)
    except TypeError:
        return ImageFont.load_default()


def mapa(v):
    """0..1 → negro, morado, naranjo, amarillo."""
    pts = np.array([[0, 0, 0], [60, 20, 110], [200, 60, 60], [250, 160, 40], [255, 250, 200]], float)
    x = np.clip(v, 0, 1) * (len(pts) - 1)
    i = np.minimum(x.astype(int), len(pts) - 2)
    f = (x - i)[..., None]
    return (pts[i] * (1 - f) + pts[i + 1] * f).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("reporte")
    ap.add_argument("--desde", type=float, default=0.0)
    ap.add_argument("--hasta", type=float)
    ap.add_argument("--png")
    a = ap.parse_args()
    rep = medir.leer_json(a.reporte)
    mix = medir.leer_audio(rep["salida"], 1)
    ref = medir.leer_audio(rep["ref"], 1) if rep.get("ref") and os.path.exists(rep["ref"]) else None
    words = medir.leer_json(rep["words"]) if rep.get("words") else []
    t0, t1 = a.desde, a.hasta or len(mix) / SR
    i0, i1 = int(t0 * SR), min(len(mix), int(t1 * SR))
    mix = mix[i0:i1]
    ref = ref[i0:i1] if ref is not None else None
    w = ANCHO - 2 * MARGEN
    H_ONDA, H_ESP, H_PAL = 260, 320, 90
    y_onda, y_esp = 80, 80 + H_ONDA + 20
    y_pal = y_esp + H_ESP + 10
    alto = y_pal + H_PAL + 40
    img = Image.new("RGB", (ANCHO, alto), FONDO)
    dr = ImageDraw.Draw(img)
    f12, f14, f18 = fuente(12), fuente(14), fuente(18)
    xpos = lambda t: MARGEN + (t - t0) / (t1 - t0) * w

    titulo = (f"{os.path.basename(rep['salida'])}  ·  {rep['loudness_lufs']} LUFS  ·  {rep['true_peak_dbtp']} dBTP"
              + (f"  ·  música {rep['musica_bajo_voz_db']} dB bajo la voz" if rep.get("musica_bajo_voz_db") else "")
              + f"  ·  {sum(e['estado'] == 'ok' for e in rep['eventos'] if not e['opcional'])}/"
              f"{sum(not e['opcional'] for e in rep['eventos'])} importantes se oyen")
    dr.text((MARGEN, 20), titulo, fill=TINTA, font=f18)
    dr.text((MARGEN, 48), "naranjo = mezcla · gris = voz+música sin efectos · espectrograma 50 Hz–16 kHz (log)",
            fill=(160, 160, 170), font=f12)

    # onda (mín/máx por columna)
    def columnas(x):
        n = len(x) // w
        x = x[:n * w].reshape(w, n)
        return x.min(axis=1), x.max(axis=1)

    mid = y_onda + H_ONDA / 2
    dr.rectangle([MARGEN, y_onda, MARGEN + w, y_onda + H_ONDA], outline=GRILLA)
    for capa, color in [(mix, (240, 140, 40)), (ref, (95, 95, 105))]:
        if capa is None:
            continue
        lo, hi = columnas(capa)
        for c in range(w):
            dr.line([(MARGEN + c, mid - hi[c] * H_ONDA / 2), (MARGEN + c, mid - lo[c] * H_ONDA / 2)], fill=color)

    # espectrograma
    nfft, hop = 2048, 240
    nfr = 1 + (len(mix) - nfft) // hop
    idx = np.arange(nfft)[None, :] + hop * np.arange(nfr)[:, None]
    S = np.abs(np.fft.rfft(mix[idx] * np.hanning(nfft), axis=1)) + 1e-9
    db = 20 * np.log10(S / S.max())
    fr = np.fft.rfftfreq(nfft, 1 / SR)
    filas = 50 * (16000 / 50) ** (1 - np.arange(H_ESP) / (H_ESP - 1))
    fi = np.clip(np.searchsorted(fr, filas), 0, len(fr) - 1)
    ci = np.clip((np.arange(w) / w * nfr).astype(int), 0, nfr - 1)
    m = db[ci][:, fi].T
    img.paste(Image.fromarray(mapa((m + 80) / 80)), (MARGEN, y_esp))
    for f in (100, 1000, 10000):
        yy = y_esp + (1 - np.log(f / 50) / np.log(16000 / 50)) * (H_ESP - 1)
        dr.text((8, yy - 7), f"{f // 1000}k" if f >= 1000 else str(f), fill=(160, 160, 170), font=f12)

    # grilla de segundos
    for s in range(int(np.ceil(t0)), int(t1) + 1):
        x = xpos(s)
        dr.line([(x, y_onda + H_ONDA), (x, y_onda + H_ONDA + 6)], fill=TINTA)
        dr.text((x - 4, y_onda + H_ONDA + 6), str(s), fill=(160, 160, 170), font=f12)

    # palabras
    for k, wd in enumerate(x for x in words if t0 <= x["s"] < t1):
        x = xpos(wd["s"])
        fila = k % 3
        dr.line([(x, y_pal), (x, y_pal + 6)], fill=(120, 170, 255))
        dr.text((x + 2, y_pal + 6 + fila * 22), wd["w"], fill=(150, 190, 255), font=f14)

    # eventos
    vistos = []
    for e in rep["eventos"]:
        if not (t0 <= e["t"] <= t1):
            continue
        col = COLOR.get(e["estado"], TINTA)
        x = xpos(e["t"])
        dr.line([(x, y_onda), (x, y_esp + H_ESP)], fill=col, width=2)
        wa, wb = xpos(max(t0, e["ventana"][0])), xpos(min(t1, e["ventana"][1]))
        dr.rectangle([wa, y_onda - 8, wb, y_onda - 2], fill=col)
        fila = sum(1 for v in vistos if abs(v - x) < 190) % 5
        vistos.append(x)
        etq = f"#{e['n']} {e['sfx']} {min(e['delta_db'], 40):+.0f} dB"
        bb = dr.textbbox((x + 4, y_onda + 4 + fila * 17), etq, font=f12)
        dr.rectangle([bb[0] - 2, bb[1] - 1, bb[2] + 2, bb[3] + 1], fill=FONDO)
        dr.text((x + 4, y_onda + 4 + fila * 17), etq, fill=col, font=f12)

    png = a.png or a.reporte.replace(".reporte.json", ".png")
    img.save(png)
    print("ok", png)


if __name__ == "__main__":
    main()
