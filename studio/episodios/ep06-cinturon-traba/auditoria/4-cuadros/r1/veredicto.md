# 4-cuadros · ronda 1 · **NO APROBADO** · estilo realista

Promedio **5.75** (mínimo 8; ningún revisor bajo 7 en ningún criterio; realismo: ningún revisor bajo 8).

| criterio | nota (promedio) | más baja | por qué (la más baja) |
|---|---|---|---|
| belleza | 6.0 | **6** | B tiene luz baja de costado, auto sucio con barro y sombras reales (8) y C buen desenfoque de fondo con placas de bronce manchadas (7), pero A, el plano 1, es un interior ilegible y barroso: vigas beige, rejilla de madera, grano en las zonas oscuras, una mancha rosada plana y un capó liso que ocupa el tercio de abajo |
| personaje | 7.0 | 7 | en A el caballero calza con la ficha (yelmo con visera en T, sobreveste rojo con escudo, hombreras, manga escocesa), pero la mano es rosada y facetada (en la ficha es beige), por la visera brilla un ojo celeste que en la ficha no se ve y el borde del techo tapa la parte de arriba del yelmo |
| manos | 4.0 | **4** | A: la mano derecha del caballero, lo más cerca de la cámara (x 675-1080, y 930-1335 en 1080x1920), es un puño low-poly facetado de color salmón, sin dedos legibles y sin que se entienda qué agarra; B y C no muestran manos |
| anatomia | — | — | no aplica |
| realismo | 6.0 | **6** | B llega a 7-8 (auto con tierra, barro en los tapabarros y neumáticos con taco reales, pero un cerro de greda con piedras-huevo repetidas y sin huellas) y C a 7 (bronce con manchas y placa cepillada, pero engranajes de bordes perfectos y la cinta como un tablón liso), pero A, que define el look del video, es videojuego viejo: mano low-poly, polígono rosado sin sombra, la misma textura de esponja en techo, visera y volante, y un auto que no se reconoce. Sin ref_*.jpg para comparar (aviso de checks.json) |

## Bloqueantes y fallas automáticas (impiden aprobar)

1. 🛑 [B9] A_caballero_se_lanza: la mano derecha del caballero es low-poly a la vista (caras planas y aristas duras en los nudillos), un puño deforme color salmón en primer plano (x 675-1080, y 930-1335); como cuadro de partida, Kling va a copiar ese bloque durante todo el clip. **Arreglo:** Subdivision Surface + Shade Smooth en la mano y color de piel igual al beige de la ficha; o bajar/mover la cámara para que la mano quede libre detrás del volante o apoyada en él, no a medio agarre ni en primer plano
2. 🛑 [B9] A_caballero_se_lanza: la 'capa roja' que es la cinta trabada se ve como un polígono rosado plano, sin sombra ni textura y con bordes dentados, pegado al borde izquierdo (x 0-150, y 675-1110); se lee como error de render y lo clave del episodio, la cinta trabada, no se entiende y queda cortado por el borde. **Arreglo:** arreglar el material (normales, cara trasera o emisión) y modelarla como cinta de cinturón real: tejido plano de ~48 mm, del hombro izquierdo a la cadera, entera dentro del cuadro (correr la cámara a la derecha o abrir el lente)

## Sugerencias (las 5 más importantes; el resto queda en veredicto.json)

1. A no se lee como 'auto visto por el parabrisas': no se ve el vidrio, los bloques beige de arriba a la derecha (x 750-1080, y 270-540) parecen vigas de madera, por la ventana de atrás se ve una rejilla de madera y la cúpula oscura de arriba no se entiende. **Arreglo:** vidrio con reflejo del cielo, polvo y una marca de plumilla; tablero, volante y pilar B reconocibles; sacar la rejilla y los bloques o cambiarlos por la visera y la luneta con el cerro detrás
2. la cinta cambia de objeto entre cuadros: en A es una mancha rosada plana y en C un tablón café grueso y liso (el canto mide 1/3 del ancho; una cinta real tiene ~1 mm de espesor), sin tejido en ninguno. **Arreglo:** un solo material de cinta para todo el video (mismo color, tejido de nylon visible, espesor de cinta) y usarlo en A y C
3. C_retractor_por_dentro: la cadena de la explicación no se ve. La palanca (x 130-390, y ~1115) flota sin pivote, no toca la bolita ni llega al trinquete de la izquierda, que además tiene dientes simétricos de engranaje y no de trinquete. **Arreglo:** apoyar la palanca sobre la bolita con un pivote visible y su punta bajo un diente del trinquete; dientes de sierra en el trinquete. Así bolita → palanca → trinquete se lee de un vistazo cuando la voz lo nombre
4. B_subida_cerro: el 40% de arriba es cielo vacío (y 0-750), el auto queda abajo con la cola cortada por el borde izquierdo y nada horizontal permite saber que sube 30° (se lee igual como cámara chueca); por las ventanas los asientos se ven vacíos, sin conductor. **Arreglo:** subir el auto al centro (y 500-1300) bajando la cámara; meter una referencia horizontal (el plano del valle o un horizonte lejano) o una píldora '30°' como capa; si el caballero maneja en este plano, que se vea su silueta por el vidrio
5. A: grano de render en las zonas oscuras (detrás del yelmo y en el brazo, x 570-840, y 600-840) y la misma textura moteada de esponja en techo, bloques y volante. **Arreglo:** más muestras o denoiser; materiales distintos por pieza: tela en el techo, cuero en el volante, plástico granulado en el tablero

## Delatores del realismo (lista completa: se arreglan TODOS antes de la ronda siguiente)

- **A** · medio: mano low-poly facetada, color salmón y lisa como muñeco, en primer plano → suavizar (subdivisión), piel beige de la ficha con algo de poros o un guantelete, y sacarla del primer plano
- **A** · medio: polígono rosado sin sombra ni textura en el borde izquierdo (la cinta o la capa) → material con luz y tejido; cinta entera en el cuadro
- **A** · arriba: ojo celeste brillante por la visera, como de caricatura (en la ficha la visera se ve oscura) → oscurecer el interior de la visera, sin brillo en el ojo
- **A** · arriba: parabrisas invisible: sin reflejo, sin polvo ni marcas, sin borde de goma → vidrio con un reflejo suave del cielo, polvo y una marca de plumilla
- **A** · arriba: bloques beige arriba a la derecha que parecen vigas de madera y cúpula oscura arriba al centro: piezas que no se reconocen como partes del auto → visera parasol y espejo retrovisor con su forma real, o sacarlos del cuadro
- **A** · arriba: rejilla de madera desenfocada por la ventana de atrás: no se entiende qué es ni calza con un cerro → luneta con el cerro o el cielo detrás
- **A** · medio: la misma textura moteada de esponja repetida en techo, bloques y volante → un material por pieza (tela, cuero, plástico granulado)
- **A** · medio: grano o ruido de render en las sombras detrás del yelmo y en el brazo → más muestras o denoiser
- **A** · abajo: capó liso de un solo tono, sin polvo, sin línea de panel y sin reflejo, en todo el tercio de abajo → polvo y tierra como en B, reflejo del cielo y la línea del borde del capó
- **A** · medio: escala: la mano del asset es casi del ancho del yelmo (proporción de muñeco de la ficha) y se exagera en primer plano → alejar la mano de la cámara o achicarla un poco hacia proporción real
- **B** · medio: cerro de bultos redondeados como greda, sin ondas de viento ni cresta de duna → ondas de viento y cresta marcada, o roca con estratos y grietas
- **B** · medio: piedras en forma de huevo repetidas (mismo modelo escalado) en la ladera y abajo a la derecha → 3-4 modelos distintos, rotados y con tamaños variados
- **B** · medio: las piedras apoyadas encima de la arena, sin hundirse ni juntar arena alrededor → hundirlas un 20-30% y poner un borde de arena acumulada
- **B** · abajo: suelo bajo el auto liso y de un solo café, sin huellas de neumático, sin ondas y sin arena levantada → huellas detrás del auto, ondulación y arena saltando de la rueda trasera
- **B** · medio: tabla de surf azul con brillo de escarcha (puntitos), como plástico de juguete → laca lisa con reflejo deformado, algo de tierra y una marca de cera
- **B** · abajo: el barro de los tapabarros es la misma textura de arena pareja y del mismo espesor en todas partes → más barro abajo y en los bordes, salpicado, y menos arriba
- **B** · arriba: sin referencia horizontal: la pendiente de 30° no se distingue de una cámara inclinada → horizonte o valle lejano con bruma visible en una esquina
- **C** · medio: cinta como tablón café: el canto mide 1/3 del ancho y es lisa, sin tejido → cinta de ~1 mm de espesor con tejido de nylon y el mismo color que en A
- **C** · medio: engranaje plateado y anillo de bronce con bordes y esquinas perfectas, sin chaflán ni desgaste → biselado chico, marcas de mecanizado y algo de grasa oscura en los dientes
- **C** · medio: disco gris liso de un solo tono, sin textura → acero con marcas circulares de torno y reflejo deformado
- **C** · medio: las manchas del bronce son nubes de ruido parejas en toda la placa, no desgaste en bordes y agujeros → concentrar el óxido y la mugre en bordes, junto a los pernos y bajo los engranajes
- **C** · medio: la palanca sobre la bolita flota sin pivote ni unión a nada → pivote visible en la placa y la palanca apoyada en la bolita
- **C** · abajo: perno hexagonal suelto en la ranura entre las dos placas, sin que se vea qué sujeta → que atraviese una de las placas con su tuerca o sacarlo
- **C** · abajo: la placa derecha no se ve unida a la izquierda (parece una puerta abierta) → doblez en U visible o un remache que las una
- **C** · abajo: copa del sensor de la bolita negra lisa, sin textura → plástico negro con granulado y un brillo de borde
- **C** · medio: todo el mecanismo igual de nítido de adelante atrás: un macro de 100 mm a esta distancia desenfocaría la placa de atrás → foco en el trinquete y la placa de atrás algo blanda (abrir el diafragma)
- **C** · abajo: el mecanismo flota en el aire del desierto, sin base, y el tercio de abajo es café liso → montarlo en el pilar B cortado del auto (con el plástico del pilar abierto alrededor) para que tenga dónde apoyarse

## Avisos automáticos

- estilo.json: la referencia 'referencias/*.jpg' no encontró archivos en la carpeta del episodio · estilo.json
- estilo realista sin referencias (fotos reales en estilo.json → referencias): el revisor juzga el realismo sin poder comparar
