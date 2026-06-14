/* Einfache, abhängigkeitsfreie Konsolenausgabe mit Farben. */

const COLORS = {
  reset: "\x1b[0m",
  bold: "\x1b[1m",
  dim: "\x1b[2m",
  gray: "\x1b[90m",
  cyan: "\x1b[36m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  magenta: "\x1b[35m",
  blue: "\x1b[34m",
  red: "\x1b[31m",
} as const;

const AGENT_COLORS: Record<string, string> = {
  researcher: COLORS.blue,
  analyst: COLORS.magenta,
  writer: COLORS.green,
};

function color(text: string, c: string): string {
  return `${c}${text}${COLORS.reset}`;
}

export const log = {
  delegate(agent: string, task: string): void {
    const c = AGENT_COLORS[agent] ?? COLORS.cyan;
    console.log(`\n${color("→ delegiere an", COLORS.gray)} ${color(agent, c + COLORS.bold)}`);
    console.log(`  ${color(task, COLORS.dim)}`);
  },
  agentDone(agent: string): void {
    const c = AGENT_COLORS[agent] ?? COLORS.cyan;
    console.log(`  ${color(`✓ ${agent} fertig`, c)}`);
  },
  thought(text: string): void {
    if (text.trim()) {
      console.log(`\n${color("🧭 Orchestrator:", COLORS.cyan + COLORS.bold)} ${text.trim()}`);
    }
  },
  final(answer: string): void {
    const line = "━".repeat(60);
    console.log(`\n${color(line, COLORS.gray)}`);
    console.log(color("✅ Ergebnis", COLORS.green + COLORS.bold));
    console.log("");
    console.log(answer);
    console.log(color(line, COLORS.gray));
  },
  error(err: unknown): void {
    const msg = err instanceof Error ? err.message : String(err);
    console.error(`\n${color("✖ Fehler:", COLORS.red + COLORS.bold)} ${msg}`);
  },
};

export function banner(model: string): void {
  console.log(color("\n┌──────────────────────────────────────────────┐", COLORS.cyan));
  console.log(color("│   🤖  Multi-Agent App · Claude API             │", COLORS.cyan + COLORS.bold));
  console.log(color("└──────────────────────────────────────────────┘", COLORS.cyan));
  console.log(color(`   Modell: ${model}`, COLORS.gray));
  console.log(color("   Aufgabe eingeben · 'exit' zum Beenden\n", COLORS.gray));
}
