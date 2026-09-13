import type { ReactNode } from 'react'
import type { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

// The panel reads top to bottom as a story: what came in, when, and then what
// the bot wants to write down because of it. The rail is what makes the second
// part read as a consequence of the first.

export function Timeline({ children }: { children: ReactNode }) {
  return <div className="relative">{children}</div>
}

export function TimelineItem({
  icon: Icon,
  when,
  gap,
  title,
  meta,
  tone = 'muted',
  last = false,
  children,
}: {
  icon: LucideIcon
  /** the time on the left of the rail — absent for the outcome node */
  when?: { date: string; time: string } | null
  /** "48 h later", shown on the rail above this node */
  gap?: string | null
  title: ReactNode
  meta?: ReactNode
  tone?: 'muted' | 'action'
  last?: boolean
  children?: ReactNode
}) {
  return (
    <div className="relative pl-9">
      {/* the rail itself, stopping at the last dot */}
      {!last && <span className="absolute left-[11px] top-3 -bottom-1 w-px bg-border" aria-hidden />}

      <span
        className={cn(
          'absolute left-0 top-1 flex size-6 items-center justify-center rounded-full ring-4 ring-background',
          tone === 'action'
            ? 'bg-foreground text-background'
            : 'bg-secondary text-muted-foreground',
        )}
      >
        <Icon className="size-3.5" />
      </span>

      {gap && (
        <p className="pb-2 text-xs text-muted-foreground">
          <span className="rounded bg-background px-1">{gap}</span>
        </p>
      )}

      <div className="pb-5">
        <div className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
          {when && (
            <span className="text-[13px] font-medium tabular-nums">
              {when.date}, {when.time}
            </span>
          )}
          <span className={cn('text-[13px]', when ? 'text-muted-foreground' : 'font-medium')}>
            {title}
          </span>
          {meta && <span className="ml-auto flex items-center gap-2">{meta}</span>}
        </div>
        {children && <div className="mt-2">{children}</div>}
      </div>
    </div>
  )
}
