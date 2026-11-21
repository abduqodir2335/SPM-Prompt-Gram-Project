# Frontend conventions

- Function components and hooks only.
- API calls live in `src/api/`; components do not call `fetch`.
- Use relative URLs and React Router imports from `react-router`.
- Use TanStack Query for server state.
- Tailwind 4 is configured through the Vite plugin and `@import "tailwindcss"`.
- Test behavior with Vitest, Testing Library, and network-level MSW handlers.
