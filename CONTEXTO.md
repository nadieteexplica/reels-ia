# El viejo del dato (ex Nadie te explica) — contexto del proyecto

Leer esto entero antes de trabajar, junto con `proyecto/INSTRUCCIONES.md`: sus secciones *Seguridad* y *Publicación* mandan sobre todo. Es la fuente de verdad de lo decidido hasta ahora (18-oct-2026).

## La cuenta
- **Nombre:** **El viejo del dato**, usuario **@elviejodeldato** en las 3 redes (cambio de Tomás del 21-oct-2026: había muchas cuentas "Nadie te explica"; ya cambiado en TikTok). Foto de perfil: un viejo con boina que apunta a la cámara con un tazón, en un estudio con globo y mapa. Cuenta faceless de videos cortos hechos con Claude. El repo y la organización de GitHub siguen como `nadieteexplica`.
- **Redes:** Instagram (antes `nadie_te_explica`) · TikTok (ya @elviejodeldato) · YouTube Shorts (canal `UCFvRAW_exW4MgXEwQqCD1Fw`).
- **Metricool:** brand id `7499838`, zona horaria America/Santiago. Ya están conectadas las tres redes.
- **Dueño:** Tomás (Santiago, Chile). Habla en español chileno casual y directo, y quiere respuestas cortas.
- **Cómo trabaja:** Tomás pide cada video en el chat (decisión del 21-oct-2026: nada de producción programada). Claude investiga, escribe el guion, genera la voz, anima, deja todo listo, lo programa en Metricool con el OK de Tomás por post y revisa los datos.

## Formato (brief vigente)
- **YouTube primero (decisión de Tomás, 21-oct-2026):** es la red que paga desde Chile, así que todo se optimiza para YouTube Shorts (duración, ritmo, primer segundo, métricas, horario). **Instagram y TikTok siguen recibiendo el mismo video**, sin trabajo extra. Investigación y números en **`docs/YOUTUBE.md`**: el algoritmo prueba cada Short con una audiencia semilla y lo abre o lo corta según "visto vs. deslizado"; YPP desde el 1-feb-2027 = 1.000 suscriptores + 20 M vistas en 90 días u 8.000 h de video largo; Shorts paga poco (~US$0,03–0,06 por mil en Latam): la plata está en video largo y marcas.
- **Dos líneas de contenido (decidido por Tomás, 18-oct-2026):**
  - **Datos:** un dato impresionante por video, que termina enseñando algo, con fuentes. Usa los ganchos de abajo.
  - **Historias:** ficción (inventadas, absurdas o sin sentido: fábulas, story time). Si sale un híbrido historia + dato de forma natural, bien, pero no es requisito.
  - La proporción entre líneas está pendiente (ver "Decisiones pendientes").
- **Temas de todo el mundo**, no solo animales. Los ganchos de la línea datos son:
  - "¿Qué pasaría si…?"
  - "¿Cómo funciona por dentro?"
  - "¿Por qué no podemos…?"
  - "¿Qué pasa dentro de…?"
  - "¿Sabías que…?"
- **Formatos candidatos** (del estudio de referencias, sin probar todavía; fichas en `docs/REFERENCIAS.md` §5): corte que se transforma, objeto cotidiano "parece un error, pero es a propósito", "lo conté yo" con datos propios, concepto armado frente a ti, megaproyecto absurdo + "lo calculé", fábula absurda y story time.
- **Duración: meta 25–40 s, techo 45 s** (decisión de Tomás, 21-oct-2026, por YouTube: la mediana de vistas de los Shorts es máxima en 11–20 s y cae fuerte sobre 30 s; el promedio visto por Short es ~16 s). Un dato central, sin relleno. El chequeo automático acepta 25–45,5 s y 70–128 palabras (~2,9 palabras/s: 25 s ≈ 72, 35 s ≈ 101, 40 s ≈ 115). Historia: 62–65 s por TikTok (hasta el 21-oct), después 40–60 s el mismo día; el Ep. 3 (63,4 s) se hizo con la regla anterior y no se toca.
- **Monetización desde Chile (investigado el 21-oct-2026):** TikTok no paga por vistas (Creator Rewards sólo en EE. UU., Reino Unido, Alemania, Francia, Japón, Corea del Sur, Brasil y México, y hay que vivir ahí). Instagram no paga por vistas (los regalos en Reels sí están en Chile: US$0,01 por estrella). YouTube Shorts sí: 1.000 suscriptores + 10 M vistas de Shorts en 90 días; desde el 1-feb-2027, 20 M para los que entran y 10 M cada 90 días para seguir cobrando; ~US$0,03–0,10 por mil vistas, con Latam en la parte baja (México ~US$0,04). Facebook Content Monetization incluye Chile y el español (por invitación). La plata real son las marcas.
- **Cadencia (decisión de Tomás, 21-oct-2026; cada video lo pide él en el chat):** **5 videos por semana (lunes a viernes) y diario cuando un video tome ≤ 2,5 h**, haciendo 2 videos por sesión. La voz alcanza: a ~35 s son ~600 créditos por video, ~23.000 de 40.000 al mes con 30 videos. El cuello es el tiempo (Ep. 3: 5,5 h). Cada video tiene que ser distinto: YouTube no monetiza contenido "de plantilla con poca variación" y lo evalúa por canal. Detalle en `docs/AUTOMATIZACION.md`.
- **Video largo (decisión de Tomás, 21-oct-2026):** compilaciones de Shorts **muy de vez en cuando**, no con calendario fijo. Suman horas de video largo sin animar nada nuevo.
- **Lo que se presenta como real es real y verificado**, con fuentes. Nada de desinformar. La ficción de la línea historias puede ser todo lo loca que se quiera, pero no se disfraza de dato.
- **Animación 3D "sí o sí".**
- **Edición:** limpia, amigable, llamativa, entretenida y bonita de ver.
- **Rechazado:**
  - Low-poly (el video del oxígeno).
  - Rayos X / neón 2D.
  - Look lavado o sobreexpuesto con cámara pegada (primer intento del helado).
  - Copiar formatos de otras cuentas tal cual.
  - El pulpo como tema (no engancha).
- **Línea de la cuenta = el Ep. 5 (Tomás, 23-oct-2026):** el realista del imán y la rana es el estilo de video y de edición que más le ha gustado y se sigue en esa línea: mundo abierto a escala real, escaneos reales y Mixamo, materiales sucios, sol bajo de costado, lente real, entrar a lo que se explica con capas estilizadas encima, píldoras, SIMULACIÓN para lo hipotético y dato real + "¿y si…?" con números. Receta y tiempos en `docs/ESTILO_REALISTA.md`.
- **Realismo (Tomás, 22-oct-2026):** los videos se ven "muy animados" y quiere **realismo de verdad** (más real, no dibujo animado). Ya **no le gusta el personaje propio de MakeHuman**: pidió realismo en el aviso de Rhein (rama `rhein`) y siguió saliendo el mismo look y el mismo personaje. Primera prueba: el video del imán. **Aclarado por Tomás (22-oct, 23:26):** el realismo que quiere es el de Zack D. Films, "realista pero en un mundo animado" (referencia de calidad, nunca de marca), **no fotorrealismo**: rechazó las imágenes fotorrealistas de Canva. El auditor ya tiene el modo realista (`estilo.json` + criterio `realismo` ≥ 8; `docs/AUDITOR.md`).
- **Estilo por idea (DECIDIDO por Tomás, 19-oct-2026, manda sobre lo de abajo):** cada idea nueva se diseña **desde cero para esa idea y su viralidad**, sin arrastrar cómo se hizo el video anterior: si hace falta un humano o no, qué personajes, qué fondo, qué cámara y qué estilo 3D (puede ser totalmente otro). El protagonista humano es una opción más, no la cara obligatoria de la cuenta. Siguen vigentes: 3D sí o sí, verdad con fuentes y los estilos rechazados. Cada episodio deja sus personajes en `studio/episodios/<ep>/ficha.jpg`.
- **Estilo en evaluación (historia, hasta el Ep. 1):**
  - **Monito animado 3D.** Muestras de 5 s en tres estilos: A · Pixar suave, B · caricatura con contorno, C · plastilina.
  - **Semi-realista tipo Zack D. Films.** Él lo mostró como referencia. Usarlo como referencia de *calidad*, pero con personaje, colores y escenario propios. Nunca su marca.
  - **Usado en el Ep. 1 (18-oct-2026):** semi-realista con Mixamo y **personaje propio de cuerpo normal**, hombre joven de ~18–20 años, con el look del niño de las muestras (polera coral con estrella, pelo café en mechones). Se descartó el cabezón: las animaciones de Mixamo son captura de movimiento real y en cabezones las manos atraviesan la cabeza. Las reacciones van en primer plano para que la cara se lea en vertical.
  - Base del personaje: MakeHuman (CC0), armado en Blender. Las muestras A/B/C quedan como referencia histórica.
- **Referencias de look** (fichas en `docs/REFERENCIAS.md`; son referencias de calidad, nunca de marca):
  - **R4** (el clavo, Zack D. Films): escenas con personajes. Paredes celestes, luz suave de estudio y ropa en pastel saturado.
  - **R3** (la caverna): momentos dramáticos. Una sola fuente de luz fuerte y cálida, sombras profundas y contraluz.
  - **R8** (gancho del metro): objetos en primer plano. Render tipo producto, fondo oscuro cálido con partículas desenfocadas.

## Voz
- **ElevenLabs**, plan Starter (pagado), con **40.000 créditos al mes**. Cada toma gasta unos 1.200 créditos (hay que presupuestar ~1,3 tomas por video), y el saldo se ve en `out/status.json`.
- La voz elegida es **Fernando Martínez**: `voice_id dlGxemPxFMTY7iXagmOj`. Habla a 2,89–2,94 palabras por segundo contando las pausas (Ep. 1 y Ep. 2).
- Modelo `eleven_multilingual_v2`.
- Settings: stability 0.4, similarity 0.8, style 0.32, speaker boost activado.
- Se genera **con timestamps por carácter** para armar subtítulos palabra por palabra.

## Reglas de edición (del estudio de formatos virales y de `docs/REFERENCIAS.md`)
- **Gancho** en los primeros 0–2 s. El cuadro 0 es una imagen absurda o una pregunta: algo que todavía no tiene sentido.
- **Planos:**
  - **Algo cambia en pantalla cada 1–2 s y nunca más de 2 s sin cambio** (en un video de 35 s, unos 18–35 cambios; REFERENCIAS §3). **Máximo 6 escenas** por video (12 hasta el Ep. 3): una escena es una actuación animada que se arma una vez y se filma con varias cámaras (el Ep. 2 armó ~45); los cortes dentro de una escena son baratos y se usan los que hagan falta.
  - **Nunca más de 2 s sin un cambio en pantalla:** un corte, o algo que aparece o se transforma dentro del cuadro. Con transformación continua un plano puede durar más.
  - Cortes secos sincronizados con la voz.
  - La cámara siempre se mueve (acercamientos lentos u órbitas).
  - Cambio de escala cada 8–12 s.
- **Look (según el estilo del episodio, `estilo.json`; Tomás 22-oct-2026):** **animado** = fondos vivos (celeste/turquesa), luz suave de estudio, colores saturados; **realista** = `tools/auditor/prompts/estilos.md` (luz y materiales reales, color natural con contraste, lente real). En los dos: Nunca sobreexpuesto. Con encuadre vertical se deja aire: la cara del personaje va en el tercio superior.
- **Subtítulos:**
  - Palabra por palabra, de 1 a 3 palabras a la vez, en mayúsculas gruesas.
  - Blancos con borde negro, y la palabra activa en amarillo (#FFD23F).
  - Una o dos líneas, con la caja dentro de **x 120–888 · y 1000–1250**. Fuente de 76–88 px, que baja hasta 60 px si una palabra larga no cabe. Nunca en el 35% inferior.
  - **Palabra clave** (1–3 por video: la cifra, el objeto, el giro) en el color de su idea y un poco más grande.
  - **Excepción:** si el protagonista del plano es un objeto centrado, los subtítulos pueden ir arriba (y 280–480).
- **Llamados en pantalla:** mínimos (flechas finas, etiquetas tipo píldora). Sin logo encima.
- **Código de color fijo:** un color por idea u opción (correcto/incorrecto, opción A/B/C), igual en objetos, gráficos y subtítulos.
- **Símbolo que se repite:** un objeto o detalle que vuelve durante el video y sirve de portada.
- **Audio:**
  - Música 15–20 dB bajo la voz, con ducking.
  - Un efecto de sonido en cada evento visual.
  - −14 LUFS, true peak ≤ −1 dBTP.
- **Final en loop.** Nada de "sígueme" en el video: eso va en el texto del post o en un comentario fijado.
- **En prueba:** cierre que pide el envío con destinatario concreto ("mándaselo a ese amigo que…"). Se usa en algunos videos y se compara en `PUBLICADOS.md`.

## Pipeline técnico
- **Repo** público `nadieteexplica/reels-ia`:
  - Para generar voz se sube un JSON a `jobs/voz/`. GitHub Actions (`.github/workflows/voz.yml`) corre `tools/eleven.py` con el secreto `ELEVENLABS_API_KEY` y guarda en `out/`.
  - Modos del JSON: `voices` (buscar voces), `compare` (mismo texto con varias voces) y `tts` (locución final con alineación → `out/tts/<id>.mp3` + `<id>.json`).
  - Se espera el resultado con `git fetch` hasta que cambie `origin/main`.
- **Por qué Actions:** ElevenLabs está bloqueado desde el espacio de trabajo de Claude (la red tiene allowlist). GitHub y PyPI/npm sí funcionan.
- **Consultas web (regla de Tomás, 19-oct-2026):** nada de consultas en serie con WebFetch (assets, listados, APIs). Van todas en un solo workflow que deja el resultado en una prerelease y se lee de ahí: `fuentes.yml` (extractos de las fuentes de un guion, para el auditor), `buscar-objaverse.yml`, `descargar.yml`, `estilos.yml` (cuadros de estilo en paralelo). WebFetch sólo para una fuente puntual, máximo 1–2 por tarea.
- **Render actual (`studio/`):**
  - Cada video es una página three.js que expone `window.renderAt(t)` y `window.READY`.
  - `capture.py` (Playwright + SwiftShader) saca los cuadros a 30 fps.
  - `mux.sh` codifica H.264 + AAC con loudnorm −14 LUFS.
  - El audio (efectos y música) se sintetiza en numpy.
  - Instrucciones en `studio/README.md`.
- **Plan para subir calidad:**
  - Pasar a **Blender** (`pip install bpy`, la versión 5.2 está disponible) y renderizar en **GitHub Actions** (gratis en repo público, en paralelo).
  - Assets CC0: Poly Haven, ambientCG, Quaternius.
  - **Mixamo:** Tomás ya tiene la cuenta creada. Va a bajar un personaje (With Skin, con Breathing Idle) y unas 12 animaciones (Without Skin, FBX Binary, 30 fps, keyframe reduction none). Las adjunta en el chat. **No subirlas al repo público:** la licencia no permite redistribuir los archivos sueltos.
- **Publicación:**
  - Metricool `createScheduledPost` necesita una URL pública del video. El plan es hostearlo en el repo.
  - `createScheduledPostForReview` requiere plan de equipo. Con `autoPublish:false` llega una notificación para publicar a mano.
- **vidIQ (plan gratis):** pocos créditos. Ver un video cuesta 10 y una búsqueda de outliers cuesta 5.

## Presupuesto
- **Tope: 10.000 CLP al mes.** ElevenLabs Starter ya está pagado.
- **Octubre 2026 (excepción aprobada por Tomás el 19-oct):** compró el paquete Trial de la **API de Kling** (USD 9,80 = 100 unidades, vence a los 30 días) y cargó **USD 10 en RunPod** (sin Auto-Pay). ~19.400 CLP extra este mes.
  - Kling: 4 unidades por clip de 5 s a 1080p. Después del Trial, el paquete oficial más barato cuesta USD 700: si se sigue usando, hay que evaluar un intermediario con pago por clip (decisión de Tomás).
  - RunPod: ~USD 0,22–0,30 la hora (RTX A5000/A4000, community/secure); un video completo ~USD 0,3–0,5.
- Gratis primero: Blender, Actions, assets CC0, Mixamo. Toda compra nueva se pregunta antes con el monto en CLP.

## Seguridad (obligatorio)
- La API key de ElevenLabs vive **solo** en el secreto del repo. Nunca escribirla, repetirla ni commitearla.
- No crear cuentas ni usar contraseñas por Tomás.
- **Publicar en redes solo con su OK explícito, post por post.**

## Estado actual (23-oct-2026)
- **YouTube primero (21-oct-2026, noche):** Tomás decidió concentrar el proyecto en YouTube. Se investigó el algoritmo de Shorts, el YPP 2027, la frecuencia y la duración (`docs/YOUTUBE.md`, 27 fuentes en la prerelease `yt-fuentes`). Decidió: **videos de 25–40 s (techo 45)**, **5 por semana y diario cuando un video tome ≤ 2,5 h** (2 por sesión), **IG y TikTok siguen con el mismo video** y **compilaciones largas muy de vez en cuando**. Ajustado en el código (`presupuesto.json`: 25–45,5 s, 70–128 palabras, 6 escenas, tope 4 h y meta 2,5 h), el manual, el auditor, las ideas y las instrucciones. **Métrica principal en YouTube:** visto vs. deslizado, % visto y vistas comprometidas (se leen en YouTube Studio con el Chrome de Tomás; Metricool no las trae). Tomás calcula que el Ep. 3 (63 s, 5,5 h) gastó **~7 % de su uso semanal de Claude**: a 25–40 s se estima ~4–5 % por video, o sea ~30–35 % a la semana con uno diario. Le cabe (21:15).
**Fase actual: 0, puesta a punto.** Ver la checklist en `docs/AUTOMATIZACION.md`.

- **Proceso v2 (21-oct-2026, después del Ep. 2 — "NO SE PUEDE VOLVER A REPETIR", Tomás):** el Ep. 2 tomó más de 24 h y ~26 % del uso semanal de Claude de Tomás (medido en la bitácora: 22,7 h activas, 20 rondas del auditor, 35 revisores, 337 imágenes revisadas, ~45 escenas animadas una por una). Ahora: videos de **62–65 s**; **storyboard = fichas de plano** con lo que exige el auditor escrito antes de animar; **máx. 12 escenas** y algo que cambia cada 1–2 s; **`tools/prueba.py`** por plano (render chico + post + chequeo automático de ojos tapados, quemado, vacío y fondo liso, ~1,5–2 min; lo quieto se mide en el animatic); **animatic** auditado antes de un **solo render final**; auditor sin rondas por fallas medibles, **bloqueantes de lista cerrada**, **5 sugerencias**, **promedio ≥ 8 y ninguna nota bajo 7**, **máx. 2 rondas** (la 2.ª verifica) y 1 revisor por cada 10 planos + 1 global; **topes por video** en `tools/auditor/presupuesto.json` (los lee el código). Una auditoría independiente del mismo 21-oct encontró 20 errores en la primera versión (lección 50) y se corrigieron. **El kit es todavía un catálogo de código del Ep. 2, no plantillas programadas**, y el ahorro no está medido: se mide en el Ep. 3.

- **Estilo vigente: REALISTA, el del Ep. 5** (Tomás, 23-oct-2026 18:09: "el estilo de video y de edición que más me ha gustado; seguir esta línea"). "Realista pero en un mundo animado" (calidad Zack D. Films; nunca fotorrealismo de IA). **Receta: `docs/ESTILO_REALISTA.md`**; se parte del kit del Ep. 5 (`studio/episodios/ep05-iman-rana/escena/`) y cada episodio nuevo copia `studio/plantilla/estilo_realista.json`. El auditor tiene modo realista ajustado a esto (`docs/AUDITOR.md` → "El auditor realista"). Antes: semi-realista con Mixamo y personaje propio (Ep. 1–4, animado).
- **Auditor por etapas (19-oct; v2 desde el 21-oct, ver arriba):** `docs/AUDITOR.md` + `tools/auditor/`. Corre como subagentes (gratis) y a Tomás le llegan sólo los cuadros de estilo nuevos y el video final ya aprobados. Calibrado a ciegas con las versiones viejas del Ep. 1 (20 de 22 errores conocidos, con el auditor v1; el v2 no está recalibrado) y el chequeo automático con el Ep. 2 (`docs/AUDITOR_CALIBRACION.md`). Obligatorio, junto con la bitácora del proceso.
- **Interior del cuerpo ("cabeza de vidrio"), aprobado por Tomás el 19-oct:** perfil fijo, fondo azul noche, anatomía real de Z-Anatomy; se ve y brilla sólo lo que nombra la voz. Reglas en el manual §8.
- **Manos con objetos y reacciones → Kling** (API oficial, secreto `KILING_SECRET`, workflow `kling.yml`). En Blender los dedos flotaban; Tomás lo rechazó dos veces. Kling parte de cuadros nuestros y no se usa para anatomía.
- **Render en GPU → RunPod** (secreto `RUNPOD_API_KEY`, workflow `render-gpu.yml`). Probado el 19-oct: RTX A5000, ~1,4 s por cuadro a 720p/16 muestras, el pod se borra solo.
- **Proceso:** cada etapa pasa una puerta del **auditor** (`docs/AUDITOR.md`) antes de avanzar: guion → voz → storyboard (fichas) → cuadros (sólo escenarios nuevos; van a Tomás ya aprobados) → Kling → animatic → final → paquete, más el proceso (bitácora y topes). A Tomás le llegan sólo los cuadros de estilo de escenarios nuevos y el video final, los dos con APROBADO. Claude revisa su trabajo antes de mostrarlo y vigila cada 15 min lo que corre en paralelo (el 19-oct dos trabajos en paralelo murieron una hora sin que nadie lo notara).
- **Estudio de referencias virales:** `docs/REFERENCIAS.md` (Tomás sigue mandando videos).
- **Protagonista:** `studio/personaje/` (MakeHuman CC0 + esqueleto `mixamorig:*`, 34 shape keys de expresión).
- **Ep. 1 — Congelamiento cerebral (helado):** guion v2 con fuentes, voz de 71,7 s, escena `escena/build_ep01.py`, post `escena/post.py`, audio `escena/audio.py`, clips de Kling en `kling/`, textos en `entrega/caption.md`. Estado de la entrega: ver el final de esta sección.
- **Mixamo (referencia):**
  - **Dónde van las FBX:** repo **privado** `nadieteexplica/assets`, carpeta `mixamo/`. El render los clona con el secreto `TOKEN` (token fino "render" de la organización, solo lectura de ese repo, vence el 17-nov-2026: hay que renovarlo). Nunca van al repo público.
  - Configuración: FBX Binary, 30 fps, keyframe reduction none, y "In Place" marcado cuando exista.
  - **Animaciones en Without Skin** (elegidas mirando el catálogo el 18-oct; nombre de búsqueda → descripción en Mixamo):
    - Ep. 1 y base de la biblioteca:
      - `Drinking` → "Male Drinking" (se lleva el helado a la boca; también "toma algo tibio"),
      - `Focus` → "Shake Off Head Pain And Focus" (manos a la cabeza: el "¡zas!"),
      - `Thinking` → "Thinking While Standing",
      - `Shrugging` → "Shoulder Shrug",
      - `Arm Gesture` → "Gesturing With Arm To The Side" (presenta el corte de la cabeza),
      - `Pointing` → "Pointing With Arm Bent",
      - `Talking` → "General Conversation" y "Asking A Question With Two Hands",
      - `Surprised` → "Finding Something And Wiggling Fingers" ("y lo más loco"),
      - `Head Nod Yes` → "Nodding Head Yes" ("sí, en serio"),
      - `Relieved Sigh` → "Sighing In Relief" (cuando se pasa el dolor),
      - `Shaking Head No` → "Shaking Head No Dismissively",
      - `Laughing` → "Laughing Standing" (cierre),
      - `Happy Idle` → "Happy Idle Variation 1" (entre planos).
    - Para otros episodios: `Terrified` ("Being Terrified While Standing") y `Excited` ("Super Excited").
    - Descartadas: `Agony` (demasiado dramática).
- **Ep. 2 — "Los pájaros no sienten el picante" (sale el 21-oct: IG 10:00, YouTube 16:00, TikTok 18:00; `studio/episodios/ep02-pajaros-picante/`):**
  - Concepto hecho para la idea (decisión de Tomás): comedia 3D de dibujo animado **sin humanos**, en el desierto de Arizona; el ratón hace de "tú" (mamíferos) y el cierre lo manda al que se cree inmune. Personajes propios en `ficha.jpg` (cuitlacoche, ratón del cactus, rata, tupaya, ají guardia), todos procedurales (`escena/personajes.py`), sin modelos externos.
  - Puertas: **guion APROBADO (r2)** · **voz APROBADO (r2**, 73,6 s; pausas ajustadas con `tools/pausas.py`, 0 créditos extra) · **storyboard APROBADO (r3**, 40 planos, **0 clips de Kling**: todo render para que la llama y los personajes sean siempre los mismos).
  - **Puerta 4 (cuadros de estilo): APROBADO el 20-oct a las 17:20** (ciclo 3, r3; belleza 8, personaje 9, manos 9, anatomía 8; 6 detalles de prioridad 3 para la animación). Tres ciclos de 3 rondas: c1 (bosque v1, se rediseñó por decisión de Tomás), c2 (9 arreglos pendientes, Tomás eligió un ciclo más), c3. Archivados en `auditoria/4-cuadros-ciclo1/` y `-ciclo2/`. Tomás dio el OK para animar (20-oct 18:01).
  - **Animación (20–21 oct):** sistema por planos (`escena/plano.py`, `planos_ep02.py`, `post.py`, `audio.py`; workflow `render-planos.yml` con varios runs base y piezas partidas). Primer borrador 21:34; revisión propia → 7 planos rehechos.
  - **Publicación: Tomás aprobó el borrador que vio y pidió que saliera sí o sí a las mejores horas** (`docs/HORARIOS.md`): programado el 20-oct 22:48 para el **21-oct** → Instagram 10:00, YouTube 16:00, TikTok 18:00 (Metricool 401677198 / 401677452 / 401677487; MP4 en el Release `ep02`). Ese borrador NO pasó la puerta 6.
  - **Puerta 6: NO APROBADO en 3 rondas** (r1 76 observaciones → r2 notas 7–8 → r3 global 8–9 con 1 bloqueante; tramo 1 APROBADO). Bloqueantes de la r3: lupa que tapa el ojo del pájaro en 14–16 (al re-encuadrar el 14 la cabeza quedó bajo la lupa), hojas del brote que flotan en 25, brazo del ratón visto a través del vaso en 34. Versión r3: run 39559543358 (prerelease `ep02-borrador`). A las 06:10 del 21-oct se le dieron a Tomás 3 opciones: A ciclo nuevo con esos arreglos (recomendado) y cambiar YouTube/TikTok si aprueba antes de las 15:00; B cambiar ya a la r3; C dejar lo programado y pasar al Ep. 3. **07:51: Tomás eligió B** ("me gustó más ese"): a las 07:53 se cambió el video de los 3 posts por la r3 (`ep02-pajaros-picante-v3.mp4`, Release `ep02`), mismos textos y horas (Metricool 402005009 / 402005097 / 402005197).
- **Ep. 1 publicado** el 19-oct-2026 a las 16:35 en Instagram, TikTok y YouTube (links en `docs/PUBLICADOS.md`). Métricas a las 48 h (21-oct) y a los 7 días (26-oct).
- **Próximos pasos:**
  1. ~~Auditor por etapas~~: listo el 19-oct (`docs/AUDITOR.md`, `tools/auditor/`, calibración en `docs/AUDITOR_CALIBRACION.md`).
  2. Biblioteca de reacciones del protagonista con Kling (una vez; después se reusa sin gastar unidades).
  3. RunPod con 2–3 pods en paralelo (video completo en ~20–30 min).
  4. ~~Ep. 2~~: programado el 21-oct (versión r3, decisión de Tomás); confirmar en Metricool que quedó "Published". Métricas a las 48 h el 23-oct; comparar lo que dijo el auditor con lo que rindió.
  5. **Ep. 3 = "El edificio que caminó"** (`studio/episodios/ep03-edificio-que-camino/`, primer video con el proceso v2): **terminado el 21-oct a las 19:35 en 5,5 h** (tope 8 h). Puertas: guion, voz (63,4 s, 16 pausas), storyboard (36 planos, 9 escenas), cuadros de estilo (r2, 8,5; look con OK de Tomás 16:45), animatic (r1 NO: 2 bloqueantes; r2 APROBADO 8,38 sobre el render final), final (sin bloqueantes), paquete (8,0); **proceso NO APROBADO** por la bitácora (lección 61). Render final: run 39672294640 (16 máquinas, 86 min + 12 de armado; 2,5× el animatic), prerelease `ep03-borrador`. Textos en `entrega/caption.md`, portada en `entrega/portada.jpg`. **Programado con OK de Tomás (20:57) para el jueves 22-oct a las 10:00 en las 3 redes** (Metricool 402735806 / 402735854 / 402735900, textos ya con #elviejodeldato; MP4 en el Release `ep03`). Confirmar después de las 10:00 que quedó "Published". Medido para ajustar topes: muestras ~4 min, animatic 50 min, final ~100 min; 2 rondas por puerta alcanzaron.
  6. ~~Tareas programadas~~: la de producción la eliminó Tomás (21-oct): los videos se piden en el chat. La revisión de métricas, sólo si él la pide.
  7. **Ep. 4 = "La cortina de la ducha te persigue"** (`studio/episodios/ep04-cortina-ducha/`, primer video corto de YouTube primero, 35,7 s, 97 palabras): pedido por Tomás el 21-oct a las 23:28 y hecho de noche. Estudio previo en `docs/estudios/ep04.md` (sólo el Ep. 1 tenía métricas; Chrome no conectado, sin YouTube Studio). Personaje nuevo **Don Héctor** (MakeHuman CC0, `escena/pj/hector.blend`; de los hombros para arriba, máscara bajo el pecho y espuma: nada de desnudos). 3 escenas a medida: E1 ducha, E2 corte (la cortina se vuelve transparente y se ve el remolino acostado, eje perpendicular a la cortina según Schmidt en Scientific American), E3 cortina pesada. Puertas: guion r1, voz r1, storyboard r2 (r1: eje del remolino), cuadros r2 (r1: agua rosada; look lavado corregido), animatic r1 NO (3 bloqueantes; 2 ya arreglados en el final) → **parche** de los planos 3–5 sobre el final (lección 68) → animatic r2 (verificación sobre el final parchado) **NO: 1 bloqueante en el 17 (espalda 0,15 s y cortina que cae de golpe) y promedio 7,88** (gancho 7: el primer segundo es él tranquilo) → el 17 se simplificó (sin personaje, la cortina baja pareja) en un 2.º parche; **final APROBADO (puerta 7, 0 bloqueantes)**; **paquete APROBADO (8,5)**; **proceso NO** (bitácora sin chequeos de 15 min en la sesión y los revisores, y 5 h de 4: lección 73), con las 3 sugerencias del paquete aplicadas ("efecto cortina de ducha", pedir el envío, fuente NASW). Render final: run 39722863780 (12 máquinas, 8 muestras) + parches 39726712487 (3–5) y 39756380402 (17), prerelease `ep04-borrador`; portada en 3,7 s (`entrega/portada.jpg`). Desvíos: render final a **8 muestras** (16 no cabía en 4 h), 2 animatics cancelados a los 7–10 min (lección 67), la r2 de la puerta 6 se hizo sobre el final parchado. Tiempo: **~5 h** (23:28–03:43 y 06:23–~07:15; meta 2,5 h, **tope 4 h pasado por ~1 h**). Se paró a las 03:15 y se le dieron opciones a Tomás; a las 06:23 preguntó si estaba listo y se cerró. Lo que más costó: el render final (la máquina de los planos 13–14 tardó ~2 h, el doble de lo estimado) y los arreglos de la puerta 6 después del final. Textos en `entrega/caption.md`, **programado con OK de Tomás (22-oct 07:23) para el viernes 23-oct: IG 10:00 · TikTok 10:00 · YouTube 16:00** (Metricool 403001164 / 403001266 / 403001408; MP4 en el Release `ep04`). Confirmar después que quedó "Published". A Tomás le gustó mucho (ver "Aprendizajes").

  8. **Ep. 5 = "El imán que hace flotar a una rana"** (`studio/episodios/ep05-iman-rana/`, primer video **realista**: "realista pero en un mundo animado", calidad Zack D. Films; pedido el 22-oct 23:16, hecho de noche y en la mañana del 23). Guion v2.1 (8,25; 119 palabras), voz (41,4 s tras `pausas.py`), storyboard r2 (18 planos, 5 escenas: E1 rana en el tubo del imán en un salar de Atacama al atardecer, E2 adentro hasta el agua, E3 refri, E4 imán gigante + central nuclear, E5 Pete de Mixamo flotando; SIMULACIÓN fija en 12–17). Rana = escaneo real CC-BY; Pete = Mixamo desde el Release privado `Personajes`. **Puerta 4 (cuadros): NO en r1 y r2 (realismo 7)** → se paró (regla de Tomás) y a las 06:24 Tomás dijo "sí, sigue con todo" → **r3 forzada: realismo 8** (1 bloqueante de una pluma de vapor, arreglado). Animatic (50 min): 2 fallas automáticas + 6 planos arreglados en revisión propia; para llegar se lanzó el **final con los arreglos (720×1280/8, 16 máquinas, ~60 min)** y la **puerta 6 se hizo sobre el final: APROBADO 8,0** (0 bloqueantes; gancho y animación 7) tras un parche del plano 4. Se le agregó la píldora EN EL AIRE desde el cuadro 0 (sugerencia de la puerta 6). El armado de Actions se colgó 3 veces en apt-get: nuevo `armar.yml` (lección 92). Tiempo total ~9 h (tope 4 h; Tomás pidió seguir). Textos en `entrega/caption.md`, portada en `entrega/portada.jpg`. Estudio en `docs/estudios/ep05.md`. **Puertas 7 y 8 APROBADO**; video mandado a Tomás el 23-oct ~10:40 (MP4 en la prerelease `ep05-borrador`). **Programado con OK de Tomás (23-oct 18:19) para el sábado 24-oct: IG 10:00 · TikTok 18:00 · YouTube 20:30** (Metricool 404575035 / 404575043 / 404575057; MP4 en el Release `ep05`). Confirmar después que quedó "Published". A las 18:09 Tomás dijo que es el estilo que más le ha gustado y que se siga esta línea (ver "Estilo vigente"). **v3 (23-oct 21:20 → 24-oct ~01:30, pedido de Tomás):**
     - **Por qué:** "la idea de que el humano puede flotar se entiende recién al segundo 25, mucho chamullo". Además, sin el refri y con más construcción del imán.
     - **Guion nuevo** (105 palabras, 38,8 s): "Tu cuerpo repele los imanes. Con el imán correcto, podrías flotar…", con la rana como prueba real y la construcción en 3 pasos (el hueco, las bobinas y el reactor). Puertas 1 (8,25), 2 (8,5) y 3 (r2: 8,25).
     - **Video:** 16 planos y 4 escenas. Pete flota desde el cuadro 0 con SIMULACIÓN; hay una mano a escala junto al hueco de 3,2 cm; caen 5 bobinas de cobre; barras de 16 T contra 40 T; Pete actúa con gestos de Mixamo.
     - **Final v3.0:** la puerta 6 r1 dio 7,96 (realismo 7 por un hueco negro liso y una losa lisa; animación 7 porque Pete no actuaba). La puerta 7 lo aprobó.
     - **Re-render v3.1** con todo arreglado (lecciones 96–101).
     - **Programación:** Tomás pidió (24-oct 00:21) Instagram a las 10:00, TikTok a las 18:00 y YouTube a las 20:30 del sábado 24-oct con el video nuevo, eliminando el anterior. Se cambiaron el video y los textos en los 3 posts ya programados (24-oct 01:38; Metricool 404764457 / 404764617 / 404764622). Las puertas 6 r2 (8,26) y 8 r2 (8,5) dieron APROBADO.
     - **Archivos:** el MP4 es `ep05-iman-rana-v3.mp4` en el Release `ep05`; los textos están en `entrega/caption.md`.
  9. **Ep. 6 = "El cinturón que se traba" — VERGÜENZA MÁXIMA (Tomás, 24-oct 08:17)**: "el peor video que he visto en mi vida": música mala, guion pésimo, edición pésima, escenas pegadas, no se entendió nada; ~7,6 h y muchos tokens. No se publica. La puerta 6 nunca lo aprobó (7,71, realismo 7) y aun así se le mandó: error grave. Análisis y reglas nuevas en la lección 109 (ver el video entero corrido antes de mostrarlo, plano de situación en 3 s, ≤12 planos, un NO de calidad no llega a Tomás, tope de 4 h duro, música real con licencia). Archivos en `studio/episodios/ep06-cinturon-traba/` (MP4 sólo en la prerelease `ep06-borrador`).

- **Ronda 6 de ideas: mecánicas (23-oct-2026, 19:00):** Tomás cree que el edificio rindió por mostrar la mecánica y pidió ideas de "cómo funciona / cómo se hizo / cómo se hace". 12 ideas puntuadas + reserva en `docs/IDEAS.md` (fuentes ubicadas, cifras por verificar; vidIQ sin créditos hasta el 18-nov). Recomendadas para la próxima sesión: el rascacielos que se encoge y el touch con salchicha. Esperando 👍/👎.
- **Métricas al 22-oct ~20:00 (Studio y TikTok Studio, en `PUBLICADOS.md`):** el Ep. 3 (edificio) explotó en TikTok (118 mil) e Instagram (63,2 mil) y en YouTube quedó en 1.483. En YouTube los tres Shorts reciben una tanda de ~1.200–1.500 vistas y se frenan; el Ep. 1 tuvo una 2.ª tanda al día 2 (4.003 en total). El video no es el problema: 73–78 % no lo desliza, 0:32–0:42 de vista promedio, 93–97 % viene del feed de Shorts. Hipótesis principal: el largo (64–74 s; en el Ep. 1 a los 30 s queda el 46 %); el Ep. 4 (35,7 s) es la prueba. Público de YouTube: sobre todo México, después Argentina, Colombia, Perú y Guatemala. Horario: revisión en `docs/HORARIOS.md` (propuesta de alternar 20:30 y 16:00, pendiente de Tomás). Ojo: Instagram es @el_viejo_del_dato y el nombre visible de TikTok sigue siendo "Nadie te explica"; el canal de YouTube está en otra cuenta de Google en el Chrome de Tomás (selector de canales).

## Decisiones pendientes de Tomás
1. ~~Estilo~~: decidido el 18-oct (semi-realista con Mixamo, personaje propio de cuerpo normal, ~18–20 años); **cambiado el 23-oct al realista del Ep. 5** (`docs/ESTILO_REALISTA.md`).
2. ~~Audiencia de YouTube (`madeForKids`)~~: decidido el 19-oct → **no es para niños**.
3. ~~Repo privado de assets y token~~: listo el 18-oct (`nadieteexplica/assets` + secreto `TOKEN`). **Renovar el token antes del 17-nov-2026.**
4. **Pegar `proyecto/INSTRUCCIONES.md` en las instrucciones del proyecto en Claude** (las de ahí todavía dicen 62–75 s, todas las notas ≥ 8 y 3 rondas). Se le mandó el archivo el 21-oct.
5. ~~Producción automática~~: **decidido por Tomás el 21-oct-2026: no hay tarea programada de producción.** Él pide cada video en el chat; uno o dos videos por sesión (desde el 21-oct, YouTube primero).
6. **Proporción datos/historias.** Propuesta de Claude: ~2 de datos por cada historia en el piloto; a las 4 semanas se ajusta según envíos/alcance de cada línea.
7. **Sumar Facebook como 4.ª red** (es el mismo video y Facebook paga por vistas en Chile, por invitación). Necesita que Tomás cree una página de Facebook y la conecte a Metricool. Preguntado el 21-oct.
8. ~~Ep. 5 después de la puerta 4~~: Tomás eligió seguir (23-oct 06:24, "sí, sigue con todo").
9. **Formato de mecánica (23-oct-2026):** Tomás quiere un estilo propio para explicar cómo funciona o cómo se hace algo (no copiar la cadena de problemas de la piscina). Propuesta de Claude: "El reloj" (recomendado) o "Sácale una pieza" (`docs/REFERENCIAS.md` §5).
10. **Biblioteca realista (23-oct-2026, pedido de Tomás):** base de assets para el realista. Plan, licencias y lista de Mixamo para Tomás en `docs/BIBLIOTECA.md`. Pendiente de Tomás: bajar la lista de Mixamo (a mano, no con el script) y decidir si se prueba MetaHuman (instalar Unreal) después de leer su contrato.

## Aprendizajes
(Se llenan con los datos de cada semana. Ver `docs/PUBLICADOS.md`.)
- Antes de publicar, los aprendizajes vienen de videos ajenos: `docs/REFERENCIAS.md` §3. Se confirman o se descartan con nuestros datos.
- **Lo que Tomás destacó (Ep. 4, 22-oct-2026, "anótalo"):** meterse **dentro** de lo que se explica (la ducha en corte, con la cortina que se vuelve transparente) y explicar todo **visualmente**: el remolino girando como rueda, la baja presión en el centro y el aire de afuera empujando, cada cosa dibujada en el momento en que la voz la nombra. Es la forma de explicar la mecánica a mitad de video que se busca en cada episodio de datos.
- **El relato (Tomás, 23-oct-2026, sobre el Ep. 5):** le gustó el video, no el relato: lo más interesante (que una persona podría flotar en un imán enorme) no fue el centro y no enganchaba de una. Desde el Ep. 6 hay **torneo de guiones**: 4 guiones de verdad distintos + simulación rápida de espectadores, y gana el que más retiene y el más chistoso (lección 95).
- **Errores de producción y sus reglas: `docs/LECCIONES.md`** (se lee antes de cada video). Del Ep. 1: interior "cabeza de vidrio" con un solo foco; manos con objetos → Kling partiendo con la mano libre; nunca mostrarle nada a Tomás sin revisión propia; horas solo con datos medidos; revisar cada 15 min lo que corre en paralelo.

## Documentos
- `proyecto/INSTRUCCIONES.md`: instrucciones del proyecto en Claude.
- `docs/BIBLIOTECA.md`: biblioteca de assets del estilo realista (fuentes gratis, licencias, qué baja Claude y qué baja Tomás, lista de Mixamo).
- `docs/YOUTUBE.md`: YouTube primero (21-oct-2026): algoritmo de Shorts, YPP 2027, frecuencia, duración, política de contenido no auténtico y plan.
- `docs/LECCIONES.md`: errores de producción, cómo se solucionaron y la regla que queda (leer antes de cada video).
- `docs/AUDITOR.md`: el auditor independiente por etapas (puertas, chequeos, bloqueantes, formato del veredicto, bitácora del proceso). Código y prompts en `tools/auditor/`.
- `docs/AUDITOR_CALIBRACION.md`: el auditor corrido a ciegas sobre las versiones del Ep. 1 y qué errores detectó.
- `docs/MANUAL_PRODUCCION.md`: estándar de cada video (guion, verificación, voz, storyboard, look, subtítulos, audio, render, QA, entrega, publicación).
- `docs/AUTOMATIZACION.md`: cadencia, fases, topes por video, cómo se hace un video (a pedido) y manejo de fallas.
- `docs/IDEAS.md`: dónde buscar, puntaje, lista negra y banco de ideas.
- `docs/CAZA_DATOS.md`: método del chat de caza de datos (qué buscamos, familias, métodos, dónde verificar, datos quemados, ángulos y gustos de Tomás).
- `docs/PUBLICADOS.md`: registro de videos y métricas.
- `docs/REFERENCIAS.md`: estudio de videos virales de referencia (por qué funcionan, qué tomar, qué tan alcanzable). Documento vivo.
- `docs/investigacion-formatos-virales.md`: investigación de formatos virales. **Es histórica**: sus datos de plataformas sirven, pero sus propuestas (noticiero low-poly, publicar diario) **no están vigentes**.
- `docs/banco-ideas-antiguo.md`: banco viejo, de la época low-poly.
