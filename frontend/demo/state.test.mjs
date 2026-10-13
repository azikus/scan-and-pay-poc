import test from "node:test";
import assert from "node:assert/strict";
import { project } from "./state.js";
const state = {
  session_id: "a",
  phone: "reading",
  last_seen: 100,
  backend: "request",
  events: [],
};
const show = (overrides = {}, now = 100, connected = true) =>
  project({ sessions: [{ ...state, ...overrides }] }, "a", now, connected);
test("idle QR requires a current connected idle phone", () => {
  assert.equal(show({ phone: "idle" }).idle, true);
  assert.equal(show({ phone: "idle" }, 140).idle, false);
  assert.equal(show({ phone: "idle" }, 100, false).idle, false);
  assert.equal(project(null, "a").idle, false);
});
test("response is not success and errors do not celebrate", () => {
  assert.equal(show({ backend: "response" }).complete, undefined);
  assert.match(show({ backend: "failed" }).title, /Could not/);
  assert.match(
    show({ backend: "completed", outcome: "error" }).title,
    /Could not/,
  );
  assert.equal(show({ backend: "interrupted" }).moving, false);
});
test("completion is bounded and backend activity survives phone reset", () => {
  assert.equal(show({ phone: "idle", completed_at: 99 }).complete, true);
  assert.equal(show({ phone: "idle", completed_at: 90 }).idle, true);
  assert.match(show({ phone: "idle" }).detail, /still running/);
});
test("late backend states do not move a reviewing phone backwards", () => {
  assert.equal(show({ phone: "review" }).node, 4);
  assert.equal(show({ phone: "confirmation" }).node, 4);
  assert.equal(show().node, 2);
  assert.equal(show({}, 140).moving, false);
});
