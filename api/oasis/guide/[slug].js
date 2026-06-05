const { normalizeLang, normalizeGuideSlug, renderGuideHtml } = require("../../../lib/oasis-vercel");

module.exports = async function handler(req, res) {
  const lang = normalizeLang(req.query.lang);
  const slug = normalizeGuideSlug(req.query.slug);
  const html = renderGuideHtml(req, lang, slug);
  res.statusCode = 200;
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.setHeader("Cache-Control", "public, max-age=0, must-revalidate");
  res.end(html);
};
