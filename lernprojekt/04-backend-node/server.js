// ============================================================
//  Aufgabenliste – Projekt 4: Backend mit Node.js
// ============================================================
// Bisher lief alles nur im Browser. Jetzt bauen wir einen SERVER:
// ein Programm, das im Hintergrund läuft, Anfragen entgegennimmt
// und die Aufgaben zentral in einer Datei speichert.
//
// Wir benutzen NUR Node-Bordmittel – du musst NICHTS installieren!
//
//   Starten:            node server.js
//   Im Browser öffnen:  http://localhost:3000

import { createServer } from 'node:http'
import { readFile, writeFile, mkdir } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import { extname, join, dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const PORT = 3000

// Wo liegt dieses Skript? Daraus bauen wir die übrigen Pfade.
const __dirname = dirname(fileURLToPath(import.meta.url))
const DATA_FILE = join(__dirname, 'data', 'todos.json')
const PUBLIC_DIR = join(__dirname, 'public')

// --- Hilfsfunktionen: Aufgaben aus der Datei lesen / schreiben ---

async function ladeTodos() {
  if (!existsSync(DATA_FILE)) return []
  const inhalt = await readFile(DATA_FILE, 'utf-8')
  return JSON.parse(inhalt || '[]')
}

async function speichereTodos(todos) {
  await writeFile(DATA_FILE, JSON.stringify(todos, null, 2), 'utf-8')
}

// JSON als Antwort senden (mit Status-Code, z.B. 200 = OK)
function sendeJson(res, status, daten) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' })
  res.end(JSON.stringify(daten))
}

// Die mitgeschickten Daten (den "Body") einer Anfrage einlesen
function leseBody(req) {
  return new Promise((resolve) => {
    let daten = ''
    req.on('data', (stueck) => (daten += stueck))
    req.on('end', () => resolve(daten ? JSON.parse(daten) : {}))
  })
}

// --- Der eigentliche Server ---
// Für JEDE Anfrage aus dem Browser wird diese Funktion aufgerufen.

const server = createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`)
  const pfad = url.pathname

  // ---------- 1) Die API (alles unter /api/todos) ----------
  // Eine "API" ist eine Schnittstelle: feste Adressen, über die ein
  // Programm Daten abfragen und ändern kann. Die typischen Methoden:
  // GET = holen, POST = neu anlegen, PATCH = ändern, DELETE = löschen.

  if (pfad === '/api/todos' && req.method === 'GET') {
    return sendeJson(res, 200, await ladeTodos())
  }

  if (pfad === '/api/todos' && req.method === 'POST') {
    const body = await leseBody(req)
    const text = (body.text || '').trim()
    if (!text) return sendeJson(res, 400, { fehler: 'Text fehlt' })

    const todos = await ladeTodos()
    const neu = { id: Date.now(), text, erledigt: false }
    todos.push(neu)
    await speichereTodos(todos)
    return sendeJson(res, 201, neu) // 201 = "Neu angelegt"
  }

  // Routen MIT ID, z.B. /api/todos/1718000000000
  const treffer = pfad.match(/^\/api\/todos\/(\d+)$/)
  if (treffer) {
    const id = Number(treffer[1])
    let todos = await ladeTodos()

    if (req.method === 'PATCH') {
      const body = await leseBody(req)
      const todo = todos.find((t) => t.id === id)
      if (!todo) return sendeJson(res, 404, { fehler: 'Nicht gefunden' })
      todo.erledigt = body.erledigt
      await speichereTodos(todos)
      return sendeJson(res, 200, todo)
    }

    if (req.method === 'DELETE') {
      todos = todos.filter((t) => t.id !== id)
      await speichereTodos(todos)
      return sendeJson(res, 200, { ok: true })
    }
  }

  // ---------- 2) Statische Dateien (das Frontend in public/) ----------
  await sendeStatischeDatei(res, pfad)
})

// Liefert die HTML/CSS/JS-Dateien aus dem Ordner "public" aus.
async function sendeStatischeDatei(res, pfad) {
  const dateiPfad = join(PUBLIC_DIR, pfad === '/' ? 'index.html' : pfad)

  // Sicherheit: nicht aus dem public-Ordner "ausbrechen" lassen.
  if (!resolve(dateiPfad).startsWith(resolve(PUBLIC_DIR))) {
    res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' })
    return res.end('403 – Verboten')
  }

  if (!existsSync(dateiPfad)) {
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' })
    return res.end('404 – Datei nicht gefunden')
  }

  // Passenden Inhaltstyp anhand der Dateiendung wählen
  const typen = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'text/javascript; charset=utf-8',
  }
  const typ = typen[extname(dateiPfad)] || 'application/octet-stream'
  const inhalt = await readFile(dateiPfad)
  res.writeHead(200, { 'Content-Type': typ })
  res.end(inhalt)
}

// Sicherstellen, dass der data-Ordner existiert, dann Server starten.
await mkdir(dirname(DATA_FILE), { recursive: true })
server.listen(PORT, () => {
  console.log(`✅ Server läuft! Öffne im Browser:  http://localhost:${PORT}`)
})
