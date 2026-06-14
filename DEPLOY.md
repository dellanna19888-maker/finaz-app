# Deployment – finaz-app als öffentliches Web-Tool

Ziel: eine öffentliche URL, hinter der **Finanz-App + KI-Assistent + Notizen +
Compliance** laufen, mit **deinem eigenen** Anthropic-API-Key (als Secret).

> ⚠ Der API-Key gehört **niemals** ins Repository. Immer als Secret/Umgebungs-
> variable beim Hosting setzen.

Der Server liefert das gebaute Frontend (`dist/`) **und** die API (`/api/...`)
auf demselben Port aus – es wird also nur **ein** Dienst deployed.

---

## Option A – Render (empfohlen, kostenloser Tier)

1. Konto auf <https://render.com> anlegen und GitHub verbinden.
2. **New + → Blueprint** wählen und das Repo `finaz-app` auswählen.
   Render liest `render.yaml` (Build: `npm ci --include=dev && npm run build`,
   Start: `npm run api`, Health-Check: `/api/health`).
3. Unter **Environment** die Variable **`ANTHROPIC_API_KEY`** = dein Key
   (`sk-ant-...`) als Secret setzen. Optional `CLAUDE_MODEL` anpassen.
4. **Deploy** – nach dem Build bekommst du eine URL wie
   `https://finaz-app.onrender.com`.

Mit gesetztem Server-Key funktioniert die KI sofort für jeden Besucher.
Ohne Server-Key kann jede Person ihren eigenen Key unter **⚙️ Einstellungen**
eintragen (Bring Your Own Key).

> Kein `render.yaml`-Flow? Stattdessen **New + → Web Service**, Repo wählen,
> Build `npm ci --include=dev && npm run build`, Start `npm run api`,
> Health-Check-Pfad `/api/health`, dann den Key als Env-Var setzen.

---

## Option B – Docker (jeder Container-Host)

```bash
docker build -t finaz-app .
docker run -p 3001:3001 -e ANTHROPIC_API_KEY=sk-ant-... finaz-app
# → http://localhost:3001
```

Dasselbe Image läuft auf Fly.io, Railway, Google Cloud Run, Azure, AWS usw.
Den Key dort jeweils als Secret/Umgebungsvariable `ANTHROPIC_API_KEY` setzen.
Der Server bindet automatisch an `PORT` (Fallback 3001).

---

## Option C – getrenntes Hosting (Frontend statisch + Backend separat)

- Frontend: `npm run build` → `dist/` z. B. auf GitHub Pages / Netlify.
- Backend: `server/` separat hosten (Render/Fly/...), Key als Secret.
- Wichtig: Das Frontend ruft `/api/...` **relativ** auf. Bei getrenntem Hosting
  entweder per Reverse-Proxy auf denselben Origin legen oder im Frontend die
  API-Basis-URL ergänzen (kleine Anpassung in `src/lib/assist.ts`). Für den
  Anfang sind Option A/B (ein Dienst) deutlich einfacher.

---

## Hinweise

- **Nur das Wurzelprojekt** (finaz-app) wird deployed. Das eigenständige Projekt
  unter `ai-markdown/` ist davon unabhängig.
- BYOK im Browser ist für lokale/private Nutzung gedacht. Öffentlich gehostet:
  lieber Server-Key (Secret) nutzen.
- Audit-Logs werden in `server/logs/` geschrieben (flüchtig auf vielen Hosts –
  bei Bedarf ein Volume/persistentes Verzeichnis über `COMPLIANCE_LOG_DIR`).
