#!/usr/bin/env bash
set -euo pipefail
cd /home/claude/reels/muestras
enc() { # $1 framerate  $2 frames dir  $3 out
  ffmpeg -hide_banner -loglevel error -y -framerate "$1" -i "$2/f%05d.jpg" -i audio.wav \
    -vf "fps=30,format=yuv420p" -c:v libx264 -preset slow -crf 18 -profile:v high \
    -af "loudnorm=I=-14:TP=-1.5:LRA=11" -c:a aac -b:a 192k -ar 48000 -movflags +faststart -t 5.1 "$3"
}
enc 30 frames_a muestra_A_pixar.mp4
enc 30 frames_b muestra_B_caricatura.mp4
enc 12 frames_c muestra_C_plastilina.mp4
printf "file 'muestra_A_pixar.mp4'\nfile 'muestra_B_caricatura.mp4'\nfile 'muestra_C_plastilina.mp4'\n" > lista.txt
ffmpeg -hide_banner -loglevel error -y -f concat -safe 0 -i lista.txt -c copy muestras_ABC.mp4
for f in muestra_*.mp4 muestras_ABC.mp4; do echo "$f $(ffprobe -v error -show_entries format=duration -of csv=p=0 $f)"; done
python3 - <<'EOF'
from PIL import Image
sel={'a':[('frames_a',f) for f in (12,33,92,128)],'b':[('frames_b',f) for f in (12,33,92,128)],'c':[('frames_c',f) for f in (5,13,37,51)]}
W,H=270,480
sheet=Image.new('RGB',(W*4,H*3),'white')
for r,k in enumerate('abc'):
    for i,(d,f) in enumerate(sel[k]):
        sheet.paste(Image.open(f'{d}/f{f:05d}.jpg').resize((W,H)),(i*W,r*H))
sheet.save('muestras_fotogramas.jpg',quality=90)
EOF
