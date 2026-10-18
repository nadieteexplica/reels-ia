#!/usr/bin/env bash
cd "$(dirname "$0")/.."   # carpeta studio/ (el servidor http debe correr desde ahí)
for S in a b; do
  rm -rf muestras/frames_$S; mkdir -p muestras/frames_$S
  python3 capture.py muestras/$S.html muestras/frames_$S 0 77 30 1 > muestras/log_${S}1.txt 2>&1 &
  python3 capture.py muestras/$S.html muestras/frames_$S 77 153 30 1 > muestras/log_${S}2.txt 2>&1
  wait
done
rm -rf muestras/frames_c; mkdir -p muestras/frames_c
python3 capture.py muestras/c.html muestras/frames_c 0 31 12 1 > muestras/log_c1.txt 2>&1 &
python3 capture.py muestras/c.html muestras/frames_c 31 62 12 1 > muestras/log_c2.txt 2>&1
wait
echo DONE
