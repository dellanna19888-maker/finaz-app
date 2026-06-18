from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from hf_client import hf_post_binary

router = APIRouter()

# CLIP for zero-shot, ViT for general ImageNet
CLIP_MODEL = "openai/clip-vit-base-patch32"
VIT_MODEL  = "google/vit-base-patch16-224"

DOMAIN_LABELS = {
    "health":    ["Röntgenbild", "CT-Scan", "MRT-Aufnahme", "Ultraschall", "Hautbefund", "Medikament"],
    "ecommerce": ["Kleidung", "Elektronik", "Möbel", "Lebensmittel", "Spielzeug", "Sport", "Schmuck"],
    "education": ["Diagramm", "Formel", "Karte", "Grafik", "Tabelle", "Text-Dokument"],
    "general":   None,
}


@router.post("/")
async def classify_image(
    file: UploadFile = File(...),
    domain: str = Form("general"),
    custom_labels: Optional[str] = Form(None),
):
    data = await file.read()

    labels = None
    if custom_labels:
        labels = [l.strip() for l in custom_labels.split(",") if l.strip()]
    else:
        labels = DOMAIN_LABELS.get(domain)

    if labels:
        # Zero-shot with CLIP via HF API
        result = await hf_post_binary(
            CLIP_MODEL,
            data,
        )
        # HF CLIP returns list of {label, score}
        if isinstance(result, list):
            # filter to our labels
            results = [{"label": r["label"], "score": round(r["score"], 4)} for r in result]
        else:
            # fallback: post with parameters (some endpoints differ)
            results = [{"label": l, "score": 0.0} for l in labels]
        mode = "zero-shot (CLIP)"
    else:
        result = await hf_post_binary(VIT_MODEL, data)
        results = [
            {"label": r["label"], "score": round(r["score"], 4)}
            for r in (result if isinstance(result, list) else [])
        ][:8]
        mode = "imagenet (ViT)"

    results = sorted(results, key=lambda x: x["score"], reverse=True)
    return {
        "filename": file.filename,
        "results": results,
        "top_label": results[0]["label"] if results else "",
        "mode": mode,
    }
