import { useEffect, useRef, useState } from 'react'
import type { Kind, QueueItem } from '../api/types'

// The queue. Nothing is pre-selected beyond the first item, and there is no
// select-all accept.
//
// Bulk accept exists in exactly one place: per field type across completions.
// Thirteen `SW Version at Time` completions from one telemetry window are one
// decision. Bulk accept across new rows is not, and is not offered. The
// friction is the feature.

export type Filter = 'all' | 'new_row' | 'question' | 'completion'

const FILTERS: { id: Filter; label: string }[] = [
  { id: 'all', label: 'All' },
  { id: 'new_row', label: 'New rows' },
  { id: 'question', label: 'Questions' },
  { id: 'completion', label: 'Completions' },
]

export default function QueueList({
  items,
  selectedKey,
  filter,
  onFilter,
  onSelect,
  onBulkAcceptField,
  bulkBusy,
  canAct,
}: {
  items: QueueItem[]
  selectedKey: string | null
  filter: Filter
  onFilter: (f: Filter) => void
  onSelect: (item: QueueItem) => void
  onBulkAcceptField: (field: string, ids: number[]) => void
  bulkBusy: string | null
  canAct: boolean
}) {
  return (
    <section className="flex min-h-0 min-w-0 flex-col border-r border-neutral-200 bg-white">
      <header className="flex items-center gap-1 border-b border-neutral-200 px-2 py-1.5">
        {FILTERS.map((f) => (
          <button
            key={f.id}
            onClick={() => onFilter(f.id)}
            className={[
              'rounded px-2 py-1 text-[12px]',
              filter === f.id ? 'bg-neutral-900 text-white' : 'text-neutral-600 hover:bg-neutral-100',
            ].join(' ')}
          >
            {f.label}
          </button>
        ))}
        <span className="ml-auto pr-1 text-[11px] text-neutral-500">{items.length} pending</span>
      </header>

      <ol className="flex-1 overflow-y-auto">
        {items.map((it, i) => {
          const prev = items[i - 1]
          const newGroup =
            it.type === 'completion' &&
            (!prev || prev.type !== 'completion' || prev.item.field !== it.item.field)
          return (
            <li key={`${it.type}-${it.id}`}>
              {newGroup && it.type === 'completion' && (
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
          <li className="p-4 text-[13px] text-neutral-500">Nothing pending here.</li>
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
    <div className="sticky top-0 z-10 flex items-center gap-2 border-y border-neutral-200 bg-neutral-100 px-3 py-1.5">
      <span className="text-[11px] font-semibold uppercase tracking-wider text-neutral-600">
        {field}
      </span>
      <span className="text-[11px] text-neutral-500">{ids.length} completions</span>
      {confirming ? (
        <span className="ml-auto flex items-center gap-1">
          <button
            className="rounded bg-neutral-900 px-2 py-0.5 text-[11px] text-white disabled:opacity-40"
            disabled={busy || !canAct}
            onClick={() => {
              onAccept(field, ids)
              setConfirming(false)
            }}
          >
            {busy ? 'accepting…' : `Yes — one decision, ${ids.length} cells`}
          </button>
          <button
            className="rounded border border-neutral-300 bg-white px-2 py-0.5 text-[11px]"
            onClick={() => setConfirming(false)}
          >
            No
          </button>
        </span>
      ) : (
        <button
          className="ml-auto rounded border border-neutral-300 bg-white px-2 py-0.5 text-[11px] text-neutral-700 hover:bg-neutral-50"
          onClick={() => setConfirming(true)}
        >
          Accept all {field}
        </button>
      )}
    </div>
  )
}

const KIND_STYLE: Record<Kind, string> = {
  new_row: 'bg-emerald-100 text-emerald-900',
  completion: 'bg-blue-100 text-blue-900',
  question: 'bg-amber-100 text-amber-900',
}
const KIND_LABEL: Record<Kind, string> = {
  new_row: 'new row',
  completion: 'completion',
  question: 'question',
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

  const lines =
    item.type === 'draft'
      ? [
          // A question leads with what it is asking about; a drafted row leads
          // with the code it is claiming.
          item.kind === 'question'
            ? (item.item.row['Incident Description'] ?? 'not confident enough to draft')
            : [item.item.event_code, item.item.row['SW Version at Time']]
                .filter(Boolean)
                .join(' · '),
          [item.item.row['Organisation'], item.item.row['WardID'], item.item.row['BedID']]
            .filter(Boolean)
            .join(' '),
        ]
      : [
          item.item.field,
          `${item.item.existing ?? 'blank'} → ${item.item.proposed}`,
        ]

  return (
    <button
      ref={ref}
      onClick={onSelect}
      className={[
        'block w-full border-b border-neutral-100 px-3 py-2 text-left',
        selected ? 'bg-blue-50 ring-1 ring-inset ring-blue-300' : 'hover:bg-neutral-50',
      ].join(' ')}
    >
      <span className="flex items-center gap-2">
        <span className={`rounded px-1.5 py-0.5 text-[10px] ${KIND_STYLE[item.kind]}`}>
          {KIND_LABEL[item.kind]}
        </span>
        <span className="truncate font-mono text-[12px] text-neutral-700">
          {item.type === 'draft' ? item.item.artifact_ref : item.item.row}
        </span>
        {item.type === 'draft' && item.item.events.length > 1 && (
          <span className="rounded bg-neutral-200 px-1.5 py-0.5 text-[10px] text-neutral-700">
            {item.item.events.length} events
          </span>
        )}
      </span>
      <span className="mt-0.5 block truncate text-[13px] text-neutral-900">{lines[0]}</span>
      <span className="block truncate text-[11px] text-neutral-500">{lines[1]}</span>
    </button>
  )
}
