import { useState } from 'react'
import type { Scorecard as Card } from '../api/types'

// A panel on the queue, not a sixth screen. Its job is to discount the accept
// rate the reviewer is generating on this very screen, and putting "accept rate
// is not accuracy" one navigation step away hides it from the only person it is
// about. Full width, always visible, expands in place.

export default function Scorecard({ card }: { card: Card | undefined }) {
  const [open, setOpen] = useState(false)
  if (!card) {
    return <div className="h-[58px] border-b border-neutral-200 bg-white" />
  }
  const { coverage, coverage_projected: proj } = card
  const accuracy = card.field_accuracy.filter((f) => f.accuracy_pct !== null)
  const scoreable = accuracy.reduce((n, f) => n + f.scoreable, 0)
  const correct = accuracy.reduce((n, f) => n + f.correct, 0)
  const overall = scoreable ? (100 * correct) / scoreable : null

  return (
    <div className="border-b border-neutral-200 bg-white">
      <div className="flex items-stretch gap-6 px-4 py-2">
        <Stat
          label="Coverage"
          value={`${coverage.pct_before}% → ${coverage.pct_after}%`}
          sub={`indicator events correctly represented in the registers · ${proj.pct_after}% if every pending item were accepted as drafted`}
        />
        <Stat
          label="Rows recovered"
          value={String(coverage.rows_recovered)}
          sub={`incident rows that did not exist · ${proj.rows_recovered} pending`}
        />
        <Stat
          label="Field accuracy"
          value={overall === null ? '—' : `${overall.toFixed(1)}%`}
          sub={`of ${scoreable} scoreable filled cells, against ground truth — not against the verdicts on this screen`}
        />
        <button
          onClick={() => setOpen((v) => !v)}
          className="self-center rounded border border-neutral-300 px-2 py-1 text-[12px] text-neutral-700"
        >
          {open ? 'Collapse' : 'Expand'} ▾
        </button>
      </div>

      {open && (
        <div className="grid grid-cols-2 gap-4 border-t border-neutral-200 bg-neutral-50 px-4 py-3 text-[12px]">
          <section>
            <H>Where the register starts</H>
            <p className="text-neutral-700">{card.baseline.sentence}</p>
            <table className="mt-2 w-full">
              <tbody>
                <Tr k="Events that happened" v={card.baseline.events_happened} />
                <Tr k="Reached the incident log" v={card.baseline.events_logged} />
                <Tr k="Never written up at all" v={card.baseline.never_written_up} />
                <Tr k="Blank event code" v={card.baseline.blank_code} />
                <Tr k="Wrong event code" v={card.baseline.wrong_code} />
              </tbody>
            </table>
          </section>

          <section>
            <H>Field accuracy, per field</H>
            <table className="w-full">
              <thead className="text-[10px] uppercase text-neutral-500">
                <tr>
                  <th className="text-left font-normal">Field</th>
                  <th className="text-right font-normal">Filled</th>
                  <th className="text-right font-normal">Scoreable</th>
                  <th className="text-right font-normal">Correct</th>
                  <th className="text-right font-normal">Contradictions</th>
                </tr>
              </thead>
              <tbody>
                {card.field_accuracy.map((f) => (
                  <tr key={f.field_name} className="border-t border-neutral-200">
                    <td className="py-0.5">{f.field_name}</td>
                    <td className="text-right">{f.proposed}</td>
                    <td className="text-right text-neutral-500">{f.scoreable}</td>
                    <td className="text-right">
                      {f.accuracy_pct === null ? '—' : `${f.accuracy_pct}%`}
                    </td>
                    <td className="text-right">{f.contradictions}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="mt-1 text-[11px] text-neutral-500">
              Cells with no ground-truth opinion are counted as unscoreable rather than as correct.
            </p>
          </section>

          <section>
            <H>Blanks the capture layer can fill</H>
            <table className="w-full">
              <tbody>
                {card.field_completeness.map((f) => (
                  <tr key={`${f.table}.${f.column}`} className="border-t border-neutral-200">
                    <td className="py-0.5 font-mono text-[11px]">
                      {f.table}.{f.column}
                    </td>
                    <td className="w-14 text-right">{f.blank_pct}%</td>
                    <td className="pl-3 text-[11px] text-neutral-500">{f.capture_knows}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          <section>
            <H>Verdicts, and what they are not</H>
            <table className="w-full">
              <tbody>
                {card.verdicts.map((v, i) => (
                  <tr key={i} className="border-t border-neutral-200">
                    <td className="py-0.5">{v.bot}</td>
                    <td className="text-neutral-500">{v.kind}</td>
                    <td>{v.status}</td>
                    <td className="text-right">{v.n}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="mt-2 space-y-1">
              {card.caveats.map((c, i) => (
                <p key={i} className="rounded bg-amber-50 px-2 py-1 text-[11px] text-amber-900">
                  {c}
                </p>
              ))}
            </div>
          </section>

          <section>
            <H>Classification, by source</H>
            <table className="w-full">
              <tbody>
                {card.classification_accuracy.by_bot.map((b) => (
                  <tr key={b.bot} className="border-t border-neutral-200">
                    <td className="py-0.5">{b.bot}</td>
                    <td className="text-right">
                      {b.correct}/{b.classified}
                    </td>
                    <td className="w-16 text-right">
                      {b.accuracy_pct === null ? '—' : `${b.accuracy_pct}%`}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="mt-1 text-[11px] text-neutral-500">
              Broken out by source on purpose: telemetry is easy and free text is not, and an
              average across bots would hide that.
            </p>
          </section>

          <section>
            <H>Latency, artifact to row</H>
            <table className="w-full">
              <tbody>
                <Tr
                  k="Human (rows that got written up)"
                  v={`median ${card.latency.human.median_days}d · p90 ${card.latency.human.p90_days}d · max ${card.latency.human.max_days}d`}
                />
                <Tr k="Agent" v={card.latency.agent.note} />
              </tbody>
            </table>
            <p className="mt-1 text-[11px] text-neutral-500">{card.latency.human.scope}</p>
          </section>
        </div>
      )}
    </div>
  )
}

function Stat({ label, value, sub }: { label: string; value: string; sub: string }) {
  return (
    <div className="min-w-0 flex-1">
      <p className="text-[10px] uppercase tracking-wider text-neutral-500">{label}</p>
      <p className="text-[17px] font-semibold leading-tight text-neutral-900">{value}</p>
      <p className="truncate text-[11px] text-neutral-500" title={sub}>
        {sub}
      </p>
    </div>
  )
}

const H = ({ children }: { children: React.ReactNode }) => (
  <h3 className="mb-1 text-[10px] font-semibold uppercase tracking-wider text-neutral-500">
    {children}
  </h3>
)

const Tr = ({ k, v }: { k: string; v: string | number }) => (
  <tr className="border-t border-neutral-200">
    <td className="py-0.5 text-neutral-600">{k}</td>
    <td className="text-right font-medium">{v}</td>
  </tr>
)
