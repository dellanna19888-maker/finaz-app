from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import os, uuid, aiofiles
from hf_client import hf_post

router = APIRouter()

SUMMARY_MODEL = "facebook/bart-large-cnn"
QA_MODEL      = "deepset/roberta-base-squad2"

_docs: dict = {}


def _extract_text(path: str, filename: str) -> str:
    ext = filename.lower().rsplit(".", 1)[-1]
    if ext == "txt":
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read()
    elif ext == "pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(path)
            return "\n".join(p.extract_text() or "" for p in reader.pages)
        except Exception as e:
            raise HTTPException(400, f"PDF-Fehler: {e}")
    raise HTTPException(400, f"Format .{ext} nicht unterstützt (nur txt, pdf)")


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    ext = file.filename.lower().rsplit(".", 1)[-1]
    if ext not in {"txt", "pdf"}:
        raise HTTPException(400, "Nur .txt und .pdf erlaubt")

    content = await file.read()
    max_bytes = int(os.getenv("MAX_UPLOAD_SIZE_MB", 20)) * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(413, "Datei zu groß")

    upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
    os.makedirs(upload_dir, exist_ok=True)
    doc_id = str(uuid.uuid4())
    path = os.path.join(upload_dir, f"{doc_id}.{ext}")
    async with aiofiles.open(path, "wb") as f:
        await f.write(content)

    text = _extract_text(path, file.filename)
    _docs[doc_id] = {"text": text, "filename": file.filename}

    return {
        "document_id": doc_id,
        "filename": file.filename,
        "size_bytes": len(content),
        "word_count": len(text.split()),
        "char_count": len(text),
    }


@router.post("/summarize/{doc_id}")
async def summarize(doc_id: str):
    if doc_id not in _docs:
        raise HTTPException(404, "Dokument nicht gefunden")
    text = _docs[doc_id]["text"]

    # Send in chunks of 1000 chars (BART handles up to ~1024 tokens)
    chunk = text[:1000]
    result = await hf_post(
        SUMMARY_MODEL,
        {"inputs": chunk, "parameters": {"max_length": 150, "min_length": 30}},
    )
    summary = result[0]["summary_text"] if isinstance(result, list) else str(result)

    return {
        "filename": _docs[doc_id]["filename"],
        "summary": summary,
        "word_count": len(text.split()),
        "char_count": len(text),
    }


class QARequest(BaseModel):
    document_id: str
    question: str


@router.post("/qa")
async def qa(req: QARequest):
    if req.document_id not in _docs:
        raise HTTPException(404, "Dokument nicht gefunden")
    context = _docs[req.document_id]["text"][:3000]

    result = await hf_post(
        QA_MODEL,
        {"inputs": {"question": req.question, "context": context}},
    )
    return {
        "question": req.question,
        "answer": result.get("answer", "Keine Antwort gefunden"),
        "confidence": round(result.get("score", 0), 4),
    }
