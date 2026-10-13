import { project } from "./state.js";
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
let graphSignature = "";
function graph(model) {
  const stages = model.session?.stages || [];
  const remote = stages.filter((s) => s.execution === "external");
  const nodes = [
    ["Mobile phone", "Capture"],
    ["Backend", "Receive"],
    ...(remote.length
      ? remote.map((s) => [s.provider || "Provider", s.method])
      : [["Provider", "Awaiting dispatch"]]),
    [
      "Backend",
      stages.some((s) => s.execution === "local")
        ? "Local rules / check"
        : "Check",
    ],
    ["Mobile phone", "Review"],
  ];
  const signature = JSON.stringify(nodes);
  if (signature !== graphSignature) {
    graphSignature = signature;
    const elements = [];
    nodes.forEach(([name, detail], i) => {
      if (i) elements.push(document.createElement("i"));
      const node = document.createElement("div");
      node.className = "node";
      node.append(document.createTextNode(String(i + 1).padStart(2, "0")));
      const label = document.createElement("span");
      label.textContent = name;
      const sub = document.createElement("small");
      sub.textContent = detail;
      node.append(label, sub);
      elements.push(node);
    });
    $("graph").replaceChildren(...elements);
  }
  const index =
    model.node === 2
      ? nodes.length - 3
      : model.node === 3
        ? nodes.length - 2
        : model.node === 4
          ? nodes.length - 1
          : model.node;
  document
    .querySelectorAll(".node")
    .forEach((n, i) => n.classList.toggle("active", i === index));
  document
    .querySelectorAll("#graph i")
    .forEach((n, i) => n.classList.toggle("active", i === index - 1));
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
  if (token) connectionLoop(generation);
  else $("controls").showModal();
}
$("settings").onclick = () => $("controls").showModal();
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
  liveSelected = selected;
  replay = true;
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
