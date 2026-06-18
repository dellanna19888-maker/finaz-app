from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
import json

router = APIRouter()


class ModelInfo(BaseModel):
    model_id: str
    name: str
    task: str
    domain: str
    source: str
    local_path: Optional[str] = None


def _get_local_models() -> List[dict]:
    output_dir = os.getenv("TRAINING_OUTPUT_DIR", "./training_output")
    models = []
    if not os.path.exists(output_dir):
        return models
    for job_id in os.listdir(output_dir):
        job_path = os.path.join(output_dir, job_id)
        if not os.path.isdir(job_path):
            continue
        config_path = os.path.join(job_path, "config.json")
        if os.path.exists(config_path):
            with open(config_path) as f:
                cfg = json.load(f)
            models.append({
                "model_id": job_id,
                "name": cfg.get("_name_or_path", job_id),
                "task": "text-classification",
                "source": "lokal",
                "local_path": job_path,
            })
    return models


@router.get("/")
def list_models():
    pretrained = [
        {
            "model_id": "cross-encoder/nli-MiniLM2-L6-H768",
            "name": "Zero-Shot Klassifikator",
            "task": "text-classification",
            "domain": "allgemein",
            "source": "huggingface",
        },
        {
            "model_id": "google/vit-base-patch16-224",
            "name": "Vision Transformer",
            "task": "image-classification",
            "domain": "allgemein",
            "source": "huggingface",
        },
        {
            "model_id": "openai/clip-vit-base-patch32",
            "name": "CLIP (Zero-Shot Bilder)",
            "task": "image-classification",
            "domain": "allgemein",
            "source": "huggingface",
        },
        {
            "model_id": "facebook/bart-large-cnn",
            "name": "BART Zusammenfassung",
            "task": "summarization",
            "domain": "allgemein",
            "source": "huggingface",
        },
        {
            "model_id": "deepset/roberta-base-squad2",
            "name": "RoBERTa Frage-Antwort",
            "task": "question-answering",
            "domain": "allgemein",
            "source": "huggingface",
        },
    ]
    local = _get_local_models()
    return {"pretrained": pretrained, "custom": local, "total": len(pretrained) + len(local)}


@router.get("/{model_id}")
def get_model_info(model_id: str):
    output_dir = os.getenv("TRAINING_OUTPUT_DIR", "./training_output")
    job_path = os.path.join(output_dir, model_id)
    if os.path.exists(job_path):
        config_path = os.path.join(job_path, "config.json")
        label_path = os.path.join(job_path, "label2id.json")
        info = {"model_id": model_id, "local_path": job_path, "source": "lokal"}
        if os.path.exists(label_path):
            with open(label_path) as f:
                info["labels"] = list(json.load(f).keys())
        return info
    raise HTTPException(status_code=404, detail="Modell nicht gefunden")
