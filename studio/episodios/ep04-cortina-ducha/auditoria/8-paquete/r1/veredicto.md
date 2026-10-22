# 8-paquete · ronda 1 · **APROBADO**

Promedio **8.5** (mínimo 8; ningún revisor bajo 7 en ningún criterio).

| criterio | nota (promedio) | más baja | por qué (la más baja) |
|---|---|---|---|
| textos | 8.0 | 8 | Gancho coherente con el video y la portada ('te persigue... y no es un fantasma'), dato igual de exacto que el guion (remolino acostado, centro de baja presión, aire de afuera empuja, pasa con agua fría y con caliente más fuerte), pregunta abierta que invita a comentar, títulos de YouTube y TikTok con 'cortina de la ducha' / 'por qué' al inicio, sin faltas y con emojis medidos; no sube a 9 porque no nombra el 'efecto cortina de ducha' (lo que la gente busca) ni empuja el envío, que es la acción buscada. |
| cumplimiento | 9.0 | 9 | Descripción de YouTube y primer comentario traen 5 fuentes del guion con enlace, y cada dato extra de la descripción tiene respaldo en ellas (eje perpendicular a la cortina: Scientific American; simulación de 2001 y Eastwell 2007: Popular Science; Ig Nobel 2001: Mental Floss y ScienceABC; cortina más pesada: ScienceABC); etiquetas IA en Instagram y TikTok, madeForKids false, TikTok con título, sin 'sígueme', sin anatomía (no requiere crédito). Sólo falta la 6.ª fuente del guion (NASW). |

## Bloqueantes y fallas automáticas (impiden aprobar)

Ninguno.

## Sugerencias (las 5 más importantes; el resto queda en veredicto.json)

1. caption.md › Instagram/TikTok (línea del dato) y primera frase de la descripción de YouTube: ningún texto nombra el fenómeno por su nombre, 'efecto cortina de ducha', que es como se busca (en español y en inglés 'shower curtain effect'); hoy sólo aparecen 'cortina de la ducha' y 'por qué'.. **Arreglo:** Abrir la línea del dato con 'Es el efecto cortina de ducha: el chorro arma un remolino acostado...' y meter las mismas palabras en la primera o segunda frase de la descripción de YouTube. No cambia el largo del título.
2. caption.md › Instagram/TikTok: la acción buscada del guion es 'enviar' (a quien siente que en su casa penan), pero el texto no lo pide; los envíos por alcance son la métrica principal en Instagram y TikTok.. **Arreglo:** Unir el envío a la pregunta sin agregar líneas: '¿Qué otra cosa de tu casa parece embrujada? Mándaselo a quien jura que en su casa penan 👇'.
3. caption.md › descripción de YouTube y primer comentario: listan 5 de las 6 fuentes del guion; falta NASW ScienceWriters (respalda que la cortina 'se pega' al cuerpo, lo mismo que dice el título 'se te pega'). Las 5 que están bastan para cada dato, así que no es falta de respaldo.. **Arreglo:** Agregar en ambos la línea '• NASW ScienceWriters: https://nasw.org/sites/default/files/sciencewriters/html/win0102tex/shower.htm' para que las listas calcen con el guion.
4. caption.md › Datos para Metricool: isAiGeneratedContent false se justifica como 'animación 3D estilizada', pero guion.md llama al formato '3D semi-realista'. Material insuficiente para verificar el estilo desde este encargo.. **Arreglo:** Dejar false si el baño del render final no puede pasar por una grabación real (cara de fantasma, corte con etiquetas); si algún plano del baño se ve fotográfico, pasarlo a true. Unificar la palabra en los dos documentos.
