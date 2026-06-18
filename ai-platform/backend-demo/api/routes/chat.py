from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from hf_client import hf_post

router = APIRouter()

DOMAIN_SYSTEM = {
    "health":    "Du bist ein medizinischer Informationsassistent. Erkläre medizinische Begriffe verständlich. Empfehle immer einen Arzt für Diagnosen.",
    "ecommerce": "Du bist ein E-Commerce-Assistent. Hilf bei Produktbeschreibungen, Bewertungen und Kaufentscheidungen.",
    "education": "Du bist ein Lernassistent. Erkläre Konzepte einfach und verständlich.",
    "general":   "Du bist ein hilfreicher KI-Assistent. Antworte auf Deutsch.",
}

# Free conversational model on HF
CHAT_MODEL = "microsoft/DialoGPT-medium"


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    domain: Optional[str] = "general"


@router.post("/")
async def chat(req: ChatRequest):
    last_user = next((m.content for m in reversed(req.messages) if m.role == "user"), "")
    system = DOMAIN_SYSTEM.get(req.domain, DOMAIN_SYSTEM["general"])
    prompt = f"{system}\n\nNutzer: {last_user}\nAssistent:"

    result = await hf_post(
        "mistralai/Mistral-7B-Instruct-v0.3",
        {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 300, "temperature": 0.7, "return_full_text": False},
        },
        timeout=40.0,
    )

    if isinstance(result, list) and result:
        reply = result[0].get("generated_text", "").strip()
    else:
        reply = str(result)

    # Trim at next "Nutzer:" if model keeps generating
    if "\nNutzer:" in reply:
        reply = reply.split("\nNutzer:")[0].strip()

    return {"reply": reply, "domain": req.domain, "model": "Mistral-7B (HF API)"}


@router.get("/domains")
def domains():
    return {
        "domains": [
            {"id": "general",   "name": "Allgemein",          "icon": "🤖"},
            {"id": "health",    "name": "Gesundheit / Medizin","icon": "🏥"},
            {"id": "ecommerce", "name": "E-Commerce / Produkte","icon": "🛍️"},
            {"id": "education", "name": "Bildung / Lernen",    "icon": "📚"},
        ]
    }
