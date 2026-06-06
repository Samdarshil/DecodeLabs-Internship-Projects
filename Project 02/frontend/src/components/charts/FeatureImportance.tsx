/**
 * src/components/charts/FeatureImportance.tsx
 * Horizontal bar chart of top-10 feature contributions.
 */
import { motion } from 'framer-motion'
import type { FeatureImportance } from '@/services/api'

interface Props {
  features: FeatureImportance[]
}

function formatName(raw: string): string {
  return raw.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

export function FeatureImportanceChart({ features }: Props) {
  if (!features.length) return null

  const maxAbs = Math.max(...features.map((f) => Math.abs(f.shap_value)))

  return (
    <div className="space-y-2.5">
      {features.map((f, i) => {
        const isPos   = f.impact_direction === 'positive'
        const pct     = (Math.abs(f.shap_value) / maxAbs) * 100
        const color   = isPos ? '#ef4444' : '#22c55e'
        const bgColor = isPos ? 'rgba(239,68,68,0.08)' : 'rgba(34,197,94,0.08)'

        return (
          <motion.div
            key={f.feature}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.04 }}
            className="group"
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-medium text-slate-600 dark:text-slate-300 truncate max-w-[180px]">
                {formatName(f.feature)}
              </span>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400 dark:text-slate-500 font-mono">
                  {f.value.toFixed(4)}
                </span>
                <span
                  className="text-xs font-semibold tabular-nums w-16 text-right"
                  style={{ color }}
                >
                  {isPos ? '+' : ''}{f.shap_value.toFixed(4)}
                </span>
              </div>
            </div>
            <div className="h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
              <motion.div
                className="h-full rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${pct}%` }}
                transition={{ duration: 0.6, delay: i * 0.04, ease: 'easeOut' }}
                style={{ background: color, boxShadow: `0 0 6px ${color}60` }}
              />
            </div>
          </motion.div>
        )
      })}

      <p className="text-xs text-slate-400 dark:text-slate-600 pt-1">
        🔴 Positive impact → Malignant &nbsp;|&nbsp; 🟢 Negative impact → Benign
      </p>
    </div>
  )
}
