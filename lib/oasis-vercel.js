const fs = require("fs");
const path = require("path");

const LANGS = { en: "en", zh: "zh-CN", tc: "zh-Hant" };
const ROUTES = new Set(["today", "sound", "vent", "joy"]);
const GUIDE_SLUGS = ["digital-hug", "anxiety-breathing", "white-noise", "anonymous-venting", "cozy-web-corner"];

const META = {
  en: {
    today: ["Digital Sanctuary - Pause when you are tired | OASIS", "A lightweight digital sanctuary for tired, anxious, sleepy, or in-between moments: kind words, white noise, and private release."],
    sound: ["Sound Oasis - White noise breathing room | OASIS", "Relax with woodfire, cat purr, rain, autumn leaves, and a soft 4-7-8 breathing guide."],
    vent: ["Release Pool - Privately put down a heavy moment | OASIS", "Write one thing you do not want to carry and let it go. Private release notes are never shown publicly."],
    joy: ["Joy Swapper - Anonymous happy moments | OASIS", "Share a tiny happy moment anonymously and receive a stranger's joy in return."]
  },
  zh: {
    today: ["数字避难所 - 累的时候停一下 | OASIS", "一个轻量数字避难所：给疲惫、焦虑、睡前和工作间隙的人一句温柔话、白噪音和匿名解压入口。"],
    sound: ["声音绿洲 - 白噪音与呼吸引导 | OASIS", "木火、猫咪呼噜、雨声、秋叶，以及柔和的 4-7-8 呼吸练习。"],
    vent: ["解压池 - 私密放下此刻的重量 | OASIS", "写下一句此刻不想带走的东西，然后把它放下。内容不会公开展示。"],
    joy: ["快乐交换商店 - 匿名交换小开心 | OASIS", "匿名提交一个小小开心，收到陌生人的快乐瞬间。"]
  },
  tc: {
    today: ["數位避難所 - 累的時候停一下 | OASIS", "一個輕量數位避難所：給疲憊、焦慮、睡前和工作間隙的人一句溫柔話、白噪音和匿名解壓入口。"],
    sound: ["聲音綠洲 - 白噪音與呼吸引導 | OASIS", "木火、貓咪呼嚕、雨聲、秋葉，以及柔和的 4-7-8 呼吸練習。"],
    vent: ["解壓池 - 私密放下此刻的重量 | OASIS", "寫下一句此刻不想帶走的東西，然後把它放下。內容不會公開展示。"],
    joy: ["快樂交換商店 - 匿名交換小開心 | OASIS", "匿名提交一個小小開心，收到陌生人的快樂瞬間。"]
  }
};

function normalizeLang(value) {
  return Object.prototype.hasOwnProperty.call(LANGS, value) ? value : "zh";
}

function normalizeRoute(value) {
  return ROUTES.has(value) ? value : "today";
}

function normalizeGuideSlug(value) {
  return GUIDE_SLUGS.includes(value) ? value : "digital-hug";
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

const GUIDE_CONTENT = {
  en: {
    "digital-hug": {
      title: "What Is a Digital Hug? A Tiny Ritual for Heavy Moments | OASIS",
      description: "A gentle guide to digital hugs, kind words, and small online rituals that can make a difficult moment feel less lonely.",
      eyebrow: "DIGITAL HUG GUIDE",
      headline: "A digital hug is a small signal that says: you do not have to carry this minute alone.",
      intro: "OASIS uses the phrase digital hug for a brief, low-pressure moment of care: one kind sentence, one slower breath, one reminder that being tired does not make you a failure.",
      sections: [
        ["Why tiny comfort works", "When the mind is overloaded, a small cue can be easier to receive than a long explanation. A digital hug is intentionally short, soft, and repeatable."],
        ["How to use it", "Open Today's Hug, read one line slowly, and let it be enough for the next minute. You do not need to turn it into a full self-improvement task."],
        ["A gentle boundary", "OASIS is a calming web corner, not medical treatment. If you are in danger or need urgent support, contact local emergency or crisis services."]
      ],
      cta: "Open Today's Hug",
      ctaHref: "/oasis/en/today",
      keywords: "digital hug, kind words, calming website, anxiety relief micro moment"
    },
    "anxiety-breathing": {
      title: "4-7-8 Breathing as a Soft Online Break | OASIS",
      description: "A simple explanation of 4-7-8 breathing and how to use a gentle visual guide for short anxiety relief breaks.",
      eyebrow: "BREATHING GUIDE",
      headline: "Breathing is not about doing it perfectly. It is about giving the body one steady rhythm to follow.",
      intro: "The Sound Oasis page includes a quiet breathing circle. It expands and settles so your attention has something simple to hold.",
      sections: [
        ["The rhythm", "Inhale for 4 seconds, hold for 7 seconds, and exhale for 8 seconds. If that feels too long, shorten it. Comfort matters more than precision."],
        ["When to try it", "Use it between meetings, before sleep, after a difficult message, or whenever your thoughts feel too crowded to sort."],
        ["Keep it low pressure", "Stop if breath holding feels uncomfortable. A softer rhythm like 3-3-5 is still a valid calming break."]
      ],
      cta: "Try Sound Oasis",
      ctaHref: "/oasis/en/sound",
      keywords: "4-7-8 breathing, anxiety breathing, breathing guide, mindful micro break"
    },
    "white-noise": {
      title: "White Noise for a Cozy Digital Sanctuary | OASIS",
      description: "How soft ambient sound like rain, woodfire, cat purr, and leaves can help create a quieter online corner.",
      eyebrow: "WHITE NOISE GUIDE",
      headline: "A small soundscape can make a screen feel less sharp and a room feel more held.",
      intro: "White noise and ambient loops are useful because they give attention a harmless place to rest. OASIS keeps the sound controls simple: pick one texture, or blend several.",
      sections: [
        ["Choose a texture", "Rain can feel steady, fire can feel warm, leaves can feel spacious, and a cat purr can feel close and familiar."],
        ["Use low volume", "The goal is not to cover the world completely. Let the sound sit behind your day like a soft background."],
        ["Make it a cue", "Return to the same sound when you want to read, breathe, journal, or end the day with less friction."]
      ],
      cta: "Open White Noise",
      ctaHref: "/oasis/en/sound",
      keywords: "white noise, ambient sound, cozy web corner, rain sound breathing"
    },
    "anonymous-venting": {
      title: "Anonymous Venting Without Saving Your Worries | OASIS",
      description: "Why a private, browser-only venting ritual can help you name a worry without leaving a permanent record.",
      eyebrow: "PRIVATE VENTING GUIDE",
      headline: "Some thoughts only need to be named, softened, and put down.",
      intro: "The Release Pool lets you type one heavy sentence and let it sink out of the moment. The note is not saved or shown publicly.",
      sections: [
        ["Why privacy matters", "A venting space should not make you wonder who will read it later. OASIS keeps this ritual client-side by design."],
        ["Write simply", "You can write one sentence, one word, or a messy draft. The point is expression, not a polished confession."],
        ["After release", "Notice whether your shoulders, jaw, or breathing changed even slightly. You do not have to feel better right away."]
      ],
      cta: "Use Release Pool",
      ctaHref: "/oasis/en/vent",
      keywords: "anonymous venting, private worry release, stress relief website, emotional release"
    },
    "cozy-web-corner": {
      title: "How to Build a Cozy Web Corner Into Your Day | OASIS",
      description: "A gentle guide to using a tiny calming website as a daily pause without turning rest into another task.",
      eyebrow: "COZY WEB CORNER",
      headline: "A cozy web corner is a place you visit before the day gets too loud.",
      intro: "OASIS is designed for tiny visits: one sentence, one breath, one sound, one happy moment from someone else.",
      sections: [
        ["Keep visits short", "Two minutes is enough. A calming ritual works best when it remains easy to begin."],
        ["Pair it with a real cue", "Open it with tea, after commuting, before sleep, or when you close a difficult tab."],
        ["Share gently", "If a line helps you, copy it to someone who might need a softer minute too."]
      ],
      cta: "Enter OASIS",
      ctaHref: "/oasis/en/today",
      keywords: "cozy web corner, calming website, digital sanctuary, tiny wellness ritual"
    }
  },
  zh: {
    "digital-hug": {
      title: "什么是数字拥抱？给疲惫时刻的一分钟温柔 | OASIS",
      description: "了解数字拥抱、温柔句子和轻量线上仪式，如何让一个难熬的小瞬间变得没那么孤单。",
      eyebrow: "数字拥抱指南",
      headline: "数字拥抱不是解决一切，它只是轻轻提醒你：这一分钟不用一个人扛。",
      intro: "在 OASIS 里，数字拥抱是一句很短的温柔话、一次慢一点的呼吸、一个允许自己不完美的提示。",
      sections: [
        ["为什么要做得很小", "当人已经疲惫时，长篇道理常常进不来。短句、轻触和可重复的小仪式，反而更容易被身体接住。"],
        ["怎么使用", "打开今日拥抱，慢慢读一句话，让它只陪你撑过下一分钟。它不需要变成新的任务。"],
        ["温柔边界", "OASIS 是放松心情的小角落，不是医疗或心理治疗。如果你处在危险中，请及时联系本地紧急援助。"]
      ],
      cta: "打开今日拥抱",
      ctaHref: "/oasis/zh/today",
      keywords: "数字拥抱, 温柔句子, 治愈小网站, 缓解焦虑小工具"
    },
    "anxiety-breathing": {
      title: "4-7-8 呼吸：给焦虑时刻的柔和线上休息 | OASIS",
      description: "了解 4-7-8 呼吸节奏，以及如何用可视化呼吸圆点做一个短暂、温柔的情绪缓冲。",
      eyebrow: "呼吸指南",
      headline: "呼吸练习不是为了做得完美，而是给身体一个可以跟随的稳定节奏。",
      intro: "声音绿洲里有一个安静的呼吸圆点。它慢慢变大、停留、再缩小，让注意力有一个简单的位置可以停靠。",
      sections: [
        ["基础节奏", "吸气 4 秒，停留 7 秒，呼气 8 秒。如果觉得太长，可以缩短。舒服比标准更重要。"],
        ["什么时候适合", "会议间隙、睡前、收到压力消息之后，或者脑子太满但又不知道从哪里整理时，都可以试一次。"],
        ["不要勉强", "如果屏息让你不舒服，就改成 3-3-5 这样的短节奏。柔和地停下来，也是一种照顾。"]
      ],
      cta: "试试白噪音呼吸",
      ctaHref: "/oasis/zh/sound",
      keywords: "4-7-8 呼吸, 缓解焦虑, 呼吸引导, 放松心情"
    },
    "white-noise": {
      title: "白噪音如何把网页变成一个舒服的小角落 | OASIS",
      description: "了解雨声、柴火、猫咪呼噜和秋叶声如何帮助你创造更安静的数字避难所。",
      eyebrow: "白噪音指南",
      headline: "一层轻轻的声音，可以让屏幕不那么刺眼，让房间变得更容易待下去。",
      intro: "白噪音和环境音的好处，是给注意力一个无害、稳定的落点。OASIS 把控制做得很简单：选一种声音，或者轻轻混合几种。",
      sections: [
        ["选择声音质感", "雨声像稳定的背景，柴火像温暖的房间，秋叶更空旷，猫咪呼噜则更靠近身体。"],
        ["音量放低", "它不需要盖过世界，只要像一层柔和背景，留在你的一天后面。"],
        ["把它变成提示", "每次读书、呼吸、写点东西或准备睡觉时，回到同一种声音，身体会慢慢记住这个停靠点。"]
      ],
      cta: "打开声音绿洲",
      ctaHref: "/oasis/zh/sound",
      keywords: "白噪音, 雨声, 猫咪呼噜, 放松网站, 数字避难所"
    },
    "anonymous-venting": {
      title: "匿名解压：写下烦恼，但不把它存进数据库 | OASIS",
      description: "为什么一个只在浏览器里发生的私人释放仪式，可以帮你命名烦恼，又不留下永久记录。",
      eyebrow: "匿名解压指南",
      headline: "有些念头不一定要被保存，它们只需要被看见、变轻，然后离开。",
      intro: "解压池允许你写下此刻很重的一句话，再让它慢慢沉下去。内容不会保存，也不会公开展示。",
      sections: [
        ["隐私为什么重要", "真正的释放不该让你担心以后谁会读到。OASIS 特意把这个仪式留在浏览器里。"],
        ["写得简单就好", "一句话、一个词、一段乱糟糟的草稿都可以。重点是表达，不是写得漂亮。"],
        ["放下之后", "可以留意一下肩膀、下颌或呼吸有没有轻一点点。你不需要马上变好。"]
      ],
      cta: "进入解压池",
      ctaHref: "/oasis/zh/vent",
      keywords: "匿名解压, 情绪释放, 压力缓解, 私人树洞"
    },
    "cozy-web-corner": {
      title: "如何把一个治愈小网站放进日常 | OASIS",
      description: "学会用一个免费的安静网页做每日短暂停靠，不把休息变成另一项任务。",
      eyebrow: "治愈小角落",
      headline: "一个舒服的网页角落，是在生活变得太吵之前，给自己留的一点空白。",
      intro: "OASIS 适合很短的访问：一句温柔话、一次呼吸、一层声音、一个陌生人的小开心。",
      sections: [
        ["访问要短", "两分钟就够了。越容易开始的小仪式，越可能真的留在生活里。"],
        ["绑定真实提示", "可以在泡茶时、通勤后、睡前，或者关掉一个很累的页面之后打开它。"],
        ["轻轻分享", "如果某句话帮到了你，可以复制给一个可能也需要被温柔接住的人。"]
      ],
      cta: "进入 OASIS",
      ctaHref: "/oasis/zh/today",
      keywords: "治愈小网站, 数字避难所, 放松心情, 温柔网页"
    }
  },
  tc: {
    "digital-hug": {
      title: "什麼是數位擁抱？給疲憊時刻的一分鐘溫柔 | OASIS",
      description: "了解數位擁抱、溫柔句子和輕量線上儀式，如何讓一個難熬的小瞬間變得沒那麼孤單。",
      eyebrow: "數位擁抱指南",
      headline: "數位擁抱不是解決一切，它只是輕輕提醒你：這一分鐘不用一個人扛。",
      intro: "在 OASIS 裡，數位擁抱是一句很短的溫柔話、一次慢一點的呼吸、一次允許自己不完美的提示。",
      sections: [
        ["為什麼要做得很小", "當人已經疲憊時，長篇道理常常進不來。短句、輕觸和可重複的小儀式，反而更容易被身體接住。"],
        ["怎麼使用", "打開今日擁抱，慢慢讀一句話，讓它只陪你撐過下一分鐘。它不需要變成新的任務。"],
        ["溫柔邊界", "OASIS 是放鬆心情的小角落，不是醫療或心理治療。如果你處在危險中，請及時聯繫本地緊急援助。"]
      ],
      cta: "打開今日擁抱",
      ctaHref: "/oasis/tc/today",
      keywords: "數位擁抱, 溫柔句子, 治癒小網站, 緩解焦慮小工具"
    },
    "anxiety-breathing": {
      title: "4-7-8 呼吸：給焦慮時刻的柔和線上休息 | OASIS",
      description: "了解 4-7-8 呼吸節奏，以及如何用視覺化呼吸圓點做一個短暫、溫柔的情緒緩衝。",
      eyebrow: "呼吸指南",
      headline: "呼吸練習不是為了做得完美，而是給身體一個可以跟隨的穩定節奏。",
      intro: "聲音綠洲裡有一個安靜的呼吸圓點。它慢慢變大、停留、再縮小，讓注意力有一個簡單的位置可以停靠。",
      sections: [
        ["基礎節奏", "吸氣 4 秒，停留 7 秒，呼氣 8 秒。如果覺得太長，可以縮短。舒服比標準更重要。"],
        ["什麼時候適合", "會議間隙、睡前、收到壓力訊息之後，或者腦子太滿但又不知道從哪裡整理時，都可以試一次。"],
        ["不要勉強", "如果屏息讓你不舒服，就改成 3-3-5 這樣的短節奏。柔和地停下來，也是一種照顧。"]
      ],
      cta: "試試白噪音呼吸",
      ctaHref: "/oasis/tc/sound",
      keywords: "4-7-8 呼吸, 緩解焦慮, 呼吸引導, 放鬆心情"
    },
    "white-noise": {
      title: "白噪音如何把網頁變成一個舒服的小角落 | OASIS",
      description: "了解雨聲、柴火、貓咪呼嚕和秋葉聲如何幫助你創造更安靜的數位避難所。",
      eyebrow: "白噪音指南",
      headline: "一層輕輕的聲音，可以讓螢幕不那麼刺眼，讓房間變得更容易待下去。",
      intro: "白噪音和環境音的好處，是給注意力一個無害、穩定的落點。OASIS 把控制做得很簡單：選一種聲音，或者輕輕混合幾種。",
      sections: [
        ["選擇聲音質感", "雨聲像穩定的背景，柴火像溫暖的房間，秋葉更空曠，貓咪呼嚕則更靠近身體。"],
        ["音量放低", "它不需要蓋過世界，只要像一層柔和背景，留在你的一天後面。"],
        ["把它變成提示", "每次讀書、呼吸、寫點東西或準備睡覺時，回到同一種聲音，身體會慢慢記住這個停靠點。"]
      ],
      cta: "打開聲音綠洲",
      ctaHref: "/oasis/tc/sound",
      keywords: "白噪音, 雨聲, 貓咪呼嚕, 放鬆網站, 數位避難所"
    },
    "anonymous-venting": {
      title: "匿名解壓：寫下煩惱，但不把它存進資料庫 | OASIS",
      description: "為什麼一個只在瀏覽器裡發生的私人釋放儀式，可以幫你命名煩惱，又不留下永久記錄。",
      eyebrow: "匿名解壓指南",
      headline: "有些念頭不一定要被保存，它們只需要被看見、變輕，然後離開。",
      intro: "解壓池允許你寫下此刻很重的一句話，再讓它慢慢沉下去。內容不會保存，也不會公開展示。",
      sections: [
        ["隱私為什麼重要", "真正的釋放不該讓你擔心以後誰會讀到。OASIS 特意把這個儀式留在瀏覽器裡。"],
        ["寫得簡單就好", "一句話、一個詞、一段亂糟糟的草稿都可以。重點是表達，不是寫得漂亮。"],
        ["放下之後", "可以留意一下肩膀、下顎或呼吸有沒有輕一點點。你不需要馬上變好。"]
      ],
      cta: "進入解壓池",
      ctaHref: "/oasis/tc/vent",
      keywords: "匿名解壓, 情緒釋放, 壓力緩解, 私人樹洞"
    },
    "cozy-web-corner": {
      title: "如何把一個治癒小網站放進日常 | OASIS",
      description: "學會用一個免費的安靜網頁做每日短暫停靠，不把休息變成另一項任務。",
      eyebrow: "治癒小角落",
      headline: "一個舒服的網頁角落，是在生活變得太吵之前，給自己留的一點空白。",
      intro: "OASIS 適合很短的訪問：一句溫柔話、一次呼吸、一層聲音、一個陌生人的小開心。",
      sections: [
        ["訪問要短", "兩分鐘就夠了。越容易開始的小儀式，越可能真的留在生活裡。"],
        ["綁定真實提示", "可以在泡茶時、通勤後、睡前，或者關掉一個很累的頁面之後打開它。"],
        ["輕輕分享", "如果某句話幫到了你，可以複製給一個可能也需要被溫柔接住的人。"]
      ],
      cta: "進入 OASIS",
      ctaHref: "/oasis/tc/today",
      keywords: "治癒小網站, 數位避難所, 放鬆心情, 溫柔網頁"
    }
  }
};

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  })[char]);
}

function renderGuideHtml(req, lang, slug) {
  const safeLang = normalizeLang(lang);
  const safeSlug = normalizeGuideSlug(slug);
  const origin = originFor(req);
  const guide = GUIDE_CONTENT[safeLang][safeSlug];
  const canonical = `${origin}/oasis/${safeLang}/guide/${safeSlug}`;
  const langLabel = { en: "EN", zh: "简", tc: "繁" };
  const labels = {
    en: { back: "Back to OASIS", readMore: "More quiet guides" },
    zh: { back: "回到 OASIS", readMore: "更多安静指南" },
    tc: { back: "回到 OASIS", readMore: "更多安靜指南" }
  }[safeLang];
  const articleJson = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: guide.title,
    description: guide.description,
    author: { "@type": "Organization", name: "OASIS" },
    publisher: { "@type": "Organization", name: "OASIS" },
    inLanguage: LANGS[safeLang],
    mainEntityOfPage: canonical
  };
  const guideLinks = GUIDE_SLUGS
    .filter((item) => item !== safeSlug)
    .map((item) => `<a href="/oasis/${safeLang}/guide/${item}">${escapeHtml(GUIDE_CONTENT[safeLang][item].eyebrow)}</a>`)
    .join("");
  return `<!DOCTYPE html>
<html lang="${LANGS[safeLang]}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="google-site-verification" content="gor7CUCalhiruDBHpFwXK26_b9z8q_V1H83GNluy5VU">
  <title>${escapeHtml(guide.title)}</title>
  <meta name="description" content="${escapeHtml(guide.description)}">
  <meta name="keywords" content="${escapeHtml(`${guide.keywords}, OASIS`)}">
  <meta property="og:title" content="${escapeHtml(guide.title)}">
  <meta property="og:description" content="${escapeHtml(guide.description)}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="${canonical}">
  <meta property="og:image" content="${origin}/oasis/og-image.svg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="${escapeHtml(guide.title)}">
  <meta name="twitter:description" content="${escapeHtml(guide.description)}">
  <meta name="twitter:image" content="${origin}/oasis/og-image.svg">
  <link rel="canonical" href="${canonical}">
  <link rel="alternate" hreflang="en" href="${origin}/oasis/en/guide/${safeSlug}">
  <link rel="alternate" hreflang="zh-CN" href="${origin}/oasis/zh/guide/${safeSlug}">
  <link rel="alternate" hreflang="zh-Hant" href="${origin}/oasis/tc/guide/${safeSlug}">
  <link rel="alternate" hreflang="x-default" href="${origin}/oasis/en/guide/${safeSlug}">
  <script type="application/ld+json">${JSON.stringify(articleJson)}</script>
  <script>
    (function() {
      var GA_MEASUREMENT_ID = "G-JYE6MFTFTB";
      var allowedHosts = ["tiny-joy-oasis.vercel.app"];
      if (allowedHosts.indexOf(window.location.hostname) === -1) return;
      window.dataLayer = window.dataLayer || [];
      window.gtag = function() { window.dataLayer.push(arguments); };
      window.gtag("js", new Date());
      window.gtag("config", GA_MEASUREMENT_ID, {
        page_path: window.location.pathname,
        page_title: document.title,
        oasis_lang: "${safeLang}",
        oasis_route: "guide",
        guide_slug: "${safeSlug}"
      });
      var script = document.createElement("script");
      script.async = true;
      script.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_MEASUREMENT_ID;
      document.head.appendChild(script);
    })();
  </script>
  <style>
    body { margin: 0; min-height: 100vh; color: #475569; font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Helvetica Neue', sans-serif; background: linear-gradient(135deg, #FDFBF7 0%, #F5EFE6 52%, #E6F0FA 100%); }
    .nav { max-width: 1040px; margin: 0 auto; padding: 28px 28px 8px; display: flex; justify-content: space-between; align-items: center; gap: 18px; }
    .logo { letter-spacing: 2px; font-weight: 600; color: #1e293b; text-decoration: none; }
    .langs { display: flex; gap: 10px; align-items: center; font-size: 13px; }
    .langs a { color: #94a3b8; text-decoration: none; }
    .langs a.active { color: #475569; font-weight: 600; }
    main { max-width: 820px; margin: 0 auto; padding: 56px 28px 72px; }
    .eyebrow { display: inline-block; font-size: 12px; letter-spacing: 2px; color: #FDA4AF; background: rgba(255, 241, 242, 0.8); border-radius: 999px; padding: 7px 16px; font-weight: 600; }
    h1 { color: #1e293b; font-size: clamp(32px, 5vw, 54px); line-height: 1.08; letter-spacing: 0; font-weight: 500; margin: 26px 0 22px; max-width: 780px; }
    .intro { font-size: 18px; line-height: 1.9; color: #64748b; margin: 0 0 34px; }
    article { background: rgba(255,255,255,0.72); border: 1px solid rgba(255,255,255,0.8); border-radius: 28px; padding: 30px; box-shadow: 0 30px 60px rgba(148, 163, 184, 0.06); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); }
    section + section { border-top: 1px solid rgba(226, 232, 240, 0.7); margin-top: 24px; padding-top: 24px; }
    h2 { color: #1e293b; font-weight: 500; font-size: 22px; margin: 0 0 10px; }
    p { font-size: 16px; line-height: 1.9; margin: 0; }
    .actions { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 30px; align-items: center; }
    .button { color: #57534e; font-weight: 600; text-decoration: none; border-radius: 999px; padding: 13px 22px; background: linear-gradient(90deg, #FAD0C4 0%, #FEE180 100%); box-shadow: 0 8px 20px rgba(250, 208, 196, 0.34); }
    .guide-links { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 38px; font-size: 14px; }
    .guide-links span { color: #94a3b8; margin-right: 2px; }
    .guide-links a { color: #64748b; text-decoration: none; background: rgba(255,255,255,0.55); border: 1px solid rgba(226,232,240,0.7); border-radius: 999px; padding: 8px 12px; }
    @media (max-width: 680px) { .nav { padding: 24px 20px 0; } main { padding: 42px 20px 58px; } article { padding: 24px 20px; border-radius: 24px; } }
  </style>
</head>
<body>
  <nav class="nav">
    <a class="logo" href="/oasis/${safeLang}/today">OASIS .</a>
    <div class="langs">${Object.keys(LANGS).map((item) => `<a class="${item === safeLang ? "active" : ""}" href="/oasis/${item}/guide/${safeSlug}">${langLabel[item]}</a>`).join("<span>|</span>")}</div>
  </nav>
  <main>
    <span class="eyebrow">${escapeHtml(guide.eyebrow)}</span>
    <h1>${escapeHtml(guide.headline)}</h1>
    <p class="intro">${escapeHtml(guide.intro)}</p>
    <article>
      ${guide.sections.map(([heading, body]) => `<section><h2>${escapeHtml(heading)}</h2><p>${escapeHtml(body)}</p></section>`).join("")}
      <div class="actions">
        <a class="button" href="${guide.ctaHref}">${escapeHtml(guide.cta)}</a>
        <a href="/oasis/${safeLang}/today">${escapeHtml(labels.back)}</a>
      </div>
    </article>
    <div class="guide-links"><span>${escapeHtml(labels.readMore)}</span>${guideLinks}</div>
  </main>
</body>
</html>`;
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
    "__OG_IMAGE__": `${origin}/oasis/og-image.svg`,
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
  GUIDE_SLUGS,
  GUIDE_CONTENT,
  normalizeGuideSlug,
  renderGuideHtml,
  requireSupabase,
  readJson,
  supabaseRest
};
