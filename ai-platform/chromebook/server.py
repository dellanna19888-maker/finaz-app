"""
KI-Plattform — Chromebook Single-File Server
Kein Node.js nötig. Start: python server.py
"""
import os, uuid, json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

import httpx
import aiofiles
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List

# ──────────────────────────────────────────────────────────────────────────────
# Hugging Face Inference API
# ──────────────────────────────────────────────────────────────────────────────
HF_API = "https://api-inference.huggingface.co/models"


def _hf_headers():
    token = os.getenv("HUGGINGFACE_TOKEN", "")
    if not token or token == "hf_deinTokenHier":
        raise HTTPException(503, "⚠️ Kein HF-Token gesetzt. Bitte in .env eintragen.")
    return {"Authorization": f"Bearer {token}"}


async def hf_json(model: str, payload: dict, timeout=35.0):
    async with httpx.AsyncClient(timeout=timeout) as c:
        r = await c.post(f"{HF_API}/{model}", json=payload, headers=_hf_headers())
        if r.status_code == 503:
            raise HTTPException(503, "Modell lädt gerade, 20 Sek. warten und nochmal versuchen.")
        if not r.is_success:
            raise HTTPException(r.status_code, f"HF-Fehler: {r.text[:300]}")
        return r.json()


async def hf_bytes(model: str, data: bytes, timeout=35.0):
    async with httpx.AsyncClient(timeout=timeout) as c:
        r = await c.post(f"{HF_API}/{model}", content=data,
                         headers={**_hf_headers(), "Content-Type": "application/octet-stream"})
        if r.status_code == 503:
            raise HTTPException(503, "Modell lädt, bitte warten.")
        if not r.is_success:
            raise HTTPException(r.status_code, f"HF-Fehler: {r.text[:300]}")
        return r.json()


# ──────────────────────────────────────────────────────────────────────────────
# In-memory document store
# ──────────────────────────────────────────────────────────────────────────────
DOCS: dict = {}
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# ──────────────────────────────────────────────────────────────────────────────
# FastAPI App
# ──────────────────────────────────────────────────────────────────────────────
app = FastAPI(title="KI-Plattform Chromebook")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])


# ──────────────────────────────────────────────────────────────────────────────
# Frontend HTML (eingebettet — kein Node.js nötig)
# ──────────────────────────────────────────────────────────────────────────────
HTML = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>KI-Plattform</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0f0f1a;--card:#1a1a2e;--border:#2d2d4a;
  --primary:#6366f1;--light:#a5b4fc;--green:#10b981;
  --text:#e2e8f0;--muted:#94a3b8;--r:12px;
}
body{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;display:flex}
a{color:var(--light);text-decoration:none}
button{cursor:pointer;font-family:inherit}
input,textarea,select{font-family:inherit;background:#0f0f1a;color:var(--text);border:1px solid var(--border);border-radius:8px;padding:.55rem .85rem;font-size:.9rem;outline:none;width:100%;transition:border .2s}
input:focus,textarea:focus,select:focus{border-color:var(--primary)}
.btn{display:inline-flex;align-items:center;gap:.4rem;padding:.55rem 1.1rem;border-radius:8px;border:none;font-size:.9rem;font-weight:600;transition:all .2s;cursor:pointer}
.btn-p{background:var(--primary);color:#fff}.btn-p:hover{filter:brightness(.9)}
.btn-s{background:transparent;color:var(--light);border:1px solid var(--primary)}.btn-s:hover{background:rgba(99,102,241,.1)}
.btn:disabled{opacity:.4;cursor:not-allowed}
/* layout */
nav{width:200px;background:var(--card);border-right:1px solid var(--border);display:flex;flex-direction:column;flex-shrink:0}
.nav-logo{padding:1.2rem 1rem;font-size:1rem;font-weight:700;background:linear-gradient(135deg,var(--light),var(--green));-webkit-background-clip:text;-webkit-text-fill-color:transparent;border-bottom:1px solid var(--border)}
.nav-item{display:flex;align-items:center;gap:.6rem;padding:.6rem 1rem;color:var(--muted);cursor:pointer;transition:all .2s;font-size:.88rem}
.nav-item:hover{background:rgba(99,102,241,.08);color:var(--text)}
.nav-item.active{background:rgba(99,102,241,.15);color:var(--light);border-left:3px solid var(--primary)}
.nav-icon{font-size:1.1rem}
main{flex:1;padding:2rem;overflow-y:auto}
/* cards */
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:1.25rem;margin-bottom:1rem}
.page-title{font-size:1.6rem;font-weight:800;margin-bottom:.3rem}
.subtitle{color:var(--muted);margin-bottom:1.5rem;font-size:.9rem}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:1rem}
@media(max-width:700px){.grid2{grid-template-columns:1fr}nav{display:none}.mobile-bar{display:flex!important}}
.fg{display:flex;flex-direction:column;gap:.35rem;margin-bottom:.85rem}
.fg label{font-size:.75rem;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;font-weight:600}
/* chat */
#chat-messages{height:380px;overflow-y:auto;display:flex;flex-direction:column;gap:.75rem;padding:.5rem 0;margin-bottom:1rem}
.msg{display:flex;gap:.6rem;max-width:80%;align-items:flex-end}
.msg.user{flex-direction:row-reverse;align-self:flex-end}
.msg-bubble{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:.65rem .9rem;font-size:.9rem;line-height:1.5;white-space:pre-wrap;word-break:break-word}
.msg.user .msg-bubble{background:rgba(99,102,241,.18);border-color:var(--primary)}
.msg-av{font-size:1.3rem;flex-shrink:0}
.typing span{display:inline-block;width:7px;height:7px;background:var(--light);border-radius:50%;animation:bop 1.2s infinite;margin:0 2px}
.typing span:nth-child(2){animation-delay:.2s}.typing span:nth-child(3){animation-delay:.4s}
@keyframes bop{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-6px)}}
.chat-row{display:flex;gap:.5rem}
/* bars */
.bar-row{display:grid;grid-template-columns:140px 1fr 48px;align-items:center;gap:.4rem;margin-bottom:.4rem}
.bar-track{background:var(--border);border-radius:4px;height:7px;overflow:hidden}
.bar-fill{height:100%;background:linear-gradient(90deg,var(--primary),var(--green));border-radius:4px;transition:width .5s}
.bar-label{font-size:.82rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar-score{font-size:.78rem;color:var(--muted);text-align:right}
/* misc */
.top-badge{background:rgba(99,102,241,.15);border:1px solid var(--primary);border-radius:8px;padding:.5rem 1rem;display:flex;justify-content:space-between;align-items:center;margin-bottom:.75rem}
.top-label{color:var(--light);font-weight:700;font-size:1rem}
.top-score{color:var(--green);font-weight:800;font-size:1.1rem}
.drop{border:2px dashed var(--border);border-radius:var(--r);padding:1.5rem;text-align:center;cursor:pointer;transition:all .2s;min-height:120px;display:flex;align-items:center;justify-content:center;margin-bottom:.75rem}
.drop:hover,.drop.over{border-color:var(--primary);background:rgba(99,102,241,.05)}
.drop p{color:var(--muted);font-size:.85rem;margin-top:.3rem}
.hint{font-size:.75rem;color:var(--muted)}
.err{background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.3);border-radius:8px;padding:.4rem .7rem;color:#f87171;font-size:.82rem;margin-top:.5rem}
.ok{background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.3);border-radius:8px;padding:.4rem .7rem;color:#34d399;font-size:.82rem;margin-top:.5rem}
.hidden{display:none!important}
::-webkit-scrollbar{width:5px}::-webkit-scrollbar-track{background:var(--bg)}::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}
</style>
</head>
<body>

<nav id="sidebar">
  <div class="nav-logo">🧠 KI-Plattform</div>
  <div class="nav-item active" onclick="show('dashboard')" id="n-dashboard"><span class="nav-icon">📊</span>Dashboard</div>
  <div class="nav-item" onclick="show('chat')" id="n-chat"><span class="nav-icon">💬</span>Chat</div>
  <div class="nav-item" onclick="show('text')" id="n-text"><span class="nav-icon">📝</span>Text-Analyse</div>
  <div class="nav-item" onclick="show('image')" id="n-image"><span class="nav-icon">🖼️</span>Bild-Erkennung</div>
  <div class="nav-item" onclick="show('docs')" id="n-docs"><span class="nav-icon">📄</span>Dokumente</div>
  <div class="nav-item" onclick="show('settings')" id="n-settings"><span class="nav-icon">⚙️</span>Einstellungen</div>
</nav>

<main>

<!-- DASHBOARD -->
<div id="page-dashboard">
  <div class="page-title">🧠 KI-Plattform</div>
  <div class="subtitle">Chromebook Demo — läuft komplett lokal</div>
  <div class="grid2">
    <div class="card" style="cursor:pointer" onclick="show('chat')"><div style="font-size:2rem">💬</div><b>Chat / Assistent</b><p class="hint" style="margin-top:.3rem">Gespräch mit KI für Gesundheit, E-Commerce, Bildung</p></div>
    <div class="card" style="cursor:pointer" onclick="show('text')"><div style="font-size:2rem">📝</div><b>Text-Analyse</b><p class="hint" style="margin-top:.3rem">Texte klassifizieren &amp; Stimmung erkennen</p></div>
    <div class="card" style="cursor:pointer" onclick="show('image')"><div style="font-size:2rem">🖼️</div><b>Bild-Erkennung</b><p class="hint" style="margin-top:.3rem">Bilder automatisch analysieren</p></div>
    <div class="card" style="cursor:pointer" onclick="show('docs')"><div style="font-size:2rem">📄</div><b>Dokument-Analyse</b><p class="hint" style="margin-top:.3rem">PDFs zusammenfassen &amp; befragen</p></div>
  </div>
  <div class="card" id="status-card">
    <b>Server-Status</b>
    <div id="status-msg" style="color:var(--muted);font-size:.88rem;margin-top:.4rem">Prüfe Verbindung...</div>
  </div>
</div>

<!-- CHAT -->
<div id="page-chat" class="hidden">
  <div class="page-title">💬 Chat</div>
  <div class="subtitle">Stelle Fragen — wähle deinen Bereich</div>
  <div class="card">
    <div class="fg">
      <label>Bereich</label>
      <select id="chat-domain">
        <option value="general">🤖 Allgemein</option>
        <option value="health">🏥 Gesundheit</option>
        <option value="ecommerce">🛍️ E-Commerce</option>
        <option value="education">📚 Bildung</option>
      </select>
    </div>
    <div id="chat-messages"></div>
    <div class="chat-row">
      <textarea id="chat-input" rows="2" placeholder="Schreib eine Nachricht... (Enter = Senden)"></textarea>
      <button class="btn btn-p" id="chat-send" onclick="chatSend()" style="align-self:flex-end;flex-shrink:0">➤</button>
    </div>
    <div id="chat-err" class="err hidden"></div>
    <div class="hint" style="margin-top:.3rem">Enter = Senden · Shift+Enter = neue Zeile</div>
  </div>
</div>

<!-- TEXT -->
<div id="page-text" class="hidden">
  <div class="page-title">📝 Text-Analyse</div>
  <div class="subtitle">Texte klassifizieren oder Stimmung erkennen</div>
  <div class="grid2">
    <div class="card">
      <div class="fg"><label>Bereich</label>
        <select id="text-domain" onchange="loadLabels()">
          <option value="general">🤖 Allgemein</option>
          <option value="health">🏥 Gesundheit</option>
          <option value="ecommerce">🛍️ E-Commerce</option>
          <option value="education">📚 Bildung</option>
        </select>
      </div>
      <div class="fg"><label>Text</label><textarea id="text-input" rows="5" placeholder="Gib Text ein..."></textarea></div>
      <div class="fg"><label>Eigene Kategorien (optional, Komma-getrennt)</label><input id="text-labels" placeholder="z.B. Gut, Schlecht, Neutral"></div>
      <div style="display:flex;gap:.5rem;flex-wrap:wrap">
        <button class="btn btn-p" onclick="textClassify()">🔍 Klassifizieren</button>
        <button class="btn btn-s" onclick="textSentiment()">😊 Stimmung</button>
      </div>
      <div id="text-err" class="err hidden"></div>
      <div id="text-labels-info" style="margin-top:.75rem;font-size:.8rem;color:var(--muted)"></div>
    </div>
    <div class="card">
      <div id="text-result-empty" style="text-align:center;color:var(--muted);padding:3rem 0">📊<br><br>Ergebnis erscheint hier</div>
      <div id="text-result" class="hidden"></div>
    </div>
  </div>
</div>

<!-- IMAGE -->
<div id="page-image" class="hidden">
  <div class="page-title">🖼️ Bild-Erkennung</div>
  <div class="subtitle">Lade ein Bild hoch zur Analyse</div>
  <div class="grid2">
    <div class="card">
      <div class="fg"><label>Bereich</label>
        <select id="img-domain">
          <option value="general">🤖 Allgemein</option>
          <option value="health">🏥 Gesundheit</option>
          <option value="ecommerce">🛍️ E-Commerce</option>
          <option value="education">📚 Bildung</option>
        </select>
      </div>
      <div class="fg"><label>Eigene Kategorien (optional)</label><input id="img-labels" placeholder="z.B. Katze, Hund, Vogel"></div>
      <div class="drop" id="img-drop" onclick="document.getElementById('img-file').click()"
           ondragover="event.preventDefault();this.classList.add('over')"
           ondragleave="this.classList.remove('over')"
           ondrop="imgDrop(event)">
        <div id="img-preview-wrap">
          <div>🖼️</div>
          <p>Bild hierher ziehen oder klicken</p>
          <p class="hint">JPG, PNG, WEBP</p>
        </div>
      </div>
      <input type="file" id="img-file" accept="image/*" style="display:none" onchange="imgSelect(event)">
      <button class="btn btn-p" id="img-btn" onclick="imgClassify()" disabled style="width:100%">🔍 Bild analysieren</button>
      <div id="img-err" class="err hidden"></div>
    </div>
    <div class="card">
      <div id="img-result-empty" style="text-align:center;color:var(--muted);padding:3rem 0">🔍<br><br>Ergebnis erscheint hier</div>
      <div id="img-result" class="hidden"></div>
    </div>
  </div>
</div>

<!-- DOCS -->
<div id="page-docs" class="hidden">
  <div class="page-title">📄 Dokument-Analyse</div>
  <div class="subtitle">PDF oder TXT hochladen, zusammenfassen, befragen</div>
  <div class="grid2">
    <div class="card">
      <div class="drop" id="doc-drop" onclick="document.getElementById('doc-file').click()"
           ondragover="event.preventDefault();this.classList.add('over')"
           ondragleave="this.classList.remove('over')"
           ondrop="docDrop(event)">
        <div id="doc-drop-inner">
          <div>📄</div>
          <p>PDF oder TXT hierher ziehen</p>
          <p class="hint">Bis 20 MB</p>
        </div>
      </div>
      <input type="file" id="doc-file" accept=".pdf,.txt" style="display:none" onchange="docSelect(event)">
      <div id="doc-info" class="hidden ok"></div>
      <div id="doc-err" class="err hidden"></div>
      <div id="doc-btns" class="hidden" style="display:none;gap:.5rem;flex-wrap:wrap">
        <button class="btn btn-p" onclick="docSummarize()">📋 Zusammenfassen</button>
        <button class="btn btn-s" onclick="document.getElementById('doc-qa-area').classList.remove('hidden')">❓ Fragen stellen</button>
        <button class="btn btn-s" onclick="docReset()">🗑 Neu</button>
      </div>
      <div id="doc-qa-area" class="hidden" style="margin-top:.75rem">
        <div class="chat-row">
          <input id="doc-question" placeholder="Deine Frage zum Dokument..." onkeydown="if(event.key==='Enter')docAsk()">
          <button class="btn btn-p" onclick="docAsk()" style="flex-shrink:0">➤</button>
        </div>
        <div id="doc-qa-result" style="margin-top:.5rem;font-size:.88rem"></div>
      </div>
    </div>
    <div class="card">
      <div id="doc-result-empty" style="text-align:center;color:var(--muted);padding:3rem 0">📄<br><br>Lade ein Dokument hoch</div>
      <div id="doc-result" class="hidden"></div>
    </div>
  </div>
</div>

<!-- SETTINGS -->
<div id="page-settings" class="hidden">
  <div class="page-title">⚙️ Einstellungen</div>
  <div class="subtitle">Hugging Face Token konfigurieren</div>
  <div class="card">
    <b>Hugging Face Token</b>
    <p style="color:var(--muted);font-size:.85rem;margin:.5rem 0 .75rem">
      Kostenlos erstellen: <a href="https://huggingface.co/settings/tokens" target="_blank">huggingface.co/settings/tokens</a>
    </p>
    <div class="fg">
      <label>Token (wird in .env gespeichert)</label>
      <input id="hf-token-input" type="password" placeholder="hf_..." />
    </div>
    <button class="btn btn-p" onclick="saveToken()">💾 Speichern & Testen</button>
    <div id="token-result" style="margin-top:.5rem;font-size:.85rem"></div>
  </div>
  <div class="card">
    <b>Verwendete Modelle (Hugging Face API)</b>
    <table style="width:100%;font-size:.82rem;margin-top:.5rem;border-collapse:collapse">
      <tr><td style="padding:.3rem .5rem;color:var(--muted)">Chat</td><td>mistralai/Mistral-7B-Instruct-v0.3</td></tr>
      <tr><td style="padding:.3rem .5rem;color:var(--muted)">Text</td><td>facebook/bart-large-mnli (Zero-Shot)</td></tr>
      <tr><td style="padding:.3rem .5rem;color:var(--muted)">Bild</td><td>openai/clip-vit-base-patch32 / google/vit-base-patch16-224</td></tr>
      <tr><td style="padding:.3rem .5rem;color:var(--muted)">Zusammenfassung</td><td>facebook/bart-large-cnn</td></tr>
      <tr><td style="padding:.3rem .5rem;color:var(--muted)">Frage & Antwort</td><td>deepset/roberta-base-squad2</td></tr>
    </table>
  </div>
</div>

</main>

<script>
// ── Navigation ────────────────────────────────────────────────────────────────
const PAGES=['dashboard','chat','text','image','docs','settings'];
function show(p){
  PAGES.forEach(x=>{
    document.getElementById('page-'+x).classList.toggle('hidden',x!==p);
    document.getElementById('n-'+x)?.classList.toggle('active',x===p);
  });
  if(p==='text') loadLabels();
}

// ── API helper ────────────────────────────────────────────────────────────────
async function api(path,opts={}){
  const r=await fetch('/api'+path,opts);
  const j=await r.json().catch(()=>({detail:r.statusText}));
  if(!r.ok) throw new Error(j.detail||'Fehler');
  return j;
}
function showErr(id,msg){const el=document.getElementById(id);el.textContent=msg;el.classList.remove('hidden')}
function hideErr(id){document.getElementById(id).classList.add('hidden')}

// ── Status check ─────────────────────────────────────────────────────────────
async function checkStatus(){
  try{
    const r=await fetch('/health');const j=await r.json();
    document.getElementById('status-msg').innerHTML=
      j.status==='healthy'
        ? '✅ Server läuft · <span style="color:var(--green)">Bereit</span>'
        : '⚠️ '+JSON.stringify(j);
  }catch{document.getElementById('status-msg').textContent='❌ Server nicht erreichbar'}
}
checkStatus();

// ── CHAT ──────────────────────────────────────────────────────────────────────
let chatHistory=[];
function chatMsg(role,text){
  const el=document.getElementById('chat-messages');
  const d=document.createElement('div');
  d.className='msg '+role;
  d.innerHTML=`<div class="msg-av">${role==='user'?'👤':'🤖'}</div>
    <div class="msg-bubble">${text.replace(/</g,'&lt;')}</div>`;
  el.appendChild(d);el.scrollTop=el.scrollHeight;
}
function chatTyping(){
  const el=document.getElementById('chat-messages');
  const d=document.createElement('div');d.id='typing';d.className='msg assistant';
  d.innerHTML='<div class="msg-av">🤖</div><div class="msg-bubble typing"><span></span><span></span><span></span></div>';
  el.appendChild(d);el.scrollTop=el.scrollHeight;
}
function removeTyping(){document.getElementById('typing')?.remove()}

document.getElementById('chat-input').addEventListener('keydown',e=>{
  if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();chatSend()}
});
async function chatSend(){
  const inp=document.getElementById('chat-input');
  const text=inp.value.trim();if(!text)return;
  inp.value='';hideErr('chat-err');
  chatHistory.push({role:'user',content:text});
  chatMsg('user',text);chatTyping();
  const btn=document.getElementById('chat-send');btn.disabled=true;
  try{
    const r=await api('/chat/',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({messages:chatHistory,domain:document.getElementById('chat-domain').value})});
    removeTyping();chatHistory.push({role:'assistant',content:r.reply});chatMsg('assistant',r.reply);
  }catch(e){removeTyping();showErr('chat-err',e.message)}
  finally{btn.disabled=false}
}

// ── TEXT ──────────────────────────────────────────────────────────────────────
async function loadLabels(){
  const d=document.getElementById('text-domain').value;
  try{const r=await api('/classify/text/labels/'+d);
    document.getElementById('text-labels-info').textContent='Kategorien: '+r.labels.join(' · ')}catch{}
}
function renderBars(results,containerId){
  const c=document.getElementById(containerId);
  c.innerHTML='';
  if(results[0]){
    const tb=document.createElement('div');tb.className='top-badge';
    tb.innerHTML=`<span class="top-label">${results[0].label}</span><span class="top-score">${(results[0].score*100).toFixed(1)}%</span>`;
    c.appendChild(tb);
  }
  results.slice(0,7).forEach(r=>{
    const row=document.createElement('div');row.className='bar-row';
    row.innerHTML=`<div class="bar-label" title="${r.label}">${r.label}</div>
      <div class="bar-track"><div class="bar-fill" style="width:${r.score*100}%"></div></div>
      <div class="bar-score">${(r.score*100).toFixed(1)}%</div>`;
    c.appendChild(row);
  });
}
async function textClassify(){
  const txt=document.getElementById('text-input').value.trim();if(!txt)return;
  hideErr('text-err');
  const lblRaw=document.getElementById('text-labels').value;
  const labels=lblRaw?lblRaw.split(',').map(l=>l.trim()).filter(Boolean):undefined;
  try{
    const r=await api('/classify/text/',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({text:txt,labels,domain:document.getElementById('text-domain').value})});
    document.getElementById('text-result-empty').classList.add('hidden');
    const res=document.getElementById('text-result');res.classList.remove('hidden');
    renderBars(r.results,'text-result');
  }catch(e){showErr('text-err',e.message)}
}
async function textSentiment(){
  const txt=document.getElementById('text-input').value.trim();if(!txt)return;
  hideErr('text-err');
  try{
    const r=await api('/classify/text/sentiment?text='+encodeURIComponent(txt.slice(0,512)),{method:'POST'});
    document.getElementById('text-result-empty').classList.add('hidden');
    document.getElementById('text-result').classList.remove('hidden');
    document.getElementById('text-result').innerHTML=
      `<div class="top-badge"><span class="top-label">${r.sentiment}</span><span class="top-score">${(r.score*100).toFixed(1)}%</span></div>`;
  }catch(e){showErr('text-err',e.message)}
}

// ── IMAGE ──────────────────────────────────────────────────────────────────────
let imgFile=null;
function imgSelect(e){const f=e.target.files[0];if(f)setImgFile(f)}
function imgDrop(e){e.preventDefault();document.getElementById('img-drop').classList.remove('over');const f=e.dataTransfer.files[0];if(f)setImgFile(f)}
function setImgFile(f){
  imgFile=f;
  const url=URL.createObjectURL(f);
  document.getElementById('img-preview-wrap').innerHTML=
    `<img src="${url}" style="max-width:100%;max-height:160px;object-fit:contain;border-radius:8px">`;
  document.getElementById('img-btn').disabled=false;
  hideErr('img-err');
}
async function imgClassify(){
  if(!imgFile)return;hideErr('img-err');
  const fd=new FormData();fd.append('file',imgFile);
  fd.append('domain',document.getElementById('img-domain').value);
  const lbl=document.getElementById('img-labels').value;if(lbl)fd.append('custom_labels',lbl);
  try{
    const r=await api('/classify/image/',{method:'POST',body:fd});
    document.getElementById('img-result-empty').classList.add('hidden');
    const res=document.getElementById('img-result');res.classList.remove('hidden');
    renderBars(r.results,'img-result');
    const badge=document.createElement('div');
    badge.innerHTML=`<div class="hint" style="margin-top:.5rem">Modus: ${r.mode}</div>`;
    res.appendChild(badge);
  }catch(e){showErr('img-err',e.message)}
}

// ── DOCUMENTS ──────────────────────────────────────────────────────────────────
let docId=null;
function docSelect(e){const f=e.target.files[0];if(f)uploadDoc(f)}
function docDrop(e){e.preventDefault();document.getElementById('doc-drop').classList.remove('over');const f=e.dataTransfer.files[0];if(f)uploadDoc(f)}
async function uploadDoc(f){
  hideErr('doc-err');
  const fd=new FormData();fd.append('file',f);
  try{
    const r=await api('/documents/upload',{method:'POST',body:fd});
    docId=r.document_id;
    const info=document.getElementById('doc-info');
    info.textContent=`✅ ${r.filename} — ${r.word_count.toLocaleString()} Wörter`;
    info.classList.remove('hidden');
    const btns=document.getElementById('doc-btns');btns.style.display='flex';btns.classList.remove('hidden');
    document.getElementById('doc-drop-inner').innerHTML=`<div>📄</div><p>${r.filename}</p>`;
  }catch(e){showErr('doc-err',e.message)}
}
async function docSummarize(){
  if(!docId)return;
  try{
    const r=await api('/documents/summarize/'+docId,{method:'POST'});
    document.getElementById('doc-result-empty').classList.add('hidden');
    const res=document.getElementById('doc-result');res.classList.remove('hidden');
    res.innerHTML=`<b>📋 Zusammenfassung</b><p style="margin-top:.5rem;line-height:1.7;color:var(--text)">${r.summary}</p>
      <div class="hint" style="margin-top:.5rem">${r.word_count.toLocaleString()} Wörter · ${r.char_count.toLocaleString()} Zeichen</div>`;
  }catch(e){showErr('doc-err',e.message)}
}
async function docAsk(){
  if(!docId)return;
  const q=document.getElementById('doc-question').value.trim();if(!q)return;
  try{
    const r=await api('/documents/qa',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({document_id:docId,question:q})});
    document.getElementById('doc-qa-result').innerHTML=
      `<b>❓ ${r.question}</b><br><span style="color:var(--green)">💡 ${r.answer}</span>
       <div class="hint">Konfidenz: ${(r.confidence*100).toFixed(1)}%</div>`;
  }catch(e){showErr('doc-err',e.message)}
}
function docReset(){docId=null;document.getElementById('doc-drop-inner').innerHTML='<div>📄</div><p>PDF oder TXT hierher ziehen</p><p class="hint">Bis 20 MB</p>';document.getElementById('doc-info').classList.add('hidden');document.getElementById('doc-btns').style.display='none';document.getElementById('doc-result').classList.add('hidden');document.getElementById('doc-result-empty').classList.remove('hidden');}

// ── SETTINGS ──────────────────────────────────────────────────────────────────
async function saveToken(){
  const t=document.getElementById('hf-token-input').value.trim();if(!t)return;
  try{
    const r=await api('/settings/token',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token:t})});
    document.getElementById('token-result').innerHTML='<span style="color:var(--green)">✅ '+r.message+'</span>';
  }catch(e){document.getElementById('token-result').innerHTML='<span style="color:#f87171">❌ '+e.message+'</span>'}
}
</script>
</body>
</html>"""


# ──────────────────────────────────────────────────────────────────────────────
# Routes: Frontend
# ──────────────────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def index():
    return HTML


@app.get("/health")
def health():
    return {"status": "healthy", "mode": "chromebook-single-file"}


# ──────────────────────────────────────────────────────────────────────────────
# Routes: Settings / Token
# ──────────────────────────────────────────────────────────────────────────────
class TokenRequest(BaseModel):
    token: str


@app.post("/api/settings/token")
async def set_token(req: TokenRequest):
    if not req.token.startswith("hf_"):
        raise HTTPException(400, "Token muss mit 'hf_' beginnen")
    env_path = Path(".env")
    if env_path.exists():
        content = env_path.read_text()
        if "HUGGINGFACE_TOKEN=" in content:
            lines = [
                f"HUGGINGFACE_TOKEN={req.token}" if l.startswith("HUGGINGFACE_TOKEN=") else l
                for l in content.splitlines()
            ]
            env_path.write_text("\n".join(lines) + "\n")
        else:
            env_path.write_text(content + f"\nHUGGINGFACE_TOKEN={req.token}\n")
    else:
        env_path.write_text(f"HUGGINGFACE_TOKEN={req.token}\n")
    os.environ["HUGGINGFACE_TOKEN"] = req.token
    return {"message": "Token gespeichert und aktiviert"}


# ──────────────────────────────────────────────────────────────────────────────
# Routes: Chat
# ──────────────────────────────────────────────────────────────────────────────
DOMAIN_SYSTEM = {
    "health":    "Du bist ein medizinischer Informationsassistent. Erkläre Begriffe verständlich. Weise immer auf einen Arztbesuch hin.",
    "ecommerce": "Du bist ein E-Commerce-Assistent. Hilf bei Produkten, Bewertungen und Kaufentscheidungen.",
    "education": "Du bist ein Lernassistent. Erkläre Konzepte klar und verständlich.",
    "general":   "Du bist ein hilfreicher Assistent. Antworte auf Deutsch.",
}


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    domain: Optional[str] = "general"


@app.post("/api/chat/")
async def chat(req: ChatRequest):
    last = next((m.content for m in reversed(req.messages) if m.role == "user"), "")
    system = DOMAIN_SYSTEM.get(req.domain or "general", DOMAIN_SYSTEM["general"])
    prompt = f"<s>[INST] {system}\n\n{last} [/INST]"
    result = await hf_json(
        "mistralai/Mistral-7B-Instruct-v0.3",
        {"inputs": prompt, "parameters": {"max_new_tokens": 350, "temperature": 0.7, "return_full_text": False}},
        timeout=45.0,
    )
    reply = result[0].get("generated_text", "").strip() if isinstance(result, list) else str(result)
    return {"reply": reply, "domain": req.domain}


# ──────────────────────────────────────────────────────────────────────────────
# Routes: Text Classification
# ──────────────────────────────────────────────────────────────────────────────
DOMAIN_LABELS = {
    "health":    ["Diagnose", "Symptome", "Medikamente", "Labor-Ergebnisse", "Behandlungsplan"],
    "ecommerce": ["Produktbeschreibung", "Positive Bewertung", "Negative Bewertung", "Reklamation"],
    "education": ["Mathematik", "Naturwissenschaften", "Geschichte", "Sprachen", "Informatik"],
    "general":   ["Positiv", "Negativ", "Neutral", "Frage", "Aussage"],
}


class TextRequest(BaseModel):
    text: str
    labels: Optional[List[str]] = None
    domain: Optional[str] = "general"
    multi_label: Optional[bool] = False


@app.post("/api/classify/text/")
async def classify_text(req: TextRequest):
    labels = req.labels or DOMAIN_LABELS.get(req.domain or "general", DOMAIN_LABELS["general"])
    r = await hf_json("facebook/bart-large-mnli",
                      {"inputs": req.text, "parameters": {"candidate_labels": labels, "multi_label": req.multi_label}})
    results = [{"label": l, "score": round(s, 4)} for l, s in zip(r["labels"], r["scores"])]
    return {"text": req.text, "results": results, "top_label": results[0]["label"] if results else "", "domain": req.domain}


@app.post("/api/classify/text/sentiment")
async def sentiment(text: str):
    r = await hf_json("cardiffnlp/twitter-roberta-base-sentiment-latest", {"inputs": text[:512]})
    top = r[0] if isinstance(r, list) else r
    mapping = {"positive": "Positiv 😊", "negative": "Negativ 😟", "neutral": "Neutral 😐"}
    return {"text": text, "sentiment": mapping.get(top["label"].lower(), top["label"]), "score": round(top["score"], 4)}


@app.get("/api/classify/text/labels/{domain}")
def text_labels(domain: str):
    return {"domain": domain, "labels": DOMAIN_LABELS.get(domain, DOMAIN_LABELS["general"])}


# ──────────────────────────────────────────────────────────────────────────────
# Routes: Image Classification
# ──────────────────────────────────────────────────────────────────────────────
IMG_DOMAIN_LABELS = {
    "health":    ["Röntgenbild", "CT-Scan", "MRT", "Ultraschall", "Hautbefund", "Medikament"],
    "ecommerce": ["Kleidung", "Elektronik", "Möbel", "Lebensmittel", "Spielzeug", "Sport"],
    "education": ["Diagramm", "Formel", "Karte", "Grafik", "Tabelle", "Dokument"],
    "general":   None,
}


@app.post("/api/classify/image/")
async def classify_image(
    file: UploadFile = File(...),
    domain: str = Form("general"),
    custom_labels: Optional[str] = Form(None),
):
    data = await file.read()
    labels = None
    if custom_labels:
        labels = [l.strip() for l in custom_labels.split(",") if l.strip()]
    else:
        labels = IMG_DOMAIN_LABELS.get(domain)

    if labels:
        r = await hf_bytes("openai/clip-vit-base-patch32", data)
        results = sorted(
            [{"label": x["label"], "score": round(x["score"], 4)} for x in (r if isinstance(r, list) else [])],
            key=lambda x: x["score"], reverse=True,
        )
        mode = "zero-shot (CLIP)"
    else:
        r = await hf_bytes("google/vit-base-patch16-224", data)
        results = [{"label": x["label"], "score": round(x["score"], 4)} for x in (r if isinstance(r, list) else [])][:8]
        mode = "imagenet (ViT)"

    return {"filename": file.filename, "results": results, "top_label": results[0]["label"] if results else "", "mode": mode}


# ──────────────────────────────────────────────────────────────────────────────
# Routes: Documents
# ──────────────────────────────────────────────────────────────────────────────
def _extract(path: str, filename: str) -> str:
    ext = filename.lower().rsplit(".", 1)[-1]
    if ext == "txt":
        return Path(path).read_text(encoding="utf-8", errors="ignore")
    if ext == "pdf":
        try:
            from pypdf import PdfReader
            return "\n".join(p.extract_text() or "" for p in PdfReader(path).pages)
        except Exception as e:
            raise HTTPException(400, f"PDF-Fehler: {e}")
    raise HTTPException(400, f"Format nicht unterstützt: .{ext}")


@app.post("/api/documents/upload")
async def doc_upload(file: UploadFile = File(...)):
    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(413, "Datei zu groß (max 20 MB)")
    ext = file.filename.lower().rsplit(".", 1)[-1]
    if ext not in {"txt", "pdf"}:
        raise HTTPException(400, "Nur .txt und .pdf erlaubt")
    doc_id = str(uuid.uuid4())
    path = UPLOAD_DIR / f"{doc_id}.{ext}"
    async with aiofiles.open(path, "wb") as f:
        await f.write(content)
    text = _extract(str(path), file.filename)
    DOCS[doc_id] = {"text": text, "filename": file.filename}
    return {"document_id": doc_id, "filename": file.filename, "size_bytes": len(content),
            "word_count": len(text.split()), "char_count": len(text)}


@app.post("/api/documents/summarize/{doc_id}")
async def doc_summarize(doc_id: str):
    if doc_id not in DOCS:
        raise HTTPException(404, "Dokument nicht gefunden")
    text = DOCS[doc_id]["text"][:1000]
    r = await hf_json("facebook/bart-large-cnn",
                      {"inputs": text, "parameters": {"max_length": 150, "min_length": 30}})
    summary = r[0]["summary_text"] if isinstance(r, list) else str(r)
    return {"filename": DOCS[doc_id]["filename"], "summary": summary,
            "word_count": len(DOCS[doc_id]["text"].split()), "char_count": len(DOCS[doc_id]["text"])}


class QARequest(BaseModel):
    document_id: str
    question: str


@app.post("/api/documents/qa")
async def doc_qa(req: QARequest):
    if req.document_id not in DOCS:
        raise HTTPException(404, "Dokument nicht gefunden")
    context = DOCS[req.document_id]["text"][:3000]
    r = await hf_json("deepset/roberta-base-squad2",
                      {"inputs": {"question": req.question, "context": context}})
    return {"question": req.question, "answer": r.get("answer", "Keine Antwort"),
            "confidence": round(r.get("score", 0), 4)}


# ──────────────────────────────────────────────────────────────────────────────
# Start
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    print(f"\n🧠 KI-Plattform startet auf http://localhost:{port}\n")
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
