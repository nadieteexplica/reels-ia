"""Chequeo automático por plano (sin IA). Lo corre el EDITOR en cada prueba y el render en cada borrador, ANTES del auditor:
pilla en segundos lo que en el Ep. 2 costó rondas enteras del auditor.

  python3 tools/auditor/chequeo_planos.py (--video borrador.mp4 | --cuadros carpeta_post) --planos planos.json \\
      [--meta carpeta_render/meta] [--graficos graficos.json] [--subs subs_log.json] [--salida chequeo.json]

Qué mira (umbrales calibrados con el Ep. 2, ver docs/AUDITOR.md):
  🛑 ojo_tapado      un ojo de un personaje bajo un gráfico (lupa, recuadro, píldora, marca) o un subtítulo ≥ 0,2 s
                     (necesita "ojos" en el meta, que escribe plano.py con studio/plantilla/caras.py, y graficos.json del post)
  🛑 quemado         más del 3 % del cuadro sobre 250, sin contar subtítulos ni gráficos, ≥ 0,2 s
  🛑 pantalla_vacia  fondo liso sin contenido ≥ 0,2 s
  ❌ cara_bajo_ui    ojos bajo y 1250 (la interfaz de la app los tapa)
  ❌ plano_quieto    1,6 s o más sin cambio visible (fuera de la franja de subtítulos)
  ⚠️ cara_en_franja  ojos en y 1000–1250 (la franja de subtítulos)
  ⚠️ poco_movimiento la mediana del cambio entre cuadros es muy baja (cámara fija y nada se mueve: P13, P19 y P20 del Ep. 2)
  ⚠️ quieto_1s       entre 1,0 y 1,6 s sin cambio
  ⚠️ fondo_liso      más del 70 % del cuadro es superficie lisa (P19 del Ep. 2: "suelo liso que ocupa la mitad")
  ⚠️ cara_al_borde   ojos pegados al borde o bajo la barra de arriba (y < 200)
Sale con código 1 si hay algún 🛑 o ❌.
"""
import argparse, glob, json, os, sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comun
import detectores as D

FPS = 30
QUIETO_PAR = 0.6        # cambio medio (niveles de gris, 216x384, sin franja) bajo el cual dos cuadros "no cambian"
QUIETO_FALLA, QUIETO_AVISO = 1.6, 1.0
MOV_BAJO = 0.5
LISO_AVISO = 0.70
QUEMADO = 0.03
FRANJA = (1000, 1250)


def _franja_mask():
    m = np.ones((D.DH, D.DW), bool)
    m[int(980 / D.ESC):int(1270 / D.ESC)] = False
    return m


def metricas(G, planos, fps=D.FPS_D):
    """Por plano: mediana del cambio entre cuadros, segundos seguidos sin cambio y fracción de superficie lisa."""
    G = G.astype(np.float32)
    band = _franja_mask()
    d = np.abs(np.diff(G, axis=0))[:, band].mean(axis=1) if len(G) > 1 else np.zeros(0)
    celdas = np.ones((32, 18), bool)
    celdas[int(980 / D.ESC / 12):int(1270 / D.ESC / 12) + 1] = False
    out = {}
    for p in planos:
        a, b = int(round(p["a"] * fps)), int(round(p["b"] * fps))
        seg = d[a + 1:b - 1] if b - a > 3 else d[a:b]
        mejor = act = 0
        for v in seg:
            act = act + 1 if v < QUIETO_PAR else 0
            mejor = max(mejor, act)
        idx = list(range(a, b, max(1, (b - a) // 4)))[:5] or [min(a, len(G) - 1)]
        lis = [float((G[i][:384, :216].reshape(32, 12, 18, 12).std(axis=(1, 3)) < 3.0)[celdas].mean()) for i in idx if i < len(G)]
        out[p["plano"]] = {"mov_mediana": round(float(np.median(seg)), 2) if len(seg) else None,
                           "quieto_max_s": round(mejor / fps, 2), "fondo_liso": round(float(np.mean(lis)), 2) if lis else None}
    return out


def _plano(planos, t):
    return next((p["plano"] for p in planos if p["a"] <= t < p["b"]), planos[-1]["plano"] if planos else None)


def leer_ojos(meta_dir):
    """{cuadro global: [[x, y, r, nombre], ...]} juntando el meta de todas las piezas."""
    ojos = {}
    for p in sorted(glob.glob(os.path.join(meta_dir or "", "*.json"))):
        try:
            d = json.load(open(p))
        except (OSError, json.JSONDecodeError):
            continue
        for f, info in (d.get("cuadros") or {}).items():
            if isinstance(info, dict) and info.get("ojos"):
                ojos.setdefault(int(f), []).extend(info["ojos"])
    return ojos


def leer_cajas(graficos=None, subs=None):
    cajas = {}
    for g in comun.leer(graficos, []) if graficos else []:
        f, tipo, x0, y0, x1, y1 = g[:6]
        cajas.setdefault(int(f), []).append((tipo, (x0, y0, x1, y1)))
    for s in comun.leer(subs, []) if subs else []:
        f, tok, x0, y0, x1, y1 = s[:6]
        cajas.setdefault(int(f), []).append((f"subtítulo '{tok}'", (x0, y0, x1, y1)))
    return cajas


def _agrupar(marcas, planos, ralo):
    """marcas: [(f, clave, detalle)] → eventos por clave con tramos de cuadros seguidos (huecos de ≤2 cuadros)."""
    ev = []
    por = {}
    for f, clave, det in sorted(marcas):
        por.setdefault(clave, []).append((f, det))
    hueco = 60 if ralo else 3
    for clave, fs in por.items():
        grupos = []
        ini = prev = fs[0][0]
        det = fs[0][1]
        for f, d_ in fs[1:]:
            if f - prev <= hueco and _plano(planos, (f - 1) / FPS) == _plano(planos, (prev - 1) / FPS):
                prev = f
                continue
            grupos.append((ini, prev, det))
            ini = prev = f
            det = d_
        grupos.append((ini, prev, det))
        for ini, prev, det in grupos:
            t0, t1 = (ini - 1) / FPS, prev / FPS
            ev.append({"clave": clave, "t0": round(t0, 2), "t1": round(t1, 2), "dur": round(t1 - t0, 2),
                       "plano": _plano(planos, t0), "detalle": det})
    return sorted(ev, key=lambda e: e["t0"])


def ojos_vs_cajas(ojos, cajas, planos, ralo=False):
    tapados, franja, bajo, borde = [], [], [], []
    for f, lista in ojos.items():
        for x, y, r, nombre in lista:
            m = 0.3 * r
            for tipo, (x0, y0, x1, y1) in cajas.get(f, []):
                if x0 - m <= x <= x1 + m and y0 - m <= y <= y1 + m:
                    tapados.append((f, (nombre, tipo.split(" ")[0]), f"{tipo} {[int(x0), int(y0), int(x1), int(y1)]} sobre {nombre} en ({x}, {y})"))
            if y > FRANJA[1]:
                bajo.append((f, nombre, f"{nombre} en y={y}"))
            elif y >= FRANJA[0]:
                franja.append((f, nombre, f"{nombre} en y={y}"))
            if x < 25 or x > 1055 or y < 200:
                borde.append((f, nombre, f"{nombre} en ({x}, {y})"))
    return [_agrupar(z, planos, ralo) for z in (tapados, franja, bajo, borde)]


def cuadros_carpeta(d):
    """Cuadros finales del post (NNNNN.png/jpg, número de cuadro global) → (lista de cuadros, gris 216x384)."""
    from PIL import Image
    fs = sorted(glob.glob(os.path.join(d, "[0-9]" * 5 + ".png")) + glob.glob(os.path.join(d, "[0-9]" * 5 + ".jpg")))
    nums = [int(os.path.basename(f)[:5]) for f in fs]
    G = np.stack([np.asarray(Image.open(f).convert("L").resize((D.DW, D.DH), Image.BOX)) for f in fs]) if fs else np.zeros((0, D.DH, D.DW), np.uint8)
    return nums, G


def quemados(G, nums, cajas):
    """Fracción de píxeles > 250 por cuadro, sin franja de subtítulos ni gráficos."""
    band = _franja_mask()
    out = []
    for i, f in enumerate(nums):
        m = band.copy()
        for _t, (x0, y0, x1, y1) in cajas.get(f, []):
            m[max(0, int(y0 / D.ESC)):int(y1 / D.ESC) + 1, max(0, int(x0 / D.ESC)):int(x1 / D.ESC) + 1] = False
        out.append(float((G[i][m] > 250).mean()) if m.any() else 0.0)
    return out


def chequear(planos, G=None, nums=None, ojos=None, cajas=None, ralo=False, vacias=True):
    """Devuelve {"fallas", "avisos", "planos"} con el mismo formato que checks.py."""
    r = {"fallas": [], "avisos": [], "planos": {}}
    F = lambda q, ev, b=False: r["fallas"].append({"que": q, "evidencia": ev, "bloqueante": b})
    A = lambda q, ev="": r["avisos"].append({"que": q, "evidencia": ev})
    cajas = cajas or {}
    if ojos:
        tap, fra, baj, bor = ojos_vs_cajas(ojos, cajas, planos, ralo)
        for e in tap:
            if ralo or e["dur"] >= 0.2:
                F(f"ojo_tapado · plano {e['plano']}: {e['detalle']}", f"{e['t0']:.2f}–{e['t1']:.2f} s", True)
        for e in baj:
            F(f"cara_bajo_ui · plano {e['plano']}: {e['detalle']} (la interfaz de la app la tapa)", f"{e['t0']:.2f}–{e['t1']:.2f} s")
        for e in fra:
            if ralo or e["dur"] >= 0.3:
                A(f"cara_en_franja · plano {e['plano']}: {e['detalle']} (franja de subtítulos y 1000–1250)", f"{e['t0']:.2f}–{e['t1']:.2f} s")
        for e in bor:
            if ralo or e["dur"] >= 0.3:
                A(f"cara_al_borde · plano {e['plano']}: {e['detalle']}", f"{e['t0']:.2f}–{e['t1']:.2f} s")
        r["ojos_cuadros"] = len(ojos)
    else:
        A("sin datos de ojos en el meta: no se pudo comprobar 'cara tapada' (plano.py + studio/plantilla/caras.py)")
    if G is not None and len(G):
        q = quemados(G, nums, cajas)
        marcas = [(f, "quemado", f"{v * 100:.1f} %") for f, v in zip(nums, q) if v > QUEMADO]
        for e in _agrupar(marcas, planos, ralo):
            if ralo or e["dur"] >= 0.2:
                F(f"quemado · plano {e['plano']}: {e['detalle']} del cuadro sobre 250 (máx. 3 %, sin subtítulos ni gráficos)", f"{e['t0']:.2f}–{e['t1']:.2f} s", True)
        det = D.detalle(G.astype(np.float32))
        marcas = [(f, "vacia", f"detalle {v:.4f}") for f, v in zip(nums, det) if v < 0.008] if vacias else []
        for e in _agrupar(marcas, planos, ralo):
            if ralo or e["dur"] >= 0.2:
                F(f"pantalla_vacia · plano {e['plano']}: fondo liso sin contenido ({e['detalle']})", f"{e['t0']:.2f}–{e['t1']:.2f} s", True)
        if not ralo:
            met = metricas(G, planos)
            r["planos"] = met
            for k, m in met.items():
                if m["quieto_max_s"] >= QUIETO_FALLA:
                    F(f"plano_quieto · plano {k}: {m['quieto_max_s']:.1f} s seguidos sin cambio visible (máx. {QUIETO_FALLA})", "")
                elif m["quieto_max_s"] >= QUIETO_AVISO:
                    A(f"quieto_1s · plano {k}: {m['quieto_max_s']:.1f} s sin cambio visible")
                if m["mov_mediana"] is not None and m["mov_mediana"] < MOV_BAJO:
                    A(f"poco_movimiento · plano {k}: cambio mediano {m['mov_mediana']} (cámara fija y nada se mueve)")
                if m["fondo_liso"] is not None and m["fondo_liso"] > LISO_AVISO:
                    A(f"fondo_liso · plano {k}: {m['fondo_liso'] * 100:.0f} % del cuadro es superficie lisa")
        else:
            for p in planos:
                idx = [i for i, f in enumerate(nums) if p["a"] <= (f - 1) / FPS < p["b"]]
                if idx:
                    met = metricas(G[idx], [{"plano": p["plano"], "a": 0, "b": len(idx) / D.FPS_D}])[p["plano"]]
                    r["planos"][p["plano"]] = {"fondo_liso": met["fondo_liso"], "cuadros": len(idx)}
                    if met["fondo_liso"] and met["fondo_liso"] > LISO_AVISO:
                        A(f"fondo_liso · plano {p['plano']}: {met['fondo_liso'] * 100:.0f} % del cuadro es superficie lisa")
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video")
    ap.add_argument("--cuadros", help="carpeta con los cuadros del post (NNNNN.png)")
    ap.add_argument("--planos", required=True)
    ap.add_argument("--meta")
    ap.add_argument("--graficos")
    ap.add_argument("--subs")
    ap.add_argument("--salida")
    a = ap.parse_args()
    planos = comun.cargar_planos(a.planos)
    ojos = leer_ojos(a.meta) if a.meta else {}
    cajas = leer_cajas(a.graficos if a.graficos and os.path.exists(a.graficos) else None,
                       a.subs if a.subs and os.path.exists(a.subs) else None)
    G = nums = None
    ralo = False
    if a.video:
        G = comun.leer_cuadros(a.video, fps=D.FPS_D, w=D.DW, h=D.DH, gris=True)
        nums = [int(round(i / D.FPS_D * FPS)) + 1 for i in range(len(G))]
    elif a.cuadros:
        nums, G = cuadros_carpeta(a.cuadros)
        ralo = True        # muestras sueltas: cada cuadro cuenta solo
        ojos = {f: v for f, v in ojos.items() if f in set(nums)} if ojos else ojos
    r = chequear(planos, G, nums, ojos, cajas, ralo)
    if a.salida:
        comun.guardar(a.salida, r)
    for x in r["fallas"]:
        print(("🛑 " if x["bloqueante"] else "❌ ") + x["que"] + (f" · {x['evidencia']}" if x["evidencia"] else ""))
    for x in r["avisos"]:
        print("⚠️  " + x["que"] + (f" · {x['evidencia']}" if x["evidencia"] else ""))
    print(f"{len(r['fallas'])} fallas ({sum(1 for x in r['fallas'] if x['bloqueante'])} bloqueantes), {len(r['avisos'])} avisos")
    sys.exit(1 if r["fallas"] else 0)


if __name__ == "__main__":
    main()
