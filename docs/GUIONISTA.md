# Guionista — el agente que se preocupa sólo del guion (1-nov-2026; reordenado el 23-nov-2026)

> **Cómo leer este documento**
> - **Dos niveles.** Las **reglas duras [DURA]** no se rompen nunca (lista justo abajo). **Todo lo demás es criterio:** puntos de partida, no leyes. Un criterio se rompe cuando el resultado le gana a los virales, anotando por qué en `guion.md`.
> - **Cada criterio lleva su evidencia:** **[MEDIDA]** sale de nuestros números (`PUBLICADOS.md`, YouTube Studio) o se revisa objetivamente (un texto ilegible); **[PROBABLE]** lo respalda un principio conocido (`docs/estudios/`) o varios virales de `docs/referencias/virales/`; **[HIPÓTESIS]** es una opinión, de Tomás o de Claude, sin probar.
> - **Las hipótesis nunca bloquean:** se anotan y se prueban con datos reales, alternando entre videos (`docs/ROTACION.md`) y revisando cada 4–6 videos. Cada 5 videos, una limpieza baja de nivel o borra lo que los datos no confirmaron.
> - **Qué decide si algo está bueno, en orden:** (1) las métricas reales (YouTube visto vs. deslizado y % visto; envíos en IG) mandan; (2) el ojo de Tomás en el celular; (3) los jueces ciegos, sólo como orientación.

**Pedido de Tomás (1-nov-2026):** "los videos han estado fallando porque el hook es muy malo… el guion entero es bastante malo. Quiero un agente que se preocupe solo del guion: lo necesario y perfecto para el tema, que el hook sea increíble, que sepa qué es lo mejor para el algoritmo de hoy, con simulaciones si sirven."

## Reglas duras [DURA]
1. Lo que se presenta como real es real, con **2 fuentes confiables**.
2. **Nada se publica ni se programa sin el OK de Tomás para ese post.**
3. Nunca escribir, pedir ni subir **API keys**.
4. **No copiar un video ajeno entero** (mismo tema + misma secuencia + mismos visuales). Reusar una fórmula de gancho o una estructura con otro tema sí se puede.
5. **Nada con derechos de autor** (los assets con licencia restringida viven sólo en `nadieteexplica/assets`).
6. **Temas prohibidos:** los de `proyecto/INSTRUCCIONES.md`.

---

## §0 · El proceso del guion (Tomás, 23-nov-2026)
**La meta: que cada guion le gane a los virales de la biblioteca** (`docs/referencias/virales/`). Éste es el proceso por defecto. Sus jueces orientan, no deciden: Claude puede pasar por encima de un juez escribiendo la razón en `guion.md`. El paso a paso está en la skill `guion` (`.claude/skills/guion/SKILL.md`).
1. **3 guionistas en paralelo**, cada uno con una estructura distinta (A inventaste X · B mecanismo con contradicción · C escalera de micro-datos · D mito + analogía), rotando según `docs/ROTACION.md`: la del video anterior no se repite. [PROBABLE] (las 4 salen de los virales de `investigacion-2026-11-23-formatos.md`; YouTube 2026 castiga lo "de plantilla").
2. **Gancho:** 12 ganchos (4 por guionista) en **duelo ciego** (`tools/guionista/duelo.py`, 4 `juez-gancho`). El ganador se mide además contra los ganchos virales (`duelo.py preparar … --anclas virales`); si pierde contra más de la mitad, por defecto se busca otro. Ojo: en texto, una escena imaginada tiende a ganarle a un video real (Ep. 8: nuestros 6 ganchos les ganaron a 5 de 6 anclas), así que este duelo orienta; el filtro fuerte es con el video del plano 1 (§4, paso 9). **Las fórmulas de apertura de los virales se pueden reusar con otro tema** y compiten en el duelo como cualquier gancho.
3. **Medio: algo nuevo cada 4–6 s** (dato, paso, número, falla nueva), cero relleno, unido con "pero"/"por eso". Si `juez-viral` marca `segundos_sin_novedad`, por defecto no pasa. [PROBABLE] (varios virales: falla nueva cada 3–5 s en "inventaste X", algo nuevo en pantalla cada 2–3 s; investigación de retención. El intervalo exacto no lo fija ningún estudio.)
4. **Final:** remate + loop + **"mándaselo a…" ligado al contenido** (detalle en §6.2, regla 11). [PROBABLE] (virales: "envíaselo a ese amigo que…"; Mosseri: los envíos llevan a no seguidores.)
5. **`juez-viral`** compara cada guion contra la biblioteca, parte por parte (gancho, medio, final). Por defecto pasa con 3 GANA, o 2 GANA + 1 EMPATA. Después, los **espectadores** (`feed.py`) buscan fugas en el que pasó.
6. **Máximo 2 reescrituras** (sólo lo que señalan los jueces). Si no llega, la idea se cambia por otra de la ronda del cazador, **sin pedirle correcciones a Tomás**.
7. **Tipo de apertura:** "lo raro primero" o "lo normal que escala antes de 3 s". [HIPÓTESIS] Ninguna está probada: se alternan, cada guion anota cuál usa en `docs/ROTACION.md`, y cada 4–6 videos se compara con visto vs. deslizado de YouTube.

**Cómo se usa a los jueces:** comparan **de forma relativa** contra el viral del mismo tramo ("¿cuál se ve más profesional?", "¿cuál deslizarías?"), nunca con nota absoluta. Cuando ya hay video, lo ven **en video**, no en láminas de cuadros quietos. **Si un juez le pone menos de 6 a un viral de millones, el mal calibrado es el juez, no el viral.**

**Qué hay:**
- **El agente `guionista`** (`.claude/agents/guionista.md`): premisa, ganchos, guiones y el `guion.md` final. No se pone nota a sí mismo.
- **Los jueces** (`.claude/agents/juez-gancho.md`, `juez-viral.md` y `espectador.md`): ciegos, no escribieron nada y nunca ven los resultados reales.
- **Las herramientas** (`tools/guionista/`): `duelo.py` y `feed.py` arman las pruebas; `duelo.py contar` y `puntuar.py` las cuentan; `tira.py` saca los cuadros de 0–3 s; `calibracion/anclas.json` guarda los publicados con su resultado real (nunca se le muestra a un juez).
- **La investigación:** `docs/estudios/guionista-a-algoritmo.md`, `-b-ganchos.md`, `-c-estructura.md`, `-d-simulacion.md` y `investigacion-2026-11-23-*.md`. Una revisión independiente (1-nov) corrigió exageraciones de la primera versión (lección 118).

Si en una sesión no aparecen los tipos `guionista`, `juez-gancho` o `espectador` en el Agent tool, se lanza un `general-purpose` con el `.md` del agente como prompt.

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

Los primeros 3 s de cada uno: `tools/guionista/calibracion/primeros3s_ep01-07.jpg`. Con 6 videos, todo lo que sigue es indicio.
1. **El gancho mata cuando es malo, pero no hace viral a nadie.** [MEDIDA] Al Ep. 5 se quedó el 39,7 % (Galloway, 5.400 Shorts: bajo 60 % casi nunca rinden). El Ep. 7 fue el 2.º peor (70,7 %) y aun así se abrió. Los demás, 73–80 %. Las causas que creemos (en el Ep. 5: sujeto chico, píldora **SIMULACIÓN**, frase abstracta; en el Ep. 7: edificio chico, 3–4 píldoras, superlativo) son [HIPÓTESIS]: YouTube no dice en qué segundo se fueron.
2. **Lo que separa a los que se abrieron (13–14 mil) de los demás (1–4 mil) son los segundos vistos:** 42–47 s contra 25–40 s. [MEDIDA] El % visto solo no separa (el Ep. 4 tuvo 75,8 % y el mejor "se quedó" del canal, pero dura 37 s y se frenó).
3. **La premisa pesa más que la frase:** los dos que se abrieron son *algo gigante que hace algo imposible, con la mecánica a la vista*; los otros cuatro son cosas chicas del cuerpo o la casa, o una promesa abstracta. [MEDIDA] (2 de 6). Que YouTube empareje por tema en un canal nuevo es lectura de OutlierKit, no de YouTube.
4. **Envíos: sin patrón todavía.** [MEDIDA] Por cada mil vistas: Ep. 3 10,8; Ep. 5 11,2; Ep. 1 24,2; Ep. 7 0,6 (bajo). Que se comparte el asombro (Berger y Milkman) no lo podemos confirmar con 6.
5. **Nadie predijo nada:** el Ep. 3 no destacó en nuestras revisiones y el panel del Ep. 6 eligió el peor video del canal. [MEDIDA] Ningún revisor ni simulador predice un viral (Salganik et al. 2006). **El sistema tiene que:** no dejar salir un gancho desastre, construir la retención con criterios revisables, elegir premisas del tipo que ya funcionó y medir cada video.

**El guion del Ep. 7** tenía cero "tú", dos "lo más…", datos laterales después del pico, el mejor gancho al final y 146 palabras en 47 s; crítica en `docs/estudios/guionista-c-estructura.md` §4–5. [HIPÓTESIS] Igual se abrió, y el Ep. 3 sí decía años y nombres (1935, 2020, Shanghái).

---

## 2. Lo que dice la investigación (resumen; fuentes en `docs/estudios/`)
Ésta es la evidencia detrás de los [PROBABLE] de este documento.

**El algoritmo:**
- YouTube prueba cada Short con una audiencia semilla: la puerta es **visto vs. deslizado**; después pesan tiempo visto, repeticiones, likes y compartidos. Las vistas llegan en olas (el Ep. 3 pasó de 1.483 a 13.894).
- Instagram: las 3 señales top son **tiempo visto, likes por alcance y envíos por alcance**; los envíos llevan a no seguidores (Mosseri, ene-2025). TikTok: terminar el video.
- Los deslizamientos se concentran **al principio y al final** (Dashlet).
- YouTube 2026 castiga lo "genérico, repetitivo o de plantilla" y lo resubido.
- **Duración:** quso.ai (108 mil Shorts) ve más vistas en 11–20 s (correlación); en los virales la gente mira ~30–47 s aunque duren 80–127 (`investigacion-2026-11-23-automatizacion.md`); en YouTube cuenta el % visto.
- **Pruebas reales:** YouTube anunció (23-sep-2026) que se podrán probar hasta 3 cortes del mismo video; Instagram tiene Trial Reels (sólo a no seguidores).

**El gancho:**
- El feed de Shorts no muestra miniatura: **el cuadro 0 lo es** (Galloway).
- **Hay ~1 s, no 3:** el sentido de una imagen se capta en 13 ms (Potter 2014) y en el celular se pasa ~1,7 s por contenido (Facebook IQ). Cuando la persona decide, vio todo el cuadro y escuchó ~4 palabras: **manda la imagen** (Hoyos: tiene que entenderse en mudo).
- **Curiosidad = brecha de información** (Loewenstein 1994), máxima cuando uno *casi* sabe la respuesta (Kang et al. 2009). Explicar en el gancho cierra la brecha.
- **El movimiento captura la atención solo** (Abrams y Christ 2003).
- **Texto en pantalla:** en 67 % de los TikToks virales contra 30 % de los que no (Ling et al.).
- **Se comparte el asombro** (Berger y Milkman 2012).

**El guion:**
- Conflicto → resolución → conflicto nuevo, con **"pero" / "por eso"**, nunca "y después" (Hoyos; Parker y Stone).
- **Pico-final:** se recuerda lo mejor y el final; cortar en el pico.
- Una frase, una imagen; cada dato lateral cuesta (Mayer, coherencia).
- Cifras sólo si cambian la imagen o traen una comparación conocida (Barrio et al. 2016).
- **Los virales con /watch** (`docs/referencias/virales/README.md`): 186–230 palabras/min, algo nuevo en pantalla cada 2–3 s y casi nunca un zoom de cámara, un ancla que aparece temprano y vuelve al 60–90 %, y se entienden sin sonido.

**La simulación:**
- Simular audiencias con IA **sirve para filtrar perdedores claros y problemas de comprensión, no para elegir virales.**
- Lo que peor rinde: personas demográficas, nota absoluta, juzgar texto en vez de imagen. Lo que sirve: pares en los dos órdenes, jueces ciegos e independientes, imagen real, calibrar con resultados reales y **anotar la predicción antes de publicar** (Maiorano 2026 es indicio, no prueba).

---

## 3. Nuestro simulador, calibrado (1-nov-2026)
Se corrió a ciegas sobre los 6 publicados (las "anclas"), con códigos al azar. **La corrida que vale** (`calibracion/corrida-2026-11-01b/`): un descriptor ciego describió las tiras de 0–3 s, enunciado neutro, cada par 2 veces en cada orden.

| Prueba (4 jueces × 15 pares) | Correlación con "se quedó" | Sin el Ep. 5 | Con vistas | Los 2 peores reales (Ep. 5 y 7) |
|---|---|---|---|---|
| **Duelo con cuadros reales** | **0,66** | 0,50 | −0,31 | **5.º y 6.º** |
| Duelo con descripción de texto | 0,49 | 0,10 | 0,26 | Ep. 5 último; Ep. 7 2.º |

La primera corrida (`corrida-2026-11-01/`) **está contaminada y no cuenta** (las descripciones las escribió quien conocía los resultados).

**Qué quiere decir** [MEDIDA] (6 videos, indicio):
- **Con imagen real sirve para el gancho:** los dos peores quedaron últimos. Con texto sólo atrapa el desastre (0,10 sin el Ep. 5).
- **No predice vistas** (−0,31 a 0,26).
- **Sesgo:** premia las caras en primer plano (el Ep. 1 ganó 19 de 20; en la vida real, 2.º en "se quedó").
- **Uso:** filtro de ganchos con imagen real y buscador de fugas; nunca elige al ganador solo. La calibración se hizo con tiras de cuadros; la versión en video (§0) está por calibrar.
- Cada publicado entra a `anclas.json` (tira con `tira.py`, descriptor ciego) y la calibración se repite cada 4 videos. Si en 10 videos la predicción del simulador (§7) acierta menos del 60 %, pierde el voto.

---

## 4. El método, paso a paso (tope: 45 min del guionista; ~15–20 subagentes de jueces por video)
**Entrada:** la ficha de la idea (`IDEAS.md` o caza de datos) con sus fuentes, `PUBLICADOS.md` y este documento.
**Salida:** `studio/episodios/<ep>/guion.md` (formato del manual §1–2) + `studio/episodios/<ep>/guionista/` con premisa, ganchos, guiones, pruebas y predicción.

1. **La premisa** (§4.1). Si la idea no tiene un imposible visible, se dice antes de escribir.
2. **12 paquetes de gancho** (4 por guionista, de al menos 4 tipos de §5.3), cada uno con sus 3 capas (§5.1). La receta de §5.2 sirve para mejorarlos y desempatar, no para botarlos antes del duelo.
3. **Duelo de ganchos** (§0.2): los 12 entre ellos con `duelo.py preparar <ep>`, cada par en los dos órdenes, y el ganador contra los ganchos virales.
4. **3 guiones distintos de verdad**, uno por guionista, cada uno con su estructura (§0.1) y los criterios de §6.
5. **`juez-viral`** (§0.5), con máximo 2 reescrituras (§0.6).
6. **Cazadores de fugas:** `feed.py <ep>` (6 paneles): **un solo guion por panel**, mezclado con las anclas, y 6 `espectador` dicen en qué frase se irían. (Con los 3 guiones de la misma idea en un feed, castigan la repetición: Ep. 8.) Sirve para encontrar fugas, no para elegir. Por defecto, la frase donde se fueron 2 o más se reescribe o se saca. "Lo ve entero" no se compara con las anclas, que duran el doble.
7. **Elegir y entregar.** Claude elige el que pasó `juez-viral` con menos fugas; si se aparta de lo que dijeron los jueces, anota por qué. `guion.md` lleva **"Paquete de gancho"** (cuadro 0, texto, voz, pregunta que abre, segundo en que se paga, momento para mandarlo) y **"Predicción"** (§7).
8. **Puerta 1 del auditor.** Si pide cambios en el gancho, los hace el guionista.
9. **Con el plano 1 renderizado (antes de la puerta 6), el filtro fuerte:** (a) **prueba de mudo:** el clip de 0–1,5 s a 5 jueces que no vieron nada ("¿qué está pasando y qué te prometen?", 10 palabras); pasa con 4 de 5 que coinciden con la promesa. (b) **Duelo contra las anclas y los virales** con imagen real (`duelo.py preparar <ep> --imagenes --con-anclas`, todo a 360 px), relativo y en video cuando se pueda (§0). Si pierde contra más de la mitad, por defecto se cambia el plano 1, no el guion.
10. **A las 48 h:** se compara con las predicciones (§7), se anota en `PUBLICADOS.md` si acertaron y el video entra a `anclas.json`.

### 4.1 La premisa
1. **¿Hay un imposible que se ve en un cuadro?** (un edificio con patas sí; "tu cuerpo repele los imanes", no). [MEDIDA] (los 2 de 6 que se abrieron).
2. **¿Es grande o se puede hacer grande?** [MEDIDA] (los mismos 2 de 6).
3. **¿La pregunta que deja es una que el espectador cree que podría contestar?** ("¿cómo mueves una casa sin camión?" sí; "¿qué es el diamagnetismo?" no). [PROBABLE] (Kang et al. 2009).
4. **¿La respuesta es una mecánica que se muestra en 2–3 pasos visibles?** [PROBABLE] (virales "inventaste X").
5. **¿Hay un momento de "mira esta weá"** que dé ganas de mandarlo? [PROBABLE] (Berger y Milkman).
6. **¿La idea central cabe en una frase, sin "y además", y la carga un solo objeto o imagen que vuelve en el gancho, el medio y el cierre?** (Ep. 10e: la flor de cerezo; el Ep. 10d metió seis ideas y ninguna central). Si no, hay dos videos. [PROBABLE] (los virales usan un ancla que vuelve al 60–90 %; Mayer, coherencia.)

---

## 5. El gancho
### 5.1 El paquete: tres capas que dicen lo mismo
| Capa | Qué es | Punto de partida |
|---|---|---|
| **Cuadro 0** | La miniatura del feed | Un solo sujeto, grande, centrado, recortado contra el fondo, **ya haciendo lo imposible** |
| **Texto en pantalla** | Para el que mira en mudo | 1 píldora, ≤ 5 palabras, que nombre lo raro ("UNA CASA CRUZANDO EL MAR") |
| **Voz 0–2 s** | La frase | ≤ 10 palabras: el objeto concreto + lo raro |

### 5.2 La receta (sí o no; la revisa también el auditor en la puerta 1)
- **G1 · Mudo:** ¿se entiende qué pasa con el cuadro 0 y el texto, sin voz? [PROBABLE] (Potter; Hoyos; virales).
- **G2 · Imposible ya pasando:** ¿el cuadro 0 muestra lo raro *pasando*, sin calma antes? [PROBABLE] (Galloway; virales).
- **G3 · Concreto:** ¿la primera frase nombra un objeto que se puede dibujar ("este edificio") y no una propiedad ("tu cuerpo", "el magnetismo")? [PROBABLE] (Ep. 5 + virales).
- **G4 · Sin superlativo abstracto** como gancho ("el más alto…"); puede ir a los 4–8 s si suma. [HIPÓTESIS] (el Ep. 7 lo tenía y se abrió).
- **G5 · El qué, no el porqué:** ¿queda una pregunta abierta, sin explicar la respuesta? [PROBABLE] (Loewenstein; Kang).
- **G6 · Coinciden:** ¿imagen, texto y voz dicen lo mismo en el mismo segundo? [PROBABLE] (Mayer, contigüidad).
- **G7 · Legible:** ¿el sujeto y el texto se leen en un teléfono a un brazo de distancia? [MEDIDA] (se revisa en el cuadro). Que el sujeto ocupe más de un tercio del cuadro: [PROBABLE] (Ep. 5 y 7 + virales).
- **G8 · Sin señal de falso:** nada en el cuadro 0 dice "esto no es real" (píldora SIMULACIÓN, "imagina que…", cara de maqueta); si hay que avisar, chico y desde los 3 s. Si la frase suena increíble, el cuadro 0 muestra la prueba real. [PROBABLE] (Ep. 5; los virales avisan "ilustrativo" en letra chica).
- **G9 · Una sola cosa:** una idea y una píldora en los primeros 2 s. [PROBABLE] (Mayer; Ep. 7).
- **G10 · Se mueve** algo antes de los 0,5 s. [PROBABLE] (Abrams y Christ).
- **G11 · La tensión, temprano:** la palabra que crea la tensión ("caminando", "achicó") suena antes de 1,5 s, dentro de las primeras ~5 palabras. [PROBABLE] (Facebook IQ; Potter).
- **G12 · Para Latam y sin datos de archivo en la voz:** nada de "botar", "weá", "polola"; sin años, nombres ni contexto en la frase del gancho. [HIPÓTESIS] (regla de Tomás; el Ep. 3 decía años y fue el mejor).

### 5.3 Tipos de gancho
| Tipo | Ejemplo | Cuándo | Evidencia |
|---|---|---|---|
| **Objeto imposible en acción** | "Este edificio de cinco pisos se fue caminando." (Ep. 3) | Lo imposible se ve. Primera opción | [MEDIDA] (1 video) |
| **Paradoja con escala** | "Nadie vio caer este rascacielos de cuarenta pisos." | El resultado contradice lo que se ve | [HIPÓTESIS] |
| **El clímax primero** | Cuadro 0 = el final (la casa en medio del mar) y la voz pregunta cómo llegó ahí | Procesos largos con final visual fuerte | [HIPÓTESIS] |
| **"Tú" en la escena** | "Si te metes a este lago, en dos días caminas por el fondo." | El espectador puede ponerse ahí (nada imitable) | [HIPÓTESIS] |
| **Mito al revés** | "En Chiloé no te mudas de casa. Te mudas CON la casa." | Una frase de sentido común que se da vuelta | [PROBABLE] (virales D) |
| **Conflicto que ya está pasando** | La cortina ya pegada en la cara | Lo cotidiano | [PROBABLE] (G2) |

### 5.4 Lo que ya nos falló
| Gancho | Qué pasó | Qué probar |
|---|---|---|
| "Tu cuerpo repele los imanes." + hombre chico flotando con píldora SIMULACIÓN (Ep. 5) | [MEDIDA] 39,7 % se quedó, el peor. Causa [HIPÓTESIS]: propiedad abstracta, sujeto chico, píldora que dice "falso" | El imposible grande y real primero (la rana flotando, cerca) y la promesa sobre ti después |
| "Este es el edificio más alto que Japón ha botado." + ciudad lejos y 4 píldoras (Ep. 7) | [MEDIDA] 70,7 % se quedó, 2.º peor, pero se abrió. Causa [HIPÓTESIS]: superlativo, edificio chico, letreros, "botado" | "Nadie vio caer este rascacielos de cuarenta pisos": el edificio grande achicándose, una píldora |
| "Te estás duchando..." + señor tranquilo (Ep. 4) | [HIPÓTESIS] "El primer segundo es la calma"; ojo: tuvo el mejor "se quedó" del canal (79,9 %) | La cortina ya pegada en la cara |
| "Te comes un helado rápido y..." (Ep. 1) | [MEDIDA] 40 s vistos de 73: el video se alargaba | Gancho igual, guion más corto |
| "Este piloto tiene veintiún años. Mañana sale en una misión kamikaze..." (Ep. 10c) | [HIPÓTESIS] Tomás: "pésimo". Sin paradoja ni pregunta; 4 protagonistas; "..." lentos; cierre con una cita que no contestaba nada | "A este piloto kamikaze lo castigaron por seguir vivo." |

---

## 6. El guion entero
### 6.1 Estructura (para un video de ~45 s)
| Tramo | Qué va | Prueba |
|---|---|---|
| **0–2 s · Gancho** | El paquete de §5 | ¿Se entiende en mudo? |
| **2–6 s · Lo que está en juego** | Una frase: quién, cuánto o por qué importa; queda abierto el "¿cómo?" | ¿Quedó una pregunta? |
| **6–30 s · Mecánica** | Pasos unidos con "pero" / "por eso", algo nuevo cada 4–6 s | ¿Quedó algún "y después"? |
| **30–40 s · El pago** | La imagen que responde la pregunta del gancho; el tramo más rápido | ¿Se paga después del 60 % del video? |
| **Últimos 3–5 s · Cierre en el pico** | Remate + loop + "mándaselo a…" | ¿Quedan ≤ 2 frases después del pago? |

### 6.2 Criterios del guion (sí o no; los revisa el auditor en la puerta 1)
1. **Duración: 35–50 s de voz, ~110–150 palabras a ~3,1 pal/s** (techo 52 s; meta de YouTube primero, Tomás 23-nov-2026). Si no cabe, se sacan pasos, no se acelera. [PROBABLE] (en los virales la gente mira ~30–47 s aunque duren más; nuestro Ep. 7 tuvo 89 % visto con 48 s). Reemplaza los números viejos (25–40 s, 70–105 palabras, techo de 45 s). Una versión larga sólo para IG es [HIPÓTESIS] por probar.
2. **Pregunta abierta en los primeros 5 s, pagada con imagen después del 60 % del video.** [PROBABLE] (Loewenstein; Dashlet).
3. **Algo nuevo cada 4–6 s** (§0.3), marcado en `guion.md` con su segundo: un dato que sube la apuesta, una pregunta corta ("¿Por qué?") o un "pero" que da vuelta lo anterior. [PROBABLE]
4. **Cero "y después", "después" o "luego" entre pasos;** las transiciones son "pero", "por eso", "así que", "hasta que". [PROBABLE] (Hoyos; Parker y Stone).
5. **Cada frase ≤ 14 palabras y una sola imagen que se puede dibujar;** la frase que no hace avanzar la idea central (§4.1.6) se saca, aunque sea un dato bueno. [PROBABLE] (Mayer).
6. **Cifras:** cambian la imagen o traen una comparación conocida; máximo 2 en la voz (el resto, a la pantalla o al post). [PROBABLE] (Barrio et al.).
7. **Etiquetas de emoción** ("lo más loco", "increíble"): cero, o una sola seguida de algo más grande que todo lo anterior. "Y lo más loco" va a la mitad como segundo gancho, nunca después del pago. [HIPÓTESIS]
8. **Al menos un "tú"** que ponga al espectador en la escena. [HIPÓTESIS] (el Ep. 3 tenía tres y el Ep. 7 cero, y los dos se abrieron).
9. **Historias: un solo protagonista, del gancho al cierre;** el contexto entra por él ("Su misión: estrellar su avión…"), nunca como clase ("Japón, 1944…"); nombres difíciles, en pantalla. [HIPÓTESIS] (Tomás 7-nov; espectadores del Ep. 10d).
10. **Cada "por qué" se contesta con una causa concreta que se puede imaginar** ("si decías que no, te iban a llamar cobarde"), no con una abstracción ("era su cultura"), y en cadena: versión oficial → "pero" con la verdad de adentro → consecuencia. [HIPÓTESIS] (Tomás 7-nov).
11. **Cierre:** el remate es la frase más fuerte, contesta la pregunta del tema y cierra el objeto del gancho, y empalma con la primera frase (loop). Después del pago quedan ≤ 2 frases y ≤ 5 s. Prohibido terminar con una cita de un personaje nuevo, un dato de contexto o un "pero no todos pensaban igual". [PROBABLE] (pico-final; Dashlet; las repeticiones cuentan en YouTube). Que el remate tenga ≤ 12 palabras: [HIPÓTESIS].
12. **El CTA "mándaselo a…" ligado al contenido:** una persona concreta que sale del tema ("mándaselo a quien siempre culpa al semáforo"), nunca genérico ("a un amigo"); en la voz, después del remate, ≤ ~2 s. [PROBABLE] (virales; Mosseri). Que dure ≤ 2 s: [HIPÓTESIS].
13. **El "momento para mandarlo"** se marca en el guion ("mira, una casa en el mar con bueyes adentro"). [PROBABLE] (Berger y Milkman).
14. **Sin presentaciones** ("en este video", "hoy te cuento"). [PROBABLE] (los deslizamientos se concentran al principio). **Sin años, nombres de científicos ni "un estudio dijo" en la voz, y sin chilenismos:** [HIPÓTESIS] (regla de Tomás del 21-oct; ver G12).
15. **La enseñanza útil** (regla de `proyecto/INSTRUCCIONES.md`): el espectador termina sabiendo cómo funciona; si hay una frase de "qué hacer", corta y dentro del remate. [HIPÓTESIS] (sacarla está pendiente, §8).
16. **Pausas con puntuación, sin "…" de más:** el narrador de Qwen3-TTS hace pausas largas en cada punto suspensivo (después se aprietan a ≤ 0,3 s con `tools/voz_ajustar.py`). Sólo puntos y comas; citas sin comillas. [MEDIDA] (prueba de voz del 23-nov-2026)
17. **Voz con energía:** el narrador de Qwen3-TTS ajustado por `tools/voz_ajustar.py` (hasta 1,2×); en el `words.json`, ≥ 3,1 pal/s y ningún silencio de más de 0,5 s entre frases, salvo los respiros de 0,4–0,6 s que se agregan en la edición antes del giro y antes de la frase final. Si sale lento, se recorta el texto. [MEDIDA] la velocidad se mide; que rinda mejor es [HIPÓTESIS] (Tomás 7-nov), aunque los virales hablan a 186–230 pal/min.
18. **Imagen sin bombeo de zoom:** lo que cambia cada 1–2 s es el contenido (un corte a un detalle, algo que cae, un texto), no la cámara entrando y saliendo; el movimiento lo dan elementos en cuadro y los cortes. [PROBABLE] (los virales con /watch casi nunca usan zoom; Tomás 8-nov).

### 6.3 Historias (Tomás, 7-nov-2026: "que no te demores en contar la historia")
Para historias reales con un protagonista. Caben en la duración de §6.2.1: el largo de 50–60 s y 150–190 palabras del 7-nov queda reemplazado. El orden [HIPÓTESIS]:

| Tramo | Qué va | Ejemplo (Ep. 10d) |
|---|---|---|
| **0–3 s · Gancho** | Paradoja con el protagonista; la pregunta se paga al final | "A este piloto kamikaze lo castigaron por seguir vivo." |
| **Lo que está en juego** | El contexto contado a través de él, en 2 frases | "Su misión: estrellar su avión con una bomba contra un barco…" |
| **La explicación oficial** | Re-gancho con pregunta + la respuesta que todos creen | "¿Cómo aceptas morir así? … era el mayor honor" |
| **El "pero"** | La verdad de adentro, con causa concreta y una cita corta del protagonista (el pico del medio) | "Pero él tenía miedo… ¿Por qué? Si decías que no…" |
| **La escena** | Un momento que se ve (objeto, gesto, frase) + el giro hacia el pago | Las azaleas, "Me adelanto", el motor que falla |
| **Pago y cierre** | Se paga el gancho; la última frase contesta y empalma con la primera | "Volvió vivo… Pero le tenían más miedo a volver vivos." |

Antes de mandar la voz: **leer el guion en voz alta con cronómetro** y marcar qué trabajo hace cada frase (gancho, contexto, re-gancho, causa, escena, pago); la que no hace ninguno, se saca. Y cazadores de fugas (§4, paso 6) aunque haya apuro, antes de gastar créditos de voz.

---

## 7. La predicción (se anota antes de publicar y se revisa a las 48 h)
En `guion.md` → "Predicción", y la misma línea en `PUBLICADOS.md`:
- **Se quedó (YouTube):** sobre o bajo el promedio del canal (72,6 % al 1-nov).
- **% visto (YouTube):** sobre o bajo 75 % (los dos que se abrieron: 74 y 89 %; los demás: 43–76 %).
- **Envíos en IG por cada mil vistas:** sobre o bajo la mediana del canal (10,6 al 1-nov).
- **Dónde se va la gente:** la frase que el guionista cree que es el punto débil (en Studio: dónde cae la curva).
- **La del simulador, aparte:** si el gancho les gana a la mayoría de las anclas en el paso 9 → "se quedó" sobre el promedio; si no, bajo.

A las 48 h se anota si acertó cada una. El simulador pierde el voto si en 10 videos acierta menos del 60 %; la del guionista se mide igual. Estos resultados alimentan la limpieza de cada 5 videos (las hipótesis que no se confirman bajan o se borran).

---

## 8. Decisiones pendientes de Tomás
1. **"Termina enseñando algo útil" (regla de las instrucciones del proyecto)** choca con cortar en el pico. Propuesta: la enseñanza es entender la mecánica; la frase de "qué hacer" sale. Mientras no decida, vale §6.2.15 y la puerta 1 no lo castiga.
2. **Probar ganchos con gente real:** Instagram Trial Reels (cada prueba es un post: necesita tu OK) y la prueba de 3 cortes de YouTube cuando aparezca en tu Studio. Propuesta: el próximo video con 2 ganchos (los primeros 3 s distintos, el resto igual).
3. **Insistir en "gigante imposible + mecánica"** por un tiempo (ingeniería, construcción, naturaleza a escala): es lo único que se abrió y es el carril que más rompe en los virales.

(El techo de 45 s quedó resuelto el 23-nov: 35–50 s, techo 52, §6.2.1.)
