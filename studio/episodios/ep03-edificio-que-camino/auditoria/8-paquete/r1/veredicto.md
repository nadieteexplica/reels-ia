# 8-paquete · ronda 1 · **APROBADO**

Promedio **8.0** (mínimo 8; ningún revisor bajo 7 en ningún criterio).

| criterio | nota (promedio) | más baja | por qué (la más baja) |
|---|---|---|---|
| textos | 9.0 | 9 | El gancho 'Este edificio de más de 7.600 toneladas se fue caminando' calza con el video sin prometer de más. La línea del dato repite exacto lo del guion (1935, 2020, 62 m, 198 patas, dos grupos que se turnan). La pregunta '¿Qué edificio de tu ciudad pondrías a caminar?' es abierta. El título de YouTube parte con 'Edificio que caminó', sin faltas y con pocos emojis. Lo único que falta es 'China' como palabra de búsqueda. |
| cumplimiento | 7.0 | 7 | Bien: la etiqueta IA de Instagram y TikTok, madeForKids false, el título de TikTok y el primer comentario, con 5 enlaces del guion que cargan y dicen lo afirmado (7.600 t, 198 patas, 62 m, 18 días, 21°, sala de conciertos a 66,46 m en 2003). Falla: la descripción de YouTube nombra 7 fuentes sin ningún enlace, y el encargo pide enlaces. Además, isAiGeneratedContent false choca con el '3D semi-realista' que dice el guion (línea 5). |

## Bloqueantes y fallas automáticas (impiden aprobar)

Ninguno.

## Sugerencias (las 5 más importantes; el resto queda en veredicto.json)

1. La descripción de YouTube ('Fuentes: CNN (2020) · BBC Mundo (2020) · ...') no trae ningún enlace, y su lista (7 medios, con Construction Equipment y The Urban Developer) es distinta de la del primer comentario (5 medios con enlace). El chequeo automático de 'fuentes' no lo pilló, seguramente porque sólo mira el primer comentario.. **Arreglo:** Poner en la descripción la misma lista del primer comentario, con sus 5 URL. Si se quieren dejar Construction Equipment y The Urban Developer, agregarlas en las dos partes con la URL que tienen en guion.md.
2. YouTube va con isAiGeneratedContent false porque el texto lo llama 'animación 3D estilizada'. Pero guion.md (línea 5) define el formato como '3D semi-realista', y el video muestra un hecho real en un lugar real (Shanghái), del que además circula video real. Con lo que tengo no puedo ver si el render se puede confundir con una grabación.. **Arreglo:** Mirar la portada (C0) y dos o tres cuadros del render final. Si la calle o el edificio se ven fotorrealistas, poner isAiGeneratedContent true. Si se ven claramente animados, dejar false y anotar en caption.md por qué.
3. Los textos nunca dicen 'China', que es la palabra con que la gente busca este caso (el titular de Xataka parte con 'China utiliza 198 patas robóticas...'). Sólo aparece 'Shanghái' y #shanghai.. **Arreglo:** En la línea del dato de Instagram/TikTok y al inicio de la descripción de YouTube escribir 'en Shanghái (China)'. Opcional: agregar #china como quinto hashtag.
4. La pregunta para comentarios es divertida, pero no usa la discusión que el guion buscaba ('¿no era más fácil hacer las oficinas en otro lado?'), que es la que genera respuestas en contra y conversación.. **Arreglo:** Probar '¿La habrías movido o demolido para hacer oficinas? 👇', o dejar la actual y usar esta en el primer comentario después de las fuentes.
