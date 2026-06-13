// ============================================================
//  Frontend für Projekt 4 – spricht mit dem Server
// ============================================================
// Das sieht aus wie Projekt 1 – mit EINEM großen Unterschied:
// Statt im Browser (localStorage) zu speichern, schicken wir die
// Daten jetzt mit "fetch" an unseren Server. Der speichert sie in
// einer Datei. So sind die Aufgaben für ALLE gleich und bleiben
// auch dann erhalten, wenn du einen anderen Browser benutzt.

const form = document.querySelector("#todo-form");
const input = document.querySelector("#todo-input");
const list = document.querySelector("#todo-list");
const counter = document.querySelector("#counter");

// Beim Start: Aufgaben vom Server holen und anzeigen.
ladeUndZeichne();

// Neue Aufgabe -> per POST an den Server schicken.
form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (!text) return;

  await fetch("/api/todos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });

  input.value = "";
  ladeUndZeichne();
});

// Klick auf Checkbox (ändern) oder Löschen-Button.
list.addEventListener("click", async (event) => {
  const li = event.target.closest("li");
  if (!li) return;
  const id = Number(li.dataset.id);

  if (event.target.matches('input[type="checkbox"]')) {
    // Erledigt-Status ändern -> PATCH
    await fetch(`/api/todos/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ erledigt: event.target.checked }),
    });
  }

  if (event.target.matches(".loeschen")) {
    // Aufgabe löschen -> DELETE
    await fetch(`/api/todos/${id}`, { method: "DELETE" });
  }

  ladeUndZeichne();
});

// Aufgaben vom Server laden (GET) und die Liste neu zeichnen.
async function ladeUndZeichne() {
  const antwort = await fetch("/api/todos");
  const todos = await antwort.json();

  list.innerHTML = "";
  for (const todo of todos) {
    const li = document.createElement("li");
    li.dataset.id = todo.id;
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

  const offen = todos.filter((t) => !t.erledigt).length;
  counter.textContent = `${offen} offen / ${todos.length} gesamt`;
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
