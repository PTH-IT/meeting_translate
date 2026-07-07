#!/bin/bash
set -e

# Download models if not present
if [ ! -d "/app/models" ] || [ -z "$(ls -A /app/models)" ]; then
    echo "Downloading models..."
    python -c "
from huggingface_hub import snapshot_download
import os
os.makedirs('/app/models', exist_ok=True)
snapshot_download('facebook/m2m100_418M', cache_dir='/app/models', local_files_only=False)
" || echo "Model download skipped or failed"
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000