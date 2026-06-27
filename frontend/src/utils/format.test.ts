import { describe, expect, it } from "vitest";

import {
  complexityBand,
  formatNumber,
  languageColor,
  languageLabel,
} from "@/utils/format";

describe("format helpers", () => {
  it("returns distinct colours per language and a fallback", () => {
    expect(languageColor("python")).not.toEqual(languageColor("javascript"));
    expect(languageColor("does-not-exist")).toEqual(languageColor("unknown"));
  });

  it("labels languages nicely", () => {
    expect(languageLabel("cpp")).toBe("C++");
    expect(languageLabel("typescript")).toBe("TypeScript");
    expect(languageLabel("rust")).toBe("rust");
  });

  it("formats numbers with separators", () => {
    expect(formatNumber(1234567)).toMatch(/1.234.567|1,234,567/);
  });

  it("bands complexity scores", () => {
    expect(complexityBand(3).label).toBe("Low");
    expect(complexityBand(8).label).toBe("Moderate");
    expect(complexityBand(15).label).toBe("High");
    expect(complexityBand(50).label).toBe("Very High");
  });
});
