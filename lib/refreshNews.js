const fs = require("fs");
const path = require("path");
const { bilingual, summaryFromTitle } = require("./translate");

const DATA = path.join(__dirname, "..", "data", "news.json");

const KEYWORDS = [
  "billionaire",
  "billionaires",
  "rich list",
  "net worth",
  "unicorn",
  "self-made",
  "hurun",
  "forbes 400",
  "富豪",
  "百富",
  "创富",
  "独角兽",
  "身价",
  "估值",
  "白手起家"
];

const SOURCES = [
  {
    source: "forbes",
    url: "https://www.forbes.com/billionaires/",
    extra: "https://www.forbes.com/real-time-billionaires/"
  },
  {
    source: "hurun",
    url: "https://www.hurun.net/zh-CN/Info/List"
  }
];

function loadNews() {
  return JSON.parse(fs.readFileSync(DATA, "utf8"));
}

function saveNews(doc) {
  fs.writeFileSync(DATA, JSON.stringify(doc, null, 2) + "\n");
}

function isListNews(text) {
  const hay = String(text || "").toLowerCase();
  return KEYWORDS.some((k) => hay.includes(k.toLowerCase()));
}

function decode(html) {
  return html
    .replace(/&amp;/g, "&")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&#x27;/g, "'");
}

function extractLinks(html, source) {
  const found = [];
  const re = /<a[^>]+href=["']([^"']+)["'][^>]*>([\s\S]*?)<\/a>/gi;
  let m;
  while ((m = re.exec(html))) {
    const href = m[1];
    const title = decode(m[2].replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
    if (!title || title.length < 8 || title.length > 160) continue;
    if (!isListNews(title)) continue;
    let url = href;
    if (url.startsWith("//")) url = "https:" + url;
    if (url.startsWith("/")) {
      url = source === "hurun" ? "https://www.hurun.net" + url : "https://www.forbes.com" + url;
    }
    if (!/^https?:\/\//i.test(url)) continue;
    found.push({ title, url, source });
  }
  return found;
}

async function fetchText(url) {
  const res = await fetch(url, {
    headers: {
      "user-agent":
        "WealthTrackerLocal/1.0 (personal research; +local refresh button)",
      accept: "text/html,application/xhtml+xml"
    },
    signal: AbortSignal.timeout(15000)
  });
  if (!res.ok) {
    throw new Error(`${url} -> ${res.status}`);
  }
  return res.text();
}

function slug(url) {
  return Buffer.from(url).toString("base64url").slice(0, 24);
}

async function refreshNews(cutoff = new Date()) {
  const doc = loadNews();
  const errors = [];
  const incoming = [];

  for (const src of SOURCES) {
    const urls = [src.url, src.extra].filter(Boolean);
    for (const url of urls) {
      try {
        const html = await fetchText(url);
        incoming.push(...extractLinks(html, src.source));
      } catch (err) {
        errors.push(`${src.source}: ${err.message}`);
      }
    }
  }

  const seen = new Set(doc.items.map((i) => i.url));
  const cutoffIso = cutoff.toISOString();
  let added = 0;

  for (const row of incoming) {
    if (seen.has(row.url)) continue;
    seen.add(row.url);
    const { titleZh, titleEn } = bilingual(row.title);
    const { summaryZh, summaryEn } = summaryFromTitle(titleZh, titleEn, row.source);
    doc.items.unshift({
      id: "live-" + slug(row.url),
      source: row.source,
      publishedAt: cutoffIso,
      fetchedAt: cutoffIso,
      titleZh,
      titleEn,
      summaryZh,
      summaryEn,
      url: row.url,
      personIds: []
    });
    added += 1;
  }

  doc.items.sort((a, b) => String(b.publishedAt).localeCompare(String(a.publishedAt)));
  doc.lastRefreshAt = cutoffIso;
  doc.cutoffAt = cutoffIso;
  saveNews(doc);

  return {
    added,
    total: doc.items.length,
    cutoffAt: cutoffIso,
    errors,
    noteZh:
      added > 0
        ? `已收入截止到刷新时刻的 ${added} 条新稿。`
        : errors.length
          ? "官网这次没有拉到新标题，或被网站拦住了；本地仍保留上次消息。"
          : "本次刷新无新的榜单相关消息。",
    noteEn:
      added > 0
        ? `Saved ${added} new item(s) published before this refresh.`
        : errors.length
          ? "The official sites did not yield new headlines this time, or they blocked the request; last saved news stays."
          : "No new list-related items in this refresh."
  };
}

module.exports = { refreshNews, loadNews };
