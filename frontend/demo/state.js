// Pure projection shared by all three views. No invoice fields enter this channel.
export const phoneTitles = {
  idle: "Ready for the next scan",
  crop: "Adjusting crop",
  preview: "Ready to send",
  preparing: "Preparing image",
  uploading: "Sending invoice",
  queued: "Invoice received",
  reading: "Reading invoice",
  review: "Reviewing on the mobile phone",
  confirmation: "Checking confirmation",
  recovery: "Waiting for recovery on the mobile phone",
  failed: "Could not prepare a draft",
  paused: "Mobile phone paused",
};
export function project(
  snapshot,
  sessionID,
  now = Date.now() / 1000,
  connected = true,
) {
  const s = snapshot?.sessions.find((s) => s.session_id === sessionID);
  if (!s)
    return {
      title: "Waiting for mobile phone",
      node: -1,
      moving: false,
      idle: false,
      detail:
        "Enable Demo displays in the mobile app, then select its session.",
    };
  const base = {
    session: s,
    node: 0,
    moving: false,
    idle: false,
    detail: "",
    title: phoneTitles[s.phone] || "Waiting for mobile phone",
  };
  if (!connected || now - s.last_seen > 30 || s.phone === "paused")
    return {
      ...base,
      node: -1,
      title: connected
        ? "Mobile phone paused or disconnected"
        : "Connection lost",
      detail: `Last known stage: ${phoneTitles[s.phone] || s.phone}`,
    };
  if (s.completed_at && now - s.completed_at < 4)
    return {
      ...base,
      title: "Scan complete",
      node: 4,
      detail: "No payment made",
      complete: true,
    };
  if (s.phone === "idle")
    return {
      ...base,
      idle: true,
      node: -1,
      detail: [
        "queued",
        "running",
        "request",
        "response",
        "validation",
        "local",
      ].includes(s.backend)
        ? "Previous scan is still running on the backend."
        : "",
    };
  if (["failed", "interrupted"].includes(s.backend) || s.outcome === "error")
    return {
      ...base,
      node: 1,
      title:
        s.backend === "interrupted"
          ? "Processing interrupted"
          : "Could not prepare a draft",
      detail: "Continue on the mobile phone. No automatic retry.",
    };
  if (["review", "confirmation", "recovery", "failed"].includes(s.phone))
    return {
      ...base,
      node: 4,
      detail:
        s.outcome === "incomplete"
          ? "Some details need your review"
          : "",
    };
  if (s.backend === "request")
    return {
      ...base,
      node: 2,
      moving: true,
      title: "Waiting for provider response",
      detail: "Remote processing progress is not observable",
    };
  if (s.backend === "response")
    return {
      ...base,
      node: 3,
      moving: true,
      title: "Provider response received",
      detail: "A response is not yet a validated draft",
    };
  if (["validation", "local"].includes(s.backend))
    return {
      ...base,
      node: 3,
      moving: true,
      title: "Checking extracted fields",
      detail: "Local processing on the backend",
    };
  if (["completed", "partially_completed"].includes(s.backend))
    return {
      ...base,
      node: 4,
      title: "Draft ready on the backend",
      detail: "Waiting for the mobile phone to open review",
    };
  if (["queued", "running"].includes(s.backend))
    return {
      ...base,
      node: 1,
      moving: s.backend === "running",
      title:
        s.backend === "queued"
          ? "Waiting in the backend queue"
          : "Preparing provider request",
    };
  return {
    ...base,
    node: s.phone === "uploading" ? 1 : 0,
    moving: s.phone === "uploading",
  };
}

// Exact version is retained when choosing a provider; unavailable profiles never appear.
export const usableProfile = (p) => Boolean(p?.implemented && p.enabled && p.configured);
export const providerLabel = (provider) => ({openai:"OpenAI",gemini:"Google",mistral:"Mistral",anthropic:"Anthropic",together:"Together",xai:"xAI",aws:"AWS",azure:"Azure",google:"Google"}[provider] || provider || "Provider");
export const methodLabel = (method) => ({
  direct_vision: "Image → LLM",
  prebuilt_document_mapping: "Image → document extraction",
  custom_document_mapping: "Image → custom document extraction",
  document_annotations: "Image → OCR with annotations",
  direct_image_llm: "Image → AI",
  managed_ocr_rules: "OCR → rules",
  managed_ocr_llm: "OCR → AI",
}[method] || method.replaceAll("_", " "));
export const profileLabel = (p) => [p.provider ? providerLabel(p.provider) : null, p.processor, p.model].filter(Boolean).join(" · ") +
  (p.component_ids?.includes("invoice-context@1") ? " · Invoice context" : "");
export function selectedProfile(data) {
  return data?.profiles.find(p => p.id === data.default_extract_profile_id && p.version === data.default_extract_profile_version);
}
export function graphIndex(model, remote) {
  if (model.node === 2) {
    const active = remote.findIndex(s => ["request", "running"].includes(s.state));
    return 2 + (active >= 0 ? active : Math.max(0, remote.length - 1));
  }
  return model.node >= 3 ? model.node + Math.max(0, remote.length - 1) : model.node;
}

// Timings use observed backend timestamps only, never estimates or payment fields.
const eventLabels = {
  crop: "Image captured", preview: "Image ready", preparing: "Preparing upload",
  uploading: "Sending image", accepted: "Backend received image", queued: "Queued",
  running: "Processing started", request: "Request sent to provider",
  response: "Provider response received", validation: "Checking fields", local: "Applying rules",
  completed: "Draft prepared", partially_completed: "Draft needs review",
  review: "Review opened", confirmation: "Confirmation opened", confirmed: "Confirmation saved",
  failed: "Processing failed", interrupted: "Processing interrupted", recovery: "Recovery needed",
};
export function scanInsights(session, now, active = true) {
  const events = (session?.events || []).filter(e => e.journey_id === session.journey_id);
  const activity = [];
  for (const e of events) {
    if (!eventLabels[e.kind]) continue;
    const last = activity.at(-1);
    if (last?.kind === e.kind && last.source === e.source && last.stage_id === e.stage_id) continue;
    activity.push({...e, label: eventLabels[e.kind]});
  }
  const start = events.find(e => e.source === "backend" && e.kind === "accepted");
  const end = events.find(e => e.source === "backend" && ["completed", "partially_completed", "failed", "interrupted"].includes(e.kind) && !e.stage_id);
  const current = active ? now : Math.min(now, session?.updated_at ?? session?.last_seen ?? now);
  const elapsed = start ? Math.max(0, (end?.server_time ?? current) - start.server_time) : null;
  return {activity: activity.slice(-4).reverse(), elapsed, finished: Boolean(end), paused: !active && !end};
}
