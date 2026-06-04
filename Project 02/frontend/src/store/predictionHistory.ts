/**
 * src/store/predictionHistory.ts — Global prediction history with Zustand.
 *
 * Design: In-memory (session) storage. IndexedDB integration would be the
 * production upgrade path for persistent cross-session history.
 */
import { create } from 'zustand'
import { PredictionResult, PredictionInput } from '@/services/api'

export interface HistoryEntry {
  id:        string
  timestamp: string
  input:     PredictionInput
  result:    PredictionResult
}

interface HistoryStore {
  entries:   HistoryEntry[]
  addEntry:  (input: PredictionInput, result: PredictionResult) => void
  clear:     () => void
}

export const useHistoryStore = create<HistoryStore>((set) => ({
  entries: [],

  addEntry: (input, result) =>
    set((state) => ({
      entries: [
        {
          id:        crypto.randomUUID(),
          timestamp: new Date().toISOString(),
          input,
          result,
        },
        ...state.entries,
      ].slice(0, 50), // Keep latest 50
    })),

  clear: () => set({ entries: [] }),
}))
