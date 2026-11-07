# 2-voz · ronda 1 · **APROBADO**

Promedio **8.0** (mínimo 8; ningún revisor bajo 7 en ningún criterio).

| criterio | nota (promedio) | más baja | por qué (la más baja) |
|---|---|---|---|
| pronunciacion | 9.0 | 9 | asr_coincidencia 1.0 y asr_diferencias vacío: kamikaze (0.33), 'diecisiete' (1.23), 1945 (3.01), Okinawa (31.95 y 44.74), Truman (43.61), 'atómica' (49.13) salen como el guion; no puedo escuchar el audio, sólo juzgo tiempos y transcripción |
| ritmo | 7.0 | 7 | dos pausas de ~1,1 s en puntos normales (tras 'imposible.' 15.49 → 1,12 s y tras 'perdón.' 20.21 → 1,07 s) sobre el máximo de 0,9 s; los '…' de 'guerra' (0,18 s), 'familia' (0,21 s) y 'rinde' (0,22 s) quedan bajo 0,3 s y casi no se oyen; la voz dura 53,31 s, sobre el límite de 45,5 s de la etapa (el guion declara un techo propio de 62 s por pedido de Tomás) |

## Bloqueantes y fallas automáticas (impiden aprobar)

Ninguno.

## Sugerencias (las 5 más importantes; el resto queda en veredicto.json)

1. pausas de 1,12 s y 1,07 s tras 'casi imposible.' y 'le piden perdón.' sin '…' en el guion; la segunda cae justo antes de la segunda pregunta del gancho, que el guion quiere a los 19 s — 15.49 y 20.21 s. **Arreglo:** tools/pausas.py: recortar ambas a ~0,6 s (0 créditos); ahorra ~1 s y la segunda pregunta ('cómo frenar...') entra a ~19,7 s
2. los '…' de 'guerra...', 'familia...' y 'rinde...' dan sólo 0,18 / 0,21 / 0,22 s de silencio; el de 'rinde... todavía despegan kamikazes' es el remate y debería pesar — 8.39, 18.90, 51.43 s. **Arreglo:** tools/pausas.py: alargar esos tres a 0,4–0,6 s, sobre todo el de 51.43 (remate); no regenerar
3. 'Y el día que Japón se rinde...' va a 4,2 palabras/s, la frase más apurada, y es la de cierre; 'y manda a sus pilotos a no volver' va a 3,9 palabras/s (8.39) — 49.75 s. **Arreglo:** con la pausa más larga tras 'atómica.' (hoy 0,14 s) y tras 'rinde...' se compensa sin tocar el texto
4. duración 53,31 s (+0,4 s de cola) contra 25–45,5 s de la etapa y meta 25–40 s; el guion lo declara como excepción (pedido de 'un minuto', techo 62 s), no pude verificar el presupuesto.json — 53.31 s. **Arreglo:** si no existe esa excepción registrada, recortar ~8 s (p. ej. quitar 'Y a Estados Unidos todavía le falta invadir Japón' o la frase de Truman); si existe, queda como está

## Avisos automáticos

- pausa de 1.12 s después de '(silencio)' · 15.35 s
- pausa de 1.07 s después de '(silencio)' · 20.10 s
- ritmo de 3.9 palabras/s en 'y manda a sus pilotos a no volver.' · 8.39 s
- ritmo de 4.2 palabras/s en 'Y el día que Japón se rinde...' · 49.75 s
