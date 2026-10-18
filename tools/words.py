"""Arma words.json (lista de {w, s, e}) desde la alineación de ElevenLabs.

Uso:
  python3 tools/words.py out/tts/<id>.json <salida/words.json> [guion_pantalla.txt]

- Usa "alignment" (coincide carácter a carácter con el texto enviado), NO "normalized_alignment".
- Si el texto enviado a la voz tenía palabras escritas fonéticamente, pasa el guion de pantalla:
  cada palabra se reemplaza por la del guion (deben tener el mismo número de palabras).
"""
import json, sys

src, dst = sys.argv[1], sys.argv[2]
al = json.load(open(src, encoding="utf-8"))["alignment"]
chars, starts, ends = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
words, cur, s, e = [], "", None, None
for c, a, b in zip(chars, starts, ends):
    if c.isspace():
        if cur:
            words.append({"w": cur, "s": round(s, 3), "e": round(e, 3)}); cur = ""
        continue
    if not cur:
        s = a
    cur += c; e = b
if cur:
    words.append({"w": cur, "s": round(s, 3), "e": round(e, 3)})
if len(sys.argv) > 3:
    screen = open(sys.argv[3], encoding="utf-8").read().split()
    if len(screen) != len(words):
        sys.exit(f"ERROR: guion de pantalla tiene {len(screen)} palabras y la voz {len(words)}")
    for w, x in zip(words, screen):
        w["w"] = x
long = [w for w in words if w["e"] - w["s"] > 1.2]
json.dump(words, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(f"{len(words)} palabras · {words[-1]['e']:.2f} s" + (f" · OJO palabras > 1,2 s: {[w['w'] for w in long]}" if long else ""))
