---
name: aprender
description: Guarda cada nota de Tomás sobre un video (idealmente con el segundo exacto) en la skill que corresponde y en docs/LECCIONES.md, para no repetir el error. Usar cuando Tomás da feedback ("en el 0:22 hiciste X, quiero Y") o escribe /aprender.
---

# Aprender de una nota de Tomás

1. **Entiende la nota:** qué segundo (si no lo dio y hace falta, pregúntalo una vez), qué pasó, qué quiere en su lugar. Cita sus palabras textuales.
2. **Clasifícala** y escribe la regla en el lugar que la va a hacer cumplir la próxima vez:
   - idea/tema → `cazar-ideas` (y `docs/CAZA_DATOS.md` §9 "Gustos de Tomás")
   - guion, gancho, cierre → `guion` y `docs/GUIONISTA.md` (y, si es una vara, una línea en la ficha viral que corresponda)
   - voz, pausas, pronunciación → `voz`
   - imagen, movimiento, estilo → `estilo-visual`
   - sonido → `sonido`
   - algo que el QA debió pillar → la lista de `qa-video` (y, si se puede medir, un chequeo en `tools/qa.py`)
   - publicación → `publicar`
   La regla se escribe como **prueba que se puede revisar** ("ningún texto se mueve mientras se lee"), no como deseo ("mejor ritmo").
3. **`docs/LECCIONES.md`:** una fila nueva (número siguiente) con: qué pasó (con el segundo y el episodio), por qué pasó, la regla que queda y dónde quedó escrita.
4. Si la nota pide arreglar el video actual, arréglalo además de guardar la regla.
5. Commit y push ("Lección NNN: …"). Contéstale a Tomás en una línea: qué regla quedó y dónde.
