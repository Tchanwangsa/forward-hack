import type { Episode, TelemetryEventView } from '../api/types'
import { pointsAt, type Evidence } from '../lib/evidence'

// THE ARTIFACT. Whatever the bot read, rendered beside what it wrote, and never
// behind a click — a reviewer who has to open another tab starts accepting
// without looking, and a rubber-stamped queue is worth less than no queue.
//
// Where a burst was grouped into one episode, every event in the episode is
// here. Ten HUB-OFFLINE events at one site over six days are one queue item
// showing ten events, not ten items.

export default function ArtifactPane({
  episode,
  hovered,
}: {
  episode: Episode | undefined
  hovered: Evidence | null
}) {
  const events = episode?.events ?? []
  return (
    <section className="flex min-h-0 flex-1 flex-col">
      <header className="flex items-baseline justify-between border-b border-neutral-200 px-4 py-2">
        <h2 className="text-[11px] font-semibold uppercase tracking-wider text-neutral-500">
          The artifact
        </h2>
        <span className="text-[11px] text-neutral-500">
          {events.length === 1
            ? 'one telemetry event'
            : `${events.length} telemetry events · one episode, one queue item`}
        </span>
      </header>

      {hovered?.kind === 'inv' && (
        <p className="border-b border-amber-200 bg-amber-50 px-4 py-2 text-[12px] text-amber-900">
          Resolved from the hub inventory ({hovered.id}), not from this event. The evidence for that
          field is the inventory record, not anything visible below.
        </p>
      )}
      {hovered?.isRule && hovered.raw && (
        <p className="border-b border-neutral-200 bg-neutral-50 px-4 py-2 text-[12px] text-neutral-600">
          Not read from the artifact — a drafting convention: <em>{hovered.raw}</em>
        </p>
      )}

      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        {events.map((e, i) => (
          <EventCard
            key={e.event_id}
            event={e}
            index={i}
            total={events.length}
            hovered={hovered && pointsAt(hovered, e.event_id) ? hovered : null}
            dimmed={!!hovered && hovered.kind === 'tel' && !pointsAt(hovered, e.event_id)}
          />
        ))}
        {events.length === 0 && (
          <p className="text-[13px] text-neutral-500">No artifact resolved for this item.</p>
        )}
      </div>
    </section>
  )
}

function EventCard({
  event,
  index,
  total,
  hovered,
  dimmed,
}: {
  event: TelemetryEventView
  index: number
  total: number
  hovered: Evidence | null
  dimmed: boolean
}) {
  const lit = (key: string) => !!hovered?.keys.includes(key)
  return (
    <article
      className={[
        'rounded border bg-white transition-colors',
        hovered ? 'border-blue-400 ring-1 ring-blue-200' : 'border-neutral-200',
        dimmed ? 'opacity-40' : '',
      ].join(' ')}
    >
      <header className="flex items-center gap-2 border-b border-neutral-100 px-3 py-1.5">
        {total > 1 && (
          <span className="rounded bg-neutral-100 px-1.5 py-0.5 text-[10px] text-neutral-600">
            {index + 1}/{total}
          </span>
        )}
        <code className={hl(lit('event_id'), 'text-[12px] text-neutral-700')}>{event.event_id}</code>
        <code className={hl(lit('code'), 'text-[12px] font-semibold text-neutral-900')}>
          {event.code}
        </code>
        <span className={hl(lit('severity'), 'text-[11px] uppercase text-neutral-500')}>
          {event.severity}
        </span>
        <span className="ml-auto text-[11px] text-neutral-500">{event.source}</span>
      </header>
      <dl className="grid grid-cols-[8.5rem_1fr] gap-x-3 gap-y-0.5 px-3 py-2 text-[12px]">
        <Row label="hub_id" value={event.hub_id} lit={lit('hub_id')} />
        <Row label="sw_version" value={event.sw_version} lit={lit('sw_version')} />
        <Row label="ts_device" value={event.ts_device} lit={lit('ts_device')} />
        <Row label="ts_received" value={event.ts_received} lit={lit('ts_received')} />
      </dl>
      {event.payload && Object.keys(event.payload).length > 0 && (
        <div className="border-t border-neutral-100 px-3 py-2">
          <p className={hl(lit('payload'), 'mb-1 text-[10px] uppercase tracking-wider text-neutral-500')}>
            payload
          </p>
          <dl className="grid grid-cols-[8.5rem_1fr] gap-x-3 gap-y-0.5 text-[12px]">
            {Object.entries(event.payload).map(([k, v]) => (
              <Row key={k} label={k} value={String(v)} lit={lit('payload')} />
            ))}
          </dl>
        </div>
      )}
    </article>
  )
}

function Row({ label, value, lit }: { label: string; value: string | null; lit: boolean }) {
  return (
    <>
      <dt className={hl(lit, 'font-mono text-[11px] text-neutral-500')}>{label}</dt>
      <dd className={hl(lit, 'font-mono text-[12px] text-neutral-800')}>{value ?? '—'}</dd>
    </>
  )
}

const hl = (lit: boolean, base: string) =>
  lit ? `${base} rounded bg-blue-100 px-1 -mx-1 ring-1 ring-blue-300` : base
