#!/usr/bin/env python3
import io
import json
import math
import mimetypes
import os
import re
import sqlite3
import struct
import sys
import time
import wave
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("DB_PATH", str(ROOT / "app_data.sqlite"))).expanduser()
DB_PATH = DB_PATH if DB_PATH.is_absolute() else ROOT / DB_PATH
DB_PATH = DB_PATH.resolve()
CAPTURE_PATH = ROOT / "prototype-capture.json"

WEBSITE_NAMES = {
    "首页",
    "产品能力",
    "解决方案",
    "案例报告",
    "服务套餐",
    "资源中心",
    "关于我们",
    "预约演示",
}

OASIS_LANGS = {"en": "en", "zh": "zh-CN", "tc": "zh-Hant"}
OASIS_ROUTES = {"today", "sound", "vent", "joy"}
OASIS_PUBLIC_ROUTES = {"today": "today", "sound": "white-noise", "vent": "release", "joy": "joy"}
OASIS_GUIDE_SLUGS = ["digital-hug", "anxiety-breathing", "white-noise", "anonymous-venting", "cozy-web-corner"]
OASIS_AUDIO_ASSETS = {
    "fire": {
        "label": "Woodfire",
        "source_url": "https://assets.mixkit.co/active_storage/sfx/2432/2432-84.wav",
    },
    "cat": {
        "label": "Cat Purr",
        "source_url": "https://upload.wikimedia.org/wikipedia/commons/6/6e/Cat_purring_panting.ogg",
    },
    "rain": {
        "label": "Soft Rain",
        "source_url": "https://assets.mixkit.co/active_storage/sfx/2448/2448-84.wav",
    },
    "leaves": {
        "label": "Autumn Leaves",
        "source_url": "https://assets.mixkit.co/active_storage/sfx/1204/1204-84.wav",
    },
}
OASIS_META = {
    "en": {
        "today": ("Today's Hug - Digital hugs and kind words | OASIS", "Get a gentle micro-moment with warm daily quotes, kind words, and a cozy web corner for stress relief."),
        "sound": ("Sound Oasis - White noise breathing room | OASIS", "Relax with woodfire, cat purr, rain, autumn leaves, and a soft 4-7-8 breathing guide."),
        "vent": ("Cyber Vent - Private worry release | OASIS", "Type worries and release them privately. Nothing is saved. A gentle client-side anxiety relief ritual."),
        "joy": ("Joy Swapper - Anonymous happy moments | OASIS", "Share a tiny happy moment anonymously and receive a stranger's joy in return."),
    },
    "zh": {
        "today": ("今日拥抱 - 温柔句子和数字拥抱 | OASIS", "获得一句温柔话，一个适合放松心情、缓解焦虑、让自己轻一点的小瞬间。"),
        "sound": ("声音绿洲 - 白噪音与呼吸引导 | OASIS", "木火、猫咪呼噜、雨声、秋叶，以及柔和的 4-7-8 呼吸练习。"),
        "vent": ("赛博解压池 - 不保存的私人释放 | OASIS", "写下烦恼并释放，内容不会保存，适合短暂情绪整理和压力缓解。"),
        "joy": ("快乐交换商店 - 匿名交换小开心 | OASIS", "匿名提交一个小小开心，收到陌生人的快乐瞬间。"),
    },
    "tc": {
        "today": ("今日擁抱 - 溫柔句子和數位擁抱 | OASIS", "獲得一句溫柔話，一個適合放鬆心情、緩解焦慮、讓自己輕一點的小瞬間。"),
        "sound": ("聲音綠洲 - 白噪音與呼吸引導 | OASIS", "木火、貓咪呼嚕、雨聲、秋葉，以及柔和的 4-7-8 呼吸練習。"),
        "vent": ("賽博解壓池 - 不保存的私人釋放 | OASIS", "寫下煩惱並釋放，內容不會保存，適合短暫情緒整理和壓力緩解。"),
        "joy": ("快樂交換商店 - 匿名交換小開心 | OASIS", "匿名提交一個小小開心，收到陌生人的快樂瞬間。"),
    },
}


def now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def public_origin(handler):
    host = handler.headers.get("Host") or "localhost:8000"
    proto = "https" if "trycloudflare.com" in host else "http"
    return f"{proto}://{host}"


def oasis_lang_route(path):
    parts = [part for part in path.split("/") if part]
    lang = parts[1] if len(parts) > 1 else "en"
    route = parts[2] if len(parts) > 2 else "today"
    if lang not in OASIS_LANGS:
        lang = "en"
    if route not in OASIS_ROUTES:
        route = "today"
    return lang, route


def oasis_keywords(lang, route):
    keywords = {
        "en": "digital sanctuary, anxiety relief website, cozy web corner, digital hug, white noise breathing, mindful micro break, anonymous joy exchange",
        "zh": "治愈小网站, 放松心情, 缓解焦虑, 数字拥抱, 白噪音呼吸, 情绪解压, 匿名快乐交换",
        "tc": "治癒小網站, 放鬆心情, 緩解焦慮, 數位擁抱, 白噪音呼吸, 情緒解壓, 匿名快樂交換",
    }
    return f"{keywords[lang]}, OASIS, {route}"


def oasis_structured_data(origin, lang, route, title, description):
    return {
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": "OASIS",
        "url": f"{origin}/oasis/{lang}/{route}",
        "applicationCategory": "WellnessApplication",
        "inLanguage": OASIS_LANGS[lang],
        "description": description,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "featureList": ["digital hugs", "white noise breathing", "private venting", "anonymous joy swapping"],
    }


def load_pages():
    with CAPTURE_PATH.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    pages = []
    for page in payload["pages"]:
        page = dict(page)
        page["route"] = f"page-{page['index']}"
        page["group"] = group_for(page)
        pages.append(page)
    return pages


def group_for(page):
    name = page["name"]
    index = int(page["index"])
    if name in WEBSITE_NAMES:
        return "官网"
    if index >= 83:
        return "后台"
    if index >= 44:
        return "管理"
    if index >= 28:
        return "运营"
    return "分析"


def source_for(page):
    name = page["name"]
    group = page["group"]
    if name == "预约演示":
        return {
            "sourceType": "后台表单提交",
            "sourceDetail": "客户在官网预约页提交品牌、联系人和诊断诉求，进入线索表后由运营人员跟进。",
            "ingestOwner": "市场运营",
            "refreshPolicy": "用户提交时实时写入",
            "primaryTables": ["lead_submissions", "cms_pages"],
            "notes": "这类数据不是抓取数据，需要表单、校验、入库和通知链路。",
        }
    if group == "官网":
        return {
            "sourceType": "后台上传/CMS",
            "sourceDetail": "官网文案、案例、套餐、资源文章和关于我们信息由后台 CMS 上传维护。",
            "ingestOwner": "市场运营",
            "refreshPolicy": "人工发布后立即生效",
            "primaryTables": ["cms_pages", "cms_blocks"],
            "notes": "不建议从外部抓取，属于品牌自有内容。",
        }
    if name.startswith("配置_") or name in {"项目配置", "产品管理", "受众人群", "种子配置", "词签管理", "词池发布"}:
        return {
            "sourceType": "后台上传/手动配置",
            "sourceDetail": "品牌、产品、资料来源、竞品、黑白名单、风格套件等由管理员在配置中心录入。",
            "ingestOwner": "品牌管理员",
            "refreshPolicy": "保存配置时实时写入；分析任务读取最新版本",
            "primaryTables": ["project_configs", "products", "seed_terms", "tag_rules"],
            "notes": "这是本次优先打通的数据链路。",
        }
    if name in {"资料来源", "上传文档", "证据片段", "证据详情", "证据片段新增", "补充证据", "图片文件夹", "上传图片", "新建文件夹", "图片详情", "引用来源", "新增引用来源", "确认删除"}:
        return {
            "sourceType": "后台上传+解析",
            "sourceDetail": "原始文档、图片和引用来源由后台上传，再解析为证据片段和可引用来源。",
            "ingestOwner": "知识库管理员",
            "refreshPolicy": "上传后异步解析；审核后对分析和内容创作生效",
            "primaryTables": ["source_documents", "evidence_snippets", "media_assets", "citation_sources"],
            "notes": "不是外部抓取主链路，重点是上传、解析、审核和知识资产绑定。",
        }
    if name in {"知识库", "知识资产", "资产详情", "停用资产", "调整调用", "知识空间", "加入资产", "调用记录"}:
        return {
            "sourceType": "后台沉淀+系统调用日志",
            "sourceDetail": "知识资产来自资料解析、人工补充和内容沉淀；调用记录由系统模块和 Agent 自动写入。",
            "ingestOwner": "知识库系统",
            "refreshPolicy": "资产变更实时写入；调用日志实时追加",
            "primaryTables": ["knowledge_assets", "knowledge_spaces", "knowledge_calls"],
            "notes": "知识资产是上传和人工治理后的结果，调用记录是系统自动产生。",
        }
    if group == "后台":
        return {
            "sourceType": "系统任务+抓取配置",
            "sourceDetail": "后台任务、行业意图和标签树由平台任务调度、行业词库和规则配置生成。",
            "ingestOwner": "平台后台",
            "refreshPolicy": "任务运行后写入；规则发布后生效",
            "primaryTables": ["jobs", "industry_intents", "tag_trees"],
            "notes": "属于后台治理数据，既有系统生成也有运营配置。",
        }
    if group == "运营":
        return {
            "sourceType": "系统生成+后台处理",
            "sourceDetail": "机会、诊断报告、内容需求和内容创作来自监测结果计算，也由运营人员确认、编辑和发布。",
            "ingestOwner": "运营系统",
            "refreshPolicy": "监测批次完成后生成；人工处理状态实时更新",
            "primaryTables": ["opportunities", "diagnostic_reports", "content_requests", "contents"],
            "notes": "上游是抓取和监测，下游是后台人工处理。",
        }
    return {
        "sourceType": "AI平台抓取/监测任务",
        "sourceDetail": "通过 Prompt 任务从豆包、Kimi、DeepSeek 等 AI 平台采集回答、引用、品牌提及和风险结果。",
        "ingestOwner": "监测任务",
        "refreshPolicy": "按批次采集，通常每日或按项目手动触发",
        "primaryTables": ["crawl_batches", "answer_samples", "visibility_metrics", "risk_findings"],
        "notes": "这些页面的核心数据应来自抓取与指标计算，不应由人工直接填写。",
    }


def default_config(section, page_name):
    base = {
        "企业名称": "桂龙药业（安徽）有限公司",
        "品牌名称": "慢严舒柠",
        "产品名称": "慢严舒柠清喉利咽颗粒",
        "项目类型": "OTC / 中成药 GEO 监测",
        "监测平台": "豆包、Kimi、DeepSeek、通义千问、文心一言",
        "主要竞品": "蓝芩口服液、蒲地蓝消炎口服液",
        "品牌语气": "专业、严谨、易懂",
        "补充说明": "用于保证 AI 分析、内容创作和知识调用时能够准确识别品牌边界。",
    }
    if "资料来源" in page_name:
        base.update({"资料名称": "慢严舒柠品牌手册_v3.pdf", "解析状态": "已解析", "可信等级": "高"})
    if "名称" in page_name:
        base.update({"标准名称": "慢严舒柠", "常见别名": "慢严舒柠颗粒、清喉利咽颗粒", "错别字": "慢严舒宁"})
    if "官网" in page_name:
        base.update({"官网地址": "https://example.com", "公众号": "桂龙药业", "电商渠道": "天猫、京东、抖音"})
    if "竞品" in page_name:
        base.update({"竞品品牌": "蓝芩口服液", "竞品类型": "咽喉用药", "监测优先级": "P0"})
    if "黑白" in page_name:
        base.update({"白名单": "官网、说明书、品牌手册", "黑名单": "未经验证的偏方、低可信论坛"})
    if "品牌资产" in page_name:
        base.update({"资产范围": "品牌定位、产品说明、FAQ、合规表达", "审核状态": "已审核"})
    if "风格" in page_name:
        base.update({"表达风格": "专业但通俗", "禁用表达": "绝对疗效、保证治愈", "适用平台": "官网、公众号、知乎"})
    if "检查" in page_name:
        base.update({"配置完整度": "92%", "待补充项": "竞品证据、特殊人群安全边界"})
    return base


def default_document_content():
    return (
        "慢严舒柠清喉利咽颗粒用于咽喉不适、声音嘶哑、咽干咽痛等场景的品牌知识整理。"
        "资料来源包含品牌手册、产品说明、官网内容和已审核的合规表达。"
        "在 AI 问答监测中，知识库优先引用高可信来源，避免使用未经验证的偏方和低可信论坛内容。"
    )


def split_snippets(content):
    text = re.sub(r"\s+", " ", content or "").strip()
    if not text:
        return []
    parts = [part.strip(" ,，;；") for part in re.split(r"[。！？!?]\s*|\n+", text) if part.strip()]
    snippets = []
    for part in parts:
        if len(part) < 14:
            continue
        snippets.append(part[:180])
        if len(snippets) >= 5:
            break
    if not snippets:
        snippets.append(text[:180])
    return snippets


def tags_for(text):
    tag_map = [
        ("慢严舒柠", "品牌"),
        ("清喉", "产品功效"),
        ("咽喉", "咽喉健康"),
        ("竞品", "竞品"),
        ("官网", "官网渠道"),
        ("合规", "合规表达"),
        ("引用", "引用来源"),
    ]
    tags = [tag for keyword, tag in tag_map if keyword in text]
    return "、".join(tags[:3] or ["知识资产"])


def seed_knowledge(conn):
    exists = conn.execute("SELECT COUNT(*) FROM source_documents").fetchone()[0]
    if exists:
        return
    created_at = now_iso()
    content = default_document_content()
    cur = conn.execute(
        """
        INSERT INTO source_documents (title, source_type, trust_level, file_name, content, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ("慢严舒柠品牌手册", "品牌上传资料", "高", "brand-manual-demo.txt", content, "已解析", created_at),
    )
    document_id = cur.lastrowid
    for index, snippet in enumerate(split_snippets(content), start=1):
        conn.execute(
            """
            INSERT INTO evidence_snippets (document_id, title, content, tags, trust_level, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (document_id, f"品牌手册片段 {index}", snippet, tags_for(snippet), "高", "已审核", created_at),
        )
    conn.execute(
        """
        INSERT INTO citation_sources (title, url, source_type, owner, trust_level, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "慢严舒柠官网",
            "https://example.com",
            "官网",
            "品牌管理员",
            "高",
            "作为官网渠道和品牌资料引用来源的占位记录，可在引用来源页修改或新增。",
            created_at,
        ),
    )


def default_image_data():
    return (
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='480' height='320' viewBox='0 0 480 320'%3E"
        "%3Crect width='480' height='320' fill='%23f0fdfa'/%3E"
        "%3Crect x='36' y='36' width='408' height='248' rx='18' fill='white' stroke='%2399f6e4'/%3E"
        "%3Ccircle cx='142' cy='132' r='46' fill='%230d9488'/%3E"
        "%3Crect x='206' y='102' width='156' height='18' rx='9' fill='%232563eb'/%3E"
        "%3Crect x='206' y='142' width='118' height='14' rx='7' fill='%2394a3b8'/%3E"
        "%3Crect x='86' y='218' width='292' height='22' rx='11' fill='%23ccfbf1'/%3E"
        "%3Ctext x='240' y='174' text-anchor='middle' font-size='30' font-family='Arial' fill='%230f172a'%3EZJ%3C/text%3E"
        "%3C/svg%3E"
    )


def seed_media(conn):
    if conn.execute("SELECT COUNT(*) FROM media_folders").fetchone()[0]:
        return
    created_at = now_iso()
    cur = conn.execute(
        "INSERT INTO media_folders (name, description, created_at) VALUES (?, ?, ?)",
        ("品牌素材", "官网、内容创作和 AI 回答引用时可用的品牌图片。", created_at),
    )
    folder_id = cur.lastrowid
    conn.execute(
        """
        INSERT INTO media_assets (folder_id, title, file_name, mime_type, data_url, alt_text, tags, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            folder_id,
            "品牌视觉占位图",
            "brand-visual-demo.svg",
            "image/svg+xml",
            default_image_data(),
            "智荐品牌素材占位图",
            "品牌、官网、内容创作",
            "已审核",
            created_at,
        ),
    )


def seed_assets(conn):
    if conn.execute("SELECT COUNT(*) FROM knowledge_spaces").fetchone()[0] == 0:
        conn.execute(
            "INSERT INTO knowledge_spaces (name, description, status, created_at) VALUES (?, ?, ?, ?)",
            ("默认知识空间", "承载品牌资料、证据片段、引用来源和内容创作调用。", "启用", now_iso()),
        )
    if conn.execute("SELECT COUNT(*) FROM knowledge_assets").fetchone()[0]:
        return
    created_at = now_iso()
    snippet = conn.execute(
        "SELECT id, title, content, trust_level FROM evidence_snippets ORDER BY id LIMIT 1"
    ).fetchone()
    if snippet:
        asset_cur = conn.execute(
            """
            INSERT INTO knowledge_assets (source_type, source_id, title, content, trust_level, status, usage_count, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("evidence_snippet", snippet[0], snippet[1], snippet[2], snippet[3], "启用", 1, created_at),
        )
        conn.execute(
            """
            INSERT INTO knowledge_calls (asset_id, caller, purpose, result, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (asset_cur.lastrowid, "内容创作", "生成品牌问答素材", "调用成功：返回 1 条高可信证据。", created_at),
        )


def generated_answer(platform, prompt):
    return (
        f"{platform} 对“{prompt}”的监测样本：建议优先核对症状场景、用药边界和资料来源。"
        "慢严舒柠在咽喉不适、声音嘶哑等场景中具备较高品牌可见性，回答应引用官网、品牌手册和已审核证据片段。"
    )


def insert_monitor_run(conn, task_id, task_name, platforms, prompts):
    created_at = now_iso()
    batch_cur = conn.execute(
        "INSERT INTO crawl_batches (task_id, status, created_at, finished_at) VALUES (?, ?, ?, ?)",
        (task_id, "已完成", created_at, created_at),
    )
    batch_id = batch_cur.lastrowid
    rows = []
    for prompt_index, prompt in enumerate(prompts):
        for platform_index, platform in enumerate(platforms):
            brand_mentioned = 1 if (prompt_index + platform_index) % 4 != 1 else 0
            position = 1 + ((prompt_index + platform_index) % 5) if brand_mentioned else 0
            risk_level = "高" if "特殊人群" in prompt or "禁忌" in prompt else ("中" if platform_index % 3 == 0 else "低")
            citations = "官网、品牌手册" if brand_mentioned else "未识别"
            cur = conn.execute(
                """
                INSERT INTO answer_samples (
                    batch_id, task_id, platform, prompt, answer, brand_mentioned, position,
                    citations, risk_level, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    batch_id,
                    task_id,
                    platform,
                    prompt,
                    generated_answer(platform, prompt),
                    brand_mentioned,
                    position,
                    citations,
                    risk_level,
                    created_at,
                ),
            )
            rows.append(cur.lastrowid)
            if risk_level in {"中", "高"}:
                conn.execute(
                    """
                    INSERT INTO risk_findings (sample_id, title, detail, severity, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        cur.lastrowid,
                        f"{platform} 风险复核",
                        f"Prompt“{prompt}”需要复核用药边界、引用来源和合规表达。",
                        risk_level,
                        "待处理",
                        created_at,
                    ),
                )
    conn.execute(
        "UPDATE monitor_tasks SET status = ?, last_run_at = ? WHERE id = ?",
        ("已完成", created_at, task_id),
    )
    return batch_id, rows


def seed_monitoring(conn):
    if conn.execute("SELECT COUNT(*) FROM monitor_tasks").fetchone()[0]:
        return
    created_at = now_iso()
    platforms = ["豆包", "Kimi", "DeepSeek"]
    prompts = ["慢性咽炎反复不适怎么办", "清喉利咽颗粒和竞品怎么选", "特殊人群用药要注意什么"]
    cur = conn.execute(
        """
        INSERT INTO monitor_tasks (name, platforms, prompts, schedule, status, created_at, last_run_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        ("咽喉健康场景监测", json.dumps(platforms, ensure_ascii=False), json.dumps(prompts, ensure_ascii=False), "每日", "待运行", created_at, ""),
    )
    insert_monitor_run(conn, cur.lastrowid, "咽喉健康场景监测", platforms, prompts)


def seed_oasis(conn):
    if conn.execute("SELECT COUNT(*) FROM oasis_joy_entries").fetchone()[0]:
        return
    created_at = now_iso()
    entries = [
        ("en", "A stranger held the elevator and smiled like they had all the time in the world."),
        ("en", "The first sip of tea was exactly the right temperature."),
        ("en", "A patch of sunlight landed on my notebook and stayed there."),
        ("zh", "今天路过一家面包店，刚好闻到热面包出炉的味道。"),
        ("zh", "有人很认真地听我把一句话说完。"),
        ("zh", "午后的光落在杯子边缘，看起来像一个小小的奖励。"),
        ("tc", "今天路過一家麵包店，剛好聞到熱麵包出爐的味道。"),
        ("tc", "有人很認真地聽我把一句話說完。"),
        ("tc", "午後的光落在杯子邊緣，看起來像一個小小的獎勵。"),
    ]
    conn.executemany(
        "INSERT INTO oasis_joy_entries (lang, text, created_at) VALUES (?, ?, ?)",
        [(lang, text, created_at) for lang, text in entries],
    )


def seeded_noise(seed):
    state = seed & 0x7FFFFFFF

    def next_value():
        nonlocal state
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        return (state / 0x7FFFFFFF) * 2 - 1

    return next_value


def generate_oasis_audio(sound_key, seconds=4, sample_rate=22050):
    total = sample_rate * seconds
    rand = seeded_noise(sum(ord(char) for char in sound_key) * 97)
    output = io.BytesIO()
    with wave.open(output, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        frames = bytearray()
        fire_decay = 0.0
        leaf_decay = 0.0
        rain_smooth = 0.0
        for index in range(total):
            t = index / sample_rate
            noise = rand()
            if sound_key == "cat":
                purr_gate = 0.65 + 0.35 * math.sin(2 * math.pi * 11.2 * t)
                sample = (
                    math.sin(2 * math.pi * 72 * t)
                    + 0.46 * math.sin(2 * math.pi * 86 * t)
                    + 0.16 * math.sin(2 * math.pi * 144 * t)
                ) * 0.105 * purr_gate
            elif sound_key == "rain":
                rain_smooth = rain_smooth * 0.82 + noise * 0.18
                sample = rain_smooth * 0.26 + rand() * 0.035
            elif sound_key == "leaves":
                if rand() > 0.965:
                    leaf_decay = 0.42 + abs(rand()) * 0.32
                leaf_decay *= 0.985
                sample = noise * leaf_decay * 0.38 + rand() * 0.015
            else:
                if rand() > 0.989:
                    fire_decay = 0.62 + abs(rand()) * 0.35
                fire_decay *= 0.975
                ember = math.sin(2 * math.pi * 145 * t) * 0.018
                sample = noise * (0.035 + fire_decay * 0.34) + ember
            sample = max(-0.88, min(0.88, sample))
            frames.extend(struct.pack("<h", int(sample * 32767)))
        wav.writeframes(bytes(frames))
    return output.getvalue()


def seed_oasis_audio(conn):
    created_at = now_iso()
    for sound_key, meta in OASIS_AUDIO_ASSETS.items():
        exists = conn.execute(
            "SELECT 1 FROM oasis_audio_assets WHERE sound_key = ?",
            (sound_key,),
        ).fetchone()
        if exists:
            continue
        conn.execute(
            """
            INSERT INTO oasis_audio_assets (
                sound_key, label, source_url, mime_type, data, storage_note, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sound_key,
                meta["label"],
                meta["source_url"],
                "audio/wav",
                sqlite3.Binary(generate_oasis_audio(sound_key)),
                "Stored in SQLite as a self-contained generated loop because the original external demo URLs were unavailable.",
                created_at,
                created_at,
            ),
        )


def init_db():
    pages = load_pages()
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS data_sources (
                route TEXT PRIMARY KEY,
                page_index INTEGER NOT NULL,
                page_name TEXT NOT NULL,
                group_name TEXT NOT NULL,
                source_type TEXT NOT NULL,
                source_detail TEXT NOT NULL,
                ingest_owner TEXT NOT NULL,
                refresh_policy TEXT NOT NULL,
                primary_tables TEXT NOT NULL,
                notes TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS project_configs (
                section TEXT PRIMARY KEY,
                page_name TEXT NOT NULL,
                payload TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS lead_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS source_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                source_type TEXT NOT NULL,
                trust_level TEXT NOT NULL,
                file_name TEXT NOT NULL,
                content TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS evidence_snippets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT NOT NULL,
                trust_level TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS citation_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                source_type TEXT NOT NULL,
                owner TEXT NOT NULL,
                trust_level TEXT NOT NULL,
                notes TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS media_folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS media_assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folder_id INTEGER,
                title TEXT NOT NULL,
                file_name TEXT NOT NULL,
                mime_type TEXT NOT NULL,
                data_url TEXT NOT NULL,
                alt_text TEXT NOT NULL,
                tags TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge_spaces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge_assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_type TEXT NOT NULL,
                source_id INTEGER,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                trust_level TEXT NOT NULL,
                status TEXT NOT NULL,
                usage_count INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id INTEGER,
                caller TEXT NOT NULL,
                purpose TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS monitor_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                platforms TEXT NOT NULL,
                prompts TEXT NOT NULL,
                schedule TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_run_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS crawl_batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                finished_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS answer_samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id INTEGER,
                task_id INTEGER,
                platform TEXT NOT NULL,
                prompt TEXT NOT NULL,
                answer TEXT NOT NULL,
                brand_mentioned INTEGER NOT NULL,
                position INTEGER NOT NULL,
                citations TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS risk_findings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sample_id INTEGER,
                title TEXT NOT NULL,
                detail TEXT NOT NULL,
                severity TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS oasis_joy_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lang TEXT NOT NULL,
                text TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS oasis_audio_assets (
                sound_key TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                source_url TEXT NOT NULL,
                mime_type TEXT NOT NULL,
                data BLOB NOT NULL,
                storage_note TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        for page in pages:
            source = source_for(page)
            conn.execute(
                """
                INSERT INTO data_sources (
                    route, page_index, page_name, group_name, source_type, source_detail,
                    ingest_owner, refresh_policy, primary_tables, notes, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(route) DO UPDATE SET
                    page_index=excluded.page_index,
                    page_name=excluded.page_name,
                    group_name=excluded.group_name,
                    source_type=excluded.source_type,
                    source_detail=excluded.source_detail,
                    ingest_owner=excluded.ingest_owner,
                    refresh_policy=excluded.refresh_policy,
                    primary_tables=excluded.primary_tables,
                    notes=excluded.notes,
                    updated_at=excluded.updated_at
                """,
                (
                    page["route"],
                    page["index"],
                    page["name"],
                    page["group"],
                    source["sourceType"],
                    source["sourceDetail"],
                    source["ingestOwner"],
                    source["refreshPolicy"],
                    json.dumps(source["primaryTables"], ensure_ascii=False),
                    source["notes"],
                    now_iso(),
                ),
            )
            if page["name"].startswith("配置_"):
                section = section_for_page(page)
                exists = conn.execute("SELECT 1 FROM project_configs WHERE section = ?", (section,)).fetchone()
                if not exists:
                    conn.execute(
                        "INSERT INTO project_configs (section, page_name, payload, updated_at) VALUES (?, ?, ?, ?)",
                        (
                            section,
                            page["name"],
                            json.dumps(default_config(section, page["name"]), ensure_ascii=False),
                            now_iso(),
                        ),
                    )
        seed_knowledge(conn)
        seed_media(conn)
        seed_assets(conn)
        seed_monitoring(conn)
        seed_oasis(conn)
        seed_oasis_audio(conn)
        conn.commit()


def section_for_page(page):
    return f"page-{page['index']}"


def db_row_to_source(row):
    return {
        "route": row[0],
        "pageIndex": row[1],
        "pageName": row[2],
        "group": row[3],
        "sourceType": row[4],
        "sourceDetail": row[5],
        "ingestOwner": row[6],
        "refreshPolicy": row[7],
        "primaryTables": json.loads(row[8]),
        "notes": row[9],
        "updatedAt": row[10],
    }


def db_row_to_document(row):
    return {
        "id": row[0],
        "title": row[1],
        "sourceType": row[2],
        "trustLevel": row[3],
        "fileName": row[4],
        "content": row[5],
        "status": row[6],
        "createdAt": row[7],
    }


def db_row_to_snippet(row):
    return {
        "id": row[0],
        "documentId": row[1],
        "title": row[2],
        "content": row[3],
        "tags": row[4],
        "trustLevel": row[5],
        "status": row[6],
        "createdAt": row[7],
        "documentTitle": row[8] if len(row) > 8 else "",
    }


def db_row_to_citation(row):
    return {
        "id": row[0],
        "title": row[1],
        "url": row[2],
        "sourceType": row[3],
        "owner": row[4],
        "trustLevel": row[5],
        "notes": row[6],
        "createdAt": row[7],
    }


def db_row_to_folder(row):
    return {"id": row[0], "name": row[1], "description": row[2], "createdAt": row[3], "assetCount": row[4] if len(row) > 4 else 0}


def db_row_to_media(row):
    return {
        "id": row[0],
        "folderId": row[1],
        "title": row[2],
        "fileName": row[3],
        "mimeType": row[4],
        "dataUrl": row[5],
        "altText": row[6],
        "tags": row[7],
        "status": row[8],
        "createdAt": row[9],
        "folderName": row[10] if len(row) > 10 else "",
    }


def db_row_to_asset(row):
    return {
        "id": row[0],
        "sourceType": row[1],
        "sourceId": row[2],
        "title": row[3],
        "content": row[4],
        "trustLevel": row[5],
        "status": row[6],
        "usageCount": row[7],
        "createdAt": row[8],
    }


def db_row_to_space(row):
    return {"id": row[0], "name": row[1], "description": row[2], "status": row[3], "createdAt": row[4]}


def db_row_to_call(row):
    return {
        "id": row[0],
        "assetId": row[1],
        "caller": row[2],
        "purpose": row[3],
        "result": row[4],
        "createdAt": row[5],
        "assetTitle": row[6] if len(row) > 6 else "",
    }


def db_row_to_task(row):
    return {
        "id": row[0],
        "name": row[1],
        "platforms": json.loads(row[2]),
        "prompts": json.loads(row[3]),
        "schedule": row[4],
        "status": row[5],
        "createdAt": row[6],
        "lastRunAt": row[7],
    }


def db_row_to_sample(row):
    return {
        "id": row[0],
        "batchId": row[1],
        "taskId": row[2],
        "platform": row[3],
        "prompt": row[4],
        "answer": row[5],
        "brandMentioned": bool(row[6]),
        "position": row[7],
        "citations": row[8],
        "riskLevel": row[9],
        "createdAt": row[10],
        "taskName": row[11] if len(row) > 11 else "",
    }


def db_row_to_risk(row):
    return {
        "id": row[0],
        "sampleId": row[1],
        "title": row[2],
        "detail": row[3],
        "severity": row[4],
        "status": row[5],
        "createdAt": row[6],
    }


def parse_list(value, fallback):
    if isinstance(value, list):
        items = value
    else:
        items = re.split(r"[\n,，、]+", str(value or ""))
    cleaned = [str(item).strip() for item in items if str(item).strip()]
    return cleaned or fallback


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stdout.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))

    def do_OPTIONS(self):
        self.send_response(204)
        self.add_cors()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if path == "/api/health":
            return self.send_json({"ok": True, "db": str(DB_PATH.name), "time": now_iso()})
        if path == "/robots.txt":
            return self.handle_robots()
        if path == "/sitemap.xml":
            return self.handle_root_sitemap()
        if path == "/oasis/sitemap.xml":
            return self.handle_oasis_sitemap()
        if path == "/api/data-sources":
            return self.handle_data_sources()
        if path == "/api/knowledge":
            return self.handle_knowledge()
        if path == "/api/media":
            return self.handle_media()
        if path == "/api/assets":
            return self.handle_assets()
        if path == "/api/monitoring":
            return self.handle_monitoring()
        if path.startswith("/api/oasis/audio/"):
            return self.handle_oasis_audio(path.rsplit("/", 1)[-1])
        if path == "/api/oasis/joy":
            return self.handle_oasis_joy(parsed.query)
        if path.startswith("/api/config/"):
            return self.handle_get_config(path.rsplit("/", 1)[-1])
        return self.serve_static(path)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if path.startswith("/api/config/"):
            return self.handle_save_config(path.rsplit("/", 1)[-1])
        if path == "/api/leads":
            return self.handle_lead()
        if path == "/api/documents":
            return self.handle_document()
        if path == "/api/evidence-snippets":
            return self.handle_snippet()
        if path == "/api/citation-sources":
            return self.handle_citation()
        if path == "/api/media-folders":
            return self.handle_media_folder()
        if path == "/api/media-assets":
            return self.handle_media_asset()
        if path == "/api/knowledge-assets":
            return self.handle_knowledge_asset()
        if path == "/api/knowledge-calls":
            return self.handle_knowledge_call()
        if path == "/api/monitor-tasks":
            return self.handle_monitor_task()
        if path == "/api/oasis/joy":
            return self.handle_oasis_joy_save()
        return self.send_json({"error": "not found"}, 404)

    def add_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.add_cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_text(self, body, content_type="text/plain; charset=utf-8", status=200):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def handle_robots(self):
        origin = public_origin(self)
        self.send_text(
            "\n".join(
                [
                    "User-agent: *",
                    "Allow: /",
                    "Disallow: /api/",
                    "Disallow: /admin/",
                    "Disallow: /scripts/",
                    "Disallow: /supabase/",
                    "",
                    f"Sitemap: {origin}/sitemap.xml",
                    "",
                ]
            )
        )

    def handle_root_sitemap(self):
        origin = public_origin(self)
        body = "\n".join(
            [
                '<?xml version="1.0" encoding="UTF-8"?>',
                '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
                "  <sitemap>",
                f"    <loc>{origin}/oasis/sitemap.xml</loc>",
                "  </sitemap>",
                "</sitemapindex>",
                "",
            ]
        )
        self.send_text(body, "application/xml; charset=utf-8")

    def handle_oasis_sitemap(self):
        origin = public_origin(self)
        urls = []
        for lang in OASIS_LANGS:
            for route in sorted(OASIS_ROUTES):
                urls.append((f"{origin}/oasis/{lang}/{OASIS_PUBLIC_ROUTES[route]}", "0.8"))
            for slug in OASIS_GUIDE_SLUGS:
                urls.append((f"{origin}/oasis/{lang}/guide/{slug}", "0.7"))
        body = "\n".join(
            [
                '<?xml version="1.0" encoding="UTF-8"?>',
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
                *[f"  <url><loc>{url}</loc><changefreq>weekly</changefreq><priority>{priority}</priority></url>" for url, priority in urls],
                "</urlset>",
                "",
            ]
        )
        self.send_text(body, "application/xml; charset=utf-8")

    def read_json(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def handle_data_sources(self):
        with sqlite3.connect(DB_PATH) as conn:
            rows = conn.execute(
                """
                SELECT route, page_index, page_name, group_name, source_type, source_detail,
                       ingest_owner, refresh_policy, primary_tables, notes, updated_at
                FROM data_sources
                ORDER BY page_index
                """
            ).fetchall()
        sources = [db_row_to_source(row) for row in rows]
        self.send_json({"items": sources, "byRoute": {item["route"]: item for item in sources}})

    def handle_knowledge(self):
        with sqlite3.connect(DB_PATH) as conn:
            doc_rows = conn.execute(
                """
                SELECT id, title, source_type, trust_level, file_name, content, status, created_at
                FROM source_documents
                ORDER BY id DESC
                LIMIT 30
                """
            ).fetchall()
            snippet_rows = conn.execute(
                """
                SELECT s.id, s.document_id, s.title, s.content, s.tags, s.trust_level, s.status,
                       s.created_at, COALESCE(d.title, '')
                FROM evidence_snippets s
                LEFT JOIN source_documents d ON d.id = s.document_id
                ORDER BY s.id DESC
                LIMIT 50
                """
            ).fetchall()
            citation_rows = conn.execute(
                """
                SELECT id, title, url, source_type, owner, trust_level, notes, created_at
                FROM citation_sources
                ORDER BY id DESC
                LIMIT 30
                """
            ).fetchall()
            stats = {
                "documents": conn.execute("SELECT COUNT(*) FROM source_documents").fetchone()[0],
                "snippets": conn.execute("SELECT COUNT(*) FROM evidence_snippets").fetchone()[0],
                "citations": conn.execute("SELECT COUNT(*) FROM citation_sources").fetchone()[0],
                "highTrust": conn.execute(
                    "SELECT COUNT(*) FROM source_documents WHERE trust_level IN ('高', '高可信')"
                ).fetchone()[0],
            }
        self.send_json(
            {
                "documents": [db_row_to_document(row) for row in doc_rows],
                "snippets": [db_row_to_snippet(row) for row in snippet_rows],
                "citations": [db_row_to_citation(row) for row in citation_rows],
                "stats": stats,
            }
        )

    def handle_document(self):
        data = self.read_json()
        title = (data.get("title") or data.get("fileName") or "未命名资料").strip()
        source_type = data.get("sourceType") or "后台上传资料"
        trust_level = data.get("trustLevel") or "中"
        file_name = data.get("fileName") or ""
        content = (data.get("content") or "").strip()
        if not content:
            content = f"{title}：资料已登记，等待补充正文或解析结果。"
        created_at = now_iso()
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute(
                """
                INSERT INTO source_documents (title, source_type, trust_level, file_name, content, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (title, source_type, trust_level, file_name, content[:20000], "已解析", created_at),
            )
            document_id = cur.lastrowid
            snippets = []
            for index, snippet in enumerate(split_snippets(content), start=1):
                snippet_title = f"{title}片段 {index}"
                row = (
                    document_id,
                    snippet_title,
                    snippet,
                    tags_for(snippet),
                    trust_level,
                    "待审核",
                    created_at,
                )
                snippet_cur = conn.execute(
                    """
                    INSERT INTO evidence_snippets (document_id, title, content, tags, trust_level, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    row,
                )
                snippets.append(
                    {
                        "id": snippet_cur.lastrowid,
                        "documentId": document_id,
                        "title": snippet_title,
                        "content": snippet,
                        "tags": tags_for(snippet),
                        "trustLevel": trust_level,
                        "status": "待审核",
                        "createdAt": created_at,
                        "documentTitle": title,
                    }
                )
            conn.commit()
        self.send_json(
            {
                "ok": True,
                "document": {
                    "id": document_id,
                    "title": title,
                    "sourceType": source_type,
                    "trustLevel": trust_level,
                    "fileName": file_name,
                    "content": content[:20000],
                    "status": "已解析",
                    "createdAt": created_at,
                },
                "snippets": snippets,
            }
        )

    def handle_snippet(self):
        data = self.read_json()
        title = (data.get("title") or "手动补充证据").strip()
        content = (data.get("content") or "").strip()
        if not content:
            return self.send_json({"error": "content required"}, 400)
        trust_level = data.get("trustLevel") or "中"
        tags = data.get("tags") or tags_for(content)
        created_at = now_iso()
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute(
                """
                INSERT INTO evidence_snippets (document_id, title, content, tags, trust_level, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (data.get("documentId"), title, content[:2000], tags, trust_level, "待审核", created_at),
            )
            conn.commit()
            snippet_id = cur.lastrowid
        self.send_json(
            {
                "ok": True,
                "snippet": {
                    "id": snippet_id,
                    "documentId": data.get("documentId"),
                    "title": title,
                    "content": content[:2000],
                    "tags": tags,
                    "trustLevel": trust_level,
                    "status": "待审核",
                    "createdAt": created_at,
                    "documentTitle": "",
                },
            }
        )

    def handle_citation(self):
        data = self.read_json()
        title = (data.get("title") or "未命名引用来源").strip()
        url = (data.get("url") or "").strip()
        source_type = data.get("sourceType") or "官网"
        owner = data.get("owner") or "品牌管理员"
        trust_level = data.get("trustLevel") or "中"
        notes = data.get("notes") or ""
        created_at = now_iso()
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute(
                """
                INSERT INTO citation_sources (title, url, source_type, owner, trust_level, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (title, url, source_type, owner, trust_level, notes, created_at),
            )
            conn.commit()
            citation_id = cur.lastrowid
        self.send_json(
            {
                "ok": True,
                "citation": {
                    "id": citation_id,
                    "title": title,
                    "url": url,
                    "sourceType": source_type,
                    "owner": owner,
                    "trustLevel": trust_level,
                    "notes": notes,
                    "createdAt": created_at,
                },
            }
        )

    def handle_media(self):
        with sqlite3.connect(DB_PATH) as conn:
            folder_rows = conn.execute(
                """
                SELECT f.id, f.name, f.description, f.created_at, COUNT(a.id)
                FROM media_folders f
                LEFT JOIN media_assets a ON a.folder_id = f.id
                GROUP BY f.id
                ORDER BY f.id DESC
                """
            ).fetchall()
            asset_rows = conn.execute(
                """
                SELECT a.id, a.folder_id, a.title, a.file_name, a.mime_type, a.data_url,
                       a.alt_text, a.tags, a.status, a.created_at, COALESCE(f.name, '')
                FROM media_assets a
                LEFT JOIN media_folders f ON f.id = a.folder_id
                ORDER BY a.id DESC
                LIMIT 40
                """
            ).fetchall()
            stats = {
                "folders": conn.execute("SELECT COUNT(*) FROM media_folders").fetchone()[0],
                "assets": conn.execute("SELECT COUNT(*) FROM media_assets").fetchone()[0],
                "approved": conn.execute("SELECT COUNT(*) FROM media_assets WHERE status = '已审核'").fetchone()[0],
            }
        self.send_json(
            {
                "folders": [db_row_to_folder(row) for row in folder_rows],
                "assets": [db_row_to_media(row) for row in asset_rows],
                "stats": stats,
            }
        )

    def handle_media_folder(self):
        data = self.read_json()
        name = (data.get("name") or "新建文件夹").strip()
        description = data.get("description") or ""
        created_at = now_iso()
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute(
                "INSERT INTO media_folders (name, description, created_at) VALUES (?, ?, ?)",
                (name, description, created_at),
            )
            conn.commit()
            folder_id = cur.lastrowid
        self.send_json({"ok": True, "folder": {"id": folder_id, "name": name, "description": description, "createdAt": created_at, "assetCount": 0}})

    def handle_media_asset(self):
        data = self.read_json()
        title = (data.get("title") or data.get("fileName") or "未命名图片").strip()
        file_name = data.get("fileName") or ""
        mime_type = data.get("mimeType") or "image/svg+xml"
        data_url = data.get("dataUrl") or default_image_data()
        alt_text = data.get("altText") or title
        tags = data.get("tags") or "品牌素材"
        created_at = now_iso()
        with sqlite3.connect(DB_PATH) as conn:
            folder_id = data.get("folderId")
            if not folder_id:
                row = conn.execute("SELECT id FROM media_folders ORDER BY id LIMIT 1").fetchone()
                folder_id = row[0] if row else None
            cur = conn.execute(
                """
                INSERT INTO media_assets (folder_id, title, file_name, mime_type, data_url, alt_text, tags, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (folder_id, title, file_name, mime_type, data_url, alt_text, tags, "待审核", created_at),
            )
            conn.commit()
            asset_id = cur.lastrowid
        self.send_json(
            {
                "ok": True,
                "asset": {
                    "id": asset_id,
                    "folderId": folder_id,
                    "title": title,
                    "fileName": file_name,
                    "mimeType": mime_type,
                    "dataUrl": data_url,
                    "altText": alt_text,
                    "tags": tags,
                    "status": "待审核",
                    "createdAt": created_at,
                },
            }
        )

    def handle_assets(self):
        with sqlite3.connect(DB_PATH) as conn:
            space_rows = conn.execute(
                "SELECT id, name, description, status, created_at FROM knowledge_spaces ORDER BY id DESC"
            ).fetchall()
            asset_rows = conn.execute(
                """
                SELECT id, source_type, source_id, title, content, trust_level, status, usage_count, created_at
                FROM knowledge_assets
                ORDER BY id DESC
                LIMIT 50
                """
            ).fetchall()
            call_rows = conn.execute(
                """
                SELECT c.id, c.asset_id, c.caller, c.purpose, c.result, c.created_at, COALESCE(a.title, '')
                FROM knowledge_calls c
                LEFT JOIN knowledge_assets a ON a.id = c.asset_id
                ORDER BY c.id DESC
                LIMIT 40
                """
            ).fetchall()
            stats = {
                "spaces": conn.execute("SELECT COUNT(*) FROM knowledge_spaces").fetchone()[0],
                "assets": conn.execute("SELECT COUNT(*) FROM knowledge_assets").fetchone()[0],
                "enabled": conn.execute("SELECT COUNT(*) FROM knowledge_assets WHERE status = '启用'").fetchone()[0],
                "calls": conn.execute("SELECT COUNT(*) FROM knowledge_calls").fetchone()[0],
            }
        self.send_json(
            {
                "spaces": [db_row_to_space(row) for row in space_rows],
                "assets": [db_row_to_asset(row) for row in asset_rows],
                "calls": [db_row_to_call(row) for row in call_rows],
                "stats": stats,
            }
        )

    def handle_knowledge_asset(self):
        data = self.read_json()
        created_at = now_iso()
        with sqlite3.connect(DB_PATH) as conn:
            snippet_id = data.get("sourceId")
            snippet = None
            if snippet_id:
                snippet = conn.execute(
                    "SELECT id, title, content, trust_level FROM evidence_snippets WHERE id = ?",
                    (snippet_id,),
                ).fetchone()
            if not snippet and not data.get("content"):
                snippet = conn.execute(
                    "SELECT id, title, content, trust_level FROM evidence_snippets ORDER BY id DESC LIMIT 1"
                ).fetchone()
            source_type = "manual"
            source_id = data.get("sourceId")
            title = data.get("title") or "手动知识资产"
            content = data.get("content") or ""
            trust_level = data.get("trustLevel") or "中"
            if snippet:
                source_type = "evidence_snippet"
                source_id = snippet[0]
                title = data.get("title") or snippet[1]
                content = data.get("content") or snippet[2]
                trust_level = data.get("trustLevel") or snippet[3]
            cur = conn.execute(
                """
                INSERT INTO knowledge_assets (source_type, source_id, title, content, trust_level, status, usage_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (source_type, source_id, title, content[:4000], trust_level, "启用", 0, created_at),
            )
            conn.commit()
            asset_id = cur.lastrowid
        self.send_json(
            {
                "ok": True,
                "asset": {
                    "id": asset_id,
                    "sourceType": source_type,
                    "sourceId": source_id,
                    "title": title,
                    "content": content[:4000],
                    "trustLevel": trust_level,
                    "status": "启用",
                    "usageCount": 0,
                    "createdAt": created_at,
                },
            }
        )

    def handle_knowledge_call(self):
        data = self.read_json()
        created_at = now_iso()
        with sqlite3.connect(DB_PATH) as conn:
            asset_id = data.get("assetId")
            if not asset_id:
                row = conn.execute("SELECT id FROM knowledge_assets WHERE status = '启用' ORDER BY id DESC LIMIT 1").fetchone()
                asset_id = row[0] if row else None
            caller = data.get("caller") or "分析任务"
            purpose = data.get("purpose") or "验证知识资产调用"
            result = data.get("result") or "调用成功：返回可引用知识资产。"
            cur = conn.execute(
                "INSERT INTO knowledge_calls (asset_id, caller, purpose, result, created_at) VALUES (?, ?, ?, ?, ?)",
                (asset_id, caller, purpose, result, created_at),
            )
            if asset_id:
                conn.execute("UPDATE knowledge_assets SET usage_count = usage_count + 1 WHERE id = ?", (asset_id,))
            conn.commit()
            call_id = cur.lastrowid
        self.send_json({"ok": True, "call": {"id": call_id, "assetId": asset_id, "caller": caller, "purpose": purpose, "result": result, "createdAt": created_at}})

    def handle_monitoring(self):
        with sqlite3.connect(DB_PATH) as conn:
            task_rows = conn.execute(
                "SELECT id, name, platforms, prompts, schedule, status, created_at, last_run_at FROM monitor_tasks ORDER BY id DESC LIMIT 20"
            ).fetchall()
            sample_rows = conn.execute(
                """
                SELECT s.id, s.batch_id, s.task_id, s.platform, s.prompt, s.answer, s.brand_mentioned,
                       s.position, s.citations, s.risk_level, s.created_at, COALESCE(t.name, '')
                FROM answer_samples s
                LEFT JOIN monitor_tasks t ON t.id = s.task_id
                ORDER BY s.id DESC
                LIMIT 80
                """
            ).fetchall()
            risk_rows = conn.execute(
                "SELECT id, sample_id, title, detail, severity, status, created_at FROM risk_findings ORDER BY id DESC LIMIT 30"
            ).fetchall()
            total = conn.execute("SELECT COUNT(*) FROM answer_samples").fetchone()[0]
            mentioned = conn.execute("SELECT COUNT(*) FROM answer_samples WHERE brand_mentioned = 1").fetchone()[0]
            risky = conn.execute("SELECT COUNT(*) FROM risk_findings WHERE status = '待处理'").fetchone()[0]
            avg_row = conn.execute("SELECT AVG(position) FROM answer_samples WHERE brand_mentioned = 1 AND position > 0").fetchone()
            stats = {
                "tasks": conn.execute("SELECT COUNT(*) FROM monitor_tasks").fetchone()[0],
                "samples": total,
                "visibilityRate": round((mentioned / total) * 100, 1) if total else 0,
                "avgPosition": round(avg_row[0] or 0, 1),
                "pendingRisks": risky,
            }
        self.send_json(
            {
                "tasks": [db_row_to_task(row) for row in task_rows],
                "samples": [db_row_to_sample(row) for row in sample_rows],
                "risks": [db_row_to_risk(row) for row in risk_rows],
                "stats": stats,
            }
        )

    def handle_monitor_task(self):
        data = self.read_json()
        name = (data.get("name") or "新建监测任务").strip()
        platforms = parse_list(data.get("platforms"), ["豆包", "Kimi", "DeepSeek"])
        prompts = parse_list(data.get("prompts"), ["慢严舒柠适合哪些咽喉不适场景"])
        schedule = data.get("schedule") or "手动"
        created_at = now_iso()
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute(
                """
                INSERT INTO monitor_tasks (name, platforms, prompts, schedule, status, created_at, last_run_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    json.dumps(platforms, ensure_ascii=False),
                    json.dumps(prompts, ensure_ascii=False),
                    schedule,
                    "运行中",
                    created_at,
                    "",
                ),
            )
            task_id = cur.lastrowid
            batch_id, sample_ids = insert_monitor_run(conn, task_id, name, platforms, prompts)
            conn.commit()
        self.send_json(
            {
                "ok": True,
                "task": {
                    "id": task_id,
                    "name": name,
                    "platforms": platforms,
                    "prompts": prompts,
                    "schedule": schedule,
                    "status": "已完成",
                    "createdAt": created_at,
                    "lastRunAt": now_iso(),
                },
                "batchId": batch_id,
                "sampleIds": sample_ids,
                "collector": "local-simulator",
                "nextStep": "接入真实平台凭证后，将 local-simulator 替换为外部采集器。",
            }
        )

    def handle_oasis_joy(self, query):
        params = {}
        for pair in query.split("&"):
            if "=" in pair:
                key, value = pair.split("=", 1)
                params[key] = unquote(value)
        lang = params.get("lang") if params.get("lang") in OASIS_LANGS else "en"
        with sqlite3.connect(DB_PATH) as conn:
            row = conn.execute(
                """
                SELECT id, text, created_at
                FROM oasis_joy_entries
                WHERE lang = ?
                ORDER BY RANDOM()
                LIMIT 1
                """,
                (lang,),
            ).fetchone()
        if not row:
            fallback = {
                "en": "The kettle clicked off right as the rain got softer.",
                "zh": "水壶刚好在雨声变轻的时候响了一下。",
                "tc": "水壺剛好在雨聲變輕的時候響了一下。",
            }
            return self.send_json({"id": None, "text": fallback[lang], "source": "OASIS seed"})
        self.send_json({"id": row[0], "text": row[1], "source": "anonymous", "createdAt": row[2]})

    def handle_oasis_audio(self, sound_key):
        sound_key = re.sub(r"[^a-z-]", "", sound_key.lower())
        if sound_key not in OASIS_AUDIO_ASSETS:
            return self.send_json({"error": "audio not found"}, 404)
        with sqlite3.connect(DB_PATH) as conn:
            row = conn.execute(
                """
                SELECT mime_type, data, updated_at
                FROM oasis_audio_assets
                WHERE sound_key = ?
                """,
                (sound_key,),
            ).fetchone()
        if not row:
            return self.send_json({"error": "audio not found"}, 404)
        mime_type, data, updated_at = row
        data = bytes(data)
        total = len(data)
        start = 0
        end = total - 1
        status = 200
        range_header = self.headers.get("Range")
        if range_header:
            match = re.match(r"bytes=(\d*)-(\d*)", range_header)
            if match:
                if match.group(1):
                    start = int(match.group(1))
                if match.group(2):
                    end = int(match.group(2))
                start = max(0, min(start, total - 1))
                end = max(start, min(end, total - 1))
                status = 206
        body = data[start : end + 1]
        self.send_response(status)
        self.add_cors()
        self.send_header("Content-Type", mime_type)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "public, max-age=3600")
        self.send_header("ETag", f'"oasis-audio-{sound_key}-{updated_at}"')
        if status == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{total}")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def handle_oasis_joy_save(self):
        data = self.read_json()
        lang = data.get("lang") if data.get("lang") in OASIS_LANGS else "en"
        text = re.sub(r"\s+", " ", str(data.get("text") or "")).strip()
        if len(text) < 3 or len(text) > 220:
            return self.send_json({"error": "text must be 3-220 characters"}, 400)
        created_at = now_iso()
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute(
                "INSERT INTO oasis_joy_entries (lang, text, created_at) VALUES (?, ?, ?)",
                (lang, text, created_at),
            )
            conn.commit()
            entry_id = cur.lastrowid
        self.send_json({"ok": True, "id": entry_id, "createdAt": created_at})

    def handle_get_config(self, section):
        with sqlite3.connect(DB_PATH) as conn:
            row = conn.execute(
                "SELECT page_name, payload, updated_at FROM project_configs WHERE section = ?",
                (section,),
            ).fetchone()
        if not row:
            return self.send_json({"section": section, "pageName": "", "payload": {}, "updatedAt": None})
        self.send_json({"section": section, "pageName": row[0], "payload": json.loads(row[1]), "updatedAt": row[2]})

    def handle_save_config(self, section):
        data = self.read_json()
        page_name = data.get("pageName") or section
        payload = data.get("payload")
        if payload is None:
            payload = {key: value for key, value in data.items() if key != "pageName"}
        updated_at = now_iso()
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                """
                INSERT INTO project_configs (section, page_name, payload, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(section) DO UPDATE SET
                    page_name=excluded.page_name,
                    payload=excluded.payload,
                    updated_at=excluded.updated_at
                """,
                (section, page_name, json.dumps(payload, ensure_ascii=False), updated_at),
            )
            conn.commit()
        self.send_json({"ok": True, "section": section, "pageName": page_name, "payload": payload, "updatedAt": updated_at})

    def handle_lead(self):
        payload = self.read_json()
        created_at = now_iso()
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.execute(
                "INSERT INTO lead_submissions (payload, created_at) VALUES (?, ?)",
                (json.dumps(payload, ensure_ascii=False), created_at),
            )
            conn.commit()
            lead_id = cur.lastrowid
        self.send_json({"ok": True, "id": lead_id, "createdAt": created_at})

    def serve_static(self, path):
        if path == "/oasis" or path.startswith("/oasis/"):
            return self.serve_oasis(path)
        if path in {"", "/"}:
            path = "/index.html"
        target = (ROOT / path.lstrip("/")).resolve()
        if not str(target).startswith(str(ROOT)) or not target.exists() or target.is_dir():
            return self.send_json({"error": "not found"}, 404)
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        data = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def serve_oasis(self, path):
        clean_path = unquote(path.split("?", 1)[0])
        target = (ROOT / clean_path.lstrip("/")).resolve()
        if (
            str(target).startswith(str(ROOT))
            and target.exists()
            and target.is_file()
            and target.name != "index.html"
        ):
            content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
            data = target.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        lang, route = oasis_lang_route(clean_path)
        title, description = OASIS_META[lang][route]
        origin = public_origin(self)
        canonical = f"{origin}/oasis/{lang}/{route}"
        html = (ROOT / "oasis" / "index.html").read_text(encoding="utf-8")
        replacements = {
            "__LANG_ATTR__": OASIS_LANGS[lang],
            "__SEO_TITLE__": title,
            "__SEO_DESCRIPTION__": description,
            "__SEO_KEYWORDS__": oasis_keywords(lang, route),
            "__CANONICAL_URL__": canonical,
            "__ALT_EN__": f"{origin}/oasis/en/{route}",
            "__ALT_ZH__": f"{origin}/oasis/zh/{route}",
            "__ALT_TC__": f"{origin}/oasis/tc/{route}",
            "__ALT_DEFAULT__": f"{origin}/oasis/en/{route}",
            "__OG_LOCALE__": {"en": "en_US", "zh": "zh_CN", "tc": "zh_HK"}[lang],
            "__STRUCTURED_DATA__": json.dumps(oasis_structured_data(origin, lang, route, title, description), ensure_ascii=False),
        }
        for key, value in replacements.items():
            html = html.replace(key, value)
        data = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    init_db()
    port = int(os.environ.get("PORT", sys.argv[1] if len(sys.argv) > 1 else "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Serving 智荐AI app with API on http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
