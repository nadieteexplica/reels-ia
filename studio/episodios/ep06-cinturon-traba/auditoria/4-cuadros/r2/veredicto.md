# 4-cuadros · ronda 2 · **NO APROBADO** · estilo realista

Promedio **7.0** (mínimo 8; ningún revisor bajo 7 en ningún criterio; realismo: ningún revisor bajo 8).

**2 rondas sin llegar a realismo 8: no se abre otra y el video NO sigue.** No se reemplaza por plantillas del kit (son animadas). Se para y se le pregunta a Tomás con opciones (otra vía para lo que se ve de juguete, por ejemplo Kling o sacar a la persona de cuadro; aceptar el nivel actual; o cambiar el episodio a animado).

| criterio | nota (promedio) | más baja | por qué (la más baja) |
|---|---|---|---|
| belleza | 7.0 | 7 | B tiene sol bajo de costado, negros reales y un auto con polvo creíble; A tiene luz cálida y f/2 pero la cinta es una franja rosada plana y arriba hay piezas que no se reconocen; C tiene profundidad de campo pero bordes de CG perfectos, disco gris liso y óxido en nubes parejas |
| personaje | 7.0 | 7 | en A el caballero coincide con la ficha (sobreveste con escudo verde y león amarillo, mangas a cuadros, hombrera beige), pero por la visera se ve la cara con dos ojos celestes brillantes (x 175 y 395, y 645), y en la ficha la visera es oscura |
| manos | 7.0 | 7 | A: la mano ya no tiene facetas (suavizada y blanda por el f/2, x 700-1080, y 1080-1490), pero es una manopla pálida sin dedos legibles que roza el borde del volante: Kling puede inventar el agarre |
| anatomia | — | — | no aplica |
| realismo | 7.0 | **7** | B queda cerca del 8: auto real, aunque la ladera es de bultos redondeados de greda y los bloques nuevos tienen bordes y esquinas perfectas. A lo baja la franja rosada sin luz ni tejido, la misma textura de esponja en techo, bloques y volante, y las piezas de arriba que no se reconocen. C lo baja la cinta, un tablón grueso y liso, el disco gris de un tono y el pedestal con ruido moteado parejo |

## Bloqueantes y fallas automáticas (impiden aprobar)

1. 🛑 [B9] [A2 sin arreglar] A_caballero_se_lanza: la 'capa roja' que es la cinta trabada se ve como un polígono rosado plano, sin sombra ni textura y con bordes dentados, pegado al borde izquierdo (x 0-150, y 675-1110); se lee como error de render y lo clave del episodio, la cinta trabada, no se entiende y queda cortado por el borde. **Arreglo:** arreglar el material (normales, cara trasera o emisión) y modelarla como cinta de cinturón real: tejido plano de ~48 mm, del hombro izquierdo a la cadera, entera dentro del cuadro (correr la cámara a la derecha o abrir el lente)

## Sugerencias (las 5 más importantes; el resto queda en veredicto.json)

1. [A3 sin arreglar] A no se lee como 'auto visto por el parabrisas': no se ve el vidrio, los bloques beige de arriba a la derecha (x 750-1080, y 270-540) parecen vigas de madera, por la ventana de atrás se ve una rejilla de madera y la cúpula oscura de arriba no se entiende. **Arreglo:** vidrio con reflejo del cielo, polvo y una marca de plumilla; tablero, volante y pilar B reconocibles; sacar la rejilla y los bloques o cambiarlos por la visera y la luneta con el cerro detrás
2. [A4 sin arreglar] la cinta cambia de objeto entre cuadros: en A es una mancha rosada plana y en C un tablón café grueso y liso (el canto mide 1/3 del ancho; una cinta real tiene ~1 mm de espesor), sin tejido en ninguno. **Arreglo:** un solo material de cinta para todo el video (mismo color, tejido de nylon visible, espesor de cinta) y usarlo en A y C
3. [A5 sin arreglar] C_retractor_por_dentro: la cadena de la explicación no se ve. La palanca (x 130-390, y ~1115) flota sin pivote, no toca la bolita ni llega al trinquete de la izquierda, que además tiene dientes simétricos de engranaje y no de trinquete. **Arreglo:** apoyar la palanca sobre la bolita con un pivote visible y su punta bajo un diente del trinquete; dientes de sierra en el trinquete. Así bolita → palanca → trinquete se lee de un vistazo cuando la voz lo nombre
4. [A6 sin arreglar] B_subida_cerro: el 40% de arriba es cielo vacío (y 0-750), el auto queda abajo con la cola cortada por el borde izquierdo y nada horizontal permite saber que sube 30° (se lee igual como cámara chueca); por las ventanas los asientos se ven vacíos, sin conductor. **Arreglo:** subir el auto al centro (y 500-1300) bajando la cámara; meter una referencia horizontal (el plano del valle o un horizonte lejano) o una píldora '30°' como capa; si el caballero maneja en este plano, que se vea su silueta por el vidrio
5. [A7 sin arreglar] A: grano de render en las zonas oscuras (detrás del yelmo y en el brazo, x 570-840, y 600-840) y la misma textura moteada de esponja en techo, bloques y volante. **Arreglo:** más muestras o denoiser; materiales distintos por pieza: tela en el techo, cuero en el volante, plástico granulado en el tablero

## Verificación de la ronda anterior

| id | qué | arreglado |
|---|---|---|
| A1 | A_caballero_se_lanza: la mano derecha del caballero es low-poly a la vista (caras planas y | sí |
| A2 | A_caballero_se_lanza: la 'capa roja' que es la cinta trabada se ve como un polígono rosado | **no** |
| A3 | A no se lee como 'auto visto por el parabrisas': no se ve el vidrio, los bloques beige de  | **no** |
| A4 | la cinta cambia de objeto entre cuadros: en A es una mancha rosada plana y en C un tablón  | **no** |
| A5 | C_retractor_por_dentro: la cadena de la explicación no se ve. La palanca (x 130-390, y ~11 | **no** |
| A6 | B_subida_cerro: el 40% de arriba es cielo vacío (y 0-750), el auto queda abajo con la cola | **no** |
| A7 | A: grano de render en las zonas oscuras (detrás del yelmo y en el brazo, x 570-840, y 600- | **no** |
| D1 | [delator · medio] mano low-poly facetada, color salmón y lisa como muñeco, en primer plano | sí |
| D2 | [delator · medio] polígono rosado sin sombra ni textura en el borde izquierdo (la cinta o  | **no** |
| D3 | [delator · arriba] ojo celeste brillante por la visera, como de caricatura (en la ficha la | **no** |
| D4 | [delator · arriba] parabrisas invisible: sin reflejo, sin polvo ni marcas, sin borde de go | **no** |
| D5 | [delator · arriba] bloques beige arriba a la derecha que parecen vigas de madera y cúpula  | **no** |
| D6 | [delator · arriba] rejilla de madera desenfocada por la ventana de atrás: no se entiende q | **no** |
| D7 | [delator · medio] la misma textura moteada de esponja repetida en techo, bloques y volante | **no** |
| D8 | [delator · medio] grano o ruido de render en las sombras detrás del yelmo y en el brazo | sí |
| D9 | [delator · abajo] capó liso de un solo tono, sin polvo, sin línea de panel y sin reflejo,  | **no** |
| D10 | [delator · medio] escala: la mano del asset es casi del ancho del yelmo (proporción de muñ | **no** |
| D11 | [delator · medio] cerro de bultos redondeados como greda, sin ondas de viento ni cresta de | **no** |
| D12 | [delator · medio] piedras en forma de huevo repetidas (mismo modelo escalado) en la ladera | sí |
| D13 | [delator · medio] las piedras apoyadas encima de la arena, sin hundirse ni juntar arena al | **no** |
| D14 | [delator · abajo] suelo bajo el auto liso y de un solo café, sin huellas de neumático, sin | sí |
| D15 | [delator · medio] tabla de surf azul con brillo de escarcha (puntitos), como plástico de j | **no** |
| D16 | [delator · abajo] el barro de los tapabarros es la misma textura de arena pareja y del mis | **no** |
| D17 | [delator · arriba] sin referencia horizontal: la pendiente de 30° no se distingue de una c | **no** |
| D18 | [delator · medio] cinta como tablón café: el canto mide 1/3 del ancho y es lisa, sin tejid | **no** |
| D19 | [delator · medio] engranaje plateado y anillo de bronce con bordes y esquinas perfectas, s | **no** |
| D20 | [delator · medio] disco gris liso de un solo tono, sin textura | **no** |
| D21 | [delator · medio] las manchas del bronce son nubes de ruido parejas en toda la placa, no d | **no** |
| D22 | [delator · medio] la palanca sobre la bolita flota sin pivote ni unión a nada | sí |
| D23 | [delator · abajo] perno hexagonal suelto en la ranura entre las dos placas, sin que se vea | **no** |
| D24 | [delator · abajo] la placa derecha no se ve unida a la izquierda (parece una puerta abiert | **no** |
| D25 | [delator · abajo] copa del sensor de la bolita negra lisa, sin textura | sí |
| D26 | [delator · medio] todo el mecanismo igual de nítido de adelante atrás: un macro de 100 mm  | sí |
| D27 | [delator · abajo] el mecanismo flota en el aire del desierto, sin base, y el tercio de aba | sí |

## Avisos automáticos

- estilo.json: la referencia 'referencias/*.jpg' no encontró archivos en la carpeta del episodio · estilo.json
- estilo realista sin referencias (fotos reales en estilo.json → referencias): el revisor juzga el realismo sin poder comparar
