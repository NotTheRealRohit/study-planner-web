import { supabase } from './supabase'

const BASE = import.meta.env.VITE_INTELLIGENCE_URL ?? 'http://localhost:8000'

async function authHeaders(): Promise<Record<string, string>> {
  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function postCalibration(body: unknown): Promise<unknown> {
  const resp = await fetch(`${BASE}/v1/calibration`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...(await authHeaders()) },
    body: JSON.stringify(body),
  })
  if (!resp.ok) throw new Error(`calibration ${resp.status}`)
  return resp.json()
}
