/**
 * src/pages/Home.tsx — Main prediction interface.
 * Layout: left column = form | right column = result + feature importance.
 */
import { motion, AnimatePresence } from 'framer-motion'
import { AlertCircle, Clock, Cpu, Info } from 'lucide-react'
import { PredictionForm } from '@/components/forms/PredictionForm'
import { ConfidenceMeter } from '@/components/ui/ConfidenceMeter'
import { FeatureImportanceChart } from '@/components/charts/FeatureImportance'
import { Card, CardHeader, CardBody } from '@/components/ui/Card'
import { usePrediction } from '@/hooks/usePrediction'

function StatBadge({ icon: Icon, label, value }: { icon: any; label: string; value: string }) {
  return (
    <div className="flex items-center gap-2 text-sm">
      <Icon size={14} className="text-slate-400" />
      <span className="text-slate-400">{label}</span>
      <span className="font-mono text-slate-200 font-medium">{value}</span>
    </div>
  )
}

export default function Home() {
  const { predict, isLoading, result, error, reset } = usePrediction()

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Page header */}
      <div className="mb-8">
        <motion.h1
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-3xl font-bold text-slate-900 dark:text-white"
        >
          Tumour Classification
        </motion.h1>
        <p className="mt-1.5 text-slate-500 dark:text-slate-400 max-w-xl">
          Enter 30 nuclear cell measurements from FNA imaging to classify a breast mass as
          malignant or benign using an ensemble ML model.
        </p>

        {/* Disclaimer */}
        <div className="mt-3 flex items-start gap-2 px-3 py-2 rounded-lg bg-amber-500/10 border border-amber-500/20 max-w-xl">
          <Info size={14} className="text-amber-400 mt-0.5 shrink-0" />
          <p className="text-xs text-amber-300/80">
            For research and educational purposes only. Not a clinical diagnostic tool.
            Always consult a qualified medical professional.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* ── Input form ─────────────────────────────────────── */}
        <div className="lg:col-span-3">
          <Card>
            <CardHeader>
              <h2 className="text-base font-semibold text-slate-800 dark:text-slate-100">
                Nuclear Feature Input
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                All 30 Wisconsin Breast Cancer Dataset features
              </p>
            </CardHeader>
            <CardBody>
              <PredictionForm onSubmit={predict} isLoading={isLoading} />
            </CardBody>
          </Card>
        </div>

        {/* ── Result panel ───────────────────────────────────── */}
        <div className="lg:col-span-2 space-y-5">
          <AnimatePresence mode="wait">
            {error && (
              <motion.div
                key="error"
                initial={{ opacity: 0, scale: 0.97 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                className="flex items-start gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/20"
              >
                <AlertCircle size={16} className="text-red-400 mt-0.5 shrink-0" />
                <div>
                  <p className="text-sm font-medium text-red-300">Prediction failed</p>
                  <p className="text-xs text-red-400/80 mt-0.5">{error}</p>
                </div>
              </motion.div>
            )}

            {!result && !error && (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center justify-center gap-4 py-16 rounded-2xl
                           border-2 border-dashed border-slate-200 dark:border-slate-800"
              >
                <div className="w-16 h-16 rounded-2xl bg-brand-500/10 flex items-center justify-center">
                  <span className="text-3xl">🧬</span>
                </div>
                <div className="text-center">
                  <p className="text-sm font-medium text-slate-600 dark:text-slate-300">
                    Ready for analysis
                  </p>
                  <p className="text-xs text-slate-400 mt-1">
                    Fill in the features and click Run Prediction
                  </p>
                </div>
              </motion.div>
            )}

            {result && (
              <motion.div
                key="result"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="space-y-5"
              >
                {/* Confidence card */}
                <Card>
                  <CardBody className="flex flex-col items-center py-8">
                    <ConfidenceMeter
                      confidence={result.confidence}
                      label={result.prediction}
                      size={190}
                    />

                    {/* Probability breakdown */}
                    <div className="mt-6 w-full space-y-2">
                      <div className="flex justify-between items-center text-xs">
                        <span className="text-slate-400">Malignant probability</span>
                        <span className="font-mono font-semibold text-red-400">
                          {(result.probability_malignant * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                        <motion.div
                          className="h-full rounded-full bg-red-500"
                          initial={{ width: 0 }}
                          animate={{ width: `${result.probability_malignant * 100}%` }}
                          transition={{ duration: 0.8, ease: 'easeOut' }}
                        />
                      </div>
                      <div className="flex justify-between items-center text-xs">
                        <span className="text-slate-400">Benign probability</span>
                        <span className="font-mono font-semibold text-green-400">
                          {(result.probability_benign * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                        <motion.div
                          className="h-full rounded-full bg-green-500"
                          initial={{ width: 0 }}
                          animate={{ width: `${result.probability_benign * 100}%` }}
                          transition={{ duration: 0.8, ease: 'easeOut', delay: 0.1 }}
                        />
                      </div>
                    </div>

                    {/* Meta stats */}
                    <div className="mt-4 w-full pt-4 border-t border-slate-100 dark:border-slate-800 space-y-1.5">
                      <StatBadge icon={Clock} label="Inference" value={`${result.inference_time_ms.toFixed(1)} ms`} />
                      <StatBadge icon={Cpu}   label="Model"     value={`v${result.model_version}`} />
                    </div>
                  </CardBody>
                </Card>

                {/* Feature importance card */}
                <Card>
                  <CardHeader>
                    <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-100">
                      Feature Contributions
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Top 10 features driving this prediction
                    </p>
                  </CardHeader>
                  <CardBody>
                    <FeatureImportanceChart features={result.top_features} />
                  </CardBody>
                </Card>

                {/* New prediction button */}
                <button
                  type="button"
                  onClick={reset}
                  className="w-full py-2 text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-200
                             transition-colors border border-dashed border-slate-200 dark:border-slate-800
                             rounded-xl hover:border-slate-400 dark:hover:border-slate-600"
                >
                  ↺ Clear result
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}
