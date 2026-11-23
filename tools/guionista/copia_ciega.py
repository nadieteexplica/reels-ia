"""Copia ciega de un guion para juez-viral: sólo lo que verá y oirá el público (sin la predicción, la autorrevisión,
las notas para jueces ni el nombre de la estructura del guionista). Revisión independiente del 23-nov-2026.

  python3 tools/guionista/copia_ciega.py <guion.md> <salida.md>

Deja: idea central, paquete de gancho (cuadro 0, texto en pantalla, voz 0–3 s), la tabla del guion (segundos, voz,
qué se ve) y el texto para la voz. Saca todo lo demás. La salida va al scratchpad, fuera de la carpeta del episodio.
"""
import re, sys
from pathlib import Path

t = Path(sys.argv[1]).read_text()
secciones = re.split(r"(?m)^(?=## )", t)
# se sacan las secciones que no ve el público (las demás quedan, se llamen como se llamen)
SACA = re.compile(r"^## .*(verificaci|revisi|reglas|predicci|autorrevis|notas para|fuentes)", re.I)
SACA_LINEA = re.compile(r"(?i)predicci|autorrevis|\bG\d{1,2}\b|regla \d|juez|duelo|prueba del sistema|guionista")
out = []
for s in secciones:
    if SACA.match(s):
        continue
    lineas = [l for l in s.splitlines() if l.startswith("|") or not SACA_LINEA.search(l)]
    out.append("\n".join(lineas).strip() + "\n")
Path(sys.argv[2]).parent.mkdir(parents=True, exist_ok=True)
Path(sys.argv[2]).write_text("\n".join(out))
print("copia ciega:", sys.argv[2], f"({len(out) - 1} secciones)")
