# Calibración del auditor con el Ep. 1 (19-oct-2026)

**Pregunta:** si el auditor hubiera existido durante el Ep. 1, ¿habría pescado los errores que terminó encontrando Tomás?

## Cómo se hizo
- **Material:** las versiones reales del Ep. 1, recuperadas de GitHub:
  - **v3** (render de las 11:39 del 19-oct, run 39254716198) y **v3.1** (12:17, run 39267362199): el interior viejo y los objetos en la mano hechos con Blender. Se trajeron con `traer-artefacto.yml` a la prerelease `calibracion`.
  - **publicado** (Release `ep01`).
  - los **12 clips de Kling** (prerelease `ep01-kling`), incluidos los descartados, y sus **9 cuadros de partida**.
  - el guion, el storyboard, la voz y `caption.md` del repo, el pedido de Kling rechazado (sacado de git) y los runs de Actions del 18 y 19-oct.
- **A ciegas:** cada revisor recibió sólo sus materiales y las reglas. Nadie le dijo qué versión era, qué errores tenía ni dónde. La carpeta se llama `historico/`, no "calibración". La verdad de referencia (`tools/auditor/calibracion.json`) se escribió **antes** de leer los veredictos.
- **Qué cuenta como detectado:** un problema del revisor (o una falla automática) en el plano o clip correcto, en el segundo correcto cuando aplica, que describe el error. Lo mide `tools/auditor/calibrar.py`.
- **Lo justo de decir:** las reglas del auditor salen de `LECCIONES.md`, así que conoce **los tipos** de error (dedos que flotan, cosas que aparecen de golpe, interior confuso). La prueba es si encuentra **las instancias**, en qué plano y segundo, sin que nadie le diga dónde están.

## Resultado: 20 de 22

Detectados por el auditor, con el plano y el segundo (de `calibrar.py`; cuenta sólo si lo marcó como bloqueante o prioridad 1):

| caso | lección | error conocido | dónde se auditó | detectado | menciones | ejemplo |
|---|---|---|---|---|---|---|
| L1-v3 | #1 | interior de la cabeza confuso (cráneo, ojos de caricatura, cortes) | v3 · 6-video r1 | ✅ | 16 | plano 13 · 24.66 s — Interior con cráneo completo a la vista (dientes, mandíbula, órbitas) y ojos saltones que sobresalen del hueso |
| L1-v31 | #1 | interior de la cabeza confuso | v31 · 6-video r1 | ✅ | 11 | plano 13 · 24.66 s — Aparece el cráneo completo con la bóveda cortada a la altura de las cejas: el cerebro queda apoyado sobre un c |
| L1-sb | #1 | el storyboard ya planeaba el interior con corte y cráneo | ep01 · 3-storyboard r1 | ✅ | 7 | plano 4 · 4.17–6.62 s — 'Entramos por la frente… un copo de nieve rebota en el cráneo' con dolly frontal: se ve el cráneo y la entrada |
| L2-v3 | #2 | objetos que flotan o atraviesan la mano (cono, vaso, taza) | v3 · 6-video r1 | ✅ | 8 | plano 18 · 39.02 s — El brazo del voluntario salta de la mejilla a la cintura en ~4 cuadros (entre 39.02 y 39.14, E30) y la bombill |
| L2-v31 | #2 | objetos que flotan o atraviesan la mano | v31 · 6-video r1 | ✅ | 4 | plano 18 · 37.94 s — El vaso está pegado a la mejilla o mandíbula y no a la boca (37,94, 38,48 y 39,02; lo mismo en P17 a 37,43 y 3 |
| L2-sb | #2 | el storyboard ya pedía 8 planos de manos con objetos en Blender | ep01 · 3-storyboard r1 | ✅ | 1 | plano 3 · 2.83–4.17 (también 0.00–1.94, 9.86–14.98, 33.65–35.65, 37.90–40.69, 60.55–62.50, 68.42–71.66) s — 8 planos con manos y objetos o manos a la cara (1 muerde el cono, 3 `Focus` con las manos a la cabeza, 8 el co |
| L3-kling | #3 | Kling copia el agarre malo de la taza | ep01 · 5-kling r2 | ✅ | 8 | plano p26_taza_a + p26_taza_b (cuadro de partida) · 0,0 s s — el cuadro de partida ya trae la taza agarrada en pinza (índice bajo la base, dedos delante del cuerpo, asa lib |
| L3-cuadro | #3 | el cuadro de partida de la taza trae el agarre malo | ep01 · 4-cuadros r1 | ✅ | 1 | plano 26 · 0.00 s — p26_inicio: la taza no está agarrada. Dos dedos quedan por delante del cuerpo de la taza y la punta del índice |
| L4-kling | #4 | los vasos pasan de negros a transparentes a mitad del clip | ep01 · 5-kling r2 | ✅ | 2 | plano p17_vasos_a · 2,1–2,8 s s — los vasos cambian de color y de material: de 0,0 a 2,1 s son negros, con un líquido oscuro que se lee como beb |
| L4-cuadro | #4 | el cuadro de partida muestra los vasos negros | ep01 · 4-cuadros r1 | ✅ | 1 | plano 17 · 0.00 s — Los vasos de 'agua helada' no se ven como agua helada. En p17_inicio el vaso es casi negro con un bloque blanc |
| L6-v3 | #6 | el cono aparece de golpe en la mano al final del plano 8 | v3 · 6-video r1 | ✅ | 1 | plano 8 · 11.63 s — El cono con 3 bochas aparece de la nada en la mano derecha (E7: mano vacía en 11.54, cono completo en 11.74) s |
| L6-v31 | #6 | el cono aparece de golpe en la mano al final del plano 8 | v31 · 6-video r1 | ✅ | 1 | plano 8 · 11.63 s — El cono de 3 bolas aparece de golpe en la mano derecha (E7): en 11.54 la mano cuelga vacía, en 11.63 hay un co |
| N1-v3 | nuevo | pantalla vacía 52,9–53,5 s (nadie la vio; también está en el publicado) | v3 · 6-video r1 | ✅ | 3 | plano 23 · 52.89 s — Pantalla vacía de 52.85 a 53.53 (0,66 s, E41): sólo hay fondo azul liso y el subtítulo 'SU NOMBRE CIENTÍFICO'  |
| N1-final | nuevo | pantalla vacía 52,9–53,5 s en el video publicado | final · 6-video r1 | ✅ | 2 | plano 23 · 52.89 s — Pantalla vacía de 52.87 a 53.53 (0,66 s, E44). A 52.89 sólo se ve el fondo turquesa liso con el subtítulo SU N |
| L5 | #5 | instrucción de Kling con 'sharp pain' / 'teeth clenched' (Kling la rechazó) | git · pedido viejo chequeo | ✅ | 2 |  — p3_dolor_a: la instrucción usa 'pain' (Kling rechaza el clip por 'risk control'; usar 'funny brain freeze', et |
| L15 | #15 | más de 16 máquinas de Actions a la vez (bloqueó Kling) | ep01 · P-proceso r1 | ✅ | 1 |  — 40 máquinas de Actions corriendo a la vez a las 22:45 (máx. 16: deja 4 libres para Kling y RunPod) 18-10 22:45 |
| L20 | #20 | 8 planos de Kling en un video (46 unidades) | ep01 · 5-kling r2 | ✅ | 1 |  — 8 planos del video salen de Kling [1, 3, 9, 17, 18, 26, 30, 33] (máximo 3)  |
| L23 | #23 | TikTok sin título (Metricool lo rechaza) | ep01 · 7-paquete r1 | ✅ | 1 |  — falta tiktokData.title (Metricool rechaza TikTok sin título)  |
| N2 | nuevo | caption.md del repo con madeForKids 'pendiente' (no es lo que se publicó) | ep01 · 7-paquete r1 | ✅ | 1 |  — madeForKids no está en 'no' (decidido por Tomás el 19-oct) madeforkids`: **pendiente de tomas**, `isaigenerate |
| N3-final | nuevo | publicado, plano 1 (Kling): la cara cambia (ojos de caricatura, otra cara) a 1,5–1,9 s | final · 6-video r1 | ❌ | 0 |   |
| N4-final | nuevo | publicado, plano 9 (Kling): la cara del protagonista cambia de estilo | final · 6-video r1 | ❌ | 0 |   |
| N5-final | nuevo | publicado, plano 17 (Kling): los vasos pasan de blancos opacos a transparentes | final · 6-video r1 | ✅ | 1 | plano 17 · 36.99 s — Los vasos de todos los voluntarios cambian de golpe. Entre 35.69 y 36.56 son cilindros blancos opacos; desde 3 |

**20/22 detectados.**

**Lo importante:**
- **Los errores de imagen que encontró Tomás aparecen todos**, y en dos versiones distintas (v3 y v3.1, revisadas por revisores distintos, con el mismo resultado):
  - el interior confuso,
  - los objetos sin agarrar,
  - el cono que aparece de golpe (plano 8, 11,63 s, gracias al detector de apariciones),
  - los vasos que cambian de material,
  - el agarre de la taza que Kling copia del cuadro de partida.
- **El storyboard ya los habría frenado antes de gastar:** la puerta 3 rechaza el storyboard del Ep. 1 por el interior con corte y cráneo, y por los 8 planos con manos y objetos en render.
- **La v3 pasaba el QA automático completo** (`qa.txt`: PASA). Sin el auditor, ese video habría llegado igual a Tomás.

**Los 2 que no pasaron**, planos 1 y 9 del publicado: en los clips de Kling la cara del protagonista cambia (ojos más grandes, otras cejas). La puerta 5 (Kling) sí los rechazó como bloqueantes. El revisor del video final también lo vio, pero lo anotó como prioridad 2 ("la cara cambia entre render y Kling"), no como bloqueante.
- **Ajuste hecho:** el revisor por tramo ahora recibe la ficha del personaje y tiene la regla explícita de que una cara distinta es bloqueante, aunque parezca el mismo personaje en otro estilo.
- **Pendiente:** se comprueba con el Ep. 2. No se volvió a correr sobre el publicado, porque ya está subido y no hay nada que arreglar ahí.

## Controles (que no invente errores)
- **Voz:** la ronda 1 dijo que los "..." casi no hacían pausa (0,12 s), y era falso: la alineación de ElevenLabs mete el silencio dentro de la palabra.
  - **Ajuste:** `voz.md` ahora lleva el silencio real medido en el audio.
  - **Ronda 2:** APROBADO (pronunciación 9, ritmo 8). La transcripción automática coincide en 0,99 con el guion.
- **Kling, tramo usable:** en la ronda 1 el revisor rechazaba el clip entero por un defecto en cualquier cuadro.
  - **Ajuste:** ahora define el tramo usable de cada clip y sólo es bloqueante lo que cae dentro.
  - **Resultado:** p26_taza_d sirve de 0,0 a 3,2 s y p26_taza_e de 0,0 a 4,6 s, y la regla igual detecta que el plano 17 publicado usó el tramo donde cambian los vasos.
- **Detectores:** la pantalla vacía no tuvo falsos positivos en 3 videos. El de apariciones marca entre 40 y 55 eventos por video y los revisores descartaron la gran mayoría (etiquetas que entran a propósito, acciones rápidas). Es ruidoso a propósito, para no perder un cono.

## Ajustes que salieron de la calibración
| Problema | Ajuste |
|---|---|
| El detector de apariciones no veía el cono (lo tapaba el movimiento de cámara) | Flujo óptico: lo que el movimiento no explica es una aparición |
| La cara distinta en planos de Kling quedó como prioridad 2 | Ficha del personaje en cada tramo y regla explícita de bloqueante |
| Pausas de la voz mal medidas | Silencio real con `silencedetect` |
| Clips de Kling rechazados enteros | Tramo usable por clip + chequeo contra `kling/planos.json` (`desde`, `velocidad`, `dur`) |
| "Material insuficiente" para ver dedos en planos generales | Zoom automático donde hay movimiento (`*_detalle.jpg`) |
| WebFetch bloqueado por permisos al verificar fuentes | El guion se verifica primero con WebSearch (ronda 2: precisión 8, cifras confirmadas) |
| El chequeo de instrucciones de Kling llegaba tarde (después de gastar) | Se revisan en la puerta 4, junto con el cuadro de partida |

## Lo que la calibración no puede probar
- **Errores de proceso** (#13 trabajos muertos, #14 horas prometidas): no quedó registro. Desde el Ep. 2 los controla la bitácora; el auditor de proceso se probó con una bitácora de prueba y detecta promesas sin dato, atrasos sin aviso, huecos de más de 15 min y gasto sobre el tope.
- **#7–#10** (domo que desaparece, luces que se apagan, vuelta larga de cámara, lengua que se mueve al lado) ocurrieron en renders de prueba que no se guardaron como video. Los cubren el detector de apariciones, el de cambios de luz y la regla del interior, pero no hay video con qué probarlos.
- El revisor **no escucha** el audio: la pronunciación depende de la transcripción automática.

## Costo y tiempo medidos
- Cada revisor tardó **4–27 min** (mediana ~11 min) y no cuesta plata: corre como subagente en la sesión.
- Preparar los materiales de un video de 72 s toma ~2 min en el espacio de trabajo.
- **Los subagentes se cortan si Tomás escribe:** pasó al final de esta calibración. No se perdió nada de lo terminado: cada revisor escribe al final y los cortados simplemente no dejan archivo (se relanzan con `auditar.py lanzar`).

## Cómo repetirla
`python3 tools/auditor/calibrar.py` sobre `studio/episodios/ep01-congelamiento-cerebral/auditoria/historico/`. Los videos viejos están en la prerelease `calibracion`, los clips en `ep01-kling`, y los cortes por plano se sacan de `build_ep01.py` de cada commit.

## Proceso v2: chequeo automático por plano calibrado con el Ep. 2 (21-oct-2026)
`tools/auditor/chequeo_planos.py` corrido sobre la versión r3 del Ep. 2 (`ep02-pajaros-picante-v3.mp4`, la que se publicó) y, para los ojos, sobre una prueba local del plano 14 (`tools/prueba.py ep02-pajaros-picante --planos 14 --muestras 2`):

| Lo que marcó el auditor en las rondas | Lo que mide el chequeo (en segundos, sin IA) |
|---|---|
| r3, bloqueante: la lupa tapa el ojo del pájaro en 14–16 | 🛑 `ojo_tapado` plano 14: recuadro [110, 200, 550, 640] sobre `Cuitlacoche_ojoR` |
| r2–r3: plano 19 pobre, suelo liso que ocupa la mitad del cuadro | ❌ `plano_quieto` 2,1 s · ⚠️ `fondo_liso` 76 % · ⚠️ `poco_movimiento` 0,31 |
| r3: P13 es una imagen fija con una píldora | ⚠️ `poco_movimiento` 0,38 |
| r3: en P10 el interior del ají queda pálido con bloom | 🛑 `quemado` 3,5 % en 16,0–16,7 s |
| r1–r3: el pájaro de 14–16 "congelado 5 s" | **No** lo marca: movimiento mediano 0,8–1,0 y 0,6–0,7 s máximo quieto (push-in, parpadeos y cabeza). Se movía poco; el revisor veía 6 fotos por plano. Desde v2 el revisor recibe estas medidas y 4 cuadros por segundo |

Umbrales (en `chequeo_planos.py` y `presupuesto.json`): par de cuadros "sin cambio" bajo 0,6 niveles de gris (216×384, sin la franja de subtítulos); plano quieto ≥ 2 s = falla (REFERENCIAS §3: algo cambia cada 1–2 s), ≥ 1,2 s = aviso; poco movimiento = mediana < 0,5; fondo liso = celdas de 12×12 con desviación < 3 en más del 70 % del cuadro; quemado > 3 % sin subtítulos ni gráficos; ojo tapado = al menos medio radio del ojo dentro del círculo de la lupa/recuadro/marca o de la caja de una píldora/subtítulo, con los ojos movidos igual que la imagen en el post. Calibrado con el render final; se recalibra con el primer animatic (8 muestras) del Ep. 3.

**Lo que no ve:** de los 3 bloqueantes de revisores en la r3 pilla 1 (la lupa del 14). Las hojas que flotaban en el 25 y el brazo visto a través del vaso en el 34 no se pueden medir así: siguen siendo del revisor.
