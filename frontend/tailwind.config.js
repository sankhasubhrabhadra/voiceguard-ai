/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#FAFAFA",
        text: "#111111",
        accent: {
          DEFAULT: "#4338CA",
          hover: "#3730A3",
          subtle: "#EEF2FF"
        },
        risk: {
          low: "#0D9488",
          "low-bg": "#F0FDFA",
          medium: "#D97706",
          "medium-bg": "#FFFBEB",
          high: "#DC2626",
          "high-bg": "#FEF2F2"
        }
      },
      borderRadius: {
        DEFAULT: "8px",
        lg: "8px",
        md: "8px",
        sm: "8px",
        xl: "8px"
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif'],
      },
      boxShadow: {
        card: "0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px -1px rgba(0, 0, 0, 0.05)",
      }
    },
  },
  plugins: [],
}
