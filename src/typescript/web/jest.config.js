const nextJest = require("next/jest");

const createJestConfig = nextJest({
  dir: "./",
});

const customJestConfig = {
  moduleDirectories: ["node_modules", "<rootDir>/"],
  setupFiles: ["<rootDir>/jest.setup-env.js"],
  setupFilesAfterEnv: ["<rootDir>/jest.setup.js"],
  testEnvironment: "jest-environment-jsdom",
  moduleNameMapper: {
    "^components/(.*)$": "<rootDir>/src/components/$1",
    "^styles/(.*)$": "<rootDir>/src/styles/$1",
    "^hooks/(.*)$": "<rootDir>/src/hooks/$1",
    "^constants/(.*)$": "<rootDir>/src/constants/$1",
    "^enums/(.*)$": "<rootDir>/src/enums/$1",
    "^helpers/(.*)$": "<rootDir>/src/helpers/$1",
    "^store/(.*)$": "<rootDir>/src/store/$1",
    "#crypto": "@clerk/backend/dist/runtime/node/crypto.js",
    "#fetch": "@clerk/backend/dist/runtime/node/fetch.js",
    "#components": "@clerk/nextjs/dist/components.client.js",
    "#server": "@clerk/nextjs/dist/server-helpers.client.js",
  },
  testMatch: [
    "<rootDir>/src/hooks/**/*.test.tsx",
    "<rootDir>/src/helpers/*.test.ts",
    "<rootDir>/src/components/**/*.test.tsx",
    "<rootDir>/src/__tests__/*.test.tsx",
  ],
};

module.exports = createJestConfig(customJestConfig);
