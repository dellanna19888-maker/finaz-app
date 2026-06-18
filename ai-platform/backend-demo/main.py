from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os

load_dotenv()

from api.routes import chat, classify_text, classify_image, documents

app = FastAPI(
    title="KI-Plattform Demo API",
    description="Laptop-Demo: nutzt Hugging Face Inference API (keine lokalen Modelle)",
    version="1.0.0-demo",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router,          prefix="/api/chat",           tags=["Chat"])
app.include_router(classify_text.router, prefix="/api/classify/text",  tags=["Text"])
app.include_router(classify_image.router,prefix="/api/classify/image", tags=["Bild"])
app.include_router(documents.router,     prefix="/api/documents",      tags=["Dokumente"])

uploads_dir = os.getenv("UPLOAD_DIR", "./uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


@app.get("/")
def root():
    token_set = bool(os.getenv("HUGGINGFACE_TOKEN"))
    return {
        "status": "ok",
        "mode": "demo (Hugging Face API)",
        "hf_token_set": token_set,
    }


@app.get("/health")
def health():
    return {"status": "healthy", "mode": "demo"}
