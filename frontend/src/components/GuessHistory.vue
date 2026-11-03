<script setup>
import { computed } from 'vue'

const props = defineProps({
  guesses: { type: Array, required: true },
})

const recentFirst = computed(() => [...props.guesses].reverse())

function tempColor(g) {
  if (g.count > 0 || g.in_title || g.in_artist) return 'var(--hot-gold)'
  if (g.rank == null) return 'hsl(220, 10%, 50%)'
  const t = Math.max(0, Math.min(1, 1 - Math.log10(g.rank) / 4))
  const hue = 210 - t * 60
  return `hsl(${hue}, 65%, 58%)`
}

function label(g) {
  if (g.count > 0 || g.in_title || g.in_artist) return 'trouvé !'
  if (g.rank == null) return 'inconnu'
  return `#${g.rank}`
}
</script>

<template>
  <div class="guess-history">
    <transition-group name="pop" tag="div" class="list">
      <div
        v-for="g in recentFirst"
        :key="g.norm"
        class="guess-row"
        :class="{ repeat: g.already_guessed, newest: g === recentFirst[0] }"
      >
        <span class="word">{{ g.word }}</span>
        <span class="score" :style="{ color: tempColor(g) }">{{ (g.score * 100).toFixed(1) }}%</span>
        <span class="rank" :style="{ background: tempColor(g) }">{{ label(g) }}</span>
      </div>
    </transition-group>
    <p v-if="!guesses.length" class="empty">Les mots essayés apparaîtront ici 👀</p>
  </div>
</template>

<style scoped>
.guess-history {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.guess-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  align-items: center;
  gap: 0.4rem;
  background: var(--panel);
  border: 2px solid var(--border);
  border-radius: 14px;
  padding: 0.5rem 0.6rem;
  box-shadow: 0 2px 0 var(--border);
}
.guess-row.newest {
  border-color: var(--accent);
  box-shadow: 0 2px 0 var(--accent);
}
.guess-row.repeat {
  opacity: 0.55;
}
.word {
  font-size: 0.8rem;
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.score {
  font-variant-numeric: tabular-nums;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}
.rank {
  font-size: 0.6rem;
  font-weight: 800;
  color: var(--on-accent);
  padding: 0.15rem 0.4rem;
  border-radius: 999px;
  text-align: center;
  white-space: nowrap;
}
.empty {
  color: var(--muted);
  font-size: 0.9rem;
}
.pop-enter-active {
  transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.pop-enter-from {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}
</style>
