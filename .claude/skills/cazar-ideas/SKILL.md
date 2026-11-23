---
name: cazar-ideas
description: Encuentra temas para El viejo del dato en dos pasos: primero agrupa lo que ya está pegando (outliers guardados en studio/caza/ y los estudios del 23-nov) en 4–6 TIPOS de tema con virales de ejemplo, y después busca dentro de cada tipo historias, máquinas o fenómenos específicos que nadie haya contado (filtro estricto: nada con un video del tema exacto sobre 100 mil vistas en YouTube, español o inglés; TikTok/IG por búsqueda web). Entrega hasta 15 temas en tabla para que Tomás elija uno. Usar al empezar /nuevo-video o cuando Tomás pida ideas.
---

# Cazar ideas (enfoque de Tomás, 23-nov-2026)

Lo corre el subagente `cazador` (o tú, si no está). Pasada **rápida y ancha**: se verifica a fondo sólo el tema que Tomás elija (CAZA_DATOS §9: no gastar horas antes de que él reaccione).

## 1. Temas calientes: desde lo que ya tenemos, no desde cero
No se buscan tendencias desde cero. Se sacan de:
- `studio/caza/ronda08-demanda/` (outliers sep–nov: `README.md`, `vidiq_ig_tiktok.md`, comentarios) y `studio/caza/ronda09-demanda/ronda.md`.
- `docs/estudios/investigacion-2026-11-23-*.md` (formatos y automatización) y las fichas de `docs/referencias/virales/`.

Con eso, agrupa los virales en **4–6 TIPOS de tema que están pegando** (ej.: máquinas gigantes por dentro · objetos cotidianos por dentro · tu cuerpo al revés · qué pasaría si). Cada tipo lleva **2–3 virales de ejemplo** sacados de esos archivos (título, link, vistas, fecha). Un tipo sin virales de ejemplo en nuestros archivos no entra. La búsqueda web sólo completa un link o una cifra que falte; no inventa tipos nuevos.

## 2. Dentro de esos tipos: lo que nadie ha contado
Por cada tipo, busca **historias, máquinas o fenómenos específicos** que calcen en él y que no tengan un video grande. **Da lo mismo de qué año sea el dato.** Pistas para buscar: "how does X work inside", "largest X ever built", "the machine that…", archivos de museos, ingeniería, patentes, Atlas Obscura, IEEE Spectrum, Smithsonian, Wikipedia (sólo para llegar a la fuente).

Con los gustos de Tomás (`docs/CAZA_DATOS.md` §9): mecánica a la vista, procesos y "cómo se hace", "qué pasa si", cosas que pasan siempre y nadie se cuestiona, "qué weá" que se entiende sola, objetos, máquinas y lugares de protagonistas. **No:** fallas de la NASA, física de nerd, el pulpo, casos sueltos sin mecánica.

Fuera también lo ya hecho o prohibido: `docs/PUBLICADOS.md`, `docs/IDEAS.md` §3 (lista negra), `docs/CAZA_DATOS.md` §6 y los temas prohibidos de `proyecto/INSTRUCCIONES.md`.

## 3. Filtro de quemado (estricto)
- **Fuera si hay un video del tema EXACTO con más de 100 mil vistas**, en YouTube español o inglés, de cualquier fecha:
  `python3 tools/cazador/quemado.py --estricto "<como lo buscaría alguien en español>" "<en inglés>" "<otra forma>"`
  De a un tema, nunca en paralelo (YouTube corta). Si sale REVISAR, lee los títulos y decide si son del tema exacto (anótalo). Un video del tipo de tema pero de otra cosa no quema.
- **TikTok / IG:** búsqueda web ("<tema> tiktok", "<tema> instagram reel", en los dos idiomas). Si encuentras un video del tema exacto sobre 100 mil → fuera. Si no puedes confirmarlo, escribe **"TikTok/IG sin confirmar"**; nunca supongas que está libre.
- **Verdad posible:** que exista al menos 1 fuente seria con link (institución, museo, universidad, paper, medio de ciencia o ingeniería). La segunda fuente se busca sólo para el tema elegido.
- vidIQ sólo si hace falta (0 créditos hasta el 18-dic-2026; revisa `vidiq_balance` y no gastes más de 10 sin avisar). Reddit no (bloquea lecturas automáticas).

## 4. Entrega
`studio/caza/rondaNN-<nombre>/ronda.md` y la misma tabla en el chat. Primero los tipos:

| Tipo de tema | Virales de ejemplo (link · vistas · fecha) |
|---|---|

Después **hasta 15 temas** (si no hay 15 buenos, menos; nunca relleno):

| # | Tipo | Gancho (≤ 12 palabras, como la 1.ª frase del video) | Qué es (1 línea) | Por qué sorprende | Fuente (link) | Video más visto del tema exacto (o "nada") | Riesgo |
|---|---|---|---|---|---|---|---|

- "Video más visto" = el más grande que encontró el filtro en YouTube (es/en), con vistas y link, más el estado de TikTok/IG ("nada" / link / "TikTok/IG sin confirmar").
- "Riesgo" = lo que podría tumbarlo: fuente única, dato difícil de verificar, poca mecánica para animar, tema sensible, cercano a algo ya publicado.
- Ordena por fuerza (lo más sorprendente con el camino más limpio primero). Tomás elige uno; ese pasa a la skill `guion` con su ficha verificada (2 fuentes).
