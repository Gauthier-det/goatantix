<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  disabled: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
})
const emit = defineEmits(['guess'])

const word = ref('')
const inputEl = ref(null)

function submit() {
  const w = word.value.trim()
  if (!w || props.disabled) return
  emit('guess', w)
  word.value = ''
}

watch(
  () => props.loading,
  (loading, wasLoading) => {
    if (!loading && wasLoading && !props.disabled) {
      nextTick(() => inputEl.value?.focus())
    }
  }
)
</script>

<template>
  <form class="guess-form" @submit.prevent="submit">
    <input
      ref="inputEl"
      v-model="word"
      :disabled="disabled || loading"
      placeholder="Entrer un mot…"
      autocomplete="off"
      autofocus
    />
    <button type="submit" :disabled="disabled || loading">
      {{ loading ? '…' : 'Valider' }}
    </button>
  </form>
</template>

<style scoped>
.guess-form {
  display: flex;
  gap: 0.75rem;
  margin: 1.25rem 0;
}
input {
  flex: 1;
  background: var(--panel);
  color: var(--text);
  border: 3px solid var(--border);
  border-radius: 16px;
  padding: 0.8rem 1.1rem;
  font-size: 1.1rem;
  font-family: 'Poppins', sans-serif;
}
input:focus {
  outline: none;
  border-color: var(--accent3);
}
button {
  background: var(--accent);
  color: var(--on-accent);
  border: none;
  border-radius: 16px;
  padding: 0.8rem 1.5rem;
  font-weight: 800;
  font-size: 1.05rem;
  cursor: pointer;
  box-shadow: 0 4px 0 var(--accent-shadow);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 0 var(--accent-shadow);
}
button:active:not(:disabled) {
  transform: translateY(2px);
  box-shadow: 0 2px 0 var(--accent-shadow);
}
button:disabled, input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
