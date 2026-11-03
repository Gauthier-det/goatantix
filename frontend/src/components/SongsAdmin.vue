<script setup>
import { ref, onMounted, watch } from 'vue'
import { api } from '../services/api'

const songs = ref([])
const search = ref('')
const loading = ref(false)
const error = ref('')

let searchTimer = null

async function loadSongs() {
  loading.value = true
  error.value = ''
  try {
    songs.value = await api.listSongs(search.value)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

watch(search, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(loadSongs, 250)
})

async function toggleActive(song) {
  const previous = song.active
  song.active = !song.active
  try {
    await api.setSongActive(song.id, song.active)
  } catch (e) {
    song.active = previous
    error.value = e.message
  }
}

onMounted(loadSongs)
</script>

<template>
  <div class="songs-admin">
    <div class="toolbar">
      <input
        v-model="search"
        type="search"
        placeholder="Rechercher un son ou un artiste…"
        autocomplete="off"
      />
      <span class="count">{{ songs.length }} son{{ songs.length > 1 ? 's' : '' }}</span>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="loading" class="hint">Chargement…</p>

    <div v-else class="list">
      <div v-for="song in songs" :key="song.id" class="row" :class="{ inactive: !song.active }">
        <div class="info">
          <span class="title">{{ song.title }}</span>
          <span class="artist">{{ song.artist_name }}</span>
        </div>
        <span class="year">{{ song.release_year || '—' }}</span>
        <label class="toggle">
          <input type="checkbox" :checked="song.active" @change="toggleActive(song)" />
          <span>Actif</span>
        </label>
      </div>
      <p v-if="!songs.length" class="hint">Aucun son ne correspond à cette recherche.</p>
    </div>
  </div>
</template>

<style scoped>
.songs-admin {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.toolbar {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: var(--panel);
  border: 3px solid var(--border);
  border-radius: 20px;
  padding: 1.1rem 1.25rem;
  box-shadow: 0 4px 0 var(--border);
}
.toolbar input {
  flex: 1;
  background: var(--input-bg);
  color: var(--text);
  border: 2px solid var(--border);
  border-radius: 12px;
  padding: 0.6rem 0.9rem;
  font-size: 0.95rem;
  font-family: 'Poppins', sans-serif;
}
.toolbar input:focus {
  outline: none;
  border-color: var(--accent2);
}
.count {
  color: var(--muted);
  font-size: 0.85rem;
  font-weight: 600;
  white-space: nowrap;
}
.list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.row {
  display: grid;
  grid-template-columns: 1fr auto auto;
  align-items: center;
  gap: 1rem;
  background: var(--panel);
  border: 2px solid var(--border);
  border-radius: 14px;
  padding: 0.7rem 1.1rem;
  box-shadow: 0 2px 0 var(--border);
}
.row.inactive {
  opacity: 0.5;
}
.info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.title {
  font-weight: 700;
}
.artist {
  color: var(--accent2);
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 600;
}
.year {
  color: var(--muted);
  font-size: 0.85rem;
}
.toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.9rem;
  user-select: none;
}
.toggle input {
  width: 1.15rem;
  height: 1.15rem;
  accent-color: var(--accent);
  cursor: pointer;
}
.error {
  color: var(--danger);
  font-weight: 600;
}
.hint {
  color: var(--muted);
}
</style>
