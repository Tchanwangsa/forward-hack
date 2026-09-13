// Mirrors the Pydantic responses in backend/asteria/api/routes/capture.py.
// Keep in sync by hand, or generate from /openapi.json.

export type Kind = 'new_row' | 'completion' | 'question'
export type Status = 'Pending' | 'Accepted' | 'Edited' | 'Rejected'

export interface RailEntry {
  bot: string
  new_rows: number
  questions: number
  completions: number
}

export interface DraftSummary {
  id: number
  kind: Extract<Kind, 'new_row' | 'question'>
  bot: string
  target_register: string
  artifact_ref: string
  event_code: string | null
  confidence: number | null
  rationale: string | null
  status: Status
  row: Record<string, string | null>
  events: string[]
  committed_row_id: number | null
}

export interface DraftField {
  field: string
  proposed: string | null
  evidence: string | null
  confidence: number | null
}

export interface TelemetryEventView {
  event_id: string
  hub_id: string | null
  code: string | null
  severity: string | null
  sw_version: string | null
  ts_device: string | null
  ts_received: string | null
  payload: Record<string, unknown> | null
  source: string | null
}

export interface Episode {
  kind: 'telemetry_episode'
  events: TelemetryEventView[]
}

/** One read against the estate: what was run, what it returned, what it printed. */
export interface Probe {
  tool: string
  target: string
  summary: string
  ref: string
  metrics: Record<string, unknown>
  transcript: string[]
  /** set when an earlier step already opened this session — the reading is there */
  reused_from?: string | null
}

/** One clause of the procedure, executed. Including the ones that found nothing —
 *  what was ruled out is half of a diagnosis. */
export interface TriageStepView {
  step_id: string
  section: string | null
  title: string
  question: string | null
  /** the condition that fired, if one did */
  satisfied: string | null
  outcome: string | null
  goto: string | null
  note: string | null
  probes: Probe[]
}

export interface TriageView {
  procedure: string
  verification: string | null
  outcome: string
  label: string
  disposition: string
  citation: string | null
  narrative: string | null
  escalate_to: string | null
  checks_run: number
  confidence: number | null
  steps: TriageStepView[]
}

export interface DraftDetail extends DraftSummary {
  fields: DraftField[]
  /** field -> why this source cannot evidence it. Rendered, never hidden. */
  blank_by_design: Record<string, string>
  artifact: Episode
  /** the procedure walk behind a diagnosis, where the bot ran one */
  triage: TriageView | null
}

export interface CompletionSummary {
  id: number
  kind: 'completion' | 'question'
  bot: string
  target_register: string
  /** the human row this is a completion *for*. Never edited. */
  row: string
  field: string
  existing: string | null
  proposed: string
  contradiction: boolean
  artifact_ref: string | null
  evidence: string | null
  confidence: number | null
  rationale: string | null
  status: Status
  writes_to_source_row: false
}

export interface CompletionDetail extends CompletionSummary {
  artifact: Episode
  target_row: { row_key: string; register: string; fields: Record<string, string | null> } | null
}

export interface QueueResponse {
  rail: RailEntry[]
  drafts: DraftSummary[]
  completions: CompletionSummary[]
  counts: { drafts: number; completions: number }
}

export interface Verdict {
  reviewed_by: string
  rationale?: string | null
  edits?: Record<string, string> | null
}

/** What the middle pane holds. A draft and a completion are reviewed differently. */
export type QueueItem =
  | { type: 'draft'; id: number; kind: Kind; item: DraftSummary }
  | { type: 'completion'; id: number; kind: Kind; item: CompletionSummary }
