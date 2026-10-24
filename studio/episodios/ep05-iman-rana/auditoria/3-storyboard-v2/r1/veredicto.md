# 3-storyboard · ronda 1 · **NO APROBADO** · estilo realista

Promedio **7.75** (mínimo 8; ningún revisor bajo 7 en ningún criterio).

| criterio | nota (promedio) | más baja | por qué (la más baja) |
|---|---|---|---|
| foco | 8.0 | 8 | cada frase tiene su imagen y una idea por plano (8: flecha gris contra naranja que la iguala y le gana; 16: cables que se encienden hasta la central); flojos el 5 (células y moléculas a la vez, 'en gran parte' no se ve en la foto) y el 13 (un hombre parado mirando el cielo para '¿y si quisiéramos hacerte flotar a ti?') |
| ritmo | 8.0 | 8 | 19 cortes y ~20 cambios internos en 41,9 s (casi uno por segundo), la escala cambia seguido y no hay transiciones especiales; sólo el 13 (24,47–26,60) y el 19 (39,10–41,90) pasan de 2 s con nada más que cámara, y en el 6 la píldora UN POQUITO cae junto con 'empuja' |
| viabilidad | 7.0 | 7 | 5 escenas con 3 a medida, 0 Kling y nada en las manos: dentro del tope; pero en realista la ficha deja tres riesgos sin resolver: el P frontal de Pete (Mixamo, sin cara animada) en el 10, una rana de 2,8 cm girando en un tubo de ~3 cm (1–4, 8, 19), y vidrio + profundidad de campo + piel mojada en macro (1–4) sin plan de muestras ni GPU |
| gancho_visual | 8.0 | 8 | cuadro 0 real y absurdo con la acción en curso (la rana ya flotando, órbita), símbolo que vuelve en 1–4, 8, 9 y 19 y loop de frase 'sin hilos' → 'Esta rana está flotando'; falta asegurar que en una foto se lea 'en el aire' y no 'atascada' o 'en un tubo con agua', y que el 19 termine exacto en la cámara del 1 |

## Bloqueantes y fallas automáticas (impiden aprobar)

Ninguno.

## Sugerencias (las 5 más importantes; el resto queda en veredicto.json)

1. una rana de 2,8 cm en un tubo de ~3 cm queda a ~1 mm de las paredes: en la foto se ve atascada o sostenida por el vidrio (contradice 'nadie la sostiene'), una rana dentro de un tubo también se lee como 'rana en agua', y al girar sobre sí misma puede atravesar el vidrio (B1 en el animatic). Lo mismo pasa con la fresa del 9 — plano 1 · 0.00 s. **Arreglo:** rana de ~2,2 cm (sigue siendo real y cabe en el hueco), pose compacta con las patas colgando (no de nado), aire visible alrededor y debajo (la boca negra varios mm bajo las patas), tubo seco sin línea de agua, y giro de unos ±10° que nunca acerque la punta a la pared; en el 2, desde arriba, ese anillo de aire es la prueba de 'sin hilos'
2. P de frente de Pete mirando a la cámara: un personaje de Mixamo no trae cara animada (ni parpadeo ni expresión), y en un primer plano frontal es donde más se ve de muñeco o de plástico; además el plano dura 0,69 s (aviso automático). Pete vuelve en M en el 11 y el 17 — plano 10 · 18.62 s. **Arreglo:** reencuadrar el 10 como M de 3/4 a contraluz del sol bajo (silueta con borde de luz, cara en sombra), o unirlo al 11 (Pete junto al refri desde 18,62 y el tilt a los pies en 'flotas'); en 11, 13, 14, 17 y 18 dejar a Pete en M o G con contraluz y profundidad de campo, nunca la cara frontal y nítida
3. E1 es lo más difícil de render en realista (vidrio que refracta, profundidad de campo, sol bajo y piel mojada) y la ficha no dice muestras ni máquina: con las 8–16 muestras del animatic y del final, el vidrio y el bokeh dan ruido y luciérnagas. Además, el push-in del 4 hasta 'la piel mojada con gotitas' pide más detalle del que trae el escaneo de una rana de 2,8 cm: la textura se va a ver estirada — plano 4 · 5.02 s. **Arreglo:** declarar en la ficha que E1 va en GPU (RunPod) con muestras altas y eliminación de ruido, y probarlo en el cuadro de estilo antes de animar; en el 4, terminar el push-in a la escala del ojo y la cabeza (no más cerca de lo que aguanta la textura), con desenfoque de movimiento, gotitas como geometría y micro-relieve procedural en la piel
4. el 19 dura 2,8 s y sólo tiene la órbita, y la ficha dice 'órbita igual a la del 1': si repite el mismo recorrido, termina 35° corrido y el salto al cuadro 0 no empalma. El 13 (24,47–26,60, 2,1 s) tampoco tiene ningún cambio después de SIMULACIÓN, sólo el push-in — plano 19 · 39.10 s. **Arreglo:** 19: una órbita que llega (de −35° a 0°) y termina exacto en la cámara y la pose de la rana del cuadro 0, y la píldora SIN HILOS vuelve en 'sin hilos' (símbolo y cambio gratis). 13: a ~1,3 s ('flotar') Pete baja la mirada a la losa vacía o entra la sombra del primer anillo (es la misma escena E4)
5. en 'La rana es, en gran parte, agua', las células rojas y las moléculas de agua en el mismo cuadro son dos focos a escalas que no conviven (células de micras, moléculas de décimas de nanómetro), y la foto no dice 'en gran parte' — plano 5 · 5.90 s. **Arreglo:** un solo foco: moléculas de agua azules y nítidas llenando la mayor parte del cuadro, con las células como paredes desenfocadas al fondo

## Avisos automáticos

- 19 planos: con algo que cambia cada 1–2 s, en 50 s hacen falta ~25–50 cambios; confirmar que la columna 'cambio' los cubre
- plano 10 dura 0.69 s (muy corto para leerse)
