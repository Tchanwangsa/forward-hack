import { BookMarked, FileText, Radio, Ruler } from 'lucide-react'
import type { TelemetryEventView } from '@/api/types'
import { fieldLabel, parseEvidence, type Evidence } from '@/lib/evidence'
import { Badge } from '@/components/ui/badge'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { cn } from '@/lib/utils'

// A citation is a small chip you click. What it came from opens over the panel
// instead of sitting beside it all day — the queue reads as a list of decisions,
// and the backing detail is one click away when you want it.

export function Citation({
  evidence,
  events,
  className,
}: {
  evidence: string | null
  events: TelemetryEventView[]
  className?: string
}) {
  const ev = parseEvidence(evidence)
  if (!ev.raw) {
    return <span className={cn('text-xs text-muted-foreground', className)}>no source</span>
  }

  const Icon = ev.isRule ? Ruler : ev.kind === 'inv' ? BookMarked : ev.kind === 'tel' ? Radio : FileText
  const event = ev.kind === 'tel' ? events.find((e) => e.event_id === ev.id) : undefined

  return (
    <Popover>
      <PopoverTrigger asChild>
        <button
          className={cn(
            'inline-flex max-w-full items-center gap-1 rounded-md border border-dashed border-border px-1.5 py-0.5 text-xs text-muted-foreground transition-colors hover:border-solid hover:bg-accent hover:text-foreground',
            className,
          )}
        >
          <Icon className="size-3 shrink-0" />
          <span className="truncate">{ev.isRule ? 'House rule' : ev.label}</span>
        </button>
      </PopoverTrigger>
      <PopoverContent align="start" className="w-96 p-0">
        <CitationBody ev={ev} event={event} />
      </PopoverContent>
    </Popover>
  )
}

function CitationBody({ ev, event }: { ev: Evidence; event: TelemetryEventView | undefined }) {
  return (
    <div className="text-sm">
      <div className="flex items-baseline justify-between gap-2 border-b px-4 py-2.5">
        <span className="font-medium">{ev.label}</span>
        {ev.id && <span className="truncate text-xs text-muted-foreground">{ev.id}</span>}
      </div>

      {ev.isRule && (
        <p className="px-4 py-3 text-[13px] leading-relaxed text-muted-foreground">
          Nothing was read for this one. It is filled in the same way every time:{' '}
          <span className="text-foreground">{ev.note || ev.raw}</span>
        </p>
      )}

      {ev.kind === 'inv' && (
        <p className="px-4 py-3 text-[13px] leading-relaxed text-muted-foreground">
          Looked up in the hub records, not in the reports below.
          {ev.note && <> {ev.note}</>}
        </p>
      )}

      {ev.kind === 'tel' && (
        <div className="px-4 py-3">
          {ev.note && <p className="mb-2 text-[13px] leading-relaxed text-muted-foreground">{ev.note}</p>}
          {!event && (
            <p className="text-[13px] text-muted-foreground">
              From device report {ev.id}, which is not in the reports loaded here.
            </p>
          )}
          {event && (
            <dl className="space-y-1.5">
              {ev.keys.length === 0 && (
                <p className="text-[13px] text-muted-foreground">
                  From this report as a whole.
                </p>
              )}
              {ev.keys.map((k) => (
                <div key={k} className="flex gap-3 text-[13px]">
                  <dt className="w-32 shrink-0 text-muted-foreground">{fieldLabel(k)}</dt>
                  <dd className="min-w-0 break-words font-medium">{readKey(event, k)}</dd>
                </div>
              ))}
            </dl>
          )}
        </div>
      )}

      {!ev.isRule && ev.kind !== 'tel' && ev.kind !== 'inv' && (
        <p className="px-4 py-3 text-[13px] leading-relaxed text-muted-foreground">
          {ev.note || ev.raw}
        </p>
      )}

      {event && (
        <div className="flex items-center gap-2 border-t bg-muted/50 px-4 py-2">
          <Badge variant="secondary">{event.code}</Badge>
          <span className="text-xs text-muted-foreground">{event.ts_device}</span>
        </div>
      )}
    </div>
  )
}

function readKey(event: TelemetryEventView, key: string): string {
  const direct = (event as unknown as Record<string, unknown>)[key]
  if (direct !== undefined && direct !== null) {
    return key === 'payload' ? summarise(event.payload) : String(direct)
  }
  const fromPayload = event.payload?.[key]
  if (fromPayload !== undefined && fromPayload !== null) return String(fromPayload)
  return '—'
}

const summarise = (payload: Record<string, unknown> | null) =>
  payload
    ? Object.entries(payload)
        .map(([k, v]) => `${fieldLabel(k)}: ${v}`)
        .join(' · ')
    : '—'
