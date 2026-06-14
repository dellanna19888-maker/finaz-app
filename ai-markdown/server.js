import express from "express";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import Anthropic from "@anthropic-ai/sdk";
import "dotenv/config";
import { runGateway } from "./compliance/gateway.js";
import { readRecentDecisions } from "./compliance/logger.js";

const __dirname = dirname(fileURLToPath(import.meta.url));

const PORT = process.env.PORT || 3000;
const MODEL = process.env.CLAUDE_MODEL || "claude-opus-4-8";

const app = express();
app.set("trust proxy", true); // echte Client-IP hinter Proxys (für GeoIP)
app.use(express.json({ limit: "2mb" }));
app.use(express.static(join(__dirname, "public")));

// Der Client wird nur erstellt, wenn ein API-Key vorhanden ist – so startet der
// Server auch ohne Key und kann eine freundliche Fehlermeldung zurückgeben.
const client = process.env.ANTHROPIC_API_KEY ? new Anthropic() : null;

const SYSTEM_PROMPT = [
  "Du bist ein erstklassiger Schreib- und Markdown-Assistent.",
  "Du arbeitest mit Markdown-Dokumenten und lieferst sauberes, gut strukturiertes Markdown.",
  "Wichtige Regeln:",
  "- Gib ausschließlich das Ergebnis als Markdown zurück, ohne einleitende oder abschließende Kommentare.",
  "- Umschließe das gesamte Dokument NICHT mit ``` Code-Fences.",
  "- Behalte die Sprache des Eingabetexts bei, außer es wird ausdrücklich eine Übersetzung verlangt.",
  "- Antworte direkt mit dem fertigen Inhalt: keine Gedanken, keine Meta-Erklärungen.",
].join("\n");

// Baut den konkreten Auftrag je nach gewählter Aktion.
function buildPrompt({ action, text, instruction, language }) {
  const doc = text?.trim() ? `\n\nAktuelles Dokument:\n"""\n${text}\n"""` : "";
  switch (action) {
    case "generate":
      return `Erstelle ein neues, vollständiges Markdown-Dokument zu folgendem Wunsch:\n${
        instruction || "Ein nützliches Beispiel-Dokument."
      }`;
    case "improve":
      return `Überarbeite und verbessere das folgende Markdown (Klarheit, Struktur, Rechtschreibung, Formatierung).${
        instruction ? ` Zusätzliche Vorgabe: ${instruction}.` : ""
      }${doc}`;
    case "continue":
      return `Schreibe das folgende Markdown-Dokument sinnvoll weiter. Gib NUR die Fortsetzung zurück, ohne den vorhandenen Text zu wiederholen.${
        instruction ? ` Vorgabe: ${instruction}.` : ""
      }${doc}`;
    case "summarize":
      return `Fasse das folgende Markdown-Dokument prägnant als Markdown zusammen (Kernpunkte als Liste).${doc}`;
    case "translate":
      return `Übersetze das folgende Markdown-Dokument nach ${
        language || "Englisch"
      }. Behalte die Markdown-Formatierung exakt bei.${doc}`;
    default:
      return null;
  }
}

app.post("/api/assist", async (req, res) => {
  const { action, text = "", instruction = "", language = "" } = req.body ?? {};

  // Compliance-Gateway: jede Operation wird gefiltert und protokolliert,
  // bevor überhaupt ein Modell-Aufruf erfolgt.
  const gate = await runGateway(req, {
    action,
    text,
    consent: req.body?.consent === true,
  });
  res.setHeader("X-Compliance-Status", gate.status);
  res.setHeader("X-Compliance-Jurisdiction", gate.geo.jurisdiction);

  if (!gate.allow) {
    const code = gate.requiresAuthorization ? 428 : 403;
    return res.status(code).json({
      authorizationRequired: gate.requiresAuthorization,
      blocked: !gate.requiresAuthorization,
      error: gate.decision.decisionText,
      reasons: gate.decision.reasons,
      compliance: gate.logEntry,
    });
  }

  if (!client) {
    return res.status(500).json({
      error:
        "ANTHROPIC_API_KEY ist nicht gesetzt. Lege eine .env-Datei an (siehe .env.example).",
    });
  }

  const prompt = buildPrompt({ action, text, instruction, language });
  if (!prompt) {
    return res.status(400).json({ error: `Unbekannte Aktion: ${action}` });
  }

  // Antwort als Server-Sent Events streamen.
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");
  res.flushHeaders?.();

  const send = (payload) => res.write(`data: ${JSON.stringify(payload)}\n\n`);

  let stream;
  try {
    stream = client.messages.stream({
      model: MODEL,
      max_tokens: 16000,
      system: SYSTEM_PROMPT,
      messages: [{ role: "user", content: prompt }],
    });

    // Bricht die Generierung ab, wenn der Browser die Verbindung schließt.
    req.on("close", () => {
      try {
        stream.abort();
      } catch {
        /* ignorieren */
      }
    });

    stream.on("text", (delta) => send({ type: "delta", text: delta }));

    await stream.finalMessage();
    send({ type: "done" });
  } catch (err) {
    const message =
      err instanceof Anthropic.APIError
        ? `Claude-API-Fehler (${err.status}): ${err.message}`
        : err?.message || "Unbekannter Fehler";
    send({ type: "error", message });
  } finally {
    res.end();
  }
});

// Audit-Log der Compliance-Entscheidungen abrufen.
app.get("/api/compliance/logs", async (req, res) => {
  try {
    const limit = Math.min(Number(req.query.limit) || 50, 500);
    res.json({ decisions: await readRecentDecisions(limit) });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.listen(PORT, () => {
  console.log(`AI Markdown läuft auf http://localhost:${PORT}`);
  if (!client) {
    console.warn(
      "⚠  Kein ANTHROPIC_API_KEY gefunden – KI-Funktionen sind deaktiviert. Siehe .env.example.",
    );
  }
});
