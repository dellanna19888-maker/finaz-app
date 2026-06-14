#!/usr/bin/env python3
"""
MeinKIProjekt - Multi-Agenten Controller
Postbote: Liest status.json und steuert den Workflow zwischen Agent A und B.
"""

import json
import os
import sys
import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
SHARED_MEMORY = BASE_DIR / "shared_memory" / "status.json"
AGENT_A_PROMPT = BASE_DIR / "agent_a_scripts" / "system_prompt_agent_a.txt"
AGENT_B_PROMPT = BASE_DIR / "agent_b_scripts" / "system_prompt_agent_b.txt"
OUTPUT_FILE = BASE_DIR / "shared_memory" / "final_script.txt"


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
    print(f"\n--- DRAFT VON AGENT A ---\n{draft}")
    print("="*60 + "\n")


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        print("Verwendung:")
        print("  python main_controller.py start '<aufgabe>'")
        print("  python main_controller.py status")
        print("  python main_controller.py prompt-a '<aufgabe>'")
        print("  python main_controller.py prompt-b")
        print("  python main_controller.py inject-a '<json-antwort>'")
        print("  python main_controller.py inject-b '<json-antwort>'")
        sys.exit(0)

    cmd = args[0]

    if cmd == "start":
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
