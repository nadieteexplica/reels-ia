# reels-ia

Fábrica de videos cortos de curiosidades en 3D para **Nadie te explica** (Instagram, TikTok, YouTube Shorts).

**Empieza por [`CONTEXTO.md`](CONTEXTO.md)**: ahí está todo lo decidido (formato, voz, estilo, pipeline, estado).

- `jobs/voz/` — trabajos de voz (ElevenLabs). Al subir un `.json` acá, GitHub Actions genera la voz y guarda el resultado en `out/`.
- `tools/` — scripts del pipeline.
- `studio/` — render de los videos (three.js + Playwright), muestras de estilo y Ep. 1.
- `docs/` — investigación de formatos y banco de ideas.
- `out/` — resultados generados automáticamente (no editar a mano).

La clave de ElevenLabs vive solo en los secretos del repo (`ELEVENLABS_API_KEY`).
