// Thin fetch wrapper. Vite proxies /api to the FastAPI dev server (vite.config.ts).
export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    // FastAPI puts the reason in `detail` — "a rejection needs a rationale" is
    // worth showing the reviewer verbatim.
    const detail = await res.text().then((t) => {
      try {
        return JSON.parse(t).detail ?? t
      } catch {
        return t
      }
    })
    throw new Error(typeof detail === 'string' ? detail : `${res.status} ${res.statusText}`)
  }
  return res.json() as Promise<T>
}
