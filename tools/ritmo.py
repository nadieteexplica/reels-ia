"""Ritmo de un video, medido (lección 177): para comparar nuestro beat con la banda de los virales sin opinar.

  python3 tools/ritmo.py <video> [--desde 0] [--hasta 999] [--recorte 0.12,0.21,0.13] [--json salida.json]

Mira el video a 10 cuadros por segundo (en chico, en gris) y entre cada par de cuadros mide qué fracción de la
imagen cambió y cuánto se desplazó todo el cuadro (cámara):
  - CORTE: la estructura del cuadro (sus bordes) ya no se parece a la anterior, ni moviéndola: es otro plano.
  - CÁMARA RÁPIDA: todo se corrió (la estructura calza si se la mueve) o cambia casi todo sin ser otro plano.
  - CAMBIO DENTRO DEL PLANO: cambia una parte (> 1,5 % de la imagen): aparece algo, corre un número, se mueve una pieza.
Resume: plano promedio, cortes por 10 s, planos < 0,3 s, cambios dentro del plano por segundo (inicios de cambio),
tramo quieto más largo, ráfagas (≥ 3 inicios de cambio o corte en < 1 s) y segundos con cámara rápida.
--recorte (arriba, abajo, derecha, en fracción) saca la interfaz de las grabaciones de Instagram/TikTok.
Las cifras son una banda de referencia, no reglas: decide el ojo de Tomás (docs/REGLAS.md).
"""
import argparse, json, subprocess, sys

import numpy as np

FPS, W, H = 10, 108, 192


def cuadros(video, desde, hasta, recorte):
    a, b, d = recorte
    vf = (f"fps={FPS},crop=iw*{1 - d:.3f}:ih*{1 - a - b:.3f}:0:ih*{a:.3f},scale={W}:{H},format=gray")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(desde), "-to", str(hasta), "-i", str(video), "-vf", vf,
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    n = len(raw) // (W * H)
    return np.frombuffer(raw[: n * W * H], np.uint8).reshape(n, H, W).astype(np.float32)


def desplazamiento(f0, f1):
    """Corrimiento global (px en el cuadro chico) por correlación de fase."""
    F0, F1 = np.fft.fft2(f0 - f0.mean()), np.fft.fft2(f1 - f1.mean())
    R = F0 * np.conj(F1)
    r = np.abs(np.fft.ifft2(R / (np.abs(R) + 1e-6)))
    y, x = np.unravel_index(np.argmax(r), r.shape)
    y = y - H if y > H // 2 else y
    x = x - W if x > W // 2 else x
    return float(np.hypot(x, y)), float(r.max())


def mapa_bordes(f):
    gy, gx = np.gradient(f)
    m = np.hypot(gx, gy)
    m = m - m.mean()
    return m / (np.linalg.norm(m) + 1e-6)


def parecido(b0, b1, f0, f1):
    """Correlación de los bordes sin mover y moviendo según la cámara (lo mejor de las dos)."""
    c0 = float((b0 * b1).sum())
    sh, _ = desplazamiento(f0, f1)
    if sh < 0.5:
        return c0, c0, sh
    F0, F1 = np.fft.fft2(b0), np.fft.fft2(b1)
    r = np.real(np.fft.ifft2(F0 * np.conj(F1)))
    return c0, float(r.max()), sh


def medir(fr):
    n = len(fr)
    tipos = []
    B = [mapa_bordes(f) for f in fr]
    for i in range(1, n):
        d = np.abs(fr[i] - fr[i - 1])
        frac = float((d > 22).mean())
        c0, cmov, sh = parecido(B[i - 1], B[i], fr[i - 1], fr[i])
        if frac < 0.015:
            tipos.append("quieto")
        elif max(c0, cmov) < 0.35 and frac > 0.15:
            tipos.append("corte")        # la estructura del cuadro cambió entera: otro plano
        elif sh >= 2.0 and cmov > c0 + 0.1 or frac > 0.45:
            tipos.append("camara")       # todo se corrió o se desenfocó: barrido, zoom rápido
        else:
            tipos.append("cambio")       # cambió una parte: algo aparece, corre o se mueve
    dur = n / FPS
    cortes = [i for i, t in enumerate(tipos) if t == "corte"]
    bordes = [0] + [c + 1 for c in cortes] + [n]
    planos = [(b - a) / FPS for a, b in zip(bordes, bordes[1:]) if b > a]
    inicios = [i for i, t in enumerate(tipos) if t in ("cambio", "corte", "camara") and (i == 0 or tipos[i - 1] == "quieto")]
    quieto_max, racha = 0, 0
    for t in tipos:
        racha = racha + 1 if t == "quieto" else 0
        quieto_max = max(quieto_max, racha)
    rafagas, i = 0, 0
    while i < len(inicios):
        j = i
        while j + 1 < len(inicios) and inicios[j + 1] - inicios[i] < FPS:
            j += 1
        if j - i + 1 >= 3:
            rafagas += 1
            i = j + 1
        else:
            i += 1
    return {
        "duracion_s": round(dur, 1),
        "plano_promedio_s": round(float(np.mean(planos)), 2) if planos else None,
        "cortes_por_10s": round(10 * len(cortes) / dur, 2),
        "planos_menores_0_3s": sum(1 for p in planos if p < 0.3),
        "cambios_dentro_por_s": round(sum(1 for i in inicios if tipos[i] == "cambio") / dur, 2),
        "pct_tiempo_con_cambio": round(100 * sum(1 for t in tipos if t != "quieto") / max(1, len(tipos))),
        "tramo_quieto_max_s": round(quieto_max / FPS, 1),
        "rafagas_por_10s": round(10 * rafagas / dur, 2),
        "camara_rapida_s": round(sum(1 for t in tipos if t == "camara") / FPS, 1),
        "linea_de_tiempo": "".join({"corte": "|", "camara": "~", "cambio": "+", "quieto": "."}[t] for t in tipos),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--desde", type=float, default=0)
    ap.add_argument("--hasta", type=float, default=999)
    ap.add_argument("--recorte", default="0,0,0")
    ap.add_argument("--json")
    a = ap.parse_args()
    r = medir(cuadros(a.video, a.desde, a.hasta, [float(x) for x in a.recorte.split(",")]))
    for k, v in r.items():
        if k != "linea_de_tiempo":
            print(f"{k:24} {v}")
    print("linea (cada signo = 0,1 s; | corte · ~ cámara rápida · + cambio dentro · . quieto):")
    t = r["linea_de_tiempo"]
    for i in range(0, len(t), 50):
        print(f"  {i / FPS:5.1f}s {t[i:i + 50]}")
    if a.json:
        json.dump(r, open(a.json, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    sys.exit(main())
