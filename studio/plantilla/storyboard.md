# EpNN — Storyboard (fichas de plano)

Tiempos reales de `words.json` (s). 30 fps, vertical 1080×1920. Meta 25–40 s (techo 45 s), **máximo 6 escenas** (una escena = una actuación animada que se arma una vez y se filma con varias cámaras) y algo que cambia cada 1–2 s, nunca más de 2 s sin cambio (en 35 s, unos 18–35 cambios: los cortes dentro de una escena son baratos). Escalas: **G** general · **M** medio · **P** primer plano · **D** detalle · **I** interior.
Cada fila es la **ficha del plano**: lo que el auditor va a exigir, escrito antes de animar (`docs/MANUAL_PRODUCCION.md` §4). El chequeo automático (`auditar.py preparar <ep> storyboard`) rechaza fichas con columnas vacías, planos de más de 2 s sin "cambio" escrito, caras que bajan de y 1000, más de 6 escenas y más de 3 escenas a medida.

## Concepto
- Idea, personajes (ficha en `ficha.jpg`), set principal, código de color, símbolo que se repite, cómo empalma el loop.

| # | Tiempo | Frase de la voz | Escena | Plano (escala) | Plantilla | Acción visible (se lee en 1 foto) | Cambio (≤ 2 s) | Cámara | Cara (y) | Gráfico (dónde) | SFX | Origen |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.00–1.60 | Este pájaro se come un ají | E1 roca | P desierto | reaccion | el ratón escupe una llamarada junto al pájaro impasible | la llama crece en 0,3 s | push-in 8 % | 380–900 | — | chisporroteo | render |
| 2 | 1.60–2.70 | y ni lo siente. | E1 roca | D cabeza | reaccion | el pájaro traga el ají entero (bulto que baja) | — | tilt siguiendo el bulto | 420–760 | — | glup | render |
| 3 | 2.70–4.40 | Este ratón lo prueba... | E1 roca | M ratón | reaccion | el ratón prueba el ají apoyado en la roca, sin patas | a 0,8 s entra la lupa arriba del ratón | otra cámara de la misma escena | 480–820 | lupa x 600–980 · y 230–430 | mordisco | render |
