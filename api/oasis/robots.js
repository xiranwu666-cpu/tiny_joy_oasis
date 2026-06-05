const { originFor } = require("../../lib/oasis-vercel");

module.exports = async function handler(req, res) {
  const origin = originFor(req);
  res.statusCode = 200;
  res.setHeader("Content-Type", "text/plain; charset=utf-8");
  res.end([
    "User-agent: *",
    "Allow: /",
    "Disallow: /api/",
    "Disallow: /admin/",
    "Disallow: /scripts/",
    "Disallow: /supabase/",
    `Sitemap: ${origin}/oasis/sitemap.xml`,
    ""
  ].join("\n"));
};
