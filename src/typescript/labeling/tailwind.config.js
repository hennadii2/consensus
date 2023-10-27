/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx}",
    "./src/components/**/*.{js,ts,jsx,tsx}",
  ],
  safelist: [
    "text-2xl",
    "text-3xl",
    {
      pattern:
        /bg-(red|green|blue|gray|orange|yellow|lime)-(100|200|300|400|500|600|700|800|900)/,
      variants: ["lg", "hover", "focus", "lg:hover"],
    },
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
