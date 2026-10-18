# reels-ia

Fábrica de Reels de curiosidades en 3D para **Nadie te explica** (Instagram, TikTok, YouTube Shorts).

- `jobs/voz/` — trabajos de voz (ElevenLabs). Al subir un `.json` acá, GitHub Actions genera la voz y guarda el resultado en `out/`.
- `tools/` — scripts del pipeline.
- `out/` — resultados generados automáticamente (no editar a mano).

La clave de ElevenLabs vive solo en los secretos del repo (`ELEVENLABS_API_KEY`).
