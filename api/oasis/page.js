const { normalizeLang, normalizeRoute, renderOasisHtml } = require("../../lib/oasis-vercel");

module.exports = async function handler(req, res) {
  const lang = normalizeLang(req.query.lang);
  const route = normalizeRoute(req.query.route);
  const html = renderOasisHtml(req, lang, route);
  res.statusCode = 200;
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.setHeader("Cache-Control", "public, max-age=0, must-revalidate");
  res.end(html);
};
