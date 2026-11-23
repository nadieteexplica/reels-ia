#!/usr/bin/env bash
# Copia a assets/ lo que la composición necesita y vive en otras carpetas del repo:
# las fuentes Inter (Black y ExtraBold), la voz del beat y GSAP (del paquete npm, ruta como argumento).
# Así no se duplican archivos en el repo: assets/ está en .gitignore.
set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"
RAIZ="$(cd "$AQUI/../../.." && pwd)"
mkdir -p "$AQUI/assets/fonts"
cp "$RAIZ/studio/plantilla/fonts/Inter-Black.otf" "$RAIZ/studio/plantilla/fonts/Inter-ExtraBold.otf" "$AQUI/assets/fonts/"
cp "$RAIZ/out/voz-libre/duelo-visual/beat.wav" "$AQUI/assets/beat.wav"
if [ -n "${1:-}" ]; then cp "$1" "$AQUI/assets/gsap.min.js"; fi
test -f "$AQUI/assets/gsap.min.js" || { echo "falta assets/gsap.min.js (pasar la ruta de gsap/dist/gsap.min.js)"; exit 1; }
ls -la "$AQUI/assets" "$AQUI/assets/fonts"
