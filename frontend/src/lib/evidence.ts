// Where a value came from. The backend sends a short string with a resolvable
// head and some prose after it:
//
//   "tel:TEL-2025-0840003 hub_id"
//   "tel:TEL-2025-0840003 sw_version — reported by the hub at the moment of the fault"
//   "inv:HUB-04507 — canonical serial for this hub"
//   "drafted rows open"
//
// The head says which record, the words after it say which part of it.

export interface Evidence {
  raw: string
  /** tel | inv | eml | tx | wo | round, or null when nothing was read. */
  kind: string | null
  /** the record id, e.g. TEL-2025-0840003 */
  id: string | null
  /** fields the note names, e.g. ['sw_version'] */
  keys: string[]
  /** true when nothing was read: this is a house rule, not a reading. */
  isRule: boolean
  /** short label for the chip, e.g. "Device report" */
  label: string
  /** the prose after the id, with the id and field names stripped */
  note: string
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

const SOURCE_LABELS: Record<string, string> = {
  tel: 'Device report',
  inv: 'Hub records',
  eml: 'Email',
  tx: 'Transaction',
  wo: 'Work order',
  round: 'Ward round',
}

/** Human names for the raw field keys, so nothing reads like a database column. */
export const FIELD_LABELS: Record<string, string> = {
  event_id: 'Report ID',
  hub_id: 'Hub',
  ward_id: 'Ward',
  bed_id: 'Bed',
  code: 'Code',
  severity: 'Severity',
  sw_version: 'Software version',
  ts_device: 'Time on device',
  ts_received: 'Time received',
  payload: 'Details',
  source: 'Sent via',
  last_seen: 'Last seen',
  offline_duration_h: 'Hours offline',
  ward_wide: 'Whole ward affected',
}

export const fieldLabel = (key: string) =>
  FIELD_LABELS[key] ?? key.replace(/_/g, ' ').replace(/^./, (c) => c.toUpperCase())

export function parseEvidence(raw: string | null | undefined): Evidence {
  const text = (raw ?? '').trim()
  const head = text.match(/^([a-z]+):([A-Za-z0-9._@:-]+)/)
  const keys = EVENT_KEYS.filter((k) => new RegExp(`\\b${k}\\b`).test(text))
  const kind = head?.[1] ?? null

  // Everything after the head, minus the bare field names we already show as
  // chips, and minus the dash the backend uses to join them.
  let note = head ? text.slice(head[0].length) : text
  for (const k of keys) note = note.replace(new RegExp(`\\b${k}\\b`, 'g'), '')
  note = note.replace(/^[\s—–-]+/, '').trim()

  return {
    raw: text,
    kind,
    id: head?.[2] ?? null,
    keys,
    isRule: !head,
    label: kind ? (SOURCE_LABELS[kind] ?? 'Source') : 'House rule',
    note,
  }
}

/** Does this note point at this device report? */
export function pointsAt(ev: Evidence, eventId: string): boolean {
  return ev.kind === 'tel' && ev.id === eventId
}
