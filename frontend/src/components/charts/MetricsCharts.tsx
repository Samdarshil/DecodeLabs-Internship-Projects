/**
 * src/components/charts/MetricsCharts.tsx
 * Model metrics visualizations using Recharts.
 */
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell,
} from 'recharts'
import type { ModelMetrics } from '@/services/api'

interface Props {
  metrics: ModelMetrics
}

const BRAND = '#2fa3f7'

// ── Metric Radar ──────────────────────────────────────────────────────────────
export function MetricRadar({ metrics }: Props) {
  const data = [
    { subject: 'Accuracy',   value: metrics.accuracy   * 100 },
    { subject: 'F1 Score',   value: metrics.f1_weighted * 100 },
    { subject: 'ROC-AUC',    value: metrics.roc_auc     * 100 },
    { subject: 'CV Mean',    value: metrics.cv_accuracy_mean * 100 },
  ]

  return (
    <ResponsiveContainer width="100%" height={260}>
      <RadarChart data={data} margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
        <PolarGrid stroke="#334155" />
        <PolarAngleAxis
          dataKey="subject"
          tick={{ fontSize: 12, fill: '#94a3b8' }}
        />
        <Radar
          name="Score"
          dataKey="value"
          stroke={BRAND}
          fill={BRAND}
          fillOpacity={0.25}
          strokeWidth={2}
        />
      </RadarChart>
    </ResponsiveContainer>
  )
}

// ── Metric Bar ────────────────────────────────────────────────────────────────
export function MetricBars({ metrics }: Props) {
  const data = [
    { name: 'Accuracy',   value: metrics.accuracy,          formatted: `${(metrics.accuracy   * 100).toFixed(1)}%` },
    { name: 'F1 Score',   value: metrics.f1_weighted,       formatted: `${(metrics.f1_weighted * 100).toFixed(1)}%` },
    { name: 'ROC-AUC',    value: metrics.roc_auc,           formatted: `${(metrics.roc_auc     * 100).toFixed(1)}%` },
    { name: 'CV Acc',     value: metrics.cv_accuracy_mean,  formatted: `${(metrics.cv_accuracy_mean * 100).toFixed(1)}%` },
  ]

  const colors = ['#2fa3f7', '#818cf8', '#34d399', '#f59e0b']

  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
        <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
        <YAxis
          domain={[0.88, 1.0]}
          tickFormatter={(v: number) => `${(v * 100).toFixed(0)}%`}
          tick={{ fontSize: 11, fill: '#94a3b8' }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          formatter={(v: number) => [`${(v * 100).toFixed(2)}%`, 'Score']}
          contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: 8 }}
          labelStyle={{ color: '#94a3b8' }}
          itemStyle={{ color: '#e2e8f0' }}
          cursor={{ fill: 'rgba(255,255,255,0.03)' }}
        />
        <Bar dataKey="value" radius={[6, 6, 0, 0]} maxBarSize={52}>
          {data.map((_, i) => (
            <Cell key={i} fill={colors[i]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

// ── Static confusion matrix (from hardcoded test results) ─────────────────────
export function ConfusionMatrix() {
  // These match our actual test results: 114 test samples
  // malignant: 38 TP, 4 FN | benign: 71 TN, 1 FP
  const matrix = [
    { actual: 'Malignant', predicted_malignant: 38, predicted_benign: 4 },
    { actual: 'Benign',    predicted_malignant: 1,  predicted_benign: 71 },
  ]

  const cells = [
    { val: 38, label: 'TP', color: 'bg-green-500/20 text-green-400 border-green-500/30' },
    { val: 4,  label: 'FN', color: 'bg-red-500/20 text-red-400 border-red-500/30' },
    { val: 1,  label: 'FP', color: 'bg-red-500/20 text-red-400 border-red-500/30' },
    { val: 71, label: 'TN', color: 'bg-green-500/20 text-green-400 border-green-500/30' },
  ]

  return (
    <div className="space-y-3">
      <div className="text-xs text-slate-400 text-center">Predicted →</div>
      <div className="grid grid-cols-3 gap-1.5 text-sm">
        {/* Header row */}
        <div />
        <div className="text-center text-xs font-medium text-slate-400 pb-1">Malignant</div>
        <div className="text-center text-xs font-medium text-slate-400 pb-1">Benign</div>

        {/* Row 1 */}
        <div className="text-xs font-medium text-slate-400 flex items-center justify-end pr-2">Malignant</div>
        <div className={`rounded-lg border p-3 text-center ${cells[0].color}`}>
          <div className="text-xl font-bold">{cells[0].val}</div>
          <div className="text-xs opacity-70">{cells[0].label}</div>
        </div>
        <div className={`rounded-lg border p-3 text-center ${cells[1].color}`}>
          <div className="text-xl font-bold">{cells[1].val}</div>
          <div className="text-xs opacity-70">{cells[1].label}</div>
        </div>

        {/* Row 2 */}
        <div className="text-xs font-medium text-slate-400 flex items-center justify-end pr-2">Benign</div>
        <div className={`rounded-lg border p-3 text-center ${cells[2].color}`}>
          <div className="text-xl font-bold">{cells[2].val}</div>
          <div className="text-xs opacity-70">{cells[2].label}</div>
        </div>
        <div className={`rounded-lg border p-3 text-center ${cells[3].color}`}>
          <div className="text-xl font-bold">{cells[3].val}</div>
          <div className="text-xs opacity-70">{cells[3].label}</div>
        </div>
      </div>
      <p className="text-xs text-slate-500 text-center">114 holdout samples (20% of 569 total)</p>
    </div>
  )
}
