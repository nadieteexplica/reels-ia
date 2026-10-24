# Estilo realista — la línea de la cuenta (desde el Ep. 5)

**Decisión de Tomás (23-oct-2026, 18:09):** el Ep. 5 ("El imán que hace flotar a una rana") es **el estilo de video y de edición que más le ha gustado**. De aquí en adelante se sigue esta línea. Este documento dice qué es y cómo se hizo, para repetirlo sin volver a descubrirlo.

En una frase: **"realista pero en un mundo animado"** (Tomás, 22-oct). Es animación 3D con proporciones, materiales y luz reales. Se nota que es 3D, pero nadie lo llamaría "monito animado". La referencia de **calidad** es Zack D. Films (nunca su marca, sus personajes ni sus formatos). **No es fotorrealismo de IA**: Tomás rechazó las imágenes de Canva ("nada de nada").

Cada episodio nuevo lleva `estilo.json` con `"estilo": "realista"` (copiar `studio/plantilla/estilo_realista.json`). Así el auditor exige `realismo` ≥ 8.

---

## 1. Qué hace que se vea así (la receta visual)

### Mundo
- **Exteriores abiertos y espaciosos** (Tomás, 22-oct): nada de cuartos ni naves cerradas. El Ep. 5 pasa entero en un **salar de Atacama al atardecer**, un piso enorme y limpio que da poco ruido visual.
  - El salar mide 40 km para que llegue hasta los cerros.
  - Los cerros (8–14 km) tienen formas grandes, bruma de distancia y "falda": el relieve se apaga en el borde para que toquen el suelo.
  - Hay un volcán de cono y una central nuclear con sus torres a 2,4 km.
- **Todo a escala real**, como lo que se muestra como verdad:
  - la rana mide 2,2 cm y está en un tubo de ~3 cm;
  - Pete mide 1,79 m;
  - el refri es de tamaño normal;
  - las torres de la central miden ~150 m.

### Modelos
- **Animales y objetos:** escaneos 3D reales con licencia **CC-BY** (Objaverse/Sketchfab, se buscan con `buscar-objaverse.yml`; crédito en la descripción **y** en el primer comentario). La rana del Ep. 5 es un escaneo de una rana de verdad.
- **Personas:** personajes **Mixamo "With Skin"** (Pete: obrero con casco, chaleco, ropa con barro). Viven en el Release privado `Personajes` del repo `nadieteexplica/assets`, nunca en el público, y los workflows los bajan con `assets.txt` (`privados PETE*`, `pose *happy*idle*.fbx`).
  - Al importar hay que borrar su acción (`animation_data_clear`), si no sale en T.
  - **Pete actúa cada frase en que sale** (puerta 6 del v3: "como estatua" bajaba animación a 7).
    - Se usan los gestos de Mixamo del repo privado (`priv_assets/mixamo`: Pointing, Shrugging, Surprised, Head_Nod_Yes, Relieved_Sigh, Thinking, Talking…), con `gestos mixamo` en `assets.txt` → `GESTOS`.
    - En la escena, `gesto(P, "Pointing")` y `pose_pete(..., actua=("Pointing", cuadro_inicio, adelanto))`.
    - Al flotar va una capa encima del idle: brazos abiertos con vaivén, rodillas que se mueven y la punta de los pies hacia abajo.
- **Nada del protagonista de MakeHuman.**

### Materiales (todos procedurales, en `studio/episodios/ep05-iman-rana/escena/ep05.py`)
**Regla: todo sucio.** Lo liso y parejo delata la maqueta (lección 85).
- `mat_chorreado` y `mat_acero_industrial`: chorreados verticales de lluvia y mugre, óxido, rayas y rugosidad irregular. Es el material de las superficies grandes: el imán y las torres.
- `mat_metal_cepillado`, `mat_cobre`, `mat_concreto`, `mat_cable` (mate, con polvo; no refleja el cielo).
- `mat_sal`: costra en polígonos con bordes levantados y manchas grandes.
- `mat_lejano`: dos rocas, quebradas y bruma de distancia.
- `mat_acrilico`: vidrio delgado con fresnel, **huellas y polvo**.
- `tejido` (adentro del cuerpo): subsuperficie variable, venitas y brillo húmedo.
- `mat_vapor`: un volumen con brillo propio y una pluma distinta para cada objeto.

### Luz y color
- **Cielo físico** (`cielo_atardecer`: dispersión múltiple, sol con disco), con el **sol bajo (2,5–5°)** y **de costado o a contraluz**. Nunca cenital ni parejo.
- **Poca luz de cielo** (fuerza 0,12–0,35) y exposición −0,2 a −0,5 para que haya **negros de verdad** (percentil 5 ≤ ~25).
- AgX "Medium High Contrast" + `grado.py` (el mismo grado en los cuadros y en el video).
- Un rebote suave del lado de la cámara para leer las caras, **invisible en los reflejos** (`visible_glossy = False`).
- **El sol nunca de frente:** su brillo en la sal se vuelve una mancha detrás del sujeto.

### Cámara
- Lentes de 35–100 mm.
- Macro a f/8, con el **foco en la cabeza o el ojo**, no en el centro del cuerpo.
- **Macro al atardecer:** la cámara un poco más arriba que el sujeto (7,5 cm a 22 cm de distancia). Así el fondo es **la sal a contraluz (azul)** y no el horizonte quemado.
- **Lo que flota se recorta contra el fondo lejano o el cielo.** Si sus pies quedan contra el suelo lejano, parece parado lejos (lección 86).
- **Una línea en el suelo** (cables, caminos) que apunta al centro del cuadro se lee como una aleta vertical: correr el punto de fuga a un lado (lección 87).
- Lo que nombra la voz **tiene que verse**: revisar oclusiones en los paneos (lección 90).
- Cara u ojos sobre la franja de subtítulos (y < 1000) y bajo y = 1250.

### Explicación: capas estilizadas encima del mundo real
- **Entrar a lo que se explica** (como en el Ep. 4): la cámara se acerca a la rana y corta al agua de adentro.
  - Las moléculas de H₂O con su ángulo real.
  - Las líneas del campo, que brillan y suben desde abajo.
  - Una flecha naranja por cada molécula ("el empujoncito").
- **Píldoras** con *pop*, sólo cuando la voz lo dice: SIN HILOS, EN EL AIRE (desde el cuadro 0), IMÁN, AGUA, UN POQUITO, MILES DE VECES, ≈ 40 TESLAS, ≈ 1 GIGAVATIO, 1 REACTOR NUCLEAR.
- **Flechas de fuerza** junto al sujeto (GRAVEDAD gris hacia abajo, IMÁN naranja que crece hasta ganarle).
- **SIMULACIÓN:** píldora amarilla fija arriba a la izquierda mientras dura lo hipotético.
- Estas capas **no bajan el realismo** (`estilos.md`).

### Edición (`post.py`, `audio.py` del Ep. 5)
- **Subtítulos** palabra a palabra en la franja y 1000–1250. Las palabras clave van en color (AGUA azul; TESLAS y GIGAVATIO naranjos) y los números en cifra ("40").
- **Cada 1–2 s cambia algo:** un corte, una píldora, un movimiento de cámara.
- **Audio:**
  - Música sintetizada (pads en Re/Si m/Sol/La a 84 bpm), con la voz 15 dB arriba y todo a −14 LUFS.
  - Efectos sintetizados: viento, zumbido del imán, *dings*, golpes metálicos, zumbido eléctrico, *whoom*.
- **Loop:** el último plano termina en la cámara exacta del cuadro 0.

### Guion
- **Dato real + "¿y si…?" hipotético con números reales**, contado paso a paso y siempre en condicional ("haría falta", "gastaría", "flotarías"), con SIMULACIÓN en pantalla. Es lo que pidió Tomás: "no es desinformar".
- **Sin nombres, años ni premios en la voz.** Van en el texto del post, la descripción y el primer comentario (la anécdota del Ig Nobel + Nobel fue al post).
- **Gancho que se entiende sin sonido:** una imagen imposible y real desde el cuadro 0, con su píldora.
- **El relato (v3 del Ep. 5, pedido de Tomás del 23-oct 21:20):**
  - **La promesa sobre el espectador va en la primera frase** ("Tu cuerpo repele los imanes. Con el imán correcto, podrías flotar"), con la imagen de esa promesa en el cuadro 0 (Pete flotando, con SIMULACIÓN).
  - **La prueba real va justo después** (la rana a los 4 s, con ESTO SÍ PASÓ) y la mecánica en 2 frases como máximo.
  - **Lo que más le gusta a la gente se cuenta en pasos** ("Primero… Después… Y al final…"), cada uno con su píldora PASO N y su número de fuente.
  - **Nada de comparaciones que no empujen la idea central:** el refri del v2 "no es interesante y se pierde".
  - El v2 contaba primero el experimento y el "¿y tú?" llegaba al segundo 25: "mucho chamullo" (lección 96).
- **Medidas a escala:** se dibujan con la proyección real de la escena (`pantalla()`): la cota va de pared a pared, fuera del personaje, y una mano adulta se dibuja a escala al lado del hueco de 3 cm.

---

## 2. Cómo se produce (orden y tiempos medidos)

**Partir del kit del Ep. 5:** copiar `escena/` (`ep05.py` = kit realista, `planos_ep05.py`, `plano.py`, `post.py`, `audio.py`, `reparto.py`, `grado.py`, `estilo_*.py`, `ficha.py`, `comparar.py`) y cambiar sólo lo de la idea. No construir materiales, cielo ni salar desde cero.

1. **Guion → voz → storyboard** como siempre (puertas 1–3). En la ficha de cada plano realista se escribe:
   - qué hay detrás de lo que flota;
   - dónde está el sol respecto de la cámara;
   - el micro-movimiento de lo vivo.
2. **Cuadros de estilo** (`estilos.yml`, 1080×1920, 64 muestras; A ~5–17 min, B ~5 min, C ~10 min en paralelo):
   - Antes de la puerta 4 se revisan **recortes a resolución completa** del fondo y del sujeto; en la miniatura no se ven los cerros flotando ni el vapor cortado (lección 89).
   - `comparar.py` arma la hoja con el Ep. 4 y fotos reales (las fotos son de otros: quedan fuera del repo).
   - Puerta 4 con recortes: el auditor llena `delatores` con **todo** lo que delata la maqueta, y se arregla todo de una vez.
3. **Muestras (no animatic):**
   - `render-planos.yml` con `muestras=3` y 540×960 (~10 min) → chequeo automático (`chequeo.txt`) + revisión propia de la hoja: fondos lavados, sol de frente, sujeto en la franja, oclusiones, Pete al borde.
   - En realista el animatic completo cuesta casi lo mismo que el final (50 contra 60 min) y los problemas que encontró eran de composición, visibles en cuadros sueltos.
4. **Render final** (`render-planos.yml`, 720×1280, 8 muestras, 16 máquinas, ~60 min): `reparto.py` con pesos medidos (E1 de cerca 24 s/cuadro, interior 26, E3 15, E4 19, E5 17 a 540/8) y piezas partidas desde 45 cuadros.
5. **Puerta 6 sobre el final** (`auditar.py preparar <ep> animatic` con el MP4 final) + **puerta 7** sobre el mismo render. Lo que haya que arreglar se parcha por plano (`piezas` + `base_run`).
   - **Si el armado se cuelga** (apt-get, 23-oct), `armar.yml` arma el video desde los cuadros ya hechos sin re-renderizar.
6. **Paquete** (puerta 8) → mensaje a Tomás → con su OK, `release.yml` y Metricool (`isAiGeneratedContent: true` en YouTube).

**Tiempo realista esperado con el kit:** ~4 h (cuadros 1–1,5 h, muestras 15 min, final 1 h, puertas 45 min). El Ep. 5 tomó ~9 h porque armó el kit desde cero, necesitó 3 rondas de realismo y GitHub se colgó tres veces armando el video. **Con este estilo no se llega a "diario ≤ 2,5 h"** salvo reutilizando un set entero (sin cuadros de estilo).

---

## 3. Lo que faltó en el Ep. 5 (para hacerlo mejor en el próximo)
Lo marcó la puerta 6. La animación se quedó en 7 y el gancho también.
- **Vida:**
  - La rana casi no se movía. Hay que darle respiración (la garganta), un parpadeo y patas que derivan despacio.
  - Pete flotaba tieso. Debe usar una animación de Mixamo en loop (no una pose fija), con brazos que buscan equilibrio.
  - Regla: **lo vivo nunca está quieto más de 1 s**.
- **Física bien mostrada:** lo que flota en un imán flota **dentro del hueco** (como la rana en el tubo), no 1 m sobre la tapa.
- **Construcciones:** las piezas no aparecen en el aire; entran desde fuera de cuadro o suben desde el suelo. Ningún objeto de negro puro sin material (el tubo interior del imán).
- **Cables:** con volumen y sombra corta (a ras se veían como cuchillas).
- **Gancho:** la píldora EN EL AIRE desde el cuadro 0 resolvió "parece un acuario". El próximo cuadro 0 tiene que leerse **sin texto**, con algo que muestre aire alrededor (el borde del tubo arriba, una gota que cae).

---

## 4. Lista "señales de maqueta" (revisarla antes de mostrar un cuadro; el auditor usa la misma)
1. **Luz:** ¿sol bajo y de costado, negros de verdad (p5 ≤ ~25), sombras de contacto?
2. **Superficies grandes:** ¿tienen chorreados, mugre, rayas? Nada liso ni de un solo color.
3. **Fondo lejano:** ¿formas grandes con bruma, tocando el suelo? Nada "de greda" ni flotando.
4. **Repeticiones:** ¿dos plumas, cerros o pernos idénticos? Varían.
5. **Lo que flota a propósito:** ¿se recorta contra el fondo lejano o el cielo, con aire visible bajo él?
6. **Lo que no debe flotar:** cerros, vapor, cables, piezas. ¿Todo toca su base?
7. **Líneas al punto de fuga del centro:** ¿parecen una aleta?
8. **Sol o reflejos:** ¿alguna mancha detrás del sujeto? ¿Se ve la luz de relleno reflejada?
9. **Escala:** ¿todo mide lo que mide en la vida real?
10. **Vida:** ¿lo vivo se mueve?
