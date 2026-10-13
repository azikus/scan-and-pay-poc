import test from "node:test";
import assert from "node:assert/strict";
import { project, usableProfile, selectedProfile, graphIndex, profileLabel, scanInsights } from "./state.js";
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

test("provider choice requires ready profiles and the exact saved version", () => {
  const p={id:"openai",version:"v2",enabled:true,configured:true,implemented:true,provider:"OpenAI",model:"Mini"};
  assert.equal(usableProfile(p),true);
  for(const flag of ["enabled","configured","implemented"])assert.equal(usableProfile({...p,[flag]:false}),false);
  assert.equal(selectedProfile({profiles:[p],default_extract_profile_id:p.id,default_extract_profile_version:"v1"}),undefined);
  assert.equal(selectedProfile({profiles:[p],default_extract_profile_id:p.id,default_extract_profile_version:"v2"}),p);
  assert.match(profileLabel({...p,component_ids:["invoice-context@1"]}),/Invoice context/);
});
test("hybrid motion follows the active remote stage instead of skipping OCR", () => {
  const remote=[{state:"request"},{state:"queued"}];
  assert.equal(graphIndex({node:2},remote),2);
  remote[0].state="completed";remote[1].state="request";
  assert.equal(graphIndex({node:2},remote),3);
  assert.equal(graphIndex({node:3},remote),4);
  assert.equal(graphIndex({node:4},remote),5);
  assert.equal(graphIndex({node:-1},remote),-1);
});

test("scan insights filter old journeys, coalesce heartbeats, and freeze terminal timings", () => {
  const event = (kind, time, extra={}) => ({kind, source:"backend", server_time:time, journey_id:"current", ...extra});
  const session = {journey_id:"current", updated_at:115, events:[
    event("accepted", 20, {journey_id:"previous"}), event("accepted",100),
    event("request",102,{stage_id:"ocr"}), event("completed",105,{stage_id:"ocr"}),
    event("request",106,{stage_id:"llm"}), event("completed",112),
    event("review",113,{source:"phone"}),event("review",114,{source:"phone"}),
  ]};
  const data=scanInsights(session,120);
  assert.equal(data.elapsed,12);
  assert.equal(data.finished,true);
  assert.equal(data.activity.filter(e=>e.kind==="review").length,1);
  assert.equal(data.activity.some(e=>e.journey_id==="previous"),false);
  assert.equal(scanInsights({...session, events:session.events.slice(0,5)},120,false).elapsed,15);
  assert.equal(scanInsights(null,120).elapsed,null);
});
