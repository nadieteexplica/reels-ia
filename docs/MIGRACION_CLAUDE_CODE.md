# Migración a Claude Code (decidida por Tomás el 23-nov-2026)

El proyecto pasa del chat de claude.ai a **Claude Code en el Mac de Tomás**. Motivos: renderizar con la GPU del Mac, entorno que queda instalado, subagentes de verdad, hooks que obligan las puertas de calidad, y comandos como `/nuevo-video`.

Base de la decisión: `docs/estudios/investigacion-2026-11-23-formatos.md` y `investigacion-2026-11-23-automatizacion.md`. Leer ambos antes de tocar nada.

## Qué cambia (decidido o propuesto)
| Tema | Antes | Ahora |
|---|---|---|
| Dónde se trabaja | Chat de claude.ai + GitHub Actions | Claude Code local (Mac); Actions sólo de respaldo |
| Visual | 3D realista en Blender (Ep. 5) | **Por decidir (recomendado: mezcla)**: código 2D/2.5D (Remotion o HyperFrames) para cuerpo y conceptos; three.js o Blender para máquinas |
| Voz | ElevenLabs (pagado) | **Probar gratis**: Qwen3-TTS (voz diseñada o la de Tomás) vs ElevenLabs a ciegas; si aguanta, se cancela ElevenLabs |
| Subtítulos por palabra | Timestamps de ElevenLabs | Alineación con Whisper (local) |
| Guiones | `docs/GUIONISTA.md` | Se suman las 4 estructuras (A inventaste X, B contradicción, C escalera, D mito + analogía), rotando |
| Sonido | Casi nada | Librería CC0 de SFX + `sfx-plan.json` por acción |
| Duración | 25–40 s, techo 45 s | Sin cambio hasta la prueba controlada (45 s YT vs largo IG) |

## Orden de trabajo en la primera sesión de Claude Code
1. **Revisar el entorno:** chip del Mac, Homebrew, Node, Python, ffmpeg, Blender. Instalar lo que falte.
2. **CLAUDE.md:** ya existe uno corto. Mantenerlo corto; las reglas largas siguen en `proyecto/INSTRUCCIONES.md` y `docs/`.
3. **Prueba de voz gratis (lo primero que pidió Tomás):**
   - Instalar Qwen3-TTS en el Mac.
   - Mismo guion de un video publicado (ej. Ep. 7) con 3 voces diseñadas ("hombre mayor, cálido, ritmo rápido", etc.) + clon de la voz de Tomás si mandó un audio de 10 s.
   - Comparar a ciegas contra el audio de ElevenLabs con el auditor (sin decir cuál es cuál).
   - Si gana o empata, `tools/voz_libre.py` reemplaza a `tools/eleven.py` y Tomás cancela ElevenLabs.
   - **Resultado (23-nov):** Tomás eligió la voz diseñada **"narrador de documental"** (`studio/voz-prueba/voces.json` → `B_narrador_doc`) por sobre ElevenLabs, aunque reconoció cuál era ElevenLabs (la prueba no quedó del todo a ciegas). Orden: narrador doc > abuelo cálido > viejo chileno (el más lento: 58 s). Whisper: las 4 casi sin errores (narrador 2,1 % WER: "lo → los"; ElevenLabs 0,7 %; "quince → 15" no es error). Qwen deja 15–19 s de pausas: con `tools/voz_ajustar.py` (pausas ≤ 0,3 s y hasta 1,2×) el narrador queda en 49,6 s contra 46,6 s de ElevenLabs. Corre en Actions (`voz-libre.yml`, `macos-15`): ~3,5 min por locución de 50 s; usa ~6,8 GB de memoria (en el Mac de 8 GB va justo). Resultados en `out/voz-libre/ep07/`.
   - **Voz fijada (23-nov):** referencia de 11 s en `voz/narrador.wav` (+ `voz/narrador.json` con su texto exacto y origen). Se usa con `tools/voz_fija.py` (trabajo en `jobs/voz-libre/`, con `"voz": "narrador"`): clona la referencia trozo a trozo con el modelo Base y mide la "huella de voz" (codificador de hablante de Qwen) contra la referencia. Prueba con Ep. 7 y Ep. 16: **0,992–0,995 en todos los trozos de los dos guiones**; la voz diseñada, en cambio, se iba alejando dentro del mismo audio (0,999 → 0,926). El clon además hace menos pausas (sólo hace falta 1,05–1,14× después de apretarlas). Ep. 7: 47,1 s, Whisper sin errores reales; Ep. 16: 53,2 s, un "las → la". Audios en `out/voz-libre/fija-narrador/`.
   - **Tomás escuchó los clones y los aprobó (23-nov).**
   - **Subtítulos por palabra con Whisper (23-nov):** `tools/voz_palabras.py audio guion words.json` reemplaza a `tools/words.py`. Mismo formato (`[{w, s, e}]`); las palabras salen del guion (con puntuación, "quince" y no "15") y de Whisper sólo los tiempos. Promedia Whisper medium (llega ~40 ms tarde) y large-v3-turbo (~59 ms temprano). Validado contra los tiempos de ElevenLabs del Ep. 7: **inicio de palabra a 36 ms en promedio (p90 79 ms, peor 167 ms)**, o sea ~1 cuadro. En `voz-libre.yml`, la voz fija ya deja `<texto>.words.json` junto a cada audio; también hay un modo `"palabras"` para alinear cualquier audio. Verdad de referencia en `studio/voz-prueba/verdad/`.
   - **Falta antes de cancelar ElevenLabs:** un video real completo con la voz nueva (guion → `voz_fija.py` → `words.json` → `prep.py` del episodio leyendo `out/voz-libre/...` en vez de `out/tts/...`).
4. **Skills del pipeline** en `.claude/skills/` (una chica por tarea): cazador, guionista (ya hay agente), director visual, voz, sonido, QA, publicación. Comando `/nuevo-video` que las corre en orden.
5. **Hooks:** no se arma el render final si `tools/prueba.py` / `tools/qa.py` no pasan.
6. **Piloto:** un video tipo "inventaste X" (ingeniería) en el estilo nuevo, para comparar con nuestros mejores (Ep. 3 y 7).

## Reglas que no cambian
- Seguridad y Publicación de `proyecto/INSTRUCCIONES.md`: nunca se publica sin el OK de Tomás por post; la API key nunca se escribe; nada con derechos de autor.
- Verdad con 2 fuentes, salud sólo general, temas prohibidos.
- Después de cada sesión: actualizar `CONTEXTO.md`, `docs/PUBLICADOS.md`, `docs/IDEAS.md`, commit y push.

## Estado al cierre del 23-nov-2026
Pasos 1–6 hechos y probados con casos reales (voz, cazador, guion con jueces, director visual, kit visual en 3 vueltas con el beat v5 aprobado por Tomás, sonido, QA, hooks). El marco de decisión quedó en `docs/REGLAS.md`. Falta: el video de prueba completo del guion D y después el primer video real con la ronda 09 (ver `CONTEXTO.md` → "Cómo partir la próxima sesión").
