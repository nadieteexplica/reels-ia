---
name: guion
description: Escribe el guion de un video de El viejo del dato con la regla del guion (docs/GUIONISTA.md §0): 3 guionistas en paralelo con estructuras distintas, duelo ciego de 12 ganchos que además tiene que ganarle a los ganchos virales, juez-viral parte por parte, espectadores buscando fugas, máximo 2 reescrituras o se cambia la idea. Usar después de que Tomás elige la idea.
---

# Guion

**Regla (máxima prioridad):** ningún guion le llega a Tomás si no le gana a los virales de `docs/referencias/virales/` según `juez-viral`. Si no llega en 2 reescrituras, se descarta la idea y se toma la siguiente de la ronda, sin pedirle correcciones a Tomás.

**Lo que tienen los virales con /watch** (`docs/referencias/virales/README.md`): un **ancla** concreta presentada en los primeros 5 s que vuelve al 60–90 %; un **re-gancho** explícito a mitad; si el guion no cabe en ~45 s a ~3,1–3,4 pal/s, se **sacan pasos**, no se acelera.

## 0. Ficha y verdad (tú)
`studio/episodios/<ep>/ficha.md`: el dato central con **2 fuentes independientes leídas** (no Wikipedia), la mecánica en pasos, cifras exactas, lo que no se sabe. Sin ficha verificada no se escribe nada.

## 1. Tres guionistas en paralelo
- Elige 3 estructuras de A/B/C/D **distintas a la del video anterior** (`docs/ROTACION.md`).
- Lanza 3 subagentes `guionista` **en el mismo mensaje**, cada uno con: ruta de la ficha, su estructura, la carpeta `studio/episodios/<ep>/guionista/<X>/`. Cada uno entrega `ganchos.json` (4 ganchos) y `guion.md`.

## 2. Duelo ciego de los 12 ganchos
1. Junta los 12 en `studio/episodios/<ep>/guionista/ganchos.json` (`{"candidatos": [...]}`, ids A1…D4).
2. `python3 tools/guionista/duelo.py preparar studio/episodios/<ep>/guionista --jueces 4` → lanza 4 `juez-gancho` en paralelo, cada uno con su `duelo/juezN.md`. **Los jueces no escriben:** guarda tú la respuesta JSON de cada uno en `duelo/resultados/juezN.json` (sin tocarla). `duelo.py contar …` → gana uno.
3. **Contra los virales:** deja sólo el ganador (y el 2.º) en un `ganchos.json` aparte, `duelo.py preparar <carpeta> --anclas virales --jueces 4`, 4 jueces, guarda, `duelo.py contar <carpeta> --anclas virales`. Si el ganador pierde contra más de la mitad de los virales, prueba el 2.º; si los dos pierden → los guionistas reescriben ganchos (cuenta como reescritura 1).

## 3. juez-viral, parte por parte
- El **guionista de esa estructura** pone el gancho ganador en su guion (paquete de gancho, primera frase, texto de la voz y loop: los 4; lección 176), y si encaja también los otros dos guionistas en los suyos. Después lanza 3 `juez-viral` en paralelo, uno por guion (ruta del guion + `docs/referencias/virales/`). Guarda cada JSON en `studio/episodios/<ep>/guionista/juez-viral-<X>.json`.
- Pasa el guion con `"pasa": true`. Si pasan varios, el de más GANA; empate → el más corto.
- Si ninguno pasa: el guionista del mejor corrige **sólo** lo que señaló el juez (frases débiles con su segundo) → `guion_v2.md` → otro `juez-viral` (uno nuevo, ciego). Máximo 2 reescrituras en total. Si no pasa: **idea descartada**, anótalo en `docs/IDEAS.md` con el porqué y vuelve a la ronda del cazador por la siguiente.

## 4. Espectadores (fugas)
`python3 tools/guionista/feed.py <ep>` con el guion ganador → 6 `espectador` en paralelo, guarda sus JSON tú (no escriben), `puntuar.py`. La frase donde se va gente se reescribe (sin contar como reescritura si no cambia la estructura) y vuelve a juez-viral sólo si se tocó el gancho o el final.

## 5. Entrega
`studio/episodios/<ep>/guion.md` (formato de siempre: idea central, guion con segundos, cuadro 0, verificación por afirmación, fuentes, "Paquete de gancho" con el resultado del duelo y de juez-viral). Revisa a mano: remate ≤ 12 palabras + loop + **"mándaselo a…" ligado al contenido** (persona concreta del tema, nunca genérico). Anota la estructura en `docs/ROTACION.md` al publicar. A Tomás no se le muestra el guion salvo que lo pida: sigue la voz.
