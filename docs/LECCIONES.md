# Lecciones — errores, cómo se solucionaron y la regla que queda

Documento vivo. Cada error que le cuesta tiempo o calidad a Tomás se anota aquí con su regla, y la regla se copia al documento que corresponde (manual, automatización o CONTEXTO). **Antes de producir un video nuevo se lee este archivo.** La idea es usar cada error para mejorar siempre.

## Ep. 1 — Congelamiento cerebral (17 al 19-oct-2026)

Resultado: se publicó el 19-oct a las 16:35 en Instagram, TikTok y YouTube, pero costó ~3 días y muchas horas de Tomás mirando. Lo que más dolió fue entregar cosas malas, prometer horas que no se cumplieron y que Tomás tuviera que encontrar los errores él.

### Calidad de imagen

| # | Qué pasó | Causa | Solución | Regla que queda |
|---|---|---|---|---|
| 1 | El interior de la cabeza era "asqueroso" y no se entendía nada (v2 y v3) | Demasiadas piezas a la vez (cráneo partido, ojos de caricatura, cortes con parches planos, cerebro a medias) y cámaras distintas en cada plano | **"Cabeza de vidrio"**: siempre de perfil, fondo azul noche, anatomía real (Z-Anatomy) con materiales limpios. **Solo se ve y brilla lo que nombra la voz.** Sin cráneo ni cortes. Aprobado por Tomás el 19-oct | Manual §8 "Interior del cuerpo". Un foco por plano |
| 2 | Vasos y botellas flotando o atravesando las manos; dedos que no tocan la taza ni el cono (v2 y v3, Tomás lo marcó dos veces) | Blender + Mixamo no tienen contacto real de dedos. Cada arreglo (IK, `cup_matrix`) quedaba "casi" | **Kling** (IA de video) para todo plano con manos y objetos o con manos en la cara, partiendo de un cuadro nuestro | Manual §8 "Objetos en la mano y reacciones → Kling" |
| 3 | En Kling, los dedos de la taza seguían raros | Kling **copia el agarre del cuadro de partida**, y el nuestro era malo | Partir de un cuadro **con la mano libre** y pedir que la mano traiga el objeto (taza con las dos manos) | Siempre partir con la mano libre o con el objeto apoyado |
| 4 | En un clip, los vasos pasaron de negros a transparentes a mitad del clip | En el cuadro de partida los vasos se veían negros (transmisión pura a 12 muestras) | Vasos con alfa (se leen claros) y cuadro de partida nuevo | El cuadro de partida tiene que mostrar los objetos tal como deben verse |
| 5 | Kling rechazó un clip ("risk control") | La instrucción tenía "sharp pain" y "teeth clenched" | Reescribirla con "funny brain freeze" | Nada de palabras de dolor o violencia en las instrucciones de Kling |
| 6 | El cono aparecía de golpe en la mano al final del plano 8 | Visibilidad del objeto mal puesta | Se ocultó y se re-renderizó solo ese plano | En la hoja por plano, revisar que nada aparezca o desaparezca de golpe |
| 7 | El domo del interior desaparecía en el plano 15 (fondo celeste) | `key_vis` con intervalos repetidos: el "ocultar" del plano anterior pisaba el "mostrar" | `key_vis` ahora junta los intervalos | — (arreglado en el código) |
| 8 | Las luces del interior se apagaban durante el plano | Claves de energía con interpolación Bezier | Interpolación constante en el corte | Todo lo que cambia "en el corte" va en constante |
| 9 | La cámara de entrada a la cabeza daba la vuelta larga por detrás | Ángulos euler incompatibles entre claves | Euler compatible con la clave anterior | — (arreglado en `camera()`) |
| 10 | La lengua y el helado se movían hacia el lado y no hacia arriba | `delta_location` vive en el espacio del hueso, no del mundo | Convertir "arriba" al espacio del hueso (`UPB`) | Movimientos de objetos colgados de huesos: convertir el vector |

### Proceso y tiempos

| # | Qué pasó | Causa | Solución | Regla que queda |
|---|---|---|---|---|
| 11 | 7–8 horas para un video malo | Se renderizó todo sin aprobar el look | Gates: cuadros de estilo → OK → render → revisión → OK | Manual §8: dos OK de Tomás antes de gastar horas |
| 12 | Tomás tuvo que decir "revisa tu trabajo" | Se mostraban cosas sin autorrevisión plano por plano | Revisión propia obligatoria (tiras por plano, hoja de contacto, cuadros de contacto de manos) antes de mostrar | Nada le llega a Tomás sin revisión propia |
| 13 | Dos trabajos en paralelo (Kling y RunPod) murieron y nadie lo notó durante 1 hora | Los subagentes se cortan cuando Tomás escribe a mitad de un turno. No se revisó si seguían vivos | Se rehicieron directo. **Lo que debe sobrevivir corre en GitHub Actions o RunPod**, no en subagentes | Revisar cada 15 min todo lo que corre en paralelo y avisar al tiro si algo cae |
| 14 | Se prometieron horas que no se cumplieron (11:40, 15:45) | Estimaciones sin medir. La prueba de GPU fue con cuadros livianos | El pod sube su avance cada 3 min (`progreso.txt`) | Dar horas solo con datos medidos y avisar **antes** de la hora si se atrasa |
| 15 | El render ocupó las 20 máquinas de GitHub y bloqueó Kling | Partes = límite de concurrencia | 16 partes | Dejar siempre 4 máquinas libres |
| 16 | Una parte del render tardó más de 2 h (laboratorio con 13 personas) en cuadros que igual iba a reemplazar Kling | Se renderizaba todo | `saltar.py`: no se renderizan los planos que reemplaza Kling | — (automático en `render.yml` y RunPod) |
| 17 | Riesgo de que un render viejo pisara el borrador nuevo | Dos runs escriben en `ep01-borrador` | Se cancelaron los runs viejos antes de que subieran | Un solo armado por versión; los otros se cancelan |
| 18 | No se podían leer los logs de Actions | Bloqueado desde el espacio de trabajo | Errores y logs del pod se suben a la prerelease del run | Todo lo que haya que leer se sube a una prerelease |
| 19 | El video de 56 MB no se podía ver en el chat | Muy pesado | Versión liviana de 720p (~7 MB) | Siempre mandar versión liviana para el celular |
| 20 | Se gastaron 46 de 100 unidades de Kling en un video | Aprendizaje: 13 clips para 8 planos | Lo aprendido quedó escrito; biblioteca de reacciones (pendiente) | 2–3 clips por video, de 3 s en 720p (~5–8 unidades) |

### Herramientas y servicios

| # | Qué pasó | Solución |
|---|---|---|
| 21 | RunPod devolvía 403 (Cloudflare 1010) | `User-Agent` propio en `runpod_pod.py` |
| 22 | No había RTX 4090 en community | Se prueba en secure y con otras GPU (salió una RTX A5000 a ~USD 0,22/h) |
| 23 | Metricool rechazó TikTok: "TikTok title is required" | `tiktokData.title` obligatorio |
| 24 | No se pueden subir archivos a GitHub desde el espacio de trabajo | Workflow `release.yml` copia el MP4 del borrador al Release `epNN` |
| 25 | El asistente de RunPod ofrecía crear máquinas y pegarle la clave a un agente | No usarlo: las máquinas las crea el workflow y la clave vive solo en el secreto |

### Decisiones de Tomás tomadas en el camino
- Interior "cabeza de vidrio": **sí** (19-oct).
- YouTube `madeForKids`: **no** (19-oct).
- Kling (Trial USD 9,80) y RunPod (USD 10): comprados el 19-oct, con el presupuesto del mes excedido a propósito.
- El Ep. 1 se publicó sin la revisión independiente, porque Tomás lo aprobó y pidió publicarlo. **Desde el Ep. 2 vuelve a ser obligatoria.**

### Pendiente para el próximo video
1. **Biblioteca de reacciones** del protagonista (sorpresa, dolor, risa, pensar, tomar algo, señalar), hecha una vez con Kling y reusada sin gastar unidades.
2. ~~**Auditor** que revise cada etapa mientras se trabaja~~: listo el 19-oct (`docs/AUDITOR.md`). Ver la sección siguiente.
3. **Guiones pensados para la herramienta:** máximo 2–3 planos con objetos en la mano; el resto, anatomía o planos sin objetos.
4. **RunPod con 2–3 pods en paralelo**, para que un video completo tome ~20–30 min.
5. Medir las métricas del Ep. 1 a las 48 h y a los 7 días (`PUBLICADOS.md`).

## Auditor — lo que salió al construirlo y calibrarlo con el Ep. 1 (19-oct-2026)

| # | Qué pasó | Causa | Solución | Regla que queda |
|---|---|---|---|---|
| 26 | La v3 (interior "asqueroso", dedos flotando, cono que aparece) **pasó el QA automático completo** (`qa.txt`: PASA) | `tools/qa.py` sólo mide formato, volumen, negros y congelados | Auditor por etapas: detectores + revisores independientes | El QA técnico no es control de calidad; nada avanza sin la puerta del auditor |
| 27 | El video **publicado** tiene 0,6 s de pantalla vacía (52,9–53,5 s: fondo azul y sólo el subtítulo, antes de que caigan las letras) y nadie lo vio | Las letras del plano 23 parten fuera de cuadro | El detector de pantalla vacía lo marca como bloqueante | Ningún plano parte vacío: el título 3D entra desde el primer cuadro |
| 28 | Los clips de Kling que se usaron en el Ep. 1 tienen defectos dentro del tramo usado (cara que se "derrite" y ojos de caricatura en el plano 9, vasos que cambian de material en el 17) | La revisión de clips no se hizo cuadro por cuadro con la ficha al lado | Puerta 5: 8 cuadros + zoom donde hay movimiento + tramo usable por clip | Un clip sólo entra con su tramo usable aprobado |
| 29 | `entrega/caption.md` del repo quedó con `madeForKids: pendiente` y sin título de TikTok, aunque lo publicado sí los llevaba | Se arregló directo en las llamadas a Metricool y no en el archivo | La puerta 7 lee el archivo | Lo que se publica sale de `caption.md`; si se cambia algo al publicar, se cambia ahí primero |
| 30 | El 18-oct a las 22:45 corrían **40 máquinas** de Actions a la vez (dos renders de 20) | Se lanzó un render sin cancelar el anterior | El auditor de proceso cuenta las máquinas con la API de GitHub | Máx. 16 máquinas; antes de lanzar un render, cancelar el anterior |
| 31 | `render.yml` subía el MP4 al Release público solo, apenas pasaba el QA | `publicar: true` por defecto | Ahora `false`; el Release público lo llena `release.yml` después del OK | Al Release `epNN` sólo llega lo aprobado por el auditor y por Tomás |
| 32 | La primera revisión de la voz dijo que los "..." no hacían pausa (0,12 s) y era falso: el silencio real era 0,43 s | La alineación de ElevenLabs mete el silencio dentro de la palabra | `voz.md` lleva el silencio real medido con `silencedetect` | Las pausas se miden en el audio, no en la alineación |
| 33 | Los artefactos de Actions (renders viejos) no se pueden bajar desde el espacio de trabajo | Se sirven desde un host bloqueado | `traer-artefacto.yml` los copia a una prerelease | Para revisar una versión vieja, traerla a una prerelease |
| 34 | En planos generales (fila de voluntarios) el revisor no alcanzaba a ver los dedos | Grilla de 8 cuadros chicos | Zoom automático donde hay movimiento (`*_detalle.jpg`) | Si el revisor dice "material insuficiente", se mejora el material, no se aprueba |
| 35 | En la calibración, además de las versiones viejas, se auditó el video ya publicado y se largó una segunda ronda sobre él. Tomás no lo había pedido y no había nada que arreglar ahí | Se amplió el alcance sin preguntar | Se detuvo; lo útil quedó como regla para el Ep. 2 | No ampliar el alcance de un pedido sin preguntar; lo publicado no se re-audita salvo que Tomás lo pida |

## Ep. 2 — Los pájaros no sienten el picante (19-oct-2026)

| # | Qué pasó | Causa | Solución | Regla que queda |
|---|---|---|---|---|
| 36 | Partí armando el set con el protagonista de siempre (mesón, el mismo personaje llorando) y Tomás lo paró: "no el mismo personaje" | Arrastré la fórmula del Ep. 1 en vez de pensar qué necesitaba esta idea | Concepto nuevo hecho para la idea: comedia 3D con animales en el desierto de Arizona, el ratón hace de "tú" | **Cada idea se diseña desde cero** (¿humano o no?, personajes, fondo, cámara, estilo) pensando en la viralidad de esa idea. Está en `CONTEXTO.md` (Formato) y en el manual §4 |
| 37 | Los 3 subagentes que corrían (2 búsquedas y el revisor del guion r2) murieron cuando Tomás escribió a mitad de turno, igual que en el Ep. 1 (#13) | Los subagentes se cortan con cada mensaje de Tomás | Se anotaron como caídos en la bitácora; la r2 del guion se canceló con nota (`r2-cancelada/NOTA.md`) porque el guion cambió | Búsquedas largas, en Actions (`buscar-objaverse.yml`, `descargar.yml`); los subagentes, sólo para revisiones cortas que se relanzan |
| 38 | Abrí fuentes y listados de modelos uno por uno con WebFetch y Tomás lo paró | Consultas web en serie: lentas y frágiles (captchas, 202) | `fuentes.yml` baja todas las fuentes de una vez con reintentos y deja extractos para el auditor; las búsquedas de modelos van en `buscar-objaverse.yml` | **Consultas web en un solo workflow → prerelease → se lee el resultado.** WebFetch sólo 1–2 por tarea (CONTEXTO, Pipeline) |
| 39 | Relancé un revisor que creía caído y el original sí había terminado (escribió 1 min después del chequeo) | Revisé la carpeta un momento antes de que escribiera | Se detuvo el duplicado antes de que escribiera; el veredicto es el del original | Antes de relanzar un revisor, esperar 2–3 min después del mensaje de Tomás y volver a mirar `auditar.py estado` |

| 40 | Los 4 cuadros de estilo de la sesión anterior tenían errores que se veían a simple vista (patita despegada, molécula atravesando el sensor, ventanita de muelas rota, patas de la tupaya flotando) y la tupaya ya no era la de la ficha | El modelo de la tupaya se cambió después de renderizar `ficha.jpg` y nadie lo comparó; los cuadros se dejaron listos sin revisión propia con zoom | Revisión propia con recortes al 200 % antes del auditor; la tupaya volvió al modelo de la ficha | **El código de un personaje queda congelado cuando sale la ficha**: si se cambia, se vuelve a renderizar `ficha.jpg` en el mismo commit. Cada cuadro se revisa con zoom (manos, contactos, ojos) contra la ficha antes de la puerta 4 |
| 41 | La puerta 4 no pasó en 3 rondas por el bosque (luz plana, fondo lavado, hojas de papel) | Se arregló lo que marcaba cada ronda (encuadre, ojos, modelo) pero el set del bosque nunca se rediseñó: se le fueron agregando cosas | Se paró en la r3 y se le pidió a Tomás elegir reemplazo | Un set que en la r1 ya tiene nota de belleza baja se rediseña entero (luz, capas, materiales) en la r2, no se parcha |
| 42 | En C0 las pistas del loop (ají mordido, lentes, medalla) no se leían en dos rondas: tiradas planas en la cima no se veían y, al bajarlas, caían en la franja de subtítulos | La cámara de C0 está más abajo que la cima de la roca (mira hacia arriba): lo plano arriba queda de canto y todo lo que está bajo la altura de la cámara cae bajo y≈990 | Repisas escalonadas a la derecha del ratón: ají acostado en el borde delantero (mordisco hacia arriba y a la cámara), medalla colgando del borde con la cinta tendida en la piedra (azul, para no confundirse con el ají), lentes en la repisa más alta. Se ubicaron con `PROBE` (punto del mundo → píxel) y `RAYO_PIX` (qué objeto se ve en un píxel) antes de renderizar | **Utilería chica que tiene que leerse: primero dónde está la cámara respecto de la superficie.** Si la mira desde abajo, va en bordes, colgando o apoyada de frente; se comprueba con rayos (`PROBE`/`RAYO_PIX` de `estilo_desierto.py`) y no a puro render. Pistas que se confunden por color (rojo sobre rojo) se separan con un color complementario |
| 43 | La puerta 4 necesitó 3 ciclos (9 rondas). En cada ronda el auditor nuevo encontró cosas distintas, y varios arreglos rompieron otra cosa (el hocico más ancho alejó a la tupaya de la ficha; la cabeza de 3/4 hizo que el ají pareciera pegado a la mejilla) | Arreglos hechos mirando sólo el recorte del problema, sin volver a comparar el cuadro entero con la ficha; lente de 28 mm que deformaba al personaje | Antes de cada ronda: hoja de contacto de los 4 cuadros al lado de la ficha y revisión propia con zoom; personaje medido (proporciones y color) contra la ficha; lentes de 45 mm o más para personajes chicos | **Cada arreglo se revisa en el cuadro entero y contra la ficha, no sólo en el recorte.** Personajes en primer plano con lente ≥45 mm. Si un arreglo toca un modelo, se re-renderiza la ficha en el mismo commit |

