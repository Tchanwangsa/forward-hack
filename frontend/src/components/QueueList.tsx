import { useEffect, useRef, useState } from 'react'
import { Check, HelpCircle, Layers, Pencil, Plus } from 'lucide-react'
import type { Kind, QueueItem, RailEntry } from '@/api/types'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { cn } from '@/lib/utils'

// The list of things waiting. Which bot produced them is a dropdown, not a
// column of its own — one list, one panel, and that is the whole screen.
//
// There is one bulk accept, and only for completions of the same field. Thirteen
// software-version cells from one window are one decision. Thirteen new rows are
// not, and there is no button for it.

export type Filter = 'all' | 'new_row' | 'question' | 'completion'

const FILTERS: { id: Filter; label: string }[] = [
  { id: 'all', label: 'All' },
  { id: 'new_row', label: 'New rows' },
  { id: 'question', label: 'Questions' },
  { id: 'completion', label: 'Fill-ins' },
]

const PLANNED: Record<string, string> = {
  'inbox-triage': 'Inbox triage',
  'meeting-scribe': 'Meeting scribe',
  'rma-capture': 'RMA capture',
  'field-check': 'Field-check nudge',
}

const BOT_LABELS: Record<string, string> = { 'outage-watch': 'Outage watch', ...PLANNED }

export default function QueueList({
  items,
  rail,
  bot,
  onBot,
  selectedKey,
  filter,
  onFilter,
  onSelect,
  onBulkAcceptField,
  bulkBusy,
  canAct,
}: {
  items: QueueItem[]
  rail: RailEntry[]
  bot: string | null
  onBot: (bot: string | null) => void
  selectedKey: string | null
  filter: Filter
  onFilter: (f: Filter) => void
  onSelect: (item: QueueItem) => void
  onBulkAcceptField: (field: string, ids: number[]) => void
  bulkBusy: string | null
  canAct: boolean
}) {
  const live = new Set(rail.map((r) => r.bot))
  const idle = Object.entries(PLANNED).filter(([id]) => !live.has(id))

  return (
    <section className="flex min-h-0 min-w-0 flex-col border-r bg-background">
      <div className="space-y-2 border-b px-3 py-2.5">
        <Select
          value={bot ?? 'all'}
          onValueChange={(v) => onBot(v === 'all' ? null : v)}
        >
          <SelectTrigger className="h-8 text-[13px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All bots</SelectItem>
            {rail.map((r) => (
              <SelectItem key={r.bot} value={r.bot}>
                {BOT_LABELS[r.bot] ?? r.bot} — {r.new_rows + r.questions + r.completions} waiting
              </SelectItem>
            ))}
            {idle.map(([id, label]) => (
              <SelectItem key={id} value={id} disabled>
                {label} — not running
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <div className="flex items-center gap-2">
          <Tabs value={filter} onValueChange={(v) => onFilter(v as Filter)} className="min-w-0">
            <TabsList className="h-8">
              {FILTERS.map((f) => (
                <TabsTrigger key={f.id} value={f.id} className="px-2 text-xs">
                  {f.label}
                </TabsTrigger>
              ))}
            </TabsList>
          </Tabs>
          <span className="ml-auto shrink-0 text-xs text-muted-foreground">{items.length} waiting</span>
        </div>
      </div>

      <ol className="flex-1 overflow-y-auto">
        {items.map((it, i) => {
          const prev = items[i - 1]
          const startsGroup =
            it.type === 'completion' &&
            (!prev || prev.type !== 'completion' || prev.item.field !== it.item.field)
          return (
            <li key={`${it.type}-${it.id}`}>
              {startsGroup && it.type === 'completion' && (
                <GroupHeader
                  field={it.item.field}
                  ids={items
                    .filter((x) => x.type === 'completion' && x.item.field === it.item.field)
                    .map((x) => x.id)}
                  busy={bulkBusy === it.item.field}
                  canAct={canAct}
                  onAccept={onBulkAcceptField}
                />
              )}
              <Row
                item={it}
                selected={selectedKey === `${it.type}-${it.id}`}
                onSelect={() => onSelect(it)}
              />
            </li>
          )
        })}
        {items.length === 0 && (
          <li className="px-4 py-6 text-center text-[13px] text-muted-foreground">
            Nothing waiting here.
          </li>
        )}
      </ol>
    </section>
  )
}

function GroupHeader({
  field,
  ids,
  busy,
  canAct,
  onAccept,
}: {
  field: string
  ids: number[]
  busy: boolean
  canAct: boolean
  onAccept: (field: string, ids: number[]) => void
}) {
  const [confirming, setConfirming] = useState(false)
  return (
    <div className="sticky top-0 z-10 flex items-center gap-2 border-y bg-muted/95 px-3 py-1.5 backdrop-blur">
      <Layers className="size-3.5 shrink-0 text-muted-foreground" />
      <span className="truncate text-xs font-medium">{field}</span>
      <span className="shrink-0 text-xs text-muted-foreground">{ids.length}</span>
      {confirming ? (
        <span className="ml-auto flex shrink-0 items-center gap-1">
          <Button
            size="xs"
            disabled={busy || !canAct}
            onClick={() => {
              onAccept(field, ids)
              setConfirming(false)
            }}
          >
            {busy ? 'Saving…' : `Yes, all ${ids.length}`}
          </Button>
          <Button size="xs" variant="outline" onClick={() => setConfirming(false)}>
            No
          </Button>
        </span>
      ) : (
        <Button
          size="xs"
          variant="outline"
          className="ml-auto shrink-0"
          onClick={() => setConfirming(true)}
        >
          <Check /> Accept all
        </Button>
      )}
    </div>
  )
}

const KIND: Record<Kind, { label: string; icon: typeof Plus; className: string }> = {
  new_row: { label: 'new row', icon: Plus, className: 'bg-emerald-100 text-emerald-800' },
  completion: { label: 'fill-in', icon: Pencil, className: 'bg-blue-100 text-blue-800' },
  question: { label: 'question', icon: HelpCircle, className: 'bg-amber-100 text-amber-900' },
}

function Row({
  item,
  selected,
  onSelect,
}: {
  item: QueueItem
  selected: boolean
  onSelect: () => void
}) {
  const ref = useRef<HTMLButtonElement>(null)
  useEffect(() => {
    if (selected) ref.current?.scrollIntoView({ block: 'nearest' })
  }, [selected])

  const kind = KIND[item.kind]
  const [headline, detail] =
    item.type === 'draft'
      ? [
          item.kind === 'question'
            ? (item.item.row['Incident Description'] ?? 'Not sure enough to draft this one')
            : [item.item.event_code, item.item.row['SW Version at Time']].filter(Boolean).join(' · '),
          [item.item.row['Organisation'], item.item.row['WardID'], item.item.row['BedID']]
            .filter(Boolean)
            .join(' · '),
        ]
      : [item.item.field, `${item.item.existing ?? 'blank'} → ${item.item.proposed}`]

  return (
    <button
      ref={ref}
      onClick={onSelect}
      className={cn(
        'block w-full border-b px-3 py-2.5 text-left transition-colors',
        selected ? 'bg-accent' : 'hover:bg-accent/50',
      )}
    >
      <span className="flex items-center gap-2">
        <Badge className={cn('shrink-0 border-transparent', kind.className)}>
          <kind.icon /> {kind.label}
        </Badge>
        {item.type === 'draft' && item.item.events.length > 1 && (
          <span className="shrink-0 text-xs text-muted-foreground">
            {item.item.events.length} reports
          </span>
        )}
      </span>
      <span className="mt-1 block truncate text-[13px] font-medium">{headline}</span>
      <span className="block truncate text-xs text-muted-foreground">{detail}</span>
    </button>
  )
}
