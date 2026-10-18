# studio — render de videos (three.js + Playwright)

Para poner a punto el entorno:

```bash
cd studio && npm ci                         # three + fuentes
python3 -m http.server 8765 --bind 127.0.0.1   # servir desde studio/ (déjalo corriendo)
```

Necesitas Playwright con Chromium. En el espacio de trabajo de Claude ya viene en `/opt/pw-browsers`; no hay que correr `playwright install`.

## Probar unos cuadros

```bash
python3 capture.py muestras/a.html /tmp/test --times 0.5,3.0,4.2 1
```

## Render completo y armado del video

```bash
python3 capture.py <pagina>.html <dir>/frames 0 <n_frames> 30 1
bash mux.sh <dir> salida.mp4                # usa <dir>/frames y <dir>/audio.wav
```

## Cómo está hecha cada página

- Cada página expone `window.renderAt(t)` y marca `window.READY = true` cuando terminó de cargar.
- Todo es determinista: una semilla fija (mulberry32) y la animación calculada en función de `t`.
- `episodios/epNN-slug/` contiene un episodio cada uno (guion, storyboard, words.json, escena, audio, entrega).
- `muestras/` contiene las 3 muestras de estilo (A/B/C) del gancho del Ep. 1.
  - `main.js` es común a las tres; el estilo sale de `window.STYLE`.
  - `sound.py` arma el audio de las muestras: voz, efectos y ukelele sintetizado.
- En el estilo C (plastilina) se renderiza a 12 fps para que parezca stop-motion. Después se pasa a 30 fps al codificar.
- Rendimiento en el espacio de trabajo (2 núcleos, SwiftShader): unos 4–8 s por cuadro según el estilo. Por eso conviene mover el render a GitHub Actions.
