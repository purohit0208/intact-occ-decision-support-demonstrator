import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#08111d",
        panel: "#0e1826",
        panelEdge: "#233246",
        signal: {
          cyan: "#54d1db",
          amber: "#f8b84e",
          coral: "#ff6c5c",
          moss: "#82c98f",
        },
      },
      boxShadow: {
        panel: "0 18px 40px rgba(0, 0, 0, 0.22)",
      },
      fontFamily: {
        sans: ["Segoe UI Variable", "Bahnschrift", "Trebuchet MS", "sans-serif"],
      },
    },
  },
  plugins: [],
} satisfies Config;
