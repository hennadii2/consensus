const COLORS = require("./src/constants/colors.json");
const isObject = require("lodash/isObject");

const safelistKeys = [];

if (process.env.NODE_ENV === "development") {
  Object.keys(COLORS).map((colorKey) => {
    if (isObject(COLORS[colorKey])) {
      Object.keys(COLORS[colorKey]).map((color) => {
        safelistKeys.push(`bg-${colorKey}-${color}`);
      });
    }

    safelistKeys.push(`bg-${colorKey}`);
  });
}

module.exports = {
  mode: "jit",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx}",
    "./src/components/**/*.{js,ts,jsx,tsx}",
  ],
  safelist: [...safelistKeys, /^bg-/, /^text-/],
  theme: {
    container: {
      center: true,
      padding: "1rem",
    },
    extend: {
      fontFamily: {
        sans: ["Product Sans", "Helvetica", "Arial", "sans-serif"],
      },
      fontSize: {
        "s.m": "1.375rem",
      },
      colors: COLORS,
      dropShadow: {
        tag: "0px 8px 20px rgba(189, 201, 219, 0.4)",
      },
      boxShadow: {
        card: "0px 4px 20px rgba(189, 201, 219, 0.26)",
      },
      text: {
        "s.m": "1.375",
      },
    },
  },
  plugins: [],
};
