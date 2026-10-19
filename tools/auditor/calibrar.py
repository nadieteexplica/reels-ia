"""Calibración del auditor: ¿encontró los errores conocidos? (tools/auditor/calibracion.json)

  python3 tools/auditor/calibrar.py [--md salida.md]

Un caso cuenta como DETECTADO si algún problema del revisor (o una falla automática) cae en el plano o clip del caso
(y en su rango de tiempo, si tiene) y su texto tiene alguna de las palabras clave. Se usa la última ronda con resultados.
"""
import argparse, glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
import comun
from checks import norm

BASE = os.path.join(comun.EPIS, "ep01-congelamiento-cerebral", "auditoria", "historico")


def segundos(x):
    if x is None:
        return []
    return [float(v.replace(",", ".")) for v in re.findall(r"\d+(?:[.,]\d+)?", str(x))]


def problemas(base, etapa):
    d = os.path.join(BASE, base, etapa)
    rondas = sorted(glob.glob(os.path.join(d, "r*")), key=lambda p: int(p.rsplit("r", 1)[1]))
    for rd in reversed(rondas):
        outs = [f for f in glob.glob(os.path.join(rd, "*.json")) if os.path.basename(f) not in ("checks.json", "encargos.json", "veredicto.json")]
        encs = comun.leer(os.path.join(rd, "encargos.json"), []) or []
        completa = all((comun.leer(os.path.join(rd, e["salida"]), {}) or {}).get("completo") for e in encs)
        if (outs or os.path.exists(os.path.join(rd, "checks.json"))) and (completa or rd == rondas[0]):
            ps = []
            for f in outs:
                o = comun.leer(f, {})
                for p in o.get("problemas", []):
                    ps.append(dict(p, _de=os.path.basename(f)))
                for e in o.get("eventos", []) or []:
                    if e.get("es_defecto"):
                        ps.append({"que": e.get("por_que", ""), "evento": e.get("id"), "_de": os.path.basename(f)})
            ch = comun.leer(os.path.join(rd, "checks.json"), {})
            for x in ch.get("fallas", []):
                ps.append({"que": x["que"] + " " + x.get("evidencia", ""), "_de": "checks", "automatico": True})
            return os.path.basename(rd), ps
    return None, []


def coincide(caso, p):
    txt = norm(" ".join(str(p.get(k, "")) for k in ("que", "arreglo", "plano", "segundo", "donde")))
    if not any(norm(w) in txt for w in caso["palabras"]):
        return False
    if "clips" in caso:
        etiqueta = norm(str(p.get("plano", "")) + " " + str(p.get("que", "")))
        if any(norm(x) in etiqueta for x in caso.get("excluir", [])) and not any(
                re.search(re.escape(norm(c)) + r"(?![_a-z])", etiqueta) for c in caso["clips"]):
            return False
        return any(re.search(re.escape(norm(c)) + r"(?![_a-z])", etiqueta) for c in caso["clips"])
    if not caso.get("planos") and "t" not in caso:      # caso global de la etapa (chequeos automáticos)
        return True
    pl = p.get("plano")
    try:
        pl = int(pl)
    except (TypeError, ValueError):
        pl = None
    en_plano = pl in caso["planos"] or any(re.search(rf"\bplano {n}\b", txt) for n in caso["planos"])
    if "t" in caso:
        ts = segundos(p.get("segundo")) + segundos(p.get("donde"))
        en_t = any(caso["t"][0] <= t <= caso["t"][1] for t in ts)
        return en_t or (en_plano and not ts)
    return en_plano


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md")
    a = ap.parse_args()
    spec = comun.leer(os.path.join(os.path.dirname(__file__), "calibracion.json"))
    filas, ok = [], 0
    for c in spec["casos"]:
        if c.get("tipo") == "pedido":       # se prueba el chequeo de instrucciones de Kling con el pedido viejo sacado de git
            import subprocess, checks
            viejo = json.loads(subprocess.run(["git", "show", c["git"]], capture_output=True, text=True, cwd=comun.RAIZ).stdout or "[]")
            r = checks.pedidos_kling({x["nombre"]: x for x in viejo})
            ronda, ps = "chequeo", [{"que": f["que"], "_de": "checks"} for f in r["fallas"]]
            c = dict(c, planos=[])
        else:
            ronda, ps = problemas(c["base"], c["etapa"])
        hits = [p for p in ps if coincide(c, p)]
        det = bool(hits)
        ok += det
        ej = hits[0] if hits else {}
        donde = " · ".join(x for x in (f"plano {ej.get('plano')}" if ej.get("plano") not in (None, "") else "",
                                        f"{ej.get('segundo')} s" if ej.get("segundo") else "") if x)
        filas.append(f"| {c['id']} | {'#' + str(c['leccion']) if c['leccion'] else 'nuevo'} | {c['que']} | {c.get('base', 'git')} · {c.get('etapa', 'pedido viejo')} {ronda or '—'} | "
                     f"{'✅' if det else '❌'} | {len(hits)} | {donde} {('— ' + ej.get('que', '')[:110]) if ej else ''} |")
    head = "| caso | lección | error conocido | dónde se auditó | detectado | menciones | ejemplo |\n|---|---|---|---|---|---|---|\n"
    tabla = head + "\n".join(filas) + f"\n\n**{ok}/{len(spec['casos'])} detectados.**\n"
    print(tabla)
    if a.md:
        open(a.md, "w").write(tabla)
    sys.exit(0 if ok == len(spec["casos"]) else 1)


if __name__ == "__main__":
    main()
