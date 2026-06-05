const { normalizeLang, readJson, requireSupabase, supabaseRest } = require("../../lib/oasis-vercel");

function sendJson(res, status, payload) {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.end(JSON.stringify(payload));
}

module.exports = async function handler(req, res) {
  if (!requireSupabase(res)) return;
  const method = req.method || "GET";
  if (method === "GET") {
    const lang = normalizeLang(req.query.lang);
    const response = await supabaseRest(
      `/oasis_joy_entries?lang=eq.${encodeURIComponent(lang)}&select=id,text,created_at&order=created_at.desc&limit=100`
    );
    if (!response.ok) {
      return sendJson(res, response.status, { error: "Failed to fetch joy entries." });
    }
    const rows = await response.json();
    if (!rows.length) {
      const fallback = {
        en: "The kettle clicked off right as the rain got softer.",
        zh: "水壶刚好在雨声变轻的时候响了一下。",
        tc: "水壺剛好在雨聲變輕的時候響了一下。"
      };
      return sendJson(res, 200, { id: null, text: fallback[lang], source: "OASIS seed" });
    }
    const row = rows[Math.floor(Math.random() * rows.length)];
    return sendJson(res, 200, { id: row.id, text: row.text, source: "anonymous", createdAt: row.created_at });
  }

  if (method === "POST") {
    const body = await readJson(req);
    const lang = normalizeLang(body.lang);
    const text = String(body.text || "").replace(/\s+/g, " ").trim();
    if (text.length < 3 || text.length > 220) {
      return sendJson(res, 400, { error: "text must be 3-220 characters" });
    }
    const response = await supabaseRest("/oasis_joy_entries", {
      method: "POST",
      headers: { Prefer: "return=representation" },
      body: JSON.stringify([{ lang, text }])
    });
    if (!response.ok) {
      return sendJson(res, response.status, { error: "Failed to save joy entry." });
    }
    const rows = await response.json();
    return sendJson(res, 200, { ok: true, id: rows[0]?.id, createdAt: rows[0]?.created_at });
  }

  res.setHeader("Allow", "GET, POST");
  return sendJson(res, 405, { error: "method not allowed" });
};
