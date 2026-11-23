---
name: voz
description: Genera la locución de un guion de El viejo del dato con el narrador elegido (Qwen3-TTS clonado desde voz/narrador.wav) en GitHub Actions, con pausas apretadas, subtítulos por palabra (words.json con Whisper) y chequeo de pronunciación. Usar después del guion aprobado.
---

# Voz

- **La voz es el narrador** (`voz/narrador.wav` + `voz/narrador.json`). No se diseña otra ni se clona a nadie más (sólo a Tomás, si él manda su audio). ElevenLabs está cancelado.
- **Dónde corre:** GitHub Actions (`voz-libre.yml`, Mac `macos-15`, gratis). En el Mac de Tomás también corre, pero usa ~7 de 8 GB: no lo hagas ahí salvo que lo pida, y los modelos no se bajan por adelantado.

## Pasos
1. Texto de la voz en `studio/episodios/<ep>/voz.txt` (sólo lo que se dice, con la puntuación que marca las pausas; números en palabras si se leen raro: "cuarenta" y no "40").
2. Trabajo `jobs/voz-libre/NNNN-<ep>.json`: `{"id": "<ep>", "voz": "narrador", "textos": {"<ep>": "studio/episodios/<ep>/voz.txt"}}` → commit y push (se dispara solo). ~4 min por 50 s.
3. `git pull` → en `out/voz-libre/<ep>/`: `<ep>.wav` (pausas ≤ 0,3 s y hasta 1,2× con `tools/voz_ajustar.py`), `<ep>.words.json` (Whisper medium + large-v3-turbo promediados; 36 ms de error medio) y `metricas_<ep>.json`.
4. **Chequeo** (puerta 2 del auditor, automática):
   - Duración 35–50 s (YouTube primero; techo 52 s). Si se pasa, se acorta el guion, no se acelera más de 1,2×.
   - `metricas`: cada diferencia de la transcripción es un posible error de pronunciación (las de números escritos "15" vs "quince" no cuentan). Un nombre propio o cifra mal dicha → se escribe fonético en `voz.txt` y se regenera.
   - `huella.json`: similitud ≥ 0,98 con la referencia en todos los trozos (si baja, ese trozo se regenera con otra semilla).
5. Copia `<ep>.wav` y `<ep>.words.json` a `studio/episodios/<ep>/` como `voz.wav` y `words.json` (lo que leen el storyboard, el sonido y el render).
