import { project, usableProfile, methodLabel, profileLabel, providerLabel, selectedProfile, graphIndex } from "./state.js";
const $ = (id) => document.getElementById(id);
let token = "",
  snapshot = null,
  selected = "",
  connected = false,
  replay = false,
  controller = null,
  generation = 0;
let lastPacket = 0,
  replayStart = 0,
  liveSelected = "",
  view = new URLSearchParams(location.search).get("view") || "compact";
const native = window.Scanpay;
let graphSignature = "", phaseSignature = "";
const svgNS = "http://www.w3.org/2000/svg";
function svgElement(tag, attributes = {}) {
  const element = document.createElementNS(svgNS, tag);
  for (const [key, value] of Object.entries(attributes)) element.setAttribute(key, value);
  return element;
}
// Original schematic illustrations, rendered as local vectors rather than external artwork.
function illustration(kind) {
  const icon = svgElement("svg", {viewBox: "0 0 80 80", "aria-hidden": "true", class: "component-art"});
  const part = (tag, attrs) => icon.append(svgElement(tag, attrs));
  if (kind === "phone") {
    part("rect", {x: 23, y: 6, width: 34, height: 66, rx: 8});
    part("path", {d: "M34 12h12 M35 65h10"});
    part("rect", {x: 29, y: 25, width: 22, height: 28, rx: 2, class: "paper"});
    part("path", {d: "M34 33h12 M34 39h12 M34 45h7", class: "scan-lines"});
    part("path", {d: "M27 36h26", class: "scan-beam"});
  } else if (kind === "server") {
    [12, 32, 52].forEach((y, i) => {
      part("rect", {x: 12, y, width: 56, height: 16, rx: 4});
      part("circle", {cx: 21, cy: y + 8, r: 2, class: `server-light light-${i}`});
      part("path", {d: `M33 ${y+8}h25`});
    });
  } else {
    part("rect", {x: 21, y: 21, width: 38, height: 38, rx: 8});
    [28, 40, 52].forEach(n => part("path", {d: `M${n} 11v10 M${n} 59v10 M11 ${n}h10 M59 ${n}h10`}));
    part("circle", {cx: 40, cy: 40, r: 10, class: "processor-core"});
    part("path", {d: "M35 40l4 4 7-9", class: "processor-check"});
  }
  return icon;
}
function graph(model) {
  const stages = model.session?.stages || [];
  const remote = stages.filter(s => s.execution === "external");
  const nodes = [
    ["Mobile phone", "Capture", "phone"], ["Backend", "Receive", "server"],
    ...(remote.length ? remote.map(s => [providerLabel(s.provider), s.method.replaceAll("_", " "), "processor"]) : [["Provider", "Read invoice", "processor"]]),
    ["Backend", stages.some(s => s.execution === "local") ? "Rules / validation" : "Validate", "server"],
    ["Mobile phone", "Review", "phone"],
  ];
  const signature = JSON.stringify(nodes);
  if (signature !== graphSignature) {
    graphSignature = signature;
    const canvas = svgElement("svg", {viewBox: "0 0 1000 510", class: "orbit", "data-count": nodes.length, role: "group", "aria-label": "Scan journey, clockwise from capture to review"});
    const defs = svgElement("defs");
    const marker = svgElement("marker", {id: "flow-arrow", viewBox: "0 0 10 10", refX: 8, refY: 5, markerWidth: 7, markerHeight: 7, orient: "auto-start-reverse"});
    marker.append(svgElement("path", {d: "M1 1L8 5L1 9", fill: "none", stroke: "#9bb0cb", "stroke-width": 1.6}));
    defs.append(marker); canvas.append(defs);
    const position = angle => [500 + 365 * Math.cos(angle), 225 + 145 * Math.sin(angle)];
    const angles = nodes.map((_, i) => (-150 + i * 360 / nodes.length) * Math.PI / 180);
    angles.slice(0, -1).forEach((angle, i) => {
      const start = position(angle + .18), end = position(angles[i+1] - .22);
      const path = svgElement("path", {d: `M${start} A365 145 0 0 1 ${end}`, class: "flow-link", "marker-end": "url(#flow-arrow)"});
      canvas.append(path);
    });
    const core = svgElement("foreignObject", {x: 340, y: 160, width: 320, height: 140});
    const center = document.createElement("div");center.className = "orbit-center";
    const dots = document.createElement("div");dots.className = "activity-dots";dots.setAttribute("aria-hidden", "true");
    for(let i=0;i<5;i++)dots.append(document.createElement("b"));
    const label = document.createElement("strong");label.id="orbit-label";
    const note = document.createElement("small");note.id="orbit-note";
    center.append(dots,label,note);core.append(center);canvas.append(core);
    nodes.forEach(([name, detail, kind], i) => {
      const [x,y] = position(angles[i]);
      const box = svgElement("foreignObject", {x: x-95, y: y-52, width: 190, height: 182});
      const node = document.createElement("div");node.className = "node";
      const art = document.createElement("div");art.className="art-wrap";art.append(illustration(kind));
      const badge = document.createElement("b");badge.className="node-number";badge.textContent=String(i+1).padStart(2,"0");art.append(badge);
      const label = document.createElement("span");label.textContent=name;
      const sub = document.createElement("small");sub.textContent=detail;
      node.append(art,label,sub);box.append(node);canvas.append(box);
    });
    $("graph").replaceChildren(canvas);
  }
  const index = graphIndex(model,remote);
  document.querySelectorAll(".node").forEach((n,i) => {
    n.classList.toggle("active", i===index);
    n.classList.toggle("passed", index>=0 && i<index);
    n.classList.toggle("celebrate", Boolean(model.complete && i===index));
  });
  const waiting = model.moving && model.session?.backend === "request";
  document.querySelectorAll(".flow-link").forEach((n,i) => {
    n.classList.toggle("passed", index>i);
    n.classList.toggle("transferring", model.moving && !waiting && i===index-1);
  });
  $("orbit-label").textContent = model.complete ? "Complete" : waiting ? "Awaiting provider" : model.moving ? "In transit" : model.node===4 ? "Your review" : model.idle ? "Ready" : "Live journey";
  $("orbit-note").textContent = waiting ? "Awaiting response" : model.complete ? "No payment made" : "Capture → draft → review";
  const phase = `${selected}:${model.session?.journey_id}:${model.node}:${model.title}`;
  if (phase !== phaseSignature) {
    phaseSignature = phase;
    $("title").getAnimations().forEach(a=>a.cancel());
    if (!matchMedia("(prefers-reduced-motion: reduce)").matches)
      $("title").animate([{opacity:.35,transform:"translateY(8px)"},{opacity:1,transform:"translateY(0)"}],{duration:360,easing:"ease-out"});
  }
}
function setView(v) {
  view = ["compact", "technical", "customer"].includes(v) ? v : "compact";
  document.body.dataset.view = view;
  $("view").value = view;
}
setView(view);
function receive(data) {
  if (data.version !== 1 || !Array.isArray(data.sessions))
    throw Error("Unsupported demo channel");
  snapshot = data;
  connected = true;
  lastPacket = performance.now();
  $("error").textContent = "";
  const previous = selected;
  $("sessions").replaceChildren(
    new Option("Select a mobile phone", ""),
    ...data.sessions.map(
      (s) =>
        new Option(
          `Mobile phone ${s.session_id.slice(0, 8)} · ${s.phone}`,
          s.session_id,
        ),
    ),
  );
  $("sessions").value = previous;
  render();
}
function render() {
  // Use server time plus monotonic elapsed time, not the SUNMI wall clock.
  const now = Number.isFinite(snapshot?.server_time)
      ? snapshot.server_time + (performance.now() - lastPacket) / 1000
      : Date.now() / 1000,
    liveConnected = connected && performance.now() - lastPacket < 15000;
  const model = project(snapshot, selected, now, replay || liveConnected);
  $("connection").textContent = replay
    ? "SYNTHETIC REPLAY"
    : !liveConnected
      ? "BACKEND DISCONNECTED"
      : model.session &&
          now - model.session.last_seen < 30 &&
          model.session.phone !== "paused"
        ? "LIVE · MOBILE CONNECTED"
        : "WAITING FOR MOBILE PHONE";
  $("mode-label").textContent = replay
    ? "SYNTHETIC REPLAY · NO REQUESTS"
    : view === "customer"
      ? "YOUR SCAN"
      : "LIVE SYSTEM JOURNEY";
  const qr = model.idle && view !== "technical";
  $("idle").hidden = !qr;
  $("journey").hidden = qr;
  $("idle-note").textContent = model.detail;
  $("title").textContent = model.title;
  $("detail").textContent = model.detail;
  document.body.classList.toggle(
    "moving",
    model.moving && (replay || liveConnected),
  );
  document.body.dataset.phase = model.complete ? "complete" : model.session?.phone || "waiting";
  graph(model);
  $("stages").replaceChildren(
    ...(model.session?.stages || []).map((s) => {
      const el = document.createElement("span");
      el.textContent = `${s.execution === "local" ? "Backend" : s.provider || "Provider"} · ${s.model || s.method} · ${s.state}`;
      return el;
    }),
  );
  $("summary").hidden = !(
    view === "customer" &&
    ["review", "confirmation"].includes(model.session?.phone)
  );
  const request = [...(model.session?.events || [])]
    .reverse()
    .find((e) => e.kind === "request");
  $("timing").textContent =
    model.moving && model.session?.backend === "request" && request
      ? `${Math.max(0, Math.floor(now - request.server_time))}s since the latest provider request`
      : "";
  $("clock").textContent = new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
  $("footer-note").textContent = replay
    ? "Synthetic replay · No extraction or payment requests."
    : "Payment details stay on the mobile phone.";
}
let providerData = null, providerBusy = false, providerEpoch = 0;
function updateProviderChoice() {
  const p = providerData?.profiles.find(p => p.id === $("next-profile").value);
  const current = selectedProfile(providerData);
  const same = p && current && p.id===current.id && p.version===current.version;
  $("apply-provider").disabled = providerBusy || replay || !token || !usableProfile(p) || same;
  $("apply-provider").textContent = providerBusy ? "Please wait…" : same ? "Selected" : "Use for next scan";
  $("next-method").disabled = providerBusy || replay || !providerData;
  $("next-profile").disabled = providerBusy || replay || !providerData;
  $("refresh-providers").disabled = providerBusy || replay || !token;
}
function populateProviderChoices(preferred) {
  const choices = (providerData?.profiles || []).filter(p => usableProfile(p) && p.method === $("next-method").value);
  $("next-profile").replaceChildren(...choices.map(p => new Option(profileLabel(p) || p.id, p.id)));
  if(choices.some(p=>p.id===preferred))$("next-profile").value=preferred;
  updateProviderChoice();
}
async function providerRequest(path, options={}) {
  const abort = new AbortController(), timeout = setTimeout(()=>abort.abort(),6000);
  try {
    const r = await fetch(path,{...options,headers:{Authorization:`Bearer ${token}`,"Content-Type":"application/json"},cache:"no-store",redirect:"error",signal:abort.signal});
    if(!r.ok)throw Error(r.status===401?"Reconnect with a valid access token.":r.status===409?"The profile changed. Refresh and choose it again.":"Provider settings unavailable. Refresh to try again.");
    return await r.json();
  } finally {clearTimeout(timeout);}
}
async function loadProviders() {
  if(providerBusy)return;
  if(!token || replay){updateProviderChoice();return;}
  providerBusy=true;const epoch=++providerEpoch;updateProviderChoice();
  $("provider-message").textContent="";
  try {
    const data=await providerRequest("/v1/profiles");
    if(epoch!==providerEpoch)return;
    providerData=data;const current=selectedProfile(data);
    $("current-provider").textContent=current?`Current: ${profileLabel(current) || current.id}`:"Current selection is unavailable.";
    const methods=[...new Set(data.profiles.filter(usableProfile).map(p=>p.method))];
    $("next-method").replaceChildren(...methods.map(m=>new Option(methodLabel(m),m)));
    if(current && methods.includes(current.method))$("next-method").value=current.method;
    populateProviderChoices(current?.id);
    if(!methods.length)$("provider-message").textContent="No configured providers on this backend. The isolated rehearsal has no providers.";
  } catch(error){providerData=null;$("current-provider").textContent="Could not load current provider.";$("provider-message").textContent=error.message;}
  finally{providerBusy=false;updateProviderChoice();}
}
$("next-method").onchange=()=>populateProviderChoices();
$("next-profile").onchange=updateProviderChoice;
$("refresh-providers").onclick=loadProviders;
$("apply-provider").onclick=async()=>{
  const p=providerData?.profiles.find(p=>p.id===$("next-profile").value);
  if(providerBusy||replay||!usableProfile(p))return;
  providerBusy=true;updateProviderChoice();$("provider-message").textContent="Saving…";
  try {
    const saved=await providerRequest("/v1/admin/selection",{method:"PUT",body:JSON.stringify({id:p.id,version:p.version})});
    providerData.default_extract_profile_id=saved.id;providerData.default_extract_profile_version=saved.version;
    $("current-provider").textContent=`Current: ${profileLabel(p)||p.id}`;
    $("provider-message").textContent="Saved for the next new scan. Existing scans keep their provider.";
  } catch(error){$("provider-message").textContent=error.message;}
  finally{providerBusy=false;updateProviderChoice();}
};
async function connectionLoop(id) {
  while (id === generation && !replay) {
    const streamController = new AbortController();
    controller = streamController;
    let watchdog = setTimeout(() => streamController.abort(), 14000);
    try {
      const response = await fetch("/v1/demo/events", {
        headers: { Authorization: `Bearer ${token}` },
        signal: streamController.signal,
        cache: "no-store",
        redirect: "error",
      });
      if (!response.ok)
        throw Error(
          response.status === 401
            ? "Access token rejected"
            : "Demo channel unavailable",
        );
      if (!response.body?.getReader) throw Error("Streaming unavailable");
      const reader = response.body.getReader(),
        decoder = new TextDecoder();
      let buffer = "";
      while (id === generation) {
        const { value, done } = await reader.read();
        if (done) break;
        clearTimeout(watchdog);
        watchdog = setTimeout(() => streamController.abort(), 14000);
        buffer += decoder.decode(value, { stream: true });
        if (buffer.length > 1000000) throw Error("Unexpected stream size");
        let end;
        while ((end = buffer.indexOf("\n\n")) >= 0) {
          const block = buffer.slice(0, end);
          buffer = buffer.slice(end + 2);
          const data = block.split("\n").find((l) => l.startsWith("data: "));
          if (data && id === generation) receive(JSON.parse(data.slice(6)));
        }
      }
    } catch (error) {
      if (id === generation) {
        connected = false;
        $("error").textContent = error.message;
      }
    } finally {
      clearTimeout(watchdog);
      streamController.abort();
    }
    // Repeated authenticated snapshots also support WebViews without fetch streaming.
    for (let n = 0; n < 10 && id === generation && !replay; n++) {
      const pollController = new AbortController();
      controller = pollController;
      const timeout = setTimeout(() => pollController.abort(), 3000);
      try {
        const r = await fetch("/v1/demo/snapshot", {
          headers: { Authorization: `Bearer ${token}` },
          cache: "no-store",
          redirect: "error",
          signal: pollController.signal,
        });
        if (!r.ok) throw Error("Could not read demo state");
        const data = await r.json();
        if (id === generation) receive(data);
      } catch {
        if (id === generation) connected = false;
      } finally {
        clearTimeout(timeout);
      }
      await new Promise((resolve) => setTimeout(resolve, 500));
    }
  }
}
function startLive() {
  if (replay) selected = liveSelected;
  replay = false;
  generation++;
  controller?.abort();
  connected = false;
  snapshot = null;
  render();
  loadProviders();
  if (token) connectionLoop(generation);
  else $("controls").showModal();
}
$("settings").onclick = () => { $("controls").showModal(); loadProviders(); };
$("close").onclick = () => $("controls").close();
$("login").onsubmit = (e) => {
  e.preventDefault();
  token = $("token").value;
  $("token").value = "";
  $("error").textContent = "";
  startLive();
};
$("sessions").onchange = () => {
  selected = $("sessions").value;
  render();
};
$("view").onchange = () => setView($("view").value);
$("clear").onclick = () => {
  selected = "";
  $("sessions").value = "";
  if (native) native.follow("");
  render();
};
$("live").onclick = startLive;
$("replay").onclick = () => {
  generation++;
  controller?.abort();
  if (!replay) liveSelected = selected;
  replay = true;
  updateProviderChoice();
  replayStart = Date.now();
  $("controls").close();
};
const replaySteps = [
  ["crop", "none"],
  ["preview", "none"],
  ["uploading", "none"],
  ["queued", "queued"],
  ["reading", "request"],
  ["reading", "response"],
  ["reading", "validation"],
  ["review", "completed"],
  ["confirmation", "completed"],
  ["idle", "completed"],
  ["idle", "none"],
];
setInterval(() => {
  if (replay) {
    const index = Math.min(
      replaySteps.length - 1,
      Math.floor((Date.now() - replayStart) / 3500),
    );
    const [phone, backend] = replaySteps[index];
    selected = "synthetic";
    const now = Date.now() / 1000;
    receive({
      version: 1,
      revision: index,
      sessions: [
        {
          session_id: selected,
          phone,
          backend,
          last_seen: now,
          completed_at: index === 9 ? replayStart / 1000 + 31.5 : null,
          stages:
            index >= 4
              ? [
                  {
                    provider: "Example AI",
                    method: "vision",
                    model: "Synthetic model",
                    state: backend,
                    execution: "external",
                  },
                ]
              : [],
          events: [{ kind: "request", server_time: replayStart / 1000 + 14 }],
        },
      ],
    });
  }
  render();
}, 250);
if (native) {
  try {
    const config = JSON.parse(native.configuration());
    token = config.token;
    $("token-label").hidden = true;
    $("connect").hidden = true;
    $("native-controls").hidden = false;
    if (config.session) {
      selected = config.session;
    }
    $("sessions").addEventListener("change", () => native.follow(selected));
    $("vision").onclick = () => native.mode("vision");
    $("scanpay").onclick = () => native.mode("scanpay");
    $("configure").onclick = () => native.settings();
  } catch {
    $("error").textContent = "Open native connection settings.";
  }
}
startLive();
