"""Armado final de Rhein 01 en local (las tomas de Rhein y su placa NO van al repo público ni a sus prerelease).

Uso: METRAJE=<cuadros del video limpio de Rhein a 30 fps> CIERRE=<placa cierre_rhein.png> \
     python3 armar_local.py <borrador.mp4 de Actions> <salida.mp4> <carpeta de trabajo>
- Actions renderiza y arma el video 3D (con subtítulos); los planos de metraje (30–35 y 38) salen en negro.
- Acá: post.py arma sólo esos planos con las tomas reales (y sus subtítulos), y se intercalan cuadro a cuadro con el
  borrador; el audio se rearma con audio.py (mismo que en Actions) y se mezcla.
"""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rhein01 as E

src, dst, work = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(work, exist_ok=True)
MET = (30, 31, 32, 33, 34, 35, 38)
cuadros = []
for k in MET:
    a, b = E.FR(k)
    cuadros += list(range(a, b))
env = dict(os.environ, OUT=os.path.join(work, "datos"), LISTA=",".join(map(str, cuadros)))
os.makedirs(env["OUT"], exist_ok=True)
fin_met = os.path.join(work, "metraje_final")
subprocess.run([sys.executable, os.path.join(HERE, "post.py"), os.path.join(work, "vacio"), fin_met], env=env, check=True)
# tramos: 3D desde el borrador, metraje desde los cuadros locales
tramos, f, END = [], 1, E.FIN
while f < END:
    met = f in set(cuadros)
    g = f
    while g < END and (g in set(cuadros)) == met:
        g += 1
    tramos.append((f, g, met))
    f = g
partes = []
for i, (a, b, met) in enumerate(tramos):
    p = os.path.join(work, f"tramo{i:02d}.mp4")
    if met:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", "30", "-start_number", str(a), "-i", os.path.join(fin_met, "%05d.png"),
                        "-frames:v", str(b - a), "-vf", "scale=1080:1920:flags=lanczos,format=yuv420p", "-c:v", "libx264", "-crf", "16",
                        "-preset", "medium", "-an", p], check=True)
    else:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-vf",
                        f"select='between(n\\,{a - 1}\\,{b - 2})',setpts=N/30/TB,scale=1080:1920,format=yuv420p", "-frames:v", str(b - a),
                        "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-an", p], check=True)
    partes.append(p)
lista = os.path.join(work, "lista.txt")
open(lista, "w").write("".join(f"file '{p}'\n" for p in partes))
video = os.path.join(work, "video.mp4")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", video], check=True)
subprocess.run([sys.executable, os.path.join(HERE, "audio.py")], env=dict(os.environ, OUT=os.path.join(work, "datos")), check=True)
mix = os.path.join(work, "datos", "rhein01_mix.wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", video, "-i", mix, "-c:v", "libx264", "-profile:v", "high", "-crf", "18", "-preset", "slow",
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", dst], check=True)
print("ok", dst)
