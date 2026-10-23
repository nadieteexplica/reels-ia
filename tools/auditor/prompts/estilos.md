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
**La meta:** que parezca una película con efectos especiales, no un dibujo animado. No tiene que confundirse con una grabación, pero nadie debería decir "es un monito animado". Tomás lo pidió porque los videos se veían "muy animados", y porque al pedir realismo en otro video siguió saliendo el mismo look y el mismo personaje de MakeHuman.

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
| 10 | Un espectador podría dudar si es una grabación |
| 9 | Nivel de efectos de cine o de serie |
| **8** | **Claramente 3D, pero la luz, los materiales y la cámara son reales: nadie diría "dibujo animado". Mínimo para aprobar** |
| 7 | Mezcla: el mundo se ve real, pero algo delata el juguete (un personaje de plástico, sombras flotantes, bordes perfectos) |
| 6 | Videojuego viejo, todo de plástico o de maqueta |
| ≤ 5 | Dibujo animado o 3D estilizado (lo que se pidió evitar) |

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
El clip mantiene el mismo look que los cuadros renderizados:
- la misma luz y los mismos materiales;
- que no derive a dibujo ni a otra cámara.

Si la cara, la piel o la luz cambian de estilo a mitad del clip, es un problema de `personaje` o `estabilidad`.
