/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        vazir: ['Vazirmatn', 'sans-serif'],
      },
      colors: {
        'forest': '#2E7D32',
        'leaf': '#43A047',
        'gold': '#FFB300',
        'light': '#F1F8E9',
        'dark': '#1A1A1A',
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
}
