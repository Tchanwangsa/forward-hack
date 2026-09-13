import { useState } from 'react'
import { Check, ChevronRight, CornerDownRight, FileCheck2, Flag, Stethoscope } from 'lucide-react'
import type { Probe, TriageStepView, TriageView } from '@/api/types'
import { Badge } from '@/components/ui/badge'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { TimelineItem } from '@/components/Timeline'
import { cn } from '@/lib/utils'

// What the agent did between the events arriving and the row it wants to write:
// it ran the ops team's own procedure. The steps that found nothing are shown,
// not summarised away — a reviewer judging a root cause is judging what was
// ruled out, and OPS-SOP-004 §3 C3 requires them recorded anyway.

export default function TriageNode({ triage, gap }: { triage: TriageView; gap?: string | null }) {
  return (
    <TimelineItem
      icon={Stethoscope}
      gap={gap}
      title={
        <>
          Ran <span className="font-medium text-foreground">{triage.procedure}</span> —{' '}
          {triage.steps.length} steps, {triage.checks_run} read-only checks
        </>
      }
      meta={
        <Badge variant={triage.disposition === 'no_incident' ? 'success' : 'info'}>
          {triage.label}
        </Badge>
      }
    >
      <ol className="overflow-hidden rounded-lg border bg-card">
        {triage.steps.map((step, i) => (
          <Step key={step.step_id} step={step} last={i === triage.steps.length - 1} />
        ))}
      </ol>

      {triage.narrative && (
        <p className="mt-2 rounded-lg bg-muted px-3 py-2.5 text-[13px] leading-relaxed text-muted-foreground">
          <FileCheck2 className="mr-1.5 inline size-3.5 -translate-y-px" />
          {triage.narrative}
        </p>
      )}

      <p className="mt-1.5 text-xs text-muted-foreground">
        {triage.citation}
        {triage.escalate_to && <> · escalate to {triage.escalate_to}</>}
        {triage.verification && <> · {triage.verification}</>}
      </p>
    </TimelineItem>
  )
}

function Step({ step, last }: { step: TriageStepView; last: boolean }) {
  const [open, setOpen] = useState(false)
  const state = step.outcome ? 'concluded' : step.satisfied ? 'moved' : 'cleared'
  const Icon = state === 'concluded' ? Flag : state === 'moved' ? CornerDownRight : Check

  return (
    <li className={cn('text-[13px]', !last && 'border-b')}>
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        disabled={step.probes.length === 0}
        className={cn(
          'group flex w-full items-center gap-2.5 px-3 py-2 text-left',
          step.probes.length > 0 && 'hover:bg-muted/60',
          state === 'concluded' && 'bg-amber-50/60',
        )}
      >
        <Icon
          className={cn(
            'size-3.5 shrink-0',
            state === 'concluded'
              ? 'text-amber-700'
              : state === 'moved'
                ? 'text-muted-foreground'
                : 'text-emerald-600',
          )}
        />
        <span className="w-10 shrink-0 font-medium tabular-nums text-muted-foreground">
          §{step.section}
        </span>
        <span className="min-w-0 truncate">{step.title}</span>
        <span className="ml-auto flex shrink-0 items-center gap-2 text-xs text-muted-foreground">
          {state === 'cleared' && 'nothing found'}
          {state === 'moved' && <>{step.satisfied?.replace(/_/g, ' ')} → {step.goto}</>}
          {state === 'concluded' && (
            <span className="font-medium text-amber-800">
              {step.satisfied?.replace(/_/g, ' ') ?? 'nothing satisfied'}
            </span>
          )}
          {step.probes.length > 0 && (
            <ChevronRight
              className={cn('size-3.5 transition-transform', open && 'rotate-90')}
            />
          )}
        </span>
      </button>

      {open && (
        <div className="space-y-2 border-t bg-muted/30 px-3 py-2.5">
          {step.question && <p className="text-xs text-muted-foreground">{step.question}</p>}
          {step.probes.map((probe) => (
            <ProbeCard key={probe.ref} probe={probe} />
          ))}
        </div>
      )}
    </li>
  )
}

function ProbeCard({ probe }: { probe: Probe }) {
  // A step that read a session an earlier step opened. Shown, because a check
  // that appears to have been skipped reads as a gap in the procedure.
  if (probe.reused_from) {
    return (
      <p className="px-2.5 text-xs text-muted-foreground">
        <code className="font-medium">{probe.tool}</code> — {probe.summary}
      </p>
    )
  }

  return (
    <Collapsible className="rounded-md border bg-card" defaultOpen>
      <CollapsibleTrigger className="group flex w-full items-center gap-2 px-2.5 py-1.5 text-left text-xs">
        <ChevronRight className="size-3.5 shrink-0 transition-transform group-data-[state=open]:rotate-90" />
        <code className="font-medium">{probe.tool}</code>
        <span className="truncate text-muted-foreground">{probe.summary}</span>
      </CollapsibleTrigger>
      <CollapsibleContent>
        {/* The screen the analyst would have seen. It is the provenance for the
            diagnosis in the way an event ID is the provenance for a drafted row. */}
        <pre className="overflow-x-auto border-t px-2.5 py-2 font-mono text-[11px] leading-[1.5] text-muted-foreground">
          {probe.transcript.join('\n')}
        </pre>
      </CollapsibleContent>
    </Collapsible>
  )
}
