<script setup>
import { ref, computed, nextTick } from 'vue'
import { api, getStoredAdminPassword, setStoredAdminPassword, clearStoredAdminPassword } from './services/api'
import ArtistBar from './components/ArtistBar.vue'
import TitleBoard from './components/TitleBoard.vue'
import LyricsBoard from './components/LyricsBoard.vue'
import GuessForm from './components/GuessForm.vue'
import GuessHistory from './components/GuessHistory.vue'
import SongsAdmin from './components/SongsAdmin.vue'

const view = ref('game')
const game = ref(null)
const loading = ref(false)
const error = ref('')

const unlocked = ref(!!getStoredAdminPassword())
const showLockForm = ref(false)
const lockPasswordInput = ref('')
const lockError = ref('')
const lockLoading = ref(false)
const lockInputEl = ref(null)

function toggleLock() {
  if (unlocked.value) {
    clearStoredAdminPassword()
    unlocked.value = false
    if (view.value === 'songs') view.value = 'game'
    return
  }
  lockError.value = ''
  showLockForm.value = !showLockForm.value
  if (showLockForm.value) {
    nextTick(() => lockInputEl.value?.focus())
  }
}

async function submitLockPassword() {
  if (!lockPasswordInput.value) return
  lockLoading.value = true
  lockError.value = ''
  try {
    const result = await api.verifyPassword(lockPasswordInput.value)
    if (result.ok) {
      setStoredAdminPassword(lockPasswordInput.value)
      unlocked.value = true
      showLockForm.value = false
      lockPasswordInput.value = ''
    } else {
      lockError.value = 'Mot de passe incorrect'
    }
  } catch (e) {
    lockError.value = e.message
  } finally {
    lockLoading.value = false
  }
}

async function startGame({ artistId, mode }) {
  loading.value = true
  error.value = ''
  try {
    game.value = await api.newGame(artistId, mode)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

async function submitGuess(word) {
  if (!game.value) return
  loading.value = true
  error.value = ''
  try {
    game.value = await api.guess(game.value.game_id, word)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

const latestFoundWord = computed(() => {
  if (!game.value) return null
  const guesses = game.value.guesses
  for (let i = guesses.length - 1; i >= 0; i--) {
    const g = guesses[i]
    if (g.count > 0 || g.in_title || g.in_artist) return g.norm
  }
  return null
})
</script>

<template>
  <main class="app">
    <button class="lock-btn" @click="toggleLock" :title="unlocked ? 'Se déconnecter' : 'Zone admin'">
      {{ unlocked ? '🔓' : '🔒' }}
    </button>

    <div v-if="showLockForm" class="lock-popover">
      <form @submit.prevent="submitLockPassword">
        <input
          ref="lockInputEl"
          v-model="lockPasswordInput"
          type="password"
          placeholder="Mot de passe admin"
          autocomplete="off"
        />
        <button type="submit" :disabled="lockLoading">{{ lockLoading ? '…' : 'OK' }}</button>
      </form>
      <p v-if="lockError" class="lock-error">{{ lockError }}</p>
    </div>

    <header>
      <h1>🎤 Goatantix</h1>
      <p class="subtitle">Devine le titre du son, mot par mot.</p>
      <button v-if="unlocked" class="view-toggle" @click="view = view === 'game' ? 'songs' : 'game'">
        {{ view === 'game' ? '🎵 Gérer les sons' : '🎮 Revenir au jeu' }}
      </button>
    </header>

    <template v-if="view === 'songs' && unlocked">
      <SongsAdmin />
    </template>

    <template v-else>
      <ArtistBar :unlocked="unlocked" @start-game="startGame" />

      <p v-if="error" class="error">{{ error }}</p>

      <section v-if="game" class="game">
        <p v-if="game.mode === 'daily'" class="daily-tag">📅 Musique du jour</p>
        <p class="artist-tag">
          <template v-if="game.artist_found">{{ game.artist_name }}</template>
          <template v-else>
            <span v-for="(tok, i) in game.artist_tokens" :key="i" class="artist-word">{{ tok.t }}</span>
          </template>
        </p>
        <TitleBoard
          :title-tokens="game.title_tokens"
          :found="game.found"
          :title="game.title"
          :release-year="game.release_year"
        />
        <GuessForm :disabled="game.found" :loading="loading" @guess="submitGuess" />
        <div class="columns">
          <div class="lyrics-panel">
            <LyricsBoard
              :tokens="game.tokens"
              :found="game.found"
              :full-lyrics="game.full_lyrics"
              :latest-word="latestFoundWord"
            />
          </div>
          <aside class="history-panel">
            <h3>Essais</h3>
            <GuessHistory :guesses="game.guesses" />
          </aside>
        </div>
      </section>

      <p v-else class="empty-state">Choisis un artiste (ou laisse "aléatoire") puis lance une partie 🎧</p>
    </template>
  </main>
</template>

<style scoped>
.app {
  position: relative;
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem 1.5rem 4rem;
}
.lock-btn {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  background: var(--panel);
  border: 2px solid var(--border);
  border-radius: 999px;
  width: 2.5rem;
  height: 2.5rem;
  font-size: 1.1rem;
  line-height: 1;
  cursor: pointer;
}
.lock-btn:hover {
  border-color: var(--accent2);
}
.lock-popover {
  position: absolute;
  top: 4.25rem;
  right: 1.5rem;
  z-index: 10;
  background: var(--panel);
  border: 2px solid var(--border);
  border-radius: 14px;
  padding: 0.75rem;
  box-shadow: 0 4px 0 var(--border);
}
.lock-popover form {
  display: flex;
  gap: 0.5rem;
}
.lock-popover input {
  background: var(--input-bg);
  color: var(--text);
  border: 2px solid var(--border);
  border-radius: 10px;
  padding: 0.5rem 0.7rem;
  font-size: 0.9rem;
  font-family: 'Poppins', sans-serif;
  width: 11rem;
}
.lock-popover input:focus {
  outline: none;
  border-color: var(--accent2);
}
.lock-popover button {
  background: var(--accent);
  color: var(--on-accent);
  border: none;
  border-radius: 10px;
  padding: 0.5rem 0.9rem;
  font-weight: 700;
  cursor: pointer;
}
.lock-error {
  margin: 0.5rem 0 0;
  color: var(--danger);
  font-size: 0.8rem;
  font-weight: 600;
}
header {
  text-align: center;
  margin-bottom: 2rem;
}
h1 {
  font-size: 3rem;
  margin: 0;
  letter-spacing: 0.02em;
  background: linear-gradient(135deg, var(--accent), var(--accent3));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.subtitle {
  color: var(--muted);
  margin-top: 0.25rem;
  font-weight: 500;
}
.view-toggle {
  margin-top: 1rem;
  background: var(--panel);
  color: var(--text);
  border: 2px solid var(--border);
  border-radius: 999px;
  padding: 0.45rem 1rem;
  font-size: 0.85rem;
  font-weight: 600;
  font-family: 'Poppins', sans-serif;
  cursor: pointer;
}
.view-toggle:hover {
  border-color: var(--accent2);
}
.daily-tag {
  text-align: center;
  color: var(--hot-gold);
  font-size: 0.8rem;
  font-weight: 700;
  margin: 0 0 0.35rem;
}
.artist-tag {
  text-align: center;
  color: var(--accent2);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 0.85rem;
  font-weight: 700;
}
.artist-tag .artist-word {
  margin-right: 0.4rem;
  font-family: 'Poppins', monospace;
  font-size: 1.05em;
  letter-spacing: 0.06em;
}
.columns {
  display: grid;
  grid-template-columns: 1fr 200px;
  gap: 1rem;
  align-items: start;
  margin-top: 1.5rem;
}
.lyrics-panel {
  padding: 0 0.25rem;
}
.history-panel {
  position: sticky;
  top: 1.5rem;
}
.history-panel h3 {
  margin: 0 0 0.75rem;
  color: var(--accent3);
  font-size: 1.1rem;
}
.error {
  color: var(--danger);
  text-align: center;
  font-weight: 600;
}
.empty-state {
  text-align: center;
  color: var(--muted);
  margin-top: 3rem;
  font-size: 1.1rem;
}
@media (max-width: 860px) {
  .columns {
    grid-template-columns: 1fr;
  }
  .history-panel {
    position: static;
  }
}
</style>
