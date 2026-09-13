import { useEffect, useMemo, useState } from 'react'
import { useCompletion, useDraft, useQueue, useVerdict } from '@/api/capture'
import type { QueueItem } from '@/api/types'
import ActionBar from '@/components/ActionBar'
import QueueList, { type Filter } from '@/components/QueueList'
import ReviewPanel from '@/components/ReviewPanel'
import { Input } from '@/components/ui/input'

// The screen that matters: what the bots want to write down, and whether you
// agree. A list on the left, one panel on the right, and everything behind that
// panel folded away until you open it.

const KEY = (i: QueueItem) => `${i.type}-${i.id}`

export default function CaptureQueue() {
  const [bot, setBot] = useState<string | null>(null)
  const [filter, setFilter] = useState<Filter>('all')
  const [selectedKey, setSelectedKey] = useState<string | null>(null)
  const [editing, setEditing] = useState(false)
  const [edits, setEdits] = useState<Record<string, string>>({})
  const [rejecting, setRejecting] = useState(false)
  const [bulkBusy, setBulkBusy] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [reviewer, setReviewer] = useState(() => localStorage.getItem('reviewer') ?? '')

  const queue = useQueue(bot)
  const verdict = useVerdict()

  const items = useMemo<QueueItem[]>(() => {
    const d = queue.data
    if (!d) return []
    const drafts: QueueItem[] = d.drafts.map((item) => ({
      type: 'draft',
      id: item.id,
      kind: item.kind,
      item,
    }))
    const completions: QueueItem[] = d.completions.map((item) => ({
      type: 'completion',
      id: item.id,
      kind: item.kind,
      item,
    }))
    const all = [
      ...drafts.filter((x) => x.kind === 'new_row'),
      ...drafts.filter((x) => x.kind === 'question'),
      ...completions,
    ]
    return filter === 'all' ? all : all.filter((x) => x.kind === filter)
  }, [queue.data, filter])

  const selected = items.find((i) => KEY(i) === selectedKey) ?? items[0] ?? null
  useEffect(() => {
    if (selected && KEY(selected) !== selectedKey) setSelectedKey(KEY(selected))
  }, [selected, selectedKey])

  const draft = useDraft(selected?.type === 'draft' ? selected.id : null)
  const completion = useCompletion(selected?.type === 'completion' ? selected.id : null)

  // Moving on clears the edit buffer: something half-typed against one item must
  // never be able to land on the next one.
  useEffect(() => {
    setEditing(false)
    setEdits({})
    setRejecting(false)
    setError(null)
  }, [selectedKey])

  /** Where the list goes after a verdict — whatever takes this item's place. */
  const advance = () => {
    if (!selected) return
    const i = items.findIndex((x) => KEY(x) === KEY(selected))
    const next = items[i + 1] ?? items[i - 1] ?? null
    setSelectedKey(next ? KEY(next) : null)
  }

  const send = async (action: 'accept' | 'edit' | 'reject', body: Record<string, unknown>) => {
    if (!selected) return
    setError(null)
    try {
      await verdict.mutateAsync({
        type: selected.type,
        id: selected.id,
        action,
        verdict: { reviewed_by: reviewer.trim(), ...body },
      })
      advance()
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    }
  }

  const changed = useMemo(() => {
    if (selected?.type === 'draft') {
      const base = Object.fromEntries(
        (draft.data?.fields ?? []).map((f) => [f.field, f.proposed ?? '']),
      )
      return Object.fromEntries(Object.entries(edits).filter(([k, v]) => v !== base[k]))
    }
    if (selected?.type === 'completion' && completion.data) {
      const v = edits[completion.data.field]
      return v !== undefined && v !== completion.data.proposed
        ? { [completion.data.field]: v }
        : {}
    }
    return {}
  }, [edits, draft.data, completion.data, selected])

  const kind = selected?.kind ?? 'new_row'
  const named = reviewer.trim().length > 0

  /** The one bulk action here: one field across several fill-ins. */
  const bulkAcceptField = async (field: string, ids: number[]) => {
    if (!named) return
    setBulkBusy(field)
    try {
      for (const id of ids) {
        await verdict.mutateAsync({
          type: 'completion',
          id,
          action: 'accept',
          verdict: { reviewed_by: reviewer.trim(), rationale: `bulk accept: ${field}` },
        })
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setBulkBusy(null)
    }
  }

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div className="flex items-center gap-3 border-b bg-background px-4 py-2">
        <h1 className="text-sm font-semibold tracking-tight">Waiting for you</h1>
        <p className="text-[13px] text-muted-foreground">
          What the bots want to write down, and whether you agree
        </p>
        <div className="ml-auto flex items-center gap-3">
          <Input
            className="h-8 w-44 text-[13px]"
            placeholder="Your name"
            value={reviewer}
            onChange={(e) => {
              setReviewer(e.target.value)
              localStorage.setItem('reviewer', e.target.value)
            }}
          />
        </div>
      </div>

      <div className="grid min-h-0 flex-1 grid-cols-[22rem_1fr] grid-rows-[minmax(0,1fr)]">
        <QueueList
          items={items}
          rail={queue.data?.rail ?? []}
          bot={bot}
          onBot={setBot}
          selectedKey={selected ? KEY(selected) : null}
          filter={filter}
          onFilter={setFilter}
          onSelect={(i) => setSelectedKey(KEY(i))}
          onBulkAcceptField={bulkAcceptField}
          bulkBusy={bulkBusy}
          canAct={named}
        />

        <div className="flex min-h-0 flex-col bg-muted/30">
          <ReviewPanel
            item={selected}
            draft={draft.data}
            completion={completion.data}
            editing={editing}
            edits={edits}
            onEdit={(f, v) => setEdits((e) => ({ ...e, [f]: v }))}
          />

          {selected && (
            <ActionBar
              item={selected}
              reviewer={reviewer}
              editing={editing}
              dirty={Object.keys(changed).length > 0}
              busy={verdict.isPending}
              error={error}
              rejecting={rejecting}
              setRejecting={setRejecting}
              onAccept={() => void send('accept', {})}
              onStartEdit={() => setEditing(true)}
              onCancelEdit={() => {
                setEditing(false)
                setEdits({})
              }}
              onSaveEdit={() => void send('edit', { edits: changed })}
              onReject={(rationale) => void send('reject', { rationale })}
            />
          )}
        </div>
      </div>
    </div>
  )
}
