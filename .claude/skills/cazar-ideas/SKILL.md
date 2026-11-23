---
name: cazar-ideas
description: Encuentra temas para El viejo del dato sobre cualquier cosa del mundo (sin categorías ni familias), elige sólo los que cumplen 3 de 4 criterios de curiosidad y de ganas de compartir (pregunta abierta, emoción fuerte, te toca a ti, ganas de contarlo), sin dos con la misma idea de fondo, los pasa por el filtro estricto (nada del tema exacto sobre 100 mil vistas), un revisor ciego bota los que no mandaría a un amigo, y guarda lo que pasa en docs/BANCO.md. Tope de 10 min por ronda. Usar al empezar /nuevo-video, para rellenar el banco, o cuando Tomás pida ideas (primero se le muestra el banco).
---

# Cazar ideas (Tomás, 23-nov-2026; lección 179)

Lo corre el subagente `cazador`, y el revisor es otro subagente. Es una pasada rápida y ancha. La verificación a fondo (2 fuentes) se hace sólo para el tema que Tomás elija.

## 0. Velocidad y banco (mandan sobre lo demás)
1. **Tope de 10 minutos por ronda.** Anota la hora al partir (`date +%H:%M`). Cuando llegues a los 10 min, paras y entregas lo que ya pasó el filtro, aunque sea poco.
2. **Filtra menos, elige mejor.** Juntas candidatos sin filtrar y eliges **los 20 mejores** según el criterio de §2. Sólo esos 20 pasan por `quemado.py`, con **una búsqueda en español y una en inglés**, sin variantes.
3. **Banco siempre lleno.** Lo que pasa el filtro y la revisión va a **`docs/BANCO.md`** (meta: 20). Cuando Tomás pide temas, se le muestra el banco al instante, sin buscar. Mientras se produce cada video, el cazador rellena el banco en segundo plano.

## 1. Sin categorías
El tema puede ser **cualquier cosa del mundo**. **No partas de una lista de familias o tipos, ni de lo que ya nos funcionó** (lección 179: la ronda 10 salió entera de "mover o levantar una estructura gigante", lo mismo del Ep. 3, porque partió de lo que había pegado). Busca ancho: cuerpo, casa, comida, animales, cielo, ciudad, historia, objetos, química de la cocina, lo que pasa mientras duermes, etc. Ninguna de estas es una lista para recorrer: son sólo ejemplos de lo ancho que puede ser.

## 2. Criterio central: entra sólo si cumple **al menos 3 de 4**
Respaldo [PROBABLE]: Loewenstein 1994 (la curiosidad nace de una brecha de información que uno quiere cerrar) y Berger y Milkman 2012 (se comparte lo que provoca emoción de alta activación, como el asombro, la ansiedad o la risa, no lo tibio).
1. **Pregunta abierta:** abre una pregunta que no puedes dejar sin respuesta.
2. **Emoción fuerte:** asombro, inquietud, asco o risa. Un "ah, interesante" no cuenta.
3. **Te toca a ti:** tu cuerpo, tu casa, tu día, algo que viviste.
4. **Ganas de contarlo:** dan ganas de contárselo a alguien al tiro.

Por cada tema, anota cuáles de los 4 cumple y con qué palabra (p. ej. "2: asco"). Con 2 de 4 queda fuera, aunque sea interesante. También sirven los gustos de `docs/CAZA_DATOS.md` §9, pero el criterio de los 4 manda.

## 3. Variedad: una idea de fondo por tema
- **Nunca dos temas con la misma idea de fondo, aunque cambie el objeto.** La idea de fondo es el mecanismo o la sorpresa en una frase ("mover algo gigante entero", "tu cuerpo hace X sin que lo sepas", "un objeto esconde un truco"). Escríbela al lado de cada tema y compárala con las demás.
- **No se repite la idea de fondo de algo ya publicado** (`docs/PUBLICADOS.md`), ni lo de `docs/IDEAS.md` §3 (lista negra), ni los temas prohibidos de `proyecto/INSTRUCCIONES.md`.

## 4. Filtro de video (estricto, sólo los 20 elegidos)
- **Fuera si hay un video del tema EXACTO con más de 100 mil vistas** en YouTube, en español o en inglés, de cualquier fecha:
  `python3 tools/cazador/quemado.py --estricto "<como lo buscaría alguien en español>" "<en inglés>"` (de a un tema, ~10 s). Si sale REVISAR, lee los títulos y decide si son del tema exacto. Un video de otro tema parecido no quema.
- **TikTok/IG:** se busca en la web ("<tema> tiktok", "<tema> reel"). Si no puedes confirmarlo, escribe **"TikTok/IG sin confirmar"**. Nunca supongas que está libre.
- **Fuente:** 1 fuente seria con link (institución, universidad, paper, medio de ciencia).
- vidIQ casi no tiene créditos (revisa `vidiq_balance` y no gastes más de 10 sin avisar). Reddit no.

## 5. Revisión ciega (antes de mostrarle nada a Tomás)
La hace **un subagente que no armó la ronda** (p. ej. tipo `claude`, sólo lectura). Recibe la lista de temas (gancho + qué es) sin la evidencia ni los puntajes, y por cada uno responde: **"¿Esto se lo mandaría a un amigo ahora mismo?"** (sí/no y por qué, en una línea). Además **bota los que se parecen entre sí**: de cada grupo con la misma idea de fondo queda uno, el que más mandaría. Los temas con "no" y los repetidos no entran al banco.

## 6. Entrega
Los temas que sobreviven se **agregan a `docs/BANCO.md`** con la fecha de la ronda. El detalle de la ronda va en `studio/caza/rondaNN-<nombre>/ronda.md`. En el chat:

| # | Gancho (≤ 12 palabras, la 1.ª frase del video) | Qué es (1 línea) | Idea de fondo | Criterios (3–4 de 4) | Fuente (link) | Video más visto del tema exacto (o "nada") + TikTok/IG | Riesgo |
|---|---|---|---|---|---|---|---|

Ordénalos por cuántos criterios cumplen y por el veredicto del revisor. Si no hay 20 buenos, se entregan menos. Nunca se rellena con temas flojos. Cuando un tema se usa en un video, sale del banco y pasa a `docs/PUBLICADOS.md`.
