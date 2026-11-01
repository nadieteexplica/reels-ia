# 4-cuadros · ronda 1 · **NO APROBADO** · estilo realista

Promedio **6.0** (mínimo 8; ningún revisor bajo 7 en ningún criterio; realismo: ningún revisor bajo 8).

| criterio | nota (promedio) | más baja | por qué (la más baja) |
|---|---|---|---|
| belleza | 6.0 | **6** | Lo mejor son 00030 y 01296: el témpano tiene textura y el agua refleja bien. El resto baja la nota: hay texturas estiradas en el cerro de 00116 y en el suelo del corte (00349, 00493, 00693 y 00736, un tercio de cada cuadro), y las aéreas 00929 y 00991 tienen luz plana con neblina gris (p5 en 47) y agua de color plano. |
| personaje | — | — | no aplica |
| manos | — | — | no aplica |
| anatomia | — | — | no aplica |
| realismo | 6.0 | **6** | En la escala, 6 es 'videojuego viejo / maqueta'. Así se ven 00803 (cerros como bultos de greda, glaciar de merengue, lecho de raso), 00929 y 00991 (ríos de color plano con borde recortado, tierra con ruido de camuflaje sin árboles, glaciar que parece tapa de empanada) y 01106 (casas que son cajas con techo de pirámide y un poste que parece farol). Sólo 00030 y 01296 llegan a 7: el témpano y el agua se ven reales, pero el cerro tiene la nieve como mancha estirada, no hay bruma y el cerro chico está facetado. Las capas de corte, flechas y píldoras no bajan la nota. |

## Bloqueantes y fallas automáticas (impiden aprobar)

1. 🛑 [B1] Arriba al centro (x≈400–455, y≈0–12 en 720) flota en el cielo una piedra gris verdosa. En 00030 hay una piedra en el agua que en 01296 ya no está: parece que la animación del nivel del lago la subió al cielo.. **Arreglo:** Fijar la piedra al lecho o borrarla de la escena en cámara rápida. Revisar que nada que esté atado al nivel del agua quede sobre el horizonte en el último cuadro.
2. 🛑 [B11] La línea de la píldora 'EL RÍO × 3' baja en diagonal hasta el borde izquierdo (sale en y≈770 de 1280), sin punta de flecha y sin tocar el río: apunta fuera del cuadro. El río celeste de abajo, que es el que se triplica, queda sin señalar.. **Arreglo:** Que la línea termine dentro del cuadro con su punta sobre el río (el celeste de abajo, o el café si ése es 'el río'), igual que las otras píldoras. Es sólo un cambio del post.

## Sugerencias (las 5 más importantes; el resto queda en veredicto.json)

1. Las aéreas son lo que más delata el videojuego: luz plana con neblina gris (p5 en 47 en 00991), ríos café y celeste de un solo color con bordes duros recortados, tierra con manchas de ruido gris y verde sin árboles (no se lee la escala) y el glaciar como tapa de empanada con borde de serrucho.. **Arreglo:** Poner sol bajo de costado para que el relieve dé sombras. Darle al agua un sombreador con oleaje y espuma (más blanca donde el agua corre rápido), con orillas de barro y grava en vez de un recorte limpio. Repartir bosque de lenga en las laderas y dejar el glaciar más grande, con grietas, en vez del borde dentado repetido.
2. En el corte, el tercio de abajo (el suelo bajo la grava) es una textura estirada en rayas horizontales, como un barrido. Se ve igual en 00349, que no es cámara rápida, así que no es desenfoque de movimiento: es la textura proyectada desde arriba sobre la cara del corte.. **Arreglo:** En la cara del corte, usar proyección de caja (triplanar) o un material de estratos de roca y tierra con piedras. Alternativa más barata: bajar la cámara del corte para que el suelo ocupe menos de un 10 % del cuadro.
3. Los cerros son el fondo de todo el video y delatan la maqueta. La nieve de la cumbre es una mancha blanca lisa con ruido estirado (00030 y 01296 arriba). En 00116, el cerro izquierdo tiene una pared vertical con la textura estirada (el borde de la malla). En 00803 los cerros son bultos lisos de un solo color. Además falta bruma de distancia y el sol está alto (p5 en 45 y 43 en 00030 y 01296).. **Arreglo:** Usar un relieve real (un DEM de Aysén o roca escaneada) con nieve sólo en las quebradas y las cumbres, bruma de distancia en el fondo y sol bajo de costado, que deje caras en sombra de verdad. En 00116, mover la cámara para que no se vea el borde del terreno.
4. Las casas son cajas con techo de pirámide: sin aleros, con ventanas y puertas planas y estuco uniforme (la roja parece de plástico). La 'sirena' es una esfera blanca sobre una caja en un cilindro perfecto, y se lee como farol, no como sirena. La orilla del agua es una recta perfecta de lado a lado, y el agua café cubre un 45 % del cuadro sin detalle.. **Arreglo:** Hacer casas de Patagonia, con techo de zinc acanalado de dos aguas, aleros, tejuela o tabla y marcos de ventana, más una cerca o leña para dar escala. Para la sirena, poner bocinas de alarma (2 a 4 conos) en el poste, con una luz roja que gire. Para la orilla del agua, usar un borde irregular con espuma y bajar la cámara para que el agua ocupe menos del cuadro.
5. Sin sonido no se lee 'el lago se vació': el lecho vacío (40 % de abajo) es una superficie lisa de raso, sin piedras, sin grietas de barro y sin témpanos varados. El túnel es negro puro, con el borde del arco escalonado como serrucho, y la pared del glaciar parece merengue.. **Arreglo:** Dejar 3 a 6 témpanos varados en el lecho (es la imagen típica del lago vacío) y agregar barro agrietado con charcos que reflejen. Para el túnel, alisar el borde del booleano y meter agua corriendo hacia adentro con un poco de luz azul en el fondo.

## Delatores del realismo (lista completa: se arreglan TODOS antes de la ronda siguiente)

- **00030** · arriba: La nieve de la cumbre del cerro grande es una mancha blanca lisa con ruido estirado en diagonal, sin quebradas ni roca asomando → Nieve que siga la forma del relieve (quebradas y crestas), con roca escaneada debajo
- **00030** · arriba: No hay bruma de distancia: el cerro está tan nítido y contrastado como el glaciar, y el cielo es un degradado liso → Bruma volumétrica suave que aclare y azule lo lejano; algo de nube o calima en el horizonte
- **00030** · medio: El cerro chico de la izquierda está facetado (aristas de pocos polígonos) → Subdividir o cambiarlo por relieve real, con bruma
- **00030** · medio: Luz alta y pareja (p5 en 45): el cerro está iluminado casi entero y no hay cara en sombra → Sol bajo de costado que deje una ladera en sombra con negros de verdad
- **00116** · arriba: El cerro izquierdo tiene una pared vertical recta con la textura estirada en vertical (x≈60–90, y≈380–580 en 720): es el borde de la malla del terreno → Mover la cámara para que no se vea, o agregar faldón o cerros detrás
- **00116** · arriba: La ladera derecha tiene la textura estirada en rayas a lo largo de la pendiente → Proyección triplanar en las pendientes fuertes
- **00116** · medio: La superficie del glaciar es un patrón regular de bultos iguales, como plástico de burbujas → Grietas y seracs con variación de tamaño, y morrena oscura en franjas
- **00116** · abajo: El 40 % de abajo es agua azul oscura lisa, sin ondas ni detalle → Oleaje fino, témpanos chicos y el reflejo del glaciar más marcado, o bajar el horizonte
- **00349** · arriba: Las manchas de nieve del cerro son bultos redondeados parecidos entre sí, como camuflaje, y no siguen las quebradas (se repite en 00493, 00693 y 00736) → Máscara de nieve según pendiente y altura (nieve en lo plano y en las canaletas), con bosque abajo
- **00349** · arriba: Una línea oscura horizontal flota sobre la niebla a la derecha (x≈447–720, y≈497 en 720): parece el borde de un plano o de la caja del corte → Esconder ese borde detrás de la niebla, o alinearlo con la línea del corte
- **00349** · abajo: La cara del suelo en el corte tiene la textura estirada en rayas horizontales (un tercio del cuadro) → Material de estratos con proyección de caja, o encuadre con menos suelo
- **00493** · abajo: El mismo suelo del corte con la textura estirada, como barrido → Igual que en 00349
- **00693** · medio: Una línea vertical color crema queda suelta en el agua oscura bajo el hielo (x≈160, y≈800–870 en 720): es un resto del contorno del corte → Borrar esa arista o cerrarla con la cara del hielo
- **00693** · abajo: El mismo suelo del corte con la textura estirada → Igual que en 00349
- **00736** · arriba: Quedan huecos negros puros detrás del borde de arriba de los bloques cortados (x≈0–190, y≈415–445 en 720): se ve el interior vacío de la malla → Tapar la malla del glaciar (cara de corte cerrada) o poner nieve detrás
- **00736** · medio: La misma línea crema vertical suelta en el agua bajo el hielo (x≈270, y≈830–870 en 720) → Borrar esa arista
- **00736** · abajo: El suelo del corte con la textura estirada → Igual que en 00349
- **00803** · arriba: Los cerros son bultos lisos de un solo color (uno gris y otro verde) con ruido uniforme: sin roca, sin quebradas, sin bruma → Relieve real con roca y vegetación, y bruma de distancia
- **00803** · medio: La pared del glaciar parece merengue o papel arrugado con bultos redondos, sin grietas verticales ni azul profundo → Frente de glaciar con seracs, grietas verticales y azul en las sombras (como el frente de 00030)
- **00803** · medio: El borde del arco del túnel está escalonado como serrucho (booleano con aliasing) → Alisar o biselar el corte, o agregar desgaste irregular al borde
- **00803** · medio: El interior del túnel es negro puro y plano → Algo de luz azul que pase por el hielo y agua que corre hacia adentro
- **00803** · medio: La franja de manchas blancas y café en la base del glaciar se lee como patrón de camuflaje → Grava y bloques de hielo caídos, con forma y tamaño variados
- **00803** · abajo: El lecho del lago vacío es una superficie lisa como raso, sin piedras, sin grietas ni témpanos: no da escala → Témpanos varados, barro agrietado, charcos y bloques de roca
- **00929** · arriba: Una línea azul delgada cortada en tramos flota sobre la ladera (x≈390–420, y≈480–560 en 720) → Si es un estero, que sea continuo, con espuma y que llegue al valle; si no, borrarla
- **00929** · arriba: El glaciar se ve como una tapa de empanada chica con borde de serrucho repetido: no da la escala de un campo de hielo → Glaciar más grande que entre por el fondo del valle, con grietas y morrena, sin el borde dentado
- **00929** · medio: La crecida café es de un solo color, con bordes duros recortados contra el verde → Sombreador de agua con turbulencia y espuma, y orillas de barro húmedo
- **00929** · abajo: El río celeste es de color plano, sin oleaje ni reflejo (agua que no refracta) → Oleaje y reflejo del cielo; el celeste del Baker se queda, pero con variación
- **00929** · medio: La tierra es ruido verde con manchas grises, sin árboles ni arbustos: no hay escala y todo está igual de blando → Bosque de lenga y matorral repartidos, con sombra; profundidad de campo marcada
- **00929** · medio: Luz plana con neblina: el relieve no proyecta sombras → Sol bajo de costado
- **00991** · arriba: La misma línea azul suelta cortada en tramos (x≈625, y≈0–105 en 720) → Igual que en 00929
- **00991** · arriba: El glaciar arriba a la derecha parece papel arrugado → Frente de glaciar con seracs y grietas
- **00991** · abajo: La tierra gris y verde moteada se ve como moho o niebla pegada al suelo, sin árboles → Vegetación real repartida y bruma sólo en la distancia
- **00991** · medio: Luz plana y neblina gris en todo el cuadro (p5 en 47): no hay negros → Sol bajo de costado y menos bruma cerca de la cámara
- **00991** · medio: El agua café es plana, con bordes duros recortados → Igual que en 00929
- **01106_crudo** · medio: Las casas son cajas con techo de pirámide, sin aleros ni canaletas, con ventanas y puertas planas y estuco uniforme; la roja parece de plástico → Casas de Patagonia con zinc acanalado, aleros, tejuela o tabla, marcos y desgaste
- **01106_crudo** · medio: El poste es un cilindro perfecto con una caja y una esfera: se lee como farol, no como sirena → Poste de madera o concreto con bocinas de alarma y una baliza roja
- **01106_crudo** · medio: El suelo es un plano verde liso, sin pasto, cercas, caminos ni piedras → Pasto con variación, un camino de ripio y una cerca de palos
- **01106_crudo** · abajo: La orilla del agua es una recta perfecta de lado a lado, y el agua café es lisa en un 45 % del cuadro → Orilla irregular con espuma y escombros flotando, o bajar la cámara
- **01106_crudo** · arriba: El cerro de fondo es una masa oscura sin árboles ni forma → Bosque con silueta contra un cielo de noche un poco más claro
- **01296** · arriba: Una piedra flota en el cielo arriba al centro (ver bloqueante B1) → Borrarla o fijarla al lecho
- **01296** · arriba: Los mismos cerros que en 00030: nieve como mancha estirada, cerro chico facetado, sin bruma → Igual que en 00030
- **01296** · medio: Luz alta y pareja (p5 en 43), sin cara en sombra en el cerro → Sol bajo de costado

## Avisos automáticos

- 00030: pocos negros (percentil 5 en 45.0; los cuadros realistas aprobados quedaron en 5–22): que el revisor diga si la luz se ve plana
- 00991: pocos negros (percentil 5 en 47.0; los cuadros realistas aprobados quedaron en 5–22): que el revisor diga si la luz se ve plana
- 01296: pocos negros (percentil 5 en 43.0; los cuadros realistas aprobados quedaron en 5–22): que el revisor diga si la luz se ve plana
- estilo.json: la referencia 'referencias/*.jpg' no encontró archivos en la carpeta del episodio · estilo.json
- estilo realista sin referencias (fotos reales en estilo.json → referencias): el revisor juzga el realismo sin poder comparar
