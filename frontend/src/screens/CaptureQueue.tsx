// Screen 1 — plan/DASHBOARD.md §Screen 1. The one screen to ship if you ship one.
//
// Left: the queue of pending drafts and completion suggestions, per bot.
// Right: the artifact pane — the raw email, transcript range, telemetry event or
// work order the draft came from. A draft you cannot walk back to its source is a bug.
// Below: the capture scorecard panel — coverage, field completeness, accept rate.
//
// Accept / Edit / Reject. Reject takes a rationale. Nothing commits without a human.
export default function CaptureQueue() {
  return <h1 className="text-lg font-medium">Capture queue</h1>
}
