#!/bin/bash
# Corre DENTRO de un pod de RunPod (GPU). Arma la escena del episodio, renderiza en GPU, hace el post y el video,
# y sube el resultado a la prerelease del run de GitHub. Al final (pase lo que pase) el pod se borra a sí mismo.
# Variables (las pone el workflow render-gpu.yml): REPO SHA EP RES SAMPLES CUADROS UPLOAD_URL GH_TOKEN ASSETS_TOKEN
#   RUNPOD_API_KEY (para borrarse) · RUNPOD_POD_ID (lo pone RunPod)
set -uo pipefail
LOG=/tmp/pod.log
exec > >(tee -a "$LOG") 2>&1
T0=$(date +%s)
paso() { echo "[$(( $(date +%s) - T0 ))s] $*"; }

subir() {  # subir <archivo> [nombre]
  local f="$1" n="${2:-$(basename "$1")}"
  curl -sS -X POST -H "Authorization: Bearer $GH_TOKEN" -H "Content-Type: application/octet-stream" \
    --data-binary @"$f" "${UPLOAD_URL}?name=${n}" -o /dev/null -w "subido $n: %{http_code}\n" || true
}
fin() {
  local rc=$?
  paso "fin (código $rc)"
  echo "$rc" > /tmp/estado.txt
  subir "$LOG" pod.log
  subir /tmp/estado.txt estado.txt
  curl -sS -X DELETE "https://rest.runpod.io/v1/pods/${RUNPOD_POD_ID}" -H "Authorization: Bearer ${RUNPOD_API_KEY}" -o /dev/null -w "borrar pod: %{http_code}\n" || true
}
trap fin EXIT

paso "sistema"
export DEBIAN_FRONTEND=noninteractive
apt-get -qq update && apt-get -qq install -y --no-install-recommends git curl ca-certificates unzip ffmpeg fonts-inter fonts-dejavu-core \
  libxrender1 libxi6 libxkbcommon0 libsm6 libgl1 libegl1 libxfixes3 libxxf86vm1 libx11-6 libglib2.0-0 > /dev/null || exit 11
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader || true

paso "python 3.13 + bpy"
curl -LsSf https://astral.sh/uv/install.sh | sh > /dev/null || exit 12
export PATH="$HOME/.local/bin:$PATH"
uv venv -q -p 3.13 /opt/py || exit 13
. /opt/py/bin/activate
uv pip install -q bpy==5.2.0 numpy scipy pillow || exit 14

paso "repos"
W=/w; mkdir -p $W && cd $W
git clone -q "https://github.com/$REPO" repo && (cd repo && git checkout -q "$SHA") || exit 15
git clone -q --depth 1 "https://x-access-token:${ASSETS_TOKEN}@github.com/nadieteexplica/assets" assets || exit 16
git clone -q --depth 1 --filter=blob:none --sparse https://github.com/makehumancommunity/makehuman mh && \
  (cd mh && git sparse-checkout set makehuman/data/3dobjs makehuman/data/targets makehuman/data/eyes) || exit 17
export MH_DATA=$W/mh/makehuman/data MIXAMO_DIR=$W/assets/mixamo OUT=$W/_ep
mkdir -p "$OUT"

paso "kit de anatomía (Z-Anatomy, CC BY-SA 4.0)"
mkdir -p zanat && curl -fsSL -o zanat/z.zip https://github.com/Z-Anatomy/The-blend/raw/master/Z-Anatomy.zip && unzip -q zanat/z.zip -d zanat || exit 18
ZANAT=zanat/Z-Anatomy/Startup.blend python repo/studio/plantilla/anatomia_kit.py > /tmp/kit.log 2>&1 || { tail -30 /tmp/kit.log; exit 19; }
rm -rf zanat

paso "personaje"
(cd repo/studio/personaje && python build_body.py && python rig.py && python dress.py && python hair.py) > /tmp/pj.log 2>&1 || { tail -30 /tmp/pj.log; exit 20; }

paso "escena"
(cd "repo/studio/episodios/$EP/escena" && python build_*.py) > /tmp/esc.log 2>&1 || { tail -30 /tmp/esc.log; exit 21; }
PLANOS=$(ls "$OUT"/*_planos.json | head -1)
END=$(python -c "import json; print(json.load(open('$PLANOS'))['END'] - 1)")
RANGO=${CUADROS:-1-$END}
SKIP=$(python repo/studio/plantilla/saltar.py "$OUT" "repo/studio/episodios/$EP/kling/planos.json")

paso "render GPU $RANGO a $RES, $SAMPLES muestras"
BLEND=$(ls "$OUT"/ep*.blend | head -1) FRAMES=$RANGO RES=$RES SAMPLES=$SAMPLES DIR="$OUT/frames" SKIP="$SKIP" DEVICE=OPTIX \
  python repo/studio/plantilla/render_frames.py > /tmp/render.log 2>&1 &
RPID=$!
TOTAL=$(python -c "import json,sys; a,b='$RANGO'.split('-'); print(int(b)-int(a)+1-len(json.loads(sys.argv[1])))" "$SKIP")
PREV=""
while kill -0 $RPID 2>/dev/null; do   # avance cada 3 min en la prerelease (progreso.txt), para dar horas con datos reales
  sleep 180
  N=$(ls "$OUT"/frames/*.png 2>/dev/null | wc -l)
  echo "$(date -u +%H:%M) UTC · $N de $TOTAL cuadros · $(( ($(date +%s) - T0) / 60 )) min" > /tmp/progreso.txt
  [ -n "$PREV" ] && curl -s -X DELETE -H "Authorization: Bearer $GH_TOKEN" "https://api.github.com/repos/$REPO/releases/assets/$PREV" -o /dev/null
  PREV=$(curl -s -X POST -H "Authorization: Bearer $GH_TOKEN" -H "Content-Type: text/plain" --data-binary @/tmp/progreso.txt \
    "${UPLOAD_URL}?name=progreso.txt" | python -c "import json,sys; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)
done
wait $RPID || { tail -40 /tmp/render.log; exit 22; }
grep -E "^dispositivo|Fra:1 " /tmp/render.log | head -3
cp "$PLANOS" "$OUT/frames/"
paso "render listo: $(ls "$OUT"/frames/*.png | wc -l) cuadros"
if [ -n "${CUADROS:-}" ]; then   # prueba: se suben los cuadros sueltos y nada más
  tar -C "$OUT/frames" -cf /tmp/cuadros.tar . && subir /tmp/cuadros.tar cuadros.tar
  grep -E "Time:|Tiempo|Saved" /tmp/render.log | tail -3
  exit 0
fi

paso "clips de Kling"
M="repo/studio/episodios/$EP/kling/planos.json"
if [ -f "$M" ]; then
  TAGK="$(echo "$EP" | cut -d- -f1)-kling"
  mkdir -p kclips
  for c in $(python -c "import json,sys; print(' '.join(sorted({i['clip'] for i in json.load(open(sys.argv[1]))})))" "$M"); do
    curl -fsSL -o "kclips/$c" "https://github.com/$REPO/releases/download/$TAGK/$c" || exit 23
  done
  python repo/studio/plantilla/kling_insert.py "$M" kclips "$OUT/frames" "$PLANOS" || exit 24
fi

paso "post, audio y video"
cp "$PLANOS" "$OUT/"
(cd "repo/studio/episodios/$EP/escena" && python post.py "$OUT/frames" "$OUT/final" && python audio.py) > /tmp/post.log 2>&1 || { tail -30 /tmp/post.log; exit 25; }
ffmpeg -y -v error -framerate 30 -i "$OUT/final/%05d.png" -i "$OUT"/*_mix.wav \
  -vf "scale=1080:1920:flags=lanczos,format=yuv420p" -c:v libx264 -profile:v high -crf 18 -preset slow \
  -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart "$OUT/$EP.mp4" || exit 26
python repo/tools/qa.py "$OUT/$EP.mp4" "$OUT/frames" "$OUT/subs_log.json" > "$OUT/qa.txt" 2>&1; echo "qa: $?" >> "$OUT/qa.txt"
ffmpeg -y -v error -i "$OUT/$EP.mp4" -vf "fps=1,scale=216:384,tile=12x7" -frames:v 1 "$OUT/contacto.jpg"
paso "subiendo"
cp "$PLANOS" "$OUT/planos.json"   # cortes por plano: los usa el auditor (tools/auditor)
for f in "$OUT/$EP.mp4" "$OUT/contacto.jpg" "$OUT/qa.txt" "$OUT/subs_log.json" "$OUT/planos.json"; do subir "$f"; done
paso "listo"
exit 0
