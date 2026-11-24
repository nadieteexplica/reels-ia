# Ep. 17 · Dormir con tu pareja te da radiación — Storyboard v1 · Laboratorio nocturno

Voz de 41,30 s (128 palabras, `words.json`); video de **41,90 s = 1257 cuadros** a 30 fps, 1080×1920 (0,6 s de cola sin voz para el loop). Todo cambio cae en el inicio de su palabra en `words.json` (cuadro exacto, margen ±2). Lo mismo, para el animador, en `storyboard.json`.

**16 planos · 3 escenas · 54 cambios (1,29/s) · 6 cortes (uno cada 7,00 s, todos al cambiar la idea) · cámara quieta (0 % de cámara rápida) · hueco máximo sin cambio: 1,12 s.**

## Concepto
- **Estilo único aprobado: laboratorio nocturno del beat v5.** Carbón, objetos reales con volumen y sombra corta, etiquetas HUD. **Oro sólo en lo radiactivo** (quien irradia, el plátano, los átomos, los rayos, la pila); la torre de la central va en concreto gris: la paradoja se ve en el color. Verde sólo en el check de INOFENSIVO.
- **El gancho se VE en el cuadro 0:** la balanza ya caída hacia la cama (que brilla oro) frente a la torre de enfriamiento, `1 AÑO` sobre cada platillo y la píldora `TU CAMA > CENTRAL NUCLEAR`.
- **Ancla que vuelve:** el plátano cae al velador (6,05), se mira con lupa (7,94), se pela como 'una noche' (29,18), se vuelve la pila de cáscaras que inclina la balanza (31,66–34,49) y es la pareja en el remate (37,42).
- **Se entiende sin sonido:** `1 AÑO` vs `1 AÑO`, `POTASIO` en el plátano y en ti, `1 DE CADA ~8.500`, `~4.000 POR SEGUNDO`, `POTASIO-40`, `RAYO GAMMA`, `PIEL`, `TÚ`/`PAREJA`, `1 NOCHE ≈ 1 PLÁTANO`, ✓ `INOFENSIVO`, `NOCHE 1 → 365`.
- **Verdad (ficha):** sólo cifras con 2 fuentes (`~8.500`, `~4.000`, `POTASIO-40`). No van los 140 g ni los 30 cm (están en la mecánica de la ficha, no en la tabla verificada) ni cuántos plátanos es un año.

## Escenas
- **E1 · La balanza: tu cama contra la central.** Fondo carbón con luz arriba-izquierda, viñeta y grano quieto. `balanza(L, cx=540, cy=700)` con cámara fija s=0,86, ancla (540, 700) → destino (490, 760): pivote en (490, 760); platillo izquierdo (la cama, `cama_chica`) en x≈209 y platillo derecho (la torre de enfriamiento con vapor) en x≈771, a y≈1045–1160 según la inclinación; columna hasta y≈1371, sombra de contacto en y≈1380. Acero con brillo frío; madera y colcha de la cama con volumen; la torre en concreto gris (nunca oro: lo radiactivo es la cama). HUD `1 AÑO` (blanco, 52 px, placa oscura con esquinas de HUD) centrado sobre cada platillo en y 650–710. Píldora del gancho `TU CAMA > CENTRAL NUCLEAR` (pildora_energia, 44 px) centrada en x 490, y 550–615.
- **E2 · El dormitorio desde arriba.** Plano cenital fijo. `cama_arriba(L, cx=390, cy=1080, ancho=560, alto=760)`: marco x 88–692, cabecera y≈630, pie y≈1478. PAREJA a la izquierda (cabeza (256, 805), cuerpo (256, 1170)); TÚ a la derecha (cabeza (524, 805), cuerpo (524, 1170)); la colcha respira (respira=True). `velador(L, 808, 830)` (tapa x 698–918) con la lámpara y, desde 6,05 s, `platano(L, 808, 820, largo=170, ang=-20)`. Piso de madera oscura alrededor (no carbón plano: es un dormitorio de noche).
- **E3 · Tu cuerpo de cerca.** La misma cama de E2 con cámara fija s=1,5, ancla (524, 1170) → destino (540, 1160): el bulto de TÚ bajo la colcha llena el centro (contorno x 388–692, y 761–1559; cabeza en (540, 612)); la PAREJA queda cortada en el borde izquierdo (cuerpo x −14–290). Adentro del contorno oro de TÚ, ~60 puntitos de potasio grises (los mismos de P5) y unos pocos en oro.

## Interfaz fija
- **pildora_gancho:** TU CAMA > CENTRAL NUCLEAR · centro (490, 582), y 550–615 · P1 (cuadro 0) y P14 ('central.') → P16 (empalma con el cuadro 0)
- **hud_1_ano:** `1 AÑO` sobre cada platillo de la balanza, centros (209, 680) y (771, 680), en toda toma de E1 salvo P13, donde el de la cama corre NOCHE 1 → 365
- **personajes:** TÚ = la persona de la derecha (la que irradia primero, junto al velador); PAREJA = la izquierda (recibe los rayos y se vuelve plátano gigante)
- **Estado de la balanza:** inclin (rad, + = baja la cama): cuadro 0 0,140 → 0,145 (lento) → 0,20 en 'irradia' · P13 −0,08 (una noche: pesa la central) → 0,0 en 'Esa' · 0,20 en 'gana' (rebote) · P16 0,20 → 0,135 en 'tóxico' → 0,140 en el último cuadro = cuadro 0
- **Subtítulos:** ARRIBA (kit subtitulos, y_arriba=300, x_centro=490), 1–3 palabras, píldora oro en las claves; ocultar 'cuatro', 'mil' (P7, lo dice el número), '¿cuánto?' (P11, recuadro) e 'inofensivo' (P12). Píldora en: *irradia*, *este plátano*, *radiactiva*, *radiactivo*, *rayo gamma*, *le llega*, *un año de noches*, *le gana*, *plátano gigante*, *tóxica*.

## Resumen

| # | Escena | Segundos | Palabra gatillo (s · cuadro) | La idea |
|---|---|---|---|---|
| 1 | E1 | 0,00–4,32 | «irradia» 1,44 · 43 | Un año en esta cama pesa más (en radiación) que un año junto a una central. |
| 2 | E2 | 4,32–6,95 | «plátano:» 6,05 · 182 | La respuesta está en este plátano. |
| 3 | E2 | 6,95–7,69 | «potasio.» 6,95 · 208 | El plátano tiene potasio. |
| 4 | E2 | 7,69–10,46 | «pizca» 7,94 · 238 | Sólo una pizca de ese potasio es radiactiva. |
| 5 | E2 | 10,46–12,58 | «cuerpo» 10,69 · 321 | Tu cuerpo también está lleno de potasio. |
| 6 | E2 | 12,58–14,99 | «radiactivo.» 14,01 · 420 | Tú también eres un poquito radiactivo. |
| 7 | E3 | 14,99–19,36 | «cuatro» 16,28 · 488 | Cada segundo, unos 4.000 átomos estallan dentro de ti. |
| 8 | E3 | 19,36–22,64 | «gamma» 20,67 · 620 | Algunos sueltan un rayo gamma que sale del cuerpo. |
| 9 | E2 | 22,64–24,43 | «pareja» 22,75 · 682 | Tu pareja duerme pegada a ti. |
| 10 | E2 | 24,43–26,64 | «llega.» 26,02 · 781 | Parte de esos rayos le llega a tu pareja. |
| 11 | E2 | 26,64–30,53 | «plátano.» 29,70 · 891 | Una noche juntos es más o menos un plátano. |
| 12 | E2 | 30,53–31,48 | «Inofensivo.» 30,53 · 916 | Es inofensivo. |
| 13 | E1 | 31,48–33,22 | «súmale» 31,66 · 950 | Súmale un año de noches. |
| 14 | E1 | 33,22–35,53 | «gana» 34,49 · 1035 | Esa pila de plátanos le gana a la central (pago del gancho). |
| 15 | E2 | 35,53–38,69 | «plátano» 37,42 · 1123 | Duermes abrazado a un plátano gigante. |
| 16 | E1 | 38,69–41,90 | «Mándaselo» 38,69 · 1161 | Mándaselo a quien te irradia de noche (y vuelve al inicio). |

## Planos

### P1 · La balanza: tu cama contra la central (E1) · 0,00–4,32 s (cuadros 0–129)
- **Palabra gatillo:** «irradia» en 1,44 s (cuadro 43).
- **Qué se ve:** CUADRO 0 (gancho completo, nunca negro): la balanza ya inclinada hacia la cama (inclin 0,14 rad ≈ 8°): el platillo de la cama abajo, el de la torre de enfriamiento arriba. La cama doble con dos personas dormidas y contorno oro tenue (brillo_cama 0,35, late). HUD `1 AÑO` sobre cada platillo. Píldora `TU CAMA > CENTRAL NUCLEAR`. La torre suelta vapor gris.
- **Una idea:** Un año en esta cama pesa más (en radiación) que un año junto a una central.
- **Qué cambia:**
  - 0,00 s · c0 · (cuadro 0): cuadro 0 ya en movimiento: vapor de la torre (continuo), el brillo oro de la cama late (0,35 ± 0,1, período 41,9/26 = 1,611 s para que empalme) y el platillo de la cama se sigue hundiendo lento (0,140 → 0,145 rad, lineal hasta 1,44 s)
  - 0,37 s · c11 · «año»: el HUD `1 AÑO` de la cama parpadea (escala 1 → 1,1 → 1 y borde a blanco pleno, 0,3 s)
  - 0,97 s · c29 · «cama»: el contorno oro de la cama sube (brillo 0,35 → 0,7, 0,25 s): la cama es la que irradia
  - 1,44 s · c43 · «irradia»: el platillo de la cama cae de golpe (0,145 → 0,20 rad, sin rebote) y la torre sube; un anillo oro sale de la cama (r 40 → 220 px, 0,4 s, se apaga)
  - 2,32 s · c70 · «año»: el HUD `1 AÑO` de la torre parpadea (igual al de la cama): año contra año
  - 3,12 s · c94 · «central»: bocanada de vapor gris de la torre (opacidad ×1,6 por 0,5 s): la central
- **Movimiento:** platillo cae estado bezier(0.65, 0, 0.35, 1) 0,30 s; parpadeo HUD entrada bezier(0.16, 1, 0.3, 1) 0,15 s + salida 0,15 s; anillo entrada bezier(0.16, 1, 0.3, 1); vapor lineal; cámara quieta.
- **Etiquetas:**
  - `TU CAMA > CENTRAL NUCLEAR` (píldora) → — · centro (490, 582), y 550–615 · entra cuadro 0 (ya está) · sale '¿Por' 4,32 (corte)
  - `1 AÑO` (HUD) → platillo de la cama · centro (209, 680) · entra cuadro 0 · sale '¿Por' 4,32 (corte)
  - `1 AÑO` (HUD) → platillo de la torre · centro (771, 680) · entra cuadro 0 · sale '¿Por' 4,32 (corte)
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `tick-grave` 0,37 s (HUD de la cama) · `thud-metal` 1,44 s (la balanza cae (irradia)) · `click-mecanico` 1,44 s (el clic de contador del guion) · `tick-grave` 2,32 s (HUD de la torre) · `whoosh-suave` 3,12 s (vapor)
- **Zona segura:** Balanza x 80–900, y 720–1400; píldora y 550–615; HUD y 650–710. Nada sobre y 550 (subtítulos), nada bajo 1580, nada en x > 920.

### P2 · El dormitorio desde arriba (E2) · 4,32–6,95 s (cuadros 130–207)
- **Palabra gatillo:** «plátano:» en 6,05 s (cuadro 182).
- **Qué se ve:** CORTE (cambia la idea: el porqué) a la cama desde arriba: los dos duermen, sin brillo todavía; velador vacío a la derecha. Se prende la lámpara y cae un plátano real al velador, con su sombra.
- **Una idea:** La respuesta está en este plátano.
- **Qué cambia:**
  - 4,32 s · c130 · «¿Por»: CORTE a E2: la cama desde arriba, la colcha respira; velador vacío
  - 5,04 s · c151 · «Por»: se prende la lámpara del velador: círculo de luz blanca tibia sobre la tapa (brillo_suave, no oro)
  - 6,05 s · c182 · «plátano:»: un plátano real cae al velador (entra en 5,85 desde y 660 con escala 1,15 → 1) y aterriza justo en 'plátano' con su sombra de contacto
- **Movimiento:** luz entrada bezier(0.16, 1, 0.3, 1) 0,3 s; caída del plátano aterrizaje sin rebote bezier(0.6, 0, 0.9, 0.35) 0,2 s (es una caída: acelera); cámara quieta.
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `whoosh-suave` 4,32 s (corte) · `click-mecanico` 5,04 s (interruptor de la lámpara) · `thud-suave` 6,05 s (el plátano aterriza)
- **Zona segura:** Cama x 88–692, y 630–1478; velador x 698–918, y 735–925; plátano en (808, 820).

### P3 · El dormitorio desde arriba (E2) · 6,95–7,69 s (cuadros 208–230)
- **Palabra gatillo:** «potasio.» en 6,95 s (cuadro 208).
- **Qué se ve:** El plátano en el velador; etiqueta HUD `POTASIO` con línea guía al plátano. El plátano NO brilla todavía (el oro es sólo lo radiactivo).
- **Una idea:** El plátano tiene potasio.
- **Qué cambia:**
  - 6,95 s · c208 · «potasio.»: etiqueta `POTASIO` con línea guía al plátano (punto → guía → texto, 0,8 s)
- **Movimiento:** etiqueta del kit (entrada 0,8 s, el texto no se mueve).
- **Etiquetas:**
  - `POTASIO` (etiqueta) → plátano (808, 805) · texto en (620, 565), lado izq. · entra 'potasio.' 6,95 · sale 'tú' 12,97 (0,2 s)
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `click-ui` 6,95 s (etiqueta)
- **Zona segura:** Etiqueta x 620–870, y 565–615.

### P4 · El dormitorio desde arriba (E2) · 7,69–10,46 s (cuadros 231–313)
- **Palabra gatillo:** «pizca» en 7,94 s (cuadro 238).
- **Qué se ve:** Lupa redonda sobre el plátano (`lupa`, centro (490, 1060), r 240, unida al plátano por 2 líneas finas grises): grilla de átomos de potasio grises. En 'radiactiva' uno solo titila en oro, el plátano toma un brillo oro tenue y bajo la lupa aparece `1 DE CADA ~8.500`.
- **Una idea:** Sólo una pizca de ese potasio es radiactiva.
- **Qué cambia:**
  - 7,94 s · c238 · «pizca»: entra la lupa (escala 0,6 → 1) con 2 líneas de callout desde el plátano; adentro, la grilla gris
  - 8,68 s · c260 · «potasio»: una onda de brillo gris claro recorre la grilla de izquierda a derecha: estos son los átomos de potasio
  - 9,46 s · c284 · «radiactiva.»: UN solo átomo titila en oro (los demás siguen grises), bajo la lupa entra `1 DE CADA ~8.500` (52 px, placa oscura; 1,23 s de lectura hasta 'cuerpo') y el plátano del velador toma brillo oro tenue (brillo 0 → 0,3): un solo evento, el ojo está en el átomo
- **Movimiento:** lupa entrada bezier(0.16, 1, 0.3, 1) 0,35 s; onda lineal 0,4 s; titileo seno (el de `lupa`); texto entrada bezier(0.16, 1, 0.3, 1) 0,25 s.
- **Etiquetas:**
  - `1 DE CADA ~8.500` (texto en placa) → el átomo oro · centro (490, 1375), y 1350–1405 · entra 'radiactiva.' 9,46 · sale 'cuerpo' 10,69 (con la lupa)
  - `POTASIO` (etiqueta) → plátano · (620, 565) · entra sigue · sale 'tú' 12,97
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `pop-grave` 7,94 s (entra la lupa) · `ping` 9,46 s (el átomo radiactivo) · `click-ui` 9,58 s (texto (pegado al ping))
- **Zona segura:** Lupa x 232–748, y 802–1318 (mango decorativo hacia abajo-derecha, puede salirse); texto y 1350–1405.

### P5 · El dormitorio desde arriba (E2) · 10,46–12,58 s (cuadros 314–376)
- **Palabra gatillo:** «cuerpo» en 10,69 s (cuadro 321).
- **Qué se ve:** Sale la lupa; el plátano quedó con su brillo oro tenue. La misma etiqueta `POTASIO` aparece ahora en el cuerpo de TÚ (derecha) y su bulto se llena de puntitos grises de potasio.
- **Una idea:** Tu cuerpo también está lleno de potasio.
- **Qué cambia:**
  - 10,69 s · c321 · «cuerpo»: sale la lupa con su texto (0,18 s) y, donde estaba, entra el punto de una etiqueta `POTASIO` sobre el cuerpo de TÚ (la misma del plátano)
  - 11,35 s · c340 · «mucho»: el bulto de TÚ se llena de ~60 puntitos grises (átomos de potasio), de adentro hacia afuera
- **Movimiento:** lupa salida bezier(0.6, 0, 0.9, 0.35) 0,18 s; etiqueta del kit 0,8 s; puntitos entrada bezier(0.16, 1, 0.3, 1) escalonados en 0,5 s (semilla fija).
- **Etiquetas:**
  - `POTASIO` (etiqueta) → cuerpo de TÚ (590, 1180) · texto en (650, 1230), lado der. · entra 'cuerpo' 10,69 · sale 'Cada' 14,99 (corte)
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `swoosh-baja` 10,69 s (sale la lupa) · `click-ui` 10,99 s (etiqueta) · `pop-agudo` 11,35 s (los puntitos)
- **Zona segura:** Etiqueta x 650–900, y 1230–1280; cuerpo de TÚ x 424–624.

### P6 · El dormitorio desde arriba (E2) · 12,58–14,99 s (cuadros 377–449)
- **Palabra gatillo:** «radiactivo.» en 14,01 s (cuadro 420).
- **Qué se ve:** Etiqueta `TÚ` en la cabeza de la persona derecha. En 'radiactivo' TÚ se enciende con el mismo oro del plátano en todo el contorno y unos pocos puntitos pasan a oro.
- **Una idea:** Tú también eres un poquito radiactivo.
- **Qué cambia:**
  - 12,97 s · c389 · «tú»: etiqueta `TÚ` apunta a la cabeza de la derecha; sale la etiqueta `POTASIO` del plátano (0,2 s): el foco queda en TÚ
  - 14,01 s · c420 · «radiactivo.»: TÚ se enciende en oro en todo el contorno (brillo_der 0 → 0,7) y ~4 de los puntitos grises pasan a oro y titilan
- **Movimiento:** etiqueta del kit 0,6 s; encendido estado bezier(0.65, 0, 0.35, 1) 0,4 s.
- **Etiquetas:**
  - `TÚ` (etiqueta) → cabeza de TÚ (524, 745) · texto en (440, 565) · entra 'tú' 12,97 · sale 'Cada' 14,99 (corte); vuelve en P9
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `click-ui` 12,97 s (etiqueta TÚ) · `reveal-brillo` 14,01 s (TÚ se enciende)
- **Zona segura:** Etiqueta TÚ x 440–520, y 565–615.

### P7 · Tu cuerpo de cerca (E3) · 14,99–19,36 s (cuadros 450–580)
- **Palabra gatillo:** «cuatro» en 16,28 s (cuadro 488).
- **Qué se ve:** CORTE (cambia la idea: lo que pasa adentro) a TÚ de cerca: el bulto con contorno oro y los puntitos de potasio; chispitas oro estallan adentro. Un contador oro corre y se queda en `~4.000` con `POR SEGUNDO` debajo. Etiqueta `POTASIO-40` en un átomo, que se desintegra.
- **Una idea:** Cada segundo, unos 4.000 átomos estallan dentro de ti.
- **Qué cambia:**
  - 14,99 s · c450 · «Cada»: CORTE a E3; chispitas oro estallan adentro del cuerpo (~8 por segundo visibles, 0,3 s cada una, semilla fija; siguen hasta 22,6)
  - 15,23 s · c457 · «segundo,»: aparece el contador oro (numero_heroe 220 px, centro x 490, base y 900) y corre desde 0 saltando de cifra en cifra (rueda=False, lineal)
  - 16,28 s · c488 · «cuatro»: el contador se queda en `~4.000` (pop 1,12 → 1) y entra `POR SEGUNDO` debajo; los subtítulos ocultan 'cuatro mil'
  - 17,19 s · c516 · «átomos»: etiqueta `POTASIO-40` apunta a un átomo oro del pecho (560, 1220)
  - 17,82 s · c535 · «desintegran»: ese átomo se desintegra: destello oro (r 0 → 60 px, 0,35 s) y queda un puntito gris
  - 18,40 s · c552 · «dentro»: estallan a la vez ~12 chispitas por todo el cuerpo (0,4 s) y vuelven al ritmo base
- **Movimiento:** contador lineal 1,05 s, sin medio dígito; pop entrada bezier(0.16, 1, 0.3, 1) 0,25 s; destellos entrada bezier(0.16, 1, 0.3, 1) + salida en la mitad; cámara quieta.
- **Etiquetas:**
  - `~4.000` (número en vivo (héroe)) → — · centro x 490, base y 900 (cifra y 740–900) · entra 'segundo,' 15,23 (corre) · sale 'Algunos' 19,36 (0,2 s) · número: 0 → 4.000 entre 15,23 y 16,28; fijo en ~4.000 desde 'cuatro'
  - `POR SEGUNDO` (texto) → — · centro (490, 960), 56 px · entra 'cuatro' 16,28 · sale 'Algunos' 19,36
  - `POTASIO-40` (etiqueta) → átomo (560, 1220) · texto en (150, 1290), lado izq. · entra 'átomos' 17,19 · sale 'Algunos' 19,36
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `swoosh-baja` 14,99 s (corte) · `tick-contador` 15,23 s (racha de ticks cada ~0,07 s hasta 16,28) · `pop-grave` 16,28 s (4.000) · `click-ui` 17,19 s (etiqueta) · `pop` 17,82 s (se desintegra) · `reveal-brillo` 18,40 s (estallido de chispitas)
- **Zona segura:** Número y 740–990, x 140–840 (tapa el pecho; el cuerpo sigue visible de y 1000 a 1559); etiqueta x 150–480, y 1290–1340. Cabeza de TÚ y 513–711 (bajo la banda de subtítulos).

### P8 · Tu cuerpo de cerca (E3) · 19,36–22,64 s (cuadros 581–678)
- **Palabra gatillo:** «gamma» en 20,67 s (cuadro 620).
- **Qué se ve:** Sale el número. Un átomo oro del pecho crece y suelta un rayo gamma (trazo ondulado oro, `rayo`) hacia la izquierda: cruza el contorno de la piel con un destello y sale del cuerpo hacia la pareja.
- **Una idea:** Algunos sueltan un rayo gamma que sale del cuerpo.
- **Qué cambia:**
  - 19,36 s · c581 · «Algunos»: salen `~4.000`, `POR SEGUNDO` y `POTASIO-40` (0,2 s); un átomo oro en (560, 1250) crece y late (r ×1,6)
  - 19,76 s · c593 · «sueltan»: arranca el rayo desde ese átomo hacia (80, 1320) y avanza lento hacia la piel (p 0 → 0,37 hasta 21,69, lineal)
  - 20,67 s · c620 · «gamma»: etiqueta `RAYO GAMMA` pegada al trazo (en 'gamma': 'rayo' cae 0,56 s después de 'sueltan' y armaría una ráfaga)
  - 21,69 s · c651 · «piel»: el rayo cruza el contorno oro de la piel en (395, 1280) con un destello chico, entra la etiqueta `PIEL` y el rayo acelera hasta salir del cuerpo hacia la pareja en 'sale.' (p 0,37 → 1 en 0,7 s)
- **Movimiento:** rayo lineal (movimiento continuo); al salir estado bezier(0.65, 0, 0.35, 1) 0,35 s; latido seno; etiquetas del kit; cámara quieta.
- **Etiquetas:**
  - `RAYO GAMMA` (etiqueta) → el rayo (470, 1262) · texto en (120, 1060) · entra 'gamma' 20,67 · sale 'Tu' 22,64 (corte)
  - `PIEL` (etiqueta) → cruce (395, 1280) · texto en (150, 1420) · entra 'piel' 21,69 · sale 'Tu' 22,64 (corte)
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `swoosh-sube` 19,76 s (sale el rayo) · `click-ui` 20,67 s (etiqueta) · `pop-agudo` 21,69 s (cruza la piel) · `whoosh-rapido` 22,08 s (sale)
- **Zona segura:** Rayo y 1250–1320; etiquetas x 120–480, y 1060–1110 y 1420–1470.

### P9 · El dormitorio desde arriba (E2) · 22,64–24,43 s (cuadros 679–732)
- **Palabra gatillo:** «pareja» en 22,75 s (cuadro 682).
- **Qué se ve:** CORTE (cambia la idea: entra la pareja) a la cama desde arriba: TÚ con su brillo oro y la etiqueta `TÚ`. Etiqueta `PAREJA` en la cabeza de la izquierda; su bulto se arrima a TÚ.
- **Una idea:** Tu pareja duerme pegada a ti.
- **Qué cambia:**
  - 22,64 s · c679 · «Tu»: CORTE a E2 (TÚ brillo 0,7, etiqueta `TÚ` ya puesta, plátano con su brillo tenue en el velador) y en 'pareja' (22,75, c682: 0,11 s después, se lee como parte del corte) entra la etiqueta `PAREJA` en la cabeza de la izquierda
  - 23,42 s · c703 · «pegada»: el bulto y la cabeza de la pareja se arriman ~24 px hacia TÚ (pegada)
- **Movimiento:** etiqueta del kit 0,6 s; arrimarse estado bezier(0.65, 0, 0.35, 1) 0,4 s.
- **Etiquetas:**
  - `TÚ` (etiqueta) → cabeza de TÚ · (440, 565) · entra ya está al corte · sale '¿Cuánto?' 26,64 (0,2 s)
  - `PAREJA` (etiqueta) → cabeza de la pareja (256, 745) · texto en (80, 565) · entra 'pareja' 22,75 · sale '¿Cuánto?' 26,64 (0,2 s)
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `whoosh-suave` 22,64 s (corte) · `click-ui` 22,75 s (etiqueta) · `papel` 23,42 s (sábana)
- **Zona segura:** Etiquetas x 80–300 y 440–520, y 565–615.

### P10 · El dormitorio desde arriba (E2) · 24,43–26,64 s (cuadros 733–798)
- **Palabra gatillo:** «llega.» en 26,02 s (cuadro 781).
- **Qué se ve:** De TÚ salen 6 rayos gamma cortos en todas direcciones; 4 se van fuera de la cama y se apagan, 2 cruzan hacia la pareja, la tocan y ella se enciende apenas en oro.
- **Una idea:** Parte de esos rayos le llega a tu pareja.
- **Qué cambia:**
  - 24,43 s · c733 · «así»: salen 6 rayos cortos de TÚ en distintas direcciones (`rayo`, 0,6 s)
  - 24,84 s · c745 · «parte»: 4 de ellos salen de la cama y se apagan; quedan 2, que siguen hacia la pareja
  - 25,47 s · c764 · «rayos»: los 2 rayos llegan al borde del bulto de la pareja
  - 26,02 s · c781 · «llega.»: la tocan: la pareja se enciende apenas (brillo_izq 0 → 0,25) con 2 puntitos de impacto
- **Movimiento:** rayos lineal; los que se van salida bezier(0.6, 0, 0.9, 0.35) 0,3 s; encendido estado bezier(0.65, 0, 0.35, 1).
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `swoosh-sube` 24,43 s (rayos) · `ping` 26,02 s (le llega)
- **Zona segura:** Rayos dentro de la cama (x 110–670, y 900–1450) salvo los 4 que se van hacia los bordes del marco.

### P11 · El dormitorio desde arriba (E2) · 26,64–30,53 s (cuadros 799–915)
- **Palabra gatillo:** «plátano.» en 29,70 s (cuadro 891).
- **Qué se ve:** Recuadro HUD `¿CUÁNTO?`. Una franja de luz de luna (azul pálido, el rectángulo de la ventana) cruza la cama y se vuelve luz de día: pasó una noche (rayos tenues siguen cruzando entre los dos). En el velador el plátano se pela solo y queda la cáscara. El recuadro cambia a `1 NOCHE ≈ 1 PLÁTANO`.
- **Una idea:** Una noche juntos es más o menos un plátano.
- **Qué cambia:**
  - 26,64 s · c799 · «¿Cuánto?»: salen `TÚ` y `PAREJA` (0,2 s) y entra el recuadro HUD `¿CUÁNTO?`; los subtítulos ocultan '¿cuánto?'
  - 27,58 s · c827 · «noche»: la luz de luna entra por la izquierda y cruza la cama (lineal hasta 29,10); un rayo tenue cruza de TÚ a la pareja cada ~0,6 s
  - 28,40 s · c852 · «más»: la franja pasa de azul luna a blanco día (estado 0,6 s), sin dejar de avanzar
  - 29,18 s · c875 · «comerte»: el plátano del velador se pela solo (pelado 0 → 1): queda la cáscara
  - 29,70 s · c891 · «plátano.»: el recuadro cambia a `1 NOCHE ≈ 1 PLÁTANO` (en el mismo lugar)
- **Movimiento:** recuadro entrada bezier(0.16, 1, 0.3, 1) 0,3 s; luz lineal; color estado bezier(0.65, 0, 0.35, 1); pelado estado 0,45 s; cambio de texto salida 0,15 s + entrada 0,3 s.
- **Etiquetas:**
  - `¿CUÁNTO?` (recuadro HUD) → — · centro (490, 595), y 560–630 · entra '¿Cuánto?' 26,64 · sale 'plátano.' 29,70
  - `1 NOCHE ≈ 1 PLÁTANO` (recuadro HUD) → — · centro (490, 595), y 560–630 (x 150–830) · entra 'plátano.' 29,70 · sale 'Pero' 31,48 (corte)
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `click-ui` 26,64 s (recuadro) · `whoosh-suave` 27,58 s (pasa la noche) · `papel` 29,18 s (se pela) · `pop` 29,70 s (la respuesta)
- **Zona segura:** Recuadro y 560–630; luz dentro de la cama.

### P12 · El dormitorio desde arriba (E2) · 30,53–31,48 s (cuadros 916–943)
- **Palabra gatillo:** «Inofensivo.» en 30,53 s (cuadro 916).
- **Qué se ve:** Check verde grande sobre la cama y recuadro verde `INOFENSIVO`; los dos siguen durmiendo y respirando.
- **Una idea:** Es inofensivo.
- **Qué cambia:**
  - 30,53 s · c916 · «Inofensivo.»: check verde (`check`, centro (390, 1040), tam 280) se dibuja y entra `INOFENSIVO` en recuadro verde debajo; los subtítulos ocultan 'inofensivo'
- **Movimiento:** check trazo lineal 0,3 s; recuadro entrada bezier(0.16, 1, 0.3, 1) 0,25 s.
- **Etiquetas:**
  - `INOFENSIVO` (recuadro verde) → — · centro (390, 1250) · entra 'Inofensivo.' 30,53 · sale 'Pero' 31,48 (corte)
  - `1 NOCHE ≈ 1 PLÁTANO` (recuadro HUD) → — · (490, 595) · entra sigue · sale 'Pero' 31,48
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `ding` 30,53 s (inofensivo)
- **Zona segura:** Check x 265–515, y 930–1150; recuadro y 1220–1285.

### P13 · La balanza: tu cama contra la central (E1) · 31,48–33,22 s (cuadros 944–996)
- **Palabra gatillo:** «súmale» en 31,66 s (cuadro 950).
- **Qué se ve:** CORTE (cambia la idea: el año) a la balanza, ahora al revés: la central pesa más (inclin −0,08): una sola cáscara en el platillo de la cama. HUD de la cama `NOCHE 1`, de la torre `1 AÑO`. El contador de noches corre y las cáscaras caen una tras otra; la balanza se nivela.
- **Una idea:** Súmale un año de noches.
- **Qué cambia:**
  - 31,48 s · c944 · «Pero»: CORTE a E1: balanza a −0,08 rad (torre abajo), una cáscara en el platillo de la cama, HUD `NOCHE 1` y `1 AÑO`; sin píldora
  - 31,66 s · c950 · «súmale»: el HUD de la cama corre `NOCHE 1 → 365` (rueda=False) y las cáscaras caen al platillo (pila 0 → 1); la balanza se nivela de a poco (−0,08 → 0,0); todo lineal hasta 33,22
- **Movimiento:** contador lineal; cada cáscara cae con salida bezier(0.6, 0, 0.9, 0.35) 0,2 s; el brazo sigue a la pila con estado suave; cámara quieta.
- **Etiquetas:**
  - `NOCHE 1 → 365` (número en vivo (HUD)) → platillo de la cama · centro (209, 680), 48 px · entra 'súmale' 31,66 · sale 'Esa' 33,22 (pasa a 1 AÑO) · número: 1 → 365 entre 31,66 y 33,22
  - `1 AÑO` (HUD) → platillo de la torre · centro (771, 680) · entra 'Pero' 31,48 · sale sigue hasta el final
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `whoosh-suave` 31,48 s (corte) · `tick-contador` 31,66 s (racha que acelera hasta 33,22) · `thud-suave` 32,16 s (cáscaras (3 golpes suaves: 32,16 · 32,52 · 32,90))
- **Zona segura:** Igual que P1: balanza x 80–900, y 720–1400; HUD y 650–710. La pila tiene que verse sobre el platillo (hoy `balanza` la dibuja detrás de `cama_chica`).

### P14 · La balanza: tu cama contra la central (E1) · 33,22–35,53 s (cuadros 997–1065)
- **Palabra gatillo:** «gana» en 34,49 s (cuadro 1035).
- **Qué se ve:** El contador llega a 365 y se vuelve `1 AÑO`, igual al de la torre: la balanza queda nivelada. La pila de cáscaras brilla en oro y, en 'gana', el platillo de la cama cae de golpe frente a la torre. Entra la píldora del cuadro 0.
- **Una idea:** Esa pila de plátanos le gana a la central (pago del gancho).
- **Qué cambia:**
  - 33,22 s · c997 · «Esa»: el contador llega a 365 y pasa a `1 AÑO` (estado 0,25 s); la balanza nivelada (0,0)
  - 33,51 s · c1005 · «pila»: la pila de cáscaras toma brillo oro (borde que brilla)
  - 34,49 s · c1035 · «gana»: el platillo de la cama cae de golpe (0,0 → 0,20 rad) con el ÚNICO rebote del video; la torre sube
  - 34,88 s · c1046 · «central.»: entra la píldora `TU CAMA > CENTRAL NUCLEAR` (la misma del cuadro 0)
- **Movimiento:** HUD estado bezier(0.65, 0, 0.35, 1); brillo entrada; caída aterrizaje con rebote bezier(0.55, 0, 0.2, 1.12) 0,45 s; píldora entrada bezier(0.16, 1, 0.3, 1) 0,3 s.
- **Etiquetas:**
  - `1 AÑO` (HUD) → platillo de la cama · centro (209, 680) · entra 'Esa' 33,22 · sale sigue hasta el final
  - `TU CAMA > CENTRAL NUCLEAR` (píldora) → — · (490, 582) · entra 'central.' 34,88 · sale 'Cada' 35,53 (corte); vuelve en P16
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `tick-grave` 33,22 s (365 → 1 AÑO) · `reveal-brillo` 33,51 s (la pila brilla) · `riser-1s` 33,49 s (alinear por el final en 34,49) · `impacto-pesado` 34,49 s (le gana) · `click-ui` 34,88 s (píldora)
- **Zona segura:** Igual que P1.

### P15 · El dormitorio desde arriba (E2) · 35,53–38,69 s (cuadros 1066–1160)
- **Palabra gatillo:** «plátano» en 37,42 s (cuadro 1123).
- **Qué se ve:** CORTE (cambia la idea: el remate) a la cama desde arriba, de noche (luz de luna azul pálido quieta sobre la colcha), los dos con su brillo oro; en el velador, la cáscara. El brazo de TÚ sale de la colcha y abraza a la pareja, que se vuelve un plátano gigante con brillo oro. Vuelve la etiqueta `PAREJA`, ahora sobre el plátano.
- **Una idea:** Duermes abrazado a un plátano gigante.
- **Qué cambia:**
  - 35,53 s · c1066 · «Cada»: CORTE a E2 de noche, sin etiquetas (TÚ 0,7, pareja 0,25)
  - 36,12 s · c1084 · «duermes»: el brazo de TÚ (manga de pijama + mano, pieza nueva) sale de la colcha hacia la pareja
  - 36,60 s · c1098 · «abrazado»: el brazo se apoya sobre la pareja: abrazo
  - 37,42 s · c1123 · «plátano»: la pareja se vuelve un plátano gigante con brillo oro bajo el brazo (izq_platano 0 → 1, fundido cruzado); la punta del plátano sobre la almohada, como cabeza
  - 37,81 s · c1134 · «gigante.»: vuelve la etiqueta `PAREJA`, apuntando al plátano
- **Movimiento:** brazo estado bezier(0.65, 0, 0.35, 1); transformación estado 0,4 s; etiqueta del kit 0,6 s; cámara quieta.
- **Etiquetas:**
  - `PAREJA` (etiqueta) → el plátano gigante (256, 900) · texto en (80, 565) · entra 'gigante.' 37,81 · sale 'Mándaselo' 38,69 (corte)
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `whoosh-suave` 35,53 s (corte) · `papel` 36,12 s (colcha) · `reveal-brillo` 37,42 s (plátano gigante) · `click-ui` 37,81 s (etiqueta)
- **Zona segura:** Plátano gigante dentro del marco (x 110–400, y 750–1330); etiqueta y 565–615.

### P16 · La balanza: tu cama contra la central (E1) · 38,69–41,90 s (cuadros 1161–1256)
- **Palabra gatillo:** «Mándaselo» en 38,69 s (cuadro 1161).
- **Qué se ve:** CORTE a la balanza como quedó en el pago (0,20 rad, pila con brillo, píldora y los dos `1 AÑO`) con el plátano gigante acostado en la cama del platillo. La pila se hunde en la cama y el plátano vuelve a ser la persona: el último cuadro es el cuadro 0.
- **Una idea:** Mándaselo a quien te irradia de noche (y vuelve al inicio).
- **Qué cambia:**
  - 38,69 s · c1161 · «Mándaselo»: CORTE a E1: balanza a 0,20, pila con brillo, plátano en la cama (platano_en_cama 1)
  - 39,50 s · c1185 · «tóxico»: la pila se hunde en la cama (pila 1 → 0) y su oro pasa a la cama (brillo_cama 0,35 → 0,6 → 0,35); el platillo sube un poco (0,20 → 0,135): la cama sola sigue pesando más
  - 40,46 s · c1214 · «tóxica.»: el plátano gigante vuelve a ser la persona (platano_en_cama 1 → 0) con su contorno oro tenue
  - 40,96 s · c1229 · (sin voz (loop)): cola sin voz: el brillo de la cama late (mismo período que el cuadro 0) y el platillo se hunde lento 0,135 → 0,140 (lineal hasta el último cuadro)
- **Movimiento:** hundirse salida bezier(0.6, 0, 0.9, 0.35) 0,6 s; platillo estado bezier(0.65, 0, 0.35, 1); transformación estado 0,4 s; cola lineal (empalma con la del cuadro 0).
- **Etiquetas:**
  - `TU CAMA > CENTRAL NUCLEAR` (píldora) → — · (490, 582) · entra ya está al corte · sale — (empalma con el cuadro 0)
  - `1 AÑO` (HUD) → platillos · (209, 680) y (771, 680) · entra ya están · sale — (empalman)
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `whoosh-suave` 38,69 s (corte) · `swoosh-baja` 39,50 s (la pila se hunde) · `pop` 40,46 s (vuelve la persona)
- **Zona segura:** Igual que P1.

## Loop
El último cuadro (1256, t = 41,87 s) es el estado de t = −1/30 del cuadro 0: balanza a 0,1399 rad hacia la cama, sin pila ni plátano, contorno oro de la cama en la misma fase del latido (período 41,9/26 s), vapor en la misma fase (período 41,9/12 s), píldora TU CAMA > CENTRAL NUCLEAR y los dos HUD `1 AÑO`. Sin etiquetas y sin subtítulo en los dos. 'Mándaselo a tu tóxica' → 'Un año en esta cama…': 'esta cama' apunta a la cama que acaba de quedar abajo.

## Revisión plano por plano

| Plano | ¿Una idea? | ¿Quieto mientras la voz habla de otra cosa? | Mayor hueco sin cambio |
|---|---|---|---|
| P1 | sí | no | 0,50 s |
| P2 | sí | no | 0,72 s |
| P3 | sí | no | 0,70 s |
| P4 | sí | no | 0,39 s |
| P5 | sí | no | 0,93 s |
| P6 | sí | no | 1,12 s |
| P7 | sí | no | 0,66 s |
| P8 | sí | no | 0,56 s |
| P9 | sí | no | 0,25 s |
| P10 | sí | no | 0,61 s |
| P11 | sí | no | 0,64 s |
| P12 | sí | no | 0,53 s |
| P13 | sí | no | 0,60 s |
| P14 | sí | no | 0,68 s |
| P15 | sí | no | 0,59 s |
| P16 | sí | no | 0,81 s |

Hueco máximo de todo el video: 1,12 s (11,85 → 12,97). Huecos > 1,2 s: 0. Ráfagas de 3 cambios en < 1 s: 0. Cortes: 4,32, 14,99, 22,64, 31,48, 35,53, 38,69 s. Calculado con un script sobre los cambios (inicio + duración de cada uno); los movimientos continuos de fondo (respiración, vapor, latido) no se cuentan.

## Pendientes de arte (`arte17.py`)
- `balanza`: la pila de cáscaras se dibuja ANTES que `cama_chica` y queda tapada; dibujarla delante/al lado de la cama en el platillo, y sumar una cáscara suelta para P13 (pila mínima) y el brillo oro de la pila (P14).
- `velador`: el docstring dice lámpara pero no la dibuja; falta la lámpara (pantalla redonda vista desde arriba) y su círculo de luz blanca tibia (P2).
- `cama_arriba`: falta `acerca` (la pareja se arrima ~24 px, P9), el brazo de TÚ que abraza (manga + mano, P15), ~60 puntitos de potasio dentro de TÚ (P5–P8) y las chispitas/destellos (P7).
- Luz de ventana (franja azul luna → blanco día) sobre la cama (P11 y la de noche quieta en P15).
- Anillo oro que sale de la cama en 'irradia' (P1) y la bocanada de vapor (P1).
