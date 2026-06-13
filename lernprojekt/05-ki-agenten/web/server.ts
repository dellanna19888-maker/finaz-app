/**
 * ============================================================
 *  Web-Server fuer das Social-Media-Content-Team
 * ============================================================
 * Dieser kleine Server macht zwei Dinge:
 *   1. Er liefert die Webseite aus (Ordner "public").
 *   2. Er bietet eine Schnittstelle /api/generate, die das Agenten-Team
 *      startet und die Ergebnisse LIVE an die Webseite schickt
 *      (per "Server-Sent Events" – der Browser bekommt jede Stufe einzeln).
 *
 * WICHTIG: Der API-Schluessel bleibt hier auf dem Server und gelangt
 * NIEMALS in den Browser.
 *
 * Start:  npm start   ->  dann http://localhost:3000 oeffnen
 */

import "dotenv/config"; // liest ANTHROPIC_API_KEY aus einer .env-Datei
import express from "express";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import Anthropic from "@anthropic-ai/sdk";

const __dirname = dirname(fileURLToPath(import.meta.url));

// Das Modell zentral festlegen, damit man es leicht aendern kann.
// Tipp: "claude-haiku-4-5" ist guenstiger und schneller zum Experimentieren.
const MODELL = "claude-opus-4-8";

// Die Web-Suche liefert dem Rechercheur die NEUESTEN Regeln und Trends.
// Falls dein Konto sie nicht unterstuetzt, auf false setzen.
const WEB_SUCHE_AKTIV = true;
const WEB_SUCH_WERKZEUG: Anthropic.Messages.ToolUnion = {
  type: "web_search_20260209",
  name: "web_search",
};

// Den Client erst bei Bedarf erzeugen, damit der Server auch OHNE
// Schluessel startet (die Webseite laesst sich dann trotzdem ansehen).
let client: Anthropic | null = null;
function holeClient(): Anthropic {
  if (!client) client = new Anthropic(); // liest ANTHROPIC_API_KEY
  return client;
}

/** Ruft EINEN Agenten auf und gibt seinen Antworttext zurueck. */
async function frageAgent(
  systemPrompt: string,
  aufgabe: string,
  werkzeuge: Anthropic.Messages.ToolUnion[] = [],
): Promise<string> {
  const nachrichten: Anthropic.MessageParam[] = [
    { role: "user", content: aufgabe },
  ];
  let antwort: Anthropic.Message | undefined;

  // Bei der Web-Suche kann Claude mehrere Runden brauchen ("pause_turn").
  for (let runde = 0; runde < 6; runde++) {
    antwort = await holeClient().messages.create({
      model: MODELL,
      max_tokens: 4000,
      system: systemPrompt,
      thinking: { type: "adaptive" },
      output_config: { effort: "medium" },
      tools: werkzeuge,
      messages: nachrichten,
    });
    if (antwort.stop_reason === "pause_turn") {
      nachrichten.push({ role: "assistant", content: antwort.content });
      continue;
    }
    break;
  }

  return (antwort?.content ?? [])
    .filter((block): block is Anthropic.TextBlock => block.type === "text")
    .map((block) => block.text)
    .join("");
}

// --- Die vier Agenten (gleiche Rollen wie in der Kommandozeilen-Version) ---

function trendUndRegelRechercheur(nische: string, plattform: string) {
  const system =
    "Du bist ein Social-Media-Analyst. Du recherchierst gruendlich und nutzt " +
    "die Web-Suche, um IMMER die neuesten Informationen zu finden. " +
    "Du gibst ein kompaktes Briefing auf Deutsch mit Stichpunkten und nennst, " +
    "wann/woher die Infos stammen.";
  const aufgabe =
    `Recherchiere fuer die Nische '${nische}' auf der Plattform ${plattform}:\n` +
    `1) aktuelle Trends und beliebte Formate,\n` +
    `2) die neuesten Community-Richtlinien der Plattform,\n` +
    `3) relevante rechtliche Regeln (z.B. Werbekennzeichnung, Urheberrecht, ` +
    `Jugendschutz, Datenschutz).\n` +
    `Gib ein kompaktes Briefing mit Stichpunkten und Quellen.`;
  const werkzeuge = WEB_SUCHE_AKTIV ? [WEB_SUCH_WERKZEUG] : [];
  return frageAgent(system, aufgabe, werkzeuge);
}

function ideenAgent(nische: string, plattform: string, briefing: string) {
  const system =
    "Du bist ein kreativer Social-Media-Ideengeber. Du lieferst frische, " +
    "originelle Content-Ideen, die zu aktuellen Trends passen und die Regeln " +
    "einhalten.";
  const aufgabe =
    `Entwickle 5 frische Content-Ideen fuer die Nische '${nische}' auf ${plattform}. ` +
    `Beruecksichtige dieses Briefing (Trends + Regeln):\n\n${briefing}\n\n` +
    `Gib pro Idee: einen Titel, das Format (z.B. Reel, Story, Karussell) und ` +
    `den Aufhaenger (Hook).`;
  return frageAgent(system, aufgabe);
}

function contentAgent(plattform: string, ideen: string) {
  const system =
    "Du bist ein erfahrener Social-Media-Content-Creator. Du schreibst fertige " +
    "Posts im Stil der jeweiligen Plattform: ein starker Hook, ein kurzes Skript " +
    "bzw. eine Caption und passende Hashtags.";
  const aufgabe =
    `Waehle die beste der folgenden Ideen und erstelle daraus einen fertigen ` +
    `Post fuer ${plattform}:\n` +
    `- einen Hook (die ersten 3 Sekunden / die erste Zeile),\n` +
    `- ein kurzes Skript bzw. eine Caption,\n` +
    `- 5 bis 10 passende Hashtags.\n\n` +
    `Ideen:\n${ideen}`;
  return frageAgent(system, aufgabe);
}

function complianceLektor(post: string, briefing: string) {
  const system =
    "Du bist Lektor und Compliance-Pruefer fuer Social Media. Du verbesserst den " +
    "Text in Stil und Klarheit UND pruefst ihn gegen die genannten Regeln und " +
    "Gesetze (z.B. korrekte Werbekennzeichnung). Gib zuerst den finalen, " +
    "regelkonformen Post zurueck, danach eine kurze Checkliste der beachteten Regeln.";
  const aufgabe =
    `Hier sind die geltenden Regeln (aus dem Briefing):\n\n${briefing}\n\n` +
    `Ueberarbeite und pruefe diesen Post auf Regelkonformitaet:\n\n${post}`;
  return frageAgent(system, aufgabe);
}

// --- Der Web-Server -------------------------------------------------------

const app = express();

// Die Webseite (HTML, CSS, JS) aus dem Ordner "public" ausliefern.
app.use(express.static(join(__dirname, "public")));

// Die Schnittstelle: startet das Agenten-Team und streamt die Ergebnisse.
app.get("/api/generate", async (req, res) => {
  const nische = String(req.query.nische || "Gesunde Ernaehrung");
  const plattform = String(req.query.plattform || "Instagram und TikTok");

  // Header fuer "Server-Sent Events" (eine offene Verbindung zum Browser).
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");
  res.setHeader("X-Accel-Buffering", "no");
  res.flushHeaders();

  // Hilfsfunktion: schickt ein Ergebnis an den Browser.
  const sende = (schritt: string, text: string) =>
    res.write(`data: ${JSON.stringify({ schritt, text })}\n\n`);

  // Ohne Schluessel koennen wir die Agenten nicht starten.
  if (!process.env.ANTHROPIC_API_KEY) {
    sende(
      "fehler",
      "Kein API-Schluessel gefunden. Bitte ANTHROPIC_API_KEY in der .env-Datei setzen (siehe README.md).",
    );
    res.end();
    return;
  }

  try {
    sende("status", "Agent 1 (Trend- & Regel-Rechercheur) sucht im Web ...");
    const briefing = await trendUndRegelRechercheur(nische, plattform);
    sende("recherche", briefing);

    sende("status", "Agent 2 (Ideen-Agent) sammelt Ideen ...");
    const ideen = await ideenAgent(nische, plattform, briefing);
    sende("ideen", ideen);

    sende("status", "Agent 3 (Content-Agent) schreibt den Post ...");
    const post = await contentAgent(plattform, ideen);
    sende("post", post);

    sende("status", "Agent 4 (Compliance-Lektor) prueft die Regeln ...");
    const fertig = await complianceLektor(post, briefing);
    sende("fertig", fertig);

    sende("ende", "");
  } catch (fehler) {
    const text = fehler instanceof Error ? fehler.message : String(fehler);
    sende("fehler", text);
  } finally {
    res.end();
  }
});

const PORT = Number(process.env.PORT) || 3000;
app.listen(PORT, () => {
  console.log(`\n✅ Server laeuft!  Oeffne im Browser:  http://localhost:${PORT}\n`);
  if (!process.env.ANTHROPIC_API_KEY) {
    console.log(
      "⚠️  Hinweis: Noch kein ANTHROPIC_API_KEY gesetzt – die Seite laedt, " +
        "aber das Generieren braucht einen Schluessel (siehe README.md).\n",
    );
  }
});
