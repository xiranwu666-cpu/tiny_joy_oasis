const { requireSupabase, supabaseRest } = require("../../../lib/oasis-vercel");

function groupCount(rows, key) {
  return rows.reduce((acc, row) => {
    const value = row[key] || "unknown";
    acc[value] = (acc[value] || 0) + 1;
    return acc;
  }, {});
}

function uniqueCount(rows, key) {
  return new Set(rows.map((row) => row[key]).filter(Boolean)).size;
}

module.exports = async function handler(req, res) {
  if (!requireSupabase(res)) return;
  const adminToken = process.env.ANALYTICS_ADMIN_TOKEN;
  const providedToken = String(req.query.token || "").trim();
  const bearerToken = String(req.headers.authorization || "").replace(/^Bearer\s+/i, "").trim();
  if (adminToken && providedToken !== adminToken && bearerToken !== adminToken) {
    res.statusCode = 401;
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.end(JSON.stringify({ error: "analytics token required" }));
    return;
  }
  const since = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();
  const response = await supabaseRest(
    `/oasis_pageviews?created_at=gte.${encodeURIComponent(since)}&select=lang,route,path,referrer,device_type,country,created_at&order=created_at.desc&limit=5000`
  );
  if (!response.ok) {
    res.statusCode = response.status;
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.end(JSON.stringify({ error: "Failed to fetch analytics." }));
    return;
  }
  const rows = await response.json();
  const payload = {
    window: "7d",
    pageviews: rows.length,
    uniquePaths: uniqueCount(rows, "path"),
    byLang: groupCount(rows, "lang"),
    byRoute: groupCount(rows, "route"),
    byDevice: groupCount(rows, "device_type"),
    byCountry: groupCount(rows, "country"),
    recent: rows.slice(0, 30)
  };
  res.statusCode = 200;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.end(JSON.stringify(payload));
};
