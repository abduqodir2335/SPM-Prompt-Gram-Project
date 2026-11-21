import { useQuery } from '@tanstack/react-query'

import { getHealth } from '../api/health'

export function HealthPage() {
  const health = useQuery({
    queryKey: ['health'],
    queryFn: getHealth,
  })

  if (health.isPending) {
    return <main>Checking API status…</main>
  }

  if (health.isError) {
    return <main role="alert">API is unavailable</main>
  }

  return (
    <main>
      <h1>PromptGram</h1>
      <dl>
        <dt>Status</dt>
        <dd>{health.data.status}</dd>
        <dt>Database</dt>
        <dd>{health.data.db}</dd>
        <dt>Version</dt>
        <dd>{health.data.version}</dd>
      </dl>
    </main>
  )
}
