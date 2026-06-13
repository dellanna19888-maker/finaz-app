/**
 * ============================================================
 *  Social-Media-Content-Team  (TypeScript)
 * ============================================================
 * Gleiche Idee wie die Python-Version – vergleiche beide!
 * Ein Team aus VIER KI-Agenten erstellt Content für Social Media
 * (Instagram, TikTok & Co.) – mit frischen Ideen UND auf Basis der
 * neuesten Plattform-Regeln und Gesetze:
 *
 *   1. 🔎 Trend- & Regel-Rechercheur -> sucht im Web nach aktuellen Trends,
 *         den neuesten Plattform-Richtlinien und relevanten Gesetzen
 *   2. 💡 Ideen-Agent   -> entwickelt frische Content-Ideen
 *   3. ✍️  Content-Agent -> schreibt einen fertigen Post (Hook, Skript, Hashtags)
 *   4. ✅ Compliance-Lektor -> verbessert und prüft auf Regelkonformität
 *
 * Start:  npm start -- "<Nische>" "<Plattform>"
 * Bsp.:   npm start -- "Fitness für Anfänger" "TikTok"
 */

import "dotenv/config"; // liest ANTHROPIC_API_KEY aus einer .env-Datei
import { mkdir, writeFile } from "node:fs/promises";
import Anthropic from "@anthropic-ai/sdk";

// Ein einziger Client für alle Agenten.
// Der Schlüssel wird automatisch aus ANTHROPIC_API_KEY gelesen.
const client = new Anthropic();

// Das Modell zentral festlegen, damit man es leicht ändern kann.
// Tipp: "claude-haiku-4-5" ist günstiger und schneller zum Experimentieren.
const MODELL = "claude-opus-4-8";

// Die Web-Suche sorgt dafür, dass der Rechercheur die NEUESTEN Regeln und
// Trends findet. Sie ist ein serverseitiges Werkzeug von Anthropic und
// verursacht geringe Zusatzkosten. Falls dein Konto sie (noch) nicht
// unterstützt, setze dies auf false – dann nutzt der Agent sein vorhandenes
// Wissen statt der Live-Suche.
const WEB_SUCHE_AKTIV = true;
const WEB_SUCH_WERKZEUG: Anthropic.Messages.ToolUnion = {
  type: "web_search_20260209",
  name: "web_search",
};

/**
 * Ruft EINEN Agenten auf und gibt seinen Antworttext zurück.
 * - systemPrompt: beschreibt, WER der Agent ist (seine Rolle).
 * - aufgabe:      die konkrete Eingabe, WAS er tun soll.
 * - werkzeuge:    optionale Werkzeuge (z.B. die Web-Suche).
 */
async function frageAgent(
  systemPrompt: string,
  aufgabe: string,
  werkzeuge: Anthropic.Messages.ToolUnion[] = [],
): Promise<string> {
  const nachrichten: Anthropic.MessageParam[] = [
    { role: "user", content: aufgabe },
  ];

  let antwort: Anthropic.Message | undefined;

  // Bei der Web-Suche kann Claude mehrere Runden brauchen. "pause_turn"
  // bedeutet: die Suche läuft serverseitig noch weiter -> wir setzen fort.
  for (let runde = 0; runde < 6; runde++) {
    antwort = await client.messages.create({
      model: MODELL,
      max_tokens: 4000,
      system: systemPrompt,
      thinking: { type: "adaptive" }, // Claude denkt bei Bedarf selbst nach
      output_config: { effort: "medium" }, // Qualität vs. Kosten: low | medium | high | max
      tools: werkzeuge,
      messages: nachrichten,
    });
    if (antwort.stop_reason === "pause_turn") {
      nachrichten.push({ role: "assistant", content: antwort.content });
      continue;
    }
    break;
  }

  // Nur den sichtbaren Text aus den "text"-Blöcken einsammeln
  // (Denk-Blöcke und Suchergebnisse ignorieren wir hier).
  return (antwort?.content ?? [])
    .filter((block): block is Anthropic.TextBlock => block.type === "text")
    .map((block) => block.text)
    .join("");
}

// --- Die vier Agenten -----------------------------------------------------

// Agent 1: sucht aktuelle Trends, Plattform-Regeln und Gesetze (mit Web-Suche).
function trendUndRegelRechercheur(
  nische: string,
  plattform: string,
): Promise<string> {
  const system =
    "Du bist ein Social-Media-Analyst. Du recherchierst gründlich und nutzt " +
    "die Web-Suche, um IMMER die neuesten Informationen zu finden. " +
    "Du gibst ein kompaktes Briefing auf Deutsch mit Stichpunkten und nennst, " +
    "wann/woher die Infos stammen.";
  const aufgabe =
    `Recherchiere für die Nische '${nische}' auf der Plattform ${plattform}:\n` +
    `1) aktuelle Trends und beliebte Formate,\n` +
    `2) die neuesten Community-Richtlinien der Plattform,\n` +
    `3) relevante rechtliche Regeln (z.B. Werbekennzeichnung, Urheberrecht, ` +
    `Jugendschutz, Datenschutz).\n` +
    `Gib ein kompaktes Briefing mit Stichpunkten und Quellen.`;
  const werkzeuge = WEB_SUCHE_AKTIV ? [WEB_SUCH_WERKZEUG] : [];
  return frageAgent(system, aufgabe, werkzeuge);
}

// Agent 2: entwickelt frische Content-Ideen.
function ideenAgent(
  nische: string,
  plattform: string,
  briefing: string,
): Promise<string> {
  const system =
    "Du bist ein kreativer Social-Media-Ideengeber. Du lieferst frische, " +
    "originelle Content-Ideen, die zu aktuellen Trends passen und die Regeln " +
    "einhalten.";
  const aufgabe =
    `Entwickle 5 frische Content-Ideen für die Nische '${nische}' auf ${plattform}. ` +
    `Berücksichtige dieses Briefing (Trends + Regeln):\n\n${briefing}\n\n` +
    `Gib pro Idee: einen Titel, das Format (z.B. Reel, Story, Karussell) und ` +
    `den Aufhänger (Hook).`;
  return frageAgent(system, aufgabe);
}

// Agent 3: schreibt aus der besten Idee einen fertigen Post.
function contentAgent(plattform: string, ideen: string): Promise<string> {
  const system =
    "Du bist ein erfahrener Social-Media-Content-Creator. Du schreibst fertige " +
    "Posts im Stil der jeweiligen Plattform: ein starker Hook, ein kurzes Skript " +
    "bzw. eine Caption und passende Hashtags.";
  const aufgabe =
    `Wähle die beste der folgenden Ideen und erstelle daraus einen fertigen ` +
    `Post für ${plattform}:\n` +
    `- einen Hook (die ersten 3 Sekunden / die erste Zeile),\n` +
    `- ein kurzes Skript bzw. eine Caption,\n` +
    `- 5 bis 10 passende Hashtags.\n\n` +
    `Ideen:\n${ideen}`;
  return frageAgent(system, aufgabe);
}

// Agent 4: verbessert den Post und prüft ihn gegen die Regeln/Gesetze.
function complianceLektor(post: string, briefing: string): Promise<string> {
  const system =
    "Du bist Lektor und Compliance-Prüfer für Social Media. Du verbesserst den " +
    "Text in Stil und Klarheit UND prüfst ihn gegen die genannten Regeln und " +
    "Gesetze (z.B. korrekte Werbekennzeichnung). Gib zuerst den finalen, " +
    "regelkonformen Post zurück, danach eine kurze Checkliste der beachteten Regeln.";
  const aufgabe =
    `Hier sind die geltenden Regeln (aus dem Briefing):\n\n${briefing}\n\n` +
    `Überarbeite und prüfe diesen Post auf Regelkonformität:\n\n${post}`;
  return frageAgent(system, aufgabe);
}

// --- Der Orchestrator -----------------------------------------------------

async function main(): Promise<void> {
  // Ohne Schlüssel können wir die API nicht aufrufen -> freundlich hinweisen.
  if (!process.env.ANTHROPIC_API_KEY) {
    console.error("⚠️  Kein API-Schlüssel gefunden!");
    console.error("    Bitte lege eine .env-Datei mit ANTHROPIC_API_KEY an.");
    console.error("    (Siehe README.md, Schritt 1 und 2.)");
    process.exit(1);
  }

  // Nische und Plattform aus der Kommandozeile lesen (mit Standardwerten).
  const args = process.argv.slice(2);
  const nische = args[0] || "Gesunde Ernährung";
  const plattform = args[1] || "Instagram und TikTok";

  console.log(`\n🎯 Nische: ${nische}`);
  console.log(`📱 Plattform: ${plattform}\n`);

  console.log("🔎 Agent 1 (Trend- & Regel-Rechercheur) sucht im Web ...");
  const briefing = await trendUndRegelRechercheur(nische, plattform);
  console.log(briefing + "\n");

  console.log("💡 Agent 2 (Ideen-Agent) sammelt Ideen ...");
  const ideen = await ideenAgent(nische, plattform, briefing);
  console.log(ideen + "\n");

  console.log("✍️  Agent 3 (Content-Agent) schreibt den Post ...");
  const post = await contentAgent(plattform, ideen);
  console.log(post + "\n");

  console.log("✅ Agent 4 (Compliance-Lektor) prüft die Regeln ...");
  const fertig = await complianceLektor(post, briefing);
  console.log(fertig + "\n");

  // Das Endergebnis als Markdown-Datei speichern.
  await mkdir("output", { recursive: true });
  const dateiname = "output/social-media-post.md";
  await writeFile(dateiname, `# ${nische} – ${plattform}\n\n${fertig}\n`, "utf-8");

  console.log(`✅ Fertig! Der Post wurde gespeichert in: ${dateiname}`);
}

main().catch((fehler) => {
  console.error("Fehler:", fehler);
  process.exit(1);
});
