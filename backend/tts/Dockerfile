FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/backend

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --only tts --no-root

RUN mkdir /models

# The voices, pinned to an exact revision and checked against their SHA-256
ADD --chmod=644 --checksum=sha256:13511d46f195733c36f5e443be34c0c0dcaf3f43c7e0f8ecd9a1808107e44ac9 https://huggingface.co/techiaith/cy_GB-bu_tts/resolve/34a3def7d656f3c73f747fbe32faf4cc09de5a0c/cy_GB-bu_tts.onnx /models/
ADD --chmod=644 --checksum=sha256:d1983d55c964d4733ed01bd35a48f1d8b7996b66e5ec1309b70c73db7b4c3c65 https://huggingface.co/techiaith/cy_GB-bu_tts/resolve/34a3def7d656f3c73f747fbe32faf4cc09de5a0c/cy_GB-bu_tts.onnx.json /models/
ADD --chmod=644 --checksum=sha256:0a309668932205e762801f1efc2736cd4b0120329622adf62be09e56339d3330 https://huggingface.co/rhasspy/piper-voices/resolve/6b9cfaacb4fb2e02a9621227e3c1a48bec9710c3/en/en_GB/alan/medium/en_GB-alan-medium.onnx /models/
ADD --chmod=644 --checksum=sha256:c0f0d124e5895c00e7c03b35dcc8287f319a6998a365b182deb5c8e752ee8c1e https://huggingface.co/rhasspy/piper-voices/resolve/6b9cfaacb4fb2e02a9621227e3c1a48bec9710c3/en/en_GB/alan/medium/en_GB-alan-medium.onnx.json /models/

COPY backend/tts backend/tts

RUN useradd --create-home dyfal
USER dyfal

EXPOSE 8001
CMD ["uvicorn", "tts.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8001"]
