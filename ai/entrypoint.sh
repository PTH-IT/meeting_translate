#!/bin/sh
set -e

mkdir -p /app/models/whisperx /app/models/huggingface /app/models/torch

if [ ! -f /app/models/whisperx/.whisper-model-downloaded ]; then
  echo "Preloading Whisper model into shared cache..."
  python - <<'PY'
import os
from faster_whisper import WhisperModel
cache_dir = os.environ.get('WHISPER_CACHE_DIR', '/app/models/whisperx')
model_name = os.environ.get('WHISPER_MODEL', 'base')
WhisperModel(model_name, device='cpu', compute_type='int8', download_root=cache_dir)
open(os.path.join(cache_dir, '.whisper-model-downloaded'), 'w', encoding='utf-8').write('done')
print(f'Whisper model {model_name} cached at {cache_dir}')
PY
else
  echo "Whisper model cache already present"
fi

exec "$@"
