#!/usr/bin/env python3
"""Prueba de planos del EDITOR: render chico + post + chequeo automático + hoja, en un solo comando.
Se corre en cada plano nuevo o cambiado ANTES de mandarlo al auditor (MANUAL_PRODUCCION §8, "ficha de plano").

  python3 tools/prueba.py <ep> --planos 14,15 [--muestras 3]     # todas las piezas de esos planos (principal + lupas/recuadros)
  python3 tools/prueba.py <ep> 14:690 14S:690                     # piezas y cuadros exactos
  opciones: --res 360x640 · --samples 8 · --dir carpeta (por defecto /tmp/prueba-<ep>)

Contrato de la carpeta escena/ del episodio (el kit, studio/plantilla/KIT.md): plano.py (PIEZAS, CUADROS, MUESTRAS, RES,
SAMPLES, DIR, FORCE), post.py <render> <salida> con OUT/LISTA, y un módulo planos_*.py con el diccionario PIEZAS.
Deja en la carpeta: fin/ (cuadros del post), chequeo.json y hoja.jpg (cada cuadro con los ojos marcados: verde libre,
rojo tapado; y las cajas de los gráficos). Sale con código 1 si el chequeo tiene fallas.
"""
import argparse, glob, json, os, subprocess, sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(RAIZ, "tools", "auditor"))


def piezas_de(esc, planos):
    """{pieza: {a, b, plano, aux}} de las piezas de esos planos (lee PIEZAS del módulo planos_*.py con bpy)."""
    mod = [os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(esc, "planos_*.py"))]
    if not mod:
        sys.exit("la escena no tiene planos_*.py con PIEZAS")
    cod = (f"import json, {mod[0]} as M; print(json.dumps({{k: dict(a=v['a'], b=v['b'], plano=v.get('plano'), aux=bool(v.get('aux'))) "
           f"for k, v in M.PIEZAS.items() if v.get('plano') in {sorted(planos)}}}))")
    r = subprocess.run([sys.executable, "-c", cod], cwd=esc, capture_output=True, text=True)
    try:
        return json.loads(r.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        sys.exit("no pude leer PIEZAS:\n" + r.stderr[-1500:])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ep")
    ap.add_argument("trabajos", nargs="*", help="pieza:f1,f2")
    ap.add_argument("--planos", help="números de plano separados por coma")
    ap.add_argument("--muestras", type=int, default=3)
    ap.add_argument("--res", default="360x640")
    ap.add_argument("--samples", default="8")
    ap.add_argument("--dir")
    a = ap.parse_args()
    ep_d = os.path.join(RAIZ, "studio", "episodios", a.ep)
    esc = os.path.join(ep_d, "escena")
    d = os.path.abspath(a.dir or f"/tmp/prueba-{a.ep}")
    subprocess.run(["rm", "-rf", d])          # cada prueba parte limpia: nada viejo se cuela en la hoja
    os.makedirs(d, exist_ok=True)
    env0 = dict(os.environ, RES=a.res, SAMPLES=a.samples, DIR=d, FORCE="1")
    cuadros = set()
    if a.planos:
        pz = piezas_de(esc, {int(x) for x in a.planos.split(",")})
        for k, v in pz.items():          # misma fórmula de MUESTRAS en todas → los auxiliares calzan con su plano
            r = subprocess.run([sys.executable, "plano.py"], cwd=esc, env=dict(env0, PIEZAS=k, MUESTRAS=str(a.muestras)), capture_output=True, text=True)
            if r.returncode:
                print("FALLA", k, (r.stdout + r.stderr)[-1200:])
        cuadros |= {int(os.path.basename(p)[:5]) for p in glob.glob(os.path.join(d, "[0-9]" * 5 + ".png"))}
    for t in a.trabajos:
        pieza, fs = t.split(":")
        for f in fs.split(","):
            r = subprocess.run([sys.executable, "plano.py"], cwd=esc, env=dict(env0, PIEZAS=pieza, CUADROS=f"{f}-{f}"), capture_output=True, text=True)
            if r.returncode:
                print("FALLA", pieza, f, (r.stdout + r.stderr)[-1200:])
            cuadros.add(int(f))
    if not cuadros:
        sys.exit("nada que probar: usa --planos o pieza:cuadros")
    out = os.path.join(d, "o")
    lista = ",".join(str(f) for f in sorted(cuadros))
    r = subprocess.run([sys.executable, "post.py", d, os.path.join(d, "fin")], cwd=esc,
                       env=dict(os.environ, OUT=out, LISTA=lista, MUESTRAS="1"), capture_output=True, text=True)
    if r.returncode:
        print("FALLA post", (r.stdout + r.stderr)[-1500:])
    planos_json = (glob.glob(os.path.join(out, "*planos.json")) or [None])[0]
    import chequeo_planos as CH, comun
    planos = comun.cargar_planos(planos_json)
    nums, G = CH.cuadros_carpeta(os.path.join(d, "fin"))
    ojos = {f: v for f, v in CH.leer_ojos(os.path.join(d, "meta")).items() if f in set(nums)}
    cajas = CH.leer_cajas(os.path.join(out, "graficos.json") if os.path.exists(os.path.join(out, "graficos.json")) else None,
                          os.path.join(out, "subs_log.json") if os.path.exists(os.path.join(out, "subs_log.json")) else None)
    res = CH.chequear(planos, G, nums, ojos, cajas, ralo=True)
    comun.guardar(os.path.join(d, "chequeo.json"), res)
    hoja(d, nums, planos, ojos, cajas)
    for x in res["fallas"]:
        print(("🛑 " if x["bloqueante"] else "❌ ") + x["que"] + (f" · {x['evidencia']}" if x["evidencia"] else ""))
    for x in res["avisos"]:
        print("⚠️  " + x["que"])
    print(f"hoja: {os.path.join(d, 'hoja.jpg')} · {len(res['fallas'])} fallas, {len(res['avisos'])} avisos")
    sys.exit(1 if res["fallas"] else 0)


def hoja(d, nums, planos, ojos, cajas, W=300, H=533):
    from PIL import Image, ImageDraw
    import chequeo_planos as CH
    fs = [os.path.join(d, "fin", f"{f:05d}.png") for f in nums]
    cols = min(6, max(1, len(fs)))
    filas = -(-len(fs) // cols)
    lienzo = Image.new("RGB", (cols * W, filas * (H + 18)), (20, 20, 20))
    dr = ImageDraw.Draw(lienzo)
    k = W / 1080
    for i, (f, p) in enumerate(zip(nums, fs)):
        x, y = (i % cols) * W, (i // cols) * (H + 18)
        lienzo.paste(Image.open(p).convert("RGB").resize((W, H)), (x, y + 18))
        dr.text((x + 3, y + 3), f"P{CH._plano(planos, (f - 1) / 30)} · {f}", fill=(255, 255, 0))
        for tipo, (x0, y0, x1, y1) in cajas.get(f, []):
            if not tipo.startswith("subt"):
                dr.rectangle((x + x0 * k, y + 18 + y0 * k, x + x1 * k, y + 18 + y1 * k), outline=(80, 160, 255), width=1)
        for ox, oy, r, _n in ojos.get(f, []):
            tap = any(x0 - 0.3 * r <= ox <= x1 + 0.3 * r and y0 - 0.3 * r <= oy <= y1 + 0.3 * r for _t, (x0, y0, x1, y1) in cajas.get(f, []))
            rr = max(3, r * k)
            dr.ellipse((x + ox * k - rr, y + 18 + oy * k - rr, x + ox * k + rr, y + 18 + oy * k + rr), outline=(255, 40, 40) if tap else (40, 255, 90), width=2)
    lienzo.save(os.path.join(d, "hoja.jpg"), quality=85)


if __name__ == "__main__":
    main()
