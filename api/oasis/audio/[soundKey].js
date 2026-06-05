const { requireSupabase } = require("../../../lib/oasis-vercel");

const VALID_SOUNDS = new Set(["fire", "cat", "rain", "leaves"]);

module.exports = async function handler(req, res) {
  if (!requireSupabase(res)) return;
  const soundKey = String(req.query.soundKey || "").toLowerCase().replace(/[^a-z-]/g, "");
  if (!VALID_SOUNDS.has(soundKey)) {
    res.statusCode = 404;
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.end(JSON.stringify({ error: "audio not found" }));
    return;
  }
  const bucket = process.env.SUPABASE_AUDIO_BUCKET || "oasis-audio";
  const objectPath = `${soundKey}.wav`;
  const base = process.env.SUPABASE_URL.replace(/\/$/, "");
  const publicUrl = `${base}/storage/v1/object/public/${bucket}/${objectPath}`;
  res.statusCode = 302;
  res.setHeader("Location", publicUrl);
  res.setHeader("Cache-Control", "public, max-age=3600");
  res.end();
};
