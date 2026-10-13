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
      title: connected
        ? "Mobile phone paused or disconnected"
        : "Connection lost",
      detail: `Last known stage: ${phoneTitles[s.phone] || s.phone}`,
    };
  if (s.completed_at && now - s.completed_at < 4)
    return {
      ...base,
      title: "Demo complete",
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
          : "Payment details remain private on the mobile phone",
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
