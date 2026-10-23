# Ep. 5 — Storyboard v1 (fichas de plano) · voz de 41,40 s (video 41,90 s)

Tiempos reales de `words.json` (voz con 14 pausas recortadas con `tools/pausas.py`: 45,79 → 41,40 s; 0 créditos). 30 fps, vertical 1080×1920. Escalas: **G** general · **M** medio · **P** primer plano · **D** detalle.

## Concepto
- **Idea:** una rana viva flota dentro de un imán. El agua (y todo lo que la tiene) es empujada un poquito por un imán; con uno bien fuerte, ese empujón le gana a la gravedad. "Por qué no": el imán del refri es miles de veces más débil. Fantasía con números reales y en condicional: el imán que haría falta para hacerte flotar a ti (casi 40 T, cerca de 1 GW = un reactor nuclear).
- **Estilo: realista** (`estilo.json`): "realista pero en un mundo animado" (Tomás, 22-oct 23:26; calidad tipo Zack D. Films, nunca su marca). Render 3D con materiales imperfectos, luz de atardecer con dirección, lente real y profundidad de campo, AgX. **Nada de imágenes o video fotorrealistas de IA.**
- **Todo al aire libre (Tomás, 23-oct 00:23):** un **salar de Atacama al atardecer**, abierto y con mucho cielo (menos ruido visual): costra de sal en polígonos, cordillera y un volcán de cono a lo lejos, cielo físico con el sol bajo.
- **Todo a escala real (Tomás, 00:25):** la rana es un **escaneo de una rana real** (*Pelophylax*, CC-BY) de **~2,8 cm**, porque en el experimento cabía en un hueco de ~3 cm. Flota **dentro de un tubo de vidrio** en la boca de un electroimán de 1,25 m. Pete mide 1,79 m. El imán gigante tiene un hueco donde cabe una persona. La central nuclear (torres de ~150 m) está a ~2,4 km.
- **Personajes (`ficha.jpg`):** la **rana** y **Pete** (Mixamo With Skin, elegido por Tomás). Pete es el obrero que arma el imán y el que flota en la fantasía. **Sin objetos en la mano: 0 Kling.** Las poses salen de las animaciones de Mixamo del repo privado (Happy Idle).
- **Escenas (5; 3 sets a medida):**
  - **E1 imán de la rana**: el electroimán sobre una losa en el salar, con la rana en el tubo. Planos 1–4, 8, 9 y 19 (también el cierre).
  - **E2 adentro de la rana**: moléculas de agua entre células del tejido y el empujón del imán. Planos 5–7.
  - **E3 el refri**: Pete junto a un refri en medio del salar; no flota. Planos 10–12.
  - **E4 se construye el imán gigante**: los anillos van bajando uno por uno, después el cobre y los pernos, y los cables cruzan el salar hasta la central nuclear. Planos 13–16.
  - **E5 Pete flota**: Pete flota sobre la boca del imán gigante (SIMULACIÓN). Planos 17 y 18.
  - **Sets:** salar + electroimán (E1, a medida) · interior (E2, a medida) · salar + imán gigante + central (E4 y E5, a medida). E3 reusa el salar.
- **Código de color fijo:**
  - cian = líneas del imán;
  - naranjo = el empujón del imán;
  - gris = la gravedad;
  - azul = agua;
  - amarillo = SIMULACIÓN / hipotético.
- **Palabras clave en el subtítulo:** FLOTANDO (amarillo), AGUA (azul), GRAVEDAD (gris), TESLAS y GIGAVATIO (naranjo).
- **Cuadro 0 (estudio `docs/estudios/ep05.md`):**
  - La rana ya está flotando quieta dentro del tubo, sobre la boca negra del imán, con el horizonte del salar detrás: se entiende sin sonido.
  - Es verdad. Abrir con la persona sería mostrar como real algo que no pasó.
  - En 0–2 s la cámara le da la vuelta y en el 2 mira desde arriba (no hay nada que la sostenga). Ahí entra SIN HILOS.
- **Loop:** el plano 19 vuelve a la cámara del cuadro 0. "sin hilos" empalma con "Esta rana está flotando".
- **Gráficos:**
  - Píldoras en y 330–560. Nunca en la franja de subtítulos (y 1000–1250).
  - La píldora **SIMULACIÓN** (amarilla, arriba a la izquierda) queda fija desde el 13 hasta el 18.
  - Las flechas de fuerza en E1 van al lado de la rana, no encima.
- **Seguridad:** nadie acerca imanes a personas ni a animales. La rana se ve bien y tranquila. No se dice que se haya hecho flotar a una persona.

| # | Tiempo | Frase de la voz | Escena | Plano (escala) | Plantilla | Acción visible (se lee en 1 foto) | Cambio (≤ 2 s) | Cámara | Cara (y) | Gráfico (dónde) | SFX | Origen |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.00–1.85 | Esta rana está flotando... | E1 imán de la rana | P 3/4 | a medida | CUADRO 0: la rana quieta en el aire dentro del tubo de vidrio, sobre la boca negra del imán; atrás el horizonte del salar al atardecer | órbita continua de 35° alrededor del tubo; la rana gira apenas sobre sí misma | 100 mm, órbita a la altura de la rana | 450–800 | — | zumbido grave del imán | render |
| 2 | 1.85–3.14 | y nadie la sostiene. | E1 imán de la rana | D desde arriba | a medida | la cámara sube y mira desde arriba por la boca del tubo: nada sobre la rana | la cámara sube todo el plano; a 0,4 s SIN HILOS | 100 mm, grúa hacia arriba | 450–800 | píldora amarilla SIN HILOS (y 400) | "ding" | render |
| 3 | 3.14–5.02 | La levanta un imán gigante. | E1 imán de la rana | G | a medida | la cámara retrocede y baja: el electroimán azul entero (1,25 m) sobre su losa, en medio del salar; la rana diminuta arriba | grúa continua hacia atrás; a 0,9 s IMÁN | 35 mm, dolly atrás | — | píldora cian IMÁN (y 400) | golpe grave + zumbido | render |
| 4 | 5.02–5.90 | ¿Cómo? | E1 imán de la rana | P → D piel | a medida | la cámara se lanza hacia la rana hasta la piel mojada con gotitas | push-in rápido continuo | 100 mm, push-in | 450–800 | — | whoosh | render |
| 5 | 5.90–8.20 | La rana es, en gran parte, agua. | E2 adentro de la rana | M | a medida | adentro: células rojas del tejido y moléculas de agua flotando | push-in lento; a 1,0 s entra AGUA; las moléculas giran | 50 mm, push-in | — | píldora azul AGUA (y 400) | burbuja "glup" | render |
| 6 | 8.20–11.50 | Y al agua, un imán la empuja... un poquito. | E2 adentro de la rana | M molécula | a medida | una molécula de agua (ángulo real) al centro; suben las líneas cian del imán y le sale una flecha naranja chica hacia arriba | líneas crecen desde 0,2 s; la flecha nace en "empuja" (2,6 s); a 2,6 s UN POQUITO | 50 mm, órbita lenta | — | flecha 3D en la molécula; píldora (y 400) | zumbido + "tic" | render |
| 7 | 11.50–14.05 | Ese empujoncito lo recibe cada molécula. | E2 adentro de la rana | G muchas | a medida | la cámara retrocede: muchas moléculas, a cada una le sale su flecha | las flechas se encienden en ola durante todo el plano | 35 mm, dolly atrás | — | flechas 3D | "tic tic tic" en cascada | render |
| 8 | 14.05–17.00 | Y con un imán bien fuerte, le gana a la gravedad. | E1 imán de la rana | M | a medida | la rana en el tubo; al lado, flecha gris hacia abajo (GRAVEDAD) y naranja hacia arriba (IMÁN) que crece hasta igualarla y ganarle | a 0,3 s flecha gris; la naranja crece desde 0,8 s y gana a 2,0 s; la rana sube 4 mm | 100 mm, push-in | 450–800 | flechas y píldoras al lado derecho de la rana | "whoom" que sube | render |
| 9 | 17.00–18.62 | Le pasa a una fresa... | E1 imán de la rana | P | a medida | sobre la misma boca, dentro del tubo, flota una fresa girando | corte seco; gira todo el plano | 100 mm, órbita | — | — | pop | render |
| 10 | 18.62–19.31 | y a ti. | E3 el refri | P | kit E1 (salar) | Pete de frente en el salar, mira a la cámara | push-in; respira (Happy Idle) | 50 mm | 400–650 | — | — | render |
| 11 | 19.31–21.30 | ¿Por qué no flotas junto al refri? | E3 el refri | M | kit E1 (salar) | Pete de pie junto a un refri en medio del salar: los pies en el suelo | idle; a 1,0 s la cámara baja hacia los pies | 35 mm, tilt abajo | 350–600 | — | "boing" chico | render |
| 12 | 21.30–24.17 | Porque ese imán es miles de veces más débil. | E3 el refri | D puerta del refri | kit E1 (salar) | un imán de refri en la puerta, con una flecha naranja diminuta | a 0,3 s flecha chiquita; a 1,2 s MILES DE VECES MÁS DÉBIL; push-in | 85 mm | — | píldora (y 420) y flecha | "pfff" | render |
| 13 | 24.17–26.60 | ¿Y si quisiéramos hacerte flotar a ti? | E4 se construye el imán gigante | G | a medida | el salar vacío al atardecer, Pete de pie mirando el cielo; la losa del imán vacía | a 0,3 s SIMULACIÓN (fija hasta el 18); push-in | 35 mm | 350–700 | SIMULACIÓN arriba a la izquierda | viento | render |
| 14 | 26.60–29.20 | Haría falta un imán gigante donde quepas. | E4 se construye el imán gigante | G time-lapse | a medida | se arma el imán: los anillos bajan uno por uno sobre la losa, al lado de Pete (escala) | un anillo cada ~0,5 s; órbita lenta | 35 mm, órbita | 350–700 | SIMULACIÓN | golpes metálicos rítmicos | render |
| 15 | 29.20–32.65 | Casi cuarenta teslas: más del doble que el de la rana. | E4 se construye el imán gigante | M tapa | a medida | más cerca: se cierra la tapa de cobre y los pernos; el cobre brilla | tapa a 0,4 s; a 0,8 s CASI 40 TESLAS; a 1,9 s MÁS DEL DOBLE QUE EL DE LA RANA | 24 mm, grúa | — | SIMULACIÓN + píldoras naranjas (y 400–520) | golpe + zumbido | render |
| 16 | 32.65–36.60 | Y gastaría cerca de un gigavatio: un reactor nuclear entero. | E4 se construye el imán gigante | G hacia el horizonte | a medida | la cámara gira a lo largo de los cables que cruzan el salar hasta la central nuclear en el horizonte; los cables se encienden | paneo continuo; a 0,6 s ≈ 1 GIGAVATIO; a 2,3 s = 1 REACTOR NUCLEAR; luz que corre por los cables | 35 mm, paneo | — | SIMULACIÓN + píldoras naranjas | zumbido eléctrico que sube | render |
| 17 | 36.60–38.10 | Ahí sí flotarías. | E5 Pete flota | M | kit E4 (imán gigante) | Pete sube despacio y queda flotando sobre la boca del imán gigante | Pete sube 0,5 m todo el plano | 35 mm, grúa | 350–650 | SIMULACIÓN | "whoom" | render |
| 18 | 38.10–39.10 | Todo eso... | E5 Pete flota | G | kit E4 (imán gigante) | plano abierto: Pete flotando, el imán gigante, los cables y la central atrás | dolly atrás continuo | 24 mm | — | SIMULACIÓN | zumbido | render |
| 19 | 39.10–41.90 | para lo que esta rana hace sin hilos. | E1 imán de la rana | P 3/4 (cámara del cuadro 0) | a medida | la rana flotando en el tubo, igual que el cuadro 0 | órbita igual a la del 1 (loop) | 100 mm | 450–800 | — | zumbido grave | render |
