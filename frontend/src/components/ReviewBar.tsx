import { useState } from 'react'
import type { Kind } from '../api/types'

// Accept · Edit · Reject — and for a question, Answer · Dismiss, because a
// question is the bot saying it is not confident enough to draft.
//
// A rejection needs a rationale. It is a permanent record with a named
// reviewer, never a deletion.

export default function ReviewBar({
  kind,
  rowKey,
  reviewer,
  editing,
  dirty,
  busy,
  error,
  onAccept,
  onStartEdit,
  onCancelEdit,
  onSaveEdit,
  onReject,
  rejecting,
  setRejecting,
}: {
  kind: Kind
  rowKey: string | null
  reviewer: string
  editing: boolean
  dirty: boolean
  busy: boolean
  error: string | null
  onAccept: () => void
  onStartEdit: () => void
  onCancelEdit: () => void
  onSaveEdit: () => void
  onReject: (rationale: string) => void
  rejecting: boolean
  setRejecting: (v: boolean) => void
}) {
  const [rationale, setRationale] = useState('')
  const question = kind === 'question'
  const named = reviewer.trim().length > 0

  return (
    <div className="border-t border-neutral-200 bg-white px-4 py-3">
      {!named && (
        <p className="mb-2 rounded bg-amber-50 px-2 py-1 text-[12px] text-amber-900">
          Put your name in the header first. Nothing here commits without a named reviewer.
        </p>
      )}
      {error && (
        <p className="mb-2 rounded bg-red-50 px-2 py-1 text-[12px] text-red-800">{error}</p>
      )}

      {rejecting ? (
        <div className="space-y-2">
          <label className="block text-[12px] text-neutral-600">
            {question ? 'Why is this not worth asking?' : 'Why is this wrong?'} A rejection is kept,
            with your name — it is how the bot's failure mode gets named.
          </label>
          <textarea
            autoFocus
            rows={2}
            className="w-full rounded border border-neutral-300 px-2 py-1 text-[13px]"
            value={rationale}
            onChange={(e) => setRationale(e.target.value)}
          />
          <div className="flex gap-2">
            <button
              className="rounded bg-red-600 px-3 py-1.5 text-[13px] font-medium text-white disabled:opacity-40"
              disabled={!rationale.trim() || !named || busy}
              onClick={() => onReject(rationale.trim())}
            >
              {question ? 'Dismiss' : 'Reject'}
            </button>
            <button
              className="rounded border border-neutral-300 px-3 py-1.5 text-[13px]"
              onClick={() => setRejecting(false)}
            >
              Cancel
            </button>
          </div>
        </div>
      ) : editing ? (
        <div className="flex flex-wrap items-center gap-2">
          <button
            className="rounded bg-amber-600 px-3 py-1.5 text-[13px] font-medium text-white disabled:opacity-40"
            disabled={!dirty || !named || busy}
            onClick={onSaveEdit}
          >
            {question ? 'Answer and commit' : 'Save and accept'}
          </button>
          <button
            className="rounded border border-neutral-300 px-3 py-1.5 text-[13px]"
            onClick={onCancelEdit}
          >
            Cancel
          </button>
          <p className="text-[11px] text-neutral-500">
            Which field you changed is the signal we keep — it says the bot was close and names how
            it was wrong.
          </p>
        </div>
      ) : (
        <div className="flex flex-wrap items-start gap-2">
          {!question && (
            <button
              className="rounded bg-neutral-900 px-3 py-1.5 text-[13px] font-medium text-white disabled:opacity-40"
              disabled={!named || busy}
              onClick={onAccept}
            >
              {kind === 'completion' ? 'Accept the field' : 'Accept'}
              <kbd className="ml-2 rounded bg-white/20 px-1 text-[10px]">A</kbd>
            </button>
          )}
          <button
            className="rounded border border-neutral-300 px-3 py-1.5 text-[13px]"
            onClick={onStartEdit}
          >
            {question ? 'Answer' : 'Edit'}
            <kbd className="ml-2 rounded bg-neutral-100 px-1 text-[10px]">E</kbd>
          </button>
          <button
            className="rounded border border-neutral-300 px-3 py-1.5 text-[13px] text-red-700"
            onClick={() => setRejecting(true)}
          >
            {question ? 'Dismiss' : 'Reject'}
            <kbd className="ml-2 rounded bg-neutral-100 px-1 text-[10px]">R</kbd>
          </button>

          {kind === 'completion' && (
            <p className="ml-1 max-w-md text-[11px] leading-snug text-neutral-600">
              <strong className="font-medium text-neutral-800">
                This does not touch {rowKey ?? 'the row'} in the customer's spreadsheet.
              </strong>{' '}
              The value is recorded in the capture layer with its evidence, and analysis reads the
              completed view. The workbook stands as written.
            </p>
          )}
          {question && (
            <p className="ml-1 max-w-md text-[11px] leading-snug text-neutral-600">
              The bot is asking, not asserting — there is no accept. Answer it with the value you
              can confirm, or dismiss it with a reason.
            </p>
          )}
        </div>
      )}
    </div>
  )
}
