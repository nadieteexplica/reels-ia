# Tu feed de Shorts

Estás pasando YouTube Shorts con el pulgar, como cualquier noche. Te van a aparecer 7 videos, uno tras otro, en el orden de abajo.
Ninguno es de una cuenta que sigas. De cada uno tienes lo que se ve y se oye en los primeros 3 segundos (descrito o en imagen)
y, si decides quedarte, el resto de lo que dice la voz.

Eres: **Camila, 22, Medellín (Colombia). Estudia diseño, mira SIN sonido en el trabajo; juzga primero si se ve bonito y claro. Comparte lo que le da 'ganas de contarle a alguien'.**

Reglas para contestar:
- Decide como de verdad decides en un feed: en menos de 2 segundos y con flojera. Lo normal es deslizar; quedarse se gana.
- Primero mira SOLO lo de los primeros 3 s ("Cuadro 0" y "0–3 s", o la imagen si la hay, más "Texto en pantalla" y "Voz 0–3 s"). Decide si deslizas ANTES de leer "Si te quedas".
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

## Video JC
- **Cuadro 0:** Baño con cortina de rayas verde agua y blancas; hombre de bigote, ojos cerrados, espuma en cabeza y torso, ocupa ~75 % del ancho y ~80 % del alto (cortado abajo); ducha arriba a la derecha. Sin otro texto.
- **0–3 s:** 0–1 s plano frontal casi fijo. ~1,5 s corte a vista lateral: la cortina se curva hacia el hombre (él ocupa ~25 % del ancho). ~3 s corte a plano de espalda con espuma.
- **Texto en pantalla:** sólo subtítulos
- **Voz 0–3 s:** "Te estás duchando... y la cortina se te viene encima."
- **Si te quedas:** ¿Un fantasma? No. Y tampoco es solo el aire caliente. Con agua caliente pasa más fuerte, pero pasa hasta con agua fría. Mira la ducha por dentro. El chorro arrastra el aire hacia abajo... y arma un remolino acostado, que gira como una rueda. En el centro del remolino, la presión baja. Y el aire de afuera, que empuja más, mete la cortina hacia ti. ¿La solución? Una cortina más pesada. Al remolino le cuesta moverla. Y si esa igual se mueve... ahí sí es un fantasma.

## Video HS
- **Cuadro 0:** Personaje 3D de pelo negro y polera salmón; cabeza ocupa ~37 % del alto y ~63 % del ancho; muerde un cono de tres bolas abajo a la izquierda; parche blanco en la frente; fondo borroso. Sin otro texto.
- **0–3 s:** 0,5 s ojos abiertos hacia el helado. 1,5 s boca abierta, cejas arriba. 2 s ojos cerrados, el parche blanco de la frente crece. 3 s corte a plano abierto: manos en la cabeza, frente roja.
- **Texto en pantalla:** sólo subtítulos
- **Voz 0–3 s:** "Te comes un helado rápido y... ¡zas! Te duele la frente."
- **Si te quedas:** Pero el frío nunca tocó tu cerebro. ¿Qué pasó? Rebobinemos. Día de calor. Pides el helado más grande del carrito... y te lo comes como si alguien te lo fuera a quitar. El helado toca el techo de tu boca y lo enfría de golpe. Los vasos sanguíneos de ahí se encogen... y de repente se abren para mandar sangre caliente. Ese cambio brusco lo detecta el trigémino, el nervio que siente toda tu cara. Una de sus ramas llega a la frente, y tu cerebro se confunde: cree que el dolor viene de ahí. En 2012, científicos de Harvard lo midieron con trece voluntarios y agua helada. Justo cuando les dolía, una arteria de su cerebro se ensanchaba. Al volver a su tamaño, el dolor se iba. Y lo más loco: tu cerebro no siente dolor. Lo que duele son los vasos y nervios que lo rodean. Su nombre científico es ganglioneuralgia esfenopalatina. Sí, en serio. El truco: aprieta la lengua contra el paladar para calentarlo, o toma algo tibio. Dura de segundos a un par de minutos, y no es peligroso. La próxima vez, come más lento... aunque, seamos honestos, nadie come helado lento.

## Video XP
- **Cuadro 0:** Cielo, montañas y dos chimeneas con vapor al fondo; hombre con casco blanco y chaleco naranja en el aire arriba a la izquierda (~23 % del alto, ~15 % del ancho); estructura cilíndrica en la mitad inferior. Texto: «SIMULACIÓN».
- **0–3 s:** 0–1,5 s plano fijo, el hombre asciende levemente. ~2 s corte a plano más abierto sobre suelo agrietado: hombre ocupa ~11–13 % del alto, sobre la estructura cilíndrica. «SIMULACIÓN» se mantiene.
- **Texto en pantalla:** «SIMULACIÓN» (etiqueta amarilla arriba a la izquierda, presente de 0 a 3 s)
- **Voz 0–3 s:** "Tu cuerpo repele los imanes. Con el imán correcto, podrías flotar."
- **Si te quedas:** Ya pasó con esta rana: flota sola dentro de un imán. Es más que nada agua, como tú. Y al agua, un imán la empuja... un poquito. Con uno bien fuerte, ese empujón le gana a la gravedad. ¿Y para ti? Habría que construirlo. Primero: un hueco donde quepas. El de la rana mide tres centímetros: ni tu mano cabe. Después: bobinas y más bobinas, hasta cuarenta teslas o más. Más del doble de lo que necesitó la rana. Y al final, enchufarlo a un reactor nuclear entero... solo para ti. Ahí sí... flotarías.

## Video NH
- **Cuadro 0:** Desierto con cactus verdes; pájaro gris con un ají rojo en el pico a la izquierda (~31 % del alto, ~28 % del ancho); detrás un ratón sobre escalones lanza una llama naranja hacia arriba. Sin otro texto.
- **0–3 s:** 0–1,5 s plano fijo, pájaro quieto, la llama del ratón cambia de forma. Entre 1,5 y 2 s corte a primer plano de la cabeza del pájaro, fondo borroso. 3 s pico entreabierto con el ají asomando.
- **Texto en pantalla:** sólo subtítulos
- **Voz 0–3 s:** "Este pájaro se come un ají y ni lo siente."
- **Si te quedas:** Este ratón lo prueba... y echa fuego. Para el ají, tú y este ratón son lo mismo: mamíferos. Tu lengua tiene sensores de calor, como alarmas de incendio. Suenan con lo que quema de verdad. El ají trae capsaicina, una molécula que las hace sonar. Tu cerebro cree que te quemas, aunque nada esté caliente. Los pájaros tienen la misma alarma, pero la capsaicina no la activa. Sienten el calor... no el picante. ¿Por qué? En Arizona, científicos filmaron un chiltepín, un ají silvestre. Ratones y ratas ni lo tocaban. Los pájaros se lo devoraban. Si se lo comiera, el ratón molería las semillas. El pájaro se las traga enteras, y salen en su caca listas para brotar. Los científicos creen que el picante es un guardia. Espanta a los que destruyen semillas. Y lo más loco: hay un mamífero que casi no lo siente. La tupaya, de China. Un solo cambio en su alarma... y come plantas picantes como si nada. ¿Y tú? Toma leche, aunque sea descremada. En un estudio con 72 personas, fue de lo que más bajó el ardor. Las bebidas con gas funcionaron mal. Mándaselo al que se cree inmune al picante. Para el ají... es un ratón más.

## Video ZX
- **Cuadro 0:** Cielo nublado sobre el mar. Abajo, una flota de barcos de guerra grises en fila. Un avión de caza verde oscuro con un círculo rojo sale de una nube en picada hacia los barcos; ocupa 30 % del cuadro.
- **0–3 s:** El avión baja en picada, crece hasta 45 % del cuadro; desde los barcos suben balas trazadoras. Corte a la cabina: un piloto joven con cinta blanca en la frente.
- **Texto en pantalla:** PACÍFICO, 1944
- **Voz 0–3 s:** "1944. Japón está perdiendo la guerra…"
- **Si te quedas:** 1944. Japón está perdiendo la guerra… y manda a sus pilotos a no volver. Así nacen los kamikazes. Mayo de 1945: dos de ellos chocan este portaaviones en treinta segundos. Mueren más de trescientos cuarenta marineros. Para los estadounidenses es una pesadilla: un enemigo que no quiere volver. Del otro lado, los pilotos tienen diecisiete, dieciocho, veinte años. Oficialmente son voluntarios. Pero decir que no es casi imposible. Antes de despegar, escriben una última carta, muchas veces para su mamá. Sólo uno de cada siete logra chocar. Pero en Okinawa hunden treinta y seis barcos. Y Japón guarda más de cinco mil aviones para cuando lo invadan. Ese miedo es una de las razones para lanzar la bomba atómica. Para esa invasión, Estados Unidos había fabricado casi medio millón de medallas para heridos. La invasión nunca llegó… y esas medallas se siguieron entregando por más de cincuenta años.

## Video US
- **Cuadro 0:** Edificio de fachada de ladrillo de cinco pisos sobre una fila de soportes cilíndricos azules y amarillos (~77 % del ancho, ~47 % del alto); cielo arriba, suelo gris-café en la mitad inferior; conos naranjos. Sin otro texto.
- **0–3 s:** 0–1 s plano general fijo. Entre 1 y 1,5 s corte a plano cercano de la base con soportes. Desde 1,5 s aparece la etiqueta «CÁMARA RÁPIDA»; plano casi igual hasta 3 s.
- **Texto en pantalla:** «CÁMARA RÁPIDA» desde ~1,5 s; de 0 a 1 s sólo subtítulos
- **Voz 0–3 s:** "Este edificio de cinco pisos se fue caminando."
- **Si te quedas:** Y no, no es broma... tiene patas. Es una escuela de mil novecientos treinta y cinco, en Shanghái. Pesa más de siete mil seiscientas toneladas. Y en dos mil veinte estorbaba: ahí iban a hacer oficinas y tiendas. En vez de demolerla, la movieron. Primero cavaron alrededor. Le metieron debajo ciento noventa y ocho patas robóticas. Cortaron las columnas... y las patas la alzaron entera. Las patas van en dos grupos. Uno aguanta el peso. El otro se alza y da un paso. Luego cambian. Como tú cuando caminas. Según el jefe técnico, es como ponerle muletas para que se pare y camine. ¿Y por qué no usaron rieles? Los rieles no doblan, y había que girarla veintiún grados. Caminó sesenta y dos metros. Se demoró dieciocho días. Tú caminas eso en menos de un minuto. Y lo más loco: Shanghái ya tenía práctica. En dos mil tres movió su sala de conciertos... para que pasara una autopista. Así que esta escuela, a los ochenta y cinco años... por fin aprendió a caminar.

## Video BM
- **Cuadro 0:** Ciudad al atardecer; torre de fachada cuadriculada en el centro (~34 % del ancho, ~47 % del alto) con un contorno blanco de caja sobre su techo; edificios bajos abajo. Textos: «CÁMARA RÁPIDA», «QUEDAN 36 PISOS», «ANTES: 40 PISOS».
- **0–3 s:** 0–2 s mismo plano; la parte alta de la torre baja y el contador va 36→34→33→32→30. ~1,5 s aparece «EL MÁS ALTO QUE JAPÓN HA BOTADO». ~3 s corte a plano cercano de fachada.
- **Texto en pantalla:** «CÁMARA RÁPIDA» (fijo); contador «QUEDAN 36 / 34 / 33 / 32 / 30 PISOS»; «ANTES: 40 PISOS»; desde ~1,5 s «EL MÁS ALTO QUE JAPÓN HA BOTADO»
- **Voz 0–3 s:** "Este es el edificio más alto que Japón ha botado."
- **Si te quedas:** Y lo más impresionante: lo demolieron piso por piso... sin ninguna explosión. El truco: el techo nunca se saca. Primero, meten columnas de acero y lo paran sobre quince gatos hidráulicos, como un sombrero gigante. Solo armar eso toma dos meses. Después, lo cierran con paneles con ventanas a la misma altura que las del hotel: desde la calle parece un piso más. Y adentro, escondidos, desarman el piso de abajo. Cuando queda vacío, los gatos bajan el sombrero... un piso. Y otra vez. Y otra vez. Como su construcción, en reversa. Y lo más loco: la grúa que baja los escombros genera electricidad... y con eso prenden las luces de la obra. Dos pisos cada diez días. Siete meses después, donde había un rascacielos de cuarenta pisos... no quedaba nada. Y nadie lo vio caer.
