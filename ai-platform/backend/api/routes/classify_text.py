from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
from transformers import pipeline
import torch

router = APIRouter()

_classifier = None
_custom_classifier = None


def get_zero_shot_classifier():
    global _classifier
    if _classifier is None:
        model_name = "cross-encoder/nli-MiniLM2-L6-H768"
        cache_dir = os.getenv("MODEL_CACHE_DIR", "./model_cache")
        hf_token = os.getenv("HUGGINGFACE_TOKEN")
        _classifier = pipeline(
            "zero-shot-classification",
            model=model_name,
            cache_dir=cache_dir,
            token=hf_token,
            device=0 if torch.cuda.is_available() else -1,
        )
    return _classifier


class TextClassifyRequest(BaseModel):
    text: str
    labels: Optional[List[str]] = None
    domain: Optional[str] = "general"
    multi_label: Optional[bool] = False


class ClassifyResult(BaseModel):
    label: str
    score: float


class TextClassifyResponse(BaseModel):
    text: str
    results: List[ClassifyResult]
    top_label: str
    domain: str


DOMAIN_LABELS = {
    "health": [
        "Diagnose", "Symptome", "Medikamente", "Labor-Ergebnisse",
        "Behandlungsplan", "Anamnese", "Befund", "Überweisung"
    ],
    "ecommerce": [
        "Produktbeschreibung", "Kundenbewertung positiv", "Kundenbewertung negativ",
        "Bestellung", "Reklamation", "Produktanfrage", "Versand", "Rückgabe"
    ],
    "education": [
        "Mathematik", "Naturwissenschaften", "Geschichte", "Sprachen",
        "Informatik", "Hausaufgaben", "Prüfungsvorbereitung", "Erklärung"
    ],
    "general": [
        "Positiv", "Negativ", "Neutral", "Frage", "Aussage", "Beschwerde", "Lob"
    ],
}


@router.post("/", response_model=TextClassifyResponse)
async def classify_text(request: TextClassifyRequest):
    try:
        labels = request.labels or DOMAIN_LABELS.get(request.domain, DOMAIN_LABELS["general"])
        classifier = get_zero_shot_classifier()
        result = classifier(
            request.text,
            candidate_labels=labels,
            multi_label=request.multi_label,
        )
        results = [
            ClassifyResult(label=l, score=round(s, 4))
            for l, s in zip(result["labels"], result["scores"])
        ]
        return TextClassifyResponse(
            text=request.text,
            results=results,
            top_label=results[0].label if results else "",
            domain=request.domain,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/labels/{domain}")
def get_domain_labels(domain: str):
    labels = DOMAIN_LABELS.get(domain, DOMAIN_LABELS["general"])
    return {"domain": domain, "labels": labels}


@router.post("/sentiment")
async def analyze_sentiment(text: str):
    try:
        pipe = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-xlm-roberta-base-sentiment",
            cache_dir=os.getenv("MODEL_CACHE_DIR", "./model_cache"),
            device=0 if torch.cuda.is_available() else -1,
        )
        result = pipe(text[:512])
        return {"text": text, "sentiment": result[0]["label"], "score": round(result[0]["score"], 4)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
