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
4. **Skills del pipeline** en `.claude/skills/` (una chica por tarea): cazador, guionista (ya hay agente), director visual, voz, sonido, QA, publicación. Comando `/nuevo-video` que las corre en orden.
5. **Hooks:** no se arma el render final si `tools/prueba.py` / `tools/qa.py` no pasan.
6. **Piloto:** un video tipo "inventaste X" (ingeniería) en el estilo nuevo, para comparar con nuestros mejores (Ep. 3 y 7).

## Reglas que no cambian
- Seguridad y Publicación de `proyecto/INSTRUCCIONES.md`: nunca se publica sin el OK de Tomás por post; la API key nunca se escribe; nada con derechos de autor.
- Verdad con 2 fuentes, salud sólo general, temas prohibidos.
- Después de cada sesión: actualizar `CONTEXTO.md`, `docs/PUBLICADOS.md`, `docs/IDEAS.md`, commit y push.
