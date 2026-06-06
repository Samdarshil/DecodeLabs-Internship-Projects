/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    screens: {
      xs: '375px', sm: '640px', md: '768px', lg: '1024px', xl: '1280px', '2xl': '1536px',
    },
    extend: {
      colors: {
        brand: {
          50:  '#eef9ff',
          100: '#d9f2ff',
          200: '#bce8ff',
          300: '#8dd9ff',
          400: '#56c1ff',
          500: '#2fa3f7',
          600: '#1585e8',
          700: '#0d6bc9',
          800: '#1257a3',
          900: '#144a82',
        },
        malignant: {
          light: '#fef2f2',
          DEFAULT: '#ef4444',
          dark: '#b91c1c',
        },
        benign: {
          light: '#f0fdf4',
          DEFAULT: '#22c55e',
          dark: '#15803d',
        },
      },
      fontFamily: {
        sans: ['Inter var', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'slide-up': 'slideUp 0.4s ease-out',
        'fade-in': 'fadeIn 0.3s ease-out',
        'shimmer': 'shimmer 2s linear infinite',
      },
      keyframes: {
        slideUp: { from: { opacity: '0', transform: 'translateY(12px)' }, to: { opacity: '1', transform: 'none' } },
        fadeIn:  { from: { opacity: '0' }, to: { opacity: '1' } },
        shimmer: { '0%': { backgroundPosition: '-200% 0' }, '100%': { backgroundPosition: '200% 0' } },
      },
      boxShadow: {
        'glow-blue': '0 0 20px rgba(47, 163, 247, 0.25)',
        'glow-red':  '0 0 20px rgba(239, 68, 68, 0.25)',
        'glow-green': '0 0 20px rgba(34, 197, 94, 0.25)',
      },
    },
  },
  plugins: [],
}
