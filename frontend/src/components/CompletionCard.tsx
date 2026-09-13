import type { CompletionDetail } from '../api/types'
import { parseEvidence, type Evidence } from '../lib/evidence'

// A completion is a decision about ONE cell on a row a human already wrote.
// The row is shown as written, with the cell in question in place, because a
// value floating on its own is not reviewable.
//
// The customer's row is never edited. That sentence is also printed next to the
// accept button (ReviewBar), not only here.

export default function CompletionCard({
  completion,
  editing,
  value,
  onEdit,
  onHover,
}: {
  completion: CompletionDetail
  editing: boolean
  value: string
  onEdit: (v: string) => void
  onHover: (ev: Evidence | null) => void
}) {
  const ev = parseEvidence(completion.evidence)
  const fields = completion.target_row?.fields ?? {}
  return (
    <div className="text-[13px]">
      <div
        className="rounded border border-blue-200 bg-blue-50/60 p-3"
        onMouseEnter={() => onHover(ev)}
        onMouseLeave={() => onHover(null)}
      >
        <p className="text-[11px] uppercase tracking-wider text-blue-900/70">
          {completion.contradiction ? 'Contradiction' : 'Blank cell'} · {completion.row} ·{' '}
          {completion.field}
        </p>
        <p className="mt-1.5 flex items-center gap-2 font-mono text-[13px]">
          <span className={completion.contradiction ? 'text-neutral-700 line-through' : 'text-neutral-400'}>
            {completion.existing ?? 'blank'}
          </span>
          <span className="text-neutral-400">→</span>
          {editing ? (
            <input
              className="rounded border border-amber-400 bg-amber-50 px-1.5 py-0.5 font-mono text-[13px]"
              value={value}
              onChange={(e) => onEdit(e.target.value)}
            />
          ) : (
            <span className="font-semibold text-neutral-900">{completion.proposed}</span>
          )}
        </p>
        <p className="mt-2 text-[11px] leading-snug text-neutral-600">{ev.raw}</p>
      </div>

      {completion.target_row && (
        <div className="mt-3">
          <p className="mb-1 text-[10px] uppercase tracking-wider text-neutral-500">
            {completion.target_row.row_key} as the customer wrote it — unchanged by this decision
          </p>
          <table className="w-full border-collapse">
            <tbody>
              {Object.entries(fields).map(([col, v]) => {
                const target = col === completion.field
                return (
                  <tr
                    key={col}
                    className={[
                      'border-b border-neutral-100 align-top',
                      target ? 'bg-blue-50' : '',
                    ].join(' ')}
                  >
                    <th className="w-44 py-1 pr-3 text-left font-normal text-neutral-500">{col}</th>
                    <td className="py-1 font-mono text-[12px] text-neutral-800">
                      {v ?? <em className="not-italic text-neutral-400">blank</em>}
                      {target && (
                        <span className="ml-2 rounded bg-blue-600 px-1.5 py-0.5 text-[10px] font-sans text-white">
                          this cell
                        </span>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
