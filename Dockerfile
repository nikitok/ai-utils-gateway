FROM python:3.12-slim

# upgrade dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache

# Pre-download models during build
RUN mkdir -p /app/data && \
    /app/.venv/bin/python -c "\
import os; \
os.environ['XDG_CACHE_HOME'] = '/app/data'; \
os.environ['TRANSFORMERS_CACHE'] = '/app/data/transformers'; \
os.environ['HF_HOME'] = '/app/data/transformers'; \
import whisper; \
from transformers import AutoTokenizer, AutoModel; \
print('Downloading Whisper model...'); \
whisper.load_model('small', download_root='/app/data'); \
print('Downloading embedding model...'); \
model_name = 'deepfile/multilingual-e5-small-onnx-qint8'; \
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir='/app/data/transformers'); \
model = AutoModel.from_pretrained(model_name, cache_dir='/app/data/transformers'); \
model_local_path = '/app/data/transformers/' + model_name.replace('/', '_'); \
os.makedirs(model_local_path, exist_ok=True); \
tokenizer.save_pretrained(model_local_path); \
model.save_pretrained(model_local_path); \
print('Models downloaded successfully!');"

# Run the application.
CMD ["/app/.venv/bin/fastapi", "run", "src/aiutils/main.py", "--port", "80", "--host", "0.0.0.0"]