/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./glamsage/static/css/*.css",
    "./glamsage/templates/*.html",
    "./glamsage/templates/admin/*.html",
    "./glamsage/templates/clients/*.html",
    "./glamsage/templates/home/*.html",
    "./glamsage/templates/providers/*.html",
    "./glamsage/templates/nav/*.html",
  ],
  // safelist: [{ pattern: /.*$/ }],

  theme: {
    extend: {
      colors: {
        "gpt-pro": "#310413",
        "red-wine": "#280101",
        // "nav-bg": "#0369a1",
        // "nav-bg": "#d20f39",
        // "nav-bg": "#7f1d1d",
        "brand-color": "#00334b",
        "nav-bg": "#0f172a",
        "nav-text": "#ffffff",
      },
    },
  },

  plugins: [require("daisyui"), require("@tailwindcss/forms")],
  daisyui: {
    themes: [
      {
        default: {
          "base-content": "black",
          // primary: "#a78bfa",
          // primary: "#f472b6",
          // primary: "#fb7185",
          // primary: "#0ea5e9",
          primary: "#38bdf8",
          secondary: "#4b5563",
          accent: "#4338ca",
          neutral: "#9ca3af",
          // "base-100": "#fbcfe8",
          // "base-100": "#fbcfe8",
          // "base-100": "#bae6fd",
          "base-100": "#d5f5f5",
          info: "#7dd3fc",
          success: "#22c55e",
          warning: "#facc15",
          error: "#ef4444",
          "gpt-pro": "#310413",
        },
      },
    ],
  },
};
