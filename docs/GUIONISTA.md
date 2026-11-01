# Guionista — el agente que se preocupa sólo del guion (1-nov-2026)

**Pedido de Tomás (1-nov-2026, 01:04):** "los videos han estado fallando porque el hook es muy malo… el guion entero es bastante malo. Quiero una investigación increíble y un agente dentro del proyecto que se preocupe solo del guion: lo necesario y perfecto para el tema, que el hook sea increíble, que sepa qué es lo mejor para el algoritmo de hoy, con simulaciones si sirven."

**Qué hay:**
- **Este documento:** lo que dicen nuestros números, la investigación, el método, la receta del gancho y del guion, y las pruebas.
- **El agente `guionista`** (`.claude/agents/guionista.md`): escribe la premisa, 12 o más ganchos, 3 guiones distintos y el `guion.md` final. **No se pone nota a sí mismo:** lo juzgan otros.
- **Los jueces** (`.claude/agents/juez-gancho.md` y `.claude/agents/espectador.md`): agentes ciegos que no escribieron nada, sin acceso a los resultados reales.
- **Las herramientas** (`tools/guionista/`): `duelo.py` y `feed.py` arman las pruebas ciegas, `duelo.py contar` y `puntuar.py` las cuentan, `tira.py` saca los cuadros de 0–3 s de un video, y `calibracion/anclas.json` guarda los videos publicados con su resultado real (nunca se le muestra a un juez).
- **Revisión independiente (1-nov, 05:00):** un revisor que no hizo nada de esto encontró que la primera versión de este documento exageraba lo que probó el simulador, que la calibración estaba contaminada y que el duelo contra las anclas no filtraba. Lo que sigue ya está corregido; el detalle, en la lección 118.
- **La investigación completa:** `docs/estudios/guionista-a-algoritmo.md`, `-b-ganchos.md`, `-c-estructura.md` y `-d-simulacion.md`.

Si en una sesión no aparecen los tipos `guionista`, `juez-gancho` o `espectador` en el Agent tool, se lanza un `general-purpose` con el contenido del `.md` del agente como prompt (misma receta, mismos límites).

---

## 1. Lo que dicen nuestros números (corte del 1-nov, `PUBLICADOS.md`)
| Ep | Dur. | YT vistas | YT se quedó | YT % visto | YT prom. | IG pasa 3 s | IG envíos |
|---|---|---|---|---|---|---|---|
| 1 helado | 73 s | 4.077 | 77,5 % | 55,9 % | 40 s | 75,8 % | 20 |
| 2 picante | 75 s | 1.306 | 73,4 % | 43,4 % | 32 s | 80,1 % | 57 |
| **3 edificio que caminó** | 64 s | **13.894** | 75,3 % | 73,7 % | **47 s** | **83,3 %** | **9.776** |
| 4 cortina | 37 s | 2.992 | **79,9 %** | 75,8 % | 28 s | 67,4 % | 52 |
| 5 imán | 40 s | 1.626 | **39,7 %** | 63,7 % | 25 s | **58,1 %** | 50 |
| **7 rascacielos** | 48 s | **13.595** | 70,7 % | **89,3 %** | **42 s** | 76,7 % | 11 |

Los primeros 3 s de cada uno, cuadro a cuadro: `tools/guionista/calibracion/primeros3s_ep01-07.jpg`.

**Lectura (Tomás tiene razón a medias):**
1. **El gancho mata cuando es malo, pero no hace viral a nadie.** Al Ep. 5 lo deslizó el 60 % (39,7 % se quedó; YouTube no dice en qué segundo exacto; Galloway, 5.400 Shorts: bajo 60 % casi nunca rinden): un hombre chico y lejos, un cilindro oscuro que ocupa media pantalla, la píldora **SIMULACIÓN** (que dice "esto es falso") y una frase abstracta ("Tu cuerpo repele los imanes"). El Ep. 7 fue el 2.º peor (70,7 %): ciudad lejos, edificio chico, 3–4 píldoras de letra chica y un superlativo abstracto ("el más alto que Japón ha botado"; "botar" no se entiende igual en México). Los demás quedaron en 73–80 %: aceptables, no buenos.
2. **Lo que separa a los que se abrieron (13–14 mil) de los que no (1–4 mil) son los segundos que la gente se queda:** 42–47 s vistos en promedio contra 25–40 s en los otros. El % visto solo no separa (el Ep. 4 tuvo 75,8 %, más que el Ep. 3, pero dura 37 s y en promedio se veían 28 s). El Ep. 4 tuvo además el mejor "se quedó" del canal (79,9 %) y se frenó igual.
3. **La premisa pesa más que la frase:** los dos que se abrieron son *algo gigante que hace algo imposible, con la mecánica a la vista* (un edificio que camina, un rascacielos que se achica). Los cuatro que no, son cosas chicas del cuerpo o de la casa (helado, ají, cortina) o una promesa abstracta (imán). Beaupré (Creator Insider, sep-2026) dijo que un canal nuevo no tiene espectadores con historial; que entonces se empareja por tema es una lectura de OutlierKit, no de YouTube. Aun así, insistir en el tema que abrió es la apuesta más razonable con lo que hay.
4. **Envíos: no hay patrón claro todavía.** El Ep. 3 tuvo 9.776 envíos en IG porque tuvo 901 mil vistas; por cada mil vistas tuvo 10,8, casi lo mismo que el Ep. 5 (11,2) y menos que el Ep. 1 (24,2). El Ep. 7 tuvo 0,6 por mil: ése sí es bajo. La investigación (Berger y Milkman) dice que se comparte el asombro; con 6 videos no lo podemos confirmar.
5. **Nadie predijo nada:** el Ep. 3 no destacó en nuestras revisiones y el panel del Ep. 6 eligió el peor video del canal. Ningún revisor ni simulador predice un viral (Salganik et al. 2006: lo mejor rara vez fracasa y lo peor rara vez triunfa; el resto es lotería). **El sistema tiene que:** (a) no dejar salir un gancho desastre, (b) construir la retención con reglas que se pueden revisar, (c) elegir premisas del tipo que ya funcionó, y (d) medir cada video y aprender.

**Y el guion entero tenía problemas:** en el Ep. 7, cero "tú" (el Ep. 3 tenía tres), dos etiquetas "lo más…", datos laterales después del pico (la grúa, "dos pisos cada diez días"), el mejor gancho guardado para el final ("nadie lo vio caer") y 146 palabras en 47 s. (Ojo: el Ep. 3, el que más rindió, sí tenía años y nombres en la voz —1935, 2020, Shanghái—; la regla de no decirlos es de Tomás, no sale de los números.) Crítica frase por frase y reescritura en `docs/estudios/guionista-c-estructura.md` §4–5.

---

## 2. Lo que dice la investigación (resumen; fuentes en `docs/estudios/guionista-*.md`)
**El algoritmo (A):**
- YouTube prueba cada Short con una audiencia semilla: la puerta es **visto vs. deslizado**; después pesan el tiempo visto, las repeticiones, los likes y los compartidos. Las vistas llegan en olas y un Short puede volver semanas después (el Ep. 3 pasó de 1.483 a 13.894). Paga lo comprometido.
- Instagram: las 3 señales top son **tiempo visto, likes por alcance y envíos por alcance**; los envíos son los que llevan a no seguidores (Mosseri, ene-2025).
- TikTok: terminar el video es la señal fuerte.
- Los deslizamientos se concentran **al principio y al final**, casi nunca al medio (Dashlet): el guion se juega en los primeros 2 s y en no avisar que se acaba.
- YouTube 2026 castiga lo "genérico, repetitivo o de plantilla" y lo resubido: cada video, distinto de verdad.
- **Prueba real que viene:** YouTube anunció (23-sep-2026) que se podrán **probar hasta 3 cortes del mismo video** con su retención; ppc.land dice que incluye Shorts. Mientras, **Trial Reels de Instagram** muestra un Reel primero sólo a no seguidores.

**El gancho (B y C):**
- **"Trata tu intro como una miniatura"** (Galloway): el feed de Shorts no muestra miniatura; el cuadro 0 lo es.
- **Tiene que entenderse en mudo** (Hoyos): no porque la gente mire sin sonido (en Shorts casi todos tienen audio), sino porque la imagen se entiende antes que la voz: cuando la persona decide, ya vio todo el cuadro y escuchó ~4 palabras.
- **Curiosidad = brecha de información** (Loewenstein 1994); es máxima cuando uno *casi* sabe la respuesta (Kang et al. 2009): la pregunta del gancho tiene que ser una que el espectador cree que podría responder.
- **Se comparte el asombro** (Berger y Milkman 2012, ~7.000 artículos: el asombro encabeza lo compartido).
- **Texto en pantalla:** aparece en 67 % de los TikToks virales contra 30 % de los que no (Ling et al.); TikTok (2020): más del 63 % de los avisos con mayor CTR muestran el mensaje clave en los primeros 3 s.
- **Hay ~1 s, no 3:** el sentido de una imagen se capta en 13 ms (Potter, MIT 2014) y en el celular se pasa ~1,7 s por contenido (Facebook IQ). Cuando la gente decide, ya vio toda la imagen y escuchó ~4 palabras de Fernando: **manda la imagen**, y la palabra de la tensión tiene que sonar antes de 1,5 s.
- **El movimiento captura la atención solo** (Abrams y Christ 2003): el cuadro 0 no puede ser un plano quieto.
- **Da el qué, nunca el porqué** (Loewenstein): explicar en el gancho cierra la brecha.

**El guion (C):**
- Conflicto → resolución → conflicto nuevo, unidos con **"pero" / "por eso"**, nunca "y después" (Hoyos; Parker y Stone).
- **Regla pico-final:** la gente recuerda lo mejor y el final; **cortar justo en el pico**.
- Una frase, una imagen; cada dato lateral cuesta (Mayer).
- Cifras: sólo si cambian la imagen o vienen con una comparación conocida (Barrio et al. 2016).

**La simulación (D):**
- Simular audiencias con IA tiene poca evidencia: **sirve para filtrar perdedores claros y problemas de comprensión, no para elegir virales.**
- Lo que peor rinde es justo lo que hicimos en el Ep. 6: personas demográficas, nota absoluta, juzgar texto en vez de imagen, y decidir por el chiste. En 399 tests reales de titulares, un panel de 10 personas acertó 34,6 % (azar 30,4 %) y un solo "lector típico" sin persona, 49,2 % (Maiorano 2026; un solo autor, sin revisión de pares y con conflicto de interés: indicio, no prueba).
- Lo que sirve: comparaciones de a pares con los dos órdenes, jueces ciegos e independientes, imágenes reales cuando existen, calibrar con resultados reales y **anotar la predicción antes de publicar para ver si acierta**.

---

## 3. Nuestro simulador, calibrado (1-nov-2026)
Se corrió a ciegas sobre los 6 videos publicados, mezclados y con códigos al azar, sin decir cuáles eran reales ni cómo les fue (`tools/guionista/calibracion/corrida-2026-11-01/`):

| Prueba | Jueces | Correlación con "se quedó" de YouTube | Con vistas de YouTube | ¿Los 2 peores reales (Ep. 5 y 7) quedaron abajo? |
|---|---|---|---|---|
| Feed con perfiles, texto | 6 | **0,77** | 0,00 | Sí (5.º y 4.º) |
| Feed con perfiles, cuadros reales | 6 | 0,68 | −0,17 | Sí (5.º y 6.º) |
| Duelo de a pares sin perfil, cuadros reales | 4 × 15 pares | 0,66 | — | Sí (5.º y 6.º) |
| Duelo de a pares sin perfil, texto | 4 × 15 pares | 0,49 | — | Sí (5.º y 6.º); el Ep. 3 salió 1.º con 20 de 20 |

**Qué quiere decir:**
- **Sirve para el gancho:** en las cuatro pruebas los dos peores ganchos reales quedaron en los dos últimos lugares, y el orden se parece al real (0,49–0,77; con 6 videos esto es un indicio, no una prueba). El duelo de texto, que es el que se puede correr antes de animar, puso al Ep. 3 (el viral) primero en los 20 duelos.
- **No sirve para predecir vistas:** la correlación es cero. Los jueces premian lo cotidiano que "me pasa" (el Ep. 4 salió 1.º, y en la vida real se frenó) y castigan las mecánicas largas que en la vida real retuvieron (el Ep. 7 salió último y tiene el mejor % visto del canal).
- **No ve magnitudes:** puso al Ep. 7 tan mal como al Ep. 5, y en la realidad el Ep. 5 fue un desastre (39,7 %) y el Ep. 7 sólo flojo (70,7 %).
- **Uso decidido:** el simulador es un **filtro de ganchos** (si un candidato queda con los peores, se reescribe) y un **buscador de fugas** (dónde dice cada espectador que se iría y por qué). Nunca elige al ganador por sí solo, y nunca juzga si algo va a ser viral.
- Cada video publicado se suma a `anclas.json` y la calibración se vuelve a correr cada 4 videos (`puntuar.py` la calcula sola). Si en 10 videos la predicción anotada acierta menos del 60 %, el simulador pierde el voto.

---

## 4. El método del guionista, paso a paso (tope: 45 min de trabajo del guionista; ~15–20 subagentes chicos de jueces por video)
**Entrada:** la ficha de la idea (de `IDEAS.md` o de la caza de datos) con sus fuentes, `PUBLICADOS.md` y este documento.
**Salida:** `studio/episodios/<ep>/guion.md` (formato del manual §1–2) + `studio/episodios/<ep>/guionista/` con la premisa, los ganchos, los 3 guiones, las pruebas y la predicción.

1. **La premisa (10 min).** En una frase: *¿qué es lo imposible que se VE?* Sale de la pregunta "¿qué le contaría alguien a un amigo en una frase para que diga 'no te creo'?". Se pasa por las 5 preguntas de §4.1. Si la idea no tiene un imposible visible, se le dice a Tomás antes de escribir nada: el guion no la salva.
2. **12 o más paquetes de gancho (10 min)**, de al menos 4 tipos de §5.3. Cada paquete trae las 3 capas: **cuadro 0** (qué se ve, dónde, de qué tamaño), **texto en pantalla** (≤ 5 palabras) y **voz de 0–2 s** (≤ 10 palabras). Se descartan los que fallan la receta de §5.2 (G1–G14); quedan 6.
3. **Duelo de ganchos entre ellos (los jueces, 10 min).** Los 6 ganchos van a `duelo.py preparar <ep>` (sin anclas: todos son escenas imaginadas del mismo tema, descritas igual) y 4 `juez-gancho` ciegos los comparan de a pares, cada par en los dos órdenes. Pasan los 3 con más victorias; un empate se resuelve por la receta G1–G14. **No se compara contra las anclas con texto:** una escena imaginada contra videos reales con sus defectos gana casi siempre (en el Ep. 8, los 6 ganchos les ganaron a 5 de las 6 anclas, casi todo 4–0), así que ese umbral no filtra. El filtro contra las anclas es con cuadros reales, en el paso 8.
4. **3 guiones distintos de verdad (10 min)**, cada uno con un gancho finalista y una estructura distinta de §6 (no 3 versiones del mismo). 70–105 palabras, con la receta de §6.2.
5. **Cazadores de fugas (los jueces, 5 min).** `feed.py <ep>` (6 paneles por defecto): **un solo guion por panel** (rotando, con perfiles distintos), mezclado con las anclas, y 6 `espectador` dicen en qué frase se irían y por qué. (Con los 3 guiones de la misma idea en un mismo feed, los espectadores castigan la repetición — "otra vez la casa en el mar" — y la prueba no sirve: Ep. 8, 1-nov.) **Sirve para encontrar fugas, no para elegir:** cada guion lo ven sólo 2 espectadores con perfil, y la investigación dice que los perfiles empeoran la predicción. Toda frase donde se fueron 2 o más, se reescribe o se saca. "Lo ve entero" depende mucho del largo: no se compara con las anclas, que duran el doble.
6. **Elegir y entregar.** Gana el guion cuyo gancho tuvo más victorias en el duelo del paso 3, siempre que (a) en los cazadores nadie se haya ido antes del pago y (b) pase las 12 reglas. Si no, el siguiente. Se escribe `guion.md` con la sección **"Paquete de gancho"** (cuadro 0, texto en pantalla, voz, pregunta que abre, segundo en que se paga, momento para mandarlo; es "el centro" que pide la puerta 1) y **"Predicción"** (§7).
7. **Puerta 1 del auditor** como siempre. Si el auditor pide cambios en el gancho, el guionista los hace; el gancho no lo reescribe el auditor.
8. **Con el plano 1 ya renderizado (antes de la puerta 6): el filtro de verdad.** (a) **Prueba de mudo:** la tira de 0–1,5 s (`tools/guionista/tira.py`) va a 5 jueces que no vieron nada, que contestan "¿qué está pasando y qué te prometen?" en 10 palabras; pasa con 4 de 5 que coinciden con la promesa del paquete. (b) **Duelo con cuadros reales contra las anclas:** `duelo.py preparar <ep> --imagenes --con-anclas` (el candidato con `tira` en `ganchos.json`; todas las tiras a 360 px, así el animatic no pierde por resolución) y 4 `juez-gancho`; **si pierde contra más de la mitad de las anclas, se cambia el plano 1** (no el guion). Ésta es la única comparación contra las anclas que vale: imagen real contra imagen real.
9. **A las 48 h de publicado:** se compara con las dos predicciones (§7: la del guionista y la del duelo del paso 8), se anota en `PUBLICADOS.md` si acertaron, y el video entra a `anclas.json` con sus números y su tira (`tira.py`), descrito por un descriptor ciego que no conoce sus resultados (§3).

### 4.1 Las 5 preguntas de la premisa (todas sí, o no se escribe)
1. **¿Hay un imposible que se ve en un cuadro?** (un edificio con patas sí; "tu cuerpo repele los imanes", no).
2. **¿Es grande o se puede hacer grande?** (escala: un edificio, un lago entero, una casa en el mar).
3. **¿La pregunta que deja es una que el espectador cree que podría contestar?** ("¿cómo mueves una casa sin camión?" sí; "¿qué es el diamagnetismo?", no).
4. **¿La respuesta es una mecánica que se puede mostrar en 2–3 pasos visibles?**
5. **¿Hay un momento de "mira esta weá"?** (lo absurdo, el chiste o el detalle que dan ganas de mandarlo).

---

## 5. El gancho
### 5.1 El paquete: tres capas que dicen lo mismo
| Capa | Qué es | Regla |
|---|---|---|
| **Cuadro 0** | La miniatura del feed | Un solo sujeto, grande (más de un tercio del cuadro), centrado, recortado contra el fondo, **ya haciendo lo imposible**. Nada de calma antes del conflicto |
| **Texto en pantalla** | Para el que mira en mudo | 1 píldora como máximo, ≤ 5 palabras, que nombre lo raro ("UNA CASA CRUZANDO EL MAR"). Nunca "SIMULACIÓN" ni contadores en el cuadro 0 |
| **Voz 0–2 s** | La frase | ≤ 10 palabras: el objeto concreto + lo raro. Sin contexto, sin superlativos, sin años ni nombres |

### 5.2 La receta (cada punto se contesta sí o no)
- **G1 · Mudo:** ¿se entiende qué pasa con sólo el cuadro 0 y el texto en pantalla, sin voz?
- **G2 · Imposible visible:** ¿el cuadro 0 muestra algo que en la vida real no debería pasar, *ya pasando*?
- **G3 · Concreto:** ¿la primera frase nombra un objeto que se puede dibujar ("este edificio", "esta casa") y no una categoría o una propiedad ("tu cuerpo", "el magnetismo")?
- **G4 · Sin superlativo abstracto:** ¿la frase evita "el más alto/grande/impresionante" como gancho? (el superlativo puede ir segundo, a los 4–8 s, si suma).
- **G5 · Pregunta abierta:** ¿queda una pregunta que el espectador cree que podría contestar ("¿cómo?"), sin dar la respuesta en el gancho?
- **G6 · Coinciden:** ¿la imagen, el texto y la voz dicen lo mismo, en el mismo segundo?
- **G7 · Tamaño:** ¿el sujeto ocupa más de un tercio del cuadro y se lee en un teléfono a un brazo de distancia?
- **G8 · Sin señal de falso:** ¿nada en el cuadro 0 dice "esto no es real" (píldora SIMULACIÓN, "imagina que…", cara de maqueta)? Si hace falta avisar que es simulación, se avisa a los 3 s o más y chico.
- **G9 · Una sola cosa:** ¿hay una sola idea y una sola píldora en los primeros 2 s?
- **G10 · Para Latam:** ¿se entiende igual en México, Argentina y Colombia? (nada de "botar", "weá", "polola" en la voz).
- **G11 · Se mueve:** ¿algo se mueve en el cuadro antes de los 0,5 s? (el movimiento captura la atención solo; un cuadro 0 quieto pierde).
- **G12 · La tensión, temprano:** ¿la palabra que crea la tensión ("caminando", "achicó", "flota") suena antes de 1,5 s, o sea dentro de las primeras ~5 palabras? (Fernando dice ~4 palabras en lo que la gente decide).
- **G13 · Prueba a la vista:** si la frase suena increíble, ¿el cuadro 0 muestra la prueba real? (el Ep. 5 prometió algo increíble y mostró una simulación).
- **G14 · El qué, no el porqué:** ¿el gancho dice qué pasa sin explicar por qué? (explicar cierra la brecha y el espectador ya no necesita quedarse).

### 5.3 Tipos de gancho (con lo que ya sabemos)
| Tipo | Ejemplo | Cuándo |
|---|---|---|
| **Objeto imposible en acción** | "Este edificio de cinco pisos se fue caminando." (Ep. 3, el que más rindió) | Lo imposible se ve. **Primera opción siempre** |
| **Paradoja con escala** | "Nadie vio caer este rascacielos de cuarenta pisos." (reescritura del Ep. 7) | Cuando el resultado contradice lo que se ve |
| **El clímax primero (in medias res)** | El cuadro 0 es el final (la casa en medio del mar) y la voz pregunta cómo llegó ahí | Procesos largos con un final visual fuerte |
| **"Tú" en la escena** | "Si te metes a este lago, en dos días caminas por el fondo." | Cuando el espectador puede ponerse ahí (con cuidado: nada que se pueda imitar) |
| **Mito al revés** | "En Chiloé no te mudas de casa. Te mudas CON la casa." | Cuando hay una frase de sentido común que se da vuelta |
| **Conflicto que ya está pasando** | La cortina ya pegada en la cara (no el señor tranquilo antes) | Lo cotidiano: el conflicto en el cuadro 0 |

### 5.4 Lo que ya nos falló (no se repite)
| Gancho | Qué falló | Cómo se hace |
|---|---|---|
| "Tu cuerpo repele los imanes." + hombre chico flotando con píldora SIMULACIÓN (Ep. 5, 39,7 %) | Propiedad abstracta; sujeto chico; la píldora dice "falso" | El imposible grande y real primero (la rana flotando, cerca) y la promesa sobre ti después |
| "Este es el edificio más alto que Japón ha botado." + ciudad lejos y 4 píldoras (Ep. 7, 70,7 %) | Superlativo abstracto; edificio chico; letreros; "botado" | "Nadie vio caer este rascacielos de cuarenta pisos": el edificio grande achicándose en el cuadro 0, una píldora |
| "Te estás duchando..." + señor tranquilo con los ojos cerrados (Ep. 4) | El primer segundo es la calma | La cortina ya pegada en la cara en el cuadro 0 |
| "Te comes un helado rápido y..." (Ep. 1) | Buen gancho, pero el video repetía y se alargaba (40 s vistos de 73) | Gancho igual, guion de 35 s |

---

## 6. El guion entero
### 6.1 Estructura segundo a segundo (25–40 s, 70–105 palabras)
| Tramo | Qué va | Prueba |
|---|---|---|
| **0–2 s · Gancho** | El paquete de §5 | ¿Se entiende en mudo? |
| **2–6 s · Lo que está en juego** | Una frase: quién, cuánto o por qué importa. Queda abierta la pregunta "¿cómo?" | ¿Quedó una pregunta? |
| **6–20 s · Mecánica** | 2–3 pasos unidos con "pero" / "por eso"; cada paso, un cambio que se ve; uno mete al espectador con un "tú" | ¿Quedó algún "y después"? |
| **20–30 s · El pago** | La imagen que responde la pregunta del gancho; el tramo más rápido | ¿Se paga después del 60 % del video? |
| **Últimos 3–5 s · Cierre en el pico** | Una consecuencia o el chiste, y la última frase empalma con la primera (loop) | ¿Quedan ≤ 2 frases después del pago? |

- **"Y lo más loco"** ya no va después del pago: va a la mitad, como segundo gancho, sólo si es más grande que todo lo anterior. Si no, va al comentario fijado.
- **La enseñanza útil** (línea datos; regla del proyecto): el espectador termina sabiendo cómo funciona. Si además hay una frase de "qué hacer", que sea corta y parte del remate. Sacarla del todo es una propuesta pendiente de Tomás (§8).
- **El "momento para mandarlo"** se marca en el guion: la frase o imagen por la que alguien lo mandaría ("mira, una casa en el mar con bueyes adentro").

### 6.2 Las 12 reglas (sí o no; las revisa el auditor en la puerta 1)
1. ¿El cuadro 0, en mudo, muestra algo imposible o raro? (= G1–G2)
2. ¿La primera frase tiene ≤ 10 palabras y nombra el objeto concreto y lo raro?
3. ¿Se abre una pregunta en los primeros 5 s y se paga con imagen después del 60 % del video?
4. ¿Cero "y después", "después" o "luego" entre pasos? (las transiciones son "pero", "por eso", "así que", "hasta que")
5. ¿Cada frase tiene ≤ 14 palabras (como el manual) y una sola imagen que se puede dibujar?
6. ¿Cero etiquetas de emoción ("lo más impresionante", "lo más loco", "increíble"), o una sola seguida de algo más grande que todo lo anterior?
7. ¿Toda cifra dicha cambia la imagen o trae una comparación conocida, con un máximo de 2 en la voz? (el resto, a la pantalla o al post)
8. ¿Hay al menos un "tú" que ponga al espectador en la escena?
9. ¿Después del pago quedan ≤ 2 frases y ≤ 5 s?
10. ¿La última frase, seguida de la primera, suena a una sola frase (loop)?
11. ¿70–105 palabras (techo 128) y 25–40 s de voz estimada (techo 45 s)?
12. ¿Sin presentaciones ("en este video", "hoy te cuento"), sin años, nombres de científicos ni "un estudio dijo" en la voz (regla de Tomás del 21-oct), y sin chilenismos?

---

## 7. La predicción (se anota antes de publicar y se revisa a las 48 h)
En `guion.md` → "Predicción", y la misma línea en `PUBLICADOS.md`:
- **Se quedó (YouTube):** sobre o bajo el promedio del canal (72,6 % al 1-nov).
- **% visto (YouTube):** sobre o bajo 75 % (los dos que se abrieron: 74 y 89 %; los que no: 43–76 %). Con videos de distinto largo, el % compara mejor que los segundos.
- **Envíos en IG por cada mil vistas:** sobre o bajo la mediana del canal (10,6 por mil al 1-nov: Ep. 1 24,2 · Ep. 2 10,5 · Ep. 3 10,8 · Ep. 4 4,8 · Ep. 5 11,2 · Ep. 7 0,6).
- **Dónde se va la gente:** la frase que el guionista cree que es el punto débil (en Studio: dónde cae la curva de retención).
- **La predicción del simulador, aparte:** del duelo con cuadros reales del paso 8, si el gancho les gana a la mayoría de las anclas → predice "se quedó" sobre el promedio del canal; si no, bajo.

A las 48 h se anota si acertó cada una. **El simulador pierde el voto si en 10 videos su predicción acierta menos del 60 %**; la del guionista se mide igual, para saber si el método sirve.

---

## 8. Decisiones pendientes de Tomás
1. **El techo de 45 s.** Los dos videos que se abrieron duran 48 y 64 s, y en promedio se vieron 42–47 s. La investigación dice que más corto rinde más en general, pero lo que cuenta es retener. Propuesta: meta 30–40 s igual, y hasta **50 s** sólo para una mecánica en pasos cuyos cazadores de fugas no encuentren dónde se va la gente.
2. **"Termina enseñando algo útil" (regla de las instrucciones del proyecto).** Choca con cortar en el pico. Propuesta: la enseñanza es entender la mecánica; la frase de "qué hacer" sale de la cola. **Mientras Tomás no decida, la regla del proyecto manda:** el guion tiene que dejar algo útil (si es una frase al final, que sea corta y sea parte del remate), y la puerta 1 no lo castiga.
3. **Probar ganchos con gente real.** Instagram Trial Reels (cada prueba es un post: necesita tu OK) y, cuando aparezca en tu Studio, la prueba de 3 cortes de YouTube. Propuesta: probarlo en el próximo video con 2 ganchos (los primeros 3 s distintos, el resto igual).
4. **Insistir en "gigante imposible + mecánica"** por un tiempo (ingeniería, construcción, naturaleza a escala), porque es lo único que se abrió.
