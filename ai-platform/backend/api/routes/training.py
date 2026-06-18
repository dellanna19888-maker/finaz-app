from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import uuid
import json
import time
import threading

router = APIRouter()

_jobs: Dict[str, dict] = {}


class TrainingConfig(BaseModel):
    job_name: str
    task_type: str
    base_model: str
    num_epochs: Optional[int] = 3
    learning_rate: Optional[float] = 2e-5
    batch_size: Optional[int] = 16
    push_to_hub: Optional[bool] = False
    hub_model_id: Optional[str] = None


class TrainingJob(BaseModel):
    job_id: str
    job_name: str
    status: str
    task_type: str
    base_model: str
    created_at: float
    progress: Optional[float] = 0.0
    message: Optional[str] = None
    metrics: Optional[dict] = None


RECOMMENDED_MODELS = {
    "text-classification": [
        {"id": "bert-base-multilingual-cased", "name": "BERT Multilingual", "size": "680MB"},
        {"id": "distilbert-base-multilingual-cased", "name": "DistilBERT Multilingual (schneller)", "size": "280MB"},
        {"id": "xlm-roberta-base", "name": "XLM-RoBERTa", "size": "1.1GB"},
    ],
    "image-classification": [
        {"id": "google/vit-base-patch16-224", "name": "Vision Transformer (ViT)", "size": "346MB"},
        {"id": "microsoft/resnet-50", "name": "ResNet-50", "size": "98MB"},
    ],
    "question-answering": [
        {"id": "deepset/roberta-base-squad2", "name": "RoBERTa QA", "size": "499MB"},
    ],
    "summarization": [
        {"id": "facebook/bart-large-cnn", "name": "BART CNN", "size": "1.6GB"},
        {"id": "sshleifer/distilbart-cnn-12-6", "name": "DistilBART (schneller)", "size": "1GB"},
    ],
}


def _run_training(job_id: str, config: dict, data_path: str):
    try:
        _jobs[job_id]["status"] = "running"
        _jobs[job_id]["message"] = "Lade Daten..."
        _jobs[job_id]["progress"] = 5.0

        time.sleep(2)

        _jobs[job_id]["message"] = "Lade Basismodell von Hugging Face..."
        _jobs[job_id]["progress"] = 15.0

        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        from datasets import load_dataset, Dataset
        import torch
        from torch.optim import AdamW

        cache_dir = os.getenv("MODEL_CACHE_DIR", "./model_cache")
        hf_token = os.getenv("HUGGINGFACE_TOKEN")
        output_dir = os.path.join(
            os.getenv("TRAINING_OUTPUT_DIR", "./training_output"),
            job_id
        )
        os.makedirs(output_dir, exist_ok=True)

        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        texts = [item["text"] for item in data]
        raw_labels = [item["label"] for item in data]
        unique_labels = sorted(set(raw_labels))
        label2id = {l: i for i, l in enumerate(unique_labels)}
        labels = [label2id[l] for l in raw_labels]

        _jobs[job_id]["message"] = f"Gefunden: {len(unique_labels)} Klassen, {len(texts)} Beispiele"
        _jobs[job_id]["progress"] = 25.0

        tokenizer = AutoTokenizer.from_pretrained(
            config["base_model"],
            cache_dir=cache_dir,
            token=hf_token,
        )
        model = AutoModelForSequenceClassification.from_pretrained(
            config["base_model"],
            num_labels=len(unique_labels),
            id2label={v: k for k, v in label2id.items()},
            label2id=label2id,
            cache_dir=cache_dir,
            token=hf_token,
        )

        _jobs[job_id]["message"] = "Tokenisiere Daten..."
        _jobs[job_id]["progress"] = 40.0

        encodings = tokenizer(texts, truncation=True, padding=True, max_length=512, return_tensors="pt")

        class SimpleDataset(torch.utils.data.Dataset):
            def __init__(self, enc, lbls):
                self.enc = enc
                self.labels = lbls
            def __len__(self):
                return len(self.labels)
            def __getitem__(self, idx):
                item = {k: v[idx] for k, v in self.enc.items()}
                item["labels"] = torch.tensor(self.labels[idx])
                return item

        dataset = SimpleDataset(encodings, labels)
        loader = torch.utils.data.DataLoader(dataset, batch_size=config.get("batch_size", 8))

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)

        optimizer = AdamW(model.parameters(), lr=config.get("learning_rate", 2e-5))
        num_epochs = config.get("num_epochs", 3)

        _jobs[job_id]["message"] = f"Starte Training ({num_epochs} Epochen)..."

        for epoch in range(num_epochs):
            model.train()
            total_loss = 0
            for batch_idx, batch in enumerate(loader):
                optimizer.zero_grad()
                inputs = {k: v.to(device) for k, v in batch.items()}
                outputs = model(**inputs)
                loss = outputs.loss
                loss.backward()
                optimizer.step()
                total_loss += loss.item()

            avg_loss = total_loss / len(loader)
            progress = 40.0 + ((epoch + 1) / num_epochs) * 55.0
            _jobs[job_id]["progress"] = progress
            _jobs[job_id]["message"] = f"Epoche {epoch + 1}/{num_epochs} — Loss: {avg_loss:.4f}"
            _jobs[job_id]["metrics"] = {"loss": round(avg_loss, 4), "epoch": epoch + 1}

        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)

        with open(os.path.join(output_dir, "label2id.json"), "w") as f:
            json.dump(label2id, f)

        if config.get("push_to_hub") and config.get("hub_model_id") and hf_token:
            _jobs[job_id]["message"] = "Lade Modell auf Hugging Face hoch..."
            model.push_to_hub(config["hub_model_id"], token=hf_token)
            tokenizer.push_to_hub(config["hub_model_id"], token=hf_token)

        _jobs[job_id]["status"] = "completed"
        _jobs[job_id]["progress"] = 100.0
        _jobs[job_id]["message"] = f"Training abgeschlossen! Modell gespeichert in: {output_dir}"
        _jobs[job_id]["output_dir"] = output_dir

    except Exception as e:
        _jobs[job_id]["status"] = "failed"
        _jobs[job_id]["message"] = f"Fehler: {str(e)}"


@router.post("/start")
async def start_training(
    background_tasks: BackgroundTasks,
    config_json: str = Form(...),
    training_data: UploadFile = File(...),
):
    try:
        config = json.loads(config_json)
    except Exception:
        raise HTTPException(status_code=400, detail="Ungültige Konfiguration (kein gültiges JSON)")

    upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
    os.makedirs(upload_dir, exist_ok=True)

    data_contents = await training_data.read()
    data_path = os.path.join(upload_dir, f"training_{uuid.uuid4()}.json")
    with open(data_path, "wb") as f:
        f.write(data_contents)

    try:
        json.loads(data_contents)
    except Exception:
        raise HTTPException(status_code=400, detail="Trainingsdaten müssen im JSON-Format sein")

    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "job_id": job_id,
        "job_name": config.get("job_name", "Unbenannt"),
        "status": "queued",
        "task_type": config.get("task_type", "text-classification"),
        "base_model": config.get("base_model", "bert-base-multilingual-cased"),
        "created_at": time.time(),
        "progress": 0.0,
        "message": "Warte auf Start...",
        "metrics": None,
    }

    thread = threading.Thread(target=_run_training, args=(job_id, config, data_path), daemon=True)
    thread.start()

    return {"job_id": job_id, "message": "Training gestartet"}


@router.get("/jobs")
def list_jobs():
    return {"jobs": list(_jobs.values())}


@router.get("/jobs/{job_id}")
def get_job(job_id: str):
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job nicht gefunden")
    return _jobs[job_id]


@router.delete("/jobs/{job_id}")
def delete_job(job_id: str):
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job nicht gefunden")
    del _jobs[job_id]
    return {"message": "Job gelöscht"}


@router.get("/models")
def get_recommended_models():
    return {"models": RECOMMENDED_MODELS}


@router.get("/data-format")
def get_data_format_example():
    return {
        "format": "JSON-Array",
        "text-classification-example": [
            {"text": "Der Patient hat Kopfschmerzen und Fieber.", "label": "Symptome"},
            {"text": "Nehmen Sie 2x täglich 500mg Ibuprofen.", "label": "Medikamente"},
        ],
        "description": "Jedes Objekt braucht 'text' (string) und 'label' (string) Felder.",
    }
