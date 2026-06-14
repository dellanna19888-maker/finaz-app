import type Anthropic from "@anthropic-ai/sdk";
import { client } from "./client.js";
import { MODEL, MAX_TOKENS, MAX_SUBAGENT_CONTINUATIONS } from "./config.js";

type Tool = Anthropic.Messages.ToolUnion;
type Effort = "low" | "medium" | "high";

// Server-seitige Anthropic-Werkzeuge. Der Cast über `unknown` sorgt dafür, dass
// der Code auch mit leicht älteren SDK-Typdefinitionen kompiliert – zur Laufzeit
// werden die Typ-Strings unverändert an die API übergeben.
const webSearch = { type: "web_search_20260209", name: "web_search" } as unknown as Tool;
const webFetch = { type: "web_fetch_20260209", name: "web_fetch" } as unknown as Tool;
const codeExecution = { type: "code_execution_20260120", name: "code_execution" } as unknown as Tool;

export interface AgentSpec {
  /** Kurzbeschreibung – wird dem Orchestrator zur Auswahl angezeigt. */
  description: string;
  /** System-Prompt, der die Rolle des Agenten definiert. */
  system: string;
  /** Server-seitige Werkzeuge, die dieser Agent nutzen darf. */
  tools: Tool[];
  /** Denk-/Aufwandsstufe. */
  effort: Effort;
}

export const AGENTS: Record<string, AgentSpec> = {
  researcher: {
    description: "Recherchiert aktuelle Informationen im Web (Websuche + Seitenabruf).",
    system:
      "Du bist ein Recherche-Agent in einem Multi-Agenten-System. " +
      "Nutze die Websuche und den Seitenabruf, um aktuelle und belastbare Informationen zu finden. " +
      "Gib eine prägnante, gut strukturierte Zusammenfassung zurück und nenne die wichtigsten Quellen (URLs). " +
      "Wenn du etwas nicht sicher belegen kannst, sage es offen. " +
      "Antworte in der Sprache der Aufgabe.",
    tools: [webSearch, webFetch],
    effort: "medium",
  },
  analyst: {
    description: "Analysiert Sachverhalte, rechnet und verarbeitet Daten (kann Code ausführen).",
    system:
      "Du bist ein Analyse-Agent in einem Multi-Agenten-System. " +
      "Du analysierst Sachverhalte gründlich, rechnest und verarbeitest Daten. " +
      "Für Berechnungen, Datenverarbeitung oder Simulationen kannst du Code ausführen. " +
      "Gib ein klares, nachvollziehbares Ergebnis mit den wichtigsten Schritten und Annahmen zurück. " +
      "Antworte in der Sprache der Aufgabe.",
    tools: [codeExecution],
    effort: "high",
  },
  writer: {
    description: "Formuliert hochwertige, klar strukturierte Texte.",
    system:
      "Du bist ein Schreib-Agent in einem Multi-Agenten-System. " +
      "Du formulierst klare, gut strukturierte und ansprechende Texte. " +
      "Halte dich an die gewünschte Form, Länge und Tonalität. " +
      "Antworte in der Sprache der Aufgabe.",
    tools: [],
    effort: "medium",
  },
};

/** Liste der Agenten als Text für den System-Prompt des Orchestrators. */
export function agentRoster(): string {
  return Object.entries(AGENTS)
    .map(([name, spec]) => `- ${name}: ${spec.description}`)
    .join("\n");
}

/** Hängt alle Text-Blöcke einer Antwort zu einem String zusammen. */
export function extractText(message: Anthropic.Message): string {
  return message.content
    .filter((b): b is Anthropic.TextBlock => b.type === "text")
    .map((b) => b.text)
    .join("\n")
    .trim();
}

/**
 * Führt einen spezialisierten Agenten für eine klar umrissene Teilaufgabe aus
 * und gibt dessen Textergebnis zurück.
 */
export async function runSubAgent(agentKey: string, task: string): Promise<string> {
  const spec = AGENTS[agentKey];
  if (!spec) {
    return `Fehler: Unbekannter Agent "${agentKey}". Verfügbar: ${Object.keys(AGENTS).join(", ")}.`;
  }

  const messages: Anthropic.MessageParam[] = [{ role: "user", content: task }];

  for (let i = 0; i < MAX_SUBAGENT_CONTINUATIONS; i++) {
    const response = await client.messages.create({
      model: MODEL,
      max_tokens: MAX_TOKENS,
      system: spec.system,
      ...(spec.tools.length ? { tools: spec.tools } : {}),
      thinking: { type: "adaptive" },
      output_config: { effort: spec.effort },
      messages,
    });

    // Server-seitige Werkzeuge (Websuche, Code-Ausführung) brauchen ggf. mehrere
    // Runden – bei "pause_turn" die Antwort anhängen und fortsetzen.
    if (response.stop_reason === "pause_turn") {
      messages.push({ role: "assistant", content: response.content });
      continue;
    }
    if (response.stop_reason === "refusal") {
      return "Der Agent hat die Anfrage aus Sicherheitsgründen abgelehnt.";
    }
    return extractText(response) || "(Der Agent hat keine Textantwort geliefert.)";
  }

  return "Der Agent hat das Schritt-Limit erreicht, ohne fertig zu werden.";
}
