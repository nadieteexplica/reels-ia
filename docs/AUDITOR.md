# Auditor — revisión independiente por etapas

**Para qué:** que ningún error llegue a Tomás ni a las redes. En el Ep. 1 los errores los encontró Tomás (`LECCIONES.md`); desde el Ep. 2, si Tomás encuentra un error que el auditor dejó pasar, eso es una falla del auditor y se corrige acá.

**Decidido por Tomás (19-oct-2026):**
- El auditor corre como **subagentes en la misma sesión** (gratis). No usa la API de Anthropic.
- **Umbral:** todas las notas **≥ 8** y **ningún bloqueante**. Con un bloqueante no pasa aunque las notas den 10.
- **A Tomás le llegan 2 cosas:** los cuadros de estilo de escenarios nuevos y el video final, los dos **ya aprobados** por el auditor y con su informe (`veredicto.md`). El resto de las etapas no le llega.
- **Máximo 3 rondas por etapa.** Si en la 3.ª no pasa, no se sigue corrigiendo: se propone un reemplazo (otra idea, otro plano, otro clip).

## Cómo funciona
Cada etapa es una **puerta**: si no pasa, no se avanza a la siguiente. Cada puerta tiene dos filtros:
1. **Chequeo automático** (`tools/auditor/checks.py`, `detectores.py`, `proceso.py`): mide lo que se puede medir (duraciones, palabras, títulos, etiquetas, zonas, volumen, cosas que aparecen de golpe, pantalla vacía, máquinas a la vez, gasto). Una falla automática = NO APROBADO.
2. **Revisor** (subagente): mira los materiales con un prompt fijo por etapa (`tools/auditor/prompts/`). Nunca ve la autoevaluación de quien hizo el trabajo, ni otras rondas, ni otros encargos.

Las revisiones son **cortas y relanzables**: cada encargo cubre una etapa o un tramo de ≤9 planos. El revisor escribe su resultado **una sola vez, al final**, en un JSON con `"completo": true`. Si se corta (por ejemplo, porque Tomás escribe a mitad de un turno), el archivo no existe y se relanza el mismo encargo; no se pierde nada. Los materiales (imágenes) se regeneran desde los archivos de origen, así que no se suben al repo.

## Etapas

| # | Etapa | Cuándo | Chequeo automático | Lo que mira el revisor | Criterios |
|---|---|---|---|---|---|
| 1 | **Idea y guion** | antes de generar la voz | 190–215 palabras, 62–75 s estimados, frases ≤14 palabras, pausas, frases prohibidas, lista negra, 2 fuentes con URL (sin Wikipedia), tabla de verificación completa, cifras con fuente, puntaje de la idea ≥ mínimo | abre cada fuente y comprueba cada cifra; fuentes independientes; gancho en el primer segundo; entendible para un niño de 12; estructura; salud; ¿a quién se lo mandan? | precisión, gancho, claridad, compartible |
| 2 | **Voz** | después de la voz, antes del storyboard | duración 62–75 s, palabras de más de 1,2 s, pausas de más de 1 s, ritmo por frase, conteo de palabras = guion, error en `status.json`, créditos < 8.000, **transcripción automática** (`asr.yml`) contra el guion | qué diferencias de la transcripción son mala pronunciación; ritmo | pronunciación, ritmo |
| 3 | **Storyboard** | antes de cuadros, Kling o render | columna `Origen` (render/kling/biblioteca), máx. 3 planos de Kling, planos con manos y objetos que salen de render, huecos, planos largos sin transformación, escala cada ≤12 s, interior con cortes/cráneo, fundido en el plano 1 | un foco por plano, cada frase con su imagen, "cabeza de vidrio", qué no puede hacer el pipeline, cuadro 0, símbolo, loop | foco, ritmo, viabilidad, gancho visual |
| 4 | **Cuadros** de estilo y de partida para Kling | antes de mostrárselos a Tomás / antes de mandar a Kling | resolución, % quemado, lavado, muy oscuro | manos libres o bien agarradas, objetos como deben verse, personaje igual a la ficha, anatomía limpia, belleza | belleza, personaje, manos, anatomía |
| 5 | **Clips de Kling** | antes de meterlos al video | resolución, palabras que activan el filtro, máx. 3 planos de Kling | 8 cuadros por clip: dedos, objeto pegado a la mano, cara y ropa iguales, nada que cambie de forma o color, desde qué segundo sirve | manos, objeto, personaje, estabilidad |
| 6 | **Video final** | después del render, antes de mostrárselo a Tomás | QA técnico (`tools/qa.py`), **pantalla vacía**, **cosas que aparecen o desaparecen de golpe** (flujo óptico), cambios de luz dentro del plano, planos largos, subtítulos palabra por palabra contra `words.json` (que aparezcan, a tiempo y en zona), voz vs. música | tira de 6 cuadros por plano (en tramos de 9), cada evento de los detectores, gancho, contacto 1 cuadro/s, loop, subtítulos, audio, precisión de lo que se ve | los 8 del manual |
| 7 | **Paquete** | antes del mensaje a Tomás | título ≤60, 3–5 hashtags con `#nadieteexplica`, pregunta, fuentes con enlaces en el primer comentario y en YouTube, `madeForKids` = no, TikTok con `title`, etiquetas IA, crédito de Z-Anatomy si hay anatomía, URL pública del MP4 responde | coherencia con el video, dato igual de exacto que el guion, palabras buscables, ortografía | textos, cumplimiento |
| P | **Proceso** | en cada puerta y al final | bitácora existe; cada hora prometida con su dato medido y cumplida o avisada **antes**; chequeo cada 15 min de todo trabajo de más de 15 min; runs caídos notados; **≤16 máquinas** de Actions a la vez; gasto del video contra el tope; unidades de Kling del mes | — (es todo medible) | — |

**Bloqueantes** (lista completa en `tools/auditor/prompts/comun.md`): dedos u objetos que flotan o atraviesan; algo que aparece, desaparece o cambia de golpe; pantalla vacía; personaje distinto a la ficha (`studio/personaje/ficha.jpg`); cara tapada o subtítulos fuera de zona o desfasados; dato sin respaldo; interior confuso (más de un foco, cortes, cráneo, órganos inventados); lista negra; estilo rechazado; faltas de ortografía.

## Formato de salida (fijo)
Cada ronda queda en `studio/episodios/<ep>/auditoria/<etapa>/rN/`:
- `checks.json`: el chequeo automático.
- `<encargo>.json`: lo que escribió cada revisor (notas con evidencia, problemas con plano y segundo, eventos revisados).
- **`veredicto.md`** y `veredicto.json`: **APROBADO / NO APROBADO**, tabla de notas, **arreglos en orden** (bloqueantes primero, cada uno con dónde, qué y cómo arreglarlo) y avisos.
- `auditoria/ESTADO.md`: una línea por etapa y ronda.

Las notas de varios revisores se juntan tomando **la más baja** de cada criterio. APROBADO sólo si no hay fallas automáticas, ni bloqueantes, ni notas bajo 8, ni criterios sin nota, y todos los revisores aprobaron.

## Cómo se corre (lo hace Claude, no Tomás)
```bash
# 1. preparar: chequeo automático + materiales + encargos (crea la ronda siguiente)
python3 tools/auditor/auditar.py preparar <ep> guion
python3 tools/auditor/auditar.py preparar <ep> voz                      # necesita out/asr/<ep>.json (asr.yml corre solo después de voz.yml)
python3 tools/auditor/auditar.py preparar <ep> storyboard
python3 tools/auditor/auditar.py preparar <ep> cuadros --imagenes 'ruta/*.jpg' --nota "para qué es cada cuadro"
python3 tools/auditor/auditar.py preparar <ep> kling --clips 'ruta/*.mp4'
python3 tools/auditor/auditar.py preparar <ep> video --video borrador.mp4 --planos planos.json --subs subs_log.json
python3 tools/auditor/auditar.py preparar <ep> paquete --url <URL pública del MP4>
python3 tools/auditor/auditar.py preparar <ep> proceso
# 2. lanzar: imprime el texto exacto de cada subagente que falta → se lanzan con la herramienta Agent, en paralelo y en segundo plano
python3 tools/auditor/auditar.py lanzar <ep> <etapa>
# 3. estado: qué encargos terminaron (los que faltan se relanzan con 'lanzar'; no se reescribe nada a mano)
python3 tools/auditor/auditar.py estado <ep> <etapa>
# 4. cerrar: junta todo en veredicto.md (sale 0 si APROBADO) → commit y push
python3 tools/auditor/auditar.py cerrar <ep> <etapa>
```
- Los archivos del borrador (`planos.json`, `subs_log.json`, MP4) se bajan de la prerelease `epNN-borrador`; los renders los suben solos.
- **Prohibido** escribir o editar a mano un `<encargo>.json` o un `veredicto.*`. Si el auditor se equivoca, se corrige el prompt o el chequeo y se corre una ronda nueva.
- Con NO APROBADO: se arregla en orden la lista de arreglos y se corre `preparar` otra vez (ronda siguiente). En la 3.ª ronda sin aprobar, se propone un reemplazo.

## Bitácora del proceso (obligatoria desde el Ep. 2)
Mientras se trabaja, cada hecho se anota con `tools/auditor/bitacora.py` en `auditoria/proceso.jsonl`:
```bash
python3 tools/auditor/bitacora.py <ep> promesa --hora 18:40 --que "video completo" --dato "progreso.txt: 540/2160 cuadros en 12 min = 1,33 s/cuadro"
python3 tools/auditor/bitacora.py <ep> aviso   --que "se atrasa a 19:10: el pod bajó a 1,8 s/cuadro"     # cada aviso a Tomás, ANTES de la hora
python3 tools/auditor/bitacora.py <ep> cumplida --id <n de la promesa>
python3 tools/auditor/bitacora.py <ep> trabajo --id "pod a5000-1" --estado inicio|fin|caido              # lo que GitHub no ve
python3 tools/auditor/bitacora.py <ep> chequeo --id "render-gpu 39290639291" --estado "vivo, 812/2160"   # cada 15 min
python3 tools/auditor/bitacora.py <ep> gasto   --servicio kling --monto 4 --nota "p3_frente_b"          # kling unidades · runpod USD · eleven créditos
```
Topes por video y saldos de paquetes: `tools/auditor/presupuesto.json` (Kling 8 unidades, RunPod USD 0,5, ElevenLabs 2.600 créditos por video).

## Límites (dichos derecho)
- **El revisor no escucha el audio.** La pronunciación se juzga con la transcripción automática (Whisper en Actions) y el volumen con mediciones. Un error de entonación que Whisper entiende bien puede pasar.
- **Los detectores marcan, no deciden** (salvo la pantalla vacía): el revisor mira cada evento "antes | después". Hay falsos positivos (etiquetas que entran a propósito, acciones rápidas); el revisor los descarta con una frase.
- **El revisor ve 6 cuadros por plano, no el video corrido.** Un defecto de 1–2 cuadros entre dos muestras lo pescan los detectores, no el revisor.
- **Independencia:** el revisor conoce las reglas (que salen de los errores del Ep. 1), pero no sabe qué se hizo, qué se arregló ni qué opina quien lo hizo.
- **Proceso hacia atrás:** lo que no quedó en la bitácora no se puede auditar. Por eso la bitácora es obligatoria.

## Calibración
Ver `docs/AUDITOR_CALIBRACION.md`: el auditor corrido a ciegas sobre las versiones viejas del Ep. 1 y qué errores de `LECCIONES.md` detectó.

## Mantenimiento
Cada error nuevo que llegue a Tomás o a las redes: se anota en `LECCIONES.md`, se agrega la regla al prompt o al chequeo que lo habría pescado, y se vuelve a correr la calibración para comprobar que ahora lo detecta.
