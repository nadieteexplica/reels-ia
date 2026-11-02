#!/usr/bin/env bash
# Arma el Ep. 9 con el plano 0 (el mapa) delante del video ya aprobado por Tomás:
#   cuadros del mapa (prerelease ep09-mapa) → intro_post.py (píldoras + subtítulos) → intro.mp4 (con intro_audio.py)
#   → intro + video del borrador (prerelease ep09-borrador), sin tocar el resto → ep09-lago-que-se-vacia-v4.mp4 (cada parte ya viene en −14 LUFS: se pegan sin renormalizar)
# Uso: W=carpeta_de_trabajo VIDEO=borrador.mp4 bash intro_armar.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"
W="${W:?carpeta de trabajo}"; VIDEO="${VIDEO:?video del borrador}"
DUR="${DUR:-3.0}"
mkdir -p "$W/zips" "$W/crudo" "$W/post"
for id in $(gh api repos/nadieteexplica/reels-ia/releases/tags/ep09-mapa --jq '.assets[]|select(.name|startswith("mapa_parte_"))|.id'); do
  n=$(gh api repos/nadieteexplica/reels-ia/releases/assets/$id --jq .name)
  gh api -H "Accept: application/octet-stream" repos/nadieteexplica/reels-ia/releases/assets/$id > "$W/zips/$n"
done
for z in "$W"/zips/*.zip; do unzip -q -o "$z" -d "$W/crudo"; done
echo "cuadros del mapa: $(ls "$W"/crudo/*.png | wc -l)"
# el meta de pantalla se calcula aquí (no hace falta renderizar)
# (mapa_meta.json queda en el repo: SOLO_META=1 python3 mapa.py lo rehace si cambia la cámara)
python3 "$HERE/intro_post.py" "$W/crudo" "$HERE/mapa_meta.json" "$REPO/out/asr/ep09-intro-t1.json" "$W/post"
python3 "$HERE/intro_audio.py" "$REPO/out/tts/ep09-intro-t1.mp3" "$REPO/out/asr/ep09-intro-t1.json" "$W/intro_mix.wav" "$DUR"
ffmpeg -y -v error -framerate 30 -i "$W/post/%05d.png" -i "$W/intro_mix.wav" -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p \
       -c:a aac -b:a 192k -ar 48000 -ac 1 -shortest "$W/intro.mp4"
ffmpeg -y -v error -i "$W/intro.mp4" -i "$VIDEO" -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]" \
       -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -ar 48000 -ac 1 \
       -movflags +faststart "$W/ep09-lago-que-se-vacia-v4.mp4"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$W/ep09-lago-que-se-vacia-v4.mp4"
