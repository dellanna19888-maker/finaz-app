import Anthropic from "@anthropic-ai/sdk";

/**
 * Anthropic-Client.
 *
 * Liest den API-Schlüssel automatisch aus der Umgebungsvariable
 * ANTHROPIC_API_KEY (z. B. aus der .env-Datei dieses Projekts – also dem
 * eigenen Konto dieser App).
 */
export const client = new Anthropic();
