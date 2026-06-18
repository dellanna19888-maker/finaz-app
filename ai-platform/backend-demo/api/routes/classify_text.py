from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from hf_client import hf_post

router = APIRouter()

# Zero-shot classification — works without training data
ZS_MODEL = "facebook/bart-large-mnli"

DOMAIN_LABELS = {
    "health":    ["Diagnose", "Symptome", "Medikamente", "Labor-Ergebnisse", "Behandlungsplan", "Anamnese"],
    "ecommerce": ["Produktbeschreibung", "Positive Bewertung", "Negative Bewertung", "Reklamation", "Bestellung"],
    "education": ["Mathematik", "Naturwissenschaften", "Geschichte", "Sprachen", "Informatik", "Hausaufgaben"],
    "general":   ["Positiv", "Negativ", "Neutral", "Frage", "Aussage", "Beschwerde"],
}


class TextClassifyRequest(BaseModel):
    text: str
    labels: Optional[List[str]] = None
    domain: Optional[str] = "general"
    multi_label: Optional[bool] = False


@router.post("/")
async def classify(req: TextClassifyRequest):
    labels = req.labels or DOMAIN_LABELS.get(req.domain, DOMAIN_LABELS["general"])

    result = await hf_post(
        ZS_MODEL,
        {"inputs": req.text, "parameters": {"candidate_labels": labels, "multi_label": req.multi_label}},
    )

    results = [
        {"label": l, "score": round(s, 4)}
        for l, s in zip(result["labels"], result["scores"])
    ]
    return {
        "text": req.text,
        "results": results,
        "top_label": results[0]["label"] if results else "",
        "domain": req.domain,
    }


@router.post("/sentiment")
async def sentiment(text: str):
    result = await hf_post(
        "cardiffnlp/twitter-roberta-base-sentiment-latest",
        {"inputs": text[:512]},
    )
    top = result[0] if isinstance(result, list) else result
    label_map = {"positive": "Positiv 😊", "negative": "Negativ 😟", "neutral": "Neutral 😐"}
    label = label_map.get(top["label"].lower(), top["label"])
    return {"text": text, "sentiment": label, "score": round(top["score"], 4)}


@router.get("/labels/{domain}")
def labels(domain: str):
    return {"domain": domain, "labels": DOMAIN_LABELS.get(domain, DOMAIN_LABELS["general"])}
