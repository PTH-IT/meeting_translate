FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
COPY ai/requirements.txt .
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt
COPY ai/main.py ai/
COPY ai/models/ ai/models/
COPY ai/pipelines/ ai/pipelines/
COPY ai/loaders/ ai/loaders/
COPY ai/preprocess/ ai/preprocess/
COPY ai/postprocess/ ai/postprocess/
COPY ai/inference/ ai/inference/
COPY ai/utils/ ai/utils/
COPY ai/__init__.py ai/__init__.py

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "ai.main:app", "--host", "0.0.0.0", "--port", "8000"]
