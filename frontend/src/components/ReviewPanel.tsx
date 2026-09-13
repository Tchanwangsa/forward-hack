import { ChevronRight, Inbox, Radio } from 'lucide-react'
import type { CompletionDetail, DraftDetail, QueueItem, TelemetryEventView } from '@/api/types'
import { confidenceLabel, describe } from '@/lib/suggestion'
import { byTime, gapBetween } from '@/lib/time'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { Citation } from '@/components/Citation'
import EventNode from '@/components/EventNode'
import RowCard, { toLines } from '@/components/RowCard'
import TriageNode from '@/components/TriageNode'
import { Timeline, TimelineItem } from '@/components/Timeline'
import { cn } from '@/lib/utils'

// One panel, read top to bottom as a timeline: what came in and when, then what
// the bot wants to write down because of it.

export default function ReviewPanel({
  item,
  draft,
  completion,
  editing,
  edits,
  onEdit,
}: {
  item: QueueItem | null
  draft: DraftDetail | undefined
  completion: CompletionDetail | undefined
  editing: boolean
  edits: Record<string, string>
  onEdit: (field: string, value: string) => void
}) {
  if (!item) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-2 text-muted-foreground">
        <Inbox className="size-8" />
        <p className="text-sm">Nothing left to review.</p>
      </div>
    )
  }

  const s = describe(item)
  const conf = confidenceLabel(item.item.confidence)
  const rationale = item.item.rationale
  const detail = item.type === 'draft' ? draft : completion
  const events = byTime(detail?.artifact?.events ?? [], (e) => e.ts_device)

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="mx-auto max-w-2xl px-5 py-5">
        <div className="mb-4 flex items-start gap-3">
          <span
            className={cn(
              'mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg',
              s.askOnly ? 'bg-amber-100 text-amber-700' : 'bg-secondary text-secondary-foreground',
            )}
          >
            <s.icon className="size-4" />
          </span>
          <div className="min-w-0 flex-1">
            <h2 className="text-base font-semibold leading-tight">{s.title}</h2>
            {s.where && <p className="mt-0.5 text-[13px] text-muted-foreground">{s.where}</p>}
          </div>
          <Badge variant={conf.variant} className="mt-1 shrink-0">
            {conf.text}
          </Badge>
        </div>

        {rationale && (
          <p
            className={cn(
              'mb-4 rounded-lg px-3 py-2.5 text-[13px] leading-relaxed',
              s.askOnly ? 'bg-amber-50 text-amber-900' : 'bg-muted text-muted-foreground',
            )}
          >
            {s.askOnly && (
              <span className="font-medium text-amber-900">It is asking, not telling. </span>
            )}
            {rationale}
          </p>
        )}

        <Timeline>
          {detail && events.length === 0 && (
            <TimelineItem icon={Radio} title="Nothing was loaded to back this up" />
          )}

          {events.map((e, i) => (
            <EventNode
              key={e.event_id}
              event={e}
              gap={i > 0 ? gapBetween(events[i - 1].ts_device, e.ts_device) : null}
            />
          ))}

          {draft?.triage && (
            <TriageNode
              triage={draft.triage}
              gap={events.length > 0 ? 'then the procedure ran' : null}
            />
          )}

          <TimelineItem icon={s.icon} title={s.outcome} tone="action" last>
            {item.type === 'draft' && draft && (
              <RowCard
                lines={toLines(draft.fields, draft.blank_by_design)}
                events={events}
                editing={editing}
                edits={edits}
                onEdit={onEdit}
              />
            )}

            {item.type === 'completion' && completion && (
              <CompletionBody
                completion={completion}
                events={events}
                editing={editing}
                value={edits[completion.field] ?? completion.proposed}
                onEdit={(v) => onEdit(completion.field, v)}
              />
            )}
          </TimelineItem>
        </Timeline>
      </div>
    </div>
  )
}

function CompletionBody({
  completion,
  events,
  editing,
  value,
  onEdit,
}: {
  completion: CompletionDetail
  events: TelemetryEventView[]
  editing: boolean
  value: string
  onEdit: (v: string) => void
}) {
  const fields = Object.entries(completion.target_row?.fields ?? {})

  return (
    <>
      <div className="rounded-lg border bg-card px-3 py-2.5">
        <div className="flex items-center gap-2 text-[13px]">
          <span className="text-muted-foreground">{completion.field}</span>
          <span
            className={cn(
              'ml-auto',
              completion.contradiction ? 'text-muted-foreground line-through' : 'text-muted-foreground',
            )}
          >
            {completion.existing ?? 'blank'}
          </span>
          <span className="text-muted-foreground">→</span>
          {editing ? (
            <Input
              className="h-8 max-w-[14rem] border-amber-400 bg-amber-50 text-[13px]"
              value={value}
              onChange={(e) => onEdit(e.target.value)}
            />
          ) : (
            <span className="font-semibold">{completion.proposed}</span>
          )}
          <Citation evidence={completion.evidence} events={events} className="shrink-0" />
        </div>
      </div>

      {fields.length > 0 && (
        <Collapsible className="mt-2 rounded-lg border bg-card">
          <CollapsibleTrigger className="group flex w-full items-center gap-2 px-3 py-1.5 text-left text-xs text-muted-foreground hover:text-foreground">
            <ChevronRight className="size-3.5 shrink-0 transition-transform group-data-[state=open]:rotate-90" />
            The rest of {completion.target_row?.row_key ?? 'the row'}
            <span className="ml-auto">unchanged by this</span>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <dl className="divide-y border-t">
              {fields.map(([col, v]) => {
                const target = col === completion.field
                return (
                  <div
                    key={col}
                    className={cn('flex items-start gap-3 px-3 py-2', target && 'bg-blue-50')}
                  >
                    <dt className="w-40 shrink-0 text-[13px] text-muted-foreground">{col}</dt>
                    <dd className="min-w-0 flex-1 break-words text-[13px]">
                      {v ?? <span className="text-muted-foreground">blank</span>}
                      {target && (
                        <Badge variant="info" className="ml-2">
                          this one
                        </Badge>
                      )}
                    </dd>
                  </div>
                )
              })}
            </dl>
          </CollapsibleContent>
        </Collapsible>
      )}
    </>
  )
}
