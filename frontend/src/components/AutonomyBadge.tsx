// Every agent action shows its autonomy level (1-5). Cross-cutting, per DASHBOARD.md.
export default function AutonomyBadge({ level }: { level: 1 | 2 | 3 | 4 | 5 }) {
  return <span className="rounded bg-neutral-200 px-1.5 py-0.5 text-xs">L{level}</span>
}
