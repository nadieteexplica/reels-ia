---
name: nuevo-video
description: Hace un video completo de El viejo del dato de punta a punta, en orden: cazar → Tomás elige 1 de 10 ganchos → guion (regla del guion) → voz → storyboard y animación → sonido → QA → paquete → OK de Tomás por post → programar. Usar cuando Tomás escribe /nuevo-video o pide un video.
---

# /nuevo-video

Antes: `git pull`, lee `CLAUDE.md`, `proyecto/INSTRUCCIONES.md` (Seguridad y Publicación mandan), `CONTEXTO.md` → Estado actual, `docs/ROTACION.md` y las últimas 10 filas de `docs/LECCIONES.md`. Métricas de los videos anteriores a las 48 h → `docs/PUBLICADOS.md`.

1. **Cazar** — skill `cazar-ideas` (subagente `cazador`) → 10 ganchos con evidencia. **Parar: Tomás elige 1.** (Si trae su propia idea, se salta, pero igual pasa por el filtro de quemado.)
2. **Ficha + guion** — skill `guion`: ficha verificada (2 fuentes) → 3 `guionista` en paralelo (estructuras distintas a la anterior) → duelo de 12 ganchos + contra virales → `juez-viral` → espectadores. Máx. 2 reescrituras; si no pasa, siguiente idea de la ronda sin preguntarle a Tomás.
3. **Voz** — skill `voz` (Actions) → `voz.wav` + `words.json`; duración 35–50 s.
4. **Storyboard** — subagente `director-visual` con el único estilo aprobado: laboratorio nocturno del beat v5 (rotación de estilos apagada) → `storyboard.md/json`.
5. **Animación** — skill `estilo-visual` + kit, con la autorrevisión de `qa-video` (hojas por beat hasta que una pasada no encuentre nada).
6. **Sonido** — skill `sonido` → `sfx-plan.json` → mezcla con la voz (chequeo de audibilidad).
7. **QA** — skill `qa-video`: `qa_video.py preparar` → `auditor-final` (ciego) → `qa_video.py cerrar`. Sin `qa.json` aprobado, el hook no deja renderizar el final.
8. **Render final** (Actions) → Release `epNN`.
9. **Paquete y mensaje** — skill `publicar`. **Parar: Tomás da el OK por post** con `tools/ok.sh epNN <redes>` (sin archivo, el hook bloquea Metricool).
10. **Programar**, anotar en `PUBLICADOS.md` y `ROTACION.md`, actualizar `CONTEXTO.md` → Estado actual, commit y push.

Topes: 4 h por video (meta 2,5 h). Si algo se va a pasar, para y avísale a Tomás con opciones. A Tomás sólo le llegan dos mensajes: los 10 ganchos y el video terminado con su paquete.
