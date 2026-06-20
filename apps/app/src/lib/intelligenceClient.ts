const BASE = import.meta.env.VITE_INTELLIGENCE_URL ?? 'http://localhost:8000'

export async function postCalibration(body: unknown): Promise<unknown> {
  const resp = await fetch(`${BASE}/v1/calibration`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!resp.ok) throw new Error(`calibration ${resp.status}`)
  return resp.json()
}
