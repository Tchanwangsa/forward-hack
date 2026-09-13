import type { RailEntry } from '../api/types'

// Grouped by bot: the reviewer for a drafted incident row is not the reviewer
// for a drafted comms row, and the edit rate that matters is per bot.
//
// The four bots that are not built yet are listed and shown as not running.
// Hiding them would suggest the queue is the whole of tier 1.
const PLANNED = [
  { bot: 'inbox-triage', label: 'Inbox triage' },
  { bot: 'meeting-scribe', label: 'Meeting scribe' },
  { bot: 'rma-capture', label: 'RMA capture' },
  { bot: 'field-check', label: 'Field-check nudge' },
]

const LABELS: Record<string, string> = {
  'outage-watch': 'Outage watch',
  ...Object.fromEntries(PLANNED.map((p) => [p.bot, p.label])),
}

export default function BotRail({
  rail,
  selected,
  onSelect,
}: {
  rail: RailEntry[]
  selected: string | null
  onSelect: (bot: string | null) => void
}) {
  const live = new Set(rail.map((r) => r.bot))
  return (
    <nav className="flex min-h-0 flex-col border-r border-neutral-200 bg-white">
      <header className="border-b border-neutral-200 px-4 py-2">
        <h2 className="text-[11px] font-semibold uppercase tracking-wider text-neutral-500">
          Bots
        </h2>
      </header>
      <div className="flex-1 overflow-y-auto p-2">
        <button
          onClick={() => onSelect(null)}
          className={[
            'mb-1 w-full rounded px-2 py-1.5 text-left text-[13px]',
            selected === null ? 'bg-neutral-900 text-white' : 'hover:bg-neutral-100',
          ].join(' ')}
        >
          All bots
        </button>
        {rail.map((r) => (
          <button
            key={r.bot}
            onClick={() => onSelect(r.bot)}
            className={[
              'mb-1 w-full rounded px-2 py-1.5 text-left',
              selected === r.bot ? 'bg-neutral-900 text-white' : 'hover:bg-neutral-100',
            ].join(' ')}
          >
            <span className="block text-[13px] font-medium">{LABELS[r.bot] ?? r.bot}</span>
            <span
              className={[
                'block text-[11px] leading-tight',
                selected === r.bot ? 'text-neutral-300' : 'text-neutral-500',
              ].join(' ')}
            >
              {r.new_rows} new · {r.questions} questions · {r.completions} completions
            </span>
          </button>
        ))}
        {PLANNED.filter((p) => !live.has(p.bot)).map((p) => (
          <div key={p.bot} className="mb-1 px-2 py-1.5 text-[13px] text-neutral-400">
            {p.label}
            <span className="block text-[11px] leading-tight">not running</span>
          </div>
        ))}
      </div>
    </nav>
  )
}
