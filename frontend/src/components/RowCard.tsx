import type { DraftField, TelemetryEventView } from '@/api/types'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Citation } from '@/components/Citation'
import { cn } from '@/lib/utils'

// Every column of the row in one list — including the ones the bot could not
// fill. Those are outlined, not filed away somewhere else: a blank cell that
// looks like an oversight gets helpfully filled in by whoever is reviewing,
// which is the habit this whole screen exists to break.

export interface RowLine {
  field: string
  proposed: string | null
  evidence: string | null
  /** set when nothing here could fill it — the reason goes on the card */
  needs: string | null
}

/** The evidenced fields and the deliberate blanks, as one list in row order. */
export function toLines(fields: DraftField[], blanks: Record<string, string>): RowLine[] {
  return [
    ...fields.map((f) => ({
      field: f.field,
      proposed: f.proposed,
      evidence: f.evidence,
      needs: null,
    })),
    ...Object.entries(blanks).map(([field, why]) => ({
      field,
      proposed: null,
      evidence: null,
      needs: why,
    })),
  ]
}

export default function RowCard({
  lines,
  events,
  editing,
  edits,
  onEdit,
}: {
  lines: RowLine[]
  events: TelemetryEventView[]
  editing: boolean
  edits: Record<string, string>
  onEdit: (field: string, value: string) => void
}) {
  return (
    <div className="overflow-hidden rounded-lg border bg-card">
      <dl className="divide-y">
        {lines.map((l) => {
          const changed = edits[l.field] !== undefined && edits[l.field] !== (l.proposed ?? '')
          const filledIn = l.needs && (edits[l.field] ?? '').trim().length > 0

          return (
            <div
              key={l.field}
              className={cn(
                'flex items-start gap-3 px-3 py-2',
                l.needs && !filledIn && 'bg-rose-50/50',
              )}
            >
              <dt className="flex w-40 shrink-0 items-center gap-1.5 pt-1 text-[13px] text-muted-foreground">
                {l.field}
              </dt>

              <dd className="flex min-w-0 flex-1 flex-col gap-1">
                <div className="flex items-start gap-2">
                  {editing ? (
                    <Input
                      className={cn(
                        'h-8 flex-1 text-[13px]',
                        changed && 'border-amber-400 bg-amber-50',
                        l.needs && !filledIn && 'border-rose-300 bg-white',
                      )}
                      placeholder={l.needs ? 'Needs you' : undefined}
                      value={edits[l.field] ?? l.proposed ?? ''}
                      onChange={(e) => onEdit(l.field, e.target.value)}
                    />
                  ) : l.needs ? (
                    <span className="flex-1 rounded-md border border-dashed border-rose-300 bg-white px-2 py-1 text-[13px] text-rose-700">
                      Required — nobody has filled this in
                    </span>
                  ) : (
                    <span className="min-w-0 flex-1 break-words pt-1 text-[13px]">
                      {l.proposed ?? <span className="text-muted-foreground">—</span>}
                    </span>
                  )}

                  {l.needs ? (
                    <Badge
                      variant="outline"
                      className="mt-1 shrink-0 border-rose-300 text-rose-700"
                    >
                      required
                    </Badge>
                  ) : (
                    <Citation evidence={l.evidence} events={events} className="mt-1 shrink-0" />
                  )}
                </div>

                {l.needs && (
                  <p className="text-xs leading-snug text-rose-700/80">{l.needs}</p>
                )}
              </dd>
            </div>
          )
        })}
      </dl>
    </div>
  )
}
