---
name: qa-video
description: Control de calidad del video de El viejo del dato a tamaño celular, con autorrevisión de cuadros durante la animación y el veredicto ciego de auditor-final antes del render final. Sin qa.json aprobado el hook no deja renderizar el final. Usar en cada borrador y antes de renderizar.
---

# QA del video

Marco: `docs/REGLAS.md`. Lo técnico y lo que se ve objetivamente (texto cortado o ilegible, cuadros negros, volumen, desfase voz/imagen) es **[MEDIDA]** y manda. El auditor ciego **orienta**: sus bloqueantes (errores que un espectador notaría) frenan, sus notas sólo informan. Pasar por encima de un bloqueante se puede, con el motivo escrito.

## Mientras animas: autorrevisión (ciclo de claude-motion, MIT, pasado a Python)
Cada borrador: render a media resolución (540×960) → **una hoja de cuadros por beat**, tomados 0,3 s después de cada cambio (los segundos salen del storyboard y `words.json`) → revisar con la lista → arreglar → volver a renderizar → **repetir hasta que una pasada completa no encuentre nada**. Nunca digas "arreglado" sin mirar la hoja nueva. Para una transición dudosa, cuadros cada 0,2 s de ese tramo.

**Lista [MEDIDA salvo lo marcado]:** choques no buscados · cosas cortadas por el borde · zona segura (nada clave bajo 1580 px ni en los 160 px de la derecha) · ¿se lee a ancho de celular? · texto que se mueve mientras se lee · tiempos de lectura (≥ 1 s por frase corta + 0,25 s por palabra sobre 3) · salidas más rápidas que entradas · sólo colores de la paleta [PROBABLE] · el mismo objeto se ve igual en todo el video · nada quieto > 2 s [PROBABLE] · cada cambio en la palabra que lo nombra [PROBABLE] · el subtítulo no repite el número gigante en pantalla [PROBABLE].

## Ritmo (lección 177) [PROBABLE]
- `python3 tools/ritmo.py <borrador.mp4>` y compara con la banda de los virales (`docs/estudios/ritmo-virales.md`): cámara rápida 2–6 % del tiempo, cambios dentro del plano 0,7–1,0 por segundo, tiempo con cambio 71–95 %, tramo quieto ≤ 1,5 s.
- **Prueba de primera vista:** `python3 tools/primera_vista.py <borrador.mp4> <words.json> <scratchpad>/primera-vista` y un juez ciego que lo ve UNA vez (cuadros cada 0,1 s) y cuenta qué pasó por segundo. Un tramo que no puede contar va demasiado rápido.
- Decide el ojo de Tomás en el celular.

## Antes del render final: la puerta
1. `python3 tools/qa_video.py preparar <ep> <borrador.mp4>` → `studio/episodios/<ep>/qa/` (técnico, `hook.jpg`, hojas a 405×720, `subtitulos.md`).
2. Lanza **`auditor-final`** (ciego, no escribe) con la ruta de esa carpeta. Guarda su respuesta tal cual: pégala cruda en el scratchpad y `python3 tools/guardar_veredicto.py <crudo> studio/episodios/<ep>/qa/auditor_final.json` (el hook no deja escribirlo a mano). Mira también `qa/sincronia/` (un cuadro 0,15 s después de cada cambio del storyboard).
3. `python3 tools/qa_video.py cerrar <ep>` → `qa/qa.json`. Aprueba si `tools/qa.py` pasa y el auditor no marcó bloqueantes. Si decides pasar por encima de un bloqueante: `cerrar <ep> --motivo "…"` (queda guardado). Lo técnico no tiene excepción.
4. Si no aprueba: arregla los bloqueantes (y las sugerencias baratas), vuelve al paso 1. Máximo 2 rondas; un plano que falla dos veces se simplifica.
5. Con `qa.json` aprobado, recién ahí el trabajo de render final (`jobs/render2d/*.json`, con Write). Si cambias cualquier fuente después (guion, voz, sonido, escena), la aprobación se cae sola (huella) y hay que repetir.
