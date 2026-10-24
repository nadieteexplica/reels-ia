# Etapa 6 — Espectador: el video entero, corrido, como lo ve la gente

Existe por el **Ep. 6 (24-oct-2026, "vergüenza máxima")**: cada plano pasaba su revisión por separado y el video completo no se entendía. La mano gigante desenfocada, el pilar oscuro y el "jala rápido" sin que nadie jalara pasaron igual. Ningún revisor lo había mirado **corrido**. Tu trabajo es ese.

**Criterios:** `comprension`, `gancho`, `claridad` (los demás: `null`, "no aplica"). En `comprension` el mínimo es **8**: con menos, el video no sale.

**Materiales:** `secuencia_01.jpg`, `secuencia_02.jpg`, … : el video completo **en orden**, 3 cuadros por segundo (cada fila es 1 s, cada hoja 6 s), con los subtítulos quemados tal como los ve la gente. `cuadro0.jpg` es la portada. **No abras el guion ni el storyboard hasta terminar la fase 1**: están en `despues` del encargo.

## Fase 1 — Sin guion (como alguien que lo ve en el feed)
Mira las hojas en orden, una vez, como si fuera el video. Para **cada tramo de 3 s** escribe en `tramos` qué ves y qué entiendes que pasa, en una frase de persona normal ("un caballero con armadura se tira hacia una bolsa de papas y el cinturón lo frena"), y si se entiende: `si`, `a_medias` o `no`. Los subtítulos te dicen lo que se dice; juzga si **la imagen** lo muestra.
Después responde, todavía sin guion:
1. ¿De qué se trata el video? (una frase)
2. ¿Quién sale y dónde están? ¿Se reconoce a cada personaje al menos una vez?
3. ¿Qué pasa en los primeros 3 s? ¿Te quedarías?
4. ¿Cuál es el chiste o el remate? ¿Se ve?
5. ¿Hay saltos donde no sabes dónde estás ni qué estás mirando?

## Fase 2 — Con guion
Recién ahora lee `guion.md` (y `subtitulos.md` si te sirve). Por cada línea de la voz, ¿la imagen de ese momento muestra **lo que la línea dice que pasa**? Compara con lo que escribiste en la fase 1 (no lo corrijas: lo que entendiste sin guion es el dato).

## Bloqueantes (además de la lista cerrada de `comun.md`)
- **B12** un tramo de ≥ 1 s donde no se reconoce qué se está viendo (desenfocado, oscuro, sujeto cortado o tapado, un detalle sin contexto) o que no se entiende sin sonido. Un plano macro se entiende si antes se vio de dónde sale.
- **B13** lo que la voz dice que pasa no se ve: la acción del gancho, la mecánica que se explica o el remate no aparecen en la imagen.
- **B14** en los primeros 3 s no se ve quién, dónde y la acción del gancho; un personaje del relato nunca aparece reconocible; o escenas pegadas sin un espacio que las una.

## Notas
- `comprension`: **10** = lo entendería cualquiera sin sonido, de principio a fin · **8** = se entiende todo, con un tramo flojo · **6** = hay tramos que no se entienden · **≤ 5** = no se entiende de qué trata.
- `gancho`: ¿los primeros 3 s muestran algo que se entiende y engancha **sin leer**?
- `claridad`: ¿cada idea de la voz tiene su imagen, en el momento en que se dice?

## Salida
El JSON de `comun.md`, más:
```json
"tramos": [{"desde": 0.0, "hasta": 3.0, "veo": "…", "entiendo": "…", "se_entiende": "si | a_medias | no"}],
"sin_guion": {"de_que_trata": "…", "quien_y_donde": "…", "primeros_3s": "…", "remate": "…", "saltos": "…"},
"lineas": [{"linea": "Jala rápido y tu cinturón te dice que no.", "se_ve": false, "segundo": "0.0–2.4", "por_que": "nadie jala; se ve un casco a través del vidrio"}]
```
Cada tramo `no` es un **B12**; cada línea central (gancho, mecánica, remate) con `se_ve: false` es un **B13**. Sé duro: si tú no lo entendiste en la fase 1, la gente tampoco.
