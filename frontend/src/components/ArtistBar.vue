<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../services/api'

defineProps({
  unlocked: { type: Boolean, default: false },
})
const emit = defineEmits(['start-game'])

const artists = ref([])
const selectedArtistId = ref('')
const loading = ref(false)
const dailyLoading = ref(false)
const collecting = ref(false)
const newArtistName = ref('')
const error = ref('')

async function loadArtists() {
  try {
    artists.value = await api.listArtists()
  } catch (e) {
    error.value = e.message
  }
}

async function startGame() {
  loading.value = true
  error.value = ''
  try {
    const artistId = selectedArtistId.value ? Number(selectedArtistId.value) : null
    emit('start-game', { artistId, mode: 'random' })
  } finally {
    loading.value = false
  }
}

async function startDaily() {
  dailyLoading.value = true
  error.value = ''
  try {
    emit('start-game', { artistId: null, mode: 'daily' })
  } finally {
    dailyLoading.value = false
  }
}

async function collectArtist() {
  if (!newArtistName.value.trim()) return
  collecting.value = true
  error.value = ''
  try {
    const result = await api.collectArtist(newArtistName.value.trim())
    newArtistName.value = ''
    await loadArtists()
    error.value = `${result.artist} : ${result.songs_imported} sons importés.`
  } catch (e) {
    error.value = e.message
  } finally {
    collecting.value = false
  }
}

onMounted(loadArtists)
</script>

<template>
  <div class="artist-bar">
    <div class="row">
      <select v-model="selectedArtistId">
        <option value="">Artiste aléatoire (tous)</option>
        <option v-for="a in artists" :key="a.id" :value="a.id">
          {{ a.name }} ({{ a.song_count }} sons)
        </option>
      </select>
      <button :disabled="loading" @click="startGame">Nouvelle partie</button>
      <button class="daily-btn" :disabled="dailyLoading" @click="startDaily">
        📅 Musique du jour
      </button>
    </div>

    <details v-if="unlocked" class="collect">
      <summary>Importer un nouvel artiste (Genius)</summary>
      <div class="row">
        <input v-model="newArtistName" placeholder="Nom de l'artiste" @keyup.enter="collectArtist" />
        <button :disabled="collecting" @click="collectArtist">
          {{ collecting ? 'Import en cours…' : 'Importer' }}
        </button>
      </div>
      <p class="hint">Peut prendre plusieurs minutes selon la taille du catalogue. Pense à relancer l'entraînement des embeddings ensuite (script backend).</p>
    </details>

    <p v-if="error" class="notice">{{ error }}</p>
  </div>
</template>

<style scoped>
.artist-bar {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  margin-bottom: 1.5rem;
  background: var(--panel);
  border: 3px solid var(--border);
  border-radius: 20px;
  padding: 1.1rem 1.25rem;
  box-shadow: 0 4px 0 var(--border);
}
.row {
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}
select, input, button {
  background: var(--input-bg);
  color: var(--text);
  border: 2px solid var(--border);
  border-radius: 12px;
  padding: 0.55rem 0.85rem;
  font-size: 0.95rem;
  font-family: 'Poppins', sans-serif;
}
button {
  cursor: pointer;
  background: var(--accent3);
  border: none;
  color: var(--text);
  font-weight: 700;
  box-shadow: 0 3px 0 var(--accent3-shadow);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 0 var(--accent3-shadow);
}
button:active:not(:disabled) {
  transform: translateY(1px);
  box-shadow: 0 1px 0 var(--accent3-shadow);
}
button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.daily-btn {
  background: var(--accent);
  color: var(--on-accent);
  box-shadow: 0 3px 0 var(--accent-shadow);
}
.daily-btn:hover:not(:disabled) {
  box-shadow: 0 5px 0 var(--accent-shadow);
}
.daily-btn:active:not(:disabled) {
  box-shadow: 0 1px 0 var(--accent-shadow);
}
.collect {
  font-size: 0.85rem;
  color: var(--muted);
}
.collect summary {
  cursor: pointer;
  font-weight: 600;
}
.hint {
  color: var(--muted);
  font-size: 0.8rem;
}
.notice {
  color: var(--accent2);
  font-size: 0.85rem;
  font-weight: 600;
}
</style>
