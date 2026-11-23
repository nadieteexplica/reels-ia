# Ronda 08 — demanda real (23-nov-2026), materia prima del cazador

Pedido de Tomás: ideas desde demanda real, filtro de quemado (video en español > 500 mil vistas en 6 meses), 10 ganchos de una línea con evidencia. Ronda interrumpida para armar el sistema completo (ver `docs/MIGRACION_CLAUDE_CODE.md`); esto queda como insumo.

## Fuentes que sí se pudieron leer
- **vidIQ outliers YouTube Shorts (en, 3 meses, ≥300 mil vistas, engagement ≥2 %)** — 5 créditos. Destacados (vistas · veces sobre su canal · fecha):
  - Rope over a branch → tower crane (Things Opened) 4,3 M · 1233x · 18-oct — "inventaste X"
  - Washing machine weighs your laundry (Cutaway) 1,1 M · 439x · 16-nov
  - Boring machine (Logibu) 4,5 M · 368x · 1-nov
  - Why you can never turn the last gear (Cranky Science) 5 M · 63x · 2-nov
  - Why are there so many kinds of screws? (I Build It) 1,7 M · 50x · 17-oct
  - How bulletproof vests actually work (Fablr) 3,9 M · 49x · 1-nov
  - Leaning Tower of Pisa should have fallen (CFelms) 1,3 M · 46x · 13-nov
  - Why are race tracks slanted? (Fact Blast) 5,4 M · 36x · 29-oct
  - Vending machines detect fake coins (PatentYogi) 1,2 M · 27x · 7-oct; Vending machines used to take washers (Trial & Eureka) 16,2 M · 8x · 10-oct
  - The hidden Y inside every zipper (The Inner How) 328 mil · 12x · 27-oct
  - Never drain your pool after a week of rain (ConstrucBIM) 1,3 M · 7,7x · 12-nov
  - Only one tenth of your fireplace heat reaches you (ConstrucBIM) 2,8 M · 6,6x · 18-nov
  - These metal blocks stick without glue or magnets (vt.physics) 1,4 M · 4,4x · 16-nov
  - How to move a 1-ton machine with a finger (Infinite Desk) 2,2 M · 3,3x · 3-nov
  - Clever way soap dispensers work (JaDropping Science) 4,9 M · 2,2x · 22-sep
  - How you invented the toilet / vacuum / air conditioning (Odd Tilt) 5 M / 641 mil / 2,3 M
- **vidIQ outliers Instagram/TikTok (en, desde 24-sep, ≥300 mil)** — 5 créditos. Detalle completo en `vidiq_ig_tiktok.md`. Destacados: rallador de queso 1,5 M · 1044x; portones antirrobo del súper 10,1 M · 1173x; arrocera que "espera que se acabe el agua" 1,3 M · 858x; martinete 34,1 M · 772x; freno secreto del ascensor 5 M · 27x; imán en tubo de cobre 2,6 M · 225x; mesa de pool que se queda con las bolas salvo una 3 M · 15x; bola de la lata de Guinness 564 mil · 153x; rodamientos (¿cómo meten las bolas?) 797 mil; rascacielos de Las Vegas que quemaba con el sol 1,7 M · 206x; mover un muro sobre el Golden Gate 1,8 M; dardos tranquilizantes 1,9 M · 67x.
- **vidIQ comment_insights (es, nicho explicadores)** — 5 créditos. Poca señal de temas: casi todo "sube otro"; pedidos concretos: fibras submarinas/amplificadores (Veritasium es), terraformar Marte.
- **Comentarios de "How you invented the toilet" (Odd Tilt, 5 M)** — 5 créditos, `comentarios_oddtilt_toilet.json` (100 hilos). Sin pedidos claros de "haz X ahora".
- **vidIQ: 0 créditos hasta el 18-dic-2026.**

## Fuentes que no se pudieron leer
- **Reddit** (r/explainlikeimfive, r/NoStupidQuestions, r/todayilearned): bloquea lecturas automáticas (403), está restringido en el Chrome de Tomás por la extensión y el buscador web no indexa sus posts. Opciones: que Tomás pegue los tops del mes, o un dataset público reciente.

## Filtro de quemado
`tools/cazador/quemado.py "consulta" ["otra forma"]` lee la búsqueda pública de YouTube (videos y Shorts en español) y abre la página de cada resultado > 500 mil vistas para ver la fecha. Probado con la pistola de bencina: LIBRE en YouTube (el mayor, 732 mil de 2022). **Límite:** no ve Instagram ni TikTok, donde Tomás dice que la pistola ya fue viral.
