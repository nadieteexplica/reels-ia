"""Plano 23 completo (puerta 4 c2): ratón de perfil + lupa con las muelas aplastando semillas + recuadro "y si…" + ✕.
Corre estilo_muelas.py dos veces (MODO=cara y MODO=lupa) y los junta con compone_muelas.py y marco_ysi.py.
Variables: RES (del cuadro final), SAMPLES, OUT, NOMBRE (sale $OUT/$NOMBRE.png)."""
import os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("OUT", os.path.join(HERE, "out"))
NOMBRE = os.environ.get("NOMBRE", "estilo_muelas2")
RES = os.environ.get("RES", "720x1280")
W = int(RES.split("x")[0])
env = dict(os.environ)
env.update({"MODO": "cara", "NOMBRE": NOMBRE + "_cara", "TGT_Y": os.environ.get("TGT_Y", "-0.014"), "TGT_Z": os.environ.get("TGT_Z", "-0.0005"),
            "CAMOFF": os.environ.get("CAMOFF", "1.0,0.0,0.0"), "LENS": os.environ.get("LENS", "50")})
# puerta 4 c2 r2: el ratón entero y sentado como en la ficha (a la derecha, mirando a la izquierda), la lupa arriba a la
# izquierda, delante del hocico (no tapa las orejas), y la ✕ abajo al centro de la lupa (niega la escena entera)
r = subprocess.run([sys.executable, os.path.join(HERE, "estilo_muelas.py")], env=env, capture_output=True, text=True)
m = re.search(r"mejilla en pantalla (\d+) (\d+)", r.stdout)
if not m:
    print(r.stdout[-2000:], r.stderr[-2000:])
    sys.exit("no salió el render de la cara")
mx, my = m.groups()
env.update({"MODO": "lupa", "NOMBRE": NOMBRE + "_lupa", "LADO": str(int(W * 0.75)), "LENS": os.environ.get("LENS_LUPA", "65")})
r2 = subprocess.run([sys.executable, os.path.join(HERE, "estilo_muelas.py")], env=env, capture_output=True, text=True)
if r2.returncode:
    print(r2.stdout[-2000:], r2.stderr[-2000:])
    sys.exit("no salió el render de la lupa")
comp = os.path.join(OUT, NOMBRE + "_comp.png")
envc = dict(os.environ, LUPA_ZOOM=os.environ.get("LUPA_ZOOM", "0.55"), LUPA_CX=os.environ.get("LUPA_CX", "300"), LUPA_CY=os.environ.get("LUPA_CY", "540"),
            LUPA_DIAM=os.environ.get("LUPA_DIAM", "420"))
subprocess.run([sys.executable, os.path.join(HERE, "compone_muelas.py"), os.path.join(OUT, NOMBRE + "_cara.png"), os.path.join(OUT, NOMBRE + "_lupa.png"), comp, mx, my], env=envc, check=True)
envm = dict(os.environ, MARCA_XY=os.environ.get("MARCA_XY", "300,752"))
subprocess.run([sys.executable, os.path.join(HERE, "marco_ysi.py"), comp, os.path.join(OUT, NOMBRE + ".png"), "x", "izq", "mascara"], env=envm, check=True)
print("ok", os.path.join(OUT, NOMBRE + ".png"))
