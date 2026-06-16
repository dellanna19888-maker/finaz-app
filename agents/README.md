# FinAz Agenten-System

Sistema multi-agente locale (Python + Ollama). Nessun middleware esterno.

## Struttura

```
agents/
├── master.py           # Orchestratore centrale
├── silentscale.py      # Content-Agent "Dan"
├── sales_receiver.py   # Sales-Engine per i lead
├── compliance_rules.py # Gatekeeper deterministico
├── blocklist.txt       # Parole vietate (estendibile)
└── output/             # JSON dei risultati (auto-creata)
```

## Utilizzo

```bash
cd agents
python3 master.py
```

### Modalità 1 – Content
Genera un post → compliance check → salva in `output/content_*.json`

### Modalità 2 – Lead
```
{"name":"Mario","email":"mario@x.de","interesse":"ETF","quelle":"Instagram"}
```

### Modalità 3 – Batch
Un file `.txt` con un tema per riga.

## Aggiungere parole vietate

```bash
echo "nuova parola" >> blocklist.txt
```

## Requisiti

- Python 3.10+
- Ollama in esecuzione su `localhost:11434`
- Modello: `ollama pull qwen2.5:3b`
