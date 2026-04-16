import type { Config } from 'tailwindcss'

export default {
  content: [
    './index.html',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3525cd',
        'primary-container': '#4f46e5',
        'on-primary': '#ffffff',
        'primary-fixed': '#e2dfff',
        secondary: '#4648d4',
        'secondary-container': '#6063ee',
        'on-surface': '#191c1d',
        'on-surface-variant': '#464555',
        surface: '#f8f9fa',
        'surface-container': '#edeeef',
        'surface-container-low': '#f3f4f5',
        'surface-container-lowest': '#ffffff',
        'surface-container-high': '#e7e8e9',
        'outline-variant': '#c7c4d8',
        error: '#ba1a1a',
      },
      fontFamily: {
        headline: ['Manrope', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
} satisfies Config
