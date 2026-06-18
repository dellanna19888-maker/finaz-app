from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
import json
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

router = APIRouter()

_chat_pipeline = None


def get_pipeline():
    global _chat_pipeline
    if _chat_pipeline is None:
        model_name = os.getenv("CHAT_MODEL", "microsoft/DialoGPT-medium")
        cache_dir = os.getenv("MODEL_CACHE_DIR", "./model_cache")
        hf_token = os.getenv("HUGGINGFACE_TOKEN")
        _chat_pipeline = pipeline(
            "text-generation",
            model=model_name,
            cache_dir=cache_dir,
            token=hf_token,
            device=0 if torch.cuda.is_available() else -1,
        )
    return _chat_pipeline


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    domain: Optional[str] = "general"
    max_tokens: Optional[int] = 512
    temperature: Optional[float] = 0.7


class ChatResponse(BaseModel):
    reply: str
    domain: str
    model: str


DOMAIN_PROMPTS = {
    "health": (
        "Du bist ein medizinischer Assistent. Du hilfst beim Verstehen von medizinischen Dokumenten. "
        "WICHTIG: Gib keine medizinischen Diagnosen. Empfehle immer einen Arzt."
    ),
    "ecommerce": (
        "Du bist ein E-Commerce-Assistent. Du hilfst bei Produktbeschreibungen, "
        "Kundenbewertungen und Kaufentscheidungen."
    ),
    "education": (
        "Du bist ein Lernassistent. Du erklärst Konzepte verständlich, "
        "gibst Lernempfehlungen und hilfst beim Verstehen von Lernmaterial."
    ),
    "general": "Du bist ein hilfreicher KI-Assistent.",
}


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        system_prompt = DOMAIN_PROMPTS.get(request.domain, DOMAIN_PROMPTS["general"])
        conversation = f"System: {system_prompt}\n\n"
        for msg in request.messages[-10:]:
            role_label = "Nutzer" if msg.role == "user" else "Assistent"
            conversation += f"{role_label}: {msg.content}\n"
        conversation += "Assistent:"

        pipe = get_pipeline()
        result = pipe(
            conversation,
            max_new_tokens=request.max_tokens,
            temperature=request.temperature,
            do_sample=True,
            pad_token_id=pipe.tokenizer.eos_token_id,
            return_full_text=False,
        )
        reply = result[0]["generated_text"].strip()
        if "\nNutzer:" in reply:
            reply = reply.split("\nNutzer:")[0].strip()

        return ChatResponse(
            reply=reply,
            domain=request.domain,
            model=os.getenv("CHAT_MODEL", "microsoft/DialoGPT-medium"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/domains")
def get_domains():
    return {
        "domains": [
            {"id": "general", "name": "Allgemein", "icon": "🤖"},
            {"id": "health", "name": "Gesundheit / Medizin", "icon": "🏥"},
            {"id": "ecommerce", "name": "E-Commerce / Produkte", "icon": "🛍️"},
            {"id": "education", "name": "Bildung / Lernen", "icon": "📚"},
        ]
    }
