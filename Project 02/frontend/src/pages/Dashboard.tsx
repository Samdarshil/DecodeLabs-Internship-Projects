/**
 * src/pages/Dashboard.tsx — Prediction history with export.
 */
import { motion } from 'framer-motion'
import { Trash2, Download, Clock, TrendingUp } from 'lucide-react'
import { useHistoryStore } from '@/store/predictionHistory'
import { Card, CardHeader, CardBody } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'

function Badge({ label, isMalignant }: { label: string; isMalignant: boolean }) {
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${
        isMalignant
          ? 'bg-red-500/10 text-red-400 border border-red-500/20'
          : 'bg-green-500/10 text-green-400 border border-green-500/20'
      }`}
    >
      {label}
    </span>
  )
}

function exportAsCSV(entries: ReturnType<typeof useHistoryStore.getState>['entries']) {
  if (!entries.length) return
  const headers = ['timestamp', 'prediction', 'confidence', 'prob_malignant', 'prob_benign', 'inference_ms']
  const rows = entries.map((e) => [
    e.timestamp,
    e.result.prediction,
    e.result.confidence,
    e.result.probability_malignant,
    e.result.probability_benign,
    e.result.inference_time_ms,
  ])
  const csv = [headers, ...rows].map((r) => r.join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href     = url
  a.download = `predictions_${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

export default function Dashboard() {
  const { entries, clear } = useHistoryStore()

  const malignantCount = entries.filter((e) => e.result.prediction === 'Malignant').length
  const benignCount    = entries.filter((e) => e.result.prediction === 'Benign').length
  const avgConf        = entries.length
    ? (entries.reduce((s, e) => s + e.result.confidence, 0) / entries.length * 100).toFixed(1)
    : '—'

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6 flex items-start justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Prediction History</h1>
          <p className="mt-1 text-slate-500 dark:text-slate-400">
            {entries.length} prediction{entries.length !== 1 ? 's' : ''} this session
          </p>
        </div>
        {entries.length > 0 && (
          <div className="flex gap-2">
            <Button variant="secondary" size="sm" onClick={() => exportAsCSV(entries)}>
              <Download size={14} /> Export CSV
            </Button>
            <Button variant="destructive" size="sm" onClick={clear}>
              <Trash2 size={14} /> Clear
            </Button>
          </div>
        )}
      </div>

      {/* Stats row */}
      {entries.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
          {[
            { label: 'Total',      value: entries.length,    color: 'text-brand-400' },
            { label: 'Malignant',  value: malignantCount,    color: 'text-red-400' },
            { label: 'Benign',     value: benignCount,       color: 'text-green-400' },
            { label: 'Avg Conf.',  value: `${avgConf}%`,     color: 'text-amber-400' },
          ].map((s) => (
            <Card key={s.label} className="py-4 px-5">
              <div className={`text-2xl font-bold ${s.color}`}>{s.value}</div>
              <div className="text-xs text-slate-400 mt-0.5">{s.label}</div>
            </Card>
          ))}
        </div>
      )}

      {/* History list */}
      {entries.length === 0 ? (
        <Card className="py-20 flex flex-col items-center gap-4">
          <TrendingUp size={40} className="text-slate-600 dark:text-slate-700" />
          <p className="text-slate-400">No predictions yet. Run one from the home page.</p>
        </Card>
      ) : (
        <div className="space-y-3">
          {entries.map((entry, i) => (
            <motion.div
              key={entry.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.03 }}
            >
              <Card hover>
                <CardBody className="flex flex-wrap items-center gap-4">
                  {/* Timestamp */}
                  <div className="flex items-center gap-1.5 text-xs text-slate-400 min-w-[140px]">
                    <Clock size={12} />
                    {new Date(entry.timestamp).toLocaleTimeString()}
                  </div>

                  {/* Result */}
                  <Badge label={entry.result.prediction} isMalignant={entry.result.prediction === 'Malignant'} />

                  {/* Confidence bar */}
                  <div className="flex-1 min-w-[120px]">
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-slate-400">Confidence</span>
                      <span className="font-mono font-medium text-slate-200">
                        {(entry.result.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="h-1.5 rounded-full bg-slate-200 dark:bg-slate-800 overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          entry.result.prediction === 'Malignant' ? 'bg-red-500' : 'bg-green-500'
                        }`}
                        style={{ width: `${entry.result.confidence * 100}%` }}
                      />
                    </div>
                  </div>

                  {/* Top feature */}
                  {entry.result.top_features[0] && (
                    <div className="text-xs text-slate-400 hidden sm:block">
                      Top feature:{' '}
                      <span className="text-slate-200 font-medium">
                        {entry.result.top_features[0].feature.replace(/_/g, ' ')}
                      </span>
                    </div>
                  )}

                  {/* Inference time */}
                  <div className="text-xs text-slate-500 font-mono ml-auto">
                    {entry.result.inference_time_ms.toFixed(1)} ms
                  </div>
                </CardBody>
              </Card>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}
