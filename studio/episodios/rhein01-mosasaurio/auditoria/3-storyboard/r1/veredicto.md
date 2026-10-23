# 3-storyboard · ronda 1 · **NO APROBADO**

Promedio **7.5** (mínimo 8; ningún revisor bajo 7 en ningún criterio).

| criterio | nota (promedio) | más baja | por qué (la más baja) |
|---|---|---|---|
| foco | 8.0 | 8 | Cada frase tiene su imagen y hay una sola idea por plano (11: carrete en corte con 'engranajes de camión'; 12: pinza roja con 'freno'; 5: la micro al lado del lomo con 'largo de una micro'). Fallan dos cosas: la bisagra de la venta, 29 '¡Hay uno que cabe en tu mochila!', no muestra ninguna mochila, y en el 14 el tirón no tiene causa a la vista (el mosasaurio recién muerde en el 25). |
| ritmo | 8.0 | 8 | 38 planos en 42,27 s (mediana 1,07 s). Ninguno pasa de 2 s salvo el 38 (2,41 s, con la entrada del logo), la escala alterna G/M/D/P y hay una sola transición especial (29). Baja porque 6 planos duran 0,75 s o menos, y tres de ellos son las portadas del producto (33, 35 y 36, de 0,65–0,68 s), que es justo lo que vende el aviso. |
| viabilidad | 6.0 | **6** | Las 4 escenas lo son sólo de nombre. E1 junta ~15 actuaciones distintas (pollos que vuelan en el 3, popa que se hunde en el 8, caída de poto en el 14, salto con salpicadura en el 25, remolque en el 26, lluvia de huesos en el 27 y 7 reacciones), y E2 son seis mecanismos con modelo propio (7, 9, 11, 12, 13, 16). Además hay agua semi-realista (8, 19, 23, 25, 26) y la ficha no deja el plan B de Kling que sí traía el guion. A favor: ninguna mano con objetos y 9 s de metraje real que no se renderizan. |
| gancho_visual | 8.0 | 8 | El cuadro 0 es absurdo y la acción ya está en curso (racimo de 200 pollos sobre el mar y una sombra que cruza), y hay dos símbolos que vuelven (los pollos y el radar verde). Pierde porque la cámara del 1 'baja desde la polea' (el cuadro 0 podría ser la polea), porque el final es un logo sobre negro que no empalma con el cuadro 0 y porque el radar se paga como portada en sólo 0,65 s (35). |

## Bloqueantes y fallas automáticas (impiden aprobar)

Ninguno.

## Sugerencias (las 5 más importantes; el resto queda en veredicto.json)

1. Mucha agua en estilo semi-realista: el salto con salpicadura enorme (25), el remolque con estela y saltos (26), la popa que salta agua (8) y dos planos bajo el agua (19, 23). La ficha lo marca todo como render, sin plan B, y además pide 'pelo al viento' en el 26 aunque el niño lleva gorro. — plano 25 · 26.70 s. **Arreglo:** Decidirlo ya en la ficha. El 25 sale de Kling a partir de un cuadro nuestro: es un solo clip y no aparece el niño, así que el personaje no cambia. Si queda en render, el lomo sale detrás de una cortina de partículas de spray, sin simular fluidos. El 26 va en plano general con modificador de océano y partículas de espuma, y sin pelo: lo que flamea es el impermeable. En el 8, la popa baja y sale spray de partículas. El 19 y el 23 se hacen con niebla volumétrica azul y una textura de cáusticas, sin superficie simulada.
2. E2 son en realidad seis montajes distintos: pernos y torreta (7), cable trenzándose (9), carrete transparente (11), disco con pinza y chispas (12), trinquete (13) y arnés (16). E1 suma acciones de cuerpo entero que ninguna plantilla cubre: tambaleo (8) y caída de poto (14). El ritmo se apoya en armar piezas nuevas, no en cortar dentro de lo que ya está. — plano 7 · 8.10 s. **Arreglo:** Que E2 sea un solo modelo: el carrete en corte. Los planos 11, 12 y 13 pasan a ser tres cámaras sobre ese mismo carrete transparente, que ya trae los engranajes verdes, la pinza roja y el pestillo amarillo, con push-in. El 7 se arma con la base de la grúa de E1 y flechas verdes en el post. El 16 es un detalle del mismo asiento del 15. El 9 es un macro del cable de E1 con un shader de torsión animado. En el 14, el niño se cae fuera del cuadro por abajo y sólo vuelven a entrar sus botas, y una flecha roja que sale del agua tira del cable para que el tirón tenga causa.
3. La cámara 'baja lento desde la polea': el cuadro 0, que es la portada y donde se decide visto o deslizado, puede quedar en la polea y el cable en vez del racimo con la sombra. — plano 1 · 0.00 s. **Arreglo:** Que el plano parta ya encuadrado en el racimo, en el tercio superior, con los pollos dorados grandes y legibles, y con la sombra en la mitad de abajo. El único movimiento es el push-in del 8 %, sin paneo vertical.
4. '¡Hay uno que cabe en tu mochila!' se ve con una explosión de radar y ninguna mochila. Además, el radar verde que 'al final es la portada' recién aparece en el 35 y dura 0,65 s, así que el símbolo nunca se paga. — plano 29 · 30.56 s. **Arreglo:** En el 29, que el brillo verde salga de adentro de una mochila escolar apoyada en la cubierta y que la mochila explote en verde. En el 30, hacer un match-cut desde ese verde a la portada del radar 'Untamed Waters' (mismo verde, el barrido en el mismo lugar) y dejar el collage para después.
5. Hay textos que pueden fallar en el animatic. Para la voz se escribió 'Rain' y 'Ti Rex': si los subtítulos salen de words.json, en pantalla dirán RAIN y TI REX, que sería B10. En el 30, el 32 y el 38 hay texto grande de marca en el cuadro, y el subtítulo quedaría duplicado o encima del producto. En el 2, el contador (y 280–460) comparte la franja con la cara (y 420–700) y la ficha no dice en qué x va cada uno. — plano 32 · 34.37 s. **Arreglo:** En el paso de subtítulos, mapear Rain → RHEIN y Ti Rex → T. REX. En el 30, el 32 y el 38, ocultar los subtítulos (silencio del título). Encuadrar el metraje para que las portadas queden en y 300–950 y confirmar que el video original no trae texto pegado. En el 2, escribir la x en la ficha: el niño a la derecha y el contador sobre la montaña de la izquierda, o subir el contador a y 260–400.

## Avisos automáticos

- plano 2: el gráfico (y 280–460) comparte franja con la cara (y 420–700): ubicarlo con graficos.lugar_libre y confirmarlo con tools/prueba.py
- plano 8 dura 0.66 s (muy corto para leerse)
- plano 17 dura 0.74 s (muy corto para leerse)
- plano 20 dura 0.75 s (muy corto para leerse)
- plano 33 dura 0.68 s (muy corto para leerse)
- plano 35 dura 0.65 s (muy corto para leerse)
- plano 36 dura 0.66 s (muy corto para leerse)
