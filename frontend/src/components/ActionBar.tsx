import { useState } from 'react'
import { AlertCircle, Check, Pencil, ThumbsDown, X } from 'lucide-react'
import type { QueueItem } from '@/api/types'
import { describe } from '@/lib/suggestion'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'

// Yes, change it, or no. Saying no needs a reason — it is kept with your name,
// and it is the only way anyone finds out where the bot keeps getting it wrong.

export default function ActionBar({
  item,
  reviewer,
  editing,
  dirty,
  busy,
  error,
  rejecting,
  setRejecting,
  onAccept,
  onStartEdit,
  onCancelEdit,
  onSaveEdit,
  onReject,
}: {
  item: QueueItem
  reviewer: string
  editing: boolean
  dirty: boolean
  busy: boolean
  error: string | null
  rejecting: boolean
  setRejecting: (v: boolean) => void
  onAccept: () => void
  onStartEdit: () => void
  onCancelEdit: () => void
  onSaveEdit: () => void
  onReject: (rationale: string) => void
}) {
  const [reason, setReason] = useState('')
  const s = describe(item)
  const named = reviewer.trim().length > 0

  return (
    <div className="border-t bg-background px-5 py-3">
      {!named && (
        <p className="mb-2 flex items-center gap-2 rounded-md bg-amber-50 px-3 py-2 text-[13px] text-amber-900">
          <AlertCircle className="size-4 shrink-0" />
          Add your name at the top first — nothing saves without one.
        </p>
      )}
      {error && (
        <p className="mb-2 flex items-center gap-2 rounded-md bg-red-50 px-3 py-2 text-[13px] text-red-800">
          <AlertCircle className="size-4 shrink-0" />
          {error}
        </p>
      )}

      {rejecting ? (
        <div className="space-y-2">
          <p className="text-[13px] text-muted-foreground">
            {s.askOnly ? 'Why is this not worth asking?' : "What's wrong with it?"} Kept with your
            name.
          </p>
          <Textarea
            autoFocus
            rows={2}
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="A sentence is enough."
          />
          <div className="flex gap-2">
            <Button
              variant="destructive"
              size="sm"
              disabled={!reason.trim() || !named || busy}
              onClick={() => onReject(reason.trim())}
            >
              <ThumbsDown /> {s.askOnly ? 'Dismiss it' : 'Send it back'}
            </Button>
            <Button variant="outline" size="sm" onClick={() => setRejecting(false)}>
              Cancel
            </Button>
          </div>
        </div>
      ) : editing ? (
        <div className="flex flex-wrap items-center gap-2">
          <Button size="sm" disabled={!dirty || !named || busy} onClick={onSaveEdit}>
            <Check /> {s.askOnly ? 'Answer and save' : 'Save my version'}
          </Button>
          <Button variant="outline" size="sm" onClick={onCancelEdit}>
            <X /> Cancel
          </Button>
          <p className="text-xs text-muted-foreground">
            What you changed is the useful part — it says how close it got.
          </p>
        </div>
      ) : (
        <div className="flex flex-wrap items-center gap-2">
          {!s.askOnly && (
            <Button size="sm" disabled={!named || busy} onClick={onAccept}>
              <Check /> {s.accept}
            </Button>
          )}
          <Button variant="outline" size="sm" onClick={onStartEdit}>
            <Pencil /> {s.askOnly ? 'Answer it' : 'Change it first'}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="text-destructive hover:text-destructive"
            onClick={() => setRejecting(true)}
          >
            <ThumbsDown /> {s.askOnly ? 'Dismiss' : 'No, this is wrong'}
          </Button>

          {item.type === 'completion' && !s.askOnly && (
            <p className="ml-auto max-w-xs text-right text-xs leading-snug text-muted-foreground">
              The customer's own spreadsheet is left exactly as they wrote it.
            </p>
          )}
        </div>
      )}
    </div>
  )
}
