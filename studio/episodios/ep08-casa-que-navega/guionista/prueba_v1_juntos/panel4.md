# Tu feed de Shorts

Estás pasando YouTube Shorts con el pulgar, como cualquier noche. Te van a aparecer 9 videos, uno tras otro, en el orden de abajo.
Ninguno es de una cuenta que sigas. De cada uno tienes lo que se ve y se oye en los primeros 3 segundos (descrito cuadro a cuadro)
y, si decides quedarte, el resto de lo que dice la voz.

Eres: **Ximena, 28, Ciudad de México. Pasa Shorts en la cama antes de dormir, CON sonido, cansada. Ya vio mil videos de 'datos curiosos' y le aburren los que empiezan igual. Le manda a su pareja lo que le da risa.**

Reglas para contestar:
- Decide como de verdad decides en un feed: en menos de 2 segundos y con flojera. Lo normal es deslizar; quedarse se gana.
- Primero mira SOLO lo de los primeros 3 s ("Cuadro 0" y "0–3 s", o la imagen si la hay, más "Texto en pantalla" y "Voz 0–3 s"). Decide si deslizas ANTES de leer "Si te quedas".
- Si en el cuadro 0 no entiendes qué estás mirando, o se ve falso, genérico, de IA, o como una clase, deslizas.
- No premies lo "inteligente": premia lo que te haría quedarte, reírte o mandárselo a alguien.
- Si te quedas, lee "Si te quedas" y di en qué frase te irías (si te vas) y por qué, en tus palabras.

Contesta SOLO con un JSON válido (sin texto antes ni después), con esta forma:
{"perfil": "<tu nombre>",
  "videos": [
    {"codigo": "<código>",
      "se_queda_2s": true|false,
      "por_que_2s": "<una frase: qué viste o entendiste en el primer segundo>",
      "se_va_en": "<frase exacta donde te irías, o 'final' si lo ves entero, o 'cuadro0'>",
      "lo_ve_entero_pct": <0-100, probabilidad de que lo veas hasta el final>,
      "lo_manda": true|false,
      "a_quien": "<a quién, o ''>",
      "pregunta_que_te_dejo": "<la pregunta que te hizo quedarte, o ''>"}
  ],
  "orden": ["<código del que más te enganchó>", "...", "<código del que menos>"]}

## Video KD (73 s)
- **Cuadro 0:** Primer plano de un joven 3D de dibujo animado (polera coral con estrella) comiéndose un cono de helado de 3 bolas; la cara ocupa el tercio superior, fondo de parque desenfocado.
- **0–3 s:** 0–1 s: sigue comiendo. 1,5 s: abre los ojos y la boca. 2 s: primerísimo plano, escarcha que le sale de la frente, ojos apretados. 3 s: plano medio, se agarra la cabeza con las dos manos.
- **Texto en pantalla:** Subtítulos palabra por palabra.
- **Voz 0–3 s:** "Te comes un helado rápido y... ¡zas! Te duele la frente."
- **Si te quedas:** Pero el frío nunca tocó tu cerebro. ¿Qué pasó? Rebobinemos. Día de calor. Pides el helado más grande del carrito... y te lo comes como si alguien te lo fuera a quitar. El helado toca el techo de tu boca y lo enfría de golpe. Los vasos sanguíneos de ahí se encogen... y de repente se abren para mandar sangre caliente. Ese cambio brusco lo detecta el trigémino, el nervio que siente toda tu cara. Una de sus ramas llega a la frente, y tu cerebro se confunde: cree que el dolor viene de ahí. En 2012, científicos de Harvard lo midieron con trece voluntarios y agua helada. [...] Y lo más loco: tu cerebro no siente dolor. [...] El truco: aprieta la lengua contra el paladar para calentarlo, o toma algo tibio. [...] La próxima vez, come más lento... aunque, seamos honestos, nadie come helado lento.

## Video SS (29 s)
- **Cuadro 0:** Playa de arena oscura. Una casa de madera de un piso sobre troncos, tirada por dos yuntas de bueyes; la casa ocupa media pantalla y los bueyes un cuarto abajo. El mar, unos metros adelante.
- **0–3 s:** Los bueyes tiran, un tronco sale rodando por atrás y se levanta arena. A los 2 s, corte desde el agua: la casa viene de frente hacia la cámara.
- **Texto en pantalla:** Píldora 'DIRECTO AL MAR' + subtítulos
- **Voz 0–3 s:** "Bueyes arrastrando una casa… al mar. Es una mudanza,"
- **Si te quedas:** en unas islas del sur de Chile. Aquí, cuando te mudas, te llevas la casa entera. Los vecinos ponen sus bueyes, y la casa rueda sobre troncos. Pero el terreno nuevo está al otro lado del agua. Por eso, en la orilla, los bueyes se quedan… y la casa sigue sin ellos. Es de madera: flota, remolcada por una lancha. Así que aquí, en día de mudanza, vas a ver…

## Video KA (30 s)
- **Cuadro 0:** Vista desde una lancha mirando hacia atrás: abajo, la popa, el motor y la estela. Una cuerda tensa sube hasta una casa de madera de un piso que flota detrás, de frente, media pantalla de ancho.
- **0–3 s:** La cámara se mece con el bote, la estela corre y la casa avanza detrás. A los 2 s, corte lateral: la lancha chica tirando de la casa.
- **Texto en pantalla:** Píldora 'MUDANZA POR EL MAR' + subtítulos
- **Voz 0–3 s:** "Tu casa te sigue… por el mar. Así te mudas"
- **Si te quedas:** en unas islas del sur de Chile. Primero, le pides ayuda a tus vecinos: traen sus bueyes. Montan tu casa sobre troncos, y los bueyes la arrastran hasta la orilla. Pero tu terreno nuevo queda al otro lado del agua. Por eso la amarran a una lancha… y tu casa se mete al mar. Es de madera: flota, y te sigue. Así que si te mudas aquí, no mires atrás:

## Video BY (75 s)
- **Cuadro 0:** Desierto de dibujo animado con cactus. En primer plano un pájaro gris con un ají rojo en el pico; detrás, un ratón rosado que escupe una llamarada de fuego por la boca.
- **0–3 s:** 0–1,5 s: el mismo cuadro, la llamarada sigue. 2 s: primer plano del pájaro tragándose el ají, tranquilo. 3 s: el pájaro de perfil.
- **Texto en pantalla:** Subtítulos palabra por palabra.
- **Voz 0–3 s:** "Este pájaro se come un ají y ni lo siente."
- **Si te quedas:** Este ratón lo prueba... y echa fuego. Para el ají, tú y este ratón son lo mismo: mamíferos. Tu lengua tiene sensores de calor, como alarmas de incendio. [...] El ají trae capsaicina, una molécula que las hace sonar. [...] Los pájaros tienen la misma alarma, pero la capsaicina no la activa. [...] En Arizona, científicos filmaron un chiltepín [...] El pájaro se las traga enteras, y salen en su caca listas para brotar. [...] Y lo más loco: hay un mamífero que casi no lo siente. La tupaya, de China. [...] Toma leche, aunque sea descremada. [...] Mándaselo al que se cree inmune al picante. Para el ají... es un ratón más.

## Video LA (37 s)
- **Cuadro 0:** Primer plano de un hombre mayor 3D con bigote, ojos cerrados y espuma de shampoo en el pelo, tranquilo bajo la ducha; detrás, una cortina a rayas turquesa; la espuma le tapa el pecho.
- **0–3 s:** 0–1 s: el mismo plano, tranquilo. 1,5–2 s: corte: la cortina se infla hacia adentro y se le pega por la espalda. 3 s: plano de espalda con la cortina encima.
- **Texto en pantalla:** Subtítulos palabra por palabra.
- **Voz 0–3 s:** "Te estás duchando... y la cortina se te viene encima."
- **Si te quedas:** ¿Un fantasma? No. Y tampoco es solo el aire caliente. Con agua caliente pasa más fuerte, pero pasa hasta con agua fría. Mira la ducha por dentro. El chorro arrastra el aire hacia abajo... y arma un remolino acostado, que gira como una rueda. En el centro del remolino, la presión baja. Y el aire de afuera, que empuja más, mete la cortina hacia ti. ¿La solución? Una cortina más pesada. Al remolino le cuesta moverla. Y si esa igual se mueve... ahí sí es un fantasma.

## Video OX (64 s)
- **Cuadro 0:** Un edificio de ladrillo de 5 pisos, entero, solo en una explanada vacía, visto desde abajo en diagonal; en la base, en vez de cimientos, una hilera de patas mecánicas cortas (amarillas y azules). Cielo azul.
- **0–3 s:** 0–1 s: el edificio sobre sus patas. 1,5 s: corte a la base: la hilera de patas de cerca, píldora 'CÁMARA RÁPIDA'. 2–3 s: las patas se mueven y el edificio avanza.
- **Texto en pantalla:** Subtítulos palabra por palabra; píldora 'CÁMARA RÁPIDA'.
- **Voz 0–3 s:** "Este edificio de cinco pisos se fue caminando."
- **Si te quedas:** Y no, no es broma... tiene patas. Es una escuela de mil novecientos treinta y cinco, en Shanghái. Pesa más de siete mil seiscientas toneladas. Y en dos mil veinte estorbaba: ahí iban a hacer oficinas y tiendas. En vez de demolerla, la movieron. Primero cavaron alrededor. Le metieron debajo ciento noventa y ocho patas robóticas. Cortaron las columnas... y las patas la alzaron entera. Las patas van en dos grupos. Uno aguanta el peso. El otro se alza y da un paso. Luego cambian. Como tú cuando caminas. [...] ¿Y por qué no usaron rieles? Los rieles no doblan, y había que girarla veintiún grados. Caminó sesenta y dos metros. Se demoró dieciocho días. Tú caminas eso en menos de un minuto. Y lo más loco: Shanghái ya tenía práctica. En dos mil tres movió su sala de conciertos... para que pasara una autopista. Así que esta escuela, a los ochenta y cinco años... por fin aprendió a caminar.

## Video IP (40 s)
- **Cuadro 0:** Plano general de un salar al atardecer: un cilindro metálico oscuro enorme ocupa la mitad de abajo del cuadro; arriba, chico y lejos, un hombre con chaleco naranja flota en el aire; dos columnas de vapor blanco detrás. Píldora 'SIMULACIÓN' arriba a la izquierda.
- **0–3 s:** 0–1,5 s: el mismo plano, el hombre flota quieto. 2–3 s: la cámara se aleja: el cilindro entero en el salar y el hombre flotando sobre él.
- **Texto en pantalla:** Píldora 'SIMULACIÓN'; subtítulos palabra por palabra.
- **Voz 0–3 s:** "Tu cuerpo repele los imanes. Con el imán correcto, podrías flotar."
- **Si te quedas:** Ya pasó con esta rana: flota sola dentro de un imán. Es más que nada agua, como tú. Y al agua, un imán la empuja... un poquito. Con uno bien fuerte, ese empujón le gana a la gravedad. ¿Y para ti? Habría que construirlo. Primero: un hueco donde quepas. El de la rana mide tres centímetros: ni tu mano cabe. Después: bobinas y más bobinas, hasta cuarenta teslas o más. Más del doble de lo que necesitó la rana. Y al final, enchufarlo a un reactor nuclear entero... solo para ti. Ahí sí... flotarías.

## Video UB (28 s)
- **Cuadro 0:** Plano cerrado: casa de madera de un piso en medio del mar, dos tercios del ancho, cámara baja. No se ve lancha; sólo una cuerda tensa que sale por el borde derecho. Cerros al fondo.
- **0–3 s:** Una ola chica pega en el costado; la casa se mece y avanza, con estela. A los 2 s, corte lateral a ras del agua: la cuerda sigue saliendo de cuadro.
- **Texto en pantalla:** Píldora 'LA CASA QUE NADA' (a los 2 s cambia a 'SE ESTÁ MUDANDO') + subtítulos
- **Voz 0–3 s:** "Esta casa sabe nadar. No se está hundiendo:"
- **Si te quedas:** se está mudando, en Chiloé, al sur de Chile. ¿Y cómo llegó hasta aquí? Los vecinos la montaron sobre troncos, y sus bueyes la arrastraron hasta la orilla. Pero en la orilla, los bueyes se quedaron… y la casa siguió sola, mar adentro. ¿Nadar? No tanto: es de madera, flota… y la remolca una lancha. Así que si ves una casa en el mar, tranquilo:

## Video XG (48 s)
- **Cuadro 0:** Plano general de una ciudad al atardecer: un rascacielos en el centro (ocupa ~1/4 del alto del cuadro) con una caja de andamios en la punta. Píldoras arriba: 'CÁMARA RÁPIDA', 'QUEDAN 36 PISOS', 'ANTES: 40 PISOS'.
- **0–3 s:** 0–2 s: el contador baja (36, 34, 33, 32, 30) mientras el edificio se acorta; a 1,5 s aparece la píldora 'EL MÁS ALTO QUE JAPÓN HA BOTADO'. 3 s: corte a la fachada de cerca.
- **Texto en pantalla:** 3–4 píldoras con texto chico + subtítulos.
- **Voz 0–3 s:** "Este es el edificio más alto que Japón ha botado."
- **Si te quedas:** Y lo más impresionante: lo demolieron piso por piso... sin ninguna explosión. El truco: el techo nunca se saca. Primero, meten columnas de acero y lo paran sobre quince gatos hidráulicos, como un sombrero gigante. Solo armar eso toma dos meses. Después, lo cierran con paneles con ventanas a la misma altura que las del hotel: desde la calle parece un piso más. Y adentro, escondidos, desarman el piso de abajo. Cuando queda vacío, los gatos bajan el sombrero... un piso. Y otra vez. Y otra vez. Como su construcción, en reversa. Y lo más loco: la grúa que baja los escombros genera electricidad... y con eso prenden las luces de la obra. Dos pisos cada diez días. Siete meses después, donde había un rascacielos de cuarenta pisos... no quedaba nada. Y nadie lo vio caer.
