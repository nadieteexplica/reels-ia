"""Guarda la respuesta de un juez (auditor-final, juez-viral, juez-gancho, espectador) TAL CUAL, validada como JSON.

  python3 tools/guardar_veredicto.py <respuesta_cruda.txt> <destino.json>

La respuesta cruda se pega sin tocar en un archivo del scratchpad; este script saca el bloque JSON (aunque venga
entre ```), lo valida y lo guarda con la fecha y un sha256 del texto crudo. Nada de "resúmenes" escritos a mano:
si un juez dijo algo, queda exactamente lo que dijo (revisión independiente del 23-nov-2026).
"""
import hashlib, json, re, sys, time
from pathlib import Path

crudo = Path(sys.argv[1]).read_text()
m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", crudo, re.S) or re.search(r"(\{.*\})", crudo, re.S)
if not m:
    sys.exit("no encontré un JSON en la respuesta")
datos = json.loads(m.group(1))
datos["_registro"] = {"guardado": time.strftime("%Y-%m-%d %H:%M"), "sha256_crudo": hashlib.sha256(crudo.encode()).hexdigest()}
Path(sys.argv[2]).parent.mkdir(parents=True, exist_ok=True)
Path(sys.argv[2]).write_text(json.dumps(datos, ensure_ascii=False, indent=1))
print("guardado", sys.argv[2])
