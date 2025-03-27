from contextlib import asynccontextmanager
import whisper
from transformers import AutoTokenizer, AutoModel
from fastapi import FastAPI, Body

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application...")

    # Загружаем модель при запуске приложения
    print("Whisper loading...")
    model = whisper.load_model("small")
    print("Whisper loaded.")
    print("e5 loading...")
    app.state.tokenizer = AutoTokenizer.from_pretrained('deepfile/multilingual-e5-small-onnx-qint8')
    app.state.pretrained = AutoModel.from_pretrained('deepfile/multilingual-e5-small-onnx-qint8')
    app.state.pretrained_name = "multilingual-e5-small-onnx-qint8"
    print("e5 loaded.")
    #
    # # Добавляем модель в состояние приложения (app.state) для последующего использования
    app.state.whisper_model = model

    yield


    print("Shutting down application...")
    app.state.model = None