// Import the necessary testing utilities
import { afterEach, expect } from "vitest";
import { cleanup } from "@testing-library/react";
import * as matchers from "@testing-library/jest-dom/matchers";

// Extend Vitest's expect with jest-dom matchers
Object.entries(matchers).forEach(([matcherName, matcher]) => {
  if (typeof matcher === "function") {
    expect.extend({
      [matcherName]: matcher,
    });
  }
});

// Run cleanup after each test case
afterEach(() => {
  cleanup();
});
