/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0b0f19',
        surface: '#111827',
        accent: {
          razorpay: '#0284c7',
          intelligence: '#6366f1',
        }
      }
    },
  },
  plugins: [],
}
