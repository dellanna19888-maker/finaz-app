# Projekt 2: Vue 3 + TypeScript

Dieselbe Aufgabenliste wie in Projekt 1 – aber jetzt mit einem **Framework**.
Vue nimmt dir die mühsame Arbeit ab, die Anzeige bei jeder Änderung von Hand
neu zu bauen.

## ▶️ So startest du

Anders als Projekt 1 braucht ein Framework einen kurzen Aufbau-Schritt:

```bash
cd 02-vue
npm install     # einmalig: lädt Vue & Werkzeuge herunter (dauert kurz)
npm run dev     # startet die App
```

Danach zeigt das Terminal eine Adresse an, z.B. `http://localhost:5173/`.
Öffne sie im Browser. Änderst du den Code, aktualisiert sich die Seite
**automatisch** (das nennt man „Hot Reload").

Weitere Befehle:

```bash
npm run build   # erstellt die fertige Version für den Einsatz (Ordner dist/)
npm run preview # zeigt die gebaute Version an
```

## 🆚 Der wichtigste Unterschied zu Projekt 1

In Projekt 1 mussten wir die Liste bei jeder Änderung selbst neu zeichnen
(`zeichneListe()`). In Vue ist das überflüssig:

| Projekt 1 (pur) | Projekt 2 (Vue) |
|-----------------|------------------|
| `todos.push(...)` **und** danach `zeichneListe()` aufrufen | nur `todos.value.push(...)` – Vue zeichnet selbst neu |
| `document.querySelector` + `innerHTML` | `v-for`, `v-model`, `{{ ... }}` direkt im Template |
| Klick-Logik mit `addEventListener` | `@click="..."` direkt am Element |

Das Zauberwort heißt **Reaktivität**: Vue beobachtet deine Daten und
aktualisiert die Anzeige automatisch.

## 🔑 Konzepte in `src/App.vue`

- **`ref(...)`** – macht eine Variable reaktiv.
- **`computed(...)`** – ein Wert, der sich automatisch neu berechnet.
- **`v-model`** – verbindet ein Eingabefeld mit einer Variable (beide Richtungen).
- **`v-for`** – wiederholt ein Element für jeden Eintrag einer Liste.
- **`@submit` / `@click`** – reagiert auf Ereignisse.
- **`<style scoped>`** – Stile, die nur für diese eine Komponente gelten.

## 💪 Übung

Schau dir als Nächstes Projekt 3 (React) an. Es macht **dasselbe** wie Vue,
nur mit anderer Schreibweise. Achte darauf, was sich ähnelt!
