// ============================================================
//  Aufgabenliste – Projekt 1: Web-Grundlagen (Logik)
// ============================================================
// Diese Datei enthält die LOGIK der App in reinem JavaScript.
// Ohne Framework müssen wir alles selbst machen: auf Klicks
// reagieren und die Liste von Hand neu aufbauen. Genau das
// nehmen dir Vue (Projekt 2) und React (Projekt 3) später ab.

// 1) Wir holen uns die HTML-Elemente, mit denen wir arbeiten.
//    "document.querySelector" findet ein Element anhand seiner id (#).
const form = document.querySelector("#todo-form");
const input = document.querySelector("#todo-input");
const list = document.querySelector("#todo-list");
const counter = document.querySelector("#counter");

// 2) Hier leben unsere Aufgaben. Eine Aufgabe ist ein Objekt:
//    { id: 123, text: "Einkaufen", erledigt: false }
//    Beim Start laden wir gespeicherte Aufgaben aus dem Browser.
let todos = ladeTodos();

// 3) Wenn das Formular abgeschickt wird (Button oder Enter-Taste),
//    legen wir eine neue Aufgabe an.
form.addEventListener("submit", (event) => {
  event.preventDefault(); // verhindert das automatische Neuladen der Seite

  const text = input.value.trim(); // Leerzeichen am Rand entfernen
  if (text === "") return; // leere Eingaben ignorieren

  // Neue Aufgabe ans Ende der Liste hängen
  todos.push({
    id: Date.now(), // die aktuelle Uhrzeit in Millisekunden = eindeutige ID
    text: text,
    erledigt: false,
  });

  input.value = ""; // Eingabefeld leeren
  speichereTodos();
  zeichneListe();
});

// 4) Klicks innerhalb der Liste behandeln.
//    Wir hängen EINEN Listener an die ganze Liste und schauen dann,
//    worauf genau geklickt wurde. Das nennt man "Event Delegation".
list.addEventListener("click", (event) => {
  const li = event.target.closest("li"); // das <li>, in dem geklickt wurde
  if (!li) return;

  const id = Number(li.dataset.id); // die id der Aufgabe (aus data-id)

  // Wurde die Checkbox geklickt? -> Erledigt-Status umschalten
  if (event.target.matches('input[type="checkbox"]')) {
    const todo = todos.find((t) => t.id === id);
    todo.erledigt = !todo.erledigt;
  }

  // Wurde der Löschen-Button geklickt? -> Aufgabe entfernen
  if (event.target.matches(".loeschen")) {
    todos = todos.filter((t) => t.id !== id);
  }

  speichereTodos();
  zeichneListe();
});

// 5) Die Liste im HTML komplett neu aufbauen.
//    Ohne Framework müssen wir das selbst tun, sobald sich etwas ändert.
function zeichneListe() {
  list.innerHTML = ""; // alte Einträge entfernen

  for (const todo of todos) {
    const li = document.createElement("li");
    li.dataset.id = todo.id; // wird zu data-id="..." im HTML
    li.className = todo.erledigt ? "erledigt" : "";

    li.innerHTML = `
      <label>
        <input type="checkbox" ${todo.erledigt ? "checked" : ""} />
        <span>${escapeHtml(todo.text)}</span>
      </label>
      <button class="loeschen" aria-label="Löschen">✕</button>
    `;

    list.appendChild(li);
  }

  // Den Zähler aktualisieren
  const offen = todos.filter((t) => !t.erledigt).length;
  counter.textContent = `${offen} offen / ${todos.length} gesamt`;
}

// 6) Speichern & Laden über "localStorage".
//    localStorage ist ein kleiner Speicher im Browser. So bleiben
//    deine Aufgaben erhalten, auch wenn du die Seite neu lädst.
function speichereTodos() {
  localStorage.setItem("meine-todos", JSON.stringify(todos));
}

function ladeTodos() {
  const gespeichert = localStorage.getItem("meine-todos");
  // Wenn etwas gespeichert ist: aus Text zurück in ein Array wandeln.
  return gespeichert ? JSON.parse(gespeichert) : [];
}

// Kleiner Helfer: macht Eingaben sicher, falls jemand z.B. "<b>" eintippt.
// So wird der Text immer als Text angezeigt und nicht als HTML ausgeführt.
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// 7) Beim Start einmal die (geladene) Liste zeichnen.
zeichneListe();
