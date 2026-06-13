<script setup lang="ts">
// ============================================================
//  Aufgabenliste – Projekt 2: Vue 3 + TypeScript
// ============================================================
// Vergleiche das hier mit Projekt 1 (app.js)! Der große
// Unterschied: Wir bauen die Liste NICHT mehr von Hand. Wir
// beschreiben nur noch, WIE die Anzeige aussehen soll – Vue
// aktualisiert sie automatisch, sobald sich die Daten ändern.

import { ref, computed, watch } from 'vue'

// Mit TypeScript beschreiben wir den Typ einer Aufgabe.
// So warnt uns der Editor sofort, wenn wir z.B. ein Feld vertippen.
interface Todo {
  id: number
  text: string
  erledigt: boolean
}

// "ref" macht eine Variable REAKTIV. Ändert sich ihr Wert,
// aktualisiert Vue automatisch die Anzeige im <template> unten.
const todos = ref<Todo[]>(ladeTodos())
const neuerText = ref('')

// "computed" berechnet einen Wert automatisch neu,
// sobald sich todos ändert (hier: Anzahl offener Aufgaben).
const offeneAnzahl = computed(
  () => todos.value.filter((t) => !t.erledigt).length,
)

// Eine neue Aufgabe hinzufügen.
function hinzufuegen() {
  const text = neuerText.value.trim()
  if (text === '') return

  todos.value.push({
    id: Date.now(),
    text,
    erledigt: false,
  })
  neuerText.value = '' // Eingabefeld leeren
}

// Eine Aufgabe entfernen.
function entfernen(id: number) {
  todos.value = todos.value.filter((t) => t.id !== id)
}

// "watch" beobachtet die Aufgabenliste und speichert sie bei
// JEDER Änderung im Browser (localStorage).
watch(
  todos,
  (neueListe) => {
    localStorage.setItem('vue-todos', JSON.stringify(neueListe))
  },
  { deep: true },
)

function ladeTodos(): Todo[] {
  const gespeichert = localStorage.getItem('vue-todos')
  return gespeichert ? JSON.parse(gespeichert) : []
}
</script>

<template>
  <main class="card">
    <h1>📝 Meine Aufgaben</h1>
    <p class="untertitel">Gebaut mit Vue 3 + TypeScript</p>

    <!-- @submit.prevent = bei Absenden NICHT die Seite neu laden -->
    <form @submit.prevent="hinzufuegen">
      <!-- v-model verbindet das Eingabefeld mit der Variable neuerText.
           Tippt der Nutzer, ändert sich neuerText automatisch – und umgekehrt. -->
      <input
        v-model="neuerText"
        type="text"
        placeholder="Was möchtest du erledigen?"
        autocomplete="off"
      />
      <button type="submit">Hinzufügen</button>
    </form>

    <p class="counter">{{ offeneAnzahl }} offen / {{ todos.length }} gesamt</p>

    <ul>
      <!-- v-for wiederholt dieses <li> automatisch für jede Aufgabe.
           Das mussten wir in Projekt 1 noch per Schleife selbst bauen! -->
      <li
        v-for="todo in todos"
        :key="todo.id"
        :class="{ erledigt: todo.erledigt }"
      >
        <label>
          <input type="checkbox" v-model="todo.erledigt" />
          <span>{{ todo.text }}</span>
        </label>
        <button class="loeschen" aria-label="Löschen" @click="entfernen(todo.id)">
          ✕
        </button>
      </li>
    </ul>
  </main>
</template>

<!-- "scoped" bedeutet: Diese Stile gelten NUR für diese Komponente.
     Das ist eine praktische Vue-Funktion. -->
<style scoped>
.card {
  background: #ffffff;
  width: 100%;
  max-width: 480px;
  padding: 2rem;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

h1 {
  font-size: 1.6rem;
  color: #1e1b4b;
}

.untertitel {
  color: #6b7280;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
}

form {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

input[type='text'] {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 1rem;
  outline: none;
}

input[type='text']:focus {
  border-color: #42b883;
}

button[type='submit'] {
  padding: 0.75rem 1.25rem;
  background: #42b883; /* das typische Vue-Grün */
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  cursor: pointer;
}

button[type='submit']:hover {
  background: #369870;
}

.counter {
  font-size: 0.85rem;
  color: #9ca3af;
  margin-bottom: 0.75rem;
}

ul {
  list-style: none;
}

li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.75rem 0.5rem;
  border-bottom: 1px solid #f3f4f6;
}

li label {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  cursor: pointer;
  flex: 1;
}

li input[type='checkbox'] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

li.erledigt span {
  text-decoration: line-through;
  color: #9ca3af;
}

.loeschen {
  background: transparent;
  border: none;
  color: #ef4444;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
}

.loeschen:hover {
  background: #fef2f2;
}
</style>
