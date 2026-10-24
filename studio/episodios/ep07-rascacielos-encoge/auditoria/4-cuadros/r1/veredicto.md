# 4-cuadros · ronda 1 · **NO APROBADO** · estilo realista

Promedio **7.0** (mínimo 8; ningún revisor bajo 7 en ningún criterio; realismo: ningún revisor bajo 8).

| criterio | nota (promedio) | más baja | por qué (la más baja) |
|---|---|---|---|
| belleza | 6.0 | **6** | A (sol bajo de costado, bruma cálida, negros reales p5=9) y D (sol rasante en los pisos altos, calle en sombra) se ven bien; B es azul oscuro con negros p5=0 y un piso que parece agua, y C es un interior oscuro de cajas primitivas que no se lee |
| personaje | 8.0 | 8 | Pete calza con la ficha en B y D (casco blanco, barba, chaleco naranja con cintas amarillas, camisa oscura, pantalón sucio, botas café) y en B la cara queda en y≈615–780 de 1920 con aire; delata la barba de B, que es un bloque negro plano con borde dentado de recorte |
| manos | 8.0 | 8 | B: las dos manos libres, palmas arriba, cinco dedos cada una y sin objeto (sirve para Kling), aunque quedan oscuras; D: mano apoyada en la cadera, dedos sobre el pantalón, sin atravesar |
| anatomia | — | — | no aplica |
| realismo | 6.0 | **6** | La luz es real (sol bajo, bruma en A, negros), pero la ciudad es de videojuego: torres-caja con la misma textura de grilla de ventanas y ventanas blancas al azar (A y D), techos lisos con cubos de ruido y ventanas negras planas (A abajo), avenida vacía de asfalto liso (D) y en C una grúa hecha con dos cajas y un disco; juzgado sin fotos de referencia (checks: estilo.json sin referencias) |

## Bloqueantes y fallas automáticas (impiden aprobar)

1. 🛑 [B12] Sin sonido no se entiende qué es: un interior oscuro con una caja amarilla y una celeste sobre una rueda negra puestas en una viga blanca (la 'grúa', x≈310–705, y≈690–885 en 1920), un cilindro amarillo chico (el 'gato', y≈980–1110), cajitas cafés y paneles en zigzag arriba y abajo cruzados por dos barras naranjas brillantes. No se lee que es el sombrero de una torre por dentro ni que alguien desarma un piso (la voz dice 'DESARMAN EL PISO' y no hay nadie ni nada desarmándose) — plano 6. **Arreglo:** Rehacer el cuadro como corte legible: cámara más atrás que muestre el borde de la torre y el sombrero con el frente abierto (el exterior de la torre visible a un lado para dar contexto); grúa de verdad reconocible (pluma con cable y gancho levantando una losa), gatos hidráulicos como columnas de pistón bajo el techo, 1–2 obreros con casco y chaleco, la losa a medio cortar; iluminar el interior con focos de faena; si las barras naranjas son la línea de corte, que sea una sola, con píldora que lo diga

## Sugerencias (las 5 más importantes; el resto queda en veredicto.json)

1. La ciudad delata la maqueta: todas las torres usan la misma grilla de ventanas con ventanas blancas al azar (look de videojuego), los techos del primer plano de A son planos lisos con cubos de ruido gris y ventanas negras planas, y la avenida de D es asfalto liso sin un solo objeto (sin autos, postes, semáforos, soleras ni tapas) — plano 1. **Arreglo:** En fachadas: vidrio con reflejo del cielo y del sol, montantes con relieve, chorreados bajo los antepechos y menos ventanas encendidas (de día casi ninguna). En techos de A: membrana o gravilla con juntas, manchas, equipos de clima y estanques de agua en vez de cubos. En D: asfalto con parches, grietas y desgaste en las líneas, 2–3 autos estacionados, postes de luz y semáforo a los lados (assets CC0)
2. El techo donde está Pete (y > 1185 en 1920) es azul oscuro con un ruido ondulado horizontal: se lee como agua, Pete parece parado en un lago. Además Pete y su mitad baja están casi negros (negros_p5 = 0) — plano 3. **Arreglo:** Al pasarlo a la parte con sol (ya anunciado), cambiar también el material del piso a membrana asfáltica gris clara o gravilla con juntas, una canaleta o un desagüe; verificar en el recorte abajo que se lea como techo
3. El gancho depende del fantasma de altura y en el cuadro 0 es una caja de alambre bajita (≈5 pisos, y≈360–495 en 1920) de línea delgada: no se lee de inmediato que la torre era más alta y se está encogiendo. La píldora 'QUEDAN 34 PISOS' toca la esquina de atrás del alambre — plano 1. **Arreglo:** Que el fantasma muestre toda la altura que la torre tenía, como volumen translúcido (relleno blanco al 15–20 %) con una flecha hacia abajo sobre el sombrero; subir o correr la píldora para que no toque el alambre; contar que los pisos visibles bajo el sombrero coincidan con '34' (en el cuadro se cuentan ≈29–30 bandas)
4. Las botas de Pete (y≈1388–1418 en 1920) no tienen sombra de contacto ni oclusión: el asfalto bajo ellas mide igual que el de al lado (17 vs 17–18), y con el talón izquierdo levantado se lee como si flotara — plano 11. **Arreglo:** Activar oclusión ambiental o poner un plano de sombra suave bajo los pies; verificar que la suela toque el asfalto
5. La barba de Pete es una masa negra plana con borde dentado de recorte y la píldora 'SIN EXPLOSIONES' queda pegada al casco (borde de la píldora y≈562, casco y≈570) — plano 3. **Arreglo:** Con el sol de costado la barba gana volumen; si sigue plana, aclararla a café oscuro y suavizar el borde; subir la píldora 40–60 px para dejar aire sobre el casco

## Delatores del realismo (lista completa: se arreglan TODOS antes de la ronda siguiente)

- **A** · medio: todas las torres del fondo son cajas con la misma textura de grilla de ventanas y ventanas blancas encendidas al azar (look de videojuego) → variar fachadas (2–3 tipos), vidrio con reflejo del cielo, menos ventanas encendidas de día
- **A** · medio: aristas y esquinas perfectas en todas las torres, sin cornisas, antenas ni equipos en los techos → bisel en esquinas, remates, antenas y equipos en los techos de las torres del fondo
- **A** · abajo: techos del primer plano lisos de un solo color, sin juntas, manchas, desagües ni parapetos → membrana o gravilla con juntas, chorreados y un parapeto con remate
- **A** · abajo: los equipos del techo son cubos con un ruido gris de escala gigante (textura tipo granito estirada) → reemplazar por equipos de clima, ductos o estanques (assets CC0) con textura a escala real
- **A** · abajo: ventanas de los edificios del primer plano son huecos negros planos sin reflejo ni interior → vidrio con reflejo del cielo y algo de interior o cortinas
- **A** · arriba: rectángulo de sombra oscuro en la cara del sombrero sin objeto que lo proyecte → sacar el objeto oculto o quitarle la sombra
- **A** · arriba: sombrero de la torre: banda beige lisa sin juntas ni manchas → paneles con juntas, chorreados y algo de óxido o polvo de faena
- **A** · arriba: cielo en degradé plano, sin nubes ni resplandor del sol bajo → cielo HDRI de atardecer con algunas nubes y halo cálido del lado del sol
- **B** · abajo: piso del techo azul oscuro con ruido ondulado: se lee como agua → membrana asfáltica gris clara o gravilla con juntas y un desagüe
- **B** · arriba: muro gigante detrás de Pete: bloque liso con ruido tipo nube y arista perfecta (ya anunciado que se saca) → confirmar que se sacó; si queda algo, que tenga juntas de moldaje y manchas
- **B** · medio: parapeto de la derecha liso, sin remate ni manchas → remate metálico o de hormigón con chorreados
- **B** · medio: luz plana de sombra sobre Pete, sin dirección; mitad baja casi negra (negros_p5 = 0) → sol bajo de costado sobre Pete (ya anunciado), con rebote del piso claro
- **B** · medio: barba como masa negra plana con borde dentado de recorte → aclarar a café oscuro, suavizar el borde, luz de costado que le dé volumen
- **C** · medio: la 'grúa' son dos cajas (amarilla y celeste) y un disco negro: geometría primitiva de maqueta → modelo real de grúa o polipasto con pluma, cable y gancho
- **C** · medio: texturas amarillas de ruido a escala gigante (efecto camuflaje) en la grúa y el gato → pintura amarilla industrial con desgaste y óxido a escala real
- **C** · medio: la grúa está apoyada en una viga blanca delgada como en un estante; las cajas cafés del piso no tienen sombra de contacto → apoyar la grúa en la losa con su base y dar oclusión a todo lo que toca el piso
- **C** · medio: losa y piso lisos de un solo gris oscuro, sin polvo, escombros ni marcas de corte → hormigón con polvo, escombro chico y la línea de corte visible
- **C** · medio: luz pareja y apagada, sin fuente identificable → focos de faena colgados que den dirección y sombras
- **C** · medio: brillo naranja suelto en el borde derecho (y≈1065 en 1920) que parece un objeto → quitar o explicar la fuente
- **C** · arriba: barras naranjas brillantes cruzando en diagonal arriba y abajo: se leen como neón o láser sin explicación → si es la línea de corte, dejar una sola con píldora; si no, sacarlas
- **C** · abajo: paneles en zigzag beige lisos con aristas perfectas y ventanas negras planas detrás → paneles con juntas y manchas, vidrio con reflejo
- **C** · medio: sin personas ni nada de tamaño conocido: no se lee la escala del interior → poner 1–2 obreros como referencia de escala
- **D** · abajo: asfalto liso de un solo azul oscuro sin parches, grietas ni tapas → textura de asfalto con parches, grietas, manchas de aceite y una tapa de alcantarilla
- **D** · abajo: líneas de pista blancas limpias, sin desgaste → pintura gastada y sucia
- **D** · abajo: botas de Pete sin sombra de contacto ni oclusión → oclusión ambiental o plano de sombra bajo los pies
- **D** · medio: avenida vacía: sin autos, postes, semáforos, árboles ni soleras marcadas → 2–3 autos estacionados, postes de luz y un semáforo a los lados
- **D** · medio: torres laterales con la misma grilla de ventanas y ventanas blancas al azar → variar fachadas y bajar las ventanas encendidas
- **D** · arriba: sombrero de la torre: banda gris casi lisa con borde perfecto → paneles con juntas, chorreados y polvo de faena
- **D** · arriba: cielo en degradé plano sin nubes → HDRI de atardecer con algunas nubes

## Avisos automáticos

- estilo.json: la referencia 'referencias/*.jpg' no encontró archivos en la carpeta del episodio · estilo.json
- estilo realista sin referencias (fotos reales en estilo.json → referencias): el revisor juzga el realismo sin poder comparar
