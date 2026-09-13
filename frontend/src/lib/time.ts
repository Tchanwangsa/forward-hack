// Times on this screen are read down a column, so they need to line up and be
// scannable: "12 Jan 2026, 08:58" rather than an ISO string.

const DATE = new Intl.DateTimeFormat('en-GB', {
  day: 'numeric',
  month: 'short',
  year: 'numeric',
})
const TIME = new Intl.DateTimeFormat('en-GB', { hour: '2-digit', minute: '2-digit' })

export function formatWhen(iso: string | null | undefined): { date: string; time: string } | null {
  if (!iso) return null
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return null
  return { date: DATE.format(d), time: TIME.format(d) }
}

/** "48 hours later", for the gap between two events in an episode. */
export function gapBetween(a: string | null | undefined, b: string | null | undefined): string | null {
  if (!a || !b) return null
  const ms = new Date(b).getTime() - new Date(a).getTime()
  if (Number.isNaN(ms) || ms <= 0) return null
  const mins = Math.round(ms / 60000)
  if (mins < 60) return `${mins} min later`
  const hours = Math.round(mins / 60)
  if (hours < 48) return `${hours} h later`
  return `${Math.round(hours / 24)} days later`
}

/** Oldest first — a timeline that runs backwards is not a timeline. */
export function byTime<T>(items: T[], when: (t: T) => string | null | undefined): T[] {
  return [...items].sort((x, y) => {
    const a = when(x)
    const b = when(y)
    if (!a || !b) return 0
    return new Date(a).getTime() - new Date(b).getTime()
  })
}
