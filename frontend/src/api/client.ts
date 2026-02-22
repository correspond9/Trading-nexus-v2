/**
 * src/api/client.ts
 * Axios instance for Trading Nexus API.
 *
 * VITE_API_URL is baked in at Docker build time for production:
 *   e.g.  https://api.tradingnexus.pro/api/v2
 * Falls back to /api/v2 for local dev (Nginx / Vite proxy).
 */
import axios from 'axios'

const api = axios.create({
  baseURL: (import.meta.env.VITE_API_URL as string) || '/api/v2',
  timeout: 15_000,
  headers: { 'Content-Type': 'application/json' },
})

export default api
