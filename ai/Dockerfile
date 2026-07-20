FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/app/models/huggingface \
    TRANSFORMERS_CACHE=/app/models/huggingface/transformers \
    TORCH_HOME=/app/models/torch \
    WHISPER_CACHE_DIR=/app/models/whisperx \
    WHISPER_MODEL=base \
    CUDA_AVAILABLE=false

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    pkg-config \
    build-essential \
    python3-dev \
    libavformat-dev \
    libavcodec-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    libavdevice-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY ai/requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip \
    && pip install --prefer-binary -r requirements.txt

# glibc 2.41 rejects .so files flagged with an executable stack (ctranslate2's
# libctranslate2-*.so), causing "cannot enable executable stack ... Invalid argument".
# Clear the flag so the library loads inside the container.
RUN apt-get update && apt-get install -y --no-install-recommends patchelf \
    && find /usr/local/lib/python3.11/site-packages/ctranslate2 -name 'libctranslate2-*.so*' -exec patchelf --clear-execstack {} + \
    && find /usr/local/lib/python3.11/site-packages/ctranslate2.libs -name 'libctranslate2-*.so*' -exec patchelf --clear-execstack {} + \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/models/whisperx /app/models/huggingface /app/models/torch \
    && python - <<'PY'
import os
from faster_whisper import WhisperModel
cache_dir = os.environ['WHISPER_CACHE_DIR']
model_name = os.environ['WHISPER_MODEL']
print(f'Preloading Whisper model {model_name} into {cache_dir}')
WhisperModel(model_name, device='cpu', compute_type='int8', download_root=cache_dir)
print('Whisper model preload completed')
PY

COPY ai/ ./ai/

RUN chmod +x /app/ai/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/ai/entrypoint.sh"]
CMD ["python", "-m", "uvicorn", "ai.main:app", "--host", "0.0.0.0", "--port", "8000"]
