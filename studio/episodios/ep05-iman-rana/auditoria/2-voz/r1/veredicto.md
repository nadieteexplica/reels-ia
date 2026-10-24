# 2-voz · ronda 1 · **APROBADO**

Promedio **8.5** (mínimo 8; ningún revisor bajo 7 en ningún criterio).

| criterio | nota (promedio) | más baja | por qué (la más baja) |
|---|---|---|---|
| pronunciacion | 9.0 | 9 | la transcripción automática coincide 1,0 con el guion y no tiene diferencias, incluidas las palabras de riesgo ('teslas' 28.64, 'centímetros' 23.40, 'bobinas' 26.23, 'reactor nuclear' 33.72); no puedo escuchar la entonación de '¿Y para ti?' (17.07) |
| ritmo | 8.0 | 8 | 37,83 s (38,2 s con la cola) a 2,78 palabras/s, ninguna palabra pasa de 1,2 s (máx. 'flotarías.' 1,00 s al cierre), los puntos dejan 0,33–0,50 s y 'empuja...' 0,50 s; lo flojo es el remate: 'entero...' 0,24 s, 'ti.'→'Ahí' 0,00 s y 'sí...' 0,20 s. Los dos avisos no son defectos: 'Más del doble…' (29.79) da 3,9 palabras/s por 5 monosílabos, pero son 14 sílabas en 2,09 s (habla normal); 'Primero: un hueco…' (19.51) a 2,1 palabras/s es el énfasis buscado del primer paso |

## Bloqueantes y fallas automáticas (impiden aprobar)

Ninguno.

## Sugerencias (las 5 más importantes; el resto queda en veredicto.json)

1. el remate 'solo para ti. Ahí sí... flotarías.' pierde el golpe: entre 'ti.' y 'Ahí' hay 0,00 s de silencio y la pausa dramática de 'sí...' dura 0,20 s, menos que cualquier punto normal del guion (0,33–0,46 s), así que el final suena apurado justo en el remate — 35.92–36.83 s. **Arreglo:** con tools/pausas.py (0 créditos): 0,35 s después de 'ti.' (35.92) y subir la de 'sí...' (36.72) a 0,45 s; suma ~0,6 s
2. 'entero...' deja 0,24 s, bajo el rango 0,3–0,9 s de los '…': 'reactor nuclear entero' se pega a 'solo para ti' y el remate del gigavatio no respira — 35.05 s. **Arreglo:** subir el silencio después de 'entero...' a 0,40 s con tools/pausas.py (+0,16 s)
3. los 3 pasos de la construcción quedan con pausas disparejas: 0,24 s después de 'Primero:' (20.32), 0,14 s después de 'Después:' (26.16) y 0,00 s después de 'Y al final,' (32.84); el tercer paso no se marca como paso — 26.16 / 32.84 s. **Arreglo:** dejar ~0,22 s después de 'Después:' y de 'final,' con tools/pausas.py (+0,3 s). Con las 3 sugerencias, la voz queda en ~38,9 s (39,3 s con la cola), dentro de la meta de 40 s

## Avisos automáticos

- ritmo de 2.1 palabras/s en 'Primero: un hueco donde quepas.' · 19.51 s
- ritmo de 3.9 palabras/s en 'Más del doble de lo que necesitó la rana.' · 29.79 s
