# Ep. 14 — "Tu tarjeta no tiene batería" (cómo paga una tarjeta sin contacto)

Pedido de Tomás (12-nov-2026, 10:25): descartó el Ep. 13 (pantalla táctil) porque "ese video ya existe y sabías que existía… busca una idea nueva". Se le mostraron 3 ideas con lo que se encontró de cada una en español y **eligió "Tarjeta sin contacto"** (sabiendo que el ángulo "sin batería" tiene algo de cobertura en blogs). **Falta su OK para publicar.**
Línea: datos (tecnología cotidiana, "¿cómo funciona por dentro?"). Estilo: 2D de comedia por código.

## Idea central (regla 0)
Tu tarjeta no tiene batería: la máquina donde pagas le manda la energía por el aire, y con esa energía el chip despierta, paga y se vuelve a apagar.
**Objeto que carga la idea:** la tarjeta dormida (cuadro 0, el alambre por dentro, el chip que despierta, la tarjeta que se vuelve a dormir).

## Paquete de gancho
- **Cuadro 0:** una tarjeta durmiendo (Zzz) y una batería tachada.
- **Texto en pantalla:** SIN BATERÍA
- **Voz 0–3 s:** "Tu tarjeta paga sin batería. Ni pila, ni nada."
- **Pregunta que abre:** si no tiene batería, ¿con qué energía paga cuando la acercas?
- **Se paga:** la energía de la máquina y el alambre que la atrapa (~35–55 %), el chip que despierta (~60 %).
- **Momento para mandarlo:** "Tu tarjeta pasa la vida apagada. Solo despierta para pagar."

## Voz (v2, tras la puerta 1)
Tu tarjeta paga sin batería. Ni pila, ni nada. La acercas y paga igual. ¿De dónde saca la energía? Se la presta la máquina. Dentro del plástico hay un alambre enrollado. Es una antena. Cuando te van a cobrar, la máquina se activa. Crea a su alrededor un campo invisible de energía. Tú acercas la tarjeta y el alambre atrapa parte de esa energía. Pero solo funciona muy cerca: a unos pocos centímetros. Con esa energía se prende el chip. En un segundo o dos, despierta y le manda un código a la máquina. Ese código sirve una sola vez. La alejas, y el chip se queda sin energía. Tu tarjeta pasa la vida apagada. Solo despierta cuando la acercas.

## Puerta 1 (auditor independiente, 12-nov)
v1: CAMBIOS (cumple el pedido: objeto cotidiano, puro mecanismo, cero anécdota; pero la paradoja llegaba en la frase 3 → va en la 1; "lanza energía al aire" chocaba con que la máquina sólo emite al iniciar el cobro → "cuando te van a cobrar, la máquina se activa. Crea a su alrededor un campo invisible de energía"; fuera "finísimo"; "se vuelve a apagar" → "la alejas, y el chip se queda sin energía"; sin "por eso" en la distancia; "solo despierta para pagar" → "cuando la acercas"; una frase de 19 palabras partida en dos). v2 = la reescritura del auditor (119 palabras).

## Fuentes (leídas en el párrafo, 12-nov-2026)
1. Secure Technology Alliance (ex Smart Card Alliance), preguntas frecuentes sobre tarjetas sin contacto (copia): https://www.scribd.com/doc/223970335/Www-Smartcardalliance-Org — la tarjeta tiene un chip y una antena embebida en el plástico; usa campos magnéticos o electromagnéticos tanto para alimentar la tarjeta como para intercambiar datos; cuando la tarjeta entra al campo electromagnético del lector, el chip se enciende; estándar ISO/IEC 14443 a 13,56 MHz, a menos de 10 cm.
2. SecureIDNews, "Tech 101: Contactless smart cards" (con ingenieros de NXP): https://www.secureidnews.com/news-item/tech-101-contactless-smart-cards/ — dentro de la tarjeta hay una bobina de antena conectada al chip, que elimina la necesidad de una fuente de energía interna: "no tiene batería… la alimenta el campo del lector"; el lector genera un campo magnético y cuando la tarjeta entra en él obtiene la energía para encenderse.
3. Visa, "Contactless payments" (preguntas frecuentes oficiales): https://usa.visa.com/pay-with-visa/contactless-payments/contactless-payments.html y https://www.visa.com/en-za/personal/technologies/contactless-payments — la tarjeta sin contacto es una tarjeta con chip y antena NFC para pagos de corto alcance; cada transacción va con un código de un solo uso que cambia en cada pago; hay que ponerla a 2,5–5 cm (1–2 pulgadas) del símbolo; "uno o dos segundos deberían bastar"; el comercio tiene que iniciar primero el cobro.
4. Golden 1 Credit Union, "Are contactless cards safe?": https://help.golden1.com/article/are-contactless-cards-safe-3358 — segunda fuente del código de un solo uso: es específico de cada transacción y no se puede reutilizar; la tarjeta debe estar a 1–2 pulgadas del terminal.
- No se dice: marcas; que es imposible de clonar o 100 % segura (Visa dice que el fraude por lectura es "muy improbable y limitado"); cuánta energía; que la máquina emite siempre (emite cuando se inicia el cobro); la frecuencia.
- "Enrollado": las fuentes dicen "bobina de antena" (antenna coil).
