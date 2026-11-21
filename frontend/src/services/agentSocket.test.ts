import { describe, expect, it } from "vitest";
import { acceptEvent } from "./agentSocket";

describe("agent event cursor", () => {
  it("deduplicates repeated events", () => {
    expect(acceptEvent("e1", { id: "e1" }).accepted).toBe(false);
    expect(acceptEvent("e1", { id: "e2" })).toEqual({ accepted: true, cursor: "e2" });
  });
});
