const HARD_STOP_SEVERITIES = new Set(["P0"]);

export function reviewFindings(artifact) {
  return Array.isArray(artifact?.findings) ? artifact.findings : [];
}

export function hasHardStopFinding(artifact) {
  return reviewFindings(artifact).some((item) => HARD_STOP_SEVERITIES.has(String(item?.severity || "").toUpperCase()));
}

export function hasAskOnFinding(artifact, askOn = []) {
  const levels = new Set(askOn.map((item) => String(item).toUpperCase()));
  if (!levels.size) return false;
  return reviewFindings(artifact).some((item) => levels.has(String(item?.severity || "").toUpperCase()));
}

export function shouldInterruptForReview(artifact, options = {}) {
  if (hasHardStopFinding(artifact)) return { interrupt: true, reason_code: "planner_p0_finding" };
  if (options.strictInterrupt && hasAskOnFinding(artifact, options.askOn?.length ? options.askOn : ["P0", "P1"])) {
    return { interrupt: true, reason_code: "strict_interrupt_review_finding" };
  }
  return { interrupt: false, reason_code: "" };
}

export function recommendedRouteFromReview(artifact) {
  const route = String(artifact?.synthesis?.recommended_route || "continue_delivery").trim();
  return route || "continue_delivery";
}

export function applyLifecycleRoute(reviewArtifact) {
  const route = recommendedRouteFromReview(reviewArtifact);
  if (route === "terminal_aborted" || route === "user_decision_pending") {
    return { continueDelivery: false, route, reason_code: `recommended_route_${route}` };
  }
  return { continueDelivery: true, route, reason_code: "" };
}
