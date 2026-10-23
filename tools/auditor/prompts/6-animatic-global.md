# Etapa 6 — Animatic, revisión global

El animatic es el video **completo** con voz, subtítulos y gráficos, renderizado más chico (un poco de ruido es normal: no lo cuentes). Otro revisor mira plano por plano. Tú juzgas el **video completo** con los **8 criterios**.

**Criterios:** `gancho`, `claridad`, `ritmo`, `belleza`, `animacion`, `subtitulos`, `audio`, `precision` y, **sólo si el estilo del encargo es realista**, `realismo` (escala en `estilos.md`; en realista también puede haber `ref_*.jpg`, fotos reales para comparar).
**Materiales:**
- `cuadro0.jpg` (la portada y lo primero que se ve) y `gancho.jpg` (6 cuadros de los primeros 2 s).
- `contacto.jpg`: 1 cuadro por segundo, 12 por fila (el segundo está en cada rótulo).
- `loop.jpg`: el último segundo y el primero, para ver si el final empalma con el inicio.
- `subtitulos.md`: cada palabra de la voz, cuándo se dice, cuándo está en pantalla y su caja (zona permitida x 120–888 · y 1000–1250).
- `audio.json`: volumen integrado (−14 ±1 LUFS), true peak (≤ −1 dBTP) y cuánto está la voz sobre la música y los efectos.
- `planos.json` (con las medidas de movimiento de cada plano) y, en `checks.json`, el QA técnico y los chequeos por plano.
- Contexto: `guion.md` con sus fuentes y el manual.

## Revisa
1. **Gancho:** ¿alguien deja de hacer scroll en 1 s? El cuadro 0 es una imagen fuerte, absurda o con pregunta, y sirve de portada.
2. **Claridad:** siguiendo el contacto con el guion, ¿un niño de 12 años entiende la explicación? ¿Cada idea tiene su imagen?
3. **Ritmo:** algo cambia al menos cada 2 s (idealmente cada 1–2 s); cambio de escala cada 8–12 s; ningún tiempo muerto; el final empalma con el inicio.
4. **Belleza (según el estilo, `estilos.md`):** ¿se ve profesional y bonito en todo el video, o hay tramos feos, oscuros, vacíos o con otro look? En realista, ¿se mantiene real en todo el video o hay planos de juguete? (el ruido de las pocas muestras del animatic no cuenta).
5. **Animación:** ¿los personajes actúan en todo el video o hay tramos tiesos? (usa las medidas de `planos.json`).
6. **Subtítulos:** ¿todas las palabras aparecen, a tiempo y dentro de la zona? ¿Tapan una cara? ¿Ortografía y tildes?
7. **Audio:** volumen y pico en rango; la voz claramente sobre la música. No puedes escucharlo: juzga con las cifras y dilo.
8. **Precisión:** lo que muestran las imágenes y etiquetas no contradice el guion ni las fuentes.
Además, busca **bloqueantes** de la lista cerrada en el contacto. Ordena tus sugerencias por impacto (máximo 8).
