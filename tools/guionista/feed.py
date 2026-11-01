"""Arma los "feeds" ciegos para la prueba de deslizamiento del guionista (docs/GUIONISTA.md §5).

  python3 tools/guionista/feed.py <ep | carpeta> [--paneles 5] [--semilla N]

Lee studio/episodios/<ep>/guionista/candidatos.json (paquetes de gancho del guionista) y
tools/guionista/calibracion/anclas.json (los videos publicados, con su resultado real, que NUNCA se muestra).
Escribe en studio/episodios/<ep>/guionista/prueba/:
  panel<N>.md   un feed por espectador: anclas + candidatos mezclados, cada uno con un código al azar,
                sin decir cuáles son reales ni cómo les fue
  clave.json    código -> id, por panel (sólo para puntuar.py; no se le pasa a nadie)

Cada panel lleva todas las anclas y UN candidato (rotando; --paneles = múltiplo del número de candidatos), en un orden
distinto, para que ni el orden ni la repetición decidan. Con --juntos van todos los candidatos en cada panel (sólo para
ideas distintas entre sí).
"""
import argparse, json, random, string
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
MAX_PALABRAS = {"cuadro0": 45, "0_3s": 40}  # como las anclas: si el candidato se describe más lindo, gana por la prosa
ANCLAS = RAIZ / "tools/guionista/calibracion/anclas.json"
CAMPOS = ("cuadro0", "0_3s", "texto_pantalla_0_3s", "voz_0_3s", "resto")

INSTRUCCIONES = """# Tu feed de Shorts

Estás pasando YouTube Shorts con el pulgar, como cualquier noche. Te van a aparecer {n} videos, uno tras otro, en el orden de abajo.
Ninguno es de una cuenta que sigas. De cada uno tienes lo que se ve y se oye en los primeros 3 segundos (descrito cuadro a cuadro)
y, si decides quedarte, el resto de lo que dice la voz.

Eres: **{perfil}**

Reglas para contestar:
- Decide como de verdad decides en un feed: en menos de 2 segundos y con flojera. Lo normal es deslizar; quedarse se gana.
- Primero mira SOLO lo de los primeros 3 s ("Cuadro 0" y "0–3 s", o la imagen si la hay, más "Texto en pantalla" y "Voz 0–3 s"). Decide si deslizas ANTES de leer "Si te quedas".
- Si en el cuadro 0 no entiendes qué estás mirando, o se ve falso, genérico, de IA, o como una clase, deslizas.
- No premies lo "inteligente": premia lo que te haría quedarte, reírte o mandárselo a alguien.
- Si te quedas, lee "Si te quedas" y di en qué frase te irías (si te vas) y por qué, en tus palabras.

Contesta SOLO con un JSON válido (sin texto antes ni después), con esta forma:
{{"perfil": "<tu nombre>",
  "videos": [
    {{"codigo": "<código>",
      "se_queda_2s": true|false,
      "por_que_2s": "<una frase: qué viste o entendiste en el primer segundo>",
      "se_va_en": "<frase exacta donde te irías, o 'final' si lo ves entero, o 'cuadro0'>",
      "lo_ve_entero_pct": <0-100, probabilidad de que lo veas hasta el final>,
      "lo_manda": true|false,
      "a_quien": "<a quién, o ''>",
      "pregunta_que_te_dejo": "<la pregunta que te hizo quedarte, o ''>"}}
  ],
  "orden": ["<código del que más te enganchó>", "...", "<código del que menos>"]}}
"""


def bloque(codigo, p, img=None):
    ver = (f"- **Imagen de 0–3 s (míralo con Read: 6 cuadros de izquierda a derecha en 0, 0,5, 1, 1,5, 2 y 3 s):** `{img}`\n"
           if img else "")
    desc = "" if img else (f"- **Cuadro 0:** {p['cuadro0']}\n"
                           f"- **0–3 s:** {p['0_3s']}\n")
    return (f"## Video {codigo} ({p.get('dur_s', '?')} s)\n" + ver + desc +
            f"- **Texto en pantalla:** {p.get('texto_pantalla_0_3s') or 'subtítulos palabra por palabra'}\n"
            f"- **Voz 0–3 s:** \"{p['voz_0_3s']}\"\n"
            f"- **Si te quedas:** {p['resto']}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ep")
    ap.add_argument("--paneles", type=int, default=5)
    ap.add_argument("--semilla", type=int, default=None)
    ap.add_argument("--juntos", action="store_true",
                    help="todos los candidatos en cada panel (sólo si son ideas DISTINTAS; con guiones de la misma idea el "
                         "espectador castiga la repetición: Ep. 8, 1-nov-2026)")
    ap.add_argument("--imagenes", action="store_true",
                    help="usar la tira de cuadros reales de 0–3 s ('tira' en el paquete; anclas: calibracion/<id>_0-3s.jpg)")
    a = ap.parse_args()
    rnd = random.Random(a.semilla)
    base = Path(a.ep).resolve() if Path(a.ep).is_dir() else RAIZ / "studio/episodios" / a.ep / "guionista"
    fc = base / "candidatos.json"
    cand = json.load(open(fc))["candidatos"] if fc.exists() else []
    anclas = json.load(open(ANCLAS))["anclas"]
    perfiles = json.load(open(RAIZ / "tools/guionista/perfiles.json"))["perfiles"]
    for p in cand + anclas:
        falta = [c for c in CAMPOS if not p.get(c)]
        if falta:
            raise SystemExit(f"{p.get('id')}: faltan {falta}")
        for campo, tope in MAX_PALABRAS.items():
            if len(str(p.get(campo, "")).split()) > tope:
                raise SystemExit(f"{p['id']}: '{campo}' tiene más de {tope} palabras; descríbelo seco, como las anclas")
    items = [("C", p) for p in cand] + [("A", p) for p in anclas]
    out = base / ("prueba_img" if a.imagenes else "prueba")
    out.mkdir(parents=True, exist_ok=True)
    if a.imagenes:
        import shutil
        (out / "img").mkdir(exist_ok=True)
    clave = {}
    usados = set()
    anclas_items = [("A", p) for p in anclas]
    for n in range(1, a.paneles + 1):
        if a.juntos or not cand:
            orden = items[:]
        else:  # un solo candidato por panel, rotando: cada guion se ve fresco, como en el feed real
            orden = [("C", cand[(n - 1) % len(cand)])] + anclas_items
        rnd.shuffle(orden)
        clave[f"panel{n}"] = {}
        texto = []
        for tipo, p in orden:
            while True:
                cod = "".join(rnd.choice(string.ascii_uppercase) for _ in range(2))
                if cod not in usados:
                    usados.add(cod)
                    break
            clave[f"panel{n}"][cod] = {"id": p["id"], "tipo": "ancla" if tipo == "A" else "candidato"}
            img = None
            if a.imagenes:
                src = Path(p["tira"]) if p.get("tira") else ANCLAS.parent / f"{p['id']}_0-3s.jpg"
                if not src.is_absolute():
                    src = RAIZ / src
                if not src.exists():
                    raise SystemExit(f"{p['id']}: no está la tira {src}")
                img = out / "img" / f"{cod}.jpg"
                shutil.copy(src, img)
            texto.append(bloque(cod, p, img))
        perfil = perfiles[(n - 1) % len(perfiles)]
        md = INSTRUCCIONES.format(n=len(orden), perfil=perfil) + "\n" + "\n".join(texto)
        (out / f"panel{n}.md").write_text(md)
    (out / "clave.json").write_text(json.dumps(clave, ensure_ascii=False, indent=1))
    print(f"{a.paneles} paneles con {len(cand)} candidatos + {len(anclas)} anclas en {out}")


if __name__ == "__main__":
    main()
