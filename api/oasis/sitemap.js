const { GUIDE_SLUGS, LANGS, ROUTES, originFor, publicRouteFor } = require("../../lib/oasis-vercel");

module.exports = async function handler(req, res) {
  const origin = originFor(req);
  const urls = [];
  for (const lang of Object.keys(LANGS)) {
    for (const route of Array.from(ROUTES).sort()) {
      urls.push({ loc: `${origin}/oasis/${lang}/${publicRouteFor(route)}`, priority: "0.8" });
    }
    for (const slug of GUIDE_SLUGS) {
      urls.push({ loc: `${origin}/oasis/${lang}/guide/${slug}`, priority: "0.7" });
    }
  }
  const body = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ...urls.map((url) => `  <url><loc>${url.loc}</loc><changefreq>weekly</changefreq><priority>${url.priority}</priority></url>`),
    "</urlset>",
    ""
  ].join("\n");
  res.statusCode = 200;
  res.setHeader("Content-Type", "application/xml; charset=utf-8");
  res.setHeader("Cache-Control", "public, max-age=0, s-maxage=86400, stale-while-revalidate=3600");
  res.end(body);
};
