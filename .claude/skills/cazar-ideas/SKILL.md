---
name: cazar-ideas
description: Encuentra ideas para El viejo del dato desde demanda real (outliers recientes en inglés sin versión en español, comentarios del nicho, búsqueda web), las pasa por el filtro de quemado y entrega 10 ganchos de una línea con su evidencia para que Tomás elija uno. Usar al empezar /nuevo-video o cuando Tomás pida ideas.
---

# Cazar ideas

Lo corre el subagente `cazador` (o tú, si no está). Tomás elige 1 de 10; no hay puntaje /45.

## 1. Juntar candidatas (40+), en este orden
1. **Lo ya cazado:** `studio/caza/*/README.md` y `ronda.md` (outliers guardados de rondas anteriores, con vistas y fecha). Lo que tenga más de 60 días se vuelve a revisar.
2. **Búsqueda web (gratis):** WebSearch de temas "how it works / why does / what happens if" recientes; listas de virales de la semana; preguntas que la gente hace (Google "Otras preguntas"). Reddit NO (bloquea lecturas automáticas).
3. **YouTube público:** `tools/cazador/quemado.py` también sirve para mirar qué hay en español de un tema.
4. **vidIQ (sólo si hace falta):** `vidiq_balance` primero. Hasta el 18-dic-2026 quedan 0 créditos. Con créditos: `vidiq_outliers` (Shorts, en, 30–60 días, ≥300 mil, engagement ≥0,02), `vidiq_instagram_tiktok_outlier_search` (en, 60 días). Máx. 10 créditos por ronda sin avisar.
5. **Comentarios:** preguntas repetidas en comentarios de virales del nicho ("¿y cómo funciona X?") y lo que pide la gente en nuestros propios videos (`docs/IDEAS.md` §5).

**Demanda real = evidencia:** un outlier (vistas, veces sobre su canal, fecha, link), un hilo de comentarios que lo pide, o búsquedas. Sin evidencia no entra.

## 2. Filtrar
- **Quemado (regla de Tomás):** `python3 tools/cazador/quemado.py "<como lo buscaría la gente en español>" "<otra forma>" "<otra>"`. Si hay un video en español con más de 500 mil vistas en los últimos 6 meses → fuera. **De a una idea, nunca en paralelo** (YouTube corta). Veredictos: QUEMADO · **REVISAR** (hay videos grandes y recientes cuyo título no calza con la búsqueda: léelos y decide si son del tema; anota tu decisión) · LIBRE. Si sale **AVISO saturado** (> 5 M en 12 meses), dilo en la ronda: Tomás decide (propuesta pendiente: tratarlo como quemado). Ojo: sólo mira YouTube. Pregúntate siempre si fue viral en TikTok o IG en español (búscalo en la web: "<tema> tiktok"); si sí, también fuera (lección 174: la pistola de bencina pasó el filtro de YouTube y ya había sido viral).
- **Ya hecho o prohibido:** `docs/PUBLICADOS.md`, `docs/IDEAS.md` §3 (lista negra), `docs/CAZA_DATOS.md` §6 (quemados) y §9 (gustos de Tomás: mecánica a la vista, "qué weá", procesos; no fallas de la NASA ni física de nerd; no el pulpo).
- **Verdad posible:** que existan 2 fuentes serias (instituciones, universidades, papers, medios de ciencia). Sólo ubicarlas, no verificar a fondo todavía.
- **Variedad:** que la ronda permita las 4 estructuras (A inventaste X · B contradicción · C escalera · D mito + analogía) y al menos 5 familias; nada de la misma familia que el último video (`docs/ROTACION.md`).

## 3. Entregar
`studio/caza/rondaNN-<tema>/ronda.md` y la misma tabla en el chat:

| # | Gancho (la primera frase del video, ≤ 12 palabras) | Evidencia | Quemado | Estructura | Fuentes candidatas |
|---|---|---|---|---|---|

Ordenadas por fuerza de la evidencia. Tomás elige una; la elegida pasa a la skill `guion` con su ficha (`studio/episodios/<ep>/ficha.md`: gancho, dato, mecánica en pasos, 2 fuentes).
