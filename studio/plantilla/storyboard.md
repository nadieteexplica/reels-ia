# EpNN — Storyboard (fichas de plano)

Tiempos reales de `words.json` (s). 30 fps, vertical 1080×1920. 62–65 s, **16–22 planos**. Escalas: **G** general · **M** medio · **P** primer plano · **D** detalle · **I** interior.
Cada fila es la **ficha del plano**: lo que el auditor va a exigir, escrito antes de animar (`docs/MANUAL_PRODUCCION.md` §4). El chequeo automático (`auditar.py preparar <ep> storyboard`) rechaza fichas con columnas vacías, planos de más de 2,2 s sin "cambio" escrito, caras que bajan de y 1000 y más de 22 planos.

## Concepto
- Idea, personajes (ficha en `ficha.jpg`), set principal, código de color, símbolo que se repite, cómo empalma el loop.

| # | Tiempo | Frase de la voz | Plano (escala) | Plantilla | Acción visible (se lee en 1 foto) | Cambio cada 2 s | Cámara | Cara (y) | Gráfico (dónde) | SFX | Origen |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.00–2.10 | Este pájaro se come un ají | P desierto | reaccion | el ratón escupe una llamarada junto al pájaro impasible | la llama crece en 0,3 s; push-in | push-in 8 % | 380–900 | — | chisporroteo | render |
| 2 | 2.10–4.40 | y ni lo siente. | D cabeza | detalle_lupa | el pájaro traga el ají entero (bulto que baja) | a 1,2 s entra la lupa al lado del pico | tilt siguiendo el bulto | 420–760 | lupa x 120–520 · y 260–660 (lugar_libre) | glup | render |
