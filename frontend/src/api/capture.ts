import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from './client'
import type {
  CompletionDetail,
  DraftDetail,
  QueueResponse,
  Scorecard,
  Verdict,
} from './types'

export function useQueue(bot: string | null) {
  return useQuery({
    queryKey: ['queue', bot],
    queryFn: () =>
      api<QueueResponse>(`/capture/drafts?limit=500${bot ? `&bot=${encodeURIComponent(bot)}` : ''}`),
  })
}

export function useDraft(id: number | null) {
  return useQuery({
    queryKey: ['draft', id],
    queryFn: () => api<DraftDetail>(`/capture/drafts/${id}`),
    enabled: id !== null,
  })
}

export function useCompletion(id: number | null) {
  return useQuery({
    queryKey: ['completion', id],
    queryFn: () => api<CompletionDetail>(`/capture/completions/${id}`),
    enabled: id !== null,
  })
}

export function useScorecard() {
  return useQuery({ queryKey: ['scorecard'], queryFn: () => api<Scorecard>('/capture/scorecard') })
}

type Target = { type: 'draft' | 'completion'; id: number }
type Action = 'accept' | 'edit' | 'reject'

/** Every verdict goes through here: nothing on this screen commits without a
 *  named reviewer, and the queue and the scorecard both move afterwards. */
export function useVerdict() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ type, id, action, verdict }: Target & { action: Action; verdict: Verdict }) =>
      api<{ status: string }>(`/capture/${type === 'draft' ? 'drafts' : 'completions'}/${id}/${action}`, {
        method: 'POST',
        body: JSON.stringify(verdict),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['queue'] })
      qc.invalidateQueries({ queryKey: ['scorecard'] })
    },
  })
}
