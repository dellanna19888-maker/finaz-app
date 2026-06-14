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

function postAssist(action, consent, signal) {
  return fetch("/api/assist", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      action,
      text: editor.value,
      instruction: instruction.value,
      language: language.value,
      consent,
    }),
    signal,
  });
}

async function runAction(action) {
  if (currentController) currentController.abort();
  const controller = new AbortController();
  currentController = controller;

  aiBuffer = "";
  aiOutput.textContent = "";
  aiTitle.textContent = TITLES[action] || "KI-Ausgabe";
  aiStatus.textContent = "… prüft Compliance";
  aiPanel.classList.remove("hidden");

  try {
    let resp = await postAssist(action, false, controller.signal);

    // WARN → menschliche Autorisierung erforderlich (Compliance-Gateway).
    if (resp.status === 428) {
      const data = await resp.json().catch(() => ({}));
      const jur = data.compliance?.angewandte_gerichtsbarkeit || "";
      const reasons = (data.reasons || []).join("\n");
      const ok = confirm(
        `Compliance-Hinweis (${jur}):\n${reasons}\n\nMenschliche Autorisierung erteilen und fortfahren?`,
      );
      if (!ok) {
        aiStatus.textContent = "⛔ keine Autorisierung";
        aiOutput.textContent = `${data.error || "Autorisierung erforderlich."}\n\n${reasons}`;
        return;
      }
      aiStatus.textContent = "… generiert (autorisiert)";
      resp = await postAssist(action, true, controller.signal);
    }

    // BLOCK → Operation abgelehnt.
    if (resp.status === 403) {
      const data = await resp.json().catch(() => ({}));
      aiStatus.textContent = "⛔ blockiert";
      aiOutput.textContent = `Blockiert: ${data.error || ""}\n\n${(data.reasons || []).join("\n")}`;
      return;
    }

    if (!resp.ok) {
      const data = await resp.json().catch(() => ({ error: resp.statusText }));
      throw new Error(data.error || "Anfrage fehlgeschlagen");
    }

    const jurisdiction = resp.headers.get("X-Compliance-Jurisdiction") || "";
    const cstatus = resp.headers.get("X-Compliance-Status") || "PASS";
    aiStatus.textContent = "… generiert";

    await readSSE(resp, (event) => {
      if (event.type === "delta") {
        aiBuffer += event.text;
        aiOutput.textContent = aiBuffer;
        aiOutput.scrollTop = aiOutput.scrollHeight;
      } else if (event.type === "error") {
        throw new Error(event.message);
      }
    });

    aiStatus.textContent = `✓ fertig · ${cstatus} · ${jurisdiction}`;
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
  const textToCopy = aiBuffer || aiOutput.textContent;
  if (!textToCopy) return;
  try {
    await navigator.clipboard.writeText(textToCopy);
    aiStatus.textContent = "✓ kopiert";
  } catch {
    aiStatus.textContent = "⚠ Kopieren nicht möglich";
  }
});

$("#ai-close").addEventListener("click", () => {
  if (currentController) currentController.abort();
  aiPanel.classList.add("hidden");
});

// --- Audit-Log (Compliance) --------------------------------------------------

$("#audit-btn").addEventListener("click", showAuditLog);

async function showAuditLog() {
  aiBuffer = "";
  aiTitle.textContent = "Audit-Log (Compliance)";
  aiStatus.textContent = "… lädt";
  aiPanel.classList.remove("hidden");
  try {
    const resp = await fetch("/api/compliance/logs?limit=100");
    if (!resp.ok) throw new Error("Konnte Audit-Log nicht laden");
    const { decisions } = await resp.json();
    aiOutput.textContent = decisions.length
      ? decisions
          .slice()
          .reverse()
          .map(
            (d) =>
              `[${d.konformitätsstatus}] ${d.timestamp} · ${d.angewandte_gerichtsbarkeit} · ${d.angeforderte_aktion}\n` +
              `   → ${d.endgültige_entscheidung}  (${d.gesetzliche_referenz})`,
          )
          .join("\n\n")
      : "Noch keine Einträge.";
    aiStatus.textContent = `✓ ${decisions.length} Einträge`;
  } catch (err) {
    aiStatus.textContent = "⚠ Fehler";
    aiOutput.textContent = `Fehler: ${err.message}`;
  }
}

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
