#!/bin/sh
# OK de Tomás para programar un post (lo corre Tomás en su terminal; Claude no puede: el hook se lo bloquea).
#   tools/ok.sh ep17 youtube instagram tiktok
# Deja studio/ok/<ep>-<red>.ok. Sin ese archivo, tools/hooks/puertas.py no deja crear ni cambiar el post en Metricool.
set -e
[ $# -ge 2 ] || { echo "uso: tools/ok.sh <epNN> <red> [red...]   (redes: youtube instagram tiktok)"; exit 1; }
ep="$1"; shift
dir="$(cd "$(dirname "$0")/.." && pwd)/studio/ok"
mkdir -p "$dir"
for red in "$@"; do
  case "$red" in youtube|instagram|tiktok) ;; *) echo "red desconocida: $red"; exit 1;; esac
  printf 'OK de Tomás para %s en %s · %s\n' "$ep" "$red" "$(date '+%Y-%m-%d %H:%M:%S %z')" > "$dir/$ep-$red.ok"
  echo "OK guardado: studio/ok/$ep-$red.ok"
done
