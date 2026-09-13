import { useEffect, useMemo, useRef, useState } from 'react'
import { useCompletion, useDraft, useQueue, useScorecard, useVerdict } from '../api/capture'
import type { QueueItem } from '../api/types'
import type { Evidence } from '../lib/evidence'
import ArtifactPane from '../components/ArtifactPane'
import BotRail from '../components/BotRail'
import CompletionCard from '../components/CompletionCard'
import DraftedRow from '../components/DraftedRow'
import QueueList, { type Filter } from '../components/QueueList'
import ReviewBar from '../components/ReviewBar'
import Scorecard from '../components/Scorecard'

// Screen 1 — plan/DASHBOARD.md §Screen 1. The primary screen, and the only one
// where a human does work the agent cannot: what has the agent drafted, and is
// it right?
//
// Three panes. The bot rail, the queue, and — the whole point — the artifact
// beside the drafted row. Keyboard first: j/k move, a accepts, e edits,
// r rejects. A queue of fifty drafts is a five-minute job or it does not
// get done.

const KEY = (i: QueueItem) => `${i.type}-${i.id}`

export default function CaptureQueue() {
  const [bot, setBot] = useState<string | null>(null)
  const [filter, setFilter] = useState<Filter>('all')
  const [selectedKey, setSelectedKey] = useState<string | null>(null)
  const [editing, setEditing] = useState(false)
  const [edits, setEdits] = useState<Record<string, string>>({})
  const [hovered, setHovered] = useState<Evidence | null>(null)
  const [rejecting, setRejecting] = useState(false)
  const [bulkBusy, setBulkBusy] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [reviewer, setReviewer] = useState(() => localStorage.getItem('reviewer') ?? '')

  const queue = useQueue(bot)
  const scorecard = useScorecard()
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

  // Leaving an item resets the edit buffer: an edit half-typed against one
  // draft must never be able to land on the next one.
  useEffect(() => {
    setEditing(false)
    setEdits({})
    setRejecting(false)
    setError(null)
    setHovered(null)
  }, [selectedKey])

  const move = (delta: number) => {
    if (!selected) return
    const i = items.findIndex((x) => KEY(x) === KEY(selected))
    const next = items[Math.min(items.length - 1, Math.max(0, i + delta))]
    if (next) setSelectedKey(KEY(next))
  }

  /** Where the queue goes after a verdict — the item that takes this one's place. */
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

  // Keyboard, but never while the reviewer is typing into something.
  const stateRef = useRef({ editing, rejecting, kind, named })
  stateRef.current = { editing, rejecting, kind, named }
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement
      if (t && ['INPUT', 'TEXTAREA', 'SELECT'].includes(t.tagName)) return
      const s = stateRef.current
      if (e.key === 'j' || e.key === 'ArrowDown') return move(1)
      if (e.key === 'k' || e.key === 'ArrowUp') return move(-1)
      if (s.editing || s.rejecting) {
        if (e.key === 'Escape') {
          setEditing(false)
          setRejecting(false)
          setEdits({})
        }
        return
      }
      if (e.key === 'a' && s.kind !== 'question' && s.named) void send('accept', {})
      if (e.key === 'e') setEditing(true)
      if (e.key === 'r') setRejecting(true)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  })

  /** The one bulk action on this screen: one field type across completions. */
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

  const episode =
    selected?.type === 'draft' ? draft.data?.artifact : completion.data?.artifact

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div className="flex items-center gap-3 border-b border-neutral-200 bg-white px-4 py-2">
        <h1 className="text-[15px] font-semibold tracking-tight">Capture queue</h1>
        <span className="text-[12px] text-neutral-500">
          what the agent drafted, and whether it is right
        </span>
        <span className="ml-auto flex items-center gap-2 text-[12px] text-neutral-600">
          <kbd className="rounded border border-neutral-300 px-1">j</kbd>
          <kbd className="rounded border border-neutral-300 px-1">k</kbd> move
          <kbd className="rounded border border-neutral-300 px-1">a</kbd> accept
          <kbd className="rounded border border-neutral-300 px-1">e</kbd> edit
          <kbd className="rounded border border-neutral-300 px-1">r</kbd> reject
        </span>
        <label className="flex items-center gap-1 text-[12px] text-neutral-600">
          Reviewer
          <input
            className="w-40 rounded border border-neutral-300 px-1.5 py-0.5 text-[12px]"
            placeholder="your name"
            value={reviewer}
            onChange={(e) => {
              setReviewer(e.target.value)
              localStorage.setItem('reviewer', e.target.value)
            }}
          />
        </label>
      </div>

      <Scorecard card={scorecard.data} />

      <div className="grid min-h-0 flex-1 grid-cols-[13rem_23rem_1fr] grid-rows-[minmax(0,1fr)]">
        <BotRail rail={queue.data?.rail ?? []} selected={bot} onSelect={setBot} />

        <QueueList
          items={items}
          selectedKey={selected ? KEY(selected) : null}
          filter={filter}
          onFilter={setFilter}
          onSelect={(i) => setSelectedKey(KEY(i))}
          onBulkAcceptField={bulkAcceptField}
          bulkBusy={bulkBusy}
          canAct={named}
        />

        <div className="grid min-h-0 grid-cols-2 grid-rows-[minmax(0,1fr)]">
          <div className="flex min-h-0 flex-col border-r border-neutral-200 bg-neutral-50">
            <ArtifactPane episode={episode} hovered={hovered} />
          </div>

          <div className="flex min-h-0 flex-col bg-white">
            <header className="flex items-baseline gap-2 border-b border-neutral-200 px-4 py-2">
              <h2 className="text-[11px] font-semibold uppercase tracking-wider text-neutral-500">
                {selected?.type === 'completion' ? 'The drafted cell' : 'The drafted row'}
              </h2>
              {selected && (
                <span className="text-[11px] text-neutral-500">
                  {selected.type === 'draft'
                    ? `${selected.item.target_register} · confidence ${selected.item.confidence ?? '—'}`
                    : `${selected.item.row} · confidence ${selected.item.confidence ?? '—'}`}
                </span>
              )}
            </header>

            <div className="flex-1 overflow-y-auto px-4 py-3">
              {!selected && <p className="text-[13px] text-neutral-500">Queue empty.</p>}

              {selected && (
                <p
                  className={[
                    'mb-3 rounded px-3 py-2 text-[12px] leading-snug',
                    kind === 'question'
                      ? 'bg-amber-50 text-amber-900'
                      : 'bg-neutral-100 text-neutral-700',
                  ].join(' ')}
                >
                  {kind === 'question' && <strong>The bot is asking, not asserting. </strong>}
                  {selected.type === 'draft'
                    ? selected.item.rationale
                    : selected.item.rationale}
                </p>
              )}

              {selected?.type === 'draft' && draft.data && (
                <DraftedRow
                  fields={draft.data.fields}
                  blanks={draft.data.blank_by_design}
                  editing={editing}
                  edits={edits}
                  onEdit={(f, v) => setEdits((e) => ({ ...e, [f]: v }))}
                  onHover={setHovered}
                />
              )}

              {selected?.type === 'completion' && completion.data && (
                <CompletionCard
                  completion={completion.data}
                  editing={editing}
                  value={edits[completion.data.field] ?? completion.data.proposed}
                  onEdit={(v) =>
                    setEdits({ [completion.data!.field]: v })
                  }
                  onHover={setHovered}
                />
              )}
            </div>

            {selected && (
              <ReviewBar
                kind={kind}
                rowKey={selected.type === 'completion' ? selected.item.row : null}
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
    </div>
  )
}
