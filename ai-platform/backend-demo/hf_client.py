"""
Hugging Face Inference API client.
Calls HF's cloud servers — no local model downloads needed.
"""
import os
import httpx
from fastapi import HTTPException

HF_API = "https://api-inference.huggingface.co/models"


def _headers():
    token = os.getenv("HUGGINGFACE_TOKEN", "")
    if not token:
        raise HTTPException(
            status_code=503,
            detail="Kein HUGGINGFACE_TOKEN gesetzt. Bitte in .env eintragen.",
        )
    return {"Authorization": f"Bearer {token}"}


async def hf_post(model: str, payload: dict, timeout: float = 30.0) -> dict | list:
    url = f"{HF_API}/{model}"
    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.post(url, json=payload, headers=_headers())
        if r.status_code == 503:
            raise HTTPException(503, "Modell wird gerade geladen, bitte 20 Sekunden warten und nochmal versuchen.")
        if not r.is_success:
            raise HTTPException(r.status_code, f"HF API Fehler: {r.text[:200]}")
        return r.json()


async def hf_post_binary(model: str, data: bytes, timeout: float = 30.0) -> dict | list:
    url = f"{HF_API}/{model}"
    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.post(url, content=data, headers={**_headers(), "Content-Type": "application/octet-stream"})
        if r.status_code == 503:
            raise HTTPException(503, "Modell wird gerade geladen, bitte 20 Sekunden warten und nochmal versuchen.")
        if not r.is_success:
            raise HTTPException(r.status_code, f"HF API Fehler: {r.text[:200]}")
        return r.json()
