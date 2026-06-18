# 🧠 KI-Plattform — Eigene KI trainieren

Eine vollständige KI-Plattform zum Trainieren und Nutzen eigener Modelle.

## Funktionen

| Funktion | Beschreibung |
|---|---|
| 💬 **Chat / Assistent** | Konversations-KI für Gesundheit, E-Commerce und Bildung |
| 📝 **Text-Klassifikation** | Texte automatisch kategorisieren (Zero-Shot, multilingual) |
| 🖼️ **Bild-Erkennung** | Bilder mit CLIP und ViT klassifizieren |
| 📄 **Dokument-Analyse** | PDFs zusammenfassen und befragen (Q&A) |
| 🎓 **KI Trainieren** | Fine-Tuning mit eigenen Daten auf Hugging Face Modellen |
| 🗄️ **Modelle** | Alle Modelle verwalten und auf HF Hub hochladen |

## Schnellstart

### Voraussetzungen
- Python 3.11+
- Node.js 20+
- (Optional) Hugging Face Account für Fine-Tuning Upload

### 1. Starten

```bash
cd ai-platform
./start.sh
```

Öffne dann: http://localhost:5173

### 2. Hugging Face Token (optional, für Fine-Tuning Upload)

1. Erstelle einen Account auf huggingface.co
2. Gehe zu Einstellungen → Access Tokens → Neues Token erstellen
3. Trage das Token in `backend/.env` ein:
   ```
   HUGGINGFACE_TOKEN=hf_deinToken...
   ```

## Datenformat für Training

```json
[
  {"text": "Patient hat Fieber 38.5°C", "label": "Symptome"},
  {"text": "Nehmen Sie 2x täglich 500mg Ibuprofen", "label": "Medikamente"},
  {"text": "Blutdruck 140/90 mmHg", "label": "Labor-Ergebnisse"}
]
```

Jedes Objekt braucht:
- `"text"`: Der Text (string)
- `"label"`: Die Kategorie (string)

Mindestens **10 Beispiele pro Kategorie** für gute Ergebnisse.

## Technologie

| Komponente | Technologie |
|---|---|
| Frontend | Vue.js 3 + TypeScript |
| Backend | Python FastAPI |
| KI-Modelle | Hugging Face Transformers |
| Chat | DialoGPT / eigene Modelle |
| Text | BERT, DistilBERT (multilingual) |
| Bilder | ViT, CLIP |
| Dokumente | BART (Zusammenfassung), RoBERTa (Q&A) |

## API-Dokumentation

Nach dem Start unter: http://localhost:8000/docs
