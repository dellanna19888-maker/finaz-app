from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
import os
import uuid
import aiofiles
from transformers import pipeline
import torch

router = APIRouter()

_summarizer = None
_qa_pipeline = None


def get_summarizer():
    global _summarizer
    if _summarizer is None:
        cache_dir = os.getenv("MODEL_CACHE_DIR", "./model_cache")
        hf_token = os.getenv("HUGGINGFACE_TOKEN")
        _summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            cache_dir=cache_dir,
            token=hf_token,
            device=0 if torch.cuda.is_available() else -1,
        )
    return _summarizer


def get_qa_pipeline():
    global _qa_pipeline
    if _qa_pipeline is None:
        cache_dir = os.getenv("MODEL_CACHE_DIR", "./model_cache")
        hf_token = os.getenv("HUGGINGFACE_TOKEN")
        _qa_pipeline = pipeline(
            "question-answering",
            model="deepset/roberta-base-squad2",
            cache_dir=cache_dir,
            token=hf_token,
            device=0 if torch.cuda.is_available() else -1,
        )
    return _qa_pipeline


def extract_text_from_file(filepath: str, filename: str) -> str:
    ext = filename.lower().split(".")[-1]
    if ext == "txt":
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    elif ext == "pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(filepath)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"PDF-Fehler: {e}")
    else:
        raise HTTPException(status_code=400, detail=f"Nicht unterstütztes Format: .{ext}")


class DocumentSummaryResponse(BaseModel):
    filename: str
    summary: str
    word_count: int
    char_count: int


class DocumentQARequest(BaseModel):
    document_id: str
    question: str


class DocumentQAResponse(BaseModel):
    question: str
    answer: str
    confidence: float


_uploaded_docs: dict = {}


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    allowed_ext = {"txt", "pdf"}
    ext = file.filename.lower().split(".")[-1]
    if ext not in allowed_ext:
        raise HTTPException(status_code=400, detail="Nur .txt und .pdf erlaubt")

    max_size = int(os.getenv("MAX_UPLOAD_SIZE_MB", 50)) * 1024 * 1024
    upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
    os.makedirs(upload_dir, exist_ok=True)

    doc_id = str(uuid.uuid4())
    filepath = os.path.join(upload_dir, f"{doc_id}.{ext}")

    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(status_code=413, detail="Datei zu groß")

    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)

    text = extract_text_from_file(filepath, file.filename)
    _uploaded_docs[doc_id] = {"text": text, "filename": file.filename, "path": filepath}

    return {
        "document_id": doc_id,
        "filename": file.filename,
        "size_bytes": len(content),
        "word_count": len(text.split()),
        "char_count": len(text),
    }


@router.post("/summarize/{document_id}", response_model=DocumentSummaryResponse)
async def summarize_document(document_id: str):
    if document_id not in _uploaded_docs:
        raise HTTPException(status_code=404, detail="Dokument nicht gefunden")

    doc = _uploaded_docs[document_id]
    text = doc["text"]

    chunks = [text[i:i+1024] for i in range(0, min(len(text), 4096), 1024)]
    summarizer = get_summarizer()
    summaries = []
    for chunk in chunks[:4]:
        if len(chunk.strip()) < 50:
            continue
        result = summarizer(chunk, max_length=150, min_length=30, do_sample=False)
        summaries.append(result[0]["summary_text"])

    combined = " ".join(summaries)
    return DocumentSummaryResponse(
        filename=doc["filename"],
        summary=combined,
        word_count=len(text.split()),
        char_count=len(text),
    )


@router.post("/qa", response_model=DocumentQAResponse)
async def document_qa(request: DocumentQARequest):
    if request.document_id not in _uploaded_docs:
        raise HTTPException(status_code=404, detail="Dokument nicht gefunden")

    doc = _uploaded_docs[request.document_id]
    context = doc["text"][:4000]

    qa = get_qa_pipeline()
    result = qa(question=request.question, context=context)

    return DocumentQAResponse(
        question=request.question,
        answer=result["answer"],
        confidence=round(result["score"], 4),
    )
