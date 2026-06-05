const fs = require("fs");
const path = require("path");

const LANGS = { en: "en", zh: "zh-CN", tc: "zh-Hant" };
const ROUTES = new Set(["today", "sound", "vent", "joy"]);

const META = {
  en: {
    today: ["Today's Hug - Digital hugs and kind words | OASIS", "Get a gentle micro-moment with warm daily quotes, kind words, and a cozy web corner for stress relief."],
    sound: ["Sound Oasis - White noise breathing room | OASIS", "Relax with woodfire, cat purr, rain, autumn leaves, and a soft 4-7-8 breathing guide."],
    vent: ["Cyber Vent - Private worry release | OASIS", "Type worries and release them privately. Nothing is saved. A gentle client-side anxiety relief ritual."],
    joy: ["Joy Swapper - Anonymous happy moments | OASIS", "Share a tiny happy moment anonymously and receive a stranger's joy in return."]
  },
  zh: {
    today: ["今日拥抱 - 温柔句子和数字拥抱 | OASIS", "获得一句温柔话，一个适合放松心情、缓解焦虑、让自己轻一点的小瞬间。"],
    sound: ["声音绿洲 - 白噪音与呼吸引导 | OASIS", "木火、猫咪呼噜、雨声、秋叶，以及柔和的 4-7-8 呼吸练习。"],
    vent: ["赛博解压池 - 不保存的私人释放 | OASIS", "写下烦恼并释放，内容不会保存，适合短暂情绪整理和压力缓解。"],
    joy: ["快乐交换商店 - 匿名交换小开心 | OASIS", "匿名提交一个小小开心，收到陌生人的快乐瞬间。"]
  },
  tc: {
    today: ["今日擁抱 - 溫柔句子和數位擁抱 | OASIS", "獲得一句溫柔話，一個適合放鬆心情、緩解焦慮、讓自己輕一點的小瞬間。"],
    sound: ["聲音綠洲 - 白噪音與呼吸引導 | OASIS", "木火、貓咪呼嚕、雨聲、秋葉，以及柔和的 4-7-8 呼吸練習。"],
    vent: ["賽博解壓池 - 不保存的私人釋放 | OASIS", "寫下煩惱並釋放，內容不會保存，適合短暫情緒整理和壓力緩解。"],
    joy: ["快樂交換商店 - 匿名交換小開心 | OASIS", "匿名提交一個小小開心，收到陌生人的快樂瞬間。"]
  }
};

function normalizeLang(value) {
  return Object.prototype.hasOwnProperty.call(LANGS, value) ? value : "zh";
}

function normalizeRoute(value) {
  return ROUTES.has(value) ? value : "today";
}

function originFor(req) {
  const host = req.headers["x-forwarded-host"] || req.headers.host || "localhost:3000";
  const proto = req.headers["x-forwarded-proto"] || (String(host).includes("localhost") ? "http" : "https");
  return `${proto}://${host}`;
}

function keywords(lang, route) {
  const values = {
    en: "digital sanctuary, anxiety relief website, cozy web corner, digital hug, white noise breathing, mindful micro break, anonymous joy exchange",
    zh: "治愈小网站, 放松心情, 缓解焦虑, 数字拥抱, 白噪音呼吸, 情绪解压, 匿名快乐交换",
    tc: "治癒小網站, 放鬆心情, 緩解焦慮, 數位擁抱, 白噪音呼吸, 情緒解壓, 匿名快樂交換"
  };
  return `${values[lang]}, OASIS, ${route}`;
}

function structuredData(origin, lang, route, title, description) {
  return {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    name: "OASIS",
    url: `${origin}/oasis/${lang}/${route}`,
    applicationCategory: "WellnessApplication",
    inLanguage: LANGS[lang],
    description,
    offers: { "@type": "Offer", price: "0", priceCurrency: "USD" },
    featureList: ["digital hugs", "white noise breathing", "private venting", "anonymous joy swapping"]
  };
}

function renderOasisHtml(req, lang, route) {
  const safeLang = normalizeLang(lang);
  const safeRoute = normalizeRoute(route);
  const origin = originFor(req);
  const [title, description] = META[safeLang][safeRoute];
  const canonical = `${origin}/oasis/${safeLang}/${safeRoute}`;
  const htmlPath = path.join(process.cwd(), "oasis", "index.html");
  let html = fs.readFileSync(htmlPath, "utf8");
  const replacements = {
    "__LANG_ATTR__": LANGS[safeLang],
    "__SEO_TITLE__": title,
    "__SEO_DESCRIPTION__": description,
    "__SEO_KEYWORDS__": keywords(safeLang, safeRoute),
    "__CANONICAL_URL__": canonical,
    "__ALT_EN__": `${origin}/oasis/en/${safeRoute}`,
    "__ALT_ZH__": `${origin}/oasis/zh/${safeRoute}`,
    "__ALT_TC__": `${origin}/oasis/tc/${safeRoute}`,
    "__ALT_DEFAULT__": `${origin}/oasis/en/${safeRoute}`,
    "__OG_LOCALE__": { en: "en_US", zh: "zh_CN", tc: "zh_HK" }[safeLang],
    "__STRUCTURED_DATA__": JSON.stringify(structuredData(origin, safeLang, safeRoute, title, description))
  };
  for (const [key, value] of Object.entries(replacements)) {
    html = html.replaceAll(key, value);
  }
  return html;
}

function supabaseHeaders(extra = {}) {
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY;
  return {
    apikey: key || "",
    Authorization: `Bearer ${key || ""}`,
    ...extra
  };
}

function requireSupabase(res) {
  if (!process.env.SUPABASE_URL || !(process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY)) {
    res.statusCode = 503;
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.end(JSON.stringify({ error: "Supabase environment variables are not configured." }));
    return false;
  }
  return true;
}

async function readJson(req) {
  if (req.body && typeof req.body === "object") return req.body;
  if (typeof req.body === "string") return JSON.parse(req.body || "{}");
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  const raw = Buffer.concat(chunks).toString("utf8");
  return raw ? JSON.parse(raw) : {};
}

async function supabaseRest(pathname, options = {}) {
  const url = `${process.env.SUPABASE_URL.replace(/\/$/, "")}/rest/v1${pathname}`;
  return fetch(url, {
    ...options,
    headers: supabaseHeaders({
      "Content-Type": "application/json",
      ...(options.headers || {})
    })
  });
}

module.exports = {
  LANGS,
  ROUTES,
  META,
  normalizeLang,
  normalizeRoute,
  originFor,
  renderOasisHtml,
  requireSupabase,
  readJson,
  supabaseRest
};
