# 2-voz · ronda 2 · **APROBADO**

Promedio **8.5** (mínimo 8; ningún revisor bajo 7 en ningún criterio).

| criterio | nota (promedio) | más baja | por qué (la más baja) |
|---|---|---|---|
| pronunciacion | 9.0 | 9 | la transcripción automática calza 100 % con el guion v2.1 (asr_coincidencia 1.0, sin diferencias): las 135 palabras de voz.md son las del guion en orden; 'igual que en tu vaso' (11,41–12,64 s) ya no sale como 'tubazo', y 'Patagonia', 'olímpicas', 'caudaloso', 'triplica', 'Ochenta mil' y 'veinte' se entienden bien |
| ritmo | 8.0 | 8 | 3,06 palabras/s en total, ninguna palabra estirada (la más larga, 'triplica.', 0,72 s), cierres de frase con 0,31–0,68 s de silencio real y los dos '…' con pausa dentro de rango ('llena...' 0,32 s, 'vez...' 0,37 s); lo flojo: 1,02 s de silencio real después de 'atrás.' (34,34 s), fuera de un '…' y justo antes de 'Por eso hay una alarma' (el punto de fuga que predice el guion), y 0,00 s de pausa después de 'noche,' (24,56 s) en el pago; las dos se arreglan con tools/pausas.py (0 créditos): bajar la de 'atrás.' a ~0,5 s y dar ~0,2 s después de 'noche,' |

## Bloqueantes y fallas automáticas (impiden aprobar)

Ninguno.

## Sugerencias (las 5 más importantes; el resto queda en veredicto.json)

1. [A1 sin arreglar] el pago 'Así que en una sola noche, el lago entero se va por ahí' (aviso de 4,2 palabras/s) pasa de 'noche,' a 'el lago entero' con 0,00 s de silencio real, y la pausa que lo prepara después de 'ancho.' (18,65 s) es sólo 0,15 s: el dato que hace mandar el video ('en una sola noche') no aterriza — 19.69-20.10 s. **Arreglo:** con tools/pausas.py (0 créditos): +0,25 s después de 'noche,' y subir a ~0,30 s el silencio después de 'ancho.'; la voz queda en ~26,6 s, dentro del rango
2. [A3 sin arreglar] material insuficiente para verificar la costura del loop: 'vez...' termina en 26,24 s con 0,36 s de silencio real, pero la alineación marca un hueco de 1,00 s; si en el armado se suman ese hueco y la cola de 0,4 s, entre 'otra vez' y 'Anoche' quedarían ~1,4 s y el loop se corta — 26.24 s. **Arreglo:** en el armado dejar entre el fin de 'vez' y el 'Anoche' del reinicio 0,4–0,8 s en total (como un '…'), recortando el silencio sobrante del archivo
3. [A4 sin arreglar] la voz real dura 26,24 s contra los ~31 s estimados en el guion (3,28 vs. 2,9 palabras/s): la tabla 'una frase, una imagen' quedó corrida, y la mecánica (vaso + levanta + se cuela + túnel) cabe ahora en 11,3 s — 7.31-18.65 s. **Arreglo:** rehacer los tiempos del storyboard con esta alineación (p. ej. 'levanta el borde del glaciar' = 11,31–12,95 s, 'se cuela por abajo' = 13,06–15,00 s) antes de las fichas de plano

## Verificación de la ronda anterior

| id | qué | arreglado |
|---|---|---|
| A1 | el pago 'Así que en una sola noche, el lago entero se va por ahí' (aviso de 4,2 palabras/s | **no** |
| A2 | '¿Por dónde se fue el agua?' sale marcada a 4,1 palabras/s, pero son 6 palabras cortas (~8 | sí |
| A3 | material insuficiente para verificar la costura del loop: 'vez...' termina en 26,24 s con  | **no** |
| A4 | la voz real dura 26,24 s contra los ~31 s estimados en el guion (3,28 vs. 2,9 palabras/s): | **no** |

## Avisos automáticos

- pausa de 1.02 s después de '(silencio)' · 34.16 s
