import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { HttpResponse, http } from 'msw'
import { afterAll, afterEach, beforeAll, describe, expect, it } from 'vitest'

import { server } from '../test/server'
import { HealthPage } from './HealthPage'

beforeAll(() => server.listen({ onUnhandledFrame: 'error' }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <HealthPage />
    </QueryClientProvider>,
  )
}

describe('PromptGram health page', () => {
  it('shows the API status and version', async () => {
    server.use(
      http.get('/api/health', () =>
        HttpResponse.json({
          status: 'ok',
          version: '0123456789abcdef',
          db: 'ok',
        }),
      ),
    )

    renderPage()

    expect(await screen.findByText('PromptGram')).toBeInTheDocument()
    expect(screen.getByText('0123456789abcdef')).toBeInTheDocument()
  })

  it('shows an unavailable state when the API fails', async () => {
    server.use(
      http.get('/api/health', () =>
        HttpResponse.json({ message: 'unavailable' }, { status: 503 }),
      ),
    )

    renderPage()

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'API is unavailable',
    )
  })
})
