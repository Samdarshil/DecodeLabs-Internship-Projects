/**
 * src/components/ui/ConfidenceMeter.tsx
 * Animated SVG radial progress with spring-based fill animation.
 */
import { useEffect, useRef } from 'react'
import { motion, useMotionValue, useTransform, animate } from 'framer-motion'

interface Props {
  confidence: number        // 0–1
  label:      string        // "Malignant" | "Benign"
  size?:      number
}

export function ConfidenceMeter({ confidence, label, size = 180 }: Props) {
  const isMalignant = label === 'Malignant'
  const color       = isMalignant ? '#ef4444' : '#22c55e'
  const glowColor   = isMalignant ? 'rgba(239,68,68,0.3)' : 'rgba(34,197,94,0.3)'

  const pct     = confidence * 100
  const r       = (size - 24) / 2
  const circ    = 2 * Math.PI * r
  const cx      = size / 2
  const cy      = size / 2

  const progress = useMotionValue(0)
  const dashOffset = useTransform(progress, (v) => circ - (v / 100) * circ)

  useEffect(() => {
    const ctrl = animate(progress, pct, { duration: 1.2, ease: [0.34, 1.56, 0.64, 1] })
    return ctrl.stop
  }, [pct])

  const displayPct = useTransform(progress, (v) => `${Math.round(v)}%`)

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative" style={{ width: size, height: size }}>
        {/* Glow backdrop */}
        <div
          className="absolute inset-0 rounded-full blur-xl opacity-40"
          style={{ background: glowColor }}
        />

        <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
          {/* Track */}
          <circle
            cx={cx} cy={cy} r={r}
            fill="none"
            stroke="currentColor"
            strokeWidth={10}
            className="text-slate-200 dark:text-slate-700"
          />
          {/* Progress arc */}
          <motion.circle
            cx={cx} cy={cy} r={r}
            fill="none"
            stroke={color}
            strokeWidth={10}
            strokeLinecap="round"
            strokeDasharray={circ}
            style={{ strokeDashoffset: dashOffset }}
            filter={`drop-shadow(0 0 6px ${color})`}
          />
        </svg>

        {/* Centre text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            className="text-3xl font-bold tabular-nums"
            style={{ color }}
          >
            {displayPct}
          </motion.span>
          <span className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 font-medium">
            confidence
          </span>
        </div>
      </div>

      {/* Label badge */}
      <span
        className="px-4 py-1.5 rounded-full text-sm font-semibold tracking-wide"
        style={{
          background: isMalignant ? 'rgba(239,68,68,0.12)' : 'rgba(34,197,94,0.12)',
          color,
          border: `1px solid ${color}40`,
        }}
      >
        {label.toUpperCase()}
      </span>
    </div>
  )
}
