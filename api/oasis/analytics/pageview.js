const { normalizeLang, normalizeRoute, readJson, requireSupabase, supabaseRest } = require("../../../lib/oasis-vercel");

function deviceType(userAgent) {
  const ua = String(userAgent || "").toLowerCase();
  if (/ipad|tablet/.test(ua)) return "tablet";
  if (/mobile|iphone|android/.test(ua)) return "mobile";
  return "desktop";
}

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.statusCode = 405;
    res.setHeader("Allow", "POST");
    res.end(JSON.stringify({ error: "method not allowed" }));
    return;
  }
  if (!requireSupabase(res)) return;
  const body = await readJson(req).catch(() => ({}));
  const userAgent = req.headers["user-agent"] || "";
  const row = {
    lang: normalizeLang(body.lang),
    route: normalizeRoute(body.route),
    path: String(body.path || req.headers.referer || "/").slice(0, 500),
    referrer: String(body.referrer || "").slice(0, 500),
    user_agent: String(userAgent).slice(0, 500),
    device_type: deviceType(userAgent),
    country: String(req.headers["x-vercel-ip-country"] || "").slice(0, 8)
  };
  const response = await supabaseRest("/oasis_pageviews", {
    method: "POST",
    headers: { Prefer: "return=minimal" },
    body: JSON.stringify([row])
  });
  res.statusCode = response.ok ? 204 : response.status;
  res.end(response.ok ? "" : JSON.stringify({ error: "Failed to record pageview." }));
};
