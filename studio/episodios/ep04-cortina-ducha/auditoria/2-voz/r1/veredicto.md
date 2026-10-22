# 2-voz · ronda 1 · **APROBADO**

Promedio **8.0** (mínimo 8; ningún revisor bajo 7 en ningún criterio).

| criterio | nota (promedio) | más baja | por qué (la más baja) |
|---|---|---|---|
| pronunciacion | 8.0 | 8 | La transcripción automática coincide al 100 % con el guion y no hay ninguna diferencia (asr_diferencias vacío); no hay nombres propios ni cifras, y las palabras más técnicas ('remolino' 16.05, 'presión' 20.87) salen con duración normal (0.42 y 0.38 s). No puedo escuchar el audio, por eso 8 y no más. |
| ritmo | 8.0 | 8 | Total 35.65 s (36.05 con la cola de 0.4 s), 97 palabras = guion, 2.72 palabras/s; ninguna palabra pasa de 0.92 s ('fantasma.' 34.73) y las tres pausas '...' producen silencio real de 0.33 s (1.25), 0.36 s (15.35) y 0.92 s (33.25), la última 0.02 s sobre el rango pero es el remate del chiste. |

## Bloqueantes y fallas automáticas (impiden aprobar)

Ninguno.

## Sugerencias (las 5 más importantes; el resto queda en veredicto.json)

1. El silencio tras '¿La solución?' mide 0.79 s, el más largo fuera de un '...' y en medio de la explicación; junto con 'rueda.' (0.60 s, 18.90), 'baja.' (0.66 s, 21.85) y 'ti.' (0.63 s, 25.96) hace que los puntos pesen más que los '...' de 'duchando...' (0.33 s) y 'abajo...' (0.36 s), así que el remate de 33.25 no se distingue tanto del resto. — 27.32 s. **Arreglo:** con tools/pausas.py (0 créditos) bajar la pausa de 27.32 a ~0.5 s y las de 18.90, 21.85 y 25.96 a ~0.45 s: gana ~1 s, la voz queda en ~35 s y el '...' final se nota más; sólo si los planos de esos puntos no necesitan ese aire para animarse
2. 'Y el aire de afuera, que empuja más,' son 8 palabras en 1.94 s (~4.1 palabras/s), por sobre las ~3.8 recomendadas, y el silencio real tras 'afuera,' (22.89) y tras 'más,' (0.24 s) es casi nulo: la oración sale corrida justo en el paso que explica por qué la cortina entra. — 22.32 s. **Arreglo:** con tools/pausas.py meter ~0.15 s tras 'afuera,' (23.25); no hace falta regenerar la voz
3. Los dos avisos del checks.json ('Una cortina más pesada.' 1.9 palabras/s en 27.32 y 'ahí sí es un fantasma.' 2.1 en 33.25) son falsos positivos: el cálculo cuenta la pausa anterior dentro de la frase. Sin ella, 'Una cortina más pesada.' va a 2.7 palabras/s (27.92–29.42) y 'ahí sí es un fantasma.' a ~2.9 (33.95–35.65). — 27.32 s. **Arreglo:** ninguno en la voz; no hay frases lentas reales

## Avisos automáticos

- ritmo de 1.9 palabras/s en 'Una cortina más pesada.' · 27.32 s
- ritmo de 2.1 palabras/s en 'ahí sí es un fantasma.' · 33.25 s
