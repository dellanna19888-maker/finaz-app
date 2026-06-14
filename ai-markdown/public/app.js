const $ = (sel) => document.querySelector(sel);

const editor = $("#editor");
const preview = $("#preview");
const instruction = $("#instruction");
const language = $("#language");

const aiPanel = $("#ai-panel");
const aiOutput = $("#ai-output");
const aiTitle = $("#ai-title");
const aiStatus = $("#ai-status");

const SAVE_KEY = "ai-markdown:doc";

let aiBuffer = "";
let currentController = null;

const TITLES = {
  generate: "Generiertes Dokument",
  improve: "Verbesserte Version",
  continue: "Fortsetzung",
  summarize: "Zusammenfassung",
  translate: "Übersetzung",
};

// --- Vorschau & Persistenz ---------------------------------------------------

function renderPreview() {
  preview.innerHTML = window.marked
    ? marked.parse(editor.value || "")
    : editor.value;
}

function persist() {
  localStorage.setItem(SAVE_KEY, editor.value);
}

editor.addEventListener("input", () => {
  renderPreview();
  persist();
});

// --- KI-Aktion ausführen -----------------------------------------------------

async function runAction(action) {
  if (currentController) currentController.abort();
  const controller = new AbortController();
  currentController = controller;

  aiBuffer = "";
  aiOutput.textContent = "";
  aiTitle.textContent = TITLES[action] || "KI-Ausgabe";
  aiStatus.textContent = "… generiert";
  aiPanel.classList.remove("hidden");

  try {
    const resp = await fetch("/api/assist", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action,
        text: editor.value,
        instruction: instruction.value,
        language: language.value,
      }),
      signal: controller.signal,
    });

    if (!resp.ok) {
      const data = await resp.json().catch(() => ({ error: resp.statusText }));
      throw new Error(data.error || "Anfrage fehlgeschlagen");
    }

    await readSSE(resp, (event) => {
      if (event.type === "delta") {
        aiBuffer += event.text;
        aiOutput.textContent = aiBuffer;
        aiOutput.scrollTop = aiOutput.scrollHeight;
      } else if (event.type === "error") {
        throw new Error(event.message);
      }
    });

    aiStatus.textContent = "✓ fertig";
  } catch (err) {
    if (err.name === "AbortError") return;
    aiStatus.textContent = "⚠ Fehler";
    aiOutput.textContent = `Fehler: ${err.message}`;
  } finally {
    if (currentController === controller) currentController = null;
  }
}

// Liest einen Server-Sent-Events-Stream aus einer fetch-Response.
async function readSSE(response, onEvent) {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const parts = buffer.split("\n\n");
    buffer = parts.pop() ?? "";
    for (const part of parts) {
      const line = part.trim();
      if (!line.startsWith("data:")) continue;
      const json = line.slice(5).trim();
      if (json) onEvent(JSON.parse(json));
    }
  }
}

// --- UI-Verdrahtung ----------------------------------------------------------

document.querySelectorAll(".toolbar button[data-action]").forEach((btn) => {
  btn.addEventListener("click", () => runAction(btn.dataset.action));
});

$("#ai-apply").addEventListener("click", () => {
  if (!aiBuffer) return;
  editor.value = aiBuffer;
  renderPreview();
  persist();
});

$("#ai-append").addEventListener("click", () => {
  if (!aiBuffer) return;
  editor.value = (editor.value ? editor.value + "\n\n" : "") + aiBuffer;
  renderPreview();
  persist();
});

$("#ai-copy").addEventListener("click", async () => {
  if (!aiBuffer) return;
  try {
    await navigator.clipboard.writeText(aiBuffer);
    aiStatus.textContent = "✓ kopiert";
  } catch {
    aiStatus.textContent = "⚠ Kopieren nicht möglich";
  }
});

$("#ai-close").addEventListener("click", () => {
  if (currentController) currentController.abort();
  aiPanel.classList.add("hidden");
});

// --- Startinhalt --------------------------------------------------------------

editor.value =
  localStorage.getItem(SAVE_KEY) ||
  `# Willkommen bei AI Markdown

Schreibe hier dein Markdown – oder lass die **KI** etwas erstellen.

- Tippe oben einen Auftrag ein und klicke **Generieren**
- **Verbessern**, **Fortsetzen**, **Zusammenfassen** und **Übersetzen** arbeiten mit dem aktuellen Dokument
- Ergebnisse landen unten im KI-Panel – per **Übernehmen** oder **Anhängen** in den Editor
`;

renderPreview();
