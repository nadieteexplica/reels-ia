---
name: guion
description: Escribe el guion de un video de El viejo del dato: ficha verificada, 3 guionistas en paralelo con estructuras distintas, duelo ciego de 12 ganchos (y contra los ganchos virales), juez-viral parte por parte con copia ciega, espectadores buscando fugas, máximo 2 reescrituras o se cambia la idea. Usar después de que Tomás elige la idea.
---

# Guion

Marco: `docs/REGLAS.md` (reglas duras, criterios con nivel de evidencia y qué decide). Aquí, lo único **[DURA]** es la verdad con 2 fuentes; todo lo demás es criterio. Los jueces **orientan**: si contradicen lo que muestran las métricas o el ojo de Tomás, mandan las métricas y Tomás. Si decides pasar por encima de un juez, lo anotas en `guion.md` con el porqué.

## 0. Ficha y verdad (tú) **[DURA]**
`studio/episodios/<ep>/ficha.md`: el dato central con **2 fuentes confiables e independientes leídas** (no Wikipedia), la mecánica en pasos, cifras exactas, lo que no se sabe. Sin ficha verificada no se escribe nada.

## 1. Tres guionistas en paralelo
- 3 estructuras de A/B/C/D, distintas a la del video anterior (`docs/ROTACION.md`) **[HIPÓTESIS: variar evita "contenido inauténtico" y no sabemos cuál rinde más]**.
- Lanza 3 `guionista` **en el mismo mensaje**: ficha, estructura, carpeta `studio/episodios/<ep>/guionista/<X>/`. Cada uno entrega `ganchos.json` (4) y `guion.md` con su sección `## Texto para la voz`.
- Apertura: cada guion anota si es **raro** (lo imposible primero) o **normal→escala** (algo normal que escala antes de 3 s) **[HIPÓTESIS]**; se alterna entre videos y se compara con "visto vs. deslizado" cada 4–6 videos. Las fórmulas de apertura de los virales se pueden reutilizar con otro tema: compiten en el duelo como cualquier gancho.

## 2. Duelo ciego de los 12 ganchos (orientación)
1. Junta los 12 en `studio/episodios/<ep>/guionista/ganchos.json` (`{"candidatos": [...]}`).
2. `python3 tools/guionista/duelo.py preparar studio/episodios/<ep>/guionista --jueces 4` → 4 `juez-gancho` en paralelo, cada uno con su `duelo/juezN.md` (la clave queda en `_claves/`, fuera de su alcance). Los jueces no escriben: pega cada respuesta cruda en el scratchpad y `python3 tools/guardar_veredicto.py <crudo> duelo/resultados/juezN.json`. `duelo.py contar …` → gana uno.
3. Contra los virales: el ganador y el 2.º en una carpeta aparte, `duelo.py preparar <carpeta> --anclas virales --jueces 4`, guardar, `contar … --anclas virales`. **Piso: que gane o empate contra la mayoría de los ganchos virales** [PROBABLE como filtro; con texto queda sesgado a favor del candidato, `duelo.py` lo advierte]. Si los dos pierden → los guionistas reescriben ganchos (cuenta como reescritura 1).

## 3. juez-viral, parte por parte (orientación)
- El guionista de esa estructura pone el gancho ganador en su guion (paquete, primera frase, texto de la voz y loop: los 4; lección 176).
- Copia ciega de cada guion: `python3 tools/guionista/copia_ciega.py <guion.md> <scratchpad>/ciega-<X>.md` (sin predicción, autorrevisión ni nombre del guionista). Lanza 3 `juez-viral` en paralelo, cada uno con su copia ciega y las rutas de las fichas de `docs/referencias/virales/`. Guarda cada respuesta con `tools/guardar_veredicto.py` en `studio/episodios/<ep>/guionista/juez-viral-<X>.json`.
- Pasa con 3 GANA o 2 GANA + 1 EMPATA **y sin tramos en `segundos_sin_novedad`** [PROBABLE: varios virales cambian algo cada 2–6 s y la retención cae en los tramos muertos]. Si pasan varios: el de más GANA; empate → el más corto.
- Si ninguno pasa: el guionista del mejor corrige sólo lo que señaló el juez → `guion_v2.md` → otro `juez-viral` nuevo y ciego. **Máximo 2 reescrituras.** Si no pasa: idea descartada (anotada en `docs/IDEAS.md` con el porqué) y se toma la siguiente de la ronda del cazador, sin pedirle correcciones a Tomás.

## 4. Espectadores (fugas, orientación)
`python3 tools/guionista/feed.py <ep>` → 6 `espectador` en paralelo, respuestas guardadas con `guardar_veredicto.py`, `puntuar.py`. La frase donde se va gente se reescribe y vuelve a juez-viral. Ojo: `puntuar.py` avisa cuando el simulador no reproduce los resultados reales; ahí sus números sólo orientan.

## 5. Entrega
`studio/episodios/<ep>/guion.md`: idea central, guion con segundos, cuadro 0, tipo de apertura, verificación por afirmación, fuentes, `## Texto para la voz`, y el resultado del duelo y de juez-viral (y si pasaste por encima de algún juez, por qué).

## Criterios de escritura (detalle y nivel de cada uno en `docs/GUIONISTA.md`)
- Algo nuevo cada 4–6 s, cero relleno, "pero / por eso" en vez de "y después" [PROBABLE].
- Un ancla concreta en los primeros 5 s que vuelve al 60–90 %, y un re-gancho a mitad [PROBABLE: virales con /watch].
- Cierre: remate (la frase más fuerte) + loop + "mándaselo a…" ligado al contenido, con una persona concreta del tema [PROBABLE: virales + investigación].
- Duración 35–50 s, ~110–150 palabras a ~3,1 pal/s; si no cabe, se sacan pasos [HIPÓTESIS: se mide con % visto].
