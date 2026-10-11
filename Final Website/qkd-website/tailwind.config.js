/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#8ecff2',
          on: '#003548',
          container: '#004d67',
          'on-container': '#c1e8ff',
        },
        secondary: {
          DEFAULT: '#b5c9d7',
          on: '#1f333d',
          container: '#364954',
          'on-container': '#d1e6f3',
        },
        tertiary: {
          DEFAULT: '#c9c2ea',
          on: '#312c4c',
          container: '#474364',
          'on-container': '#e5deff',
        },
        error: {
          DEFAULT: '#ffb4ab',
          on: '#690005',
        },
        surface: {
          DEFAULT: '#0f1417',
          dim: '#0f1417',
          bright: '#353a3d',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Space Grotesk', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'scale-in': 'scaleIn 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
    },
  },
  plugins: [],
}
