Haz el Ep. 6 de El viejo del dato: **¿por qué el cinturón de seguridad se traba cuando tiras rápido o cuando el auto frena fuerte?** Línea datos, YouTube primero, 25–40 s. Carpeta: `studio/episodios/ep06-cinturon/`.

**Look: el mismo realista del Ep. 5 (el imán y la rana), que es la línea de la cuenta.**
- Lee `docs/ESTILO_REALISTA.md` y parte del kit del Ep. 5 (`studio/episodios/ep05-iman-rana/escena/`). Copia `studio/plantilla/estilo_realista.json` como `estilo.json`.
- Mundo abierto a escala real, sol bajo de costado, materiales sucios y lente real.
- Entra a lo que se explica con capas encima (moléculas, flechas, píldoras), como cuando la cámara se metió en la rana y en la cortina.

**Material nuevo: `docs/BIBLIOTECA.md`.**
- **Carretera:** texturas `asphalt_04`/`asphalt_05` y cielos de autopista (`derelict_highway_*`, `nowhere_road`, `skidpan`) de Poly Haven, y líneas de pista `RoadLines*` de ambientCG. Búscalos y bájalos con `tools/biblioteca.py`.
- **Auto:** no hay en CC0. Búscalo con `buscar-objaverse.yml` (CC0 o CC-BY, crédito abajo), sin marca ni logo; si trae uno, se borra.
- **Personas:** del Release privado `Personajes` (`assets.txt` → `privados DUMMY*`).
  - **Dummy** (maniquí de choque): el que va en el frenazo.
  - Lewis, Megan u otro: el que tira el cinturón.
- **Movimientos:** los que haya en `Personajes` y en la carpeta `mixamo/`. Quaternius CC0 (prerelease `biblioteca`) trae `Driving_Loop` y `Sitting_Idle_Loop`. Si falta uno, pídele a Tomás el nombre exacto en Mixamo.

**Qué hay que mostrar** (el chat de ideas ya juntó fuentes en `studio/caza/ronda06.md`: parte de ahí; verifica todo con 2 fuentes, y si cambia según el auto, dilo):
- **El carrete por dentro**, en corte, con estos dos frenos:
  - **Frenazo:** un sensor de inercia (una bolita o un péndulo) se va hacia adelante y empuja una uña contra un engranaje del carrete.
  - **Tirón rápido:** el carrete gira tan rápido que unos contrapesos se abren hacia afuera y lo traban. Por eso si tiras despacio, sale.
- **Choque de verdad, si las fuentes lo sostienen:** el pretensor recoge el cinturón en una fracción de segundo.
- **Enseñanza:** si se te traba, suéltalo un poco y tira despacio.

**Ideas de escenas (máx. 6):**
1. Auto en una carretera abierta al atardecer y el frenazo, con el Dummy.
2. La cámara entra al carrete, que se ve en corte.
3. Tirón rápido contra tirón lento, en primer plano.
4. Macro de la bolita o el péndulo.

Para el frenazo puedes probar "El reloj" (`docs/REFERENCIAS.md` §5): el mundo se congela en el frenazo, el cronómetro avanza a saltos mientras se explica y al final todo pasa en un parpadeo. Úsalo si calza.

**Ojo:**
- Las manos que tiran el cinturón son el plano difícil (lección 2: los dedos no tocan bien). Resuélvelo en el storyboard, por ejemplo con una mano fija a la cinta o con el tirón visto desde el carrete.
- Nada de heridos: el Dummy hace de persona.
- No se narran estudios ni nombres; las fuentes van abajo.
- Proceso v2 con el auditor y su tope de horas (`docs/AUTOMATIZACION.md`).
