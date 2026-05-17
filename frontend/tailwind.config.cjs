/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        pagebg: '#0b1220',
        cardbg: '#0f1724',
        cardtext: '#e6eef8',
        muted: '#9fb0d8',
        accent: '#6366f1',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
    },
  },
  plugins: [],
}
