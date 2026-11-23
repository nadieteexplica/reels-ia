# Investigación 23-nov-2026 — temas, guiones, visual y Claude Code

Pedido de Tomás: "investigación de la puta" en Instagram (y redes) para arreglar lo que falla —temas que no enganchan, guiones malos, visual malo— y automatizar todo en Claude Code.

Fuentes: vidIQ (outliers IG/TikTok/YouTube Shorts, ~110 créditos de 150/mes), análisis escena por escena de 8 reels, repos de GitHub y artículos. Nuestros números: `docs/GUIONISTA.md` §1. **Leer junto con la parte 2** (`investigacion-2026-11-23-automatizacion.md`), que corrige algunas cosas de esta.

## 1. Lo más importante
1. **Nuestros 2 mejores videos (Ep. 3 edificio que caminó, Ep. 7 rascacielos) son ingeniería "¿cómo lo hicieron?"**. Es exactamente el formato que más rompe hoy en el mundo: pile hammer 34,1 M (771x), grúas 4,1 M y 2 M, submarino 2,1 M desde 3,6 mil seguidores, monedero de máquina 3,5 M (105x), barco que se hunde a propósito 1,5 M en español (182x). Ese es nuestro carril.
2. **El tamaño de la cuenta no importa; el formato sí.** @leo.explica tenía 48 seguidores y sacó 1,3 M (551x). @dannysdose 3,6 mil → 2,1 M.
3. **Lo visual que gana no es "realista": es claro.** 2D plano (buceo 2 M, ojos 1,3 M) y código (touchscreen 13,6 M, teclado 10,2 M) le ganan a 3D caro. Fondo oscuro, un color de energía que brilla, etiquetas con línea, números vivos en pantalla, sonido en cada acción.
4. **Los videos hechos 100 % con código y Claude Code ya llegan a 10–13 M** (@speedy_devv). Ya no hace falta Blender para todo.
5. **Duración:** los ganadores en IG duran 55–115 s (uno de 3:52 con 3,8 M). En YouTube Shorts en español los outliers van de 18 a 63 s. (Ver la corrección en la parte 2: la gente igual mira ~30–47 s.)

## 2. Temas que pegan (datos)
| Tipo | Ejemplos con números | Por qué |
|---|---|---|
| **Ingeniería "inventaste X"** (problema → solución → problema nuevo) | Pile hammer 34 M; grúas 4,1 M / 2 M; inodoro 2 M / 3,1 M; submarino 2,1 M; barco FLIP 1,5 M (es) | El espectador "inventa" la máquina; cada 3–5 s hay una falla nueva |
| **Mecanismo cotidiano por dentro** | Touchscreen 13,6 M; teclado 10,2 M; monedero 3,5 M; medidor de agua 2,7 M; rallador 1,5 M (1044x); alcantarillas 1,1 M (es); estufa de inducción 989 mil (es) | Lo usas todos los días y no sabes cómo funciona |
| **Tu propio cuerpo, al revés** | "Nunca has tocado nada" 3,8 M (es); ojos mientras duermes 1,3 M (es); nudillos 986 mil (es); corte con papel 7,5 M (es) | Te habla a ti y rompe lo que creías |
| **Mito + analogía cotidiana** | Buceo: "lo peligroso es subir" + gaseosa, 2 M (es, 352x) | Contradicción + objeto que todos conocen |
| **¿Qué pasaría si…?** (sobre todo YouTube) | Túnel a través de la Tierra (2 videos, 527–542 mil, 20x); gravedad 5 s (617 mil); esponja vs tsunami 1,6 M (43x) | Escenario imposible, respuesta real |
| **Historia real con giro** | Mataron a la almeja más vieja del mundo, 4,1 M (es) | Ironía; el final cambia todo |

**Regla para elegir temas:** objeto o cuerpo que el espectador tiene cerca + algo que cree y que es falso, o una máquina que nadie sabe cómo se hace. Evitar el dato suelto sin mecanismo.

## 3. Guiones: las 4 estructuras ganadoras
- **A. "Inventaste X"**: cosa simple ("Esto es un clavo") → escálalo ×100 → la solución obvia falla → arreglo → falla nueva → … → "Felicidades, acabas de inventar el ___" → imagen real que lo confirma.
- **B. Mecanismo con contradicción** (touchscreen): contradicción visible en el cuadro 0 (dedo suave sí, lápiz fuerte no) → la pregunta → dolor cotidiano (guantes en invierno) → por dentro → por qué pasa → 2 casos extra (lluvia, guantes táctiles) → frase poética que cierra en loop.
- **C. Escalera de micro-datos** (ojos): dato raro sobre ti → 4–5 datos de 4–6 s cada uno, cada uno más fuerte → "y aquí viene lo bueno" en el 60 % → CTA de envío ligado al último dato.
- **D. Mito + analogía** (buceo): "¿sabías que X no es lo peligroso?" + "para entenderlo solo necesitas una gaseosa" → la analogía vuelve en el clímax → la solución práctica → dato bonus con pregunta.

**Reglas que comparten todos:**
- Cero saludo; la primera sílaba ya es el gancho, y el cuadro 0 ya se mueve.
- Una analogía ancla (gaseosa, semilla en un estadio) que vuelve en el clímax.
- Números en pantalla que cambian en vivo (100 → 62, "CONTACTO REAL 0 %", ×100).
- Notas chicas de credibilidad ("Texas Instruments", "valores ilustrativos").
- Remate que cierra en loop con la primera frase.
- **CTA de envío a una persona específica** ("Envíaselo a ese amigo que da miedo cuando duerme", "mándaselo a quien no le funciona el celular con las manos mojadas"). Es mejor que "comenta" para nuestro tipo de video.
- "Pero" / "por eso", nunca "y después" (ya estaba en GUIONISTA.md; la data lo confirma).

## 4. Visual: lo que hacen los que ganan
- Fondo oscuro (#0B101D a #16181F) + **un color de energía** (oro o cian) con glow. Rojo sólo para peligro o error.
- Etiquetas en mayúscula con línea guía; badges tipo HUD; check y X.
- Subtítulos palabra por palabra, 1–3 palabras, con la palabra clave encerrada en un recuadro (speedy usa el recuadro azul de selección de Figma, con manillas).
- Cortes de sección, rayos X, carcasa que se vuelve transparente, vistas explotadas, zoom de escala con contador (×1 → ×10.000.000).
- Algo cambia cada 1–2 s (acción mecánica, número, etiqueta).
- **Sonido en cada acción** (clic, whoosh, golpe metálico, ping). Todos los ganadores tienen foley.
- Loop perfecto: el último cuadro vuelve al primero.
- 2D plano o 2.5D sirve igual que 3D. Lo que importa es que se entienda en 0,5 s.

## 5. Stack de Claude Code (gratis)
| Pieza | Para qué | Costo |
|---|---|---|
| Remotion + skill oficial (`remotion-dev/skills`) | Línea de tiempo, subtítulos, HUD, cifras, mezcla | Gratis para personas |
| HyperFrames (`heygen-com/hyperframes`) | HTML + GSAP a MP4; tiene flujo "faceless explainer" | Gratis (Apache 2.0) |
| three.js | Mecanismos 3D por código (cortes, explotados); Claude compara un cuadro con una referencia antes de animar | Gratis |
| Blender + Blender MCP | Sólo cuando haga falta 3D pesado o personaje | Gratis |
| `hassancs91/claude-faceless-shorts-creator` (MIT) | **Plantilla casi idéntica a lo que queremos**: beats HOOK/SETUP/QUIZ/REVEAL/TWIST/LOOP, QA de cuadros a tamaño celular, voz con tiempos por palabra, librería de SFX con `sfx-plan.json` | Gratis |
| `lemomo-ai/lemo-opuscar` (12,6 mil estrellas) | 99 estilos de película en código, para robar estilos | Gratis |
| `claude-motion` | Reglas de movimiento + SFX + Claude revisa sus propios cuadros | Gratis (MIT) |
| `ClaudeAnimationBase` (MIT) | Mascota con 31 emociones en p5.js; base si algún día queremos personaje | Gratis |
| `/watch` | Que Claude vea videos de referencia (cuadros + transcripción) | Gratis |
| Evitar | Full Visual (pack pagado de speedy), fal.ai, Higgsfield, VideoDB | Pagados |

## 6. Sistema propuesto en Claude Code
`/nuevo-video` corre en orden:
1. **Cazador**: 10 temas por la regla de §2, con contraste contra outliers (vidIQ, cuidando los 150 créditos/mes).
2. **Guionista**: elige estructura A/B/C/D, 12 ganchos, guion con beats y CTA de envío. Verificación con 2 fuentes (regla vigente).
3. **Director visual**: storyboard por beat → escenas en Remotion/HyperFrames (2D/2.5D) o three.js (3D), con el kit de marca.
4. **Voz**: tiempos por palabra → subtítulos exactos.
5. **Sonidista**: librería propia de SFX CC0 + `sfx-plan.json` por acción.
6. **QA**: cuadros a tamaño celular + checklist (gancho en cuadro 0, cambio cada ≤2 s, legibilidad, loop) + auditor ciego.
7. **Publicador**: paquete para Metricool, sólo tras el OK de Tomás.

## 7. Decisiones pendientes de Tomás
- Dirección visual: código 2D/2.5D (más rápido), three.js 3D por código, o mezcla (recomendado: mezcla).
- Duración: ver la parte 2 antes de decidir.
- Personaje: los ganadores no lo usan; queda como opcional para más adelante.
