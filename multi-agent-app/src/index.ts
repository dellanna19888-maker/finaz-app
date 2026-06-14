import "dotenv/config";
import * as readline from "node:readline/promises";
import { stdin as input, stdout as output, argv, exit } from "node:process";
import { runOrchestrator } from "./orchestrator.js";
import { log, banner } from "./logger.js";
import { MODEL } from "./config.js";

async function runOnce(task: string): Promise<void> {
  try {
    const answer = await runOrchestrator(task);
    log.final(answer);
  } catch (err) {
    log.error(err);
  }
}

async function main(): Promise<void> {
  if (!process.env.ANTHROPIC_API_KEY) {
    console.error(
      "Fehlende Umgebungsvariable ANTHROPIC_API_KEY.\n" +
        'Lege eine Datei ".env" an (Vorlage: .env.example) und trage deinen eigenen Anthropic-Schlüssel ein.',
    );
    exit(1);
  }

  banner(MODEL);

  // Einmal-Modus: Aufgabe direkt als Kommandozeilenargument.
  const oneShot = argv.slice(2).join(" ").trim();
  if (oneShot) {
    await runOnce(oneShot);
    return;
  }

  // Interaktiver Modus.
  const rl = readline.createInterface({ input, output });
  try {
    while (true) {
      const task = (await rl.question("\n📝 Aufgabe › ")).trim();
      if (!task) continue;
      if (["exit", "quit", ":q"].includes(task.toLowerCase())) break;
      await runOnce(task);
    }
  } finally {
    rl.close();
  }
}

main();
