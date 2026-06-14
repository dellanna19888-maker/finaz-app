import type Anthropic from "@anthropic-ai/sdk";
import { client } from "./client.js";
import { AGENTS, agentRoster, extractText, runSubAgent } from "./agents.js";
import { MODEL, MAX_TOKENS, ORCHESTRATOR_EFFORT, MAX_ORCHESTRATOR_STEPS } from "./config.js";
import { log } from "./logger.js";

const ORCHESTRATOR_SYSTEM = `Du bist der Orchestrator eines Multi-Agenten-Systems. Du erhältst eine Aufgabe vom Nutzer und koordinierst spezialisierte Agenten, um sie bestmöglich zu lösen.

Vorgehen:
1. Zerlege die Aufgabe in sinnvolle Teilaufgaben.
2. Delegiere jede Teilaufgabe mit dem Werkzeug "delegate_to_agent" an den am besten geeigneten Agenten. Du darfst mehrere Agenten beauftragen – auch parallel in einer Antwort.
3. Einfache Aufgaben darfst du auch direkt selbst beantworten, ohne zu delegieren.
4. Fasse die Ergebnisse zu einer klaren, vollständigen Endantwort zusammen.

Verfügbare Agenten:
${agentRoster()}

Regeln:
- Die Agenten teilen keinen gemeinsamen Speicher: Formuliere jede Teilaufgabe eigenständig und mit allem nötigen Kontext.
- Delegiere nur, was wirklich nötig ist – vermeide unnötige Schritte.
- Antworte in der Sprache der Nutzeraufgabe.
- Deine letzte Nachricht (ohne Werkzeugaufruf) ist die Endantwort für den Nutzer.`;

const delegateTool: Anthropic.Tool = {
  name: "delegate_to_agent",
  description:
    "Delegiere eine klar umrissene Teilaufgabe an einen spezialisierten Agenten und erhalte dessen Ergebnis zurück.",
  input_schema: {
    type: "object",
    properties: {
      agent: {
        type: "string",
        enum: Object.keys(AGENTS),
        description: "Der Agent, der die Teilaufgabe bearbeiten soll.",
      },
      task: {
        type: "string",
        description: "Die präzise formulierte Teilaufgabe inklusive allem nötigen Kontext.",
      },
    },
    required: ["agent", "task"],
  },
};

/**
 * Startet den Orchestrator für eine Nutzeraufgabe. Der Orchestrator plant,
 * delegiert über das Werkzeug `delegate_to_agent` an Spezial-Agenten und fasst
 * deren Ergebnisse zu einer Endantwort zusammen.
 */
export async function runOrchestrator(userTask: string): Promise<string> {
  const messages: Anthropic.MessageParam[] = [{ role: "user", content: userTask }];

  for (let step = 0; step < MAX_ORCHESTRATOR_STEPS; step++) {
    const response = await client.messages.create({
      model: MODEL,
      max_tokens: MAX_TOKENS,
      system: ORCHESTRATOR_SYSTEM,
      tools: [delegateTool],
      thinking: { type: "adaptive" },
      output_config: { effort: ORCHESTRATOR_EFFORT },
      messages,
    });

    if (response.stop_reason === "tool_use") {
      // Eventuellen Zwischenkommentar des Orchestrators anzeigen.
      const interim = extractText(response);
      if (interim) log.thought(interim);

      messages.push({ role: "assistant", content: response.content });

      const toolResults: Anthropic.ToolResultBlockParam[] = [];
      for (const block of response.content) {
        if (block.type === "tool_use" && block.name === "delegate_to_agent") {
          const input = block.input as { agent: string; task: string };
          log.delegate(input.agent, input.task);
          const result = await runSubAgent(input.agent, input.task);
          log.agentDone(input.agent);
          toolResults.push({
            type: "tool_result",
            tool_use_id: block.id,
            content: result,
          });
        }
      }
      messages.push({ role: "user", content: toolResults });
      continue;
    }

    if (response.stop_reason === "pause_turn") {
      messages.push({ role: "assistant", content: response.content });
      continue;
    }

    if (response.stop_reason === "refusal") {
      return "Die Anfrage wurde aus Sicherheitsgründen abgelehnt.";
    }

    return extractText(response) || "(Keine Antwort erzeugt.)";
  }

  return "Maximale Anzahl an Orchestrator-Schritten erreicht – bitte die Aufgabe weiter eingrenzen.";
}
