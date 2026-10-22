# YouTube primero — algoritmo de Shorts, monetización y plan (21-oct-2026)

Tomás decidió el 21-oct-2026 concentrar el proyecto en YouTube, porque es la red que paga desde Chile. Este documento junta la investigación de ese día y lo que él decidió. Los números entre corchetes remiten a la lista de fuentes del final (extractos bajados con `fuentes.yml`, prerelease `yt-fuentes`).

## Decisiones de Tomás (21-oct-2026)
1. **Duración: 25–40 s, techo 45 s.** En código: `presupuesto.json` → 25–45,5 s y 70–128 palabras.
2. **Cadencia: 5 por semana ahora y diario cuando un video tome ≤ 2,5 h**, con 2 videos por sesión. En código: tope de 4 h, meta 2,5 h y máximo 6 escenas.
3. **Instagram y TikTok siguen recibiendo el mismo video**, sin trabajo extra; todo se optimiza para YouTube.
4. **Compilaciones largas: muy de vez en cuando**, no con calendario fijo.
5. **Métrica principal en YouTube:** visto vs. deslizado, % visto y vistas comprometidas (YouTube Studio).

## 1. Cómo decide el algoritmo de Shorts (en palabras de YouTube)
- Cada Short se le muestra primero a una **audiencia semilla** chica. Según si la gente lo mira o lo desliza, YouTube lo abre a más gente o lo deja morir (Todd Sherman, jefe de producto de Shorts, Creator Insider, 23-ago-2023) [1][3][4].
- La señal de entrada es **"Visto vs. deslizado"** (está en YouTube Studio). Es el equivalente al CTR del video largo: en el feed nadie elige por miniatura, **lo primero que se ve es el primer segundo del video** [1][2][3].
- Después pesan el tiempo visto, las repeticiones, los likes, los compartidos y los comentarios [4][5]. YouTube no publica pesos: "la audiencia es el algoritmo" [3].
- **Vistas:** desde marzo de 2025 cuenta cada inicio y cada repetición. Para entrar al YPP y para cobrar cuentan las **vistas comprometidas o calificadas** (las que pasan los primeros segundos) [1][2][10].
- Un Short puede despegar tarde: la ventana de 90 días cuenta vistas de videos viejos [7].
- **Largo:** Sherman recomienda pensar en la historia y no en una duración fija [3].
- **Miniatura:** el feed no la muestra. Desde el 25-jul-2026 hay miniaturas personalizadas para Shorts, sólo para canales del YPP (se ven en ~3:2, sin prueba A/B); el resto elige un cuadro del video [21][22].

## 2. Monetización: los números
| Qué | Requisito |
|---|---|
| YPP hoy (hasta el 31-ene-2027) | 1.000 suscriptores + 10 M vistas de Shorts en 90 días, o 4.000 h de video largo en 12 meses [7][17] |
| **YPP para los que entran desde el 1-feb-2027** | 1.000 suscriptores + **20 M vistas calificadas de Shorts en 90 días (~222 mil al día)** o **8.000 h** de video largo en 365 días [6][7][9] |
| **Cobrar del pool de Shorts cada mes (desde el 1-feb-2027, también los que ya están)** | Mantener **10 M vistas calificadas en 90 días** (ventana que termina el día 15 del mes anterior). Si no se llega, se pausa sólo lo de Shorts; el video largo sigue pagando [6][10] |
| Escalón previo (no cambia) | 500 suscriptores + 3 M vistas de Shorts en 90 días (o 3.000 h): membresías, Super Thanks, Shopping y **YouTube Creator Partnerships** (marcas). No da anuncios [6][8] |
| Cómo se paga Shorts | Los anuncios entre Shorts forman un pool; se reparte según el % de vistas comprometidas de cada creador en cada país; el creador se queda con el 45 % [10] |
| Nuevo en 2027 | Bonos por Shopping, "créditos de producción" para acuerdos con marcas y 45 % directo de anuncios dirigidos a 5 canales o menos [6][8] |

- **RPM de Shorts:** US$0,01–0,33 por mil vistas; Brasil ~US$0,045; un millón de vistas de público mixto deja ~US$150–250 [17]. El público hispano de Latam está en la parte baja. **Estimación nuestra:** ~US$0,03–0,06 por mil, o sea **10 M vistas ≈ US$300–600 cada 90 días**.
- Zack D. Films (29,2 M suscriptores, 80.200 M vistas) gana, según la estimación de OutlierKit, US$3–18 mil al mes por anuncios [24]. Hasta el n.º 1 del formato gana poco por Shorts: la plata está en las marcas y en el video largo.
- **Conclusión:** llegar al YPP antes del 1-feb-2027 por Shorts (10 M vistas en 90 días partiendo de 10 suscriptores) no es realista; hay que planear con la regla de 2027. **Shorts es el motor de crecimiento; la plata viene del video largo (RPM mucho más alto, y sus horas también sirven para entrar) y de las marcas.**
- **Facebook** también paga por vistas desde Chile (por invitación; ver `CONTEXTO.md` → Monetización), así que YouTube no es la única opción: es la principal.

### Cuánto paga en pesos (cálculo del 21-oct-2026, dólar a $975,68)
- 10 M vistas en 90 días ≈ 3,3 M al mes. Con público latino (~US$0,03–0,06 por mil; Brasil, el único latino medido, está en US$0,045) → **~US$100–200 al mes ≈ $100–195 mil**.
- Para entrar desde febrero de 2027 hacen falta 20 M en 90 días → **~US$200–400 al mes ≈ $195–390 mil**.
- Si una parte del público es de EE. UU. (US$0,33 por mil), sube. Ejemplo: 20 % de EE. UU. y 80 % latino ≈ US$0,10 por mil, casi el doble.
- Paga en proporción a las vistas comprometidas: el doble de vistas, el doble de plata.

## Checklist para el YPP (22-oct-2026; canal con ~25 suscriptores)
**Todavía no se puede postular:** el botón "Postularse ahora" de Studio → Ingresos aparece recién al cumplir 1.000 suscriptores + 10 M vistas de Shorts en 90 días (20 M para los que entran desde el 1-feb-2027). Después de postular, la revisión toma ~1 mes; si te rechazan, se puede apelar en 21 días o volver a postular a los 30.

**Lo que Tomás deja listo ahora:**
1. Verificación en 2 pasos en la cuenta de Google del canal.
2. Funciones avanzadas: Studio → Configuración → Canal → Elegibilidad de funciones (verificar con el teléfono). También habilita las miniaturas personalizadas y los videos de más de 15 min, que sirven para las compilaciones.
3. País de residencia = Chile (Studio → Configuración → Canal → Información básica).
4. Studio → Ingresos → "Recibir notificación".
5. Nombre "El viejo del dato" y handle @elviejodeldato en YouTube (e Instagram), más la descripción del canal.
6. Valores de carga predeterminados: "No, no es para niños".
7. Revisar que no haya faltas por los Lineamientos de la Comunidad.

**Al postular (más adelante):** aceptar las condiciones básicas y crear AdSense para YouTube desde Studio (no antes), y después llenar la info tributaria de EE. UU. en AdSense.

## 3. Frecuencia
- vidIQ (10,2 M canales, abr-2025 a mar-2026): el crecimiento sube en cada escalón de frecuencia; con 12 o más subidas al mes, 4,1× el crecimiento de vistas de los que suben menos de una al mes. Es correlación, no causa [11].
- Metricool 2026 (799.718 videos): en Shorts **no hay techo claro**: más publicaciones dan más vistas al mes, porque cada una es otra oportunidad en el feed. El límite es la calidad. (En video largo, lo mejor es 2–4 por semana.) [27]
- vidIQ: los canales con 200 Shorts o más ven un alza sostenida [2].
- AIR: partir con 1 diario y subir; publicar de más con una premisa repetida o con calidad diluida mata el alcance y se lee como "slop" [20][26].
- YouTube no premia la frecuencia en sí: cada Short se juzga solo. Más Shorts = más boletos [1][3].

## 4. Duración
- quso.ai (108 mil Shorts maduros): la mediana de vistas es máxima en **11–20 s (901)**; baja a 347 en 31–45 s, 188 en 46–60 s y 51 sobre 90 s. Es correlación [15].
- Metricool 2026: el tiempo promedio visto por Short es **~16 s** (32 s menos que el año anterior) [12].
- OpusClip/Bytecap: 30–60 s cuando hace falta gancho, idea y remate; el largo correcto es la versión más corta que conserva el remate [14].
- Un Short de más de 1 min con contenido reclamado por Content ID se bloquea [10]: nuestra música propia o sintetizada nos protege.
- **Nuestros 3 videos duran 64–74 s: entre 2 y 4 veces el punto dulce.**

## 5. Lo que YouTube no monetiza ("contenido no auténtico", julio de 2026)
Tres tipos [18][19][20]:
1. **Genérico, repetitivo o de plantilla**: explícitamente, lo que se hace fácil con IA, CGI o plantillas con poca variación entre videos.
2. Contenido angustiante o manipulador para buscar vistas.
3. **Personas de IA que hablan de temas sensibles como salud o finanzas.**

Se evalúa por canal, no por video. Para nosotros:
- Diseñar cada idea desde cero (decisión de Tomás del 19-oct) es nuestra protección. El kit puede reutilizar **técnica** (luces, subtítulos, audio, esqueletos, cámara), no **la apariencia** de los videos.
- Salud: el dato curioso sí; nada que suene a consejo, y con menos peso en el banco de ideas, porque la voz es sintética.

## 6. Shorts y video largo
- ~6 de cada 10 vistas orgánicas de YouTube vienen del feed de Shorts [27].
- Con ~5 Shorts al mes, el video largo del canal rinde 46 % sobre lo típico; sobre 35 Shorts al mes el efecto se pierde [27].
- El video largo más exitoso de Zack D. Films es una **compilación** ("13 videos no publicados…", 10 M vistas) [24].
- **Decidido:** compilaciones de 5–8 min con capítulos e intro nueva **muy de vez en cuando** (Tomás). Suman horas de video largo sin animar nada nuevo; los Shorts que salen en ella la enlazan con "video relacionado".

## 7. Horario
Los Shorts se concentran entre 14:00 y 18:00, y el contenido pesa más que la hora [27]. Nuestro 16:00 de YouTube está bien; se compara con el 10:00 del Ep. 3.

## 8. Lo que hacemos vs. lo que pide YouTube
| Tema | Antes | Qué pide YouTube | Desde el 21-oct-2026 |
|---|---|---|---|
| Duración | 64–74 s | Rinde más en 11–30 s; hasta ~45 s si la historia lo pide | **Meta 25–40 s, techo 45 s** |
| Cadencia | 3 por semana, 5,5 h por video (Ep. 3) | Más es mejor si no baja la calidad | 5 por semana ahora → diario cuando un video tome ≤ 2,5 h |
| Primer segundo | Imagen absurda en el cuadro 0 | Es la "miniatura" del feed | Mantener |
| Final en loop | Sí | Cada repetición cuenta | Mantener |
| Métrica principal en YouTube | Envíos/alcance | Visto vs. deslizado, % visto, vistas comprometidas | Cambiar (las de IG/TikTok siguen igual) |
| Variedad visual por idea | Sí | Protege de "no auténtico" | Mantener |
| Video largo | Nada | Horas para el YPP de 2027 y RPM más alto | Compilación muy de vez en cuando |
| Datos de YouTube | Metricool (2 días de atraso, sin "visto vs. deslizado") | — | Leer YouTube Studio en el Chrome de Tomás |

## 9. ¿Cabe uno diario?
- **Voz:** ~1 crédito por carácter. Un guion de ~35 s tiene ~100 palabras (~600 caracteres). 30 videos × 1,3 tomas ≈ **23.000 de 40.000 créditos. Cabe.**
- **Tiempo:** el Ep. 3 (63 s, 36 planos, 9 escenas) tomó 5,5 h. Diario así serían ~38 h de sesiones por semana. A 30–35 s (~15–18 planos, 6 escenas como máximo, 1 ronda del auditor + revisión del final) la meta es **≤ 2,5 h por video**, y 2 videos por sesión.
- **Uso de Claude:** el Ep. 2 gastó ~26 % del uso semanal de Tomás en 22,7 h; el Ep. 3, **~7 %** (dato de Tomás). A 25–40 s se estima ~4–5 % por video: diario ≈ 30–35 % a la semana. Cabe.
- **Render:** GitHub Actions es gratis (repo público).

## Fuentes
1. https://outlierkit.com/resources/youtube-shorts-algorithm/
2. https://vidiq.com/blog/post/youtube-shorts-algorithm/
3. https://www.searchenginejournal.com/youtube-explains-how-shorts-algorithm-works/494953/
4. https://www.mediapost.com/publications/article/388588/youtube-shorts-product-lead-offers-insights-for-cr.html
5. https://www.socialmediatoday.com/news/youtube-advice-for-shorts-creators-hashtags-algorithm/691835/
6. https://support.google.com/youtube/answer/12843009?hl=en
7. https://www.searchenginejournal.com/youtube-updates-partner-program-terms-shorts-payout-rules/585331/
8. https://www.newsshooter.com/2026/08/10/youtube-updates-its-partner-program/
9. https://www.techtimes.com/articles/323954/20260811/youtube-partner-program-doubles-entry-bar-adds-monthly-shorts-earnings-gate.htm
10. https://support.google.com/youtube/answer/12504220?hl=en
11. https://vidiq.com/research/youtube-upload-frequency-study/
12. https://metricool.com/youtube-trends/
13. https://www.adobe.com/express/learn/blog/youtube-shorts-length-study (no se pudo bajar: 403)
14. https://www.bytecap.io/research/best-youtube-shorts-length
15. https://quso.ai/research/youtube-shorts-length
16. https://air.io/en/monetization/what-rpm-can-you-expect-from-shorts-in-2026
17. https://air.io/en/monetization/comparing-shorts-monetization-to-tiktok-creator-rewards
18. https://techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/
19. https://tubefilter.com/2026/01/29/youtube-ai-slop-channel-crackdown-bans/
20. https://air.io/en/news-air/how-youtube-treats-ai-in-2026-new-update
21. https://www.tubefilter.com/?p=193294
22. https://www.relevantaudience.com/social-media-marketing/youtube-shorts-custom-thumbnails-no-ab-testing/
23. https://air.io/en/audience-growth/do-youtube-shorts-help-your-long-form-videos-grow-data-from-18000-channels
24. https://outlierkit.com/channel/zackdfilms
25. https://blog.youtube/intl/es-419/culture-and-trends/llegando-mas-lejos-con-video-corto/
26. https://air.io/en/youtube-hacks/how-often-should-you-post-shorts-to-grow-faster
27. https://metricool.com/how-to-grow-on-youtube/
