"""Audio del Ep. 17: voz + efectos de sfx-plan.json con tools/sonido/mezclar.py (−14 LUFS, −1,5 dBTP, ducking).
Sin música, como el beat v5 aprobado. Uso (render-2d.yml): python audio.py <carpeta> → <carpeta>/mix.wav"""
import os
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", "..", "..", ".."))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(AQUI)
os.makedirs(OUT, exist_ok=True)
subprocess.run([sys.executable, os.path.join(RAIZ, "tools/sonido/mezclar.py"),
                os.path.join(RAIZ, "studio/episodios/ep17-radiacion-pareja/sfx-plan.json"),
                "--salida", os.path.join(OUT, "mix.wav")], cwd=RAIZ, check=True)
