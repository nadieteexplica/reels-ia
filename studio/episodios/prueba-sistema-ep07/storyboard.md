# Prueba del sistema · Ep. 7 (guion D) — Storyboard v1 · Plano técnico

**No se publica.** Voz de 45,56 s (142 palabras, `words.json`); video de **46,43 s = 1393 cuadros** a 30 fps, 1080×1920 (0,87 s de cola sin voz para el loop). Todos los tiempos salen del inicio de la palabra en `words.json`; cada cambio cae en su cuadro exacto (margen ±2 cuadros). La misma información, para el animador, en `storyboard.json`.

**19 planos · 4 escenas (máx. 6) · 83 cambios en pantalla · hueco máximo sin cambio: 1,13 s.**

## Concepto
- **Estilo Plano técnico** (`kit_explica.ESTILOS['plano_tecnico']`): líneas blancas finas (3 px, #EAF2FA) sobre azul de Prusia #0E2A47; cada objeto nuevo se dibuja en orden de dibujante (contorno → piezas → cotas). **Energía: amarillo tiza #F2E27D** y sólo significa *lo que carga el techo*: la tapa, los gatos, sus cotas y números. Rojo #E5484D sólo para la dinamita y las ✗; ✓ verde #5CD68A sólo en dos marcas (P11, P18).
- **Un ancla que vuelve (biblioteca de virales, punto 4):** la tapa amarilla está en el cuadro 0 y en todas las escenas; el **gato de botella** se dibuja en P4 (s 7,6), vuelve como recuadro MISMO GATO en P8 (s 17,7), sostiene el auto en P15–P16 (s 34,5–38,6) y **es el mismo dibujo** que, por calce de cámara, resulta ser uno de los 15 gatos en el pago (P17, s 38,65).
- **Objetos reales, no íconos:** la torre es el Grand Prince Hotel Akasaka con su fachada en zigzag (los quiebres en V), el gato es un gato hidráulico de botella con tornillo de alivio y silleta, el auto un sedán de perfil, el calendario uno de taco con espiral, la dinamita un atado de 3 cartuchos con mecha, los obreros con casco.
- **Se entiende sin sonido:** contador de pisos en vivo, cota −6 PISOS, ✗ roja sobre la dinamita, 15 GATOS con contador, guías ventana-con-ventana + ✓ ALINEADAS, DÍA 1 → 10 y −2 PISOS, −1 PISO, TECHO ✓ / EDIFICIO ✗.
- **Cámara rápida (matiz de la ficha):** píldora chica CÁMARA RÁPIDA arriba a la izquierda en toda toma de la torre achicándose, desde el s 2,6 (nunca en 0–2 s), con el aviso en letra chica *ilustración · en la realidad, 2 pisos cada 10 días*. No va en P5–P6: ahí la torre entera es la hipótesis de la dinamita.
- **Seguridad:** los obreros siempre adentro de la zona cerrada y lejos de los bordes, con casco. Nada imitable.

### Lo que arregla de los jueces ciegos
- **Cuadro 0 = 'lámina de clase'.** El cuadro 0 ya no es un dibujo quieto: (1) la torre **ya se está achicando** (el piso bajo la tapa a medio borrar, la tapa bajando) y le faltan 2 pisos marcados por el fantasma punteado; (2) vista 3/4 con volumen leve (cara superior más clara, sombra corta) en vez de alzado plano; (3) brillo sólo en la tapa; (4) número vivo 38 PISOS que cambia a los 0,44 s; (5) escala humana (persona y 2 autos al pie, ciudad baja); (6) retícula bajada a 0,04, sin cajetín, sin título, sin cotas: lo único escrito es la píldora del gancho. El tono de 'plano' queda para la hoja del gato (E2), donde sí ayuda.
- **9,4–13,9 s sin nada nuevo.** Ahora tiene 7 cambios: cargas rojas + DINAMITA (9,48) → la cámara se aleja (10,27) → vecinos (10,59) → CENTRO DE TOKIO (10,80) → nube POLVO (11,76) → ondas RUIDO (12,14) → personitas 'sobre todos' (12,67) → ✗ roja y borrador (13,41). Hueco máximo 0,96 s.
- **32,3–38,6 s sin nada nuevo.** Ahora: tapa baja 2 pisos (32,03/32,21) → −2 PISOS (32,56) → '?' (33,21) → flecha hacia abajo (33,59) → la tapa late (33,96) → corte al gato (34,54) → se dibuja el auto (34,90) → llave de cruz (35,25) → RUEDA + cota (35,74) → VÁLVULA (36,47) → ariete brilla (37,01) → el auto baja (37,52) → la rueda toca (38,30) → calce a los 15 gatos (38,65). Hueco máximo 0,88 s.

## Escenas
- **E1 · La torre en la ciudad.** El Grand Prince Hotel Akasaka (Tokio) dibujado en líneas blancas finas, vista 3/4 desde la altura de un techo vecino: fachada en zigzag (los quiebres verticales en V que lo hacen reconocible), 40 pisos de ~24 px, base en y=1330, eje en x=470, ~330 px de ancho. La cara superior de la tapa con un tono más claro y una sombra corta en el suelo (volumen leve). Ciudad baja en gris #7E97B3 (8–10 bloques con ventanas en línea, una avenida con 2 autos y una persona chica al pie de la torre). Fantasma: contorno punteado de la altura original (40 pisos) siempre visible sobre la tapa. Retícula del fondo bajada a 0,04 (casi invisible), viñeta + grano 5.
- **E2 · El gato y el auto (la analogía).** Hoja limpia (mismo azul, retícula 0,10: aquí sí se nota que es un plano). Un gato hidráulico de botella real (base ancha, cuerpo cilíndrico, ariete con silleta estriada, tornillo de alivio, cavidad de la palanca) al centro, x=490, base en y=1290, ~520 px de alto. En P15–P16 encima se dibuja un sedán de perfil (x 80–900) apoyado por su punto de levante en la silleta.
- **E3 · El corte de la tapa.** Los 3 pisos de arriba de la misma torre en corte 3/4 (el frente sin muro): la tapa (el último piso reforzado con vigas en cruz) de x 120–860 e y 420–610; debajo, 15 gatos sobre columnas temporales (3 filas de 5 en perspectiva) en y 610–700; el piso de trabajo en y 700–900 con el pozo central en x=490; los pisos de abajo siguen en línea hasta y=1330.
- **E4 · La calle.** Contrapicado desde la vereda al pie de la torre (perspectiva de 3 puntos, fugas hacia arriba): la fachada en zigzag sube y converge; la tapa queda arriba en y 300–420. Vereda y cebra en y 1150–1340. Una persona de espaldas (en línea, la cabeza en y≈960) mira hacia arriba con el celular.

## Interfaz fija y cuenta de pisos
- **Píldora de frase:** centro (490, 255), y 225–285: SE ENCOGE CON EL TECHO (P1, P19) y LO NORMAL (P5–P6)
- **CÁMARA RÁPIDA:** píldora chica arriba a la izquierda (60, 225); en toda toma de la torre achicándose (P2–P3, P13–P14, P18–P19 hasta 45,85); nunca en 0–2 s ni en la hipótesis de la dinamita (P5–P6)
- **Contador de pisos:** arriba a la derecha (700–900, 235–300), 'N PISOS'; está en el cuadro 0; nunca sube salvo en el rebobinado del loop
- **Aviso:** letra chica (Inter 22, gris) bajo CÁMARA RÁPIDA en E1: 'ilustración · en la realidad, 2 pisos cada 10 días'
- **Cuenta de pisos (la misma en todo el video):** Original 40. Cuadro 0: 38 (fantasma de 2) → 37 en 'rascacielos' → 36 en 'encogiendo' → 35 en 'no' → 34 en 'sacan' (cota −6). P5–P6: la torre entera de 40 (hipótesis 'lo normal', sin contador). E3 arranca con la tapa en el piso 40 (el método empieza arriba). P13: 30 → 28. P18: 28 → 3 (casi el suelo: la ficha dice que el techo-tapa también se desarma al final, por eso no llega a 0). P19: rebobinado 3 → 38 = cuadro 0.
- **Subtítulos:** palabra por palabra, 1–3 palabras, centrados en la banda y 1380–1560 (kit subtitulos(..., y_centro=1470)); palabra clave en recuadro amarillo tiza con manillas (estilo_clave='recuadro'). Palabras en recuadro: *encogiendo*, *explosiones*, *techo*, *gato de auto*, *dinamita*, *polvo*, *ruido*, *tapa gigante*, *quince gatos hidráulicos*, *escondidos*, *ti*, *paneles*, *alineadas*, *un piso más*, *dos pisos menos*, *aflojas el gato*, *despacio*, *un piso*, *se fue el edificio*, *obra*.

## Resumen

| # | Escena | Segundos | Palabra gatillo (s · cuadro) | La idea |
|---|---|---|---|---|
| 1 | E1 | 0,00–2,06 | «Este» 0,20 · 6 | Este rascacielos se acorta y el techo baja entero con él. |
| 2 | E1 | 2,06–4,08 | «explosiones.» 3,19 · 96 | Lo raro no es que no haya explosiones. |
| 3 | E1 | 4,08–6,01 | «nunca» 4,37 · 131 | El techo es siempre el mismo: lo que se va es lo de abajo. |
| 4 | E2 | 6,01–8,56 | «gato» 7,63 · 229 | La analogía: un gato de auto. |
| 5 | E1 | 8,56–10,27 | «dinamita.» 9,48 · 284 | Lo normal sería dinamitarlo. |
| 6 | E1 | 10,27–13,89 | «ciudad,» 10,80 · 324 | En plena ciudad, la dinamita le cae a todos. |
| 7 | E3 | 13,89–16,38 | «tapa» 15,35 · 460 | El último piso se vuelve una tapa gigante. |
| 8 | E3 | 16,38–18,67 | «quince» 17,06 · 512 | La tapa se para sobre 15 gatos hidráulicos (el mismo gato de auto). |
| 9 | E3 | 18,67–22,34 | «desarman» 20,77 · 623 | Bajo la tapa, encerrados, desarman el piso de abajo. |
| 10 | E4 | 22,34–25,05 | «¿Escondidos» 22,34 · 670 | Se esconden de ti, que miras desde la calle. |
| 11 | E4 | 25,05–28,39 | «paneles» 25,55 · 766 | Los paneles tienen ventanas alineadas con las del edificio. |
| 12 | E4 | 28,39–30,61 | «parece» 29,31 · 879 | Desde abajo, parece un piso más. |
| 13 | E1 | 30,61–33,21 | «diez» 31,08 · 932 | Cada diez días, dos pisos menos. |
| 14 | E1 | 33,21–34,54 | «¿Y» 33,21 · 996 | ¿Y cómo baja el techo? |
| 15 | E2 | 34,54–36,47 | «auto» 34,90 · 1047 | Como tu auto, levantado en el gato para cambiar una rueda. |
| 16 | E2 | 36,47–38,65 | «aflojas» 36,47 · 1094 | Aflojas el gato y el auto baja despacio. |
| 17 | E3 | 38,65–41,34 | «Aquí,» 38,65 · 1160 | Aquí, quince gatos bajan el techo un piso (el pago). |
| 18 | E1 | 41,34–43,82 | «techo.» 41,88 · 1256 | Se quedó el techo. Se fue el edificio (el remate). |
| 19 | E1 | 43,82–46,43 | «obra.» 45,32 · 1360 | Mándaselo a quien vive junto a una obra (y vuelve al inicio). |

## Planos

### P1 · La torre en la ciudad (E1) · 0,00–2,06 s (cuadros 0–61)
- **Palabra gatillo:** «Este» en 0,20 s (cuadro 6).
- **Qué se ve:** CUADRO 0 (gancho completo, nunca negro): la torre en zigzag con 38 de sus 40 pisos; arriba de la tapa, 2 pisos punteados (el fantasma de lo que falta). La tapa (último piso + techo) rellena de amarillo tiza con brillo, ya bajando; el piso de abajo de la tapa se está borrando con un barrido (45 % hecho en el cuadro 0). Píldora arriba al centro SE ENCOGE CON EL TECHO. Contador chico arriba a la derecha 38 PISOS. Persona y 2 autos al pie para la escala.
- **Una idea:** Este rascacielos se acorta y el techo baja entero con él.
- **Qué cambia:**
  - 0,00 s · c0 · (cuadro 0): cuadro 0 ya en movimiento: el barrido borra el piso bajo la tapa (45 % → 100 %)
  - 0,44 s · c13 · «rascacielos»: la tapa baja 1 piso (aterriza sin rebote); contador 38 → 37; el fantasma suma 1 piso punteado
  - 1,25 s · c38 · «encogiendo.»: otro piso: barrido + tapa baja; 37 → 36; fantasma de 4 pisos
- **Movimiento:** barrido de borrado lineal 0,30 s de izquierda a derecha; tapa baja 1 piso con estado bezier(0.65, 0, 0.35, 1) 0,35 s; contador sin medio dígito (rueda=False); la cámara quieta (nada de zoom).
- **Etiquetas:**
  - `SE ENCOGE CON EL TECHO` (píldora) → — · centro (490, 255) · entra cuadro 0 (ya está) · sale 'Lo' 2,06 s, salida 0,4 s
  - `38 PISOS` (número en vivo) → — · arriba der. (700–900, 235–300) · entra cuadro 0 · sale sigue en E1 · número: 38 → 37 → 36
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `thud-suave` 0,44 s (la tapa asienta un piso) · `tick-grave` 0,44 s (contador) · `thud-suave` 1,25 s · `tick-grave` 1,25 s
- **Zona segura:** Torre y = 370–1330 (pie de la torre sobre la banda de subtítulos), x 305–635. Píldora y 225–285. Contador x ≤ 900. Nada bajo 1580; nada en x > 920.
- **Contra la lámina:** Contra 'lámina de clase': ya se mueve en el cuadro 0, vista 3/4 con volumen y sombra (no alzado plano), brillo sólo en la tapa, número vivo, escala humana, sin cajetín, sin cotas y retícula casi apagada.

### P2 · La torre en la ciudad (E1) · 2,06–4,08 s (cuadros 62–121)
- **Palabra gatillo:** «explosiones.» en 3,19 s (cuadro 96).
- **Qué se ve:** La misma torre (sigue bajando). Junto a la base, a la izquierda, cae un atado de 3 cartuchos de dinamita con mecha, en línea roja, y una ✗ roja se dibuja encima. Ni polvo ni humo en la torre.
- **Una idea:** Lo raro no es que no haya explosiones.
- **Qué cambia:**
  - 2,06 s · c62 · «Lo»: sale la píldora del gancho; entra la etiqueta 40 PISOS · TOKIO con línea guía a la punta del fantasma
  - 2,43 s · c73 · «no»: otro piso: 36 → 35
  - 2,60 s · c78 · «es»: píldora chica CÁMARA RÁPIDA arriba a la izquierda (matiz de la ficha; nunca antes de 2 s)
  - 3,19 s · c96 · «explosiones.»: cae la dinamita junto a la base (entrada 0,5 s) y la ✗ roja se traza encima en 0,3 s
- **Movimiento:** etiqueta entrada bezier(0.16, 1, 0.3, 1) 0,8 s (punto → guía → texto); dinamita entra con entrada bezier(0.16, 1, 0.3, 1) 0,5 s; ✗ trazada lineal 0,3 s; píldora del gancho salida bezier(0.6, 0, 0.9, 0.35) 0,4 s.
- **Etiquetas:**
  - `40 PISOS · TOKIO` (etiqueta) → la punta del fantasma (y≈370) · (560, 300) lado der. · entra 'Lo' 2,06 · sale 'nunca' 4,37 (salida 0,4)
  - `CÁMARA RÁPIDA` (píldora chica) → — · (60, 225) · entra 'es' 2,60 · sale 'entenderlo' 6,01
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `tick-grave` 2,43 s (piso) · `click-ui` 2,60 s (píldora) · `pop-grave` 3,19 s (cae la dinamita) · `buzz-error` 3,45 s (la ✗)
- **Zona segura:** Dinamita en x 90–260, y 1180–1320 (sobre la banda de subtítulos). Etiqueta TOKIO x 560–880.

### P3 · La torre en la ciudad (E1) · 4,08–6,01 s (cuadros 122–179)
- **Palabra gatillo:** «nunca» en 4,37 s (cuadro 131).
- **Qué se ve:** La torre ya más corta; la tapa amarilla se enciende (late) y una etiqueta la señala: EL MISMO TECHO. En 'techo' una cota amarilla une la punta del fantasma con la tapa y cuenta los pisos que faltan.
- **Una idea:** El techo es siempre el mismo: lo que se va es lo de abajo.
- **Qué cambia:**
  - 4,08 s · c122 · «Es»: sale la dinamita con su ✗
  - 4,37 s · c131 · «nunca»: la tapa late (brillo 0,6 → 1,0) y entra EL MISMO TECHO con guía a la tapa
  - 4,77 s · c143 · «sacan»: otro piso: 35 → 34
  - 5,15 s · c154 · «techo.»: cota vertical amarilla del fantasma a la tapa con número en vivo −0 → −6 PISOS
- **Movimiento:** brillo de la tapa estado bezier(0.65, 0, 0.35, 1) 0,4 s; cota crece con entrada bezier(0.16, 1, 0.3, 1) 0,7 s (kit cota_vertical); contador lineal.
- **Etiquetas:**
  - `EL MISMO TECHO` (etiqueta) → borde izquierdo de la tapa · (70, 520) lado izq. · entra 'nunca' 4,37 · sale 'entenderlo' 6,01
  - `−6 PISOS` (cota + número en vivo) → del fantasma (y 370) a la tapa (y 514) · cota en x=690, número en (720, 440) · entra 'techo' 5,15 · sale 'entenderlo' 6,01 · número: 0 → 6
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `swoosh-baja` 4,08 s (sale la dinamita) · `ding-grave` 4,37 s (la tapa se enciende) · `tick-grave` 4,77 s · `tick-contador` 5,15 s (cota que cuenta)
- **Zona segura:** Etiqueta x 70–300; cota x 690 y número hasta x 880.

### P4 · El gato y el auto (la analogía) (E2) · 6,01–8,56 s (cuadros 180–256)
- **Palabra gatillo:** «gato» en 7,63 s (cuadro 229).
- **Qué se ve:** Corte a la hoja limpia: un gato hidráulico de botella se dibuja en orden de dibujante (contorno → piezas). En 'gato' se rellena amarillo y brilla; en 'auto' baja sobre su silleta el bajo de un auto (zócalo de la carrocería con el punto de levante) y se apoya.
- **Una idea:** La analogía: un gato de auto.
- **Qué cambia:**
  - 6,01 s · c180 · «entenderlo»: corte; el contorno del gato se traza (base, cuerpo, ariete) en 0,7 s
  - 6,76 s · c203 · «sólo»: piezas: tornillo de alivio, cavidad de la palanca, silleta estriada
  - 7,63 s · c229 · «gato»: relleno amarillo tiza + brillo + etiqueta GATO
  - 8,00 s · c240 · «auto.»: el zócalo del auto baja y asienta en la silleta (golpe)
- **Movimiento:** trazos lineal a velocidad de lápiz (~1.400 px/s); relleno estado bezier(0.65, 0, 0.35, 1) 0,3 s; zócalo entra desde arriba con entrada bezier(0.16, 1, 0.3, 1) 0,45 s (sin rebote: el rebote se guarda para P17).
- **Etiquetas:**
  - `GATO` (etiqueta) → cuerpo del gato · (600, 900) lado der. · entra 'gato' 7,63 · sale 'Lo' 8,56
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `whoosh-rapido` 6,01 s (corte) · `papel` 6,01 s (firma del estilo: trazo (no hay raspado de lápiz en la biblioteca)) · `papel` 6,76 s (piezas) · `pop` 7,63 s (relleno) · `thud-metal` 8,00 s (el auto se apoya)
- **Zona segura:** Gato x 380–600, y 770–1290; zócalo hasta x 900; etiqueta x 600–860.

### P5 · La torre en la ciudad (E1) · 8,56–10,27 s (cuadros 257–307)
- **Palabra gatillo:** «dinamita.» en 9,48 s (cuadro 284).
- **Qué se ve:** Vuelve la torre, pero entera (40 pisos, sin tapa amarilla, en tinta blanca): es 'lo normal'. Píldora LO NORMAL. En 'dinamita', cargas rojas con mecha aparecen en las 6 columnas de la base y la etiqueta DINAMITA.
- **Una idea:** Lo normal sería dinamitarlo.
- **Qué cambia:**
  - 8,56 s · c257 · «Lo»: corte a la torre entera (sin contador ni CÁMARA RÁPIDA: es hipótesis)
  - 8,75 s · c262 · «normal:»: píldora LO NORMAL arriba al centro
  - 9,48 s · c284 · «dinamita.»: 6 cargas rojas en la base, una cada 0,09 s, + etiqueta DINAMITA
- **Movimiento:** corte seco; píldora entrada bezier(0.16, 1, 0.3, 1) 0,6 s; cargas pop con entrada bezier(0.16, 1, 0.3, 1) 0,25 s escalonadas 0,09 s.
- **Etiquetas:**
  - `LO NORMAL` (píldora) → — · centro (490, 255) · entra 'normal' 8,75 · sale 'Así' 13,41
  - `DINAMITA` (etiqueta roja (peligro)) → la carga de la izquierda · (70, 1150) · entra 'dinamita' 9,48 · sale 'Así' 13,41
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `whoosh-suave` 8,56 s (corte) · `click-ui` 8,75 s · `tick-contador` 9,48 s (cada carga) · `riser-1s` 10,27 s (tensión hacia la ciudad (alinear por el final en 10,27))
- **Zona segura:** Cargas en y 1290–1330, sobre la banda; etiqueta y 1150–1210.

### P6 · La torre en la ciudad (E1) · 10,27–13,89 s (cuadros 308–416)
- **Palabra gatillo:** «ciudad,» en 10,80 s (cuadro 324).
- **Qué se ve:** La cámara se aleja (revelación de escala): alrededor de la torre se dibujan los edificios vecinos, las calles y la gente. En 'polvo' una nube punteada gris crece desde la base y tapa a los vecinos; en 'ruido' salen ondas concéntricas; en 'todos' aparecen las personitas en las veredas y ventanas. En 'Así' una ✗ roja grande tacha todo y un borrador barre la nube.
- **Una idea:** En plena ciudad, la dinamita le cae a todos.
- **Qué cambia:**
  - 10,27 s · c308 · «Pero»: la cámara se aleja 0,9 s: la torre pasa de 75 % a 45 % del alto
  - 10,59 s · c318 · «plena»: los vecinos se dibujan en orden de dibujante (contornos, 0,5 s)
  - 10,80 s · c324 · «ciudad,»: etiqueta CENTRO DE TOKIO
  - 11,76 s · c353 · «polvo»: nube de polvo punteada crece y tapa los vecinos (1,0 s) + etiqueta POLVO
  - 12,14 s · c364 · «ruido»: ondas de ruido: 3 arcos que se abren + etiqueta RUIDO
  - 12,67 s · c380 · «todos.»: 8 personitas en veredas y ventanas (pop, 0,09 s entre una y otra)
  - 13,41 s · c402 · «Así»: ✗ roja grande sobre la escena + borrador que barre nube, ondas y cargas (0,45 s)
- **Movimiento:** alejarse con estado bezier(0.65, 0, 0.35, 1) 0,9 s; vecinos trazados lineal; nube crece con entrada bezier(0.16, 1, 0.3, 1) 1,0 s; ondas lineal (continuo); ✗ trazada lineal 0,3 s; borrador salida bezier(0.6, 0, 0.9, 0.35) 0,45 s.
- **Etiquetas:**
  - `CENTRO DE TOKIO` (etiqueta) → la avenida · (70, 300) · entra 'ciudad' 10,80 · sale 'Así' 13,41
  - `POLVO` (etiqueta) → borde de la nube · (620, 760) · entra 'polvo' 11,76 · sale 'Así' 13,41
  - `RUIDO` (etiqueta) → el arco exterior · (70, 860) · entra 'ruido' 12,14 · sale 'Así' 13,41
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `whoosh-suave` 10,27 s (se aleja) · `papel` 10,59 s (vecinos) · `whomp` 11,76 s (la nube) · `pop-agudo` 12,67 s (personitas) · `buzz-error` 13,41 s (la ✗) · `whoosh-rapido` 13,55 s (borrador)
- **Zona segura:** Toda la ciudad en y 280–1340; personitas sobre y 1340; etiquetas x ≤ 880.

### P7 · El corte de la tapa (E3) · 13,89–16,38 s (cuadros 417–490)
- **Palabra gatillo:** «tapa» en 15,35 s (cuadro 460).
- **Qué se ve:** La cámara sube por la torre hasta la cima y el frente de los 3 pisos de arriba se abre en corte. El último piso se marca en amarillo; adentro se trazan vigas de acero en cruz y el piso se rellena: es la TAPA. En 'gigante' aparece un obrero con casco en el piso de abajo, chico al lado de la tapa (escala).
- **Una idea:** El último piso se vuelve una tapa gigante.
- **Qué cambia:**
  - 13,89 s · c417 · «convierten»: la cámara sube y se acerca a la cima (0,9 s); el muro del frente se desvanece: corte
  - 14,44 s · c433 · «último»: contorno amarillo del último piso
  - 14,70 s · c441 · «piso»: vigas en cruz se trazan adentro (orden de dibujante, 0,5 s)
  - 15,35 s · c460 · «tapa»: relleno amarillo + brillo + etiqueta TAPA
  - 15,55 s · c466 · «gigante.»: obrero con casco al lado (escala), lejos de todo borde
- **Movimiento:** subida y acercamiento estado bezier(0.65, 0, 0.35, 1) 0,9 s (es el traslado a la escena E3, no un zoom de relleno); muro salida bezier(0.6, 0, 0.9, 0.35) 0,4 s; vigas lineal; relleno estado bezier(0.65, 0, 0.35, 1) 0,3 s; obrero entrada bezier(0.16, 1, 0.3, 1) 0,5 s.
- **Etiquetas:**
  - `TAPA` (etiqueta) → centro de la tapa · (620, 330) lado der. · entra 'tapa' 15,35 · sale 'Bajo' 18,67
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `swoosh-sube` 13,89 s (la cámara sube) · `papel` 14,70 s (vigas) · `reveal-brillo` 15,35 s (la tapa)
- **Zona segura:** Tapa x 120–860, y 420–610; etiqueta y 330–380; obrero x 200, y 760–900.

### P8 · El corte de la tapa (E3) · 16,38–18,67 s (cuadros 491–559)
- **Palabra gatillo:** «quince» en 17,06 s (cuadro 512).
- **Qué se ve:** Desde la tapa bajan columnas temporales; sobre ellas aparecen los 15 gatos de botella, uno por uno, con contador 1 → 15. En 'hidráulicos' se rellenan amarillo y entra un recuadro chico con el gato de P4: es el MISMO GATO.
- **Una idea:** La tapa se para sobre 15 gatos hidráulicos (el mismo gato de auto).
- **Qué cambia:**
  - 16,55 s · c496 · «paran»: columnas temporales se trazan de la tapa hacia abajo (0,4 s)
  - 17,06 s · c512 · «quince»: 15 gatos uno por uno (cada 0,04 s) + contador 1 → 15
  - 17,36 s · c521 · «gatos»: etiqueta 15 GATOS (el número es el del contador)
  - 17,68 s · c530 · «hidráulicos.»: gatos amarillos con brillo + recuadro MISMO GATO con el gato de P4
- **Movimiento:** columnas lineal; cada gato pop entrada bezier(0.16, 1, 0.3, 1) 0,25 s escalonado 0,04 s; recuadro entrada bezier(0.16, 1, 0.3, 1) 0,6 s (kit inset).
- **Etiquetas:**
  - `15 GATOS` (etiqueta + número en vivo) → gato de adelante a la izquierda · (70, 760) · entra 'gatos' 17,36 · sale 'Bajo' 18,67 · número: 1 → 15 (desde 'quince')
  - `MISMO GATO` (recuadro (inset)) → — · caja (640, 250)–(900, 470) · entra 'hidráulicos' 17,68 · sale 'Bajo' 18,67
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `papel` 16,55 s (columnas) · `tick-contador` 17,06 s (uno por gato, 15 ticks) · `ping` 17,68 s (el mismo gato)
- **Zona segura:** Gatos y 610–700; recuadro x ≤ 900, y 250–470 (no tapa la tapa: la tapa empieza en y 420 desde x 120, el recuadro se corre arriba-derecha y la tapa queda visible bajo él).

### P9 · El corte de la tapa (E3) · 18,67–22,34 s (cuadros 560–669)
- **Palabra gatillo:** «desarman» en 20,77 s (cuadro 623).
- **Qué se ve:** La cámara baja un piso: el piso de trabajo bajo la tapa. En 'escondidos' el muro de afuera vuelve en línea punteada y lo encierra (CERRADO). En 'desarman' dos obreros con casco sueltan una viga y la grúa colgada de la tapa la levanta; en 'piso' las vigas y losas se van de a una; en 'abajo' bajan por el pozo central.
- **Una idea:** Bajo la tapa, encerrados, desarman el piso de abajo.
- **Qué cambia:**
  - 18,67 s · c560 · «Bajo»: la cámara baja 1 piso (0,7 s); el piso de trabajo se aclara
  - 19,80 s · c594 · «escondidos,»: muro exterior punteado encierra la zona + etiqueta CERRADO
  - 20,77 s · c623 · «desarman»: 2 obreros sueltan una viga; la grúa interior la engancha y la sube
  - 21,31 s · c639 · «piso»: vigas y losas se van de a una (cada 0,2 s)
  - 21,69 s · c651 · «abajo.»: bajan por el pozo central: flecha punteada hacia abajo + etiqueta POZO
- **Movimiento:** cámara estado bezier(0.65, 0, 0.35, 1) 0,7 s; muro punteado trazado lineal 0,4 s; viga sube estado bezier(0.65, 0, 0.35, 1); piezas salen salida bezier(0.6, 0, 0.9, 0.35) 0,35 s; flecha lineal.
- **Etiquetas:**
  - `CERRADO` (etiqueta) → el muro punteado · (640, 640) · entra 'escondidos' 19,80 · sale '¿Escondidos' 22,34
  - `POZO` (etiqueta) → boca del pozo central · (620, 1000) · entra 'abajo' 21,69 · sale '¿Escondidos' 22,34
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `swoosh-baja` 18,67 s (baja la cámara) · `papel` 19,80 s (muro punteado) · `click-mecanico` 20,77 s (gancho de la grúa) · `tick-grave` 21,31 s (cada pieza) · `swoosh-baja` 21,69 s (bajan por el pozo)
- **Zona segura:** Piso de trabajo y 520–900 tras bajar la cámara; pozo x 450–530 hasta y 1330.

### P10 · La calle (E4) · 22,34–25,05 s (cuadros 670–751)
- **Palabra gatillo:** «¿Escondidos» en 22,34 s (cuadro 670).
- **Qué se ve:** Corte a la calle en contrapicado: la torre sube y converge, la tapa allá arriba. En 'quién' un '?' amarillo junto a la tapa. En 'ti' entra una persona de espaldas con el celular en alto (TÚ). En 'calle' se trazan la vereda y la cebra.
- **Una idea:** Se esconden de ti, que miras desde la calle.
- **Qué cambia:**
  - 22,34 s · c670 · «¿Escondidos»: corte al contrapicado desde la vereda
  - 22,94 s · c688 · «quién?»: '?' amarillo junto a la tapa (pop)
  - 23,71 s · c711 · «ti,»: persona de espaldas entra desde abajo-izquierda + etiqueta TÚ
  - 24,52 s · c736 · «calle.»: vereda y cebra se trazan bajo la persona
- **Movimiento:** corte seco; '?' entrada bezier(0.16, 1, 0.3, 1) 0,4 s; persona entrada bezier(0.16, 1, 0.3, 1) 0,7 s; cebra lineal 0,4 s.
- **Etiquetas:**
  - `TÚ` (etiqueta) → la cabeza de la persona · (560, 900) · entra 'ti' 23,71 · sale 'Desde' 28,39
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `whoosh-suave` 22,34 s (corte) · `pop` 22,94 s ('?') · `swoosh-sube` 23,71 s (entra la persona) · `papel` 24,52 s (cebra)
- **Zona segura:** Persona x 180–460, y 900–1340 (cortada por la banda de subtítulos, la cabeza arriba de y 960); '?' y 300–400; etiqueta x 560–700.

### P11 · La calle (E4) · 25,05–28,39 s (cuadros 752–851)
- **Palabra gatillo:** «paneles» en 25,55 s (cuadro 766).
- **Qué se ve:** La cámara sube por la fachada hasta los 2 pisos bajo la tapa (la persona queda grande en la esquina de abajo, cortada). Bajan paneles grises que los rodean; se les dibujan ventanas; en 'alineadas' líneas guía amarillas unen cada ventana del panel con la de la fachada de abajo, una por una, y aparece ✓ verde ALINEADAS.
- **Una idea:** Los paneles tienen ventanas alineadas con las del edificio.
- **Qué cambia:**
  - 25,05 s · c752 · «La»: la cámara sube por la fachada (0,8 s)
  - 25,21 s · c756 · «rodean»: paneles grises bajan alrededor de los 2 pisos de trabajo
  - 25,55 s · c766 · «paneles»: etiqueta PANELES
  - 26,06 s · c782 · «ventanas,»: ventanas de los paneles se trazan (cada 0,09 s)
  - 26,77 s · c803 · «alineadas»: guías amarillas ventana-con-ventana (cada 0,09 s)
  - 27,63 s · c829 · «edificio.»: ✓ verde + ALINEADAS
- **Movimiento:** cámara estado bezier(0.65, 0, 0.35, 1) 0,8 s; paneles bajan con entrada bezier(0.16, 1, 0.3, 1) 0,6 s; ventanas y guías lineal escalonadas 0,09 s; ✓ entrada bezier(0.16, 1, 0.3, 1) 0,4 s.
- **Etiquetas:**
  - `PANELES` (etiqueta) → panel de la izquierda · (70, 520) · entra 'paneles' 25,55 · sale 'Desde' 28,39
  - `✓ ALINEADAS` (etiqueta con ✓ verde) → la última guía · (600, 820) · entra 'edificio' 27,63 · sale 'Desde' 28,39
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `swoosh-sube` 25,05 s (sube la cámara) · `thud-suave` 25,21 s (paneles) · `tick-contador` 26,06 s (cada ventana) · `tick-contador` 26,77 s (cada guía) · `ding` 27,63 s (✓)
- **Zona segura:** Paneles y 480–700, x 140–840; ✓ x 600–880.

### P12 · La calle (E4) · 28,39–30,61 s (cuadros 852–917)
- **Palabra gatillo:** «parece» en 29,31 s (cuadro 879).
- **Qué se ve:** La cámara vuelve al ojo de la persona (se aleja): las guías se apagan y el borde de los paneles pasa de amarillo a blanco: desde abajo la franja de paneles se ve igual a cualquier piso. Etiqueta UN PISO MÁS. La persona baja el celular.
- **Una idea:** Desde abajo, parece un piso más.
- **Qué cambia:**
  - 28,39 s · c852 · «Desde»: la cámara vuelve a la vereda (0,9 s); las guías se apagan
  - 29,31 s · c879 · «parece»: borde de los paneles amarillo → blanco: queda igual a los demás pisos
  - 29,73 s · c892 · «piso»: etiqueta UN PISO MÁS con guía a la franja de paneles
  - 29,97 s · c899 · «más.»: la persona baja el celular
- **Movimiento:** alejarse estado bezier(0.65, 0, 0.35, 1) 0,9 s; guías salida bezier(0.6, 0, 0.9, 0.35) 0,4 s; color estado bezier(0.65, 0, 0.35, 1) 0,5 s; brazo estado bezier(0.65, 0, 0.35, 1) 0,4 s.
- **Etiquetas:**
  - `UN PISO MÁS` (etiqueta) → la franja de paneles · (560, 430) · entra 'piso' 29,73 · sale 'Pero' 30,61
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `whoosh-suave` 28,39 s (vuelve a la calle) · `click-ui` 29,73 s (etiqueta)
- **Zona segura:** Igual a P10.

### P13 · La torre en la ciudad (E1) · 30,61–33,21 s (cuadros 918–995)
- **Palabra gatillo:** «diez» en 31,08 s (cuadro 932).
- **Qué se ve:** Vuelve la torre de E1, ya con 30 pisos, el fantasma arriba y CÁMARA RÁPIDA. Arriba a la izquierda entra un calendario de taco con espiral; en 'diez' pasan 10 hojas con el número DÍA 1 → 10. En 'dos' la tapa baja 2 pisos (30 → 28) y entra −2 PISOS.
- **Una idea:** Cada diez días, dos pisos menos.
- **Qué cambia:**
  - 30,61 s · c918 · «Pero»: corte a la torre (30 PISOS, fantasma de 10 pisos, CÁMARA RÁPIDA)
  - 30,86 s · c926 · «cada»: entra el calendario de taco arriba a la izquierda
  - 31,08 s · c932 · «diez»: pasan 10 hojas en 0,6 s, número DÍA 1 → 10
  - 32,03 s · c961 · «dos»: la tapa baja un piso: 30 → 29
  - 32,21 s · c966 · «pisos»: otro: 29 → 28
  - 32,56 s · c977 · «menos.»: −2 PISOS grande junto a la tapa
- **Movimiento:** calendario entrada bezier(0.16, 1, 0.3, 1) 0,5 s; hojas lineal (una cada 0,06 s); tapa estado bezier(0.65, 0, 0.35, 1) 0,3 s por piso; −2 PISOS entrada bezier(0.16, 1, 0.3, 1) 0,6 s (kit numero_heroe).
- **Etiquetas:**
  - `DÍA 1 → 10` (número en vivo en el calendario) → — · calendario (70, 300)–(300, 520) · entra 'diez' 31,08 · sale 'Como' 34,54 · número: 1 → 10
  - `30 PISOS` (número en vivo) → — · arriba der. (700, 235) · entra 'Pero' 30,61 · sale 'Como' 34,54 · número: 30 → 29 → 28
  - `−2 PISOS` (número héroe) → la tapa · (640, 700) · entra 'menos' 32,56 · sale '¿Y' 33,21
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `whoosh-rapido` 30,61 s (corte) · `papel` 30,86 s (entra el calendario) · `tick-contador` 31,08 s (cada hoja) · `thud-suave` 32,03 s · `thud-suave` 32,21 s · `pop-grave` 32,56 s (−2 PISOS)
- **Zona segura:** Calendario x 70–300, y 300–520 (no pisa CÁMARA RÁPIDA, que va en y 225–275); −2 PISOS x 640–900.

### P14 · La torre en la ciudad (E1) · 33,21–34,54 s (cuadros 996–1035)
- **Palabra gatillo:** «¿Y» en 33,21 s (cuadro 996).
- **Qué se ve:** Misma torre: un '?' grande amarillo junto a la tapa; en 'baja' una flecha punteada hacia abajo late bajo la tapa; en 'techo' la tapa late.
- **Una idea:** ¿Y cómo baja el techo?
- **Qué cambia:**
  - 33,21 s · c996 · «¿Y»: '?' amarillo grande junto a la tapa; salen calendario y −2 PISOS
  - 33,59 s · c1008 · «baja»: flecha punteada hacia abajo bajo la tapa (late)
  - 33,96 s · c1019 · «techo?»: la tapa late
- **Movimiento:** '?' entrada bezier(0.16, 1, 0.3, 1) 0,4 s; flecha lineal (pulso continuo 0,5 s); brillo estado bezier(0.65, 0, 0.35, 1).
- **Etiquetas:**
  - `?` (signo grande) → la tapa · (650, 620) · entra '¿Y' 33,21 · sale 'Como' 34,54
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `pop` 33,21 s ('?') · `riser-1s` 34,54 s (hacia la analogía (alinear por el final en 34,54))
- **Zona segura:** '?' x 650–760.

### P15 · El gato y el auto (la analogía) (E2) · 34,54–36,47 s (cuadros 1036–1093)
- **Palabra gatillo:** «auto» en 34,90 s (cuadro 1047).
- **Qué se ve:** Corte al gato de P4, mismo lugar y tamaño. En 'auto' se dibuja encima un sedán de perfil (contorno → ruedas → vidrios) apoyado en el gato: la rueda delantera en el aire. En 'cambiar' aparece la llave de cruz sobre esa rueda; en 'rueda' la etiqueta RUEDA y una cota chica entre la rueda y el suelo.
- **Una idea:** Como tu auto, levantado en el gato para cambiar una rueda.
- **Qué cambia:**
  - 34,54 s · c1036 · «Como»: corte al gato de P4 (mismo encuadre)
  - 34,90 s · c1047 · «auto»: el sedán se traza encima en orden de dibujante (0,5 s)
  - 35,25 s · c1058 · «cambiar»: llave de cruz sobre la rueda en el aire
  - 35,74 s · c1072 · «rueda:»: etiqueta RUEDA + cota rueda-suelo
- **Movimiento:** corte seco; trazo del auto lineal; llave entrada bezier(0.16, 1, 0.3, 1) 0,4 s; cota entrada bezier(0.16, 1, 0.3, 1) 0,5 s.
- **Etiquetas:**
  - `RUEDA` (etiqueta) → la rueda en el aire · (70, 820) · entra 'rueda' 35,74 · sale 'Aquí' 38,65
  - `(cota sin número)` (cota) → hueco rueda-suelo · x=300, y 1230–1300 · entra 'rueda' 35,74 · sale 'despacio' 37,77 · número: sin cifra: es analogía, no dato
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `whoosh-rapido` 34,54 s (corte) · `papel` 34,90 s (trazo del auto) · `click-mecanico` 35,25 s (llave) · `click-ui` 35,74 s (etiqueta)
- **Zona segura:** Auto x 80–900, y 820–1300; nada bajo 1340.

### P16 · El gato y el auto (la analogía) (E2) · 36,47–38,65 s (cuadros 1094–1159)
- **Palabra gatillo:** «aflojas» en 36,47 s (cuadro 1094).
- **Qué se ve:** Una mano (en línea) gira el tornillo de alivio del gato (VÁLVULA). En 'gato' el ariete brilla; en 'baja' el auto baja despacio y la cota se cierra; al final de 'despacio' la rueda toca el suelo.
- **Una idea:** Aflojas el gato y el auto baja despacio.
- **Qué cambia:**
  - 36,47 s · c1094 · «aflojas»: la mano gira el tornillo (flecha curva) + etiqueta VÁLVULA
  - 37,01 s · c1110 · «gato»: el ariete se marca amarillo con brillo
  - 37,52 s · c1126 · «baja»: el auto baja (0,8 s) y la cota se achica en vivo
  - 37,77 s · c1133 · «despacio.»: la rueda toca el suelo (fin del movimiento en 38,30) y la cota se apaga
- **Movimiento:** giro del tornillo lineal 0,5 s; brillo estado bezier(0.65, 0, 0.35, 1); bajada del auto estado bezier(0.65, 0, 0.35, 1) 0,8 s (despacio, sin rebote).
- **Etiquetas:**
  - `VÁLVULA` (etiqueta) → tornillo de alivio · (600, 1100) · entra 'aflojas' 36,47 · sale 'Aquí' 38,65
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `click-mecanico` 36,47 s (válvula) · `swoosh-baja` 37,52 s (baja el auto) · `thud-suave` 38,30 s (la rueda toca)
- **Zona segura:** Mano x 600–860, y 1100–1300; etiqueta encima.

### P17 · El corte de la tapa (E3) · 38,65–41,34 s (cuadros 1160–1239)
- **Palabra gatillo:** «Aquí,» en 38,65 s (cuadro 1160).
- **Qué se ve:** Corte por calce: el gato queda en el mismo punto de la pantalla y la cámara se aleja hasta mostrar la tapa sobre sus 15 gatos (el corte de E3); ese gato era uno de ellos. En 'quince' se encienden en ola; en 'bajan' los arietes se recogen y la tapa entera baja un piso; en 'piso' aterriza (el único rebote del video): −1 PISO. El piso de abajo ya no está.
- **Una idea:** Aquí, quince gatos bajan el techo un piso (el pago).
- **Qué cambia:**
  - 38,65 s · c1160 · «Aquí,»: calce: la cámara se aleja del gato a la tapa con sus 15 gatos (0,9 s)
  - 39,23 s · c1177 · «quince»: los 15 gatos se encienden en ola (cada 0,04 s), contador 15
  - 39,82 s · c1195 · «bajan»: arietes se recogen y la tapa baja un piso (1,0 s)
  - 40,72 s · c1222 · «piso.»: aterriza con el único rebote del video + etiqueta −1 PISO
- **Movimiento:** alejarse estado bezier(0.65, 0, 0.35, 1) 0,9 s (revelación de escala con cámara, no corte seco); ola lineal; bajada estado bezier(0.65, 0, 0.35, 1) 0,9 s y el último 0,25 s aterriza bezier(0.55, 0, 0.2, 1.12) (único rebote elástico del video).
- **Etiquetas:**
  - `15 GATOS` (etiqueta) → gato de adelante · (70, 760) · entra 'quince' 39,23 · sale 'Se' 41,34
  - `−1 PISO` (número héroe) → la tapa · (640, 360) · entra 'piso' 40,72 · sale 'Se' 41,34
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `whoosh-suave` 38,65 s (se aleja) · `tick-contador` 39,23 s (ola) · `swoosh-baja` 39,82 s (baja la tapa) · `thud-metal` 40,72 s (aterriza)
- **Zona segura:** Igual a E3; −1 PISO x 640–900, y 360–440.

### P18 · La torre en la ciudad (E1) · 41,34–43,82 s (cuadros 1240–1314)
- **Palabra gatillo:** «techo.» en 41,88 s (cuadro 1256).
- **Qué se ve:** La torre de E1 (28 pisos, fantasma). En 'techo' TECHO ✓ verde junto a la tapa. En 'fue' cámara rápida al máximo: la tapa baja de 28 a 3 pisos y el contador corre; en 'edificio' EDIFICIO ✗ roja apunta al fantasma, ahora 37 pisos vacíos. Las dos etiquetas quedan quietas hasta 'obra' (TECHO ✓ 3,4 s; EDIFICIO ✗ 2,4 s: remate ≥ 2 s).
- **Una idea:** Se quedó el techo. Se fue el edificio (el remate).
- **Qué cambia:**
  - 41,34 s · c1240 · «Se»: corte a la torre: 28 PISOS, fantasma de 12, CÁMARA RÁPIDA
  - 41,88 s · c1256 · «techo.»: TECHO ✓ verde junto a la tapa
  - 42,65 s · c1280 · «fue»: la tapa baja de 28 a 3 pisos en 0,8 s; contador 28 → 3
  - 42,95 s · c1288 · «edificio.»: EDIFICIO ✗ roja con guía al fantasma
- **Movimiento:** etiquetas entrada bezier(0.16, 1, 0.3, 1) 0,6 s y después quietas (texto que se lee no se mueve); bajada continua lineal con estado bezier(0.65, 0, 0.35, 1) en los extremos; contador sin medio dígito.
- **Etiquetas:**
  - `TECHO ✓` (etiqueta ✓ verde) → la tapa · (620, 1020) · entra 'techo' 41,88 · sale 'obra' 45,32 (quieta 3,4 s)
  - `EDIFICIO ✗` (etiqueta ✗ roja) → el fantasma (mitad) · (600, 620) · entra 'edificio' 42,95 · sale 'obra' 45,32 (quieta 2,4 s)
  - `PISOS` (número en vivo) → — · arriba der. (700, 235) · entra 'Se' 41,34 · sale sigue · número: 28 → 3
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `whoosh-rapido` 41,34 s (corte) · `ding-grave` 41,88 s (✓) · `tick-contador` 42,65 s (contador que corre) · `impacto-pesado` 42,95 s (la ✗; grave, sin explosión)
- **Zona segura:** Tapa termina en y≈1260 (sobre la banda de subtítulos 1380); etiquetas x ≤ 900.

### P19 · La torre en la ciudad (E1) · 43,82–46,43 s (cuadros 1315–1392)
- **Palabra gatillo:** «obra.» en 45,32 s (cuadro 1360).
- **Qué se ve:** TECHO ✓ y EDIFICIO ✗ siguen quietas. El edificio vecino de la izquierda (residencial bajo, con balcones) pasa de gris a blanco; en 'vive' una ventana se prende amarilla con una silueta adentro. En 'obra' la torre se rebobina: sube de 3 a 38 pisos, el contador sube con ella y el fantasma vuelve a 2 pisos. Entra la píldora SE ENCOGE CON EL TECHO y el borrado del piso bajo la tapa arranca: el último cuadro es el cuadro 0.
- **Una idea:** Mándaselo a quien vive junto a una obra (y vuelve al inicio).
- **Qué cambia:**
  - 43,82 s · c1315 · «Mándaselo»: el vecino residencial (ya estaba en gris) se enciende a tinta blanca; TECHO ✓ / EDIFICIO ✗ siguen
  - 44,52 s · c1336 · «vive»: una ventana del vecino se prende amarilla con silueta
  - 45,32 s · c1360 · «obra.»: salen TECHO ✓ y EDIFICIO ✗ (0,4 s); rebobinado: la torre sube 3 → 38 pisos en 0,8 s
  - 45,85 s · c1376 · (sin voz (cola del loop)): vecino vuelve a gris, sale CÁMARA RÁPIDA, entra la píldora del gancho
  - 46,27 s · c1388 · (sin voz (loop)): arranca el borrado bajo la tapa: en 46,40 (cuadro 1392) queda en el estado de t = −1/30 del cuadro 0
- **Movimiento:** vecino estado bezier(0.65, 0, 0.35, 1) 0,4 s; ventana entrada bezier(0.16, 1, 0.3, 1) 0,3 s; rebobinado estado bezier(0.65, 0, 0.35, 1) 0,8 s; píldora entrada bezier(0.16, 1, 0.3, 1) 0,3 s; borrado lineal (el mismo del cuadro 0).
- **Etiquetas:**
  - `SE ENCOGE CON EL TECHO` (píldora) → — · centro (490, 255) · entra 45,85 (sin voz) · sale — (empalma con el cuadro 0)
  - `PISOS` (número en vivo) → — · arriba der. · entra sigue · sale — · número: 3 → 38
- **Sonido** (ids de `tools/sonido/biblioteca/catalog.json`): `swoosh-sube` 43,82 s (vecino) · `pop-agudo` 44,52 s (ventana) · `whoosh-reverso` 45,32 s (rebobinado; alinear por el final en 46,13) · `click-ui` 45,85 s (píldora)
- **Zona segura:** Vecino x 60–260, y 1000–1330; ventana prendida y≈1120.

## Loop
El último cuadro (1392, t = 46,40 s) es el estado de t = −1/30 del cuadro 0: torre de 38 pisos con fantasma de 2, tapa arriba con brillo, píldora SE ENCOGE CON EL TECHO, contador 38, el borrado del piso bajo la tapa al ~42 %; el cuadro 0 sigue el mismo barrido (45 %). Sin CÁMARA RÁPIDA y sin etiquetas en los dos. El remate deja la torre casi en el suelo y en «obra» el rebobinado la devuelve entera; la voz vuelve a decir «se está encogiendo».

## Revisión final, plano por plano

Revisé cada plano contra tres preguntas: ¿una sola idea?, ¿algo queda quieto mientras la voz habla de otra cosa?, ¿cuánto es lo más largo sin cambio (hasta el primer cambio del plano siguiente)?

| Plano | ¿Una idea? | ¿Quieto mientras la voz habla de otra cosa? | Mayor hueco sin cambio | Nota |
|---|---|---|---|---|
| P1 | sí | no | 0,81 s | el contador y la píldora son parte del gancho; nada más escrito |
| P2 | sí | no | 0,89 s | TOKIO es la etiqueta del objeto, no otra idea; la ✗ va en la misma palabra |
| P3 | sí | no | 0,86 s | la cota repite la idea con un número |
| P4 | sí | no | 0,87 s | el zócalo del auto dice 'de auto' sin escribirlo |
| P5 | sí | no | 0,79 s | hipótesis: sin contador ni CÁMARA RÁPIDA para no mezclar con lo real |
| P6 | sí | no | 0,96 s | la ✗ cierra la misma idea (descartada), no abre otra |
| P7 | sí | no | 0,83 s | el obrero da la escala de 'gigante' |
| P8 | sí | no | 0,99 s | el recuadro MISMO GATO es la analogía, no otra idea |
| P9 | sí | no | 1,13 s | el hueco más largo del video (1,13 s) es la bajada de cámara de 'Bajo'→'escondidos', con movimiento |
| P10 | sí | no | 0,81 s |  |
| P11 | sí | no | 0,86 s |  |
| P12 | sí | no | 0,92 s |  |
| P13 | sí | no | 0,95 s |  |
| P14 | sí | no | 0,58 s | plano corto (1,33 s): pregunta del clímax |
| P15 | sí | no | 0,73 s | la cota no tiene cifra: es analogía |
| P16 | sí | no | 0,88 s |  |
| P17 | sí | no | 0,90 s | único rebote elástico del video |
| P18 | sí | no | 0,87 s | remate: etiquetas quietas ≥ 2 s |
| P19 | sí | no | 0,80 s | la cola sin voz es sólo el loop |

**Segundos sin cambio > 2 s: ninguno.** Hueco máximo de todo el video: 1,13 s (P9, 18,67 → 19,80, mientras la cámara baja). Ningún hueco pasa de 1,2 s. Lo revisé con un script sobre los 83 cambios (todos atados al inicio de su palabra en `words.json`, salvo el cuadro 0 y los 2 del loop sin voz).

## Notas para el animador
- **Subtítulos:** la skill pide la banda y 1380–1560 y el storyboard deja esa banda libre; `kit_explica.subtitulos` por defecto los pone arriba (y_arriba=292). Usar `y_centro=1470`. Si se decide ponerlos arriba (como los virales), hay que bajar la píldora del gancho y CÁMARA RÁPIDA a y ≥ 430.
- **Sonido de firma del estilo** (raspado de lápiz) no existe en la biblioteca: uso `papel` bajo cada trazo nuevo. Si se genera un `lapiz` en `tools/sonido/generar.py`, reemplaza a `papel` en P4, P6, P7, P8, P9, P10, P13 y P15.
- **Objetos que el kit no tiene todavía:** torre en zigzag 3/4 con tapa (E1/E3/E4), gato de botella, sedán de perfil, calendario de taco, dinamita, mano en la válvula, obreros con casco en línea. Del kit sirven: `etiqueta`, `cota_vertical`, `contador` (rueda=False), `numero_heroe`, `pildora_energia`, `inset`, `x_roja`, `persona`, `persona_espalda`, `linea_punteada`, `glow`, `ease_*`.
- **Números en pantalla y fuentes:** 40 PISOS · TOKIO (Prince Hotels, AFP, Core77); 15 GATOS (AFP, Taisei); 2 PISOS CADA 10 DÍAS (AFP, NBC, Nikkei); paneles con ventanas alineadas (Nikkei). Los conteos intermedios (38, 34, 30, 28, 3) son ilustrativos, en cámara rápida; el auto y su cota no llevan cifras. No va '90 % menos polvo' ni la grúa que genera electricidad (va al comentario fijado, como dice el guion).
