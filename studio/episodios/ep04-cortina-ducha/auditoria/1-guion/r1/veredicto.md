# 1-guion · ronda 1 · **APROBADO**

Promedio **8.0** (mínimo 8; ningún revisor bajo 7 en ningún criterio).

| criterio | nota (promedio) | más baja | por qué (la más baja) |
|---|---|---|---|
| precision | 8.0 | 8 | Las 9 afirmaciones calzan con los extractos: agua fría (Popular Science, Mental Floss, Straight Dope; ScienceABC: 'warm shower or cold shower'), caliente más fuerte (Eastwell en Popular Science; Straight Dope 'not quite as vigorously'), remolino horizontal con centro de baja presión (Popular Science, Mental Floss, Straight Dope) y cortina más pesada (ScienceABC 'consider switching to heavier curtains'; Popular Science 'sufficiently flimsy curtain'). Hay más de 2 fuentes independientes para el dato central y ninguna cifra. Baja de 9 porque el remolino sale de una sola simulación que nunca se midió en una ducha real (Popular Science) y ScienceABC dice 'no single explanation is settled', pero el guion lo cuenta como hecho, sin 'los físicos creen'. |
| gancho | 8.0 | 8 | 'Te estás duchando... y la cortina se te viene encima. ¿Un fantasma?' es una situación que casi todos vivieron y suma un chiste en 2 s; el giro 'tampoco es solo el aire caliente... pasa hasta con agua fría' desarma la explicación que la mayoría tiene. No llega a 9 porque la pausa después de 'duchando' atrasa la imagen fuerte (la cortina) al segundo 1,5 aprox. |
| claridad | 8.0 | 8 | Sigue la estructura del manual (gancho, giro, mecanismo en 3 pasos: arrastra, remolino, centro con baja presión y el aire de afuera empuja, enseñanza y cierre en loop) con imágenes que un niño de 12 entiende ('remolino acostado', 'como una rueda'). Tiene media frase que se puede sacar ('Con agua caliente pasa más fuerte, pero') y 'presión' no se explica en la misma frase, aunque la siguiente ('empuja más') la aclara. |
| compartible | 8.0 | 8 | Tiene destinatario claro: se lo mandan al que dice que 'en su casa penan' o a quien se ducha con cortina. Se guarda por la solución (cortina más pesada) y el remate 'ahí sí es un fantasma' es para reenviar. No llega a 9 porque la enseñanza es chica y no todos tienen cortina (muchos tienen mampara). |

## Bloqueantes y fallas automáticas (impiden aprobar)

Ninguno.

## Sugerencias (las 5 más importantes; el resto queda en veredicto.json)

1. El mecanismo del remolino se presenta como hecho comprobado. Viene de una sola simulación por computador (Schmidt 2001) que no se probó en una ducha real (Popular Science), y ScienceABC dice que 'no single explanation is settled'. El manual §1 pide decirlo ('los científicos creen…'). — Mira la ducha por dentro. El chorro arrastra el aire hacia abajo... y arma un remolino acostado s. **Arreglo:** Cambiar 'Mira la ducha por dentro.' por 'Los físicos creen que pasa esto.' (sirve igual para entrar al corte de la ducha, +1 palabra) o anteponer 'Según los físicos,' a 'el chorro arrastra…'. No hace falta nombrar el estudio.
2. 'Con agua caliente pasa más fuerte, pero' se puede sacar sin perder la idea ni el matiz obligatorio: 'tampoco es SOLO el aire caliente' ya dice que el calor ayuda. Son 6 palabras (~2 s) que frenan el giro justo cuando más se necesita ritmo. — Con agua caliente pasa más fuerte, pero pasa hasta con agua fría. s. **Arreglo:** Dejar 'No. Y tampoco es solo el aire caliente. Pasa hasta con agua fría.' (91 palabras, ~31 s). El matiz del agua caliente se puede contar en la descripción.
3. 'Presión' es la única palabra técnica y no se explica cuando se dice. La frase siguiente habla de 'empuja más', así que el espectador tiene que conectar dos palabras distintas para la misma idea. — En el centro del remolino, la presión baja. s. **Arreglo:** 'En el centro del remolino, el aire empuja menos.' Así calza con 'el aire de afuera, que empuja más' y no hace falta saber qué es presión. Si se quiere mantener la palabra, poner la etiqueta 'BAJA PRESIÓN' en pantalla en el centro del remolino.
4. La pausa después de 'duchando' deja la palabra fuerte ('cortina se te viene encima') después del primer segundo, que es cuando YouTube decide entre visto y deslizado. — Te estás duchando... y la cortina se te viene encima. s. **Arreglo:** Acortar la pausa con tools/pausas.py (0 créditos) o asegurar que el cuadro 0 ya muestre la cortina inflándose con la cara de fantasma, como dice el tono del guion.
5. Son 17 palabras en una sola oración. La pausa la divide en 7 y 10 al oído, pero en la tabla queda sobre el tope de 14 del manual. — El chorro arrastra el aire hacia abajo... y arma un remolino acostado, que gira como una rueda. s. **Arreglo:** Si se agrega 'Según los físicos,' (sugerencia 1), poner punto en la pausa: '...hacia abajo. Y arma un remolino acostado, que gira como una rueda.'

## Avisos automáticos

- palabra de la lista negra (revisar tema): 'arma'
