"""Comprime una imagen de /watch para guardarla en el repo (≤ 300 KB por defecto).

Uso: .venv/bin/python tools/watch/comprimir.py <entrada.jpg> <salida.jpg> [--max-kb 300]

Baja la calidad JPEG y, si no basta, achica la imagen, hasta quedar bajo el límite.
Pensado para docs/referencias/virales/img/<slug>/ (hook.jpg + una hoja, nada más).
"""
import argparse
import io
import sys
from pathlib import Path

from PIL import Image


def comprimir(entrada: Path, salida: Path, max_kb: int) -> int:
    img = Image.open(entrada).convert("RGB")
    while True:
        for calidad in (80, 70, 60, 50, 40):
            buf = io.BytesIO()
            img.save(buf, "JPEG", quality=calidad, optimize=True, progressive=True)
            if buf.tell() <= max_kb * 1024:
                salida.parent.mkdir(parents=True, exist_ok=True)
                salida.write_bytes(buf.getvalue())
                return buf.tell()
        if img.width < 400:
            sys.exit(f"No se pudo dejar {entrada} bajo {max_kb} KB")
        img = img.resize((int(img.width * 0.85), int(img.height * 0.85)), Image.LANCZOS)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("entrada")
    p.add_argument("salida")
    p.add_argument("--max-kb", type=int, default=300)
    a = p.parse_args()
    peso = comprimir(Path(a.entrada), Path(a.salida), a.max_kb)
    print(f"{a.salida}: {peso / 1024:.0f} KB")
