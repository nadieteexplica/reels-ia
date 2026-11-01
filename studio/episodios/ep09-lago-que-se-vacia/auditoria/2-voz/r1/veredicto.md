# 2-voz · ronda 1 · **APROBADO**

Promedio **8.5** (mínimo 8; ningún revisor bajo 7 en ningún criterio).

| criterio | nota (promedio) | más baja | por qué (la más baja) |
|---|---|---|---|
| pronunciacion | 9.0 | 9 | la transcripción automática coincide al 100 % con el guion (asr_coincidencia 1.0, sin diferencias): 'Patagonia', 'glaciar', 'represa', 'túnel' y 'ahí' salen bien; no llega a 10 porque sin escuchar no se puede juzgar acento ni entonación |
| ritmo | 8.0 | 8 | 3,28 palabras/s en total, ninguna palabra sobre 1,2 s (la más larga, 'llena...' 0,71 s), el '…' de 24,84 s da 0,52 s de silencio real y no hay pausas largas fuera de él; flojo sólo el pago de 18,76–21,73 s, que va a 4,2 palabras/s sin respiro después de 'noche,' (0,00 s) |

## Bloqueantes y fallas automáticas (impiden aprobar)

Ninguno.

## Sugerencias (las 5 más importantes; el resto queda en veredicto.json)

1. el pago 'Así que en una sola noche, el lago entero se va por ahí' (aviso de 4,2 palabras/s) pasa de 'noche,' a 'el lago entero' con 0,00 s de silencio real, y la pausa que lo prepara después de 'ancho.' (18,65 s) es sólo 0,15 s: el dato que hace mandar el video ('en una sola noche') no aterriza — 19.69-20.10 s. **Arreglo:** con tools/pausas.py (0 créditos): +0,25 s después de 'noche,' y subir a ~0,30 s el silencio después de 'ancho.'; la voz queda en ~26,6 s, dentro del rango
2. '¿Por dónde se fue el agua?' sale marcada a 4,1 palabras/s, pero son 6 palabras cortas (~8 sílabas en 1,4 s, ritmo normal en español): no está apurada; lo único es que la pregunta que abre el video entra con sólo 0,23 s después de 'represa.' — 5.70-7.16 s. **Arreglo:** opcional, con tools/pausas.py: subir a ~0,35 s el silencio después de 'represa.' (5,70 s) para que la pregunta se despegue del contexto
3. material insuficiente para verificar la costura del loop: 'vez...' termina en 26,24 s con 0,36 s de silencio real, pero la alineación marca un hueco de 1,00 s; si en el armado se suman ese hueco y la cola de 0,4 s, entre 'otra vez' y 'Anoche' quedarían ~1,4 s y el loop se corta — 26.24 s. **Arreglo:** en el armado dejar entre el fin de 'vez' y el 'Anoche' del reinicio 0,4–0,8 s en total (como un '…'), recortando el silencio sobrante del archivo
4. la voz real dura 26,24 s contra los ~31 s estimados en el guion (3,28 vs. 2,9 palabras/s): la tabla 'una frase, una imagen' quedó corrida, y la mecánica (vaso + levanta + se cuela + túnel) cabe ahora en 11,3 s — 7.31-18.65 s. **Arreglo:** rehacer los tiempos del storyboard con esta alineación (p. ej. 'levanta el borde del glaciar' = 11,31–12,95 s, 'se cuela por abajo' = 13,06–15,00 s) antes de las fichas de plano

## Avisos automáticos

- ritmo de 4.1 palabras/s en '¿Por dónde se fue el agua?' · 5.70 s
- ritmo de 4.2 palabras/s en 'Así que en una sola noche, el lago entero se va por ahí.' · 18.65 s
