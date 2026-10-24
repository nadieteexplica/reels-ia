# 2-voz · ronda 1 · **APROBADO**

Promedio **8.5** (mínimo 8; ningún revisor bajo 7 en ningún criterio).

| criterio | nota (promedio) | más baja | por qué (la más baja) |
|---|---|---|---|
| pronunciacion | 9.0 | 9 | la transcripción coincide en 98,9 % y la única diferencia ('rascacielos' → 'rascacielo', 0.34–0.91 s) se explica por la -s final pegada a la s de 'se' (la alineación le da a 'se' sólo 0.06 s y no hay silencio entre las dos): es un error de la transcripción, no de la voz; las cifras del remate ('dos', 'diez', 34.65–36.13) y 'hidráulicos', 'achicó', 'gatos' salen bien. |
| ritmo | 8.0 | 8 | ninguna palabra pasa de 1,2 s (la más larga, 'electricidad.', 0.82 s), los dos '...' sí hacen pausa (0.67 s en 1.78 y 0.77 s en 19.22) y dura 36.87 s (37.3 con la cola, dentro de la meta); las frases 'lentas' que avisa el chequeo (3.34 y 23.05) se miden contando la pausa anterior: habladas van a 2.8 y 2.5 palabras/s, normales para frases cortas de golpe. Lo flojo: las pausas de punto (0.50–0.65 s) casi igualan a las de '...' y el conjunto queda en 2.5 palabras/s, más lento que el ~2.9 habitual de Fernando. |

## Bloqueantes y fallas automáticas (impiden aprobar)

Ninguno.

## Sugerencias (las 5 más importantes; el resto queda en veredicto.json)

1. las pausas de fin de frase son casi tan largas como las dramáticas: 'techo.' 0.65 s (7.92), 'abajo.' 0.57 (16.08), 'final,' 0.52 en una coma (17.14), 'piso.' 0.60 (20.38), 'vez.' 0.62 (21.78), 'obra.' 0.61 (32.12), contra 0.67 y 0.77 de los '...'; suman ~9 s de silencio en 36.9 s y el '...' no se distingue como pausa buscada — 7.92 s. **Arreglo:** con tools/pausas.py (0 créditos) dejar las pausas de punto y coma en ~0.35 s y mantener los '...' en 0.6–0.8 s: el '...' vuelve a sonar dramático y la voz baja a ~34.5 s
2. la pausa antes del giro ('Y lo más loco:') es la más corta de todo el video (0.23 s después de 'reversa.'), así que el giro se pega a la frase anterior justo donde debería marcarse; la del remate ('dos pisos menos cada diez días', después de 'nota:' en 34.41) es 0.36 s — 25.41 s. **Arreglo:** con tools/pausas.py alargar a ~0.5 s la pausa después de 'reversa.' y dejar en ~0.45 s la de 'nota:', para que el giro y la cifra final sean las dos pausas marcadas del tramo final
3. la transcripción entendió 'rascacielo' en 'Este rascacielos se achicó'; es la -s final fundida con la s de 'se' (en el habla corrida suenan como una sola), error de la transcripción, no de la voz; no se puede confirmar sin escuchar — 0.34 s. **Arreglo:** no regenerar; Tomás lo confirma al escuchar el primer segundo en el mensaje de aprobación (y aunque se oyera 'rascacielo', es la forma común al hablar y nadie lo notaría como error)

## Avisos automáticos

- ritmo de 2.2 palabras/s en 'Sin una sola explosión.' · 3.34 s
- ritmo de 2.1 palabras/s en 'Como su construcción, en reversa.' · 23.05 s
- se escucha 'rascacielo' donde el guion dice 'rascacielos'
