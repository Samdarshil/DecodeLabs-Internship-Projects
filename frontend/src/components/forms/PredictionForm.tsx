/**
 * src/components/forms/PredictionForm.tsx
 * 30-feature breast cancer input form — 3 tabbed groups, Zod validation.
 */
import { useState } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion, AnimatePresence } from 'framer-motion'
import { clsx } from 'clsx'
import { FlaskConical, Microscope, AlertTriangle } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import type { PredictionInput } from '@/services/api'

// ── Zod schema ───────────────────────────────────────────────────────────────
const schema = z.object({
  // mean
  radius_mean:             z.coerce.number().min(0).max(30),
  texture_mean:            z.coerce.number().min(0).max(40),
  perimeter_mean:          z.coerce.number().min(0).max(200),
  area_mean:               z.coerce.number().min(0).max(2600),
  smoothness_mean:         z.coerce.number().min(0).max(0.25),
  compactness_mean:        z.coerce.number().min(0).max(0.40),
  concavity_mean:          z.coerce.number().min(0).max(0.45),
  concave_points_mean:     z.coerce.number().min(0).max(0.22),
  symmetry_mean:           z.coerce.number().min(0).max(0.35),
  fractal_dimension_mean:  z.coerce.number().min(0).max(0.10),
  // se
  radius_se:               z.coerce.number().min(0).max(3),
  texture_se:              z.coerce.number().min(0).max(5),
  perimeter_se:            z.coerce.number().min(0).max(22),
  area_se:                 z.coerce.number().min(0).max(550),
  smoothness_se:           z.coerce.number().min(0).max(0.02),
  compactness_se:          z.coerce.number().min(0).max(0.14),
  concavity_se:            z.coerce.number().min(0).max(0.40),
  concave_points_se:       z.coerce.number().min(0).max(0.06),
  symmetry_se:             z.coerce.number().min(0).max(0.08),
  fractal_dimension_se:    z.coerce.number().min(0).max(0.03),
  // worst
  radius_worst:            z.coerce.number().min(0).max(40),
  texture_worst:           z.coerce.number().min(0).max(52),
  perimeter_worst:         z.coerce.number().min(0).max(260),
  area_worst:              z.coerce.number().min(0).max(4300),
  smoothness_worst:        z.coerce.number().min(0).max(0.24),
  compactness_worst:       z.coerce.number().min(0).max(1.10),
  concavity_worst:         z.coerce.number().min(0).max(1.30),
  concave_points_worst:    z.coerce.number().min(0).max(0.32),
  symmetry_worst:          z.coerce.number().min(0).max(0.70),
  fractal_dimension_worst: z.coerce.number().min(0).max(0.22),
})

type FormValues = z.infer<typeof schema>

// ── Sample data ───────────────────────────────────────────────────────────────
const MALIGNANT_SAMPLE: FormValues = {
  radius_mean: 17.99, texture_mean: 10.38, perimeter_mean: 122.8, area_mean: 1001.0,
  smoothness_mean: 0.1184, compactness_mean: 0.2776, concavity_mean: 0.3001,
  concave_points_mean: 0.1471, symmetry_mean: 0.2419, fractal_dimension_mean: 0.07871,
  radius_se: 1.095, texture_se: 0.9053, perimeter_se: 8.589, area_se: 153.4,
  smoothness_se: 0.006399, compactness_se: 0.04904, concavity_se: 0.05373,
  concave_points_se: 0.01587, symmetry_se: 0.03003, fractal_dimension_se: 0.006193,
  radius_worst: 25.38, texture_worst: 17.33, perimeter_worst: 184.6, area_worst: 2019.0,
  smoothness_worst: 0.1622, compactness_worst: 0.6656, concavity_worst: 0.7119,
  concave_points_worst: 0.2654, symmetry_worst: 0.4601, fractal_dimension_worst: 0.1189,
}

const BENIGN_SAMPLE: FormValues = {
  radius_mean: 12.32, texture_mean: 12.39, perimeter_mean: 78.85, area_mean: 464.1,
  smoothness_mean: 0.1028, compactness_mean: 0.0698, concavity_mean: 0.0399,
  concave_points_mean: 0.037, symmetry_mean: 0.196, fractal_dimension_mean: 0.0595,
  radius_se: 0.236, texture_se: 0.666, perimeter_se: 1.67, area_se: 17.43,
  smoothness_se: 0.00819, compactness_se: 0.0145, concavity_se: 0.0164,
  concave_points_se: 0.00971, symmetry_se: 0.02116, fractal_dimension_se: 0.00262,
  radius_worst: 13.5, texture_worst: 15.64, perimeter_worst: 86.97, area_worst: 549.1,
  smoothness_worst: 0.1385, compactness_worst: 0.1266, concavity_worst: 0.1231,
  concave_points_worst: 0.1047, symmetry_worst: 0.3187, fractal_dimension_worst: 0.07419,
}

// ── Field configs per tab ─────────────────────────────────────────────────────
const TABS = [
  {
    id: 'mean',
    label: 'Mean Values',
    icon: FlaskConical,
    desc: 'Average feature measurements across the cell nuclei image.',
    fields: [
      { name: 'radius_mean',            label: 'Radius',            step: '0.001', hint: '0 – 30 µm' },
      { name: 'texture_mean',           label: 'Texture',           step: '0.01',  hint: '0 – 40' },
      { name: 'perimeter_mean',         label: 'Perimeter',         step: '0.01',  hint: '0 – 200 µm' },
      { name: 'area_mean',              label: 'Area',              step: '0.1',   hint: '0 – 2600 µm²' },
      { name: 'smoothness_mean',        label: 'Smoothness',        step: '0.0001',hint: '0 – 0.25' },
      { name: 'compactness_mean',       label: 'Compactness',       step: '0.0001',hint: '0 – 0.40' },
      { name: 'concavity_mean',         label: 'Concavity',         step: '0.0001',hint: '0 – 0.45' },
      { name: 'concave_points_mean',    label: 'Concave Points',    step: '0.0001',hint: '0 – 0.22' },
      { name: 'symmetry_mean',          label: 'Symmetry',          step: '0.0001',hint: '0 – 0.35' },
      { name: 'fractal_dimension_mean', label: 'Fractal Dimension', step: '0.0001',hint: '0 – 0.10' },
    ],
  },
  {
    id: 'se',
    label: 'Std Error',
    icon: Microscope,
    desc: 'Standard error of each feature measurement.',
    fields: [
      { name: 'radius_se',            label: 'Radius SE',            step: '0.001',  hint: '0 – 3' },
      { name: 'texture_se',           label: 'Texture SE',           step: '0.001',  hint: '0 – 5' },
      { name: 'perimeter_se',         label: 'Perimeter SE',         step: '0.001',  hint: '0 – 22' },
      { name: 'area_se',              label: 'Area SE',              step: '0.01',   hint: '0 – 550' },
      { name: 'smoothness_se',        label: 'Smoothness SE',        step: '0.00001',hint: '0 – 0.02' },
      { name: 'compactness_se',       label: 'Compactness SE',       step: '0.00001',hint: '0 – 0.14' },
      { name: 'concavity_se',         label: 'Concavity SE',         step: '0.00001',hint: '0 – 0.40' },
      { name: 'concave_points_se',    label: 'Concave Points SE',    step: '0.00001',hint: '0 – 0.06' },
      { name: 'symmetry_se',          label: 'Symmetry SE',          step: '0.00001',hint: '0 – 0.08' },
      { name: 'fractal_dimension_se', label: 'Fractal Dimension SE', step: '0.00001',hint: '0 – 0.03' },
    ],
  },
  {
    id: 'worst',
    label: 'Worst Values',
    icon: AlertTriangle,
    desc: 'Largest (worst) value of each feature across all nuclei.',
    fields: [
      { name: 'radius_worst',            label: 'Radius Worst',            step: '0.001',  hint: '0 – 40' },
      { name: 'texture_worst',           label: 'Texture Worst',           step: '0.01',   hint: '0 – 52' },
      { name: 'perimeter_worst',         label: 'Perimeter Worst',         step: '0.01',   hint: '0 – 260' },
      { name: 'area_worst',              label: 'Area Worst',              step: '0.1',    hint: '0 – 4300' },
      { name: 'smoothness_worst',        label: 'Smoothness Worst',        step: '0.0001', hint: '0 – 0.24' },
      { name: 'compactness_worst',       label: 'Compactness Worst',       step: '0.0001', hint: '0 – 1.10' },
      { name: 'concavity_worst',         label: 'Concavity Worst',         step: '0.0001', hint: '0 – 1.30' },
      { name: 'concave_points_worst',    label: 'Concave Points Worst',    step: '0.0001', hint: '0 – 0.32' },
      { name: 'symmetry_worst',          label: 'Symmetry Worst',          step: '0.0001', hint: '0 – 0.70' },
      { name: 'fractal_dimension_worst', label: 'Fractal Dimension Worst', step: '0.0001', hint: '0 – 0.22' },
    ],
  },
] as const

// ── Component ─────────────────────────────────────────────────────────────────
interface Props {
  onSubmit: (data: PredictionInput) => void
  isLoading: boolean
}

export function PredictionForm({ onSubmit, isLoading }: Props) {
  const [activeTab, setActiveTab] = useState(0)

  const { control, handleSubmit, reset, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: MALIGNANT_SAMPLE,
  })

  const tabErrors = TABS.map((tab) =>
    tab.fields.some((f) => errors[f.name as keyof FormValues])
  )

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      {/* Sample buttons */}
      <div className="flex gap-2 mb-5">
        <span className="text-xs text-slate-400 self-center mr-1">Load sample:</span>
        <button
          type="button"
          onClick={() => reset(MALIGNANT_SAMPLE)}
          className="px-3 py-1 text-xs rounded-md bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20 transition-colors"
        >
          Malignant Case
        </button>
        <button
          type="button"
          onClick={() => reset(BENIGN_SAMPLE)}
          className="px-3 py-1 text-xs rounded-md bg-green-500/10 text-green-400 border border-green-500/20 hover:bg-green-500/20 transition-colors"
        >
          Benign Case
        </button>
      </div>

      {/* Tab bar */}
      <div className="flex gap-1 mb-5 border-b border-slate-200 dark:border-slate-800">
        {TABS.map((tab, i) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(i)}
              className={clsx(
                'flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium rounded-t-lg transition-all relative',
                activeTab === i
                  ? 'text-brand-600 dark:text-brand-400 bg-white dark:bg-slate-900'
                  : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200',
              )}
            >
              <Icon size={13} />
              {tab.label}
              {tabErrors[i] && (
                <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-red-500" />
              )}
              {activeTab === i && (
                <motion.div
                  layoutId="tab-underline"
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-brand-600 dark:bg-brand-400"
                />
              )}
            </button>
          )
        })}
      </div>

      {/* Tab content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -6 }}
          transition={{ duration: 0.18 }}
        >
          <p className="text-xs text-slate-400 dark:text-slate-500 mb-4">
            {TABS[activeTab].desc}
          </p>
          <div className="grid grid-cols-1 xs:grid-cols-2 gap-x-4 gap-y-3">
            {TABS[activeTab].fields.map((field) => {
              const err = errors[field.name as keyof FormValues]
              return (
                <div key={field.name}>
                  <label
                    htmlFor={field.name}
                    className="block text-xs font-medium text-slate-600 dark:text-slate-300 mb-1"
                  >
                    {field.label}
                    <span className="ml-1.5 text-slate-400 font-normal">{field.hint}</span>
                  </label>
                  <Controller
                    name={field.name as keyof FormValues}
                    control={control}
                    render={({ field: f }) => (
                      <input
                        {...f}
                        id={field.name}
                        type="number"
                        step={field.step}
                        aria-invalid={!!err}
                        aria-describedby={err ? `${field.name}-err` : undefined}
                        className={clsx(
                          'w-full h-9 rounded-lg px-3 text-sm',
                          'bg-slate-50 dark:bg-slate-800/60',
                          'border transition-colors',
                          'focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500',
                          'font-mono text-slate-800 dark:text-slate-100',
                          err
                            ? 'border-red-400 dark:border-red-500 bg-red-50 dark:bg-red-900/10'
                            : 'border-slate-200 dark:border-slate-700',
                        )}
                      />
                    )}
                  />
                  {err && (
                    <p id={`${field.name}-err`} className="mt-0.5 text-xs text-red-500">
                      {err.message}
                    </p>
                  )}
                </div>
              )
            })}
          </div>
        </motion.div>
      </AnimatePresence>

      {/* Navigation + submit */}
      <div className="mt-6 flex items-center justify-between gap-3">
        <div className="flex gap-1">
          {TABS.map((_, i) => (
            <button
              key={i}
              type="button"
              onClick={() => setActiveTab(i)}
              className={clsx(
                'w-2 h-2 rounded-full transition-all',
                activeTab === i ? 'bg-brand-600 w-4' : 'bg-slate-300 dark:bg-slate-700',
              )}
            />
          ))}
        </div>
        <div className="flex gap-2">
          {activeTab < TABS.length - 1 ? (
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={() => setActiveTab((t) => t + 1)}
            >
              Next →
            </Button>
          ) : null}
          <Button type="submit" size="md" loading={isLoading}>
            {isLoading ? 'Analysing…' : '🧬 Run Prediction'}
          </Button>
        </div>
      </div>
    </form>
  )
}
