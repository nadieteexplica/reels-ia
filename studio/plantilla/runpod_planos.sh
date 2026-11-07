#!/bin/bash
# Corre DENTRO de un pod de RunPod (GPU) para los episodios que se arman plano por plano (escena/plano.py, Ep. 5 en adelante).
# Baja los assets de escena/assets.txt, renderiza las piezas pedidas en GPU (OptiX) y sube los cuadros como cuadros-gpu.zip
# a la prerelease del run de GitHub; render-planos.yml los suma con su entrada "gpu_runs". Al final el pod se borra solo.
# Variables (las pone render-gpu.yml): REPO SHA EP RES SAMPLES PIEZAS UPLOAD_URL GH_TOKEN ASSETS_TOKEN RUNPOD_API_KEY
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
apt-get -qq update && apt-get -qq install -y --no-install-recommends git curl ca-certificates unzip zip \
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
git clone -q --depth 1 "https://x-access-token:${ASSETS_TOKEN}@github.com/nadieteexplica/assets" priv_assets || exit 16
ESC="$W/repo/studio/episodios/$EP/escena"
DL="python $W/repo/studio/plantilla/descargar_release.py"
export ASSETS=$W/_assets
mkdir -p "$ASSETS"

paso "assets (assets.txt)"
if [ -f "$ESC/assets.txt" ]; then
  while read -r tipo valor; do
    case "$tipo" in
      modelos) GH_DL_TOKEN="$GH_TOKEN" $DL "$REPO" "$valor" "$ASSETS" "*.glb" "*.hdr" "*.jpg" "*.png" || exit 17 ;;
      mapas)   GH_DL_TOKEN="$GH_TOKEN" $DL "$REPO" mapas "$ASSETS/mapas" "world.topo.bathy.200412.3x5400x2700.jpg" \
                 "world.topo.bathy.200412.3x21600x10800.jpg" "world.topo.bathy.200412.3x21600x21600.D1.jpg" || exit 17
               python "$ESC/$valor" "$ASSETS/mapas" || exit 17 ;;
      privados) GH_DL_TOKEN="$ASSETS_TOKEN" $DL nadieteexplica/assets Personajes "$ASSETS" "$valor" || exit 17 ;;
      gestos)  d=$(find priv_assets -type d -iname "$valor" | head -1); [ -n "$d" ] && export GESTOS="$W/$d" ;;
    esac
  done < "$ESC/assets.txt"
fi
ls "$ASSETS" | head -40

paso "render en GPU: ${PIEZAS:-todas}"
mkdir -p $W/_r
if [ -z "${PIEZAS:-}" ]; then
  PIEZAS=$(cd "$ESC" && python -c "import sys; sys.argv=['x']; import planos_${EP%%-*} as P; print(','.join(P.PIEZAS))" 2>/dev/null | tail -1)
fi
( cd "$ESC" && PIEZAS="$PIEZAS" RES="$RES" SAMPLES="$SAMPLES" DIR="$W/_r" DEVICE=OPTIX python plano.py ) > /tmp/render.log 2>&1 &
RP=$!
PREV=""
while kill -0 $RP 2>/dev/null; do
  sleep 60
  N=$(ls $W/_r/*.png 2>/dev/null | wc -l)
  echo "$(date +%T) $N cuadros · $(grep -c 'pieza .*: ok' /tmp/render.log) piezas listas" > /tmp/progreso.txt
  [ -n "$PREV" ] && curl -s -X DELETE -H "Authorization: Bearer $GH_TOKEN" "https://api.github.com/repos/$REPO/releases/assets/$PREV" -o /dev/null
  PREV=$(curl -s -X POST -H "Authorization: Bearer $GH_TOKEN" -H "Content-Type: text/plain" --data-binary @/tmp/progreso.txt \
    "${UPLOAD_URL}?name=progreso.txt" | python -c "import json,sys; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)
done
wait $RP; RC=$?
grep -E "pieza .*: (ok|FALLA)" /tmp/render.log
[ $RC -eq 0 ] || { tail -40 /tmp/render.log; exit 22; }

paso "subir cuadros"
(cd $W/_r && zip -q -r /tmp/cuadros-gpu.zip .) || exit 23
ls -la /tmp/cuadros-gpu.zip
subir /tmp/cuadros-gpu.zip cuadros-gpu.zip
paso "listo"
