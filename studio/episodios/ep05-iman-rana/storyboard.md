# Ep. 5 — Storyboard v3 (fichas de plano) · voz de 38,82 s (video 39,35 s)

Tiempos reales de `words.json` (voz v3 con `tools/pausas.py`: 4 pausas recortadas y las del remate y de los 3 pasos alargadas según la puerta 2: 38,45 → 38,82 s; 0 créditos). 30 fps, vertical 1080×1920. Escalas: **G** general · **M** medio · **P** primer plano · **D** detalle.

## Concepto
- **Idea (v3, pedido de Tomás):** "tú" desde el segundo 0. Tu cuerpo repele los imanes y, con el imán correcto, podrías flotar. La rana es la prueba real (4–8 s) y la mecánica va en 2 frases (agua → empujón → le gana a la gravedad). Después se **construye el imán para ti en 3 pasos** (el hueco, las bobinas y la energía), con números de fuente. Termina con Pete flotando y vuelve al cuadro 0.
- **Qué cambia contra el v2:**
  - sin el refri (E3 sale entera);
  - el gancho es Pete flotando (SIMULACIÓN desde el cuadro 0);
  - la construcción gana 2 planos nuevos (el hueco que sale del suelo y el hueco de la rana visto desde arriba con su medida);
  - las barras 16 T contra 40 T.
- **Estilo: realista** (`estilo.json`, `docs/ESTILO_REALISTA.md`): render 3D con materiales imperfectos, salar de Atacama al atardecer con el sol bajo, lente real y profundidad de campo, AgX + `grado.py`. Los mismos sets y luces que aprobaron las puertas 4, 6 y 7 del v2. **Nada de imágenes ni video fotorrealistas de IA.**
- **Todo a escala real:**
  - la rana (escaneo real de *Pelophylax*, CC-BY) mide ~2,2 cm, dentro del tubo de 3,2 cm en la boca de un electroimán de 1,25 m;
  - Pete mide 1,79 m;
  - el imán gigante mide 3,55 m de alto y 5 m de ancho, con un hueco de 1,9 m.
- **Personajes (`ficha.jpg`):** la **rana** y **Pete** (Mixamo With Skin). Sin objetos en la mano: 0 Kling. Las poses salen de Happy Idle (repo privado), ahora **en loop con el cuadro** en todos los planos (en el v2 Pete flotaba con una pose fija).
- **Escenas (4; 3 sets a medida):**
  - **E1 imán de la rana:** planos 3, 4, 5, 8 y 11.
  - **E2 adentro de la rana:** plano 7.
  - **E4 se construye el imán gigante:** planos 6, 9, 10, 12, 13, 14 y 15. Pete en el salar; el hueco sale del suelo, las bobinas caen una tras otra, cae la tapa, se enciende el cobre y los cables cruzan el salar hasta la central nuclear.
  - **E5 Pete flota:** planos 1, 2 y 16. Mismo set que E4, con el imán terminado.
- **Código de color fijo:**
  - cian = imán y líneas del imán;
  - naranjo = el empujón y la fuerza del imán (teslas, gigavatio);
  - gris = la gravedad;
  - azul = agua;
  - amarillo = SIMULACIÓN y la palabra activa del subtítulo;
  - blanco = pasos y datos.
- **Palabras clave en el subtítulo (3):** AGUA (azul), TESLAS y GIGAVATIO (naranjo; GIGAVATIO ya no se dice: sólo va escrito en la píldora). Cifras juntas: "tres" → 3 y "cuarenta" → 40.
- **Cuadro 0:**
  - Pete flotando en el aire a 1,2 m sobre la boca negra del imán gigante, recortado contra los cerros al atardecer, con la píldora amarilla SIMULACIÓN.
  - Se lee sin sonido: "una persona flotando sobre una máquina".
  - La voz dice "Tu cuerpo repele los imanes": la promesa capciosa sobre ti.
  - No se presenta como real: la SIMULACIÓN está desde el cuadro 1 y la rana, que sí es real, lleva la píldora ESTO SÍ PASÓ.
- **Loop:** el plano 16 termina **exacto en la cámara y la pose del cuadro 0** (misma posición, lente y altura de Pete). "flotarías" empalma con "Tu cuerpo repele los imanes".
- **Gráficos:**
  - Píldoras en y 330–600. Nunca en la franja de subtítulos (y 1000–1250).
  - SIMULACIÓN (amarilla, arriba a la izquierda, y 330) en todos los planos con Pete o el imán gigante hipotético: 1, 2, 9, 10, 12–16. No va en el 6 ("como tú": Pete de pie en el salar, nada hipotético).
  - Los pasos son píldoras blancas "PASO 1 · EL HUECO", "PASO 2 · BOBINAS" y "PASO 3 · ENERGÍA", en y 450 (bajo SIMULACIÓN), y entran justo en "Primero", "Después" y "final".
  - Píldoras de 3 palabras como máximo (más el número del paso).
- **Plan de render (flujo realista, `docs/ESTILO_REALISTA.md`):**
  - muestras de cada plano a 540×960/8 (3 por plano) y revisión;
  - final a 720×1280/8 con denoise, en hasta 16 máquinas (~60 min, coordinado con el Ep. 6);
  - la puerta 6 se hace sobre el final, y los parches van por pieza (`piezas` + `base_run`).
- **Seguridad:** nadie acerca imanes a personas ni a animales. La rana se ve bien y tranquila. Nunca se dice que se haya hecho flotar a una persona: todo lo de Pete va en condicional y con SIMULACIÓN.

| # | Tiempo | Frase de la voz | Escena | Plano (escala) | Plantilla | Acción visible (se lee en 1 foto) | Cambio (≤ 2 s) | Cámara | Cara (y) | Gráfico (dónde) | SFX | Origen |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.00–1.95 | Tu cuerpo repele los imanes. | E5 Pete flota | M contrapicado (cámara del cuadro B v2.1) | kit E4 (imán gigante) | CUADRO 0: Pete flota a 1,2 m sobre la boca negra del imán gigante, con los pies sobre el horizonte y los cerros detrás; pose de flotar (brazos abiertos 18° con vaivén de equilibrio, rodillas sueltas, punta de los pies hacia abajo) | dolly in de 12 a 10,8 m con órbita de 4°; Pete sube y baja 4 cm y gira ±4° suelto en el aire | 35 mm, 12 m, apenas sobre la tapa · sol de costado (a ~90° de la mirada), fuera del cuadro | 300–800 | SIMULACIÓN (x 250, y 330) desde el cuadro 1 | whoom grave + zumbido | render |
| 2 | 1.95–4.45 | Con el imán correcto, podrías flotar. | E5 Pete flota | G (todo el imán y el salar) | kit E4 | Pete flotando sobre el imán entero; los cables cruzan el salar hasta la central humeando en el horizonte. Detrás de Pete y del aire bajo sus pies: los cerros y el cielo (nunca el salar: no se lee "parado lejos") | dolly out lento; en "imán" (2,30) el cobre de la tapa brilla un instante; Pete en su vaivén de flotar | 24 mm, de 20 a 27 m, cámara baja (1,6–1,7 m) en contrapicado: los pies de Pete (4,75 m) quedan 6–8° sobre el horizonte · sol de costado (~85° de la mirada) | 500–750 | SIMULACIÓN | zumbido eléctrico suave; "ding" en "flotar" | render |
| 3 | 4.45–6.30 | Ya pasó con esta rana: flota | E1 imán de la rana | P 3/4 | a medida | la rana real flotando quieta en el aire dentro del tubo de vidrio, de 3/4 (se ve un ojo); de fondo, la sal a contraluz | órbita continua de 35° alrededor del tubo; en "pasó" (4,71) entra ESTO SÍ PASÓ | 100 mm, órbita a 22 cm · contraluz: el sol atrás de la rana, fuera del cuadro (la sal azul de fondo, como el cuadro A) | 450–800 | píldora blanca ✓ ESTO SÍ PASÓ (x 540, y 330; ubicada con lugar_libre) | whoosh de cambio + zumbido del imán | render |
| 4 | 6.30–8.00 | sola dentro de un imán. | E1 imán de la rana | D cenital → G | a medida | desde arriba y de lado, sobre el tubo (27 cm: más cerca se veía oscuro y turbio adentro): no hay nada sobre la rana; la cámara se aleja y aparece el electroimán entero sobre su losa en el salar | grúa hacia atrás todo el plano; en "sola" (6,34) SIN HILOS; en "imán" (7,30) IMÁN | 100 → 30 mm · contraluz de costado (sol a 50–60° de la mirada, fuera del cuadro) | 450–800 | SIN HILOS (x 540, y 330) hasta "imán"; ahí la reemplaza IMÁN cian en el mismo lugar | "ding"; golpe grave en "imán" | render |
| 5 | 8.00–9.30 | Es más que nada agua, | E1 imán de la rana | P → D (la piel) | a medida | la cámara se mete hasta el ojo y la piel mojada de la rana | push-in todo el plano; en "agua" (8,97) AGUA | 100 mm, de 22 cm a ~5 cm (a 2 cm el escaneo era una mancha café) · contraluz (como el 3) | 400–800 | AGUA azul (x 540, y 330) desde "nada" (8,63) | whoosh hacia adentro | render |
| 6 | 9.30–10.30 | como tú. | E4 (salar vacío) | M | kit E4 | Pete de pie en el salar al atardecer, de 3/4 hacia la cámara (lo que es agua también eres tú) | dolly in corto; Pete respira (Happy Idle) | 50 mm a 8 m, a la altura del pecho; 15° al lado de la cámara del 9, así la central queda fuera del cuadro · sol de costado y atrás (~80° de la mirada): la cara en semisombra con borde de luz | 550–650 | HASTA 60 % AGUA azul (x 540, y 400, sobre la cabeza; lugar_libre) | "ding" | render |
| 7 | 10.30–13.50 | Y al agua, un imán la empuja... un poquito. | E2 adentro | M | a medida | adentro de la rana: moléculas de agua entre células; las líneas cian del imán suben y a la molécula del medio le sale una flecha naranja hacia arriba | líneas suben (10,5–11,9); flecha en "empuja" (11,46); la molécula sube un poquito; UN POQUITO en "poquito" (12,62) | 50 mm, órbita lenta de 14° · interior: luz de estudio (llave y contra) | — | AGUA azul hasta "empuja"; UN POQUITO (x 540, y 400) | "glup" al entrar; "tic" en "empuja"; "ding" en "poquito" | render |
| 8 | 13.50–17.00 | Con uno bien fuerte, ese empujón le gana a la gravedad. | E1 imán de la rana | P | a medida | la rana flotando con 2 flechas al lado: gris hacia abajo (GRAVEDAD) y naranja hacia arriba (IMÁN), que crece hasta ganarle | a 0,3 s la flecha gris; a 0,8 s la naranja; en "fuerte" (14,43) ≈ 16 TESLAS; en "gana" (15,80) la naranja supera a la gris y la rana sube 4 mm | 100 mm, 40 cm · contraluz (como el 3) | 450–800 | flechas a la derecha de la rana; ≈ 16 TESLAS naranjo arriba a la izquierda (x 300, y 330), lejos de la etiqueta IMÁN | whoom que sube en "gana" | render |
| 9 | 17.00–19.65 | ¿Y para ti? Habría que construirlo. | E4 (salar vacío) | G | kit E4 | Pete de pie junto a la losa vacía en medio del salar, con la central nuclear lejos; levanta la cabeza hacia donde irá el imán | dolly lento; a 1,1 s Pete mira hacia arriba; SIMULACIÓN en "construirlo" (18,70) | 35 mm, 15–18 m · sol de costado (~95° de la mirada) | ~830–870 (mirada más baja que en el v2) | SIMULACIÓN desde "construirlo" | whoosh de la parte hipotética | render |
| 10 | 19.65–22.00 | Primero: un hueco donde quepas. | E4 | M (Pete y el hueco) | kit E4 | PASO 1: un tubo de acero oscuro de 1,9 m de ancho y 3,1 m de alto sale del suelo en la losa, a la derecha de Pete (cabe una persona de pie); Pete levanta la cabeza para verlo | en "Primero" (19,72) PASO 1; el tubo sube en 1,4 s por un hoyo con tapa de acero en la losa y la cámara tiembla al llegar; en "quepas" la grúa sube a 6,8 m y mira adentro: se ve la boca del hueco (de lado se leía como un pilar: puerta 3 r2) | 24 mm, Pete a 6 m (a la izquierda, x ~220) y el hueco a 9 m (a la derecha, x 580–1010) · mirada a 62°: el sol queda a 32° de la mirada, fuera del cuadro (de costado y adelante) | 650–750 | SIMULACIÓN; PASO 1 · EL HUECO (x 330, y 470: cielo sobre Pete) | rumor grave + golpe cuando llega | render |
| 11 | 22.00–25.50 | El de la rana mide tres centímetros: ni tu mano cabe. | E1 imán de la rana | P de costado → G | a medida | v3.1 (tras las muestras: el cenital se veía oscuro y turbio adentro del tubo): de costado y de cerca, el tubo de vidrio con la rana flotando adentro (y ~620); en "mano", la cámara se aleja y aparece al lado del tubo el contorno blanco de una mano adulta a escala real (palma de 8,5 cm, 20 cm de largo, dedos hacia arriba): la mano es ~3 veces más ancha que el hueco | push-in lento; en "tres" (23,15) la cota; desde 23,93 la cámara se aleja (de 32 cm a 1,4 m, 100 → 60 mm), la cota se apaga y entra la mano; en "mano" (24,78) NO CABE | 100 → 60 mm, órbita casi de frente · contraluz (como el 3) | 450–800 | cota de pared a pared del tubo **9 mm por encima de la rana** (nunca sobre ella ni sus ojos), con flechas en los bordes reales y "3 cm" encima; mano a la izquierda del tubo (el pulgar hacia afuera, lejos de la rana); NO CABE (x 790, y 330, sobre el tubo) | "tic" de la cota; "boing" chico | render |
| 12 | 25.50–28.20 | Después: bobinas y más bobinas, | E4 | G (Pete y el imán) | kit E4 | PASO 2: 5 bobinas de cobre (con las vueltas del alambre en relieve) caen del cielo una sobre otra alrededor del hueco y al final la carcasa de acero, con sus aros y tubos, baja encima como una funda; Pete mira desde al lado | en "Después" (25,58) PASO 2; una bobina llega cada 0,33 s (26,30–27,62) desde fuera del cuadro, en 0,5 s; la carcasa llega en 27,90; la cámara tiembla en cada golpe | 35 mm, órbita de 18,5 m (de −40° a −30°) a la altura de los ojos · mirada a ~50°: el sol a ~20° de la mirada, fuera del cuadro (el plano 13 del v2, aprobado) | ~830–870 (mirada más baja que en el v2) | SIMULACIÓN; PASO 2 · BOBINAS (x 330, y 470) | "clank" metálico en cada bobina; golpe grave en la carcasa | render |
| 13 | 28.20–32.25 | hasta cuarenta teslas o más. Más del doble de lo que necesitó la rana. | E4 | G alto (la tapa) | kit E4 | cae la tapa con las bandas de cobre y los pernos; en "teslas" el cobre se enciende naranjo | la tapa cae a 0,4 s; en "cuarenta" (28,27) ≈ 40 TESLAS O MÁS; en "doble" (30,51) 2 barras: RANA 16 T (cian) y TÚ 40 T O MÁS (naranjo, 2,5 veces más larga) | 24 mm, alta sobre la tapa, dolly in · sol de costado (el plano 14 del v2, aprobado) | — | SIMULACIÓN; ≈ 40 TESLAS O MÁS (x 540, y 450); barras sobre un panel oscuro (y 520–712) | "clank" de la tapa; zumbido que sube en "teslas"; "ding" en las barras | render |
| 14 | 32.25–35.55 | Y al final, enchufarlo a un reactor nuclear entero... | E4 | G (de atrás del imán a la central) | kit E4 | PASO 3: los cables crecen desde el imán, cruzan el salar y se encienden; la cámara gira hasta la central nuclear humeando en el horizonte | en "final" (32,56) PASO 3; cables crecen 1,2 s; brillo en "enchufarlo" (33,16); paneo hasta la central (termina en 34,25); en "entero" (34,79) ≈ 1 GIGAVATIO | 35 mm, alta sobre el imán · el paneo baja de mirar la tapa a mirar el horizonte, con el rumbo casi fijo (de ~125° a ~122°): el sol queda siempre a ~92°, de costado (nunca detrás de la cámara ni en el cuadro) | — | SIMULACIÓN; PASO 3 · ENERGÍA (x 540, y 470) hasta "reactor"; al final la central queda a la derecha y sobre los subtítulos (x ~580–820, y ~600–900) y ≈ 1 GIGAVATIO naranjo va a la izquierda (x ≤ 330), sin tapar la central. Sin "1 REACTOR NUCLEAR" (repetía el subtítulo) | zumbido eléctrico que sube; "dings" | render |
| 15 | 35.55–36.70 | solo para ti. | E4 | M contrapicado | kit E4 | Pete de pie al pie del imán terminado (cables encendidos), mirando hacia arriba | dolly in corto; Pete respira | 35 mm a 5 m, cámara baja (0,7 m) en contrapicado, del mismo lado que el 12 · sol de costado y atrás (~26° fuera del cuadro): la cara en semisombra con borde de luz | 550–650 | SIMULACIÓN | zumbido del imán | render |
| 16 | 36.70–39.35 | Ahí sí... flotarías. | E5 Pete flota | M contrapicado (cámara del cuadro 0) | kit E4 | Pete sale flotando del hueco y queda a 1,2 m sobre la boca, recortado contra los cerros, con la pose de flotar | Pete sube 2,1 m todo el plano; dolly in hasta la cámara exacta del cuadro 0 (loop: la misma pose, altura y giro de Pete) | 35 mm, 13,5 → 12 m · sol como en el 1 (de costado) | 300–800 | SIMULACIÓN | whoom que sube | render |

## Ficha por plano (lo que va a mirar el auditor)
- **Todos:**
  - nada tapa la cara de Pete ni los ojos de la rana (chequeo automático);
  - la franja de subtítulos (y 1000–1250) queda libre de caras y de gráficos;
  - nada quemado: el sol nunca entra al cuadro;
  - el salar llega al horizonte, con los cerros apoyados en el suelo.
- **1 y 16 (loop):** la cámara y la altura de Pete del cuadro 0 son las del último cuadro del 16. Pete no toca la boca (1,2 m de aire bajo los pies, recortado contra los cerros).
- **3–5, 8 y 11 (la rana):**
  - la rana siempre dentro del tubo, sin tocar el vidrio (giros de ±8° como máximo);
  - respira (pulso de escala de 1 %);
  - ESTO SÍ PASÓ va sólo en planos de la rana.
- **6 y 9 (Pete en el salar vacío):** Pete entero dentro del cuadro y con los pies en el suelo; nada flota; la central queda lejos y al fondo.
- **10 (el hueco):**
  - el tubo sale del suelo sin atravesar a Pete;
  - es de acero oscuro con reflejo, no un negro plano, para que se lea como pieza de metal;
  - cuando llega, mide como una persona y media de alto.
- **11 (3 cm):**
  - la cota calza con los bordes del tubo en pantalla (se calcula proyectando los bordes reales) y va 9 mm por encima de la rana: ninguna línea ni rótulo pasa sobre ella;
  - la mano se dibuja a escala real con la misma proyección y sólo cuando la cámara ya se alejó (cabe entera en el cuadro, sobre los subtítulos y lejos de la rana);
  - "NO CABE" son 2 palabras.
- **12 (bobinas):**
  - las piezas entran desde fuera del cuadro (no aparecen en el aire);
  - se ven caer al menos 4;
  - cada llegada tiene su golpe;
  - Pete no queda debajo de nada que cae.
- **13 (40 T):** las barras van en proporción real (16 contra 40) y con rótulos legibles. El cobre se enciende en "teslas", no antes.
- **14 (energía):** al final del paneo la central se ve entera, sin que la tape el imán. Los cables nacen en los conectores del imán.
- **15:** Pete entero y con la cara sobre la franja de subtítulos.
- **Sol:** está anotado en la columna "Cámara" de cada plano. Nunca va detrás de la cámara (luz pareja de maqueta) ni dentro del cuadro. En los planos con Pete de cerca (6 y 15), va de costado y atrás.
- **Píldoras:** se ubican una vez por plano con `graficos.lugar_libre`, mirando los ojos de todos los cuadros del plano (no saltan de un cuadro a otro). La x y la y de la columna "Gráfico" son las preferidas.

## Cambios (cada 1–2 s)
Ningún tramo pasa 2 s sin cambio. Cada plano de más de 2 s trae su cambio interno en la columna "Cambio" (píldora, flecha, pieza que cae o cambio de cámara). Los cortes caen en el comienzo de cada frase.
