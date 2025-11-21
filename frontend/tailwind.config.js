/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          bg: '#0a0e1a',
          surface: '#131824',
          border: '#1e2533',
          hover: '#1a1f2e',
        },
        severity: {
          high: '#ef4444',
          med: '#f59e0b',
          low: '#3b82f6',
        }
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
