import { ChevronRight, Radio } from 'lucide-react'
import type { TelemetryEventView } from '@/api/types'
import { fieldLabel } from '@/lib/evidence'
import { formatWhen } from '@/lib/time'
import { Badge } from '@/components/ui/badge'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { TimelineItem } from '@/components/Timeline'

// One thing that came in, at the time it came in. The headline is the plain
// reading of it; the full set of values is one click down.

export default function EventNode({
  event,
  gap,
}: {
  event: TelemetryEventView
  gap?: string | null
}) {
  const when = formatWhen(event.ts_device)
  const payload = Object.entries(event.payload ?? {})

  return (
    <TimelineItem
      icon={Radio}
      when={when}
      gap={gap}
      title={headline(event)}
      meta={
        <>
          <Badge variant="secondary">{event.code}</Badge>
          {event.severity && (
            <Badge variant={event.severity.toLowerCase() === 'warn' ? 'warning' : 'outline'}>
              {event.severity.toLowerCase()}
            </Badge>
          )}
        </>
      }
    >
      <Collapsible className="rounded-lg border bg-card">
        <CollapsibleTrigger className="group flex w-full items-center gap-2 px-3 py-1.5 text-left text-xs text-muted-foreground hover:text-foreground">
          <ChevronRight className="size-3.5 shrink-0 transition-transform group-data-[state=open]:rotate-90" />
          What it said
          <span className="ml-auto truncate">{event.event_id}</span>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <dl className="space-y-1 border-t px-3 py-2.5">
            {(
              [
                ['hub_id', event.hub_id],
                ['sw_version', event.sw_version],
                ['ts_device', event.ts_device],
                ['ts_received', event.ts_received],
                ['source', event.source],
                ...payload.map(([k, v]) => [k, String(v)] as [string, string]),
              ] as [string, string | null][]
            ).map(([k, v]) => (
              <div key={k} className="flex gap-3 text-[13px]">
                <dt className="w-40 shrink-0 text-muted-foreground">{fieldLabel(k)}</dt>
                <dd className="min-w-0 break-words">{v ?? '—'}</dd>
              </div>
            ))}
          </dl>
        </CollapsibleContent>
      </Collapsible>
    </TimelineItem>
  )
}

/** The event as a sentence, using the payload where it says something useful. */
function headline(event: TelemetryEventView): string {
  const p = event.payload ?? {}
  const hours = p.offline_duration_h
  const wardWide = p.ward_wide === true

  const parts: string[] = []
  if (hours !== undefined && hours !== null) parts.push(`${hours} h without contact`)
  if (wardWide) parts.push('whole ward')
  if (parts.length === 0 && event.hub_id) parts.push(event.hub_id)

  return parts.join(' · ')
}
