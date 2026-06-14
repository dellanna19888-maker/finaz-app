#!/usr/bin/env python3
"""
MeinKIProjekt - Multi-Agenten Controller
Postbote: Liest status.json und steuert den Workflow zwischen Agent A und B.
"""

import json
import os
import re
import sys
import datetime
import urllib.request
import urllib.error
from pathlib import Path

BASE_DIR = Path(__file__).parent
SHARED_MEMORY = BASE_DIR / "shared_memory" / "status.json"
AGENT_A_PROMPT = BASE_DIR / "agent_a_scripts" / "system_prompt_agent_a.txt"
AGENT_B_PROMPT = BASE_DIR / "agent_b_scripts" / "system_prompt_agent_b.txt"
AGENT_C_PROMPT = BASE_DIR / "agent_c_scripts" / "system_prompt_agent_c.txt"
AGENT_D_PROMPT = BASE_DIR / "agent_d_scripts" / "system_prompt_agent_d.txt"
PROFILE_FILE = BASE_DIR / "config" / "profile.json"
OUTPUT_FILE = BASE_DIR / "shared_memory" / "final_script.txt"
THUMBNAIL_FILE = BASE_DIR / "shared_memory" / "thumbnail_prompts.txt"
BATCH_TOPICS_FILE = BASE_DIR / "config" / "batch_topics.json"
BATCH_OUTPUT_DIR = BASE_DIR / "outputs"
MAX_COMPLIANCE_RETRIES = 2  # Wie oft B nach D-Feedback korrigieren darf

# --- Ollama Auto-Modus Konfiguration (per Umgebungsvariable überschreibbar) ---
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1")


def load_profile_block() -> str:
    """Lädt das Kanal-Profil und formatiert es als Prompt-Block."""
    if not PROFILE_FILE.exists():
        return ""
    try:
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            profile = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[Warnung] Profil konnte nicht geladen werden: {e}")
        return ""

    profile.pop("_hinweis", None)
    profile_text = json.dumps(profile, ensure_ascii=False, indent=2)
    return (
        "\n### KANAL-PROFIL (RICHTE DICH STRIKT DANACH):\n"
        "Halte dich bei Stil, Tonalität, Zielgruppe und Hashtags an dieses Profil:\n"
        f"{profile_text}\n"
    )


def load_status() -> dict:
    with open(SHARED_MEMORY, "r", encoding="utf-8") as f:
        return json.load(f)


def save_status(data: dict):
    data["last_updated"] = datetime.datetime.now().isoformat()
    with open(SHARED_MEMORY, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def reset_workflow(task: str = "", input_file: str = ""):
    """Workflow zurücksetzen und neue Aufgabe starten."""
    status = load_status()
    status["workflow_stage"] = "agent_a_pending"
    status["agent_a"] = {"status": "pending", "task": task, "draft": "", "error": ""}
    status["agent_b"] = {"status": "idle", "task": "", "final_output": "", "error": ""}
    status["agent_c"] = {"status": "idle", "thumbnail": "", "background": "", "text_overlay_style": "", "error": ""}
    status["agent_d"] = {"status": "idle", "decision": "", "issues": [], "corrections": [], "required_disclaimer": "", "retries": 0, "error": ""}
    status["metadata"]["input_file"] = input_file
    status["metadata"]["output_file"] = str(OUTPUT_FILE)
    status["metadata"]["started_at"] = datetime.datetime.now().isoformat()
    status["metadata"]["completed_at"] = ""
    save_status(status)
    print(f"[Controller] Workflow gestartet. Aufgabe: {task}")
    return status


def check_and_trigger_agent_b():
    """Prüft ob Agent A fertig ist und triggert Agent B."""
    status = load_status()

    if status["workflow_stage"] == "agent_a_pending":
        print("[Controller] Warte auf Agent A...")
        return False

    if status["workflow_stage"] == "agent_a_done":
        draft = status["agent_a"].get("draft", "")
        if draft:
            print(f"[Controller] Agent A fertig. Draft gefunden ({len(draft)} Zeichen).")
            print("[Controller] Triggere Agent B...")
            status["workflow_stage"] = "agent_b_pending"
            status["agent_b"]["status"] = "pending"
            status["agent_b"]["task"] = f"Verarbeite diesen Draft: {draft}"
            save_status(status)
            return True
        else:
            print("[Controller] Agent A hat keinen Draft geliefert.")
            return False

    if status["workflow_stage"] == "agent_b_done":
        print("[Controller] Workflow abgeschlossen!")
        save_final_output(status)
        return True

    return False


def save_final_output(status: dict):
    """Speichert das finale Ergebnis in eine Textdatei."""
    final = status["agent_b"].get("final_output", "")
    if final:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(final)
        status["metadata"]["completed_at"] = datetime.datetime.now().isoformat()
        save_status(status)
        print(f"[Controller] Finales Ergebnis gespeichert: {OUTPUT_FILE}")


def run_compliance_loop(draft: str, model: str) -> tuple[bool, str]:
    """
    Führt den B→D→B-Feedback-Loop aus.
    Gibt (True, final_output) zurück wenn approved/warning, sonst (False, "").
    """
    profile = load_profile_block()
    retries = 0

    while retries <= MAX_COMPLIANCE_RETRIES:
        # --- Agent B: Skript erstellen (oder korrigieren) ---
        status = load_status()
        corrections = status.get("agent_d", {}).get("corrections", [])
        disclaimer_hint = status.get("agent_d", {}).get("required_disclaimer", "")

        if retries == 0:
            feedback_block = ""
        else:
            feedback_block = (
                f"\n--- KORREKTUR-FEEDBACK VON COMPLIANCE-AGENT ---\n"
                f"Dein vorheriges Skript wurde abgelehnt. Korrigiere GENAU diese Punkte:\n"
                + "\n".join(f"- {c}" for c in corrections)
                + (f"\nFüge diesen Disclaimer ans Ende der Caption: '{disclaimer_hint}'" if disclaimer_hint else "")
                + "\n--- ERSTELLE DAS KORRIGIERTE SKRIPT ---\n"
            )

        prompt_b = AGENT_B_PROMPT.read_text(encoding="utf-8")
        prompt_b += profile
        prompt_b += f"\n--- DRAFT VON AGENT A ---\n{draft}\n"
        prompt_b += feedback_block
        prompt_b += "\nAntworte NUR mit dem JSON-Objekt."

        if retries > 0:
            print(f"[Compliance] Agent B korrigiert Skript (Versuch {retries}/{MAX_COMPLIANCE_RETRIES})...")
        if not run_agent_via_ollama("b", prompt_b, model):
            return False, ""

        # final_script.txt wurde von save_final_output() geschrieben
        final_script = OUTPUT_FILE.read_text(encoding="utf-8") if OUTPUT_FILE.exists() else ""
        if not final_script:
            return False, ""

        # --- Agent D: Compliance prüfen ---
        print(f"[Compliance] Agent D prüft Skript...")
        prompt_d = AGENT_D_PROMPT.read_text(encoding="utf-8")
        prompt_d += profile
        prompt_d += f"\n--- SKRIPT ZUR PRÜFUNG ---\n{final_script}\n\nAntworte NUR mit dem JSON-Objekt."
        if not run_agent_via_ollama("d", prompt_d, model):
            return False, ""

        status = load_status()
        decision = status.get("agent_d", {}).get("decision", "APPROVED")

        if decision in ("APPROVED", "WARNING"):
            # Bei WARNING: Disclaimer anhängen falls vorhanden
            if decision == "WARNING":
                disclaimer = status["agent_d"].get("required_disclaimer", "")
                if disclaimer and disclaimer not in final_script:
                    final_script += f"\n\n⚠️ {disclaimer}"
                    OUTPUT_FILE.write_text(final_script, encoding="utf-8")
                    print(f"[Compliance] WARNING – Disclaimer angehängt.")
            return True, final_script

        # REJECTED: Retry
        retries += 1
        status["agent_d"]["retries"] = retries
        save_status(status)
        if retries > MAX_COMPLIANCE_RETRIES:
            print(f"[Compliance] Maximale Korrekturen ({MAX_COMPLIANCE_RETRIES}x) erreicht. Skript verworfen.")
            return False, ""

    return False, ""


def save_thumbnail_prompts(status: dict):
    """Speichert die Thumbnail-Prompts von Agent C in eine Textdatei."""
    c = status.get("agent_c", {})
    thumbnail = c.get("thumbnail", "")
    if not thumbnail:
        return
    lines = [
        "=== THUMBNAIL-PROMPTS (FinazBrain) ===",
        f"Erstellt: {datetime.datetime.now().isoformat()}",
        "",
        "--- THUMBNAIL (Vorschaubild) ---",
        thumbnail,
        "",
        "--- HINTERGRUNDBILD ---",
        c.get("background", ""),
        "",
        "--- TEXT-OVERLAY-STIL ---",
        c.get("text_overlay_style", ""),
        "",
        "=== VERWENDUNG ===",
        "Midjourney: /imagine <prompt>",
        "DALL-E:     Prompt direkt einfügen",
        "Stable Diffusion: txt2img, Prompt-Feld",
    ]
    THUMBNAIL_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"[Controller] Thumbnail-Prompts gespeichert: {THUMBNAIL_FILE}")


def inject_agent_response(agent: str, response_json: str):
    """
    Nimmt die JSON-Antwort eines Agenten entgegen und aktualisiert status.json.
    agent: 'a' oder 'b'
    response_json: Die rohe JSON-Antwort des Agenten als String
    """
    try:
        response = json.loads(response_json)
        status = load_status()

        if agent == "a":
            agent_data = response.get("agent_a", {})
            status["agent_a"]["status"] = agent_data.get("status", "done")
            status["agent_a"]["draft"] = agent_data.get("draft", "")
            status["agent_a"]["error"] = agent_data.get("error", "")
            if status["agent_a"]["status"] == "done" and status["agent_a"]["draft"]:
                status["workflow_stage"] = "agent_a_done"
            print(f"[Controller] Agent A Antwort verarbeitet. Draft: {status['agent_a']['draft'][:80]}...")

        elif agent == "b":
            agent_data = response.get("agent_b", {})
            status["agent_b"]["status"] = agent_data.get("status", "done")
            status["agent_b"]["final_output"] = agent_data.get("final_output", "")
            status["agent_b"]["error"] = agent_data.get("error", "")
            if status["agent_b"]["status"] == "done":
                status["workflow_stage"] = "agent_b_done"
            print(f"[Controller] Agent B Antwort verarbeitet.")

        elif agent == "c":
            agent_data = response.get("agent_c", {})
            if "agent_c" not in status:
                status["agent_c"] = {}
            status["agent_c"]["status"] = agent_data.get("status", "done")
            status["agent_c"]["thumbnail"] = agent_data.get("thumbnail", "")
            status["agent_c"]["background"] = agent_data.get("background", "")
            status["agent_c"]["text_overlay_style"] = agent_data.get("text_overlay_style", "")
            status["agent_c"]["error"] = agent_data.get("error", "")
            if status["agent_c"]["status"] == "done":
                status["workflow_stage"] = "agent_c_done"
            print(f"[Controller] Agent C Antwort verarbeitet.")

        elif agent == "d":
            agent_data = response.get("agent_d", {})
            if "agent_d" not in status:
                status["agent_d"] = {"retries": 0}
            status["agent_d"]["status"] = agent_data.get("status", "done")
            status["agent_d"]["decision"] = agent_data.get("decision", "APPROVED")
            status["agent_d"]["issues"] = agent_data.get("issues", [])
            status["agent_d"]["corrections"] = agent_data.get("corrections", [])
            status["agent_d"]["required_disclaimer"] = agent_data.get("required_disclaimer", "")
            status["agent_d"]["error"] = agent_data.get("error", "")
            decision = status["agent_d"]["decision"]
            print(f"[Controller] Agent D Entscheidung: {decision}")
            if decision == "APPROVED":
                status["workflow_stage"] = "agent_d_approved"
            elif decision == "WARNING":
                status["workflow_stage"] = "agent_d_warning"
                print(f"[Controller] Warnung(en): {status['agent_d']['issues']}")
            else:
                status["workflow_stage"] = "agent_d_rejected"
                print(f"[Controller] Abgelehnt. Probleme: {status['agent_d']['issues']}")

        save_status(status)
        check_and_trigger_agent_b()

    except json.JSONDecodeError as e:
        print(f"[FEHLER] Ungültiges JSON von Agent {agent.upper()}: {e}")
        print(f"Empfangene Antwort: {response_json[:200]}")


def show_status():
    """Zeigt den aktuellen Status des Workflows."""
    status = load_status()
    print("\n" + "="*50)
    print("WORKFLOW STATUS")
    print("="*50)
    print(f"Stage:        {status['workflow_stage']}")
    print(f"Agent A:      {status['agent_a']['status']}")
    print(f"Agent B:      {status['agent_b']['status']}")
    print(f"Gestartet:    {status['metadata']['started_at']}")
    print(f"Abgeschlossen:{status['metadata']['completed_at']}")
    if status['agent_a']['draft']:
        print(f"Draft (A):    {status['agent_a']['draft'][:100]}...")
    if status['agent_b']['final_output']:
        print(f"Output (B):   {status['agent_b']['final_output'][:100]}...")
    print("="*50 + "\n")


def print_agent_a_prompt(task: str):
    """Zeigt den vollständigen Prompt für Agent A an (zum Kopieren)."""
    prompt = AGENT_A_PROMPT.read_text(encoding="utf-8")
    print("\n" + "="*60)
    print("PROMPT FÜR AGENT A (kopiere dies in Claude/dein LLM):")
    print("="*60)
    print(prompt)
    print(load_profile_block())
    print(f"\n--- AUFGABE ---\n{task}")
    print("="*60 + "\n")


def print_agent_b_prompt():
    """Zeigt den vollständigen Prompt für Agent B an (zum Kopieren)."""
    status = load_status()
    draft = status["agent_a"].get("draft", "NOCH KEIN DRAFT")
    prompt = AGENT_B_PROMPT.read_text(encoding="utf-8")
    print("\n" + "="*60)
    print("PROMPT FÜR AGENT B (kopiere dies in Claude/dein LLM):")
    print("="*60)
    print(prompt)
    print(load_profile_block())
    print(f"\n--- DRAFT VON AGENT A ---\n{draft}")
    print("="*60 + "\n")


# ============================================================
#  AUTO-MODUS: Ollama-Anbindung (lokales LLM, kein Copy-Paste)
# ============================================================

def call_ollama(prompt: str, model: str = OLLAMA_MODEL) -> str:
    """Schickt einen Prompt an die lokale Ollama-Instanz und gibt die Antwort zurück."""
    url = f"{OLLAMA_URL}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        # Niedrige Temperatur = verlässlicheres, sauberes JSON
        "options": {"temperature": 0.4},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body.get("response", "")
    except urllib.error.URLError as e:
        raise RuntimeError(
            f"Ollama nicht erreichbar unter {OLLAMA_URL}. "
            f"Laeuft 'ollama serve'? Modell '{model}' installiert? Details: {e}"
        )


def extract_json(raw: str) -> str:
    """Extrahiert das erste JSON-Objekt aus einer LLM-Antwort (entfernt Markdown-Fences)."""
    text = raw.strip()
    # ```json ... ``` Codeblöcke entfernen
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        return fence.group(1)
    # Sonst: vom ersten { bis zum letzten }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]
    return text


def run_agent_via_ollama(agent: str, prompt: str, model: str) -> bool:
    """Ruft einen Agenten über Ollama auf, parst die Antwort und speist sie ein."""
    label = agent.upper()
    print(f"[Auto] Rufe Agent {label} über Ollama ({model}) auf...")
    raw = call_ollama(prompt, model)
    cleaned = extract_json(raw)
    try:
        json.loads(cleaned)  # Validierung
    except json.JSONDecodeError:
        print(f"[FEHLER] Agent {label} lieferte kein gültiges JSON:")
        print(raw[:400])
        return False
    inject_agent_response(agent, cleaned)
    return True


def run_auto(task: str, model: str = OLLAMA_MODEL):
    """Kompletter Workflow vollautomatisch: Thema rein, fertiges Skript raus."""
    print(f"\n[Auto] Starte vollautomatischen Workflow mit Modell '{model}'.")
    reset_workflow(task)

    # --- Agent A ---
    prompt_a = AGENT_A_PROMPT.read_text(encoding="utf-8")
    prompt_a += load_profile_block()
    prompt_a += f"\n--- AUFGABE ---\n{task}\n\nAntworte NUR mit dem JSON-Objekt."
    if not run_agent_via_ollama("a", prompt_a, model):
        print("[Auto] Abbruch bei Agent A.")
        return

    # --- Agent B + D: Skript erstellen + Compliance-Loop ---
    status = load_status()
    draft = status["agent_a"].get("draft", "")
    if not draft:
        print("[Auto] Kein Draft von Agent A erhalten. Abbruch.")
        return

    approved, final_script = run_compliance_loop(draft, model)
    if not approved:
        print("[Auto] Skript konnte Compliance nicht bestehen. Abbruch.")
        return

    # --- Agent C (Thumbnail-Prompts aus finalem Skript) ---
    if final_script and AGENT_C_PROMPT.exists():
        prompt_c = AGENT_C_PROMPT.read_text(encoding="utf-8")
        prompt_c += load_profile_block()
        prompt_c += f"\n--- SKRIPT VON AGENT B ---\n{final_script}\n\nAntworte NUR mit dem JSON-Objekt."
        if run_agent_via_ollama("c", prompt_c, model):
            save_thumbnail_prompts(load_status())

    print("\n[Auto] ✓ Fertig! Ergebnis:")
    print("-" * 60)
    print(OUTPUT_FILE.read_text(encoding="utf-8"))
    print("-" * 60)
    print(f"[Auto] Skript gespeichert:     {OUTPUT_FILE}")
    if THUMBNAIL_FILE.exists():
        print(f"[Auto] Thumbnails gespeichert: {THUMBNAIL_FILE}")


# ============================================================
#  BATCH-MODUS: Mehrere Themen auf einmal verarbeiten
# ============================================================

def _safe_filename(text: str, max_len: int = 50) -> str:
    """Wandelt ein Thema in einen sicheren Dateinamen um."""
    cleaned = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    cleaned = re.sub(r"\s+", "_", cleaned.strip())
    return cleaned[:max_len]


def run_batch(topics: list[str], model: str = OLLAMA_MODEL):
    """Verarbeitet eine Liste von Themen nacheinander; jedes Ergebnis in eigene Datei."""
    BATCH_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    total = len(topics)
    ergebnisse = []

    print(f"\n[Batch] {total} Themen gefunden. Starte mit Modell '{model}'.")
    print("=" * 60)

    for i, task in enumerate(topics, 1):
        task = task.strip()
        if not task:
            continue

        print(f"\n[Batch] Thema {i}/{total}: {task}")
        print("-" * 60)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = _safe_filename(task)
        out_file = BATCH_OUTPUT_DIR / f"{timestamp}_{i:02d}_{slug}.txt"

        try:
            reset_workflow(task)

            # Agent A
            prompt_a = AGENT_A_PROMPT.read_text(encoding="utf-8")
            prompt_a += load_profile_block()
            prompt_a += f"\n--- AUFGABE ---\n{task}\n\nAntworte NUR mit dem JSON-Objekt."
            if not run_agent_via_ollama("a", prompt_a, model):
                ergebnisse.append({"thema": task, "status": "fehler_agent_a", "datei": ""})
                continue

            # Agent B + D (Compliance-Loop)
            status = load_status()
            draft = status["agent_a"].get("draft", "")
            if not draft:
                ergebnisse.append({"thema": task, "status": "kein_draft", "datei": ""})
                continue
            approved, final_script = run_compliance_loop(draft, model)
            if not approved:
                ergebnisse.append({"thema": task, "status": "compliance_abgelehnt", "datei": ""})
                continue

            # Agent C (Thumbnail-Prompts)
            thumbnail_section = ""
            if final_script and AGENT_C_PROMPT.exists():
                prompt_c = AGENT_C_PROMPT.read_text(encoding="utf-8")
                prompt_c += load_profile_block()
                prompt_c += f"\n--- SKRIPT VON AGENT B ---\n{final_script}\n\nAntworte NUR mit dem JSON-Objekt."
                if run_agent_via_ollama("c", prompt_c, model):
                    c_status = load_status().get("agent_c", {})
                    thumbnail_section = (
                        f"\n{'='*60}\nTHUMBNAIL-PROMPTS\n{'='*60}\n"
                        f"THUMBNAIL:\n{c_status.get('thumbnail', '')}\n\n"
                        f"HINTERGRUND:\n{c_status.get('background', '')}\n\n"
                        f"TEXT-OVERLAY-STIL:\n{c_status.get('text_overlay_style', '')}\n"
                    )

            # Alles in eine Datei
            header = f"THEMA: {task}\nERSTELLT: {datetime.datetime.now().isoformat()}\n{'='*60}\n\n"
            out_file.write_text(header + final_script + thumbnail_section, encoding="utf-8")
            ergebnisse.append({"thema": task, "status": "ok", "datei": str(out_file)})
            print(f"[Batch] ✓ Gespeichert: {out_file.name}")

        except RuntimeError as e:
            print(f"[Batch] FEHLER bei Thema {i}: {e}")
            ergebnisse.append({"thema": task, "status": "fehler", "datei": ""})

    # Zusammenfassung
    print("\n" + "=" * 60)
    print(f"[Batch] FERTIG — {total} Themen verarbeitet")
    print("=" * 60)
    ok = sum(1 for e in ergebnisse if e["status"] == "ok")
    fehler = total - ok
    print(f"  Erfolgreich: {ok}  |  Fehler: {fehler}")
    for e in ergebnisse:
        symbol = "✓" if e["status"] == "ok" else "✗"
        print(f"  {symbol} {e['thema'][:55]}")
    print(f"\n  Alle Skripte in: {BATCH_OUTPUT_DIR}/")

    # Protokoll speichern
    log_file = BATCH_OUTPUT_DIR / f"batch_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_file.write_text(json.dumps(ergebnisse, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  Log: {log_file.name}")


def load_and_run_batch(model: str = OLLAMA_MODEL):
    """Lädt Themen aus config/batch_topics.json und startet den Batch."""
    if not BATCH_TOPICS_FILE.exists():
        print(f"[Batch] Keine Themen-Datei gefunden: {BATCH_TOPICS_FILE}")
        print("[Batch] Erstelle config/batch_topics.json mit einer Liste von Themen.")
        return
    with open(BATCH_TOPICS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    topics = data if isinstance(data, list) else data.get("themen", [])
    if not topics:
        print("[Batch] Keine Themen in batch_topics.json gefunden.")
        return
    run_batch(topics, model)


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        print("Verwendung:")
        print("  python main_controller.py auto '<aufgabe>'      # Vollautomatisch via Ollama")
        print("  python main_controller.py batch                 # Alle Themen aus batch_topics.json")
        print("  python main_controller.py batch '<t1>' '<t2>'   # Themen direkt als Argumente")
        print("  python main_controller.py start '<aufgabe>'     # Manueller Modus (Copy-Paste)")
        print("  python main_controller.py status")
        print("  python main_controller.py prompt-a '<aufgabe>'")
        print("  python main_controller.py prompt-b")
        print("  python main_controller.py inject-a '<json-antwort>'")
        print("  python main_controller.py inject-b '<json-antwort>'")
        print()
        print("Auto-Modus Konfiguration (Umgebungsvariablen):")
        print(f"  OLLAMA_URL   (aktuell: {OLLAMA_URL})")
        print(f"  OLLAMA_MODEL (aktuell: {OLLAMA_MODEL})")
        sys.exit(0)

    cmd = args[0]

    if cmd == "auto":
        task = args[1] if len(args) > 1 else "Erstelle ein Social-Media-Reel zum Thema Finanzen & KI."
        try:
            run_auto(task)
        except RuntimeError as e:
            print(f"[FEHLER] {e}")
            sys.exit(1)

    elif cmd == "batch":
        try:
            if len(args) > 1:
                # Themen direkt als Argumente: python main_controller.py batch "Thema 1" "Thema 2"
                run_batch(list(args[1:]))
            else:
                # Themen aus batch_topics.json
                load_and_run_batch()
        except RuntimeError as e:
            print(f"[FEHLER] {e}")
            sys.exit(1)

    elif cmd == "start":
        task = args[1] if len(args) > 1 else "Standardaufgabe: Analysiere die Eingabe."
        reset_workflow(task)
        print_agent_a_prompt(task)

    elif cmd == "status":
        show_status()

    elif cmd == "prompt-a":
        task = args[1] if len(args) > 1 else "Analysiere die Eingabe."
        print_agent_a_prompt(task)

    elif cmd == "prompt-b":
        print_agent_b_prompt()

    elif cmd == "inject-a":
        if len(args) < 2:
            print("Fehler: JSON-Antwort von Agent A fehlt.")
            sys.exit(1)
        inject_agent_response("a", args[1])

    elif cmd == "inject-b":
        if len(args) < 2:
            print("Fehler: JSON-Antwort von Agent B fehlt.")
            sys.exit(1)
        inject_agent_response("b", args[1])

    else:
        print(f"Unbekannter Befehl: {cmd}")
        sys.exit(1)
