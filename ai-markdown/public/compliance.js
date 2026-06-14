const $ = (sel) => document.querySelector(sel);

const elText = $("#c-text");
const elAction = $("#c-action");
const elJur = $("#c-jur");
const elConsent = $("#c-consent");
const elResult = $("#c-result");
const elTbody = $("#c-tbody");
const elEmpty = $("#c-empty");

let auditCache = [];

function esc(s) {
  return String(s ?? "").replace(
    /[&<>"]/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c],
  );
}

function badge(status) {
  return `<span class="badge badge-${esc(status)}">${esc(status)}</span>`;
}

// --- Prüfung (Simulation) ----------------------------------------------------

async function runCheck() {
  elResult.classList.remove("hidden");
  elResult.textContent = "… prüft";
  try {
    const resp = await fetch("/api/compliance/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        action: elAction.value,
        text: elText.value,
        jurisdiction: elJur.value,
        consent: elConsent.checked,
      }),
    });
    if (!resp.ok) {
      const data = await resp.json().catch(() => ({}));
      throw new Error(data.error || "Prüfung fehlgeschlagen");
    }
    const r = await resp.json();
    const findings = r.reasons && r.reasons.length ? r.reasons : ["Keine Befunde"];
    const befund =
      r.status !== r.originalStatus ? ` (Befund: ${badge(r.originalStatus)})` : "";

    elResult.innerHTML =
      `<h3>${badge(r.status)}${befund}</h3>` +
      `<dl>` +
      `<dt>Gerichtsbarkeit</dt><dd>${esc(r.logEntry.angewandte_gerichtsbarkeit)} ` +
      `<span class="hint">(${esc(r.geo.source)}${r.geo.geoipActive ? ", GeoIP aktiv" : ""})</span></dd>` +
      `<dt>Aktion</dt><dd>${esc(r.logEntry.angeforderte_aktion || "—")}</dd>` +
      `<dt>Entscheidung</dt><dd>${esc(r.decision)}</dd>` +
      `<dt>Referenz</dt><dd>${esc(r.reference)}</dd>` +
      `<dt>Befunde</dt><dd><ul>${findings.map((f) => `<li>${esc(f)}</li>`).join("")}</ul></dd>` +
      `</dl>` +
      `<pre>${esc(JSON.stringify(r.logEntry, null, 2))}</pre>` +
      `<p class="hint">Simulation – nicht ins Audit-Log geschrieben.</p>`;
  } catch (err) {
    elResult.innerHTML = `<span class="cell-BLOCK">Fehler: ${esc(err.message)}</span>`;
  }
}

// --- Audit-Log ---------------------------------------------------------------

async function loadAudit() {
  try {
    const resp = await fetch("/api/compliance/logs?limit=200");
    if (!resp.ok) throw new Error("Konnte Audit-Log nicht laden");
    const { decisions } = await resp.json();
    auditCache = decisions.slice().reverse(); // neueste zuerst
    renderAudit();
  } catch (err) {
    elEmpty.textContent = `Fehler: ${err.message}`;
    elEmpty.classList.remove("hidden");
  }
}

function renderAudit() {
  elTbody.innerHTML = auditCache
    .map(
      (d) =>
        `<tr>` +
        `<td>${esc(d.timestamp)}</td>` +
        `<td>${esc(d.angewandte_gerichtsbarkeit)}</td>` +
        `<td>${esc(d.angeforderte_aktion)}</td>` +
        `<td class="cell-status cell-${esc(d.konformitätsstatus)}">${esc(d.konformitätsstatus)}</td>` +
        `<td>${esc(d.gesetzliche_referenz)}</td>` +
        `<td>${esc(d.endgültige_entscheidung)}</td>` +
        `</tr>`,
    )
    .join("");
  elEmpty.classList.toggle("hidden", auditCache.length > 0);
}

function exportCsv() {
  if (!auditCache.length) return;
  const cols = [
    "timestamp",
    "angewandte_gerichtsbarkeit",
    "angeforderte_aktion",
    "konformitätsstatus",
    "gesetzliche_referenz",
    "endgültige_entscheidung",
  ];
  const cell = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
  const lines = [cols.join(",")].concat(
    auditCache.map((d) => cols.map((c) => cell(d[c])).join(",")),
  );
  const blob = new Blob(["﻿" + lines.join("\n")], {
    type: "text/csv;charset=utf-8",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "compliance-audit.csv";
  a.click();
  URL.revokeObjectURL(url);
}

// --- Verdrahtung -------------------------------------------------------------

$("#c-run").addEventListener("click", runCheck);
$("#c-refresh").addEventListener("click", loadAudit);
$("#c-csv").addEventListener("click", exportCsv);

loadAudit();
