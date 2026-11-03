<script setup>
defineProps({
  titleTokens: { type: Array, required: true },
  found: { type: Boolean, default: false },
  title: { type: String, default: null },
  releaseYear: { type: Number, default: null },
})
</script>

<template>
  <div class="title-board" :class="{ found }">
    <h2 v-if="found">🎉 {{ title }}</h2>
    <h2 v-else class="masked">
      <span v-for="(tok, i) in titleTokens" :key="i" class="word">{{ tok.t }}</span>
    </h2>
    <p v-if="releaseYear" class="hint">Sorti en {{ releaseYear }}</p>
  </div>
</template>

<style scoped>
.title-board {
  text-align: center;
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.5rem;
  background: var(--panel);
  border: 3px solid var(--border);
  border-radius: 20px;
  box-shadow: 0 4px 0 var(--border);
}
.title-board.found {
  border-color: var(--hot-gold);
  box-shadow: 0 4px 0 var(--hot-gold);
}
.title-board h2 {
  font-size: 1.8rem;
  letter-spacing: 0.02em;
  margin: 0;
}
.title-board.found h2 {
  color: var(--hot-gold);
}
.masked .word {
  margin-right: 0.7rem;
  font-family: 'Poppins', monospace;
  color: var(--accent2);
  font-size: 1.05em;
  letter-spacing: 0.06em;
}
.hint {
  margin: 0.6rem 0 0;
  color: var(--muted);
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 600;
}
</style>
