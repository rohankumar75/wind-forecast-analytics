import type { Analysis } from '../types'

const base = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')
export async function getAnalysis(start: string, end: string): Promise<Analysis> {
  const url = `${base}/api/forecast/series?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`
  const response = await fetch(url)
  if (!response.ok) {
    let detail = `API request failed (${response.status})`
    try {
      const body = await response.json()
      detail = body.detail || detail
    } catch { /* ignore non-JSON error */ }
    throw new Error(detail)
  }
  return response.json()
}
