# Projekt 3: React + TypeScript

Zum dritten Mal dieselbe Aufgabenliste – jetzt mit **React**, dem weltweit am
meisten verbreiteten Frontend-Framework. Wenn du Projekt 2 (Vue) verstanden
hast, wird dir hier vieles bekannt vorkommen.

## ▶️ So startest du

```bash
cd 03-react
npm install     # einmalig: lädt React & Werkzeuge herunter
npm run dev     # startet die App
```

Danach öffnest du die angezeigte Adresse (z.B. `http://localhost:5173/`).

Weitere Befehle:

```bash
npm run build   # erstellt die fertige Version (Ordner dist/)
npm run preview # zeigt die gebaute Version an
```

## 🆚 Vue vs. React – dieselben Ideen, andere Worte

| Idee | Vue (Projekt 2) | React (Projekt 3) |
|------|------------------|--------------------|
| Reaktiver Zustand | `const x = ref(0)` | `const [x, setX] = useState(0)` |
| Wert anzeigen | `{{ x }}` | `{x}` |
| Liste rendern | `v-for="t in todos"` | `todos.map(t => ...)` |
| Eingabefeld binden | `v-model="text"` | `value={text} onChange={...}` |
| Auf Klick reagieren | `@click="..."` | `onClick={...}` |
| Nach Änderung etwas tun | `watch(...)` | `useEffect(...)` |

**Wichtiger Unterschied:** In React änderst du den State nie direkt. Du rufst
immer die `set...`-Funktion mit einem **neuen** Wert auf (achte im Code auf das
`...`, den sogenannten Spread-Operator). Vue erlaubt dagegen direkte Änderungen
wie `todos.value.push(...)`.

## 🔑 Konzepte in `src/App.tsx`

- **`useState`** – speichert reaktiven Zustand.
- **`useEffect`** – führt Code aus, nachdem sich etwas geändert hat (z.B. speichern).
- **JSX** – die HTML-ähnliche Syntax direkt im JavaScript/TypeScript.
- **Props & Komponenten** – hier haben wir nur eine Komponente (`App`); in
  größeren Apps zerlegt man die Oberfläche in viele kleine Komponenten.

## 💪 Übung

Du hast jetzt dieselbe App dreimal gesehen (pur, Vue, React). Als Nächstes
kommt etwas ganz anderes: Projekt 4 baut einen **Server**, der die Aufgaben
nicht nur im Browser, sondern zentral speichert.
