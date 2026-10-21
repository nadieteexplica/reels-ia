# 2-voz · ronda 1 · **APROBADO**

Promedio **8.0** (mínimo 8; ningún revisor bajo 7 en ningún criterio).

| criterio | nota (promedio) | más baja | por qué (la más baja) |
|---|---|---|---|
| pronunciacion | 8.0 | 8 | Coincidencia ASR 0,966 y 181/181 palabras; 'dos mil veinte'→'2020' y 'dos mil tres'→'2003' son la transcripción escribiendo cifras con dígitos (mismo valor), 'shanghai'→'shangai' es grafía de la transcripción (Shanghái suena 'shangái'); la única dudosa es 'seiscientas'→'seiscientos' (11.06–11.63 s): mismo valor, sólo el género, y con duración normal (0,57 s), pero sin audio no puedo descartarla. |
| ritmo | 8.0 | 8 | 62,91 s de voz (63,31 s con la cola), 2,88 palabras/s, ninguna palabra sobre 1,2 s (la más larga 'caminar.' 0,79 s); 'broma...' (0,57 s) y 'columnas...' (0,43 s) sí pausan, pero 'conciertos...' (56.23, 0,17 s) y 'años...' (60.95, 0,19 s) quedan bajo 0,3 s justo en los dos remates del final, y 'peso.'→'El otro' (30.36) no tiene silencio. Las pausas fuera de los '...' ('¿Y' 0,38 s, 'Tú' 0,42 s, 'Y lo más loco' 0,36 s) son cortas y funcionan como golpe. |

## Bloqueantes y fallas automáticas (impiden aprobar)

Ninguno.

## Sugerencias (las 5 más importantes; el resto queda en veredicto.json)

1. La transcripción oyó 'siete mil seiscientos toneladas' donde el guion dice 'seiscientas'. Probablemente es la transcripción (la misma que cambió las cifras por dígitos), pero si la voz lo dice así un hispanohablante lo nota como error de concordancia. Material insuficiente para verificar: no puedo escuchar el audio. — 11.06 s. **Arreglo:** Escuchar 11.0–11.7 s antes de tocar nada (0 créditos). Sólo si dice 'seiscientos': regenerar con 'seis-cientas' en el texto para ElevenLabs y pantalla.txt con 'seiscientas' (~1.200 créditos; quedan 37.899). Hacerlo antes de alargar pausas, porque al regenerar se pierden.
2. 'años...' deja sólo 0,19 s de silencio y aparecen otros 0,26 s después de 'por' (alineado en 0,45 s, largo para una sílaba): el silencio del remate final del loop puede caer en 'por… fin' en vez de 'años… por fin'. — 60.95 s. **Arreglo:** Con tools/pausas.py (0 créditos) subir a ~0,5 s el silencio después de 'años...' (60.95). Escuchar 60.9–61.6 s: si el hueco después de 'por' se oye partido, recortarlo.
3. 'conciertos...' deja sólo 0,17 s de silencio antes de 'para que pasara una autopista': el remate de 'ya tenía práctica' entra sin pausa. — 56.23 s. **Arreglo:** Con tools/pausas.py subir el silencio después de 'conciertos...' (56.23) a ~0,45 s.
4. 'Uno aguanta el peso.' y 'El otro se alza y da un paso.' van pegadas (0,00 s de silencio), justo cuando se explica el mecanismo. El aviso de 4,8 palabras/s en esa frase viene de que son palabras cortas: con las sinalefas ('se alza y da un') se dicen ~8 sílabas en 1,6 s (~5 síl/s, la velocidad medida de Fernando), así que no está apurada. Lo que falta es el respiro entre las dos frases. — 30.36 s. **Arreglo:** Con tools/pausas.py agregar ~0,2 s después de 'peso.' (30.36).
5. 'Caminó sesenta y dos metros.' y 'Se demoró dieciocho días.' van sin silencio (0,00 s): las dos cifras quedan seguidas sin respiro. — 46.18 s. **Arreglo:** Con tools/pausas.py agregar ~0,15–0,2 s después de 'metros.' (46.18). Con las cuatro pausas (~1,0 s en total) la voz queda en ~64,3 s con la cola, dentro de 62–65 s. Todo esto se hace antes del storyboard, porque corre los tiempos.

## Avisos automáticos

- ritmo de 4.8 palabras/s en 'El otro se alza y da un paso.' · 30.36 s
- se escucha 'seiscientos' donde el guion dice 'seiscientas'
- se escucha '2020' donde el guion dice 'dos mil veinte'
- se escucha 'shangai' donde el guion dice 'shanghai'
- se escucha '2003' donde el guion dice 'dos mil tres'
