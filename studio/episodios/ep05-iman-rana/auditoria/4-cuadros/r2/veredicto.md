# 4-cuadros · ronda 2 · **NO APROBADO** · estilo realista

Promedio **8.0** (mínimo 8; ningún revisor bajo 7 en ningún criterio; realismo: ningún revisor bajo 8).

**2 rondas sin llegar a realismo 8: no se abre otra y el video NO sigue.** No se reemplaza por plantillas del kit (son animadas). Se para y se le pregunta a Tomás con opciones (otra vía para lo que se ve de juguete, por ejemplo Kling o sacar a la persona de cuadro; aceptar el nivel actual; o cambiar el episodio a animado).

| criterio | nota (promedio) | más baja | por qué (la más baja) |
|---|---|---|---|
| belleza | 8.0 | 8 | A (9): rana cálida contra el azul con profundidad de campo y vidrio con polvo; C (8): contraste fuerte, negros reales (p5=7), un solo foco; B (7): el sol bajo ya da negros (p5=19) y un lado del imán en sombra, pero la mitad inferior (y 700-1280 a 720) es sólo la pared del tanque y el suelo entre el imán y los cerros (y 595-660) es un plano beige liso. |
| personaje | 9.0 | 9 | Pete en B calza con la ficha (casco blanco, barba, chaleco naranjo con franjas amarillas, mangas oscuras, pantalón embarrado, botas café) y la rana de A es el mismo escaneo de la ficha; cara de Pete en y≈345/1920 con aire de cielo arriba. |
| manos | 8.0 | 8 | Ningún agarre: en B Pete tiene una mano en puño junto a la cadera y la otra suelta (x≈315 y x≈370, y≈355), sin dedos raros; en A los dedos delanteros de la rana están abiertos y completos. |
| anatomia | 8.0 | 8 | C muestra el interior del tejido con un solo foco (la molécula grande, en y≈420-960/1920, sobre la franja de subtítulos) y nada cortado; las venitas dibujadas sobre cada célula son una estilización (los capilares reales van entre células), pero se lee como tejido y no confunde. |
| realismo | 7.0 | **7** | A se ve 3D realista (rana escaneada, vidrio con manchas, desenfoque de lente): 9. C: moléculas son capa de explicación; el tejido tiene subsuperficie pero los brillos son manchas blancas iguales, algo de plástico: 8. B baja el conjunto: el imán (acero pintado con chorreados, pernos, tubos con abrazaderas) y Pete pasan, pero el fondo delata la maqueta: cerros de un solo café con facetas planas y sin bruma de distancia, la malla de los cerros flotando a la izquierda (ver problema 1), suelo del salar liso sin polígonos de sal, torres de bordes perfectos y vapor en conos idénticos. Para llegar a 8 en B: cambiar los cerros por un fondo de montaña real (HDRI de Poly Haven o terreno CC0 con textura de roca y variación de color) con algo de bruma, y darle al suelo textura de costra de sal (ambientCG) con su relieve. |

## Bloqueantes y fallas automáticas (impiden aprobar)

1. 🛑 [B1] Los cerros nuevos flotan: en x 0-230, y≈560-595 (a 720x1280; x 0-345, y 840-893 a 1080) se ve la parte de abajo de la malla de los cerros, dentada, con una franja clara de cielo entre ella y el suelo, que termina en un escalón vertical en x≈230 donde los cerros sí llegan al suelo. Kling va a copiar esa franja en todo el clip. — plano B · cuadro s. **Arreglo:** Bajar el objeto de los cerros 2-3 m o alargarle la falda por debajo del nivel del suelo para que toque el horizonte en todo el ancho; volver a mirar sólo la franja y 540-600.

## Sugerencias (las 5 más importantes; el resto queda en veredicto.json)

Ninguna.

## Verificación de la ronda anterior

| id | qué | arreglado |
|---|---|---|
| A1 | El imán gigante no se lee como imán sino como estanque o edificio de vidrio: paneles azule | sí |
| A2 | Luz pareja de mediodía con neblina: sin negros (p5=117, brillo 182,8) y sombras débiles; l | sí |
| A3 | La levitación no se lee: las botas de Pete quedan ~8 px (a 720) sobre una tapa cerrada (y≈ | sí |
| A4 | En el cuadro 0 la cara de la rana queda lavada por la franja vertical de reflejo del tubo  | sí |
| A5 | Una molécula queda justo detrás de la grande: su H blanco (x≈340, y≈877) y el borde rojo d | sí |
