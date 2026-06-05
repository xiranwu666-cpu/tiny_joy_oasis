const { LANGS, ROUTES, originFor } = require("../../lib/oasis-vercel");

module.exports = async function handler(req, res) {
  const origin = originFor(req);
  const urls = [];
  for (const lang of Object.keys(LANGS)) {
    for (const route of Array.from(ROUTES).sort()) {
      urls.push(`${origin}/oasis/${lang}/${route}`);
    }
  }
  const body = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ...urls.map((url) => `  <url><loc>${url}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>`),
    "</urlset>",
    ""
  ].join("\n");
  res.statusCode = 200;
  res.setHeader("Content-Type", "application/xml; charset=utf-8");
  res.end(body);
};
