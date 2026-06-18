from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
import os
from transformers import pipeline
from PIL import Image
import torch
import io

router = APIRouter()

_image_classifier = None
_object_detector = None


def get_image_classifier():
    global _image_classifier
    if _image_classifier is None:
        cache_dir = os.getenv("MODEL_CACHE_DIR", "./model_cache")
        hf_token = os.getenv("HUGGINGFACE_TOKEN")
        _image_classifier = pipeline(
            "image-classification",
            model="google/vit-base-patch16-224",
            cache_dir=cache_dir,
            token=hf_token,
            device=0 if torch.cuda.is_available() else -1,
        )
    return _image_classifier


def get_zero_shot_image_classifier():
    global _object_detector
    if _object_detector is None:
        cache_dir = os.getenv("MODEL_CACHE_DIR", "./model_cache")
        hf_token = os.getenv("HUGGINGFACE_TOKEN")
        _object_detector = pipeline(
            "zero-shot-image-classification",
            model="openai/clip-vit-base-patch32",
            cache_dir=cache_dir,
            token=hf_token,
            device=0 if torch.cuda.is_available() else -1,
        )
    return _object_detector


class ImageClassifyResult(BaseModel):
    label: str
    score: float


class ImageClassifyResponse(BaseModel):
    filename: str
    results: List[ImageClassifyResult]
    top_label: str
    mode: str


DOMAIN_IMAGE_LABELS = {
    "health": [
        "Röntgenbild", "CT-Scan", "MRT-Aufnahme", "Ultraschall",
        "Hautbefund", "Wunde", "Medikament", "Labor-Probe"
    ],
    "ecommerce": [
        "Kleidung", "Elektronik", "Möbel", "Lebensmittel",
        "Spielzeug", "Sport", "Schmuck", "Buch"
    ],
    "education": [
        "Diagramm", "Formel", "Karte", "Grafik",
        "Tabelle", "Text-Dokument", "Bild", "Schema"
    ],
    "general": None,
}


@router.post("/", response_model=ImageClassifyResponse)
async def classify_image(
    file: UploadFile = File(...),
    domain: str = Form("general"),
    custom_labels: Optional[str] = Form(None),
):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")

        labels_list = None
        if custom_labels:
            labels_list = [l.strip() for l in custom_labels.split(",") if l.strip()]
        else:
            labels_list = DOMAIN_IMAGE_LABELS.get(domain)

        if labels_list:
            classifier = get_zero_shot_image_classifier()
            result = classifier(image, candidate_labels=labels_list)
            results = [
                ImageClassifyResult(label=r["label"], score=round(r["score"], 4))
                for r in result
            ]
            mode = "zero-shot"
        else:
            classifier = get_image_classifier()
            result = classifier(image, top_k=5)
            results = [
                ImageClassifyResult(label=r["label"], score=round(r["score"], 4))
                for r in result
            ]
            mode = "imagenet"

        return ImageClassifyResponse(
            filename=file.filename,
            results=results,
            top_label=results[0].label if results else "",
            mode=mode,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
