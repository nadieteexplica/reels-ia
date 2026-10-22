# Etapa 2 — Voz

**Criterios:** `pronunciacion`, `ritmo`.
**Materiales:** `voz.md` (cada palabra con inicio, fin y duración según la alineación, y el **silencio real** medido en el audio después de cada palabra), `guion.md`, y en `checks.json` → `datos.asr_diferencias`: lo que entendió una transcripción automática del audio contra lo que dice el guion.

No puedes escuchar el audio: juzgas con los tiempos y la transcripción. Dilo en el resumen.

## Revisa
1. **Pronunciación.** Cada diferencia de la transcripción:
   - Nombres propios, términos técnicos o cifras que salen distintos (p. ej. "Humboldt" → "humbol", "1954" → "1945") = probablemente mal pronunciado → problema prioridad 1 con la palabra y el segundo, y como arreglo la escritura fonética para ElevenLabs.
   - Diferencias de puntuación, tildes o palabras homófonas = error de la transcripción, no de la voz (márcalo así).
   - Si la coincidencia general es baja o falta la transcripción, `pronunciacion` no puede ser ≥8.
2. **Ritmo.** Palabras estiradas (más de 1,2 s), pausas largas fuera de los "…" del guion, frases apuradas (más de ~3,8 palabras/s) o lentas (menos de ~2,2), y que los "…" sí produzcan pausa (0,3–0,9 s). **Las pausas se juzgan con la columna "silencio real"**, no con el hueco de la alineación: la alineación mete parte del silencio dentro de la palabra.
3. **Duración:** entre 25 y 45,5 s en total (con la cola de 0,4 s); meta 25–40 s. Si se pasa, se recorta el guion. Las pausas se arreglan con `tools/pausas.py` (0 créditos), no regenerando.

Sólo te llaman si la transcripción automática encontró diferencias o hay ritmo raro: concéntrate en eso.
