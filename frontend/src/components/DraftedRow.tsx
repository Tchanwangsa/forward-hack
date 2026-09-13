import type { DraftField } from '../api/types'
import { parseEvidence, type Evidence } from '../lib/evidence'

// THE DRAFTED ROW. Field by field, each with what it came from — hovering a
// field highlights the thing in the artifact that evidences it.
//
// Blanks render as deliberate blanks. `Assigned To — triage is a human act` is
// the correct output and has to look correct: an empty cell that reads as an
// omission trains reviewers to fill it in themselves, which is the behaviour
// the product exists to remove.

export default function DraftedRow({
  fields,
  blanks,
  editing,
  edits,
  onEdit,
  onHover,
}: {
  fields: DraftField[]
  blanks: Record<string, string>
  editing: boolean
  edits: Record<string, string>
  onEdit: (field: string, value: string) => void
  onHover: (ev: Evidence | null) => void
}) {
  return (
    <div className="text-[13px]">
      <table className="w-full border-collapse">
        <tbody>
          {fields.map((f) => {
            const ev = parseEvidence(f.evidence)
            const changed = edits[f.field] !== undefined && edits[f.field] !== (f.proposed ?? '')
            return (
              <tr
                key={f.field}
                className="group border-b border-neutral-100 align-top hover:bg-blue-50/60"
                onMouseEnter={() => onHover(ev)}
                onMouseLeave={() => onHover(null)}
                onFocus={() => onHover(ev)}
              >
                <th className="w-44 py-1.5 pr-3 text-left font-normal text-neutral-500">
                  {f.field}
                </th>
                <td className="py-1.5 pr-3">
                  {editing ? (
                    <input
                      className={[
                        'w-full rounded border px-1.5 py-0.5 font-mono text-[12px]',
                        changed ? 'border-amber-400 bg-amber-50' : 'border-neutral-300',
                      ].join(' ')}
                      value={edits[f.field] ?? f.proposed ?? ''}
                      onChange={(e) => onEdit(f.field, e.target.value)}
                    />
                  ) : (
                    <span className="font-mono text-[12px] text-neutral-900">
                      {f.proposed ?? <em className="text-neutral-400">—</em>}
                    </span>
                  )}
                </td>
                <td className="w-[46%] py-1.5 text-[11px] leading-snug text-neutral-500">
                  <span className="opacity-70 group-hover:opacity-100">
                    {ev.raw || 'no evidence recorded'}
                  </span>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>

      {Object.keys(blanks).length > 0 && (
        <div className="mt-3 rounded border border-dashed border-neutral-300 bg-neutral-50 p-3">
          <p className="mb-1.5 text-[10px] uppercase tracking-wider text-neutral-500">
            Left blank on purpose — this source does not evidence them
          </p>
          <table className="w-full border-collapse">
            <tbody>
              {Object.entries(blanks).map(([field, why]) => (
                <tr key={field} className="align-top">
                  <th className="w-44 py-1 pr-3 text-left font-normal text-neutral-500">{field}</th>
                  <td className="py-1 pr-3 font-mono text-[12px] text-neutral-400">blank</td>
                  <td className="w-[46%] py-1 text-[11px] italic leading-snug text-neutral-500">
                    {why}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
