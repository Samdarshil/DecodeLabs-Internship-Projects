/**
 * src/App.tsx — Root component with navbar, routing, query client.
 */
import { Suspense, lazy } from 'react'
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Sun, Moon, Activity, BarChart2, History, Github } from 'lucide-react'
import { useTheme } from '@/hooks/useTheme'
import { useHistoryStore } from '@/store/predictionHistory'

// ── Lazy pages ───────────────────────────────────────────────────────────────
const Home      = lazy(() => import('@/pages/Home'))
const Dashboard = lazy(() => import('@/pages/Dashboard'))
const Analytics = lazy(() => import('@/pages/Analytics'))

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

// ── Spinner ───────────────────────────────────────────────────────────────────
function Spinner() {
  return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 rounded-full border-2 border-brand-500 border-t-transparent animate-spin" />
    </div>
  )
}

// ── Navbar ────────────────────────────────────────────────────────────────────
function Navbar() {
  const { toggle, isDark } = useTheme()
  const historyCount = useHistoryStore((s) => s.entries.length)

  const navItems = [
    { to: '/',          label: 'Predict',   icon: Activity },
    { to: '/dashboard', label: 'History',   icon: History,  badge: historyCount || undefined },
    { to: '/analytics', label: 'Analytics', icon: BarChart2 },
  ]

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-950/80 backdrop-blur">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        {/* Logo */}
        <NavLink to="/" className="flex items-center gap-2 font-bold text-slate-900 dark:text-white">
          <span className="text-xl">🧬</span>
          <span className="text-brand-600 dark:text-brand-400">OncAI</span>
          <span className="hidden sm:inline text-slate-400 font-normal text-sm">Breast Cancer Classifier</span>
        </NavLink>

        {/* Nav links */}
        <nav className="flex items-center gap-0.5" aria-label="Main navigation">
          {navItems.map(({ to, label, icon: Icon, badge }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `relative flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors
                 ${isActive
                   ? 'text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-500/10'
                   : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800'
                 }`
              }
            >
              <Icon size={15} />
              <span className="hidden sm:inline">{label}</span>
              {badge ? (
                <span className="absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full bg-brand-600 text-white text-[10px] flex items-center justify-center font-bold">
                  {badge > 9 ? '9+' : badge}
                </span>
              ) : null}
            </NavLink>
          ))}
        </nav>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <motion.button
            onClick={toggle}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-500
                       hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white transition-colors"
            aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {isDark ? <Sun size={15} /> : <Moon size={15} />}
          </motion.button>
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-500
                       hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white transition-colors"
            aria-label="GitHub repository"
          >
            <Github size={15} />
          </a>
        </div>
      </div>
    </header>
  )
}

// ── Root ──────────────────────────────────────────────────────────────────────
export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100">
          <Navbar />
          <main>
            <Suspense fallback={<Spinner />}>
              <Routes>
                <Route path="/"          element={<Home />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/analytics" element={<Analytics />} />
              </Routes>
            </Suspense>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
