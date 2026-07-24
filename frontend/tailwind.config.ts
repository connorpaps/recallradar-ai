import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#18201d",
        field: "#f4f6f1",
        moss: "#476250",
        basil: "#2f7d59",
        signal: "#b42318",
        saffron: "#b86b00",
      },
      boxShadow: {
        soft: "0 18px 60px rgba(20, 31, 25, 0.08)",
      },
    },
  },
  plugins: [],
};

export default config;
