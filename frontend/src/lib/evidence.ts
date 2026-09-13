// Evidence strings arrive as prose with a resolvable head:
//
//   "tel:TEL-2025-0840003 hub_id"
//   "tel:TEL-2025-0840003 sw_version — reported by the hub at the moment of the fault"
//   "inv:HUB-04507 — canonical serial for this hub"
//   "drafted rows open"
//
// The head says which artifact, the tokens after it say which part of it. That
// is what lets hovering a drafted field highlight the thing it came from —
// DASHBOARD.md: a field the bot cannot point at should not have been filled.

export interface Evidence {
  raw: string
  /** tel | inv | eml | tx | wo | round, or null when the evidence is a rule. */
  kind: string | null
  /** the artifact id, e.g. TEL-2025-0840003 */
  id: string | null
  /** event attributes the evidence names, e.g. ['sw_version'] */
  keys: string[]
  /** true when nothing in the artifact backs this: a convention, not a reading. */
  isRule: boolean
}

const EVENT_KEYS = [
  'event_id',
  'hub_id',
  'ward_id',
  'bed_id',
  'code',
  'severity',
  'sw_version',
  'ts_device',
  'ts_received',
  'payload',
  'source',
]

export function parseEvidence(raw: string | null | undefined): Evidence {
  const text = (raw ?? '').trim()
  const head = text.match(/^([a-z]+):([A-Za-z0-9._@:-]+)/)
  const keys = EVENT_KEYS.filter((k) => new RegExp(`\\b${k}\\b`).test(text))
  return {
    raw: text,
    kind: head?.[1] ?? null,
    id: head?.[2] ?? null,
    keys,
    isRule: !head,
  }
}

/** Does this evidence point at this event? */
export function pointsAt(ev: Evidence, eventId: string): boolean {
  return ev.kind === 'tel' && ev.id === eventId
}
