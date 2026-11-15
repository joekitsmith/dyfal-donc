import vitest from "@vitest/eslint-plugin";
import nextVitals from "eslint-config-next/core-web-vitals";
import boundaries from "eslint-plugin-boundaries";
import perfectionist from "eslint-plugin-perfectionist";
import testingLibrary from "eslint-plugin-testing-library";
import { defineConfig, globalIgnores } from "eslint/config";
import tseslint from "typescript-eslint";

const SHARED_FOLDERS = ["api", "components", "config", "hooks", "theme", "types", "utils"];

export default defineConfig([
  globalIgnores([".next/**", "node_modules/**", "src/api/schema.d.ts", "next-env.d.ts"]),
  ...nextVitals,
  ...tseslint.configs.strictTypeChecked,
  ...tseslint.configs.stylisticTypeChecked,
  perfectionist.configs["recommended-natural"],
  {
    languageOptions: {
      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname },
    },
    rules: {
      "@typescript-eslint/consistent-type-definitions": ["error", "type"],
      "@typescript-eslint/restrict-template-expressions": ["error", { allowNumber: true }],
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: ["@/features/*/*"],
              message: "Import a feature through its index.ts, or relatively from inside it",
            },
          ],
        },
      ],
      "padding-line-between-statements": [
        "error",
        { blankLine: "always", next: "*", prev: ["for", "if", "while", "switch", "try"] },
      ],
      "perfectionist/sort-classes": "off",
      "perfectionist/sort-modules": "off",
    },
  },
  { files: ["**/*.mjs"], ...tseslint.configs.disableTypeChecked },
  {
    files: ["src/app/**/{page,layout}.tsx", "*.config.ts"],
    rules: { "import/no-default-export": "off" },
  },
  {
    plugins: { boundaries },
    rules: {
      "boundaries/dependencies": [
        "error",
        {
          default: "disallow",
          policies: [
            {
              allow: { to: { element: { types: ["app", "feature", "shared"] } } },
              from: { element: { type: "app" } },
            },
            {
              allow: { to: { element: { types: ["feature", "shared"] } } },
              from: { element: { type: "feature" } },
            },
            {
              allow: { to: { element: { type: "shared" } } },
              from: { element: { type: "shared" } },
            },
          ],
        },
      ],
    },
    settings: {
      "boundaries/elements": [
        { pattern: "src/app", type: "app" },
        { capture: ["name"], pattern: "src/features/*", type: "feature" },
        { pattern: `src/{${SHARED_FOLDERS.join(",")}}`, type: "shared" },
      ],
    },
  },
  {
    files: ["tests/**"],
    rules: { "no-restricted-imports": "off" },
  },
  {
    files: ["tests/**"],
    plugins: { "testing-library": testingLibrary, vitest },
    rules: { ...vitest.configs.recommended.rules, ...testingLibrary.configs["flat/react"].rules },
  },
]);
