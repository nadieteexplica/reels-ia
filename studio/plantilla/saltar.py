"""Cuadros que NO hay que renderizar: el plano 6 (rebobinado, lo arma el post) y los planos que reemplaza Kling.
Uso: python saltar.py <carpeta con *_planos.json> [kling/planos.json]  → imprime una lista JSON."""
import glob, json, os, sys
m = json.load(open(glob.glob(os.path.join(sys.argv[1], "*_planos.json"))[0]))
FR = m["FR"]
planos = {"6"}
if len(sys.argv) > 2 and os.path.exists(sys.argv[2]):
    planos |= {str(i["plano"]) for i in json.load(open(sys.argv[2]))}
print(json.dumps(sorted(f for k in planos if k in FR for f in range(FR[k][0], FR[k][1]))))
