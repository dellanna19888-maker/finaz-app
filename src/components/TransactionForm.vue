<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <h2>{{ editing ? 'Transaktion bearbeiten' : 'Neue Transaktion' }}</h2>

      <div class="type-toggle">
        <button :class="['toggle-btn', form.type === 'income' ? 'income-active' : '']" @click="form.type = 'income'">
          + Einnahme
        </button>
        <button :class="['toggle-btn', form.type === 'expense' ? 'expense-active' : '']" @click="form.type = 'expense'">
          - Ausgabe
        </button>
      </div>

      <div class="form-group">
        <label>Betrag (€)</label>
        <input v-model.number="form.amount" type="number" min="0.01" step="0.01" placeholder="0.00" />
      </div>

      <div class="form-group">
        <label>Kategorie</label>
        <select v-model="form.category">
          <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
        </select>
      </div>

      <div class="form-group">
        <label>Beschreibung</label>
        <input v-model="form.description" type="text" placeholder="Beschreibung..." />
      </div>

      <div class="form-group">
        <label>Datum</label>
        <input v-model="form.date" type="date" />
      </div>

      <div class="form-actions">
        <button class="btn-cancel" @click="$emit('close')">Abbrechen</button>
        <button class="btn-save" @click="handleSave">Speichern</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed } from 'vue'
import { useTransactionStore, INCOME_CATEGORIES, EXPENSE_CATEGORIES, type Transaction } from '../stores/transactions'

const props = defineProps<{ editing?: Transaction }>()
const emit = defineEmits(['close'])

const store = useTransactionStore()

const form = reactive({
  type: (props.editing?.type ?? 'expense') as 'income' | 'expense',
  amount: props.editing?.amount ?? 0,
  category: props.editing?.category ?? '',
  description: props.editing?.description ?? '',
  date: props.editing?.date ?? new Date().toISOString().split('T')[0],
})

const categories = computed(() =>
  form.type === 'income' ? INCOME_CATEGORIES : EXPENSE_CATEGORIES
)

function handleSave() {
  if (!form.amount || !form.category || !form.date) return
  if (props.editing) {
    store.updateTransaction({ ...props.editing, ...form })
  } else {
    store.addTransaction({ ...form })
  }
  emit('close')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.modal {
  background: #1e293b;
  border-radius: 12px;
  padding: 2rem;
  width: 100%;
  max-width: 440px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.4);
}

h2 { color: #e2e8f0; margin: 0 0 1.5rem; font-size: 1.2rem; }

.type-toggle {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.toggle-btn {
  flex: 1;
  padding: 0.6rem;
  border-radius: 8px;
  border: 2px solid #334155;
  background: transparent;
  color: #64748b;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.income-active { border-color: #10b981; color: #10b981; background: rgba(16,185,129,0.1); }
.expense-active { border-color: #ef4444; color: #ef4444; background: rgba(239,68,68,0.1); }

.form-group { margin-bottom: 1rem; }
.form-group label { display: block; color: #94a3b8; font-size: 0.8rem; margin-bottom: 0.3rem; }

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.6rem 0.8rem;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 8px;
  color: #e2e8f0;
  font-size: 0.95rem;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #60a5fa;
}

.form-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.btn-cancel, .btn-save {
  flex: 1;
  padding: 0.7rem;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-size: 0.95rem;
  transition: opacity 0.2s;
}

.btn-cancel { background: #334155; color: #94a3b8; }
.btn-save { background: #3b82f6; color: white; font-weight: 600; }
.btn-cancel:hover, .btn-save:hover { opacity: 0.85; }
</style>
