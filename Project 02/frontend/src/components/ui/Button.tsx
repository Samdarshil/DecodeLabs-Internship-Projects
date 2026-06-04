/**
 * src/components/ui/Button.tsx
 */
import { forwardRef, ButtonHTMLAttributes } from 'react'
import { clsx } from 'clsx'
import { motion } from 'framer-motion'

type Variant = 'primary' | 'secondary' | 'ghost' | 'destructive'
type Size    = 'sm' | 'md' | 'lg'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?:  Variant
  size?:     Size
  loading?:  boolean
}

const variants: Record<Variant, string> = {
  primary:     'bg-brand-600 hover:bg-brand-700 text-white shadow-sm hover:shadow-glow-blue focus-visible:ring-brand-500',
  secondary:   'bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700',
  ghost:       'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800',
  destructive: 'bg-red-600 hover:bg-red-700 text-white shadow-sm',
}

const sizes: Record<Size, string> = {
  sm: 'h-8  px-3  text-sm  gap-1.5',
  md: 'h-10 px-4  text-sm  gap-2',
  lg: 'h-12 px-6  text-base gap-2.5',
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', loading, children, className, disabled, ...props }, ref) => (
    <motion.button
      ref={ref}
      whileHover={{ scale: disabled || loading ? 1 : 1.02 }}
      whileTap={  { scale: disabled || loading ? 1 : 0.97 }}
      disabled={disabled || loading}
      className={clsx(
        'inline-flex items-center justify-center rounded-lg font-medium',
        'transition-all duration-150',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2',
        'disabled:pointer-events-none disabled:opacity-50',
        variants[variant],
        sizes[size],
        className,
      )}
      {...(props as any)}
    >
      {loading && (
        <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      )}
      {children}
    </motion.button>
  )
)
Button.displayName = 'Button'
