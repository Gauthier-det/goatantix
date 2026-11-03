const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const ADMIN_KEY = 'goatantix_admin_password'

export function getStoredAdminPassword() {
  return localStorage.getItem(ADMIN_KEY) || ''
}

export function setStoredAdminPassword(password) {
  localStorage.setItem(ADMIN_KEY, password)
}

export function clearStoredAdminPassword() {
  localStorage.removeItem(ADMIN_KEY)
}

async function request(path, options = {}, { admin = false } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  if (admin) headers['X-Admin-Password'] = getStoredAdminPassword()

  const res = await fetch(`${BASE_URL}${path}`, { headers, ...options })
  if (!res.ok) {
    if (admin && res.status === 401) clearStoredAdminPassword()
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Erreur API (${res.status})`)
  }
  return res.json()
}

export const api = {
  listArtists: () => request('/api/artists'),

  collectArtist: (name, maxSongs = 50) =>
    request(
      '/api/artists/collect',
      { method: 'POST', body: JSON.stringify({ name, max_songs: maxSongs }) },
      { admin: true }
    ),

  newGame: (artistId = null, mode = 'random') =>
    request('/api/game/new', {
      method: 'POST',
      body: JSON.stringify({ artist_id: artistId, mode }),
    }),

  getGame: (gameId) => request(`/api/game/${gameId}`),

  guess: (gameId, word) =>
    request(`/api/game/${gameId}/guess`, {
      method: 'POST',
      body: JSON.stringify({ word }),
    }),

  verifyPassword: (password) =>
    request('/api/auth/verify', {
      method: 'POST',
      body: JSON.stringify({ password }),
    }),

  listSongs: (search = '') =>
    request(
      `/api/songs${search ? `?search=${encodeURIComponent(search)}` : ''}`,
      {},
      { admin: true }
    ),

  setSongActive: (songId, active) =>
    request(
      `/api/songs/${songId}`,
      { method: 'PATCH', body: JSON.stringify({ active }) },
      { admin: true }
    ),
}
