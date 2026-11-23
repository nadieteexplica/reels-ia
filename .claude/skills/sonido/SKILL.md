---
name: sonido
description: Pone los efectos de sonido (SFX) y arma la mezcla final de un episodio. Usar después del storyboard, cuando ya hay voz y words.json, para convertir la columna SFX del storyboard en un sfx-plan.json, colocar un sonido por cada acción visible, mezclar voz + efectos + música con ducking y revisar que cada golpe importante se escuche sin tapar la voz.
---

# Sonido: efectos por acción y mezcla

Todo vive en `tools/sonido/`:

| Archivo | Qué hace |
|---|---|
| `generar.py` | Sintetiza la biblioteca propia (CC0, hecha acá) en `biblioteca/*.wav` + `biblioteca/catalog.json`. Semillas fijas: regenerar da los mismos archivos. |
| `mezclar.py` | Lee un `sfx-plan.json`, coloca los efectos, mezcla con música y ducking, deja la mezcla a −14 LUFS y revisa audibilidad. |
| `ver.py` | Dibuja onda + espectrograma + eventos + palabras en un PNG (para revisar con los ojos lo que no se puede escuchar). |
| `medir.py` | Loudness BS.1770-4 propio (igual a `ffmpeg ebur128`, comprobado con `generar.py --verificar`) y true peak. |
| `ejemplos/ep16-primeros-15s.sfx-plan.json` | Plan de ejemplo con la voz publicada del Ep. 16. |

Comandos (desde la raíz del repo, uno por bloque):

```
.venv/bin/python tools/sonido/generar.py
```
```
.venv/bin/python tools/sonido/mezclar.py studio/episodios/<ep>/sfx-plan.json --guardar-ref
```
```
.venv/bin/python tools/sonido/ver.py studio/episodios/<ep>/<salida>.reporte.json --hasta 15
```

`mezclar.py` sale con código 1 si un efecto importante no se oye; ahí se corrige el plan, no se ignora.

## La biblioteca (todos a −20 LUFS, techo −1,5 dBTP)

Elige por **función**, no por nombre bonito:

| Función (categoria) | Clips |
|---|---|
| **motion** — algo entra, sale, cambia de plano | `whoosh-suave`, `whoosh-rapido`, `whoosh-reverso` (se alinea por el final), `swoosh-sube`, `swoosh-baja`, `papel` |
| **emphasis** — aparece un dato, un golpe, una revelación | `pop`, `pop-grave`, `pop-agudo`, `reveal-brillo`, `ding`, `ding-grave`, `ping`, `thud-suave`, `impacto-pesado`, `thud-metal`, `whomp`, `gota`, `resorte` |
| **snap** — corte seco, algo calza, se toma una foto | `snap`, `click-mecanico`, `obturador`, `tecla`, `tecla-b`, `tecleo` |
| **ui** — números, pantallas, aparatos, errores | `click-ui`, `tick-contador`, `tick-grave`, `beep`, `beep-doble`, `buzz-error`, `glitch`, `glitch-corto` |
| **tension** — suspenso antes del golpe | `riser-1s`, `riser-2s` (los dos se alinean por el final) |
| **ambience** — cama de fondo | `estatica-tv` (lluvia de tele sin señal, 2 s) |

`catalog.json` trae por clip: id, categoria, tags, duracion_s, peak_dbfs, loudness_lufs, fuente, licencia ("CC0 1.0 — propio") y `usado_en`. Para anotar el episodio: `mezclar.py … --registrar ep17`.
¿Falta un sonido? Se agrega una función con `@sonido(...)` en `generar.py` (semilla nueva, fija) y se regenera. Nada bajado de internet sin licencia clara.

## Reglas

1. **Un sonido por cada acción visible**, elegido por función: movimiento = whoosh, énfasis = pop/impacto, corte = click/snap, tensión = riser. Si en pantalla pasa algo y no suena, se siente muerto; si suena algo que no se ve, confunde.
2. **Capas sólo en 2–3 momentos héroe** por video: riser → impacto, whoosh → pop. El resto, un solo clip.
3. **Lo decorativo va `"opcional": true`** (no se exige que se oiga): brillitos, ambiente, pops de subtítulos.
4. **Ganancias de partida** (relativas a los clips de −20 LUFS) y después se ajusta con la tabla: whoosh −3 · pop/impacto 0 a +3 · ui/click −3 a 0 · ambiente −10 · riser −3 a +1.
5. **Música ≥ 19 dB bajo la voz mientras habla** (regla del Ep. 16). `mezclar.py` la mide y, si no cumple, la baja sola y avisa.
6. **Nunca tapar una palabra con un golpe fuerte.** Los golpes importantes van en los huecos de la voz (fin de frase, respiro) o 0,05–0,15 s antes de la palabra con `desfase_s`. Si la tabla dice `tapa '<palabra>'`, muévelo.
7. **Un golpe corto encima de la voz casi nunca pasa los +4 dB** (en 0,3 s se diluye). Si es importante, muévelo a un hueco; subirle 10 dB sólo tapa la voz.
8. **Una textura mala no se arregla con ganancia.** Si un clip suena chillón, sucio o no calza con la acción, cambia el clip (o crea una variante en `generar.py`), no lo subas ni lo bajes.
9. Eventos a menos de 0,25 s entre sí se marcan: o es una capa buscada (riser que remata en golpe = `capa con #n`, está bien) o es un amontonamiento (se saca uno).

## Del storyboard al sfx-plan.json

La plantilla `studio/plantilla/storyboard.md` tiene la columna **SFX** por plano (y "Acción visible" dice qué la provoca). Por cada fila con SFX:

1. **Qué suena:** traduce la palabra del storyboard a un id del catálogo por función ("chisporroteo" → `glitch-corto` o `estatica-tv`; "glup" → `gota`; "golpe" → `thud-suave`/`thud-metal`/`impacto-pesado` según el material; "entra la píldora" → `pop-agudo`). Si no hay nada parecido, se crea en `generar.py`.
2. **Cuándo:** ancla el evento a la palabra de la voz que dispara la acción (`"palabra"`, y `"despues_de_s"` si la palabra se repite). Si la acción no cae en una palabra, usa `"en_s"` con el tiempo del plano.
3. **Ajuste fino:** `"desfase_s"` para que el golpe caiga en el hueco antes de la palabra; `"alinear": "fin"` para risers y `whoosh-reverso` (el clímax cae justo en el tiempo).
4. **Importante o decorativo:** si sin ese sonido se pierde un remate o una acción clave → `"opcional": false`; si no → `true`.
5. `"cue"` = lo que se ve (copia la acción visible del storyboard), para que el plan se lea solo.

Ejemplo de evento:

```json
{"sfx": "impacto-pesado", "gain_db": 2, "palabra": "Bueno", "desfase_s": -0.38,
 "cue": "explota el Big Bang chiquito en la pantalla", "opcional": false}
```

Esquema completo en el docstring de `mezclar.py` (adaptado del sfx-plan de hassancs91/claude-faceless-shorts-creator, MIT). Usa el words.json que calza con el audio que le pasas: en el Ep. 16, `words_voz.json` va con el mp3 crudo y `words.json` con la voz ya recortada por `prep.py`.

## Cómo leer la salida

- `loudness integrado` tiene que dar −14 ± 0,3 LUFS y el true peak ≤ −1,5 dBTP.
- `música bajo la voz mientras habla` ≥ 19 dB.
- Tabla de audibilidad: `Δ dB` = cuánto sube la mezcla sobre voz+música en los 0,3 s del evento. `ok` ≥ +4 dB; `NO SE OYE` en un evento importante = falla (código 1). Un Δ enorme (40–80 dB) significa que el evento cae en un silencio: perfecto para golpes héroe.
- Revisa el PNG de `ver.py`: lo naranjo que asoma sobre lo gris es lo que aportan los efectos; las líneas tienen que caer donde pasa la acción y los golpes héroe en los huecos entre palabras.
- Escuchar sigue siendo la última palabra: los números dicen que se oye, no que suene bien.
