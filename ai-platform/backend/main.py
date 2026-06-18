from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

load_dotenv()

from api.routes import chat, classify_text, classify_image, documents, training, models

app = FastAPI(
    title="KI-Plattform API",
    description="Eigene KI-Plattform — Chat, Klassifikation, Bilderkennung, Dokumentenanalyse",
    version="1.0.0",
)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(classify_text.router, prefix="/api/classify/text", tags=["Text-Klassifikation"])
app.include_router(classify_image.router, prefix="/api/classify/image", tags=["Bild-Erkennung"])
app.include_router(documents.router, prefix="/api/documents", tags=["Dokumente"])
app.include_router(training.router, prefix="/api/training", tags=["Training"])
app.include_router(models.router, prefix="/api/models", tags=["Modelle"])

uploads_dir = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


@app.get("/")
def root():
    return {"status": "ok", "message": "KI-Plattform läuft"}


@app.get("/health")
def health():
    return {"status": "healthy"}
