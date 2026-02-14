import js from "@eslint/js";
import globals from "globals";
import tseslint from "typescript-eslint";
import pluginReact from "eslint-plugin-react";

export default tseslint.config(
  {
    // Ignore build folders so they don't cause ghost errors
    ignores: ["dist", "node_modules"],
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["**/*.{ts,tsx}"],
    ...pluginReact.configs.flat.recommended,
    languageOptions: {
      globals: {
        ...globals.browser,
      },
      // This is the "magic" that makes unimported/undefined work in TS
      parserOptions: {
        project: ["./tsconfig.json", "./tsconfig.node.json"],
        tsconfigRootDir: import.meta.dirname,
      },
    },
    settings: {
      react: {
        version: "detect", // Fixes the React version warning
      },
    },
    rules: {
      "react/react-in-jsx-scope": "off",
      "no-undef": "error", // Catch those unimported/undefined variables
    },
  }
);