# Investigación D — ¿Se puede simular la audiencia con IA? (1-nov-2026)

Subagente de investigación (WebSearch; 2 WebFetch). Etiquetas: [V] leído, [A] de memoria del abstract sin re-verificar, [T] sólo el título, [O] opinión. Las [A]/[T] hay que confirmarlas antes de citarlas afuera.

## Respuesta corta
- Simular una audiencia con un LLM para elegir el gancho ganador tiene **poca evidencia a favor**. Sirve para **filtrar perdedores claros y detectar problemas de comprensión**; no sirve para elegir virales.
- El panel del Ep. 6 (personas demográficas, nota absoluta, texto en vez de imagen, decidir por el chiste) es justo lo que peor rinde según la literatura.
- Lo único que predice de verdad es una **prueba real**: hoy **Trial Reels de Instagram**; cuando salga, el **A/B de cortes de YouTube**.

## Evidencia
- **Maiorano 2026, arXiv 2609.25010 [V]** (el caso más parecido): 399 tests A/B de titulares de Upworthy con ganador confiable. Un **panel de 10 personas demográficas** acertó el ganador el **34,6 %** (azar 30,4 %; τ 0,08). **Un solo "lector típico" sin persona acertó el 49,2 %** (τ 0,36); igual con GPT-4.1. Seis reglas de agregación (mediana, Borda, Condorcet…) no arreglan el panel. En Reddit no predice ninguno. Un autor, sin revisión de pares, con conflicto de interés. Conclusión: **las personas empeoran la predicción**.
- **LOLA (Ye, Yoganarasimhan, Zheng; Marketing Science 2025) [A]:** ~17.700 tests de Upworthy; preguntarle al LLM qué titular gana rinde poco; rinden más modelos entrenados con resultados reales; lo mejor: el LLM propone y un experimento real decide (bandido).
- **Persona-prompted LLM agents (Sci. Reports 2026) y arXiv 2604.19787 [T]:** predicción modesta, no mejor que un clasificador simple.
- **LCBM (Khandelwal et al., ICLR 2024) [A]:** GPT-3.5/4 sin entrenar en comportamiento simulan mal likes y vistas.
- **Silicon samples:** Argyle 2023 (reproduce voto agregado) [A]; Horton 2023 (replica cualitativamente experimentos) [A]; Hewitt et al. 2024 (GPT-4 predijo efectos de 70 experimentos de encuesta, r ≈ 0,85) [A]; Park et al. 2024 (agentes de 1.052 personas replican sus respuestas al 85 %, pero cada uno salió de una entrevista de 2 h) [A]; Maier et al. 2025, PyMC Labs + Colgate (Likert directo da distribuciones irreales; texto libre + similitud semántica llega a ~90 % de la confiabilidad test-retest humana; mide intención de compra, no deslizamiento) [A].
- **Sesgos:** poca varianza y sensibilidad al prompt (Bisbee 2024) [A]; aplanan y estereotipan grupos (Wang et al. 2025, Nature MI) [A] — diez "personas" del mismo modelo no son diez muestras; **sesgo de posición** en comparaciones de a pares (Shi et al. 2024) [A] → siempre A/B y B/A; **humor**: los modelos rankean chistes peor que humanos (Hessel et al., ACL 2023) [A]; Kantar: GenAI "tal cual" no sirve como muestra sintética [T].
- **Modelos de engagement de video corto:** SnapUGC (ECCV 2024; ~90 mil videos con la tasa de seguir viendo pasados 5 s) [A]; ganador VQualA ICCV 2025 (modelos multimodales **entrenados** con esas etiquetas; el audio aporta) [A]; Kayal et al. 2025 (~80 % separando popular de no popular con descripciones; contrastes grandes; sin re-verificar) [A].
- **Límite de fondo:** Salganik, Dodds y Watts 2006 (Science): lo mejor rara vez fracasa y lo peor rara vez triunfa; el resto es lotería. Martin et al. 2016: aun con mucha información se explica menos de la mitad de la varianza del tamaño de una cascada [A].

## Por qué falló el panel del Ep. 6 [O]
1. Personas demográficas (lo que peor rinde). 2. Juzgó texto y la falla fue de ejecución ("no se entendía" no aparece en una descripción). 3. Nota absoluta ~7, comprimida y optimista. 4. Ganó por el chiste (punto ciego documentado). 5. Nunca se comparó con resultados reales.

**Nuestros números (n = 6, muy débil):** en "se quedó" de YouTube los dos ganadores (Ep. 3 y Ep. 7) quedaron 3.º y 5.º; los separaron la retención (73,7 y 89,3 % visto), los envíos del Ep. 3 en IG (9.776) y el concepto. Spearman entre "pasa 3 s" de IG y "se quedó" de YT ≈ **0,09**: sólo coinciden en el perdedor claro (Ep. 5). **El gancho filtra desastres; lo que separa a los ganadores es la idea + la retención.**

## Alternativas reales y baratas
- **Instagram Trial Reels** (desde dic-2024): se muestran primero a no seguidores; sirve para probar 2–3 ganchos del mismo video como trials separados (de guías de uso, no de estudios). IG agregó tasa de salto y gráfico de retención. Ruido: hora y día; con el alcance actual sólo se leen diferencias grandes, y no se traspasa fino a YouTube.
- **YouTube:** Test & Compare es para títulos y miniaturas; en Shorts no hay A/B. El **23-sep-2026 YouTube anunció "Video A/B Testing"**: hasta 3 cortes con curvas de retención por corte; la demo dice "test hooks" para Shorts [V]. No está liberado ni tiene requisitos publicados: revisar Studio cada semana.
- **No publicar 2–3 cortes casi iguales en público** [O]: "contenido no auténtico/repetitivo" en el YPP, IG castiga duplicados y se canibalizan.
- **vidIQ Outliers:** proxy de **demanda por la idea**, no del gancho.
- **5–10 personas reales** viendo los primeros 2 s sin sonido y diciendo "¿qué es esto?": gratis y mide comprensión, que fue la falla real.

## Protocolo recomendado (resumen; lo que se adoptó está en `docs/GUIONISTA.md` §5)
0. Set de calibración: cuadros 0–3 s de los publicados con resultados guardados aparte; externos: 20–30 pares de outliers ≥ 5× contra ≤ 1× del mismo canal (vidIQ).
1. **Comprensión (bloqueante):** 5 subagentes ven sólo 0–1,5 s sin sonido y dicen qué pasa y qué prometen (≤ 10 palabras); pasa con 4 de 5 que coinciden con la promesa declarada.
2. **Duelo de deslizamiento de a pares, sin persona, con cuadros reales**, 12 votos (6 jueces × 2 órdenes); decide sólo con ≥ 9/12 y el mismo resultado en los dos órdenes; si no, empate → Trial Reels.
3. **Retención:** busca problemas (segundo donde se pierde el hilo, > 2 s sin cambio, escenas pegadas) + red-team "¿por qué este sería el peor video?".
4. **Calibración pre-registrada** con umbrales fijados antes de mirar.
5. **Cerrar el ciclo:** anotar la predicción antes de publicar y compararla a las 48 h; si acierta < 60 % en 10 videos, pierde el voto.

**No confiar** si no pasó la calibración, si los votos se dividen o cambian al invertir el orden, si se juzgó texto, si decide el humor/voz/música, si las variantes son casi iguales, si la pregunta es "¿se va a viralizar?", o si contradice un Trial Reel real.

## Para leer completas
1. https://arxiv.org/abs/2609.25010 · 2. https://arxiv.org/abs/2406.02611 · 3. https://arxiv.org/abs/2510.08338 · 4. https://www.cambridge.org/core/product/B92267DC26195C7F36E63EA04A47D2FE · 5. https://arxiv.org/abs/2402.01908 · 6. https://ar5iv.labs.arxiv.org/html/2209.06899 · 7. https://arxiv.org/abs/2411.10109v1 · 8. https://www.nature.com/articles/s41598-026-66277-8 · 9. https://arxiv.org/pdf/2604.19787 · 10. https://arxiv.org/abs/2508.02516 · 11. https://arxiv.org/html/2410.00289v1 · 12. https://arxiv.org/html/2406.07791v5 · 13. https://pdodds.w3.uvm.edu/research/papers/years/2006/salganik2006a.pdf · 14. https://ppc.land/youtube-to-test-up-to-3-versions-of-one-video-on-real-viewers-shorts-too/ · 15. https://buffer.com/resources/instagram-trial-reels/
