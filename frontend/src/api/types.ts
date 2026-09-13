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

export interface DraftDetail extends DraftSummary {
  fields: DraftField[]
  /** field -> why this source cannot evidence it. Rendered, never hidden. */
  blank_by_design: Record<string, string>
  artifact: Episode
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

export interface Coverage {
  basis: string
  events_happened: number
  correct_before: number
  rows_recovered: number
  codes_corrected: number
  correct_after: number
  pct_before: number
  pct_after: number
}

export interface Scorecard {
  baseline: {
    events_happened: number
    events_logged: number
    never_written_up: number
    correctly_coded: number
    blank_code: number
    wrong_code: number
    identified_pct: number
    sentence: string
  }
  coverage: Coverage
  coverage_projected: Coverage
  field_completeness: { table: string; column: string; blank_pct: number; capture_knows: string }[]
  field_accuracy: {
    bot: string
    field_name: string
    proposed: number
    scoreable: number
    correct: number
    contradictions: number
    accuracy_pct: number | null
    unscoreable: number
  }[]
  classification_accuracy: {
    by_bot: { bot: string; classified: number; correct: number; accuracy_pct: number | null }[]
  }
  latency: {
    human: { median_days: number; p90_days: number; max_days: number; rows_scored: number; scope: string }
    agent: { median_days: number; p90_days: number; max_days: number; note: string }
  }
  verdicts: { bot: string; kind: string; status: string; n: number }[]
  caveats: string[]
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
