import { HelpCircle, Pencil, Plus, type LucideIcon } from 'lucide-react'
import type { QueueItem } from '@/api/types'

// The one-line version of what the bot wants to do, in the words a person would
// use. "Add 1 row to the incident register", not a table of proposed cells.

export interface Suggestion {
  icon: LucideIcon
  /** what happens if you say yes */
  title: string
  /** which thing it happens to */
  where: string
  /** the last node on the timeline — what follows from the events above it */
  outcome: string
  /** the accept button */
  accept: string
  /** shown instead of accept when the bot is not sure enough to propose */
  askOnly: boolean
}

const register = (name: string) => name.replace(/_/g, ' ')

export function describe(item: QueueItem): Suggestion {
  if (item.type === 'draft') {
    if (item.kind === 'question') {
      return {
        icon: HelpCircle,
        title: 'Answer a question',
        where: `about the ${register(item.item.target_register)} register`,
        outcome: 'What it has so far',
        accept: '',
        askOnly: true,
      }
    }
    return {
      icon: Plus,
      title: `Add 1 row to the ${register(item.item.target_register)} register`,
      where: [item.item.row['Organisation'], item.item.row['WardID'], item.item.row['BedID']]
        .filter(Boolean)
        .join(' · '),
      outcome: 'So it wants to add this row',
      accept: 'Add the row',
      askOnly: false,
    }
  }

  const c = item.item
  if (c.kind === 'question') {
    return {
      icon: HelpCircle,
      title: `Answer a question about ${c.field}`,
      where: `on ${c.row}`,
      outcome: 'What it is asking about',
      accept: '',
      askOnly: true,
    }
  }
  return {
    icon: Pencil,
    title: c.contradiction ? `Change ${c.field}` : `Fill in ${c.field}`,
    where: `on ${c.row}`,
    outcome: c.contradiction
      ? `So it wants to change ${c.field} on ${c.row}`
      : `So it wants to fill in ${c.field} on ${c.row}`,
    accept: c.contradiction ? 'Apply the change' : 'Fill it in',
    askOnly: false,
  }
}

/** 0.99 -> "very sure". Numbers on their own do not tell a reviewer anything. */
export function confidenceLabel(c: number | null | undefined): {
  text: string
  variant: 'success' | 'warning' | 'secondary'
} {
  if (c === null || c === undefined) return { text: 'unscored', variant: 'secondary' }
  if (c >= 0.9) return { text: 'very sure', variant: 'success' }
  if (c >= 0.7) return { text: 'fairly sure', variant: 'secondary' }
  return { text: 'not very sure', variant: 'warning' }
}
