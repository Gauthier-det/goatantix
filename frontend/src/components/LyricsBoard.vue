<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  tokens: { type: Array, required: true },
  found: { type: Boolean, default: false },
  fullLyrics: { type: String, default: null },
  latestWord: { type: String, default: null },
})

const showFull = ref(false)

watch(
  () => props.fullLyrics,
  () => {
    showFull.value = false
  }
)

function normalize(word) {
  return word
    .normalize('NFD')             // Décompose les caractères accentués (ex é -> e)
    .replace(/[̀-ͯ]/g, '')          // supprime les diacritiques isolés ("^","`","~",...)
    .toLowerCase()                // minuscule
    .replace(/[^a-z0-9']/g, '')   // supprime les caractères non-alphanumériques (sauf les apostrophes)
}

function isLatest(tok) {
  return tok.w && tok.revealed && props.latestWord && normalize(tok.t) === props.latestWord
}
</script>

<template>
  <div class="lyrics-wrap">
    <button v-if="found && fullLyrics" class="reveal-btn" @click="showFull = !showFull">
      {{ showFull ? 'Cacher les paroles' : 'Dévoiler les paroles' }}
    </button>

    <pre v-if="showFull && fullLyrics" class="lyrics-board full">{{ fullLyrics }}</pre>
    <pre v-else class="lyrics-board"><span
        v-for="(tok, i) in tokens"
        :key="i"
        :class="{ word: tok.w, revealed: tok.revealed && tok.w, latest: isLatest(tok) }"
      >{{ tok.t }}</span></pre>
  </div>
</template>

<style scoped>
.lyrics-wrap {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.reveal-btn {
  align-self: flex-start;
  background: var(--accent2);
  color: var(--on-accent);
  border: none;
  border-radius: 999px;
  padding: 0.6rem 1.25rem;
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  box-shadow: 0 3px 0 var(--accent2-shadow);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.reveal-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 0 var(--accent2-shadow);
}
.reveal-btn:active {
  transform: translateY(1px);
  box-shadow: 0 1px 0 var(--accent2-shadow);
}
.lyrics-board {
  white-space: pre-wrap;
  word-break: break-word;
  font-family: 'Poppins', monospace;
  font-size: 1.1rem;
  line-height: 1.65;
  margin: 0;
}
.lyrics-board.full {
  color: var(--text);
}
.word {
  color: var(--muted);
}
.word:not(.revealed) {
  font-size: 1.1em;
  font-weight: 700;
  letter-spacing: 0.05em;
}
.word.revealed {
  color: var(--accent2);
  font-weight: 700;
}
.word.latest {
  color: var(--accent);
  background: rgba(46, 230, 166, 0.15);
  border-radius: 6px;
  box-shadow: 0 0 0 2px rgba(46, 230, 166, 0.35);
}
</style>
