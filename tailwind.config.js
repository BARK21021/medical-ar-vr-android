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
          bg: "#0F172A",
          card: "#1E293B",
          cardAlt: "#0F172A",
          accent: "#06B6D4",
          accentHover: "#0891B2",
          text: "#F8FAFC",
          muted: "#94A3B8",
          success: "#10B981",
          danger: "#EF4444",
        }
      }
    },
  },
  plugins: [],
};