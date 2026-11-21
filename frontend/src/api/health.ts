export type HealthResponse = {
  status: 'ok' | 'degraded'
  version: string
  db: 'ok' | 'error'
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch('/api/health', {
    headers: { Accept: 'application/json' },
  })

  if (!response.ok) {
    throw new Error('API health request failed')
  }

  return response.json() as Promise<HealthResponse>
}
