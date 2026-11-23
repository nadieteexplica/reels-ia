# Investigación 23-nov-2026 (parte 2) — automatización, skills y agentes de video

Complementa `investigacion-2026-11-23-formatos.md`. Fuentes: transcripciones de 3 videos de YouTube sobre automatizar video con Claude Code (Peverelli 1 M vistas; Chahar 138 mil; Zinho 139 mil), los datos del propio @speedy_devv (Keyframes), repos de GitHub y políticas de YouTube e Instagram. Pedido de Tomás: sin sesgos, así que van también las críticas y lo que contradice la parte 1.

## 1. Técnicas que se repiten en todos los que automatizan bien
1. **La skill es el producto, y crece con feedback.** Peverelli: su skill de edición tiene ~1.400 líneas y 36 reglas. El método: Claude hace un hook, él da feedback con segundo exacto ("en el 0:22 hiciste X, quiero Y") y le pide **"guarda lo aprendido en la skill"**. Según él, nunca repite el error. Empezó con hooks sueltos, no con videos completos. Le tomó ~10 días de iteración solo con los efectos de sonido (probó 8–10 sonidos por momento).
2. **Aprender el estilo de un video de referencia.** Chahar: la skill `/watch` saca 2 cuadros por segundo + transcripción, arma una hoja de contacto, mide proporciones (ej.: 31 % del tiempo cara a pantalla completa, 45 % lienzo sin cara) y escribe un `reference-style.md` que se reutiliza.
3. **Pipeline en etapas con auditoría:** planificación de assets → corte → auditoría del corte → "geometría" del cuadro (dónde no poner texto) → captura y B-roll (índice `.md` de su librería de 500 clips) → diseño → subtítulos → sonido → render → **revisión final con un modelo distinto** del que hizo el trabajo.
4. **Una skill chica por tarea, no una gigante.** "Mientras más skills agrego, mejores videos salen" (Chahar).
5. **FFmpeg como finisher:** quita pantallas negras y revisa la sincronía del audio antes de que lo vea un humano.
6. **Las pruebas sirven de prueba:** el agente toma capturas reales de la fuente (paper, post, página) y las pone en pantalla. Calza con nuestra regla de 2 fuentes.
7. **Nicho por outliers + un "predictor de viralidad":** Zinho busca outliers en vidIQ, saca patrones y huecos, bloquea personaje y voz y puntúa el gancho antes de publicar. Ojo: el predictor es de Higgsfield (video patrocinado) y él mismo dice que "es una predicción, no una garantía".
8. **Arreglar una escena, no regenerar todo.** Se pantallea solo la parte mala y se rehace esa.

## 2. Lo que nadie dice (contrapeso)
- **El tema pone el techo.** El dueño de @speedy_devv (Hugues): las mismas herramientas le dieron 13,5 M y 244 vistas la misma semana. Su reel de chips de IA quedó en 110 mil; el de PewDiePie, en 355 mil.
- **Incluso los hits se pierden a mitad de camino.** Watch time promedio: 30,6 s de 84 (touchscreen), 32,2 de 78 (teclado), 30,4 de 89 (batería), 38,3 de 107, 47 de 127. **La gente mira ~30–47 s sin importar el largo.**
- **"Automático" significa revisar cada cuadro.** Hugues dice que el modelo suena igual de seguro cuando se equivoca.
- **Su mediana subió de 3.075 a 69.913** al cambiar de formato, pero es un antes/después de una sola cuenta, sin control de tema ni frecuencia. Y él vende un pack de US$ 99.
- **Por qué salen genéricos (Hugues):** la imagen queda quieta mientras la voz habla; hay movimiento que la voz no nombra; varias ideas por imagen; los subtítulos se desfasan de la voz; íconos en vez de objetos reales reconocibles.
- **Las skills gratis enseñan la API, no un look.** El look sale de iterar.
- **Casi todos los tutoriales venden algo** (Higgsfield, Epidemic Sound, comunidades de Skool, packs). Las cifras de costo (Peverelli: ~US$ 27 por video) son de una sola persona.
- **Riesgo de plataforma:**
  - YouTube no paga contenido "inauténtico": producido en masa, repetitivo o con plantilla y poca variación, sea IA o no. Revisa canales completos, no videos sueltos. En enero de 2026 cerró 16 canales (35 M de suscriptores).
  - Instagram premia lo original y saca de recomendaciones a los agregadores.
  - Lo que no te demonetiza es ser IA o no tener cara: es que los videos sean intercambiables.
- **Voz IA:**
  - Estudios recientes: una voz IA de alta calidad rinde igual que una humana en profesionalismo y retención. Lo que perjudica es la voz robótica.
  - Pero 77 % de los consumidores dice confiar más en voces humanas, y un paper (2024) encontró que la voz humana baja la carga cognitiva en anuncios cortos.
- **Sesgo de sobrevivencia en la parte 1:** se miraron sólo outliers. No sabemos cuántos videos iguales fracasaron.

## 3. Qué corrige de la parte 1
- **Duración:** la gente mira ~30–47 s aunque el video dure 80–127. En IG igual rompen; en YouTube cuenta el % visto (nuestro Ep. 7: 89 % con 48 s). **No soltar el techo a ciegas:** probar largo sólo en IG, o un corte de 40–50 s para YouTube y uno largo para IG.
- **Set fijo / plantilla:** choca con la regla de "inauténtico". Tiene que haber variación real de tema, estructura y visual entre videos, no sólo cambiar el texto.
- **Objetos reales > íconos.** Se recrea el objeto real (interfaz, máquina), no un dibujo genérico.

## 4. Qué aplicamos
1. Feedback con segundo exacto → "guárdalo en la skill" como rutina de cada video (Tomás da notas; Claude actualiza la skill).
2. `/watch` sobre los outliers que manda Tomás → `reference-style.md` por estilo.
3. Revisión final con un agente distinto del que hizo el video (ya lo tenemos con el auditor; se mantiene).
4. Checklist anti-genérico de Hugues dentro de la QA: cada visual cambia en la palabra que lo nombra, una idea por imagen, subtítulos sincronizados, objeto real.
5. Variación obligatoria entre videos (estructura A/B/C/D rotando y estilos distintos) para no caer en "inauténtico".
6. Duración en prueba controlada: misma idea en 45 s (YT) y versión larga (IG), y medir.

## 5. Voz gratis (Tomás quiere dejar de pagar ElevenLabs)
- **Candidato principal: Qwen3-TTS** (Apache-2.0 código y pesos, uso comercial OK, español, clona con 3 s de audio y diseña voces desde texto). En rankings ciegos queda bajo los pagados, así que hay que probarlo a ciegas contra ElevenLabs.
- **Respaldo: Kokoro** (Apache-2.0, liviano, corre en CPU; pocas voces en español).
- **Descartados:** Chatterbox (retirado, sin soporte), XTTS-v2 / F5 / Fish (pesos no comerciales), Gemini TTS gratis (preview, límites, licencia comercial del free tier sin aclarar).
- **Prohibido:** clonar a Fernando Martínez o a cualquier persona sin permiso. Sólo voz diseñada o la voz de Tomás.
- **Subtítulos por palabra sin ElevenLabs:** alinear el audio con Whisper (faster-whisper / whisper.cpp), gratis y local.
