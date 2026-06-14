/** Zentrale Konfiguration der App. */

// Verwendetes Claude-Modell (siehe https://docs.claude.com).
export const MODEL = "claude-opus-4-8";

// Maximale Ausgabe-Tokens pro Anfrage (ohne Streaming bewusst moderat gehalten).
export const MAX_TOKENS = 16_000;

// Denk-/Aufwandsstufe des Orchestrators: low | medium | high | max.
export const ORCHESTRATOR_EFFORT = "high" as const;

// Sicherheitsgrenzen gegen Endlosschleifen.
export const MAX_ORCHESTRATOR_STEPS = 12;
export const MAX_SUBAGENT_CONTINUATIONS = 8;
