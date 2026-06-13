// ============================================================
//  Aufgabenliste – Projekt 3: React + TypeScript
// ============================================================
// Dieselbe App wie in Projekt 2 (Vue), nur in React-Schreibweise.
// Vergleiche beide! Das Grundprinzip ist gleich: Wir verwalten
// Daten ("State") und beschreiben, wie die Anzeige aussehen soll.
// React aktualisiert die Anzeige automatisch, wenn sich der State ändert.

import { useState, useEffect } from 'react'

// Mit TypeScript beschreiben wir den Typ einer Aufgabe.
interface Todo {
  id: number
  text: string
  erledigt: boolean
}

function ladeTodos(): Todo[] {
  const gespeichert = localStorage.getItem('react-todos')
  return gespeichert ? JSON.parse(gespeichert) : []
}

function App() {
  // "useState" ist Reacts Weg, reaktiven Zustand zu speichern.
  // Es gibt den aktuellen Wert (todos) und eine Funktion zum Ändern (setTodos).
  // In Vue hieß das "ref" – das Prinzip ist dasselbe.
  const [todos, setTodos] = useState<Todo[]>(ladeTodos)
  const [neuerText, setNeuerText] = useState('')

  // "useEffect" läuft, nachdem sich todos geändert hat.
  // Hier nutzen wir das, um die Liste im Browser zu speichern.
  useEffect(() => {
    localStorage.setItem('react-todos', JSON.stringify(todos))
  }, [todos])

  // Ein normaler Wert, der bei jedem Rendern neu berechnet wird.
  const offeneAnzahl = todos.filter((t) => !t.erledigt).length

  function hinzufuegen(event: React.FormEvent) {
    event.preventDefault() // Seite NICHT neu laden
    const text = neuerText.trim()
    if (text === '') return

    // In React ändern wir State nie direkt, sondern erstellen ein
    // NEUES Array (hier mit "..." = Spread) und übergeben es an setTodos.
    setTodos([...todos, { id: Date.now(), text, erledigt: false }])
    setNeuerText('')
  }

  function umschalten(id: number) {
    setTodos(
      todos.map((t) => (t.id === id ? { ...t, erledigt: !t.erledigt } : t)),
    )
  }

  function entfernen(id: number) {
    setTodos(todos.filter((t) => t.id !== id))
  }

  // Das hier ist "JSX": HTML-ähnlicher Code direkt in JavaScript.
  return (
    <main className="card">
      <h1>📝 Meine Aufgaben</h1>
      <p className="untertitel">Gebaut mit React + TypeScript</p>

      <form onSubmit={hinzufuegen}>
        {/* Der Wert des Feldes kommt aus dem State, onChange schreibt zurück */}
        <input
          type="text"
          value={neuerText}
          onChange={(e) => setNeuerText(e.target.value)}
          placeholder="Was möchtest du erledigen?"
          autoComplete="off"
        />
        <button type="submit">Hinzufügen</button>
      </form>

      <p className="counter">
        {offeneAnzahl} offen / {todos.length} gesamt
      </p>

      <ul>
        {/* .map() erzeugt für jede Aufgabe ein <li> – Reacts Variante von v-for */}
        {todos.map((todo) => (
          <li key={todo.id} className={todo.erledigt ? 'erledigt' : ''}>
            <label>
              <input
                type="checkbox"
                checked={todo.erledigt}
                onChange={() => umschalten(todo.id)}
              />
              <span>{todo.text}</span>
            </label>
            <button
              className="loeschen"
              aria-label="Löschen"
              onClick={() => entfernen(todo.id)}
            >
              ✕
            </button>
          </li>
        ))}
      </ul>
    </main>
  )
}

export default App
