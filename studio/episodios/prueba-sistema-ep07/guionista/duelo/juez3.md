# Duelo de Shorts

Vas pasando YouTube Shorts con el pulgar. En este tipo de canal, 1 de cada 4 personas desliza antes de los 2 segundos.
Abajo hay 66 pares de videos. De cada video tienes SOLO lo que se ve y se oye en los primeros 3 segundos.
En cada par, elige cuál deslizarías primero (el que pierde tu atención antes). No hay empates.
Juzga como alguien cualquiera en un feed, no como experto.

Contesta SOLO con un JSON válido:
{"pares": [{"par": "<P1>", "desliza_primero": "<código>", "razon": "<una frase>"}, ...]}

## P1
**PV**
- Cuadro 0: Fondo oscuro, pantalla partida. Izquierda (~45 % del ancho): una torre implosionando en una nube de polvo gris, ✗ rojo. Derecha (~45 %): torre blanca de 40 pisos con el techo ámbar intacto, sin polvo.
- 0–3 s: A la izquierda la torre cae en polvo; a la derecha la torre baja un piso entero, limpia, con el techo igual. A los 2 s la izquierda se apaga y queda la derecha.
- Texto en pantalla: SIN UNA EXPLOSIÓN
- Voz 0–3 s: "Este rascacielos ya perdió la mitad, y sin una explosión."

**JY**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos centrada, ~75 % del alto; al lado, un calendario naranja (~15 % del cuadro) pasa hojas; con cada hoja la torre baja dos pisos, techo naranja entero.
- 0–3 s: El calendario pasa diez hojas en 1 s y la torre se acorta dos pisos; se repite una vez. Píldora chica CÁMARA RÁPIDA en una esquina desde los 2,5 s.
- Texto en pantalla: −2 PISOS CADA 10 DÍAS
- Voz 0–3 s: "Este rascacielos pierde dos pisos cada diez días."

## P2
**BT**
- Cuadro 0: Fondo oscuro. Rascacielos de 40 pisos al centro, ~80 % del alto; el techo en ámbar. Una grúa chica intenta levantar el techo y aparece un ✗ rojo grande encima. Píldora: NO LE SAQUES EL TECHO.
- 0–3 s: En 0,3 s la grúa levanta un poco el techo; en 1,2 s el ✗ rojo la frena y el techo vuelve a su lugar. En 2,5 s se borra el piso bajo el techo.
- Texto en pantalla: NO LE SAQUES EL TECHO
- Voz 0–3 s: "Para desarmar este rascacielos, nunca le saques el techo."

**UU**
- Cuadro 0: Fondo azul casi negro. Torre blanca de 40 pisos, centrada, ~75 % del alto. El último piso, en ámbar, intacto. Sobre él, una línea punteada marca la altura original, varios pisos más arriba. Camión con escombros saliendo por la base.
- 0–3 s: En 0,3 s la fachada se hunde un piso bajo el techo ámbar, que no cambia de forma; la punteada queda más lejos. A los 2,5 s el techo se ilumina.
- Texto en pantalla: LO ESTÁN DEMOLIENDO
- Voz 0–3 s: "Demuelen este rascacielos y no le sacan el techo."

## P3
**GC**
- Cuadro 0: Fondo oscuro. Rascacielos de 40 pisos al centro, ~80 % del alto, con edificios vecinos pegados a los lados (~15 % cada uno). Cartuchos de dinamita en la base, tachados con ✗ rojo. Píldora: SIN RUIDO. SIN POLVO.
- 0–3 s: En 0,2 s caen cartuchos de dinamita junto a la base; en 0,8 s se tachan con ✗ rojo. En 1,8 s el techo ámbar baja un piso y la torre queda más corta.
- Texto en pantalla: SIN RUIDO. SIN POLVO.
- Voz 0–3 s: "Dinamita no. Este rascacielos tiene que desaparecer sin hacer ruido."

**TE**
- Cuadro 0: Fondo azul noche casi negro. Torre blanca de 40 pisos, fachada en zigzag, centrada, ~75 % del alto y ~30 % del ancho. El último piso, marcado en naranja, ya va bajando: la torre se acorta.
- 0–3 s: La torre pierde pisos de arriba en cámara rápida; el techo naranja baja con ella, entero. A los 2,5 s, píldora chica CÁMARA RÁPIDA en una esquina.
- Texto en pantalla: SE ENCOGE CON EL TECHO
- Voz 0–3 s: "Este rascacielos se está encogiendo. Lo raro no es que no haya explosiones."

## P4
**KI**
- Cuadro 0: Fondo oscuro. Corte lateral de la punta de una torre blanca, ~70 % del cuadro: el techo ámbar arriba, debajo un piso totalmente vacío y, entre los dos, columnas de acero con gatos hidráulicos sosteniéndolo.
- 0–3 s: Los gatos se encogen y el techo ámbar baja despacio hacia el piso vacío; una viga cae fuera de cuadro. A los 2,5 s la cámara corta a la torre entera: el techo sigue arriba.
- Texto en pantalla: SIN PISO DEBAJO
- Voz 0–3 s: "A este rascacielos le sacaron el piso bajo el techo."

**UX**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos, ~75 % del alto. Los 2 pisos de arriba en corte: adentro, una grúa naranja levanta una viga del piso; afuera, paneles con ventanas tapan todo.
- 0–3 s: La viga sube en 0,4 s; el corte se cierra y la torre se ve entera e igual; vuelve a abrirse y falta un piso. Una sola píldora.
- Texto en pantalla: LO DESARMAN A ESCONDIDAS
- Voz 0–3 s: "A este rascacielos lo desarman a escondidas. Por arriba."

## P5
**WJ**
- Cuadro 0: Fondo oscuro. Una torre de 40 bloques de madera al centro, ~75 % del alto; una mano saca el bloque de arriba. Contador grande ×1 arriba a la derecha, en ámbar.
- 0–3 s: En 0,3 s la mano levanta el bloque de arriba. En 1,5 s el contador sube a ×100 y la torre se vuelve un rascacielos de 40 pisos, mismo tamaño en cuadro.
- Texto en pantalla: ×1 → ×100
- Voz 0–3 s: "Desarmar una torre es fácil: sacas el de arriba. Ahora hazlo con esta."

**TS**
- Cuadro 0: Fondo oscuro. Rascacielos de 40 pisos al centro, ~80 % del alto, con edificios vecinos pegados a los lados (~15 % cada uno). Cartuchos de dinamita en la base, tachados con ✗ rojo. Píldora: SIN RUIDO. SIN POLVO.
- 0–3 s: En 0,2 s caen cartuchos de dinamita junto a la base; en 0,8 s se tachan con ✗ rojo. En 1,8 s el techo ámbar baja un piso y la torre queda más corta.
- Texto en pantalla: SIN RUIDO. SIN POLVO.
- Voz 0–3 s: "Dinamita no. Este rascacielos tiene que desaparecer sin hacer ruido."

## P6
**EA**
- Cuadro 0: Fondo azul noche casi negro. Torre blanca de 40 pisos, fachada en zigzag, centrada, ~75 % del alto y ~30 % del ancho. El último piso, marcado en naranja, ya va bajando: la torre se acorta.
- 0–3 s: La torre pierde pisos de arriba en cámara rápida; el techo naranja baja con ella, entero. A los 2,5 s, píldora chica CÁMARA RÁPIDA en una esquina.
- Texto en pantalla: SE ENCOGE CON EL TECHO
- Voz 0–3 s: "Este rascacielos se está encogiendo. Lo raro no es que no haya explosiones."

**PB**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos centrada, ~75 % del alto. A su pie, un cartucho de dinamita rojo tachado con una X naranja; la torre ya empieza a acortarse desde arriba.
- 0–3 s: La X tacha la dinamita en 0,3 s; la torre se acorta en cámara rápida con el techo naranja bajando entero. Píldora chica CÁMARA RÁPIDA en una esquina desde los 2,5 s.
- Texto en pantalla: SIN DINAMITA
- Voz 0–3 s: "A este rascacielos no lo dinamitaron. Lo encogieron."

## P7
**PI**
- Cuadro 0: Fondo azul noche. Rascacielos de 40 pisos al centro, ~80 % del alto, ~35 % del ancho, techo en ámbar. El piso bajo el techo ya se está borrando. Píldora: SIN UNA EXPLOSIÓN.
- 0–3 s: En 0,3 s se borra un piso bajo el techo y el techo baja un escalón; en 1,8 s, otro. En 2,4 s entra una dinamita y se tacha con ✗ rojo.
- Texto en pantalla: SIN UNA EXPLOSIÓN
- Voz 0–3 s: "Tienes que hacer desaparecer este rascacielos. Sin una explosión."

**VD**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos centrada, ~75 % del alto; al lado, un calendario naranja (~15 % del cuadro) pasa hojas; con cada hoja la torre baja dos pisos, techo naranja entero.
- 0–3 s: El calendario pasa diez hojas en 1 s y la torre se acorta dos pisos; se repite una vez. Píldora chica CÁMARA RÁPIDA en una esquina desde los 2,5 s.
- Texto en pantalla: −2 PISOS CADA 10 DÍAS
- Voz 0–3 s: "Este rascacielos pierde dos pisos cada diez días."

## P8
**WG**
- Cuadro 0: Fondo oscuro. Rascacielos de 40 pisos al centro, ~80 % del alto, con edificios vecinos pegados a los lados (~15 % cada uno). Cartuchos de dinamita en la base, tachados con ✗ rojo. Píldora: SIN RUIDO. SIN POLVO.
- 0–3 s: En 0,2 s caen cartuchos de dinamita junto a la base; en 0,8 s se tachan con ✗ rojo. En 1,8 s el techo ámbar baja un piso y la torre queda más corta.
- Texto en pantalla: SIN RUIDO. SIN POLVO.
- Voz 0–3 s: "Dinamita no. Este rascacielos tiene que desaparecer sin hacer ruido."

**VP**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos centrada, ~75 % del alto. A su pie, un cartucho de dinamita rojo tachado con una X naranja; la torre ya empieza a acortarse desde arriba.
- 0–3 s: La X tacha la dinamita en 0,3 s; la torre se acorta en cámara rápida con el techo naranja bajando entero. Píldora chica CÁMARA RÁPIDA en una esquina desde los 2,5 s.
- Texto en pantalla: SIN DINAMITA
- Voz 0–3 s: "A este rascacielos no lo dinamitaron. Lo encogieron."

## P9
**JW**
- Cuadro 0: Fondo oscuro. Rascacielos de 40 pisos al centro, ~80 % del alto, con edificios vecinos pegados a los lados (~15 % cada uno). Cartuchos de dinamita en la base, tachados con ✗ rojo. Píldora: SIN RUIDO. SIN POLVO.
- 0–3 s: En 0,2 s caen cartuchos de dinamita junto a la base; en 0,8 s se tachan con ✗ rojo. En 1,8 s el techo ámbar baja un piso y la torre queda más corta.
- Texto en pantalla: SIN RUIDO. SIN POLVO.
- Voz 0–3 s: "Dinamita no. Este rascacielos tiene que desaparecer sin hacer ruido."

**QJ**
- Cuadro 0: Fondo oscuro, pantalla partida. Izquierda (~45 % del ancho): una torre implosionando en una nube de polvo gris, ✗ rojo. Derecha (~45 %): torre blanca de 40 pisos con el techo ámbar intacto, sin polvo.
- 0–3 s: A la izquierda la torre cae en polvo; a la derecha la torre baja un piso entero, limpia, con el techo igual. A los 2 s la izquierda se apaga y queda la derecha.
- Texto en pantalla: SIN UNA EXPLOSIÓN
- Voz 0–3 s: "Este rascacielos ya perdió la mitad, y sin una explosión."

## P10
**OO**
- Cuadro 0: Fondo oscuro. Una torre de 40 bloques de madera al centro, ~75 % del alto; una mano saca el bloque de arriba. Contador grande ×1 arriba a la derecha, en ámbar.
- 0–3 s: En 0,3 s la mano levanta el bloque de arriba. En 1,5 s el contador sube a ×100 y la torre se vuelve un rascacielos de 40 pisos, mismo tamaño en cuadro.
- Texto en pantalla: ×1 → ×100
- Voz 0–3 s: "Desarmar una torre es fácil: sacas el de arriba. Ahora hazlo con esta."

**OY**
- Cuadro 0: Fondo azul casi negro. Torre blanca de 40 pisos, centrada, ~75 % del alto. El último piso, en ámbar, intacto. Sobre él, una línea punteada marca la altura original, varios pisos más arriba. Camión con escombros saliendo por la base.
- 0–3 s: En 0,3 s la fachada se hunde un piso bajo el techo ámbar, que no cambia de forma; la punteada queda más lejos. A los 2,5 s el techo se ilumina.
- Texto en pantalla: LO ESTÁN DEMOLIENDO
- Voz 0–3 s: "Demuelen este rascacielos y no le sacan el techo."

## P11
**DR**
- Cuadro 0: Fondo azul casi negro. Torre blanca de 40 pisos, centrada, ~75 % del alto. El último piso, en ámbar, intacto. Sobre él, una línea punteada marca la altura original, varios pisos más arriba. Camión con escombros saliendo por la base.
- 0–3 s: En 0,3 s la fachada se hunde un piso bajo el techo ámbar, que no cambia de forma; la punteada queda más lejos. A los 2,5 s el techo se ilumina.
- Texto en pantalla: LO ESTÁN DEMOLIENDO
- Voz 0–3 s: "Demuelen este rascacielos y no le sacan el techo."

**GJ**
- Cuadro 0: Fondo oscuro, pantalla partida. Izquierda (~45 % del ancho): una torre implosionando en una nube de polvo gris, ✗ rojo. Derecha (~45 %): torre blanca de 40 pisos con el techo ámbar intacto, sin polvo.
- 0–3 s: A la izquierda la torre cae en polvo; a la derecha la torre baja un piso entero, limpia, con el techo igual. A los 2 s la izquierda se apaga y queda la derecha.
- Texto en pantalla: SIN UNA EXPLOSIÓN
- Voz 0–3 s: "Este rascacielos ya perdió la mitad, y sin una explosión."

## P12
**CP**
- Cuadro 0: Fondo azul noche. Rascacielos de 40 pisos al centro, ~80 % del alto, ~35 % del ancho, techo en ámbar. El piso bajo el techo ya se está borrando. Píldora: SIN UNA EXPLOSIÓN.
- 0–3 s: En 0,3 s se borra un piso bajo el techo y el techo baja un escalón; en 1,8 s, otro. En 2,4 s entra una dinamita y se tacha con ✗ rojo.
- Texto en pantalla: SIN UNA EXPLOSIÓN
- Voz 0–3 s: "Tienes que hacer desaparecer este rascacielos. Sin una explosión."

**AJ**
- Cuadro 0: Fondo oscuro, pantalla partida. Izquierda (~45 % del ancho): una torre implosionando en una nube de polvo gris, ✗ rojo. Derecha (~45 %): torre blanca de 40 pisos con el techo ámbar intacto, sin polvo.
- 0–3 s: A la izquierda la torre cae en polvo; a la derecha la torre baja un piso entero, limpia, con el techo igual. A los 2 s la izquierda se apaga y queda la derecha.
- Texto en pantalla: SIN UNA EXPLOSIÓN
- Voz 0–3 s: "Este rascacielos ya perdió la mitad, y sin una explosión."

## P13
**OC**
- Cuadro 0: Fondo oscuro. Rascacielos de 40 pisos al centro, ~80 % del alto; el techo en ámbar. Una grúa chica intenta levantar el techo y aparece un ✗ rojo grande encima. Píldora: NO LE SAQUES EL TECHO.
- 0–3 s: En 0,3 s la grúa levanta un poco el techo; en 1,2 s el ✗ rojo la frena y el techo vuelve a su lugar. En 2,5 s se borra el piso bajo el techo.
- Texto en pantalla: NO LE SAQUES EL TECHO
- Voz 0–3 s: "Para desarmar este rascacielos, nunca le saques el techo."

**QO**
- Cuadro 0: Fondo oscuro. Corte lateral de la punta de una torre blanca, ~70 % del cuadro: el techo ámbar arriba, debajo un piso totalmente vacío y, entre los dos, columnas de acero con gatos hidráulicos sosteniéndolo.
- 0–3 s: Los gatos se encogen y el techo ámbar baja despacio hacia el piso vacío; una viga cae fuera de cuadro. A los 2,5 s la cámara corta a la torre entera: el techo sigue arriba.
- Texto en pantalla: SIN PISO DEBAJO
- Voz 0–3 s: "A este rascacielos le sacaron el piso bajo el techo."

## P14
**IM**
- Cuadro 0: Fondo oscuro. Rascacielos de 40 pisos al centro, ~80 % del alto; el techo en ámbar. Una grúa chica intenta levantar el techo y aparece un ✗ rojo grande encima. Píldora: NO LE SAQUES EL TECHO.
- 0–3 s: En 0,3 s la grúa levanta un poco el techo; en 1,2 s el ✗ rojo la frena y el techo vuelve a su lugar. En 2,5 s se borra el piso bajo el techo.
- Texto en pantalla: NO LE SAQUES EL TECHO
- Voz 0–3 s: "Para desarmar este rascacielos, nunca le saques el techo."

**GG**
- Cuadro 0: Fondo azul noche casi negro. Torre blanca de 40 pisos, fachada en zigzag, centrada, ~75 % del alto y ~30 % del ancho. El último piso, marcado en naranja, ya va bajando: la torre se acorta.
- 0–3 s: La torre pierde pisos de arriba en cámara rápida; el techo naranja baja con ella, entero. A los 2,5 s, píldora chica CÁMARA RÁPIDA en una esquina.
- Texto en pantalla: SE ENCOGE CON EL TECHO
- Voz 0–3 s: "Este rascacielos se está encogiendo. Lo raro no es que no haya explosiones."

## P15
**CS**
- Cuadro 0: Fondo oscuro. Una torre de 40 bloques de madera al centro, ~75 % del alto; una mano saca el bloque de arriba. Contador grande ×1 arriba a la derecha, en ámbar.
- 0–3 s: En 0,3 s la mano levanta el bloque de arriba. En 1,5 s el contador sube a ×100 y la torre se vuelve un rascacielos de 40 pisos, mismo tamaño en cuadro.
- Texto en pantalla: ×1 → ×100
- Voz 0–3 s: "Desarmar una torre es fácil: sacas el de arriba. Ahora hazlo con esta."

**CE**
- Cuadro 0: Fondo oscuro. Rascacielos de 40 pisos al centro, ~80 % del alto; el techo en ámbar. Una grúa chica intenta levantar el techo y aparece un ✗ rojo grande encima. Píldora: NO LE SAQUES EL TECHO.
- 0–3 s: En 0,3 s la grúa levanta un poco el techo; en 1,2 s el ✗ rojo la frena y el techo vuelve a su lugar. En 2,5 s se borra el piso bajo el techo.
- Texto en pantalla: NO LE SAQUES EL TECHO
- Voz 0–3 s: "Para desarmar este rascacielos, nunca le saques el techo."

## P16
**XQ**
- Cuadro 0: Fondo azul noche casi negro. Torre blanca de 40 pisos, fachada en zigzag, centrada, ~75 % del alto y ~30 % del ancho. El último piso, marcado en naranja, ya va bajando: la torre se acorta.
- 0–3 s: La torre pierde pisos de arriba en cámara rápida; el techo naranja baja con ella, entero. A los 2,5 s, píldora chica CÁMARA RÁPIDA en una esquina.
- Texto en pantalla: SE ENCOGE CON EL TECHO
- Voz 0–3 s: "Este rascacielos se está encogiendo. Lo raro no es que no haya explosiones."

**IL**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos centrada, ~75 % del alto; al lado, un calendario naranja (~15 % del cuadro) pasa hojas; con cada hoja la torre baja dos pisos, techo naranja entero.
- 0–3 s: El calendario pasa diez hojas en 1 s y la torre se acorta dos pisos; se repite una vez. Píldora chica CÁMARA RÁPIDA en una esquina desde los 2,5 s.
- Texto en pantalla: −2 PISOS CADA 10 DÍAS
- Voz 0–3 s: "Este rascacielos pierde dos pisos cada diez días."

## P17
**ET**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos centrada, ~75 % del alto. A su pie, un cartucho de dinamita rojo tachado con una X naranja; la torre ya empieza a acortarse desde arriba.
- 0–3 s: La X tacha la dinamita en 0,3 s; la torre se acorta en cámara rápida con el techo naranja bajando entero. Píldora chica CÁMARA RÁPIDA en una esquina desde los 2,5 s.
- Texto en pantalla: SIN DINAMITA
- Voz 0–3 s: "A este rascacielos no lo dinamitaron. Lo encogieron."

**UQ**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos centrada, ~75 % del alto; al lado, un calendario naranja (~15 % del cuadro) pasa hojas; con cada hoja la torre baja dos pisos, techo naranja entero.
- 0–3 s: El calendario pasa diez hojas en 1 s y la torre se acorta dos pisos; se repite una vez. Píldora chica CÁMARA RÁPIDA en una esquina desde los 2,5 s.
- Texto en pantalla: −2 PISOS CADA 10 DÍAS
- Voz 0–3 s: "Este rascacielos pierde dos pisos cada diez días."

## P18
**ID**
- Cuadro 0: Fondo oscuro. Torre blanca de 40 pisos, centrada, ~75 % del alto, techo ámbar. Una franja vertical de la fachada está cortada: adentro, el piso bajo el techo está vacío, sólo columnas. Afuera, la fachada se ve entera.
- 0–3 s: Una franja de corte baja por la torre: por fuera, entera; por dentro, el piso bajo el techo vacío y un obrero con casco sacando una viga. En 1,5 s la torre baja un piso.
- Texto en pantalla: POR FUERA, ENTERO
- Voz 0–3 s: "Este rascacielos se achica y casi nadie lo nota."

**WL**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos, ~75 % del alto. Los 2 pisos de arriba en corte: adentro, una grúa naranja levanta una viga del piso; afuera, paneles con ventanas tapan todo.
- 0–3 s: La viga sube en 0,4 s; el corte se cierra y la torre se ve entera e igual; vuelve a abrirse y falta un piso. Una sola píldora.
- Texto en pantalla: LO DESARMAN A ESCONDIDAS
- Voz 0–3 s: "A este rascacielos lo desarman a escondidas. Por arriba."

## P19
**HP**
- Cuadro 0: Fondo oscuro. Torre blanca de 40 pisos, centrada, ~75 % del alto, techo ámbar. Una franja vertical de la fachada está cortada: adentro, el piso bajo el techo está vacío, sólo columnas. Afuera, la fachada se ve entera.
- 0–3 s: Una franja de corte baja por la torre: por fuera, entera; por dentro, el piso bajo el techo vacío y un obrero con casco sacando una viga. En 1,5 s la torre baja un piso.
- Texto en pantalla: POR FUERA, ENTERO
- Voz 0–3 s: "Este rascacielos se achica y casi nadie lo nota."

**PM**
- Cuadro 0: Fondo oscuro. Corte lateral de la punta de una torre blanca, ~70 % del cuadro: el techo ámbar arriba, debajo un piso totalmente vacío y, entre los dos, columnas de acero con gatos hidráulicos sosteniéndolo.
- 0–3 s: Los gatos se encogen y el techo ámbar baja despacio hacia el piso vacío; una viga cae fuera de cuadro. A los 2,5 s la cámara corta a la torre entera: el techo sigue arriba.
- Texto en pantalla: SIN PISO DEBAJO
- Voz 0–3 s: "A este rascacielos le sacaron el piso bajo el techo."

## P20
**AF**
- Cuadro 0: Fondo oscuro. Una torre de 40 bloques de madera al centro, ~75 % del alto; una mano saca el bloque de arriba. Contador grande ×1 arriba a la derecha, en ámbar.
- 0–3 s: En 0,3 s la mano levanta el bloque de arriba. En 1,5 s el contador sube a ×100 y la torre se vuelve un rascacielos de 40 pisos, mismo tamaño en cuadro.
- Texto en pantalla: ×1 → ×100
- Voz 0–3 s: "Desarmar una torre es fácil: sacas el de arriba. Ahora hazlo con esta."

**AP**
- Cuadro 0: Fondo oscuro. Corte lateral de la punta de una torre blanca, ~70 % del cuadro: el techo ámbar arriba, debajo un piso totalmente vacío y, entre los dos, columnas de acero con gatos hidráulicos sosteniéndolo.
- 0–3 s: Los gatos se encogen y el techo ámbar baja despacio hacia el piso vacío; una viga cae fuera de cuadro. A los 2,5 s la cámara corta a la torre entera: el techo sigue arriba.
- Texto en pantalla: SIN PISO DEBAJO
- Voz 0–3 s: "A este rascacielos le sacaron el piso bajo el techo."

## P21
**VO**
- Cuadro 0: Fondo azul casi negro. Torre blanca de 40 pisos, centrada, ~75 % del alto. El último piso, en ámbar, intacto. Sobre él, una línea punteada marca la altura original, varios pisos más arriba. Camión con escombros saliendo por la base.
- 0–3 s: En 0,3 s la fachada se hunde un piso bajo el techo ámbar, que no cambia de forma; la punteada queda más lejos. A los 2,5 s el techo se ilumina.
- Texto en pantalla: LO ESTÁN DEMOLIENDO
- Voz 0–3 s: "Demuelen este rascacielos y no le sacan el techo."

**MJ**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos centrada, ~75 % del alto. A su pie, un cartucho de dinamita rojo tachado con una X naranja; la torre ya empieza a acortarse desde arriba.
- 0–3 s: La X tacha la dinamita en 0,3 s; la torre se acorta en cámara rápida con el techo naranja bajando entero. Píldora chica CÁMARA RÁPIDA en una esquina desde los 2,5 s.
- Texto en pantalla: SIN DINAMITA
- Voz 0–3 s: "A este rascacielos no lo dinamitaron. Lo encogieron."

## P22
**XE**
- Cuadro 0: Fondo oscuro. Corte lateral de la punta de una torre blanca, ~70 % del cuadro: el techo ámbar arriba, debajo un piso totalmente vacío y, entre los dos, columnas de acero con gatos hidráulicos sosteniéndolo.
- 0–3 s: Los gatos se encogen y el techo ámbar baja despacio hacia el piso vacío; una viga cae fuera de cuadro. A los 2,5 s la cámara corta a la torre entera: el techo sigue arriba.
- Texto en pantalla: SIN PISO DEBAJO
- Voz 0–3 s: "A este rascacielos le sacaron el piso bajo el techo."

**NL**
- Cuadro 0: Fondo azul noche casi negro. Torre blanca de 40 pisos, fachada en zigzag, centrada, ~75 % del alto y ~30 % del ancho. El último piso, marcado en naranja, ya va bajando: la torre se acorta.
- 0–3 s: La torre pierde pisos de arriba en cámara rápida; el techo naranja baja con ella, entero. A los 2,5 s, píldora chica CÁMARA RÁPIDA en una esquina.
- Texto en pantalla: SE ENCOGE CON EL TECHO
- Voz 0–3 s: "Este rascacielos se está encogiendo. Lo raro no es que no haya explosiones."

## P23
**MK**
- Cuadro 0: Fondo oscuro. Rascacielos de 40 pisos al centro, ~80 % del alto; el techo en ámbar. Una grúa chica intenta levantar el techo y aparece un ✗ rojo grande encima. Píldora: NO LE SAQUES EL TECHO.
- 0–3 s: En 0,3 s la grúa levanta un poco el techo; en 1,2 s el ✗ rojo la frena y el techo vuelve a su lugar. En 2,5 s se borra el piso bajo el techo.
- Texto en pantalla: NO LE SAQUES EL TECHO
- Voz 0–3 s: "Para desarmar este rascacielos, nunca le saques el techo."

**DK**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos centrada, ~75 % del alto; al lado, un calendario naranja (~15 % del cuadro) pasa hojas; con cada hoja la torre baja dos pisos, techo naranja entero.
- 0–3 s: El calendario pasa diez hojas en 1 s y la torre se acorta dos pisos; se repite una vez. Píldora chica CÁMARA RÁPIDA en una esquina desde los 2,5 s.
- Texto en pantalla: −2 PISOS CADA 10 DÍAS
- Voz 0–3 s: "Este rascacielos pierde dos pisos cada diez días."

## P24
**AK**
- Cuadro 0: Fondo oscuro, pantalla partida. Izquierda (~45 % del ancho): una torre implosionando en una nube de polvo gris, ✗ rojo. Derecha (~45 %): torre blanca de 40 pisos con el techo ámbar intacto, sin polvo.
- 0–3 s: A la izquierda la torre cae en polvo; a la derecha la torre baja un piso entero, limpia, con el techo igual. A los 2 s la izquierda se apaga y queda la derecha.
- Texto en pantalla: SIN UNA EXPLOSIÓN
- Voz 0–3 s: "Este rascacielos ya perdió la mitad, y sin una explosión."

**YK**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos, ~75 % del alto. Los 2 pisos de arriba en corte: adentro, una grúa naranja levanta una viga del piso; afuera, paneles con ventanas tapan todo.
- 0–3 s: La viga sube en 0,4 s; el corte se cierra y la torre se ve entera e igual; vuelve a abrirse y falta un piso. Una sola píldora.
- Texto en pantalla: LO DESARMAN A ESCONDIDAS
- Voz 0–3 s: "A este rascacielos lo desarman a escondidas. Por arriba."

## P25
**MD**
- Cuadro 0: Fondo oscuro. Una torre de 40 bloques de madera al centro, ~75 % del alto; una mano saca el bloque de arriba. Contador grande ×1 arriba a la derecha, en ámbar.
- 0–3 s: En 0,3 s la mano levanta el bloque de arriba. En 1,5 s el contador sube a ×100 y la torre se vuelve un rascacielos de 40 pisos, mismo tamaño en cuadro.
- Texto en pantalla: ×1 → ×100
- Voz 0–3 s: "Desarmar una torre es fácil: sacas el de arriba. Ahora hazlo con esta."

**GW**
- Cuadro 0: Fondo oscuro. Torre blanca de 40 pisos, centrada, ~75 % del alto, techo ámbar. Una franja vertical de la fachada está cortada: adentro, el piso bajo el techo está vacío, sólo columnas. Afuera, la fachada se ve entera.
- 0–3 s: Una franja de corte baja por la torre: por fuera, entera; por dentro, el piso bajo el techo vacío y un obrero con casco sacando una viga. En 1,5 s la torre baja un piso.
- Texto en pantalla: POR FUERA, ENTERO
- Voz 0–3 s: "Este rascacielos se achica y casi nadie lo nota."

## P26
**AX**
- Cuadro 0: Fondo azul noche. Rascacielos de 40 pisos al centro, ~80 % del alto, ~35 % del ancho, techo en ámbar. El piso bajo el techo ya se está borrando. Píldora: SIN UNA EXPLOSIÓN.
- 0–3 s: En 0,3 s se borra un piso bajo el techo y el techo baja un escalón; en 1,8 s, otro. En 2,4 s entra una dinamita y se tacha con ✗ rojo.
- Texto en pantalla: SIN UNA EXPLOSIÓN
- Voz 0–3 s: "Tienes que hacer desaparecer este rascacielos. Sin una explosión."

**JI**
- Cuadro 0: Fondo azul noche casi negro. Torre blanca de 40 pisos, fachada en zigzag, centrada, ~75 % del alto y ~30 % del ancho. El último piso, marcado en naranja, ya va bajando: la torre se acorta.
- 0–3 s: La torre pierde pisos de arriba en cámara rápida; el techo naranja baja con ella, entero. A los 2,5 s, píldora chica CÁMARA RÁPIDA en una esquina.
- Texto en pantalla: SE ENCOGE CON EL TECHO
- Voz 0–3 s: "Este rascacielos se está encogiendo. Lo raro no es que no haya explosiones."

## P27
**LC**
- Cuadro 0: Fondo oscuro. Rascacielos de 40 pisos al centro, ~80 % del alto; el techo en ámbar. Una grúa chica intenta levantar el techo y aparece un ✗ rojo grande encima. Píldora: NO LE SAQUES EL TECHO.
- 0–3 s: En 0,3 s la grúa levanta un poco el techo; en 1,2 s el ✗ rojo la frena y el techo vuelve a su lugar. En 2,5 s se borra el piso bajo el techo.
- Texto en pantalla: NO LE SAQUES EL TECHO
- Voz 0–3 s: "Para desarmar este rascacielos, nunca le saques el techo."

**MM**
- Cuadro 0: Fondo oscuro. Rascacielos de 40 pisos al centro, ~80 % del alto, con edificios vecinos pegados a los lados (~15 % cada uno). Cartuchos de dinamita en la base, tachados con ✗ rojo. Píldora: SIN RUIDO. SIN POLVO.
- 0–3 s: En 0,2 s caen cartuchos de dinamita junto a la base; en 0,8 s se tachan con ✗ rojo. En 1,8 s el techo ámbar baja un piso y la torre queda más corta.
- Texto en pantalla: SIN RUIDO. SIN POLVO.
- Voz 0–3 s: "Dinamita no. Este rascacielos tiene que desaparecer sin hacer ruido."

## P28
**SC**
- Cuadro 0: Fondo oscuro. Una torre de 40 bloques de madera al centro, ~75 % del alto; una mano saca el bloque de arriba. Contador grande ×1 arriba a la derecha, en ámbar.
- 0–3 s: En 0,3 s la mano levanta el bloque de arriba. En 1,5 s el contador sube a ×100 y la torre se vuelve un rascacielos de 40 pisos, mismo tamaño en cuadro.
- Texto en pantalla: ×1 → ×100
- Voz 0–3 s: "Desarmar una torre es fácil: sacas el de arriba. Ahora hazlo con esta."

**LN**
- Cuadro 0: Fondo azul noche casi negro. Torre blanca de 40 pisos, fachada en zigzag, centrada, ~75 % del alto y ~30 % del ancho. El último piso, marcado en naranja, ya va bajando: la torre se acorta.
- 0–3 s: La torre pierde pisos de arriba en cámara rápida; el techo naranja baja con ella, entero. A los 2,5 s, píldora chica CÁMARA RÁPIDA en una esquina.
- Texto en pantalla: SE ENCOGE CON EL TECHO
- Voz 0–3 s: "Este rascacielos se está encogiendo. Lo raro no es que no haya explosiones."

## P29
**YI**
- Cuadro 0: Fondo oscuro. Rascacielos de 40 pisos al centro, ~80 % del alto, con edificios vecinos pegados a los lados (~15 % cada uno). Cartuchos de dinamita en la base, tachados con ✗ rojo. Píldora: SIN RUIDO. SIN POLVO.
- 0–3 s: En 0,2 s caen cartuchos de dinamita junto a la base; en 0,8 s se tachan con ✗ rojo. En 1,8 s el techo ámbar baja un piso y la torre queda más corta.
- Texto en pantalla: SIN RUIDO. SIN POLVO.
- Voz 0–3 s: "Dinamita no. Este rascacielos tiene que desaparecer sin hacer ruido."

**BI**
- Cuadro 0: Fondo azul casi negro. Torre blanca de 40 pisos, centrada, ~75 % del alto. El último piso, en ámbar, intacto. Sobre él, una línea punteada marca la altura original, varios pisos más arriba. Camión con escombros saliendo por la base.
- 0–3 s: En 0,3 s la fachada se hunde un piso bajo el techo ámbar, que no cambia de forma; la punteada queda más lejos. A los 2,5 s el techo se ilumina.
- Texto en pantalla: LO ESTÁN DEMOLIENDO
- Voz 0–3 s: "Demuelen este rascacielos y no le sacan el techo."

## P30
**DB**
- Cuadro 0: Fondo azul noche. Rascacielos de 40 pisos al centro, ~80 % del alto, ~35 % del ancho, techo en ámbar. El piso bajo el techo ya se está borrando. Píldora: SIN UNA EXPLOSIÓN.
- 0–3 s: En 0,3 s se borra un piso bajo el techo y el techo baja un escalón; en 1,8 s, otro. En 2,4 s entra una dinamita y se tacha con ✗ rojo.
- Texto en pantalla: SIN UNA EXPLOSIÓN
- Voz 0–3 s: "Tienes que hacer desaparecer este rascacielos. Sin una explosión."

**VJ**
- Cuadro 0: Fondo oscuro. Una torre de 40 bloques de madera al centro, ~75 % del alto; una mano saca el bloque de arriba. Contador grande ×1 arriba a la derecha, en ámbar.
- 0–3 s: En 0,3 s la mano levanta el bloque de arriba. En 1,5 s el contador sube a ×100 y la torre se vuelve un rascacielos de 40 pisos, mismo tamaño en cuadro.
- Texto en pantalla: ×1 → ×100
- Voz 0–3 s: "Desarmar una torre es fácil: sacas el de arriba. Ahora hazlo con esta."

## P31
**UE**
- Cuadro 0: Fondo oscuro. Una torre de 40 bloques de madera al centro, ~75 % del alto; una mano saca el bloque de arriba. Contador grande ×1 arriba a la derecha, en ámbar.
- 0–3 s: En 0,3 s la mano levanta el bloque de arriba. En 1,5 s el contador sube a ×100 y la torre se vuelve un rascacielos de 40 pisos, mismo tamaño en cuadro.
- Texto en pantalla: ×1 → ×100
- Voz 0–3 s: "Desarmar una torre es fácil: sacas el de arriba. Ahora hazlo con esta."

**HI**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos centrada, ~75 % del alto; al lado, un calendario naranja (~15 % del cuadro) pasa hojas; con cada hoja la torre baja dos pisos, techo naranja entero.
- 0–3 s: El calendario pasa diez hojas en 1 s y la torre se acorta dos pisos; se repite una vez. Píldora chica CÁMARA RÁPIDA en una esquina desde los 2,5 s.
- Texto en pantalla: −2 PISOS CADA 10 DÍAS
- Voz 0–3 s: "Este rascacielos pierde dos pisos cada diez días."

## P32
**NQ**
- Cuadro 0: Fondo azul noche. Rascacielos de 40 pisos al centro, ~80 % del alto, ~35 % del ancho, techo en ámbar. El piso bajo el techo ya se está borrando. Píldora: SIN UNA EXPLOSIÓN.
- 0–3 s: En 0,3 s se borra un piso bajo el techo y el techo baja un escalón; en 1,8 s, otro. En 2,4 s entra una dinamita y se tacha con ✗ rojo.
- Texto en pantalla: SIN UNA EXPLOSIÓN
- Voz 0–3 s: "Tienes que hacer desaparecer este rascacielos. Sin una explosión."

**KG**
- Cuadro 0: Fondo azul casi negro. Torre blanca de 40 pisos, centrada, ~75 % del alto. El último piso, en ámbar, intacto. Sobre él, una línea punteada marca la altura original, varios pisos más arriba. Camión con escombros saliendo por la base.
- 0–3 s: En 0,3 s la fachada se hunde un piso bajo el techo ámbar, que no cambia de forma; la punteada queda más lejos. A los 2,5 s el techo se ilumina.
- Texto en pantalla: LO ESTÁN DEMOLIENDO
- Voz 0–3 s: "Demuelen este rascacielos y no le sacan el techo."

## P33
**YL**
- Cuadro 0: Fondo oscuro. Rascacielos de 40 pisos al centro, ~80 % del alto; el techo en ámbar. Una grúa chica intenta levantar el techo y aparece un ✗ rojo grande encima. Píldora: NO LE SAQUES EL TECHO.
- 0–3 s: En 0,3 s la grúa levanta un poco el techo; en 1,2 s el ✗ rojo la frena y el techo vuelve a su lugar. En 2,5 s se borra el piso bajo el techo.
- Texto en pantalla: NO LE SAQUES EL TECHO
- Voz 0–3 s: "Para desarmar este rascacielos, nunca le saques el techo."

**ZN**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos, ~75 % del alto. Los 2 pisos de arriba en corte: adentro, una grúa naranja levanta una viga del piso; afuera, paneles con ventanas tapan todo.
- 0–3 s: La viga sube en 0,4 s; el corte se cierra y la torre se ve entera e igual; vuelve a abrirse y falta un piso. Una sola píldora.
- Texto en pantalla: LO DESARMAN A ESCONDIDAS
- Voz 0–3 s: "A este rascacielos lo desarman a escondidas. Por arriba."

## P34
**AZ**
- Cuadro 0: Fondo oscuro. Rascacielos de 40 pisos al centro, ~80 % del alto; el techo en ámbar. Una grúa chica intenta levantar el techo y aparece un ✗ rojo grande encima. Píldora: NO LE SAQUES EL TECHO.
- 0–3 s: En 0,3 s la grúa levanta un poco el techo; en 1,2 s el ✗ rojo la frena y el techo vuelve a su lugar. En 2,5 s se borra el piso bajo el techo.
- Texto en pantalla: NO LE SAQUES EL TECHO
- Voz 0–3 s: "Para desarmar este rascacielos, nunca le saques el techo."

**YU**
- Cuadro 0: Fondo oscuro. Torre blanca de 40 pisos, centrada, ~75 % del alto, techo ámbar. Una franja vertical de la fachada está cortada: adentro, el piso bajo el techo está vacío, sólo columnas. Afuera, la fachada se ve entera.
- 0–3 s: Una franja de corte baja por la torre: por fuera, entera; por dentro, el piso bajo el techo vacío y un obrero con casco sacando una viga. En 1,5 s la torre baja un piso.
- Texto en pantalla: POR FUERA, ENTERO
- Voz 0–3 s: "Este rascacielos se achica y casi nadie lo nota."

## P35
**MR**
- Cuadro 0: Fondo azul noche. Rascacielos de 40 pisos al centro, ~80 % del alto, ~35 % del ancho, techo en ámbar. El piso bajo el techo ya se está borrando. Píldora: SIN UNA EXPLOSIÓN.
- 0–3 s: En 0,3 s se borra un piso bajo el techo y el techo baja un escalón; en 1,8 s, otro. En 2,4 s entra una dinamita y se tacha con ✗ rojo.
- Texto en pantalla: SIN UNA EXPLOSIÓN
- Voz 0–3 s: "Tienes que hacer desaparecer este rascacielos. Sin una explosión."

**RG**
- Cuadro 0: Fondo oscuro. Corte lateral de la punta de una torre blanca, ~70 % del cuadro: el techo ámbar arriba, debajo un piso totalmente vacío y, entre los dos, columnas de acero con gatos hidráulicos sosteniéndolo.
- 0–3 s: Los gatos se encogen y el techo ámbar baja despacio hacia el piso vacío; una viga cae fuera de cuadro. A los 2,5 s la cámara corta a la torre entera: el techo sigue arriba.
- Texto en pantalla: SIN PISO DEBAJO
- Voz 0–3 s: "A este rascacielos le sacaron el piso bajo el techo."

## P36
**XC**
- Cuadro 0: Fondo oscuro. Rascacielos de 40 pisos al centro, ~80 % del alto; el techo en ámbar. Una grúa chica intenta levantar el techo y aparece un ✗ rojo grande encima. Píldora: NO LE SAQUES EL TECHO.
- 0–3 s: En 0,3 s la grúa levanta un poco el techo; en 1,2 s el ✗ rojo la frena y el techo vuelve a su lugar. En 2,5 s se borra el piso bajo el techo.
- Texto en pantalla: NO LE SAQUES EL TECHO
- Voz 0–3 s: "Para desarmar este rascacielos, nunca le saques el techo."

**BX**
- Cuadro 0: Fondo oscuro, pantalla partida. Izquierda (~45 % del ancho): una torre implosionando en una nube de polvo gris, ✗ rojo. Derecha (~45 %): torre blanca de 40 pisos con el techo ámbar intacto, sin polvo.
- 0–3 s: A la izquierda la torre cae en polvo; a la derecha la torre baja un piso entero, limpia, con el techo igual. A los 2 s la izquierda se apaga y queda la derecha.
- Texto en pantalla: SIN UNA EXPLOSIÓN
- Voz 0–3 s: "Este rascacielos ya perdió la mitad, y sin una explosión."

## P37
**NO**
- Cuadro 0: Fondo oscuro, pantalla partida. Izquierda (~45 % del ancho): una torre implosionando en una nube de polvo gris, ✗ rojo. Derecha (~45 %): torre blanca de 40 pisos con el techo ámbar intacto, sin polvo.
- 0–3 s: A la izquierda la torre cae en polvo; a la derecha la torre baja un piso entero, limpia, con el techo igual. A los 2 s la izquierda se apaga y queda la derecha.
- Texto en pantalla: SIN UNA EXPLOSIÓN
- Voz 0–3 s: "Este rascacielos ya perdió la mitad, y sin una explosión."

**TY**
- Cuadro 0: Fondo azul noche casi negro. Torre blanca de 40 pisos, fachada en zigzag, centrada, ~75 % del alto y ~30 % del ancho. El último piso, marcado en naranja, ya va bajando: la torre se acorta.
- 0–3 s: La torre pierde pisos de arriba en cámara rápida; el techo naranja baja con ella, entero. A los 2,5 s, píldora chica CÁMARA RÁPIDA en una esquina.
- Texto en pantalla: SE ENCOGE CON EL TECHO
- Voz 0–3 s: "Este rascacielos se está encogiendo. Lo raro no es que no haya explosiones."

## P38
**EU**
- Cuadro 0: Fondo oscuro. Corte lateral de la punta de una torre blanca, ~70 % del cuadro: el techo ámbar arriba, debajo un piso totalmente vacío y, entre los dos, columnas de acero con gatos hidráulicos sosteniéndolo.
- 0–3 s: Los gatos se encogen y el techo ámbar baja despacio hacia el piso vacío; una viga cae fuera de cuadro. A los 2,5 s la cámara corta a la torre entera: el techo sigue arriba.
- Texto en pantalla: SIN PISO DEBAJO
- Voz 0–3 s: "A este rascacielos le sacaron el piso bajo el techo."

**JP**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos centrada, ~75 % del alto. A su pie, un cartucho de dinamita rojo tachado con una X naranja; la torre ya empieza a acortarse desde arriba.
- 0–3 s: La X tacha la dinamita en 0,3 s; la torre se acorta en cámara rápida con el techo naranja bajando entero. Píldora chica CÁMARA RÁPIDA en una esquina desde los 2,5 s.
- Texto en pantalla: SIN DINAMITA
- Voz 0–3 s: "A este rascacielos no lo dinamitaron. Lo encogieron."

## P39
**BR**
- Cuadro 0: Fondo azul casi negro. Torre blanca de 40 pisos, centrada, ~75 % del alto. El último piso, en ámbar, intacto. Sobre él, una línea punteada marca la altura original, varios pisos más arriba. Camión con escombros saliendo por la base.
- 0–3 s: En 0,3 s la fachada se hunde un piso bajo el techo ámbar, que no cambia de forma; la punteada queda más lejos. A los 2,5 s el techo se ilumina.
- Texto en pantalla: LO ESTÁN DEMOLIENDO
- Voz 0–3 s: "Demuelen este rascacielos y no le sacan el techo."

**EF**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos, ~75 % del alto. Los 2 pisos de arriba en corte: adentro, una grúa naranja levanta una viga del piso; afuera, paneles con ventanas tapan todo.
- 0–3 s: La viga sube en 0,4 s; el corte se cierra y la torre se ve entera e igual; vuelve a abrirse y falta un piso. Una sola píldora.
- Texto en pantalla: LO DESARMAN A ESCONDIDAS
- Voz 0–3 s: "A este rascacielos lo desarman a escondidas. Por arriba."

## P40
**PN**
- Cuadro 0: Fondo azul noche. Rascacielos de 40 pisos al centro, ~80 % del alto, ~35 % del ancho, techo en ámbar. El piso bajo el techo ya se está borrando. Píldora: SIN UNA EXPLOSIÓN.
- 0–3 s: En 0,3 s se borra un piso bajo el techo y el techo baja un escalón; en 1,8 s, otro. En 2,4 s entra una dinamita y se tacha con ✗ rojo.
- Texto en pantalla: SIN UNA EXPLOSIÓN
- Voz 0–3 s: "Tienes que hacer desaparecer este rascacielos. Sin una explosión."

**KJ**
- Cuadro 0: Fondo oscuro. Torre blanca de 40 pisos, centrada, ~75 % del alto, techo ámbar. Una franja vertical de la fachada está cortada: adentro, el piso bajo el techo está vacío, sólo columnas. Afuera, la fachada se ve entera.
- 0–3 s: Una franja de corte baja por la torre: por fuera, entera; por dentro, el piso bajo el techo vacío y un obrero con casco sacando una viga. En 1,5 s la torre baja un piso.
- Texto en pantalla: POR FUERA, ENTERO
- Voz 0–3 s: "Este rascacielos se achica y casi nadie lo nota."

## P41
**XX**
- Cuadro 0: Fondo oscuro. Una torre de 40 bloques de madera al centro, ~75 % del alto; una mano saca el bloque de arriba. Contador grande ×1 arriba a la derecha, en ámbar.
- 0–3 s: En 0,3 s la mano levanta el bloque de arriba. En 1,5 s el contador sube a ×100 y la torre se vuelve un rascacielos de 40 pisos, mismo tamaño en cuadro.
- Texto en pantalla: ×1 → ×100
- Voz 0–3 s: "Desarmar una torre es fácil: sacas el de arriba. Ahora hazlo con esta."

**UI**
- Cuadro 0: Fondo oscuro, pantalla partida. Izquierda (~45 % del ancho): una torre implosionando en una nube de polvo gris, ✗ rojo. Derecha (~45 %): torre blanca de 40 pisos con el techo ámbar intacto, sin polvo.
- 0–3 s: A la izquierda la torre cae en polvo; a la derecha la torre baja un piso entero, limpia, con el techo igual. A los 2 s la izquierda se apaga y queda la derecha.
- Texto en pantalla: SIN UNA EXPLOSIÓN
- Voz 0–3 s: "Este rascacielos ya perdió la mitad, y sin una explosión."

## P42
**MU**
- Cuadro 0: Fondo oscuro. Corte lateral de la punta de una torre blanca, ~70 % del cuadro: el techo ámbar arriba, debajo un piso totalmente vacío y, entre los dos, columnas de acero con gatos hidráulicos sosteniéndolo.
- 0–3 s: Los gatos se encogen y el techo ámbar baja despacio hacia el piso vacío; una viga cae fuera de cuadro. A los 2,5 s la cámara corta a la torre entera: el techo sigue arriba.
- Texto en pantalla: SIN PISO DEBAJO
- Voz 0–3 s: "A este rascacielos le sacaron el piso bajo el techo."

**HJ**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos centrada, ~75 % del alto; al lado, un calendario naranja (~15 % del cuadro) pasa hojas; con cada hoja la torre baja dos pisos, techo naranja entero.
- 0–3 s: El calendario pasa diez hojas en 1 s y la torre se acorta dos pisos; se repite una vez. Píldora chica CÁMARA RÁPIDA en una esquina desde los 2,5 s.
- Texto en pantalla: −2 PISOS CADA 10 DÍAS
- Voz 0–3 s: "Este rascacielos pierde dos pisos cada diez días."

## P43
**PR**
- Cuadro 0: Fondo oscuro. Rascacielos de 40 pisos al centro, ~80 % del alto, con edificios vecinos pegados a los lados (~15 % cada uno). Cartuchos de dinamita en la base, tachados con ✗ rojo. Píldora: SIN RUIDO. SIN POLVO.
- 0–3 s: En 0,2 s caen cartuchos de dinamita junto a la base; en 0,8 s se tachan con ✗ rojo. En 1,8 s el techo ámbar baja un piso y la torre queda más corta.
- Texto en pantalla: SIN RUIDO. SIN POLVO.
- Voz 0–3 s: "Dinamita no. Este rascacielos tiene que desaparecer sin hacer ruido."

**VM**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos centrada, ~75 % del alto; al lado, un calendario naranja (~15 % del cuadro) pasa hojas; con cada hoja la torre baja dos pisos, techo naranja entero.
- 0–3 s: El calendario pasa diez hojas en 1 s y la torre se acorta dos pisos; se repite una vez. Píldora chica CÁMARA RÁPIDA en una esquina desde los 2,5 s.
- Texto en pantalla: −2 PISOS CADA 10 DÍAS
- Voz 0–3 s: "Este rascacielos pierde dos pisos cada diez días."

## P44
**DF**
- Cuadro 0: Fondo azul noche. Rascacielos de 40 pisos al centro, ~80 % del alto, ~35 % del ancho, techo en ámbar. El piso bajo el techo ya se está borrando. Píldora: SIN UNA EXPLOSIÓN.
- 0–3 s: En 0,3 s se borra un piso bajo el techo y el techo baja un escalón; en 1,8 s, otro. En 2,4 s entra una dinamita y se tacha con ✗ rojo.
- Texto en pantalla: SIN UNA EXPLOSIÓN
- Voz 0–3 s: "Tienes que hacer desaparecer este rascacielos. Sin una explosión."

**UF**
- Cuadro 0: Fondo oscuro. Rascacielos de 40 pisos al centro, ~80 % del alto; el techo en ámbar. Una grúa chica intenta levantar el techo y aparece un ✗ rojo grande encima. Píldora: NO LE SAQUES EL TECHO.
- 0–3 s: En 0,3 s la grúa levanta un poco el techo; en 1,2 s el ✗ rojo la frena y el techo vuelve a su lugar. En 2,5 s se borra el piso bajo el techo.
- Texto en pantalla: NO LE SAQUES EL TECHO
- Voz 0–3 s: "Para desarmar este rascacielos, nunca le saques el techo."

## P45
**CG**
- Cuadro 0: Fondo oscuro. Rascacielos de 40 pisos al centro, ~80 % del alto, con edificios vecinos pegados a los lados (~15 % cada uno). Cartuchos de dinamita en la base, tachados con ✗ rojo. Píldora: SIN RUIDO. SIN POLVO.
- 0–3 s: En 0,2 s caen cartuchos de dinamita junto a la base; en 0,8 s se tachan con ✗ rojo. En 1,8 s el techo ámbar baja un piso y la torre queda más corta.
- Texto en pantalla: SIN RUIDO. SIN POLVO.
- Voz 0–3 s: "Dinamita no. Este rascacielos tiene que desaparecer sin hacer ruido."

**QZ**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos, ~75 % del alto. Los 2 pisos de arriba en corte: adentro, una grúa naranja levanta una viga del piso; afuera, paneles con ventanas tapan todo.
- 0–3 s: La viga sube en 0,4 s; el corte se cierra y la torre se ve entera e igual; vuelve a abrirse y falta un piso. Una sola píldora.
- Texto en pantalla: LO DESARMAN A ESCONDIDAS
- Voz 0–3 s: "A este rascacielos lo desarman a escondidas. Por arriba."

## P46
**HO**
- Cuadro 0: Fondo oscuro, pantalla partida. Izquierda (~45 % del ancho): una torre implosionando en una nube de polvo gris, ✗ rojo. Derecha (~45 %): torre blanca de 40 pisos con el techo ámbar intacto, sin polvo.
- 0–3 s: A la izquierda la torre cae en polvo; a la derecha la torre baja un piso entero, limpia, con el techo igual. A los 2 s la izquierda se apaga y queda la derecha.
- Texto en pantalla: SIN UNA EXPLOSIÓN
- Voz 0–3 s: "Este rascacielos ya perdió la mitad, y sin una explosión."

**KY**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos centrada, ~75 % del alto. A su pie, un cartucho de dinamita rojo tachado con una X naranja; la torre ya empieza a acortarse desde arriba.
- 0–3 s: La X tacha la dinamita en 0,3 s; la torre se acorta en cámara rápida con el techo naranja bajando entero. Píldora chica CÁMARA RÁPIDA en una esquina desde los 2,5 s.
- Texto en pantalla: SIN DINAMITA
- Voz 0–3 s: "A este rascacielos no lo dinamitaron. Lo encogieron."

## P47
**ON**
- Cuadro 0: Fondo oscuro. Rascacielos de 40 pisos al centro, ~80 % del alto, con edificios vecinos pegados a los lados (~15 % cada uno). Cartuchos de dinamita en la base, tachados con ✗ rojo. Píldora: SIN RUIDO. SIN POLVO.
- 0–3 s: En 0,2 s caen cartuchos de dinamita junto a la base; en 0,8 s se tachan con ✗ rojo. En 1,8 s el techo ámbar baja un piso y la torre queda más corta.
- Texto en pantalla: SIN RUIDO. SIN POLVO.
- Voz 0–3 s: "Dinamita no. Este rascacielos tiene que desaparecer sin hacer ruido."

**ER**
- Cuadro 0: Fondo oscuro. Corte lateral de la punta de una torre blanca, ~70 % del cuadro: el techo ámbar arriba, debajo un piso totalmente vacío y, entre los dos, columnas de acero con gatos hidráulicos sosteniéndolo.
- 0–3 s: Los gatos se encogen y el techo ámbar baja despacio hacia el piso vacío; una viga cae fuera de cuadro. A los 2,5 s la cámara corta a la torre entera: el techo sigue arriba.
- Texto en pantalla: SIN PISO DEBAJO
- Voz 0–3 s: "A este rascacielos le sacaron el piso bajo el techo."

## P48
**GH**
- Cuadro 0: Fondo azul noche. Rascacielos de 40 pisos al centro, ~80 % del alto, ~35 % del ancho, techo en ámbar. El piso bajo el techo ya se está borrando. Píldora: SIN UNA EXPLOSIÓN.
- 0–3 s: En 0,3 s se borra un piso bajo el techo y el techo baja un escalón; en 1,8 s, otro. En 2,4 s entra una dinamita y se tacha con ✗ rojo.
- Texto en pantalla: SIN UNA EXPLOSIÓN
- Voz 0–3 s: "Tienes que hacer desaparecer este rascacielos. Sin una explosión."

**CF**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos centrada, ~75 % del alto. A su pie, un cartucho de dinamita rojo tachado con una X naranja; la torre ya empieza a acortarse desde arriba.
- 0–3 s: La X tacha la dinamita en 0,3 s; la torre se acorta en cámara rápida con el techo naranja bajando entero. Píldora chica CÁMARA RÁPIDA en una esquina desde los 2,5 s.
- Texto en pantalla: SIN DINAMITA
- Voz 0–3 s: "A este rascacielos no lo dinamitaron. Lo encogieron."

## P49
**KR**
- Cuadro 0: Fondo oscuro. Torre blanca de 40 pisos, centrada, ~75 % del alto, techo ámbar. Una franja vertical de la fachada está cortada: adentro, el piso bajo el techo está vacío, sólo columnas. Afuera, la fachada se ve entera.
- 0–3 s: Una franja de corte baja por la torre: por fuera, entera; por dentro, el piso bajo el techo vacío y un obrero con casco sacando una viga. En 1,5 s la torre baja un piso.
- Texto en pantalla: POR FUERA, ENTERO
- Voz 0–3 s: "Este rascacielos se achica y casi nadie lo nota."

**CK**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos centrada, ~75 % del alto; al lado, un calendario naranja (~15 % del cuadro) pasa hojas; con cada hoja la torre baja dos pisos, techo naranja entero.
- 0–3 s: El calendario pasa diez hojas en 1 s y la torre se acorta dos pisos; se repite una vez. Píldora chica CÁMARA RÁPIDA en una esquina desde los 2,5 s.
- Texto en pantalla: −2 PISOS CADA 10 DÍAS
- Voz 0–3 s: "Este rascacielos pierde dos pisos cada diez días."

## P50
**HL**
- Cuadro 0: Fondo azul casi negro. Torre blanca de 40 pisos, centrada, ~75 % del alto. El último piso, en ámbar, intacto. Sobre él, una línea punteada marca la altura original, varios pisos más arriba. Camión con escombros saliendo por la base.
- 0–3 s: En 0,3 s la fachada se hunde un piso bajo el techo ámbar, que no cambia de forma; la punteada queda más lejos. A los 2,5 s el techo se ilumina.
- Texto en pantalla: LO ESTÁN DEMOLIENDO
- Voz 0–3 s: "Demuelen este rascacielos y no le sacan el techo."

**IZ**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos centrada, ~75 % del alto; al lado, un calendario naranja (~15 % del cuadro) pasa hojas; con cada hoja la torre baja dos pisos, techo naranja entero.
- 0–3 s: El calendario pasa diez hojas en 1 s y la torre se acorta dos pisos; se repite una vez. Píldora chica CÁMARA RÁPIDA en una esquina desde los 2,5 s.
- Texto en pantalla: −2 PISOS CADA 10 DÍAS
- Voz 0–3 s: "Este rascacielos pierde dos pisos cada diez días."

## P51
**SG**
- Cuadro 0: Fondo azul noche casi negro. Torre blanca de 40 pisos, fachada en zigzag, centrada, ~75 % del alto y ~30 % del ancho. El último piso, marcado en naranja, ya va bajando: la torre se acorta.
- 0–3 s: La torre pierde pisos de arriba en cámara rápida; el techo naranja baja con ella, entero. A los 2,5 s, píldora chica CÁMARA RÁPIDA en una esquina.
- Texto en pantalla: SE ENCOGE CON EL TECHO
- Voz 0–3 s: "Este rascacielos se está encogiendo. Lo raro no es que no haya explosiones."

**NM**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos, ~75 % del alto. Los 2 pisos de arriba en corte: adentro, una grúa naranja levanta una viga del piso; afuera, paneles con ventanas tapan todo.
- 0–3 s: La viga sube en 0,4 s; el corte se cierra y la torre se ve entera e igual; vuelve a abrirse y falta un piso. Una sola píldora.
- Texto en pantalla: LO DESARMAN A ESCONDIDAS
- Voz 0–3 s: "A este rascacielos lo desarman a escondidas. Por arriba."

## P52
**NX**
- Cuadro 0: Fondo oscuro. Rascacielos de 40 pisos al centro, ~80 % del alto; el techo en ámbar. Una grúa chica intenta levantar el techo y aparece un ✗ rojo grande encima. Píldora: NO LE SAQUES EL TECHO.
- 0–3 s: En 0,3 s la grúa levanta un poco el techo; en 1,2 s el ✗ rojo la frena y el techo vuelve a su lugar. En 2,5 s se borra el piso bajo el techo.
- Texto en pantalla: NO LE SAQUES EL TECHO
- Voz 0–3 s: "Para desarmar este rascacielos, nunca le saques el techo."

**QG**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos centrada, ~75 % del alto. A su pie, un cartucho de dinamita rojo tachado con una X naranja; la torre ya empieza a acortarse desde arriba.
- 0–3 s: La X tacha la dinamita en 0,3 s; la torre se acorta en cámara rápida con el techo naranja bajando entero. Píldora chica CÁMARA RÁPIDA en una esquina desde los 2,5 s.
- Texto en pantalla: SIN DINAMITA
- Voz 0–3 s: "A este rascacielos no lo dinamitaron. Lo encogieron."

## P53
**MI**
- Cuadro 0: Fondo azul casi negro. Torre blanca de 40 pisos, centrada, ~75 % del alto. El último piso, en ámbar, intacto. Sobre él, una línea punteada marca la altura original, varios pisos más arriba. Camión con escombros saliendo por la base.
- 0–3 s: En 0,3 s la fachada se hunde un piso bajo el techo ámbar, que no cambia de forma; la punteada queda más lejos. A los 2,5 s el techo se ilumina.
- Texto en pantalla: LO ESTÁN DEMOLIENDO
- Voz 0–3 s: "Demuelen este rascacielos y no le sacan el techo."

**BP**
- Cuadro 0: Fondo oscuro. Corte lateral de la punta de una torre blanca, ~70 % del cuadro: el techo ámbar arriba, debajo un piso totalmente vacío y, entre los dos, columnas de acero con gatos hidráulicos sosteniéndolo.
- 0–3 s: Los gatos se encogen y el techo ámbar baja despacio hacia el piso vacío; una viga cae fuera de cuadro. A los 2,5 s la cámara corta a la torre entera: el techo sigue arriba.
- Texto en pantalla: SIN PISO DEBAJO
- Voz 0–3 s: "A este rascacielos le sacaron el piso bajo el techo."

## P54
**IS**
- Cuadro 0: Fondo oscuro. Rascacielos de 40 pisos al centro, ~80 % del alto, con edificios vecinos pegados a los lados (~15 % cada uno). Cartuchos de dinamita en la base, tachados con ✗ rojo. Píldora: SIN RUIDO. SIN POLVO.
- 0–3 s: En 0,2 s caen cartuchos de dinamita junto a la base; en 0,8 s se tachan con ✗ rojo. En 1,8 s el techo ámbar baja un piso y la torre queda más corta.
- Texto en pantalla: SIN RUIDO. SIN POLVO.
- Voz 0–3 s: "Dinamita no. Este rascacielos tiene que desaparecer sin hacer ruido."

**LE**
- Cuadro 0: Fondo oscuro. Torre blanca de 40 pisos, centrada, ~75 % del alto, techo ámbar. Una franja vertical de la fachada está cortada: adentro, el piso bajo el techo está vacío, sólo columnas. Afuera, la fachada se ve entera.
- 0–3 s: Una franja de corte baja por la torre: por fuera, entera; por dentro, el piso bajo el techo vacío y un obrero con casco sacando una viga. En 1,5 s la torre baja un piso.
- Texto en pantalla: POR FUERA, ENTERO
- Voz 0–3 s: "Este rascacielos se achica y casi nadie lo nota."

## P55
**VQ**
- Cuadro 0: Fondo oscuro, pantalla partida. Izquierda (~45 % del ancho): una torre implosionando en una nube de polvo gris, ✗ rojo. Derecha (~45 %): torre blanca de 40 pisos con el techo ámbar intacto, sin polvo.
- 0–3 s: A la izquierda la torre cae en polvo; a la derecha la torre baja un piso entero, limpia, con el techo igual. A los 2 s la izquierda se apaga y queda la derecha.
- Texto en pantalla: SIN UNA EXPLOSIÓN
- Voz 0–3 s: "Este rascacielos ya perdió la mitad, y sin una explosión."

**QU**
- Cuadro 0: Fondo oscuro. Torre blanca de 40 pisos, centrada, ~75 % del alto, techo ámbar. Una franja vertical de la fachada está cortada: adentro, el piso bajo el techo está vacío, sólo columnas. Afuera, la fachada se ve entera.
- 0–3 s: Una franja de corte baja por la torre: por fuera, entera; por dentro, el piso bajo el techo vacío y un obrero con casco sacando una viga. En 1,5 s la torre baja un piso.
- Texto en pantalla: POR FUERA, ENTERO
- Voz 0–3 s: "Este rascacielos se achica y casi nadie lo nota."

## P56
**ZG**
- Cuadro 0: Fondo oscuro. Torre blanca de 40 pisos, centrada, ~75 % del alto, techo ámbar. Una franja vertical de la fachada está cortada: adentro, el piso bajo el techo está vacío, sólo columnas. Afuera, la fachada se ve entera.
- 0–3 s: Una franja de corte baja por la torre: por fuera, entera; por dentro, el piso bajo el techo vacío y un obrero con casco sacando una viga. En 1,5 s la torre baja un piso.
- Texto en pantalla: POR FUERA, ENTERO
- Voz 0–3 s: "Este rascacielos se achica y casi nadie lo nota."

**CI**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos centrada, ~75 % del alto. A su pie, un cartucho de dinamita rojo tachado con una X naranja; la torre ya empieza a acortarse desde arriba.
- 0–3 s: La X tacha la dinamita en 0,3 s; la torre se acorta en cámara rápida con el techo naranja bajando entero. Píldora chica CÁMARA RÁPIDA en una esquina desde los 2,5 s.
- Texto en pantalla: SIN DINAMITA
- Voz 0–3 s: "A este rascacielos no lo dinamitaron. Lo encogieron."

## P57
**HM**
- Cuadro 0: Fondo oscuro. Torre blanca de 40 pisos, centrada, ~75 % del alto, techo ámbar. Una franja vertical de la fachada está cortada: adentro, el piso bajo el techo está vacío, sólo columnas. Afuera, la fachada se ve entera.
- 0–3 s: Una franja de corte baja por la torre: por fuera, entera; por dentro, el piso bajo el techo vacío y un obrero con casco sacando una viga. En 1,5 s la torre baja un piso.
- Texto en pantalla: POR FUERA, ENTERO
- Voz 0–3 s: "Este rascacielos se achica y casi nadie lo nota."

**JA**
- Cuadro 0: Fondo azul noche casi negro. Torre blanca de 40 pisos, fachada en zigzag, centrada, ~75 % del alto y ~30 % del ancho. El último piso, marcado en naranja, ya va bajando: la torre se acorta.
- 0–3 s: La torre pierde pisos de arriba en cámara rápida; el techo naranja baja con ella, entero. A los 2,5 s, píldora chica CÁMARA RÁPIDA en una esquina.
- Texto en pantalla: SE ENCOGE CON EL TECHO
- Voz 0–3 s: "Este rascacielos se está encogiendo. Lo raro no es que no haya explosiones."

## P58
**EB**
- Cuadro 0: Fondo azul noche. Rascacielos de 40 pisos al centro, ~80 % del alto, ~35 % del ancho, techo en ámbar. El piso bajo el techo ya se está borrando. Píldora: SIN UNA EXPLOSIÓN.
- 0–3 s: En 0,3 s se borra un piso bajo el techo y el techo baja un escalón; en 1,8 s, otro. En 2,4 s entra una dinamita y se tacha con ✗ rojo.
- Texto en pantalla: SIN UNA EXPLOSIÓN
- Voz 0–3 s: "Tienes que hacer desaparecer este rascacielos. Sin una explosión."

**NW**
- Cuadro 0: Fondo oscuro. Rascacielos de 40 pisos al centro, ~80 % del alto, con edificios vecinos pegados a los lados (~15 % cada uno). Cartuchos de dinamita en la base, tachados con ✗ rojo. Píldora: SIN RUIDO. SIN POLVO.
- 0–3 s: En 0,2 s caen cartuchos de dinamita junto a la base; en 0,8 s se tachan con ✗ rojo. En 1,8 s el techo ámbar baja un piso y la torre queda más corta.
- Texto en pantalla: SIN RUIDO. SIN POLVO.
- Voz 0–3 s: "Dinamita no. Este rascacielos tiene que desaparecer sin hacer ruido."

## P59
**YZ**
- Cuadro 0: Fondo azul noche. Rascacielos de 40 pisos al centro, ~80 % del alto, ~35 % del ancho, techo en ámbar. El piso bajo el techo ya se está borrando. Píldora: SIN UNA EXPLOSIÓN.
- 0–3 s: En 0,3 s se borra un piso bajo el techo y el techo baja un escalón; en 1,8 s, otro. En 2,4 s entra una dinamita y se tacha con ✗ rojo.
- Texto en pantalla: SIN UNA EXPLOSIÓN
- Voz 0–3 s: "Tienes que hacer desaparecer este rascacielos. Sin una explosión."

**PS**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos, ~75 % del alto. Los 2 pisos de arriba en corte: adentro, una grúa naranja levanta una viga del piso; afuera, paneles con ventanas tapan todo.
- 0–3 s: La viga sube en 0,4 s; el corte se cierra y la torre se ve entera e igual; vuelve a abrirse y falta un piso. Una sola píldora.
- Texto en pantalla: LO DESARMAN A ESCONDIDAS
- Voz 0–3 s: "A este rascacielos lo desarman a escondidas. Por arriba."

## P60
**PA**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos, ~75 % del alto. Los 2 pisos de arriba en corte: adentro, una grúa naranja levanta una viga del piso; afuera, paneles con ventanas tapan todo.
- 0–3 s: La viga sube en 0,4 s; el corte se cierra y la torre se ve entera e igual; vuelve a abrirse y falta un piso. Una sola píldora.
- Texto en pantalla: LO DESARMAN A ESCONDIDAS
- Voz 0–3 s: "A este rascacielos lo desarman a escondidas. Por arriba."

**CM**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos centrada, ~75 % del alto; al lado, un calendario naranja (~15 % del cuadro) pasa hojas; con cada hoja la torre baja dos pisos, techo naranja entero.
- 0–3 s: El calendario pasa diez hojas en 1 s y la torre se acorta dos pisos; se repite una vez. Píldora chica CÁMARA RÁPIDA en una esquina desde los 2,5 s.
- Texto en pantalla: −2 PISOS CADA 10 DÍAS
- Voz 0–3 s: "Este rascacielos pierde dos pisos cada diez días."

## P61
**OH**
- Cuadro 0: Fondo azul casi negro. Torre blanca de 40 pisos, centrada, ~75 % del alto. El último piso, en ámbar, intacto. Sobre él, una línea punteada marca la altura original, varios pisos más arriba. Camión con escombros saliendo por la base.
- 0–3 s: En 0,3 s la fachada se hunde un piso bajo el techo ámbar, que no cambia de forma; la punteada queda más lejos. A los 2,5 s el techo se ilumina.
- Texto en pantalla: LO ESTÁN DEMOLIENDO
- Voz 0–3 s: "Demuelen este rascacielos y no le sacan el techo."

**ZD**
- Cuadro 0: Fondo oscuro. Torre blanca de 40 pisos, centrada, ~75 % del alto, techo ámbar. Una franja vertical de la fachada está cortada: adentro, el piso bajo el techo está vacío, sólo columnas. Afuera, la fachada se ve entera.
- 0–3 s: Una franja de corte baja por la torre: por fuera, entera; por dentro, el piso bajo el techo vacío y un obrero con casco sacando una viga. En 1,5 s la torre baja un piso.
- Texto en pantalla: POR FUERA, ENTERO
- Voz 0–3 s: "Este rascacielos se achica y casi nadie lo nota."

## P62
**HE**
- Cuadro 0: Fondo oscuro, pantalla partida. Izquierda (~45 % del ancho): una torre implosionando en una nube de polvo gris, ✗ rojo. Derecha (~45 %): torre blanca de 40 pisos con el techo ámbar intacto, sin polvo.
- 0–3 s: A la izquierda la torre cae en polvo; a la derecha la torre baja un piso entero, limpia, con el techo igual. A los 2 s la izquierda se apaga y queda la derecha.
- Texto en pantalla: SIN UNA EXPLOSIÓN
- Voz 0–3 s: "Este rascacielos ya perdió la mitad, y sin una explosión."

**EQ**
- Cuadro 0: Fondo oscuro. Corte lateral de la punta de una torre blanca, ~70 % del cuadro: el techo ámbar arriba, debajo un piso totalmente vacío y, entre los dos, columnas de acero con gatos hidráulicos sosteniéndolo.
- 0–3 s: Los gatos se encogen y el techo ámbar baja despacio hacia el piso vacío; una viga cae fuera de cuadro. A los 2,5 s la cámara corta a la torre entera: el techo sigue arriba.
- Texto en pantalla: SIN PISO DEBAJO
- Voz 0–3 s: "A este rascacielos le sacaron el piso bajo el techo."

## P63
**XW**
- Cuadro 0: Fondo oscuro. Una torre de 40 bloques de madera al centro, ~75 % del alto; una mano saca el bloque de arriba. Contador grande ×1 arriba a la derecha, en ámbar.
- 0–3 s: En 0,3 s la mano levanta el bloque de arriba. En 1,5 s el contador sube a ×100 y la torre se vuelve un rascacielos de 40 pisos, mismo tamaño en cuadro.
- Texto en pantalla: ×1 → ×100
- Voz 0–3 s: "Desarmar una torre es fácil: sacas el de arriba. Ahora hazlo con esta."

**UY**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos centrada, ~75 % del alto. A su pie, un cartucho de dinamita rojo tachado con una X naranja; la torre ya empieza a acortarse desde arriba.
- 0–3 s: La X tacha la dinamita en 0,3 s; la torre se acorta en cámara rápida con el techo naranja bajando entero. Píldora chica CÁMARA RÁPIDA en una esquina desde los 2,5 s.
- Texto en pantalla: SIN DINAMITA
- Voz 0–3 s: "A este rascacielos no lo dinamitaron. Lo encogieron."

## P64
**RY**
- Cuadro 0: Fondo oscuro. Una torre de 40 bloques de madera al centro, ~75 % del alto; una mano saca el bloque de arriba. Contador grande ×1 arriba a la derecha, en ámbar.
- 0–3 s: En 0,3 s la mano levanta el bloque de arriba. En 1,5 s el contador sube a ×100 y la torre se vuelve un rascacielos de 40 pisos, mismo tamaño en cuadro.
- Texto en pantalla: ×1 → ×100
- Voz 0–3 s: "Desarmar una torre es fácil: sacas el de arriba. Ahora hazlo con esta."

**BA**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos, ~75 % del alto. Los 2 pisos de arriba en corte: adentro, una grúa naranja levanta una viga del piso; afuera, paneles con ventanas tapan todo.
- 0–3 s: La viga sube en 0,4 s; el corte se cierra y la torre se ve entera e igual; vuelve a abrirse y falta un piso. Una sola píldora.
- Texto en pantalla: LO DESARMAN A ESCONDIDAS
- Voz 0–3 s: "A este rascacielos lo desarman a escondidas. Por arriba."

## P65
**ZE**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos centrada, ~75 % del alto. A su pie, un cartucho de dinamita rojo tachado con una X naranja; la torre ya empieza a acortarse desde arriba.
- 0–3 s: La X tacha la dinamita en 0,3 s; la torre se acorta en cámara rápida con el techo naranja bajando entero. Píldora chica CÁMARA RÁPIDA en una esquina desde los 2,5 s.
- Texto en pantalla: SIN DINAMITA
- Voz 0–3 s: "A este rascacielos no lo dinamitaron. Lo encogieron."

**HS**
- Cuadro 0: Fondo azul noche. Torre blanca de 40 pisos, ~75 % del alto. Los 2 pisos de arriba en corte: adentro, una grúa naranja levanta una viga del piso; afuera, paneles con ventanas tapan todo.
- 0–3 s: La viga sube en 0,4 s; el corte se cierra y la torre se ve entera e igual; vuelve a abrirse y falta un piso. Una sola píldora.
- Texto en pantalla: LO DESARMAN A ESCONDIDAS
- Voz 0–3 s: "A este rascacielos lo desarman a escondidas. Por arriba."

## P66
**BU**
- Cuadro 0: Fondo azul casi negro. Torre blanca de 40 pisos, centrada, ~75 % del alto. El último piso, en ámbar, intacto. Sobre él, una línea punteada marca la altura original, varios pisos más arriba. Camión con escombros saliendo por la base.
- 0–3 s: En 0,3 s la fachada se hunde un piso bajo el techo ámbar, que no cambia de forma; la punteada queda más lejos. A los 2,5 s el techo se ilumina.
- Texto en pantalla: LO ESTÁN DEMOLIENDO
- Voz 0–3 s: "Demuelen este rascacielos y no le sacan el techo."

**IQ**
- Cuadro 0: Fondo azul noche casi negro. Torre blanca de 40 pisos, fachada en zigzag, centrada, ~75 % del alto y ~30 % del ancho. El último piso, marcado en naranja, ya va bajando: la torre se acorta.
- 0–3 s: La torre pierde pisos de arriba en cámara rápida; el techo naranja baja con ella, entero. A los 2,5 s, píldora chica CÁMARA RÁPIDA en una esquina.
- Texto en pantalla: SE ENCOGE CON EL TECHO
- Voz 0–3 s: "Este rascacielos se está encogiendo. Lo raro no es que no haya explosiones."
