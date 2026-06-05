const LANGS = ["en", "zh", "tc"];
const ROUTES = ["today", "sound", "vent", "joy"];
const BASE = "/oasis";

const copy = {
  en: {
    nav: { today: "Today's Hug", sound: "Sound Oasis", vent: "Cyber Vent", joy: "Joy Swapper" },
    footer: "NO ACCOUNT · NO PRESSURE · A SOFT CORNER OF THE WEB",
    today: {
      tag: "TODAY'S HUG",
      title: "A micro-moment for your nervous system",
      desc: "Tap once. Receive a small sentence that asks nothing from you.",
      button: "Get a Micro-moment",
      source: "OASIS keeps this gentle and random."
    },
    sound: {
      tag: "SOUND OASIS",
      title: "A small white-noise breathing room",
      desc: "Choose a texture, then start the 4-7-8 visual breathing guide.",
      start: "Start Breathe",
      stop: "Pause Breathe",
      sounds: [
        ["🔥 Woodfire", "warm crackle"],
        ["🐱 Cat Purr", "steady comfort"],
        ["🌧️ Rain", "soft morning rain"],
        ["🍂 Autumn Leaves", "paper-light rustle"]
      ],
      note: "Audio is synthesized locally as a placeholder; replace with licensed loops when deploying."
    },
    vent: {
      tag: "CYBER VENT",
      title: "Release a thought without saving it",
      desc: "Write the worry. Let it collapse. Nothing is sent to the server.",
      placeholder: "Write it here. This text will never be saved.",
      button: "Release",
      after: "It left this page. Nothing was saved."
    },
    joy: {
      tag: "JOY SWAPPER",
      title: "Trade a tiny happy thing",
      desc: "Leave a small joy anonymously, then receive one from someone else.",
      placeholder: "A tiny happy thing from today...",
      button: "Submit & Swap",
      empty: "The first sip of tea was exactly the right temperature.",
      received: "A tiny joy arrived."
    }
  },
  zh: {
    nav: { today: "今日拥抱", sound: "声音绿洲", vent: "赛博解压", joy: "快乐交换" },
    footer: "不登录 · 不催促 · 一个温柔的网页角落",
    today: {
      tag: "TODAY'S HUG",
      title: "给神经系统的一个小瞬间",
      desc: "点一下。收下一句不向你索取任何东西的温柔话。",
      button: "获得一个小瞬间",
      source: "OASIS 会随机送出一句温柔话。"
    },
    sound: {
      tag: "SOUND OASIS",
      title: "一间很小的白噪音呼吸室",
      desc: "选择一种声音质感，再启动 4-7-8 视觉呼吸引导。",
      start: "开始呼吸",
      stop: "暂停呼吸",
      sounds: [
        ["🔥 木火", "温暖的噼啪声"],
        ["🐱 猫咪呼噜", "稳定的靠近感"],
        ["🌧️ 雨声", "清晨的细雨"],
        ["🍂 秋叶", "很轻的沙沙声"]
      ],
      note: "当前声音为本地合成占位；上线时可替换成授权循环音频。"
    },
    vent: {
      tag: "CYBER VENT",
      title: "释放一个不会被保存的念头",
      desc: "写下烦恼，让它塌缩消失。不会发送到后台。",
      placeholder: "写在这里。这里的文字永远不会被保存。",
      button: "释放",
      after: "它已经离开这个页面。没有任何内容被保存。"
    },
    joy: {
      tag: "JOY SWAPPER",
      title: "交换一件很小的开心",
      desc: "匿名留下一个小开心，然后收到另一个人的小开心。",
      placeholder: "今天发生的一件很小但开心的事...",
      button: "提交并交换",
      empty: "第一口茶刚好是最舒服的温度。",
      received: "一个小快乐到了。"
    }
  },
  tc: {
    nav: { today: "今日擁抱", sound: "聲音綠洲", vent: "賽博解壓", joy: "快樂交換" },
    footer: "不登入 · 不催促 · 一個溫柔的網頁角落",
    today: {
      tag: "TODAY'S HUG",
      title: "給神經系統的一個小瞬間",
      desc: "點一下。收下一句不向你索取任何東西的溫柔話。",
      button: "獲得一個小瞬間",
      source: "OASIS 會隨機送出一句溫柔話。"
    },
    sound: {
      tag: "SOUND OASIS",
      title: "一間很小的白噪音呼吸室",
      desc: "選擇一種聲音質感，再啟動 4-7-8 視覺呼吸引導。",
      start: "開始呼吸",
      stop: "暫停呼吸",
      sounds: [
        ["🔥 木火", "溫暖的噼啪聲"],
        ["🐱 貓咪呼嚕", "穩定的靠近感"],
        ["🌧️ 雨聲", "清晨的細雨"],
        ["🍂 秋葉", "很輕的沙沙聲"]
      ],
      note: "目前聲音為本地合成占位；上線時可替換成授權循環音頻。"
    },
    vent: {
      tag: "CYBER VENT",
      title: "釋放一個不會被保存的念頭",
      desc: "寫下煩惱，讓它塌縮消失。不會發送到後台。",
      placeholder: "寫在這裡。這裡的文字永遠不會被保存。",
      button: "釋放",
      after: "它已經離開這個頁面。沒有任何內容被保存。"
    },
    joy: {
      tag: "JOY SWAPPER",
      title: "交換一件很小的開心",
      desc: "匿名留下一個小開心，然後收到另一個人的小開心。",
      placeholder: "今天發生的一件很小但開心的事...",
      button: "提交並交換",
      empty: "第一口茶剛好是最舒服的溫度。",
      received: "一個小快樂到了。"
    }
  }
};

const quotes = {
  en: [
    "You do not have to solve your whole life before drinking water.",
    "Some days healing is only noticing the light on the table.",
    "You are allowed to be unfinished and still deeply worthy of care.",
    "Let the next breath be enough for the next minute.",
    "Softness is also a form of intelligence."
  ],
  zh: [
    "你不用在喝水前解决整个人生。",
    "有些日子的治愈，只是看见桌上的光。",
    "你可以还没有完成，也依然值得被好好照顾。",
    "先让下一次呼吸，撑过下一分钟。",
    "柔软也是一种很聪明的力量。"
  ],
  tc: [
    "你不用在喝水前解決整個人生。",
    "有些日子的治癒，只是看見桌上的光。",
    "你可以還沒有完成，也依然值得被好好照顧。",
    "先讓下一次呼吸，撐過下一分鐘。",
    "柔軟也是一種很聰明的力量。"
  ]
};

let lang = "zh";
let route = "today";
let breathTimer = null;
let breathExpanded = false;
let lastTrackedPageView = "";

const soundKeys = ["fire", "cat", "rain", "leaves"];
const soundSources = {
  fire: "/api/oasis/audio/fire",
  cat: "/api/oasis/audio/cat",
  rain: "/api/oasis/audio/rain",
  leaves: "/api/oasis/audio/leaves"
};
const audioInstances = {};
const fallbackAudioInstances = {};
let fallbackAudioContext = null;

const card = document.querySelector(".dopamine-card");
const tabs = document.querySelector(".page-tabs");
const langSwitcher = document.querySelector(".lang-switcher");
const footer = document.querySelector(".footer-tips");

init();

function init() {
  readPath();
  renderShell();
  renderPage();
  trackPageView();
  window.addEventListener("popstate", () => {
    readPath();
    renderShell();
    renderPage();
    trackPageView();
  });
}

function readPath() {
  const parts = location.pathname.split("/").filter(Boolean);
  lang = LANGS.includes(parts[1]) ? parts[1] : "zh";
  route = ROUTES.includes(parts[2]) ? parts[2] : "today";
}

function pathFor(nextLang = lang, nextRoute = route) {
  return `/oasis/${nextLang}/${nextRoute}`;
}

function navigate(nextLang, nextRoute) {
  stopAllAudio();
  clearBreath();
  lang = nextLang;
  route = nextRoute;
  history.pushState({}, "", pathFor());
  renderShell();
  renderPage();
  trackPageView();
  document.querySelector("#main")?.focus({ preventScroll: true });
}

function trackPageView() {
  const path = `${location.pathname}${location.search}`;
  const dedupeKey = `${lang}|${route}|${path}`;
  if (dedupeKey === lastTrackedPageView) return;
  lastTrackedPageView = dedupeKey;
  fetch("/api/oasis/analytics/pageview", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      lang,
      route,
      path,
      referrer: document.referrer || "",
      title: document.title
    }),
    keepalive: true
  }).catch(() => {});
}

function renderShell() {
  const t = copy[lang];
  document.documentElement.lang = lang === "zh" ? "zh-CN" : lang === "tc" ? "zh-Hant" : "en";
  document.querySelector(".logo").href = pathFor(lang, "today");
  tabs.innerHTML = ROUTES.map((item) => `
    <button class="tab-btn ${item === route ? "active" : ""}" data-route="${item}" role="tab" aria-selected="${item === route}">
      ${escapeHtml(t.nav[item])}
    </button>
  `).join("");
  footer.textContent = t.footer;
  langSwitcher.querySelectorAll("[data-lang]").forEach((node) => {
    node.classList.toggle("active", node.dataset.lang === lang);
  });
  tabs.querySelectorAll("[data-route]").forEach((button) => {
    button.addEventListener("click", () => navigate(lang, button.dataset.route));
  });
  langSwitcher.querySelectorAll("[data-lang]").forEach((button) => {
    button.addEventListener("click", () => navigate(button.dataset.lang, route));
  });
}

function renderPage() {
  const page = copy[lang][route];
  if (route === "today") renderToday(page);
  if (route === "sound") renderSound(page);
  if (route === "vent") renderVent(page);
  if (route === "joy") renderJoy(page);
}

function renderCardBase(page, body) {
  card.innerHTML = `
    <span class="card-tag">${escapeHtml(page.tag)}</span>
    <h2>${escapeHtml(page.title)}</h2>
    <p class="desc">${escapeHtml(page.desc)}</p>
    ${body}
  `;
}

function renderToday(page) {
  renderCardBase(page, `
    <div class="quote-text" id="quoteText">${escapeHtml(randomItem(quotes[lang]))}</div>
    <button class="happy-btn" id="quoteBtn">${escapeHtml(page.button)}</button>
    <div class="small-note">${escapeHtml(page.source)}</div>
  `);
  document.querySelector("#quoteBtn").addEventListener("click", (event) => {
    popParticles(event);
    const quote = document.querySelector("#quoteText");
    quote.classList.add("fading");
    setTimeout(() => {
      quote.textContent = randomItem(quotes[lang]);
      quote.classList.remove("fading");
    }, 350);
  });
}

function renderSound(page) {
  renderCardBase(page, `
    <div class="sound-grid">
      ${page.sounds.map(([name, sub], index) => `
        <button class="sound-item ${audioInstances[soundKeys[index]] && !audioInstances[soundKeys[index]].paused ? "playing" : ""}" data-sound="${soundKeys[index]}">
          <strong>${escapeHtml(name)}</strong><br>
          <span>${escapeHtml(sub)}</span>
        </button>
      `).join("")}
    </div>
    <div class="breathe-container" id="breatheContainer">
      <div class="breathe-circle" id="breatheCircle" aria-hidden="true"></div>
    </div>
    <button class="happy-btn" id="breatheBtn">${escapeHtml(page.start)}</button>
    <div class="small-note" id="soundNote">${escapeHtml(page.note)}</div>
  `);
  document.querySelectorAll(".sound-item").forEach((button) => {
    button.addEventListener("click", () => {
      toggleSound(button.dataset.sound, button, page);
    });
  });
  document.querySelector("#breatheBtn").addEventListener("click", (event) => {
    popParticles(event);
    toggleBreath(page);
  });
}

function renderVent(page) {
  renderCardBase(page, `
    <form id="ventForm">
      <div class="release-wrap" id="releaseWrap">
        <textarea class="vent-input" id="ventInput" maxlength="700" placeholder="${escapeAttr(page.placeholder)}"></textarea>
      </div>
      <button class="happy-btn" type="submit">${escapeHtml(page.button)}</button>
      <div class="small-note" id="ventNote"></div>
    </form>
  `);
  document.querySelector("#ventForm").addEventListener("submit", (event) => {
    event.preventDefault();
    popParticles(event);
    const wrap = document.querySelector("#releaseWrap");
    const input = document.querySelector("#ventInput");
    const note = document.querySelector("#ventNote");
    wrap.classList.add("released");
    setTimeout(() => {
      input.value = "";
      wrap.classList.remove("released");
      note.textContent = page.after;
    }, 620);
  });
}

async function renderJoy(page) {
  renderCardBase(page, `
    <div class="joy-box" id="joyBox">${escapeHtml(page.empty)}</div>
    <form id="joyForm">
      <textarea class="vent-input joy-input" id="joyInput" maxlength="220" placeholder="${escapeAttr(page.placeholder)}"></textarea>
      <button class="happy-btn" type="submit">${escapeHtml(page.button)}</button>
      <div class="small-note" id="joyNote"></div>
    </form>
  `);
  await loadJoy(page);
  document.querySelector("#joyForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const input = document.querySelector("#joyInput");
    const note = document.querySelector("#joyNote");
    const text = input.value.trim();
    if (text.length < 3 || text.length > 220) {
      note.textContent = lang === "en" ? "Please write between 3 and 220 characters." : lang === "zh" ? "请写 3 到 220 个字。" : "請寫 3 到 220 個字。";
      return;
    }
    try {
      await fetch("/api/oasis/joy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lang, text })
      }).then((res) => {
        if (!res.ok) throw new Error("joy api");
        return res.json();
      });
      input.value = "";
      note.textContent = page.received;
      popParticles(event);
      await loadJoy(page);
    } catch (error) {
      note.textContent = lang === "en" ? "The swap shelf is resting. Try again later." : lang === "zh" ? "交换架正在休息，稍后再试。" : "交換架正在休息，稍後再試。";
    }
  });
}

async function loadJoy(page) {
  const box = document.querySelector("#joyBox");
  try {
    const payload = await fetch(`/api/oasis/joy?lang=${encodeURIComponent(lang)}`).then((res) => res.json());
    box.textContent = payload.text || page.empty;
  } catch (error) {
    box.textContent = page.empty;
  }
}

function toggleBreath(page) {
  const container = document.querySelector("#breatheContainer");
  const circle = document.querySelector("#breatheCircle");
  const button = document.querySelector("#breatheBtn");
  if (breathTimer) {
    clearBreath();
    button.textContent = page.start;
    return;
  }
  container.classList.add("active");
  button.textContent = page.stop;
  breathExpanded = false;
  const step = () => {
    breathExpanded = !breathExpanded;
    circle.classList.toggle("active", breathExpanded);
  };
  step();
  breathTimer = setInterval(step, 4100);
}

function clearBreath() {
  if (breathTimer) clearInterval(breathTimer);
  breathTimer = null;
  breathExpanded = false;
}

function getAudioInstance(soundKey) {
  if (!soundSources[soundKey]) return null;
  if (audioInstances[soundKey]) return audioInstances[soundKey];
  const audio = document.createElement("audio");
  audio.id = `oasis-audio-${soundKey}`;
  audio.loop = true;
  audio.preload = "auto";
  audio.src = soundSources[soundKey];
  audio.volume = 0.42;
  audioInstances[soundKey] = audio;
  document.body.appendChild(audio);
  return audio;
}

function toggleSound(soundKey, button, page) {
  const audio = getAudioInstance(soundKey);
  if (!audio) return;
  if (!audio.paused || fallbackAudioInstances[soundKey]) {
    stopSound(soundKey);
    updateSoundNote(page);
    return;
  }
  button.classList.add("playing");
  primeFallbackAudioContext();
  audio.play().then(() => {
    updateSoundNote(page);
  }).catch(() => {
    startFallbackSound(soundKey);
    updateSoundNote(page);
  });
}

function updateSoundNote(page) {
  const note = document.querySelector("#soundNote");
  if (!note) return;
  const playingCount = document.querySelectorAll(".sound-item.playing").length;
  note.textContent = playingCount ? page.note : page.note;
}

function stopSound(soundKey) {
  const audio = audioInstances[soundKey];
  if (audio) {
    audio.pause();
    audio.currentTime = 0;
  }
  if (fallbackAudioInstances[soundKey]) {
    fallbackAudioInstances[soundKey].stop();
    delete fallbackAudioInstances[soundKey];
  }
  document.querySelector(`[data-sound="${soundKey}"]`)?.classList.remove("playing");
}

function stopAllAudio() {
  soundKeys.forEach((soundKey) => {
    stopSound(soundKey);
  });
}

function primeFallbackAudioContext() {
  const AudioContextClass = window.AudioContext || window.webkitAudioContext;
  if (!AudioContextClass) return null;
  fallbackAudioContext ||= new AudioContextClass();
  if (fallbackAudioContext.state === "suspended" && fallbackAudioContext.resume) {
    fallbackAudioContext.resume();
  }
  return fallbackAudioContext;
}

function startFallbackSound(soundKey) {
  if (fallbackAudioInstances[soundKey]) return;
  const context = primeFallbackAudioContext();
  if (!context) return;
  const gain = context.createGain();
  gain.gain.value = soundKey === "cat" ? 0.035 : 0.05;
  gain.connect(context.destination);
  const nodes = [];
  if (soundKey === "cat") {
    [72, 86].forEach((frequency) => {
      const oscillator = context.createOscillator();
      oscillator.type = "sine";
      oscillator.frequency.value = frequency;
      oscillator.connect(gain);
      oscillator.start();
      nodes.push(oscillator);
    });
  } else {
    const duration = 2;
    const buffer = context.createBuffer(1, context.sampleRate * duration, context.sampleRate);
    const data = buffer.getChannelData(0);
    for (let index = 0; index < data.length; index += 1) {
      const noise = Math.random() * 2 - 1;
      if (soundKey === "fire") data[index] = noise * (Math.random() > 0.986 ? 0.95 : 0.045);
      if (soundKey === "rain") data[index] = noise * 0.16;
      if (soundKey === "leaves") data[index] = noise * (Math.random() > 0.92 ? 0.18 : 0.035);
    }
    const source = context.createBufferSource();
    source.buffer = buffer;
    source.loop = true;
    const filter = context.createBiquadFilter();
    filter.type = soundKey === "rain" ? "lowpass" : "bandpass";
    filter.frequency.value = soundKey === "rain" ? 1200 : soundKey === "fire" ? 650 : 1900;
    source.connect(filter);
    filter.connect(gain);
    source.start();
    nodes.push(source, filter);
  }
  fallbackAudioInstances[soundKey] = {
    stop: () => {
      nodes.forEach((node) => {
        try {
          if (node.stop) node.stop();
          if (node.disconnect) node.disconnect();
        } catch (error) {}
      });
      try { gain.disconnect(); } catch (error) {}
    }
  };
}

function popParticles(event) {
  const rect = event?.target?.getBoundingClientRect?.();
  const x = rect ? rect.left + rect.width / 2 : innerWidth / 2;
  const y = rect ? rect.top + rect.height / 2 : innerHeight / 2;
  for (let i = 0; i < 14; i += 1) {
    const node = document.createElement("span");
    node.className = "particle";
    node.style.left = `${x}px`;
    node.style.top = `${y}px`;
    node.style.setProperty("--x", `${(Math.random() - 0.5) * 130}px`);
    node.style.setProperty("--y", `${-30 - Math.random() * 90}px`);
    node.style.background = Math.random() > 0.5 ? "#FAD0C4" : "#FEE180";
    document.body.appendChild(node);
    setTimeout(() => node.remove(), 950);
  }
}

function randomItem(items) {
  return items[Math.floor(Math.random() * items.length)];
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[char]));
}

function escapeAttr(value) {
  return escapeHtml(value).replace(/`/g, "&#096;");
}
