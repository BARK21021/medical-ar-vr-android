/** @type {import('tailwindcss').Config} */

export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    container: {
      center: true,
    },
    extend: {
      colors: {
        brand: {
          bg: "#0F172A", // modern slate-900 instead of old #1a1c2e
          card: "#1E293B", // slate-800
          cardAlt: "#0F172A", // slate-900
          accent: "#06B6D4", // cyan-500
          accentHover: "#0891B2", // cyan-600
          text: "#F8FAFC", // slate-50
          muted: "#94A3B8", // slate-400
          success: "#10B981", // emerald-500
          danger: "#EF4444", // red-500
        }
      }
    },
  },
  plugins: [],
};
