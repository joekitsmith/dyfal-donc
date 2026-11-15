# tts

The speech service. It speaks the course's English and Welsh with [Piper](https://github.com/OHF-Voice/piper1-gpl) (GPL-3.0, which is why it runs as its own service and the API only talks to it over HTTP). Nothing else in the repository imports it, and a boundary test checks that.

`POST /synthesise` takes `{text, track}` and returns a WAV file. A track is `english`, `welsh` (a woman) or `welsh-slow` (a man). `voices.py` says how each is spoken, and `pace.py` how a Welsh phrase is stretched so every phrase has the same pace.

The voice files are downloaded when the image is built (`Dockerfile`), pinned to a revision and a checksum.

```
make tts-build   # build the image
make tts-up      # run it on localhost:8001 (TTS_PORT), for `poe api`
make stack-up    # or run it with the API and Postgres
```

It is published to localhost only, for development. The API is what clients call: `GET /exercises/{exercise_id}/audio/{track}`.
