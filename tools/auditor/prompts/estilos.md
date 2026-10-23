# Estilos del episodio: animado o realista

Cada episodio declara su estilo en `estilo.json`, y tu encargo trae el campo `estilo`. **Juzgas contra ese estilo, no contra el de otros videos**:
- Un video realista no pierde puntos por no tener colores saturados ni fondos celestes.
- Un video animado no pierde puntos por "no verse real".

Lee sólo la sección de tu estilo.

Lo que vale igual para los dos estilos:
- La lista cerrada de bloqueantes (comun.md).
- Nunca quemado ni lavado.
- Los personajes iguales a la ficha **de este episodio**.
- Encuadres con aire.
- La explicación dibujada en el momento en que la voz la nombra.

---

## ANIMADO (Ep. 1–4 y los que lo declaren)
El look de los primeros episodios: 3D semi-realista estilizado, tipo película animada.

- **Belleza:**
  - Luz suave de estudio, o una sola fuente fuerte y cálida para lo dramático.
  - Colores saturados sin quemar y fondo vivo (celeste, turquesa o un escenario simple y saturado).
  - Nada lavado ni plástico, y sin artefactos de render (ruido, piezas atravesadas, texturas estiradas).
- **Personajes:** estilizados está bien (proporciones de caricatura suave), siempre iguales a su ficha.
- **No hay criterio `realismo`:** no lo pongas.

---

## REALISTA (decisión de Tomás, 22-oct-2026; primero el Ep. 5)
**La meta, en palabras de Tomás:** "realista pero en un mundo animado". Su referencia de **calidad** es Zack D. Films (nunca su marca, sus personajes ni sus formatos). Se busca un mundo 3D con proporciones, materiales y luz reales, que **se nota que es animación 3D** pero nadie llamaría "monito animado". Tomás lo pidió porque los videos se veían "muy animados", y porque al pedir realismo en otro video siguió saliendo el mismo look y el mismo personaje de MakeHuman.

**No es fotorrealismo:** Tomás rechazó imágenes fotorrealistas generadas con IA ("nada de nada"). Un plano que parece grabación real o video de IA fotográfico no suma puntos: rompe el mundo animado. Si aparece al lado de planos 3D, es sugerencia de prioridad 1 en belleza ("otro look").

### Belleza (en realista)
- **Luz:** con dirección y sombras de contacto reales (los objetos tocan el suelo, con sombra debajo). Una luz de ambiente creíble (de estudio, de laboratorio, de día o de noche), no la luz pareja de una maqueta.
- **Materiales:** con textura e imperfecciones:
  - metal con rayas y reflejos que se deforman;
  - vidrio con marcas;
  - piel con poros, venas o humedad;
  - superficies con polvo, desgaste o huellas.
  - Nada liso de juguete ni de goma.
- **Color:** natural y con contraste (negros de verdad en las sombras). Sin paleta pastel de caramelo, y sin lavado ni neblina gris.
- **Cámara:** se comporta como un lente real:
  - profundidad de campo (el fondo desenfocado en un primer plano o en un macro);
  - desenfoque de movimiento en lo rápido;
  - escala creíble (una rana mide lo que mide una rana).
- **Sin artefactos de render:** ni ruido, ni luciérnagas (puntos blancos), ni texturas estiradas, ni piezas atravesadas.

### Criterio `realismo` (1–10, obligatorio en cuadros de estilo y animatic)
| Nota | Qué se ve |
|---|---|
| 10 | Al nivel de las mejores cuentas de animación 3D realista: todo el mundo (personas, animales, objetos, lugar) tiene proporciones, materiales y luz reales, coherente de principio a fin |
| 9 | Excelente: un detalle chico delata el juguete |
| **8** | **Animación 3D realista: proporciones reales, materiales con textura y luz con sombras reales; nada de caricatura ni pastel. Mínimo para aprobar** |
| 7 | Mezcla: el mundo se ve real, pero algo delata el juguete (un personaje de muñeco o de plástico, piel lisa, sombras flotantes, bordes perfectos) |
| 6 | Videojuego viejo, todo de plástico o de maqueta |
| ≤ 5 | Dibujo animado o caricatura (cabezones, ojos grandes, paleta pastel: el look de los Ep. 1–4) |

Más fotográfico no es más nota: el 10 es una animación 3D realista impecable, no un video que parezca grabado.

**Anclas (cuadros reales del Ep. 5, el video que Tomás eligió como la línea de la cuenta; receta en `docs/ESTILO_REALISTA.md`):**
- **6:** el imán gigante de la r1: paneles lisos de un solo color, luz pareja de mediodía sin negros (percentil 5 en 117), torre lisa, cerros de greda. Parecía estanque o maqueta.
- **7:** el mismo imán ya de acero sucio con pernos y Pete con su ropa real, pero el fondo de juguete: cerros facetados de un solo café sin bruma, flotando sobre una franja de cielo, y dos plumas de vapor idénticas.
- **8:** el cuadro final del imán: sol bajo de costado, negros reales, acero con chorreados y óxido, cerros con formas grandes y bruma que tocan el suelo, y Pete recortado contra los cerros.
- **9:** la rana: un escaneo real con piel moteada y gotitas, vidrio con polvo y huellas, foco en el ojo y el fondo de sal a contraluz desenfocado como en un lente real.

- **Evidencia:** di qué se ve real y qué **delata** el 3D, con plano y segundo. Delatores típicos:
  - piel lisa de muñeco, ojos grandes o brillantes de caricatura;
  - cabeza grande para el cuerpo;
  - sombras que no tocan el suelo;
  - colores de caramelo;
  - todo igual de enfocado;
  - bordes y esquinas perfectas;
  - agua o vidrio que no refractan.
- **Si tus materiales traen `ref_*.jpg` (fotos reales del tema):** compara contra ellas. ¿Los materiales, la luz y la escala se parecen a la foto? Las fotos son sólo para comparar: no son parte del video.
- **Una nota de realismo baja no es bloqueante:** es una nota, pero **más exigente que las otras**: en los demás criterios un revisor puede poner 7 y el video igual aprueba si el promedio da 8; en `realismo` **ningún revisor puede poner menos de 8** o no aprueba. "No aplica" no vale en un episodio realista.

### Señales de maqueta: revísalas TODAS, en cada cuadro, en los recortes a resolución completa
En el Ep. 5 lo que delataba la maqueta apareció de a poco, una cosa por ronda, porque no se vio en la miniatura. Por eso, en las puertas 4 y 6, recorre esta lista **completa** en cada cuadro o plano, usando los recortes `*_recorte_{arriba,medio,abajo}.jpg` (resolución completa) cuando los haya:
1. **Luz:** ¿el sol es bajo y de costado o a contraluz? ¿Hay negros de verdad y sombras de contacto? (La luz pareja cenital es maqueta.)
2. **Superficies grandes** (paredes, máquinas, torres, pisos): ¿tienen chorreados, mugre, rayas y variación? ¿O son lisas y de un solo color?
3. **Fondo lejano** (cerros, ciudad, horizonte): ¿son formas grandes con bruma de distancia, que **tocan el suelo**? ¿O son de greda, facetados o flotan (con cielo debajo)?
4. **Repeticiones:** ¿hay dos plumas, árboles, cerros o piezas idénticas?
5. **Lo que flota a propósito** (la rana, la persona): ¿se recorta contra el fondo lejano o el cielo, con aire visible bajo él? Si sus pies quedan contra el suelo lejano, se lee "parado lejos". ¿Flota donde la física lo pondría (en un imán, dentro del hueco)?
6. **Lo que no debe flotar** (vapor, cables, cerros, piezas): ¿cada cosa toca su base?
7. **Líneas en el suelo** (cables, caminos) que van al punto de fuga del centro del cuadro: ¿se leen como una aleta vertical?
8. **Brillos sueltos:** ¿hay una mancha del sol o del reflejo de una luz detrás del sujeto, que parece un objeto?
9. **Escala:** ¿todo mide lo que mide en la vida real?
10. **Material negro puro** o sin textura (un tubo, un hueco que es un agujero negro plano).

**Toda señal que veas va en `delatores`** (ver abajo), aunque sea chica. No elijas sólo las peores: la meta es arreglarlas todas en **una** pasada.

### `delatores` (sólo en realista, puertas 4 y 6)
Además de `problemas`, tu JSON lleva `"delatores": [...]` con **todo** lo que delata la maqueta, **sin tope**:
```json
"delatores": [{"cuadro": "B", "plano": null, "segundo": null, "zona": "arriba", "que": "cerros facetados de un solo café, sin bruma", "arreglo": "formas grandes y bruma de distancia; que toquen el suelo"}]
```
(`zona`: arriba, medio o abajo; en la puerta 6, `plano` y `segundo` en vez de `cuadro`.) En la ronda de verificación vuelven como ids `D1, D2…` y se verifican igual que los `A`.

### Vida (realista, puertas 6 y 7 → criterio `animacion`)
Lo vivo **nunca está quieto más de 1 s**: un animal respira o parpadea, sus patas derivan; una persona que flota busca el equilibrio con los brazos (animación en loop, no una pose fija). Un animal o una persona quietos como estatua es un 7 en `animacion`, con la sugerencia concreta del micro-movimiento.

### Capas de explicación (permitidas)
Las explicaciones pueden llevar **capas gráficas estilizadas encima del mundo real**, y eso **no baja el realismo**, siempre que el mundo de abajo sea real. Es lo que Tomás pidió que se repitiera del Ep. 4: meterse dentro de lo que se explica y dibujar cada cosa cuando la voz la nombra. Ejemplos:
- líneas de campo que brillan;
- flechas;
- una molécula de agua aumentada;
- un corte con el interior a la vista;
- etiquetas tipo píldora.

### Personajes humanos (realista)
- Proporciones reales, piel y pelo creíbles y ropa con tela de verdad.
- Nada de cabezones, ojos grandes ni piel lisa de muñeco.
- **El protagonista de MakeHuman de los episodios anteriores ya no se usa**: si aparece, baja `realismo` (y si se ve claramente de dibujo animado, es B9).
- Si una persona realista no se logra bien, es mejor que salga de espalda, en silueta, fuera de foco o sólo sus manos (con guantes), antes que una cara de muñeco en primer plano.

### Cuándo es bloqueante (B9) y cuándo es nota
- **B9** sólo cuando un plano o personaje es **claramente dibujo animado** dentro de un video realista (lo que en la escala sería ≤ 5): un monito de caricatura, ojos gigantes, un mundo de plastilina.
- Las **capas de explicación** (líneas, flechas, píldoras, la molécula aumentada, el corte) **nunca** son B9.
- Algo "de plástico" o "de juguete" que no llega a dibujo animado (un 6–7 en la escala) **no es B9**: va en la nota de `realismo` y en una sugerencia con el arreglo.

### Lo que no es defecto en realista
- Un fondo desenfocado por la profundidad de campo no es "fondo liso" ni "plano vacío": es el lente. El aviso automático de `fondo_liso` puede saltar igual, y tú dices si es defecto o es el desenfoque buscado.
- Colores sobrios (grises, metal, blanco de laboratorio) no son "lavado" si hay sombras y negros de verdad.

### Kling (realista)
Kling parte de un cuadro 3D nuestro y el clip mantiene ese mismo look (nada de pasar a fotorrealismo de IA):
- la misma luz y los mismos materiales;
- que no derive a dibujo ni a otra cámara.

Si la cara, la piel o la luz cambian de estilo a mitad del clip, es un problema de `personaje` o `estabilidad`.
