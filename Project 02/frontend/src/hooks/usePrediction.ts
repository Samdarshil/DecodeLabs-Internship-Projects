/**
 * src/hooks/usePrediction.ts — React Query mutation for predictions.
 */
import { useMutation } from '@tanstack/react-query'
import { runPrediction, PredictionInput, getErrorMessage } from '@/services/api'
import { useHistoryStore } from '@/store/predictionHistory'

export function usePrediction() {
  const addEntry = useHistoryStore((s) => s.addEntry)

  const mutation = useMutation({
    mutationFn: (input: PredictionInput) => runPrediction(input),
    onSuccess: (result, input) => {
      addEntry(input, result)
    },
  })

  return {
    predict:       mutation.mutate,
    predictAsync:  mutation.mutateAsync,
    isLoading:     mutation.isPending,
    result:        mutation.data ?? null,
    error:         mutation.error ? getErrorMessage(mutation.error) : null,
    reset:         mutation.reset,
  }
}
