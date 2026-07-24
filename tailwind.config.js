/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          900: '#1a3a52',
          800: '#2a4a62',
          700: '#3a5a72',
        },
        gold: '#d4af37',
      },
      fontFamily: {
        sans: ['Calibri', 'Cambria', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
