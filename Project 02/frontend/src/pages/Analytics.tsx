/**
 * src/pages/Analytics.tsx — Model metrics, performance report, confusion matrix.
 */
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { RefreshCw, ShieldCheck, Zap, Award } from 'lucide-react'
import { fetchMetrics } from '@/services/api'
import { Card, CardHeader, CardBody } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { MetricBars, MetricRadar, ConfusionMatrix } from '@/components/charts/MetricsCharts'

function MetricCard({ label, value, sub, color }: {
  label: string; value: string; sub?: string; color: string
}) {
  return (
    <Card hover className="p-5">
      <div className={`text-3xl font-bold font-mono ${color}`}>{value}</div>
      <div className="text-sm font-medium text-slate-600 dark:text-slate-300 mt-1">{label}</div>
      {sub && <div className="text-xs text-slate-400 mt-0.5">{sub}</div>}
    </Card>
  )
}

function SkeletonCard() {
  return (
    <div className="rounded-2xl border border-slate-200 dark:border-slate-800 p-5 animate-pulse">
      <div className="h-8 w-24 bg-slate-200 dark:bg-slate-700 rounded mb-2" />
      <div className="h-4 w-32 bg-slate-100 dark:bg-slate-800 rounded" />
    </div>
  )
}

export default function Analytics() {
  const { data: metrics, isLoading, error, refetch, isFetching } = useQuery({
    queryKey: ['metrics'],
    queryFn:  fetchMetrics,
    retry: 2,
    staleTime: 60_000,
  })

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6 flex items-start justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Model Analytics</h1>
          <p className="mt-1 text-slate-500 dark:text-slate-400">
            VotingClassifier (LR + RF + GB) · Wisconsin Breast Cancer Dataset
          </p>
        </div>
        <Button
          variant="secondary"
          size="sm"
          onClick={() => refetch()}
          loading={isFetching}
          aria-label="Refresh metrics"
        >
          <RefreshCw size={14} /> Refresh
        </Button>
      </div>

      {/* Error state */}
      {error && !isLoading && (
        <Card className="p-8 text-center">
          <p className="text-red-400 font-medium">Could not load metrics.</p>
          <p className="text-slate-400 text-sm mt-1">
            Make sure the backend is running and the model is trained.
          </p>
          <Button className="mt-4" onClick={() => refetch()}>Retry</Button>
        </Card>
      )}

      {/* Metric cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        {isLoading
          ? Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)
          : metrics
          ? [
              { label: 'Accuracy',  value: `${(metrics.accuracy   * 100).toFixed(2)}%`, sub: `${metrics.test_samples} test samples`,    color: 'text-brand-400' },
              { label: 'F1 Score',  value: `${(metrics.f1_weighted * 100).toFixed(2)}%`, sub: 'Weighted average',                       color: 'text-violet-400' },
              { label: 'ROC-AUC',   value: `${(metrics.roc_auc     * 100).toFixed(2)}%`, sub: 'Area under curve',                       color: 'text-emerald-400' },
              { label: 'CV Acc',    value: `${(metrics.cv_accuracy_mean * 100).toFixed(2)}%`, sub: `±${(metrics.cv_accuracy_std * 100).toFixed(2)}% (5-fold)`, color: 'text-amber-400' },
            ].map((m) => <MetricCard key={m.label} {...m} />)
          : null}
      </div>

      {/* Charts row */}
      {metrics && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Radar */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-100">Performance Radar</h3>
            </CardHeader>
            <CardBody>
              <MetricRadar metrics={metrics} />
            </CardBody>
          </Card>

          {/* Bar chart */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-100">Score Breakdown</h3>
            </CardHeader>
            <CardBody>
              <MetricBars metrics={metrics} />
            </CardBody>
          </Card>

          {/* Confusion matrix */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-100">Confusion Matrix</h3>
              <p className="text-xs text-slate-400 mt-0.5">Actual → Predicted</p>
            </CardHeader>
            <CardBody>
              <ConfusionMatrix />
            </CardBody>
          </Card>
        </div>
      )}

      {/* Model info cards */}
      {metrics && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <Card className="p-5">
            <div className="flex items-center gap-2 mb-3">
              <Award size={16} className="text-brand-400" />
              <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-100">Architecture</h3>
            </div>
            <ul className="space-y-1.5 text-sm text-slate-500 dark:text-slate-400">
              <li>📐 <strong className="text-slate-200">Logistic Regression</strong> – linear decision boundary</li>
              <li>🌲 <strong className="text-slate-200">Random Forest (200 trees)</strong> – non-linear, feature importance</li>
              <li>🚀 <strong className="text-slate-200">Gradient Boosting</strong> – sequential error correction</li>
              <li className="pt-1 text-xs text-slate-500">Soft voting: avg probability across 3 models</li>
            </ul>
          </Card>

          <Card className="p-5">
            <div className="flex items-center gap-2 mb-3">
              <ShieldCheck size={16} className="text-emerald-400" />
              <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-100">Dataset</h3>
            </div>
            <ul className="space-y-1.5 text-sm text-slate-500 dark:text-slate-400">
              <li>📊 <strong className="text-slate-200">{metrics.train_samples + metrics.test_samples}</strong> total samples</li>
              <li>🏋️ <strong className="text-slate-200">{metrics.train_samples}</strong> training / <strong className="text-slate-200">{metrics.test_samples}</strong> test</li>
              <li>📌 <strong className="text-slate-200">30</strong> nuclear features per sample</li>
              <li>⚖️ Stratified 80/20 split (class-balanced)</li>
              <li className="pt-1 text-xs text-slate-500">UCI Wisconsin Breast Cancer Dataset</li>
            </ul>
          </Card>

          <Card className="p-5">
            <div className="flex items-center gap-2 mb-3">
              <Zap size={16} className="text-amber-400" />
              <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-100">Performance</h3>
            </div>
            <ul className="space-y-1.5 text-sm text-slate-500 dark:text-slate-400">
              <li>⚡ Inference: <strong className="text-slate-200">&lt; 20 ms</strong> typical</li>
              <li>🔁 5-fold cross-validation used for tuning</li>
              <li>📦 Serialised with <strong className="text-slate-200">joblib</strong> (not pickle)</li>
              <li>🔒 <code className="text-xs bg-slate-800 px-1 rounded">class_weight='balanced'</code></li>
              <li className="pt-1 text-xs text-slate-500">Model version: {metrics.version}</li>
            </ul>
          </Card>
        </div>
      )}
    </div>
  )
}
