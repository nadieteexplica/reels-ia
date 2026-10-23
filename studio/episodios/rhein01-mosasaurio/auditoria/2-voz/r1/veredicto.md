# 2-voz · ronda 1 · **APROBADO**

Promedio **8.0** (mínimo 8; ningún revisor bajo 7 en ningún criterio).

| criterio | nota (promedio) | más baja | por qué (la más baja) |
|---|---|---|---|
| pronunciacion | 8.0 | 8 | coincidencia de la transcripción 95,8 %; 'mosasaurio' (0.78 y 35.88), 'Jurassic World' (33.31) y 'T. rex' (35.20, reconocido como 't-rex', o sea 'Ti Rex' bien dicho) salen limpios; 'del'→'de' (5.01) es la fusión normal de 'del largo'; la única duda es 'Rhein'→'ryan' (34.37 y 39.86), que calza con 'Rain' /rajn/ pero hay que confirmarla de oído. |
| ritmo | 8.0 | 8 | ninguna palabra pasa 1,2 s (máx. 'agárrate' 0,92 s), las frases van a 2,8–3,5 palabras/s y la venta a 3,1 (29.69–41.67); flojo en detalles de tiempo cómico: el '...' del gancho casi no pausa (0,14 s en 1.56), la vuelta a la marca va pegada (0,15 s en 30.49) y las pausas del radar (1,38 s) y del chiste (3,37 s) dejan la voz en 41,67 s, 2 s sobre la meta. |

## Bloqueantes y fallas automáticas (impiden aprobar)

Ninguno.

## Sugerencias (las 5 más importantes; el resto queda en veredicto.json)

1. la transcripción oye 'ryan' las dos veces que se dice 'Rhein' (en la presentación del producto y en el eslogan). Lo más probable es que sea la transcripción (no conoce la marca y 'Rain' dicho en español, /rajn/, suena como un 'Ryan' rápido), pero es la marca del cliente en el cierre y no se puede verificar sin escuchar — 34.37 y 39.86 s. **Arreglo:** escuchar esos dos segundos antes del storyboard (0 créditos). Si suena en dos sílabas ('rái-an') o a inglés 'rein', regenerar sólo la toma de la venta escribiendo 'Rayn' (una sílaba, 'ay' como en 'hay') en el texto para la voz; en pantalla sigue 'Rhein'
2. el '...' de 'Para pescar un mosasaurio...' deja sólo 0,14 s de silencio real (el '...' debe dar 0,3–0,9 s): el remate 'necesitas doscientos pollos asados', que es la primera risa y el gancho, entra sin pausa — 1.56 s. **Arreglo:** tools/pausas.py: subir el silencio después de 'mosasaurio' a 0,35–0,4 s (0 créditos, +0,25 s)
3. 'esto...' deja 1,38 s de silencio (más de los 0,9 s de un '...') y el chiste sin voz después de 'agárrate.' dura 3,37 s contra los 2,5 s del guion; por esto la voz queda en 41,67 s + 0,4 de cola = 42,07 s, dentro del techo de 45,5 pero 2 s sobre la meta de 40 — 24.55 y 26.69 s. **Arreglo:** tools/pausas.py: ~0,9 s después de 'esto' (alcanza para dos pitidos del radar) y ~2,5 s después de 'agárrate', salvo que el storyboard necesite más para el salto (ahorra ~1,35 s)
4. después de 'para que no te arranque el bote.' hay 0,90 s de silencio, fuera de los '...' y el triple que en los otros finales de frase (0,28–0,48 s) — 16.20 s. **Arreglo:** tools/pausas.py: bajarlo a ~0,45 s (ahorra 0,45 s)
5. '¿Muy difícil?' y '¡Hay uno que cabe en tu mochila!' van pegados (0,15 s) y la segunda frase corre a 4,6 palabras/s (7 palabras en 1,52 s; el chequeo dice 4,4). Se entiende (la transcripción la sacó entera) y la energía de la venta es buscada, pero la pregunta no alcanza a quedar en el aire justo en el giro a la marca — 30.49 s. **Arreglo:** tools/pausas.py: subir el silencio después de 'difícil?' a ~0,35 s (+0,2 s); no regenerar

## Avisos automáticos

- pausa de 1.38 s después de '(silencio)' · 24.38 s
- pausa de 3.37 s después de '(silencio)' · 26.36 s
- ritmo de 1.9 palabras/s en 'necesitas doscientos pollos asados.' · 1.56 s
- ritmo de 4.4 palabras/s en '¡Hay uno que cabe en tu mochila!' · 30.49 s
- se escucha 'de' donde el guion dice 'del'
- se escucha 'ryan' donde el guion dice 'rhein'
- se escucha 't-rex' donde el guion dice 't rex'
- se escucha 'ryan' donde el guion dice 'rhein'
