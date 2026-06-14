/**
 * src/components/ui/Card.tsx
 */
import { HTMLAttributes, forwardRef } from 'react'
import { clsx } from 'clsx'
import { motion } from 'framer-motion'

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  hover?: boolean
  glass?: boolean
}

export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ hover, glass, children, className, ...props }, ref) => (
    <motion.div
      ref={ref}
      whileHover={hover ? { y: -2, boxShadow: '0 8px 30px rgba(0,0,0,0.18)' } : {}}
      transition={{ duration: 0.2 }}
      className={clsx(
        'rounded-2xl border',
        glass
          ? 'bg-white/70 dark:bg-slate-900/70 backdrop-blur border-white/20 dark:border-slate-700/50'
          : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800',
        'shadow-sm',
        className,
      )}
      {...(props as any)}
    >
      {children}
    </motion.div>
  )
)
Card.displayName = 'Card'

export function CardHeader({ children, className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={clsx('px-6 py-5 border-b border-slate-100 dark:border-slate-800', className)} {...props}>
      {children}
    </div>
  )
}

export function CardBody({ children, className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={clsx('px-6 py-5', className)} {...props}>
      {children}
    </div>
  )
}
