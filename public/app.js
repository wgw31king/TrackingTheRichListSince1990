const pages = {
  news: document.getElementById("page-news"),
  wealth: document.getElementById("page-wealth"),
  age: document.getElementById("page-age"),
  u30: document.getElementById("page-u30"),
  u40: document.getElementById("page-u40"),
  watch: document.getElementById("page-watch")
};

let people = [];
let watchlist = [];
let u30list = [];
let u40list = [];
let newsDoc = { items: [] };
let statsDoc = null;

const MAX_AGE = 40;

function ageOf(iso) {
  const birth = new Date(iso);
  const now = new Date();
  let age = now.getFullYear() - birth.getFullYear();
  const m = now.getMonth() - birth.getMonth();
  if (m < 0 || (m === 0 && now.getDate() < birth.getDate())) age -= 1;
  return age;
}

function inU40(person) {
  if (person.ageOnList != null) return person.ageOnList <= MAX_AGE;
  if (!person.birthDate) return true;
  return ageOf(person.birthDate) <= MAX_AGE;
}

function money(n) {
  if (n >= 1e9) return (n / 1e9).toFixed(2).replace(/\.00$/, "") + "B USD";
  if (n >= 1e6) return (n / 1e6).toFixed(1) + "M USD";
  return String(n);
}

function delta(person) {
  const now = person.netWorthUsd;
  const prev = person.prevAmountUsd;
  if (prev == null || prev === undefined || !now) {
    return { textZh: "尚无上一锚点。", textEn: "No prior anchor yet.", cls: "" };
  }
  const diff = now - prev;
  if (diff === 0) {
    return {
      textZh: `较上次持平（${person.prevAsOf}，${person.prevSource}）`,
      textEn: `Flat versus last snapshot (${person.prevAsOf}, ${person.prevSource})`,
      cls: ""
    };
  }
  const pct = ((diff / prev) * 100).toFixed(0);
  const sign = diff > 0 ? "+" : "";
  return {
    textZh: `较上次 ${sign}${money(diff)}（${sign}${pct}%，${person.prevAsOf} → ${person.asOf}）`,
    textEn: `${sign}${money(diff)} versus last snapshot (${sign}${pct}%, ${person.prevAsOf} → ${person.asOf})`,
    cls: diff > 0 ? "up" : "down"
  };
}

function selfTag(kind) {
  if (kind === "self_made") return { cls: "self", zh: "白手", en: "Self-made" };
  if (kind === "not") return { cls: "not", zh: "非白手", en: "Not self-made" };
  return { cls: "wait", zh: "待核实", en: "Unverified" };
}

function tagLine(person) {
  const tags = person.listTags || [];
  if (!tags.length) return "";
  return tags
    .map((t) => `<span class="tag src">${t}</span>`)
    .join("");
}

function showPage(name) {
  Object.entries(pages).forEach(([key, el]) => {
    el.classList.toggle("hidden", key !== name);
  });
  document.querySelectorAll("nav button").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.page === name);
  });
}

function renderNews() {
  const box = document.getElementById("news-list");
  const items = (newsDoc.items || []).slice().sort((a, b) =>
    String(b.publishedAt).localeCompare(String(a.publishedAt))
  );
  if (!items.length) {
    box.innerHTML = '<p class="empty">还没有消息。点刷新，会收入截止到此刻的福布斯/胡润榜单稿。<br/>No news yet. Refresh pulls Forbes/Hurun list items published before now.</p>';
    return;
  }
  box.innerHTML = items
    .map((item) => {
      const when = new Date(item.publishedAt).toLocaleString();
      const src =
        item.source === "hurun"
          ? "胡润 Hurun"
          : item.source === "newfortune"
            ? "新财富 New Fortune"
            : "福布斯 Forbes";
      return `<article class="card">
        <div class="meta"><span class="tag src">${src}</span><span>${when}</span></div>
        <h2>${item.titleZh}</h2>
        <p class="en">${item.titleEn}</p>
        <div class="pair">
          <p>${item.summaryZh}</p>
          <p class="en">${item.summaryEn}</p>
        </div>
        <p class="meta"><a href="${item.url}" target="_blank" rel="noreferrer">原文 / Source</a></p>
      </article>`;
    })
    .join("");
}

function personCard(person) {
  const tag = selfTag(person.selfMade);
  const d = delta(person);
  const age = ageOf(person.birthDate);
  const ageLabel =
    person.birthDatePrecision === "year-approx" || person.birthDatePrecision === "month-approx"
      ? `约${age}岁 / about ${age}`
      : `${age}岁 / ${age}`;
  return `<article class="card">
    <div class="meta">
      <span class="tag ${tag.cls}">${tag.zh} / ${tag.en}</span>
      <span>${ageLabel}</span>
      <span>${person.company}</span>
      ${tagLine(person)}
    </div>
    <h2>${person.nameZh} / ${person.nameEn}</h2>
    <p class="amount">${person.displayAmount} ${person.displayUnit} · ${person.displayAmountEn}</p>
    <p class="delta ${d.cls}">${d.textZh}</p>
    <p class="en">${d.textEn}</p>
    <div class="pair">
      <p>${person.businessZh}</p>
      <p class="en">${person.businessEn}</p>
    </div>
    <p class="meta">取值日 ${person.asOf} · ${person.source}</p>
  </article>`;
}

function founderCard(person) {
  const age = person.ageOnList != null ? person.ageOnList : ageOf(person.birthDate);
  const worthZh = person.estimatedWorthZh || "预估身价：未公开";
  const worthEn = person.estimatedWorthEn || "Estimated net worth: unpublished";
  const amount =
    person.netWorthUsd != null && person.displayAmount != null
      ? `${person.displayAmount} ${person.displayUnit} · ${person.displayAmountEn}`
      : "身价未公开 · Net worth not published";
  return `<article class="card">
    <div class="meta">
      <span class="tag ${person.tier === "linked_wealth" ? "self" : "wait"}">${person.band || "U"}</span>
      <span>榜单年龄 ${age}</span>
      <span>${person.company || ""}</span>
      ${tagLine(person)}
    </div>
    <h2>${person.nameZh}${person.nameEn && person.nameEn !== person.nameZh ? " / " + person.nameEn : ""}</h2>
    <p class="amount">${amount}</p>
    <p>${worthZh}</p>
    <p class="en">${worthEn}</p>
    <div class="pair">
      <p>${person.businessZh}</p>
      <p class="en">${person.businessEn}</p>
    </div>
    <p class="meta">${person.role || ""} · ${person.industryZh || ""} · ${person.source || ""}</p>
  </article>`;
}

function watchCard(person) {
  const age = person.ageOnList != null ? person.ageOnList : ageOf(person.birthDate);
  return `<article class="card">
    <div class="meta">
      <span class="tag wait">观察 / Watch</span>
      <span>榜单年龄 ${age}</span>
      <span>${person.company}</span>
      ${tagLine(person)}
    </div>
    <h2>${person.nameZh}${person.nameEn && person.nameEn !== person.nameZh ? " / " + person.nameEn : ""}</h2>
    <p class="amount">身价未公开 · Net worth not published</p>
    <div class="pair">
      <p>${person.businessZh}</p>
      <p class="en">${person.businessEn}</p>
    </div>
    <p class="meta">${person.role || ""} · ${person.source}</p>
  </article>`;
}

function renderStats() {
  const box = document.getElementById("stats-box");
  if (!box || !statsDoc) return;
  const u30 = statsDoc.under30 || {};
  const u40s = statsDoc.under40SelfMadeOnly || {};
  const all = statsDoc.under40AllIncludingHeirs || {};
  box.innerHTML = `
    <p>Global under-30 USD billionaires with published Forbes figures: <strong>${u30.totalWithPublishedUsdBillion}</strong> (self-made ${u30.selfMade}, not self-made ${u30.notSelfMade}).</p>
    <p>全球30岁以下、福布斯公开美元亿万身价：<strong>${u30.totalWithPublishedUsdBillion}</strong> 人（白手 ${u30.selfMade}，非白手 ${u30.notSelfMade}）。</p>
    <p>Hurun global self-made USD billionaires aged 40 & under: <strong>${u40s.totalSelfMadeUsdBillion}</strong> (≤30: ${u40s.aged30AndUnder}; ≤35: ${u40s.aged35AndUnder}).</p>
    <p>胡润全球40岁及以下白手美元亿万富豪：<strong>${u40s.totalSelfMadeUsdBillion}</strong> 人（其中≤30约 ${u40s.aged30AndUnder}，≤35约 ${u40s.aged35AndUnder}）。</p>
    <p>${all.noteEn || ""}</p>
    <p>${all.noteZh || ""}</p>
  `;
}

function splitWealthRoster(list, secondaryCompare) {
  const selfMade = [];
  const notSelf = [];
  const unverified = [];
  list.forEach((p) => {
    if (p.selfMade === "self_made") selfMade.push(p);
    else if (p.selfMade === "not") notSelf.push(p);
    else unverified.push(p);
  });
  selfMade.sort(secondaryCompare);
  notSelf.sort(secondaryCompare);
  unverified.sort(secondaryCompare);
  return { selfMade, notSelf, unverified };
}

function wealthSectionsHtml(groups, secondaryLabelZh, secondaryLabelEn) {
  const parts = [];
  const blocks = [
    {
      key: "self",
      rows: groups.selfMade,
      titleZh: `白手起家 · ${groups.selfMade.length} 人`,
      titleEn: `Self-made · ${groups.selfMade.length}`
    },
    {
      key: "not",
      rows: groups.notSelf,
      titleZh: `非白手起家 · ${groups.notSelf.length} 人`,
      titleEn: `Not self-made · ${groups.notSelf.length}`
    },
    {
      key: "wait",
      rows: groups.unverified,
      titleZh: `待核实 · ${groups.unverified.length} 人`,
      titleEn: `Unverified · ${groups.unverified.length}`
    }
  ];
  blocks.forEach((block) => {
    if (!block.rows.length) return;
    parts.push(
      `<div class="group-head">
        <h3>${block.titleZh}</h3>
        <p class="en">${block.titleEn} · ${secondaryLabelEn}</p>
        <p>${secondaryLabelZh}</p>
      </div>`
    );
    parts.push(...block.rows.map(personCard));
  });
  return parts.join("");
}

function renderPeople() {
  const roster = people.filter((p) => p.netWorthUsd != null && inU40(p));
  const byWealthCmp = (a, b) => b.netWorthUsd - a.netWorthUsd;
  const byAgeCmp = (a, b) => String(b.birthDate).localeCompare(String(a.birthDate));
  const wealthGroups = splitWealthRoster(roster, byWealthCmp);
  const ageGroups = splitWealthRoster(roster, byAgeCmp);

  const selfN = wealthGroups.selfMade.length;
  const notN = wealthGroups.notSelf.length;
  const waitN = wealthGroups.unverified.length;
  const splitText =
    `Self-made ${selfN} · Not self-made ${notN}` +
    (waitN ? ` · Unverified ${waitN}` : "") +
    `<br/>白手起家 ${selfN} 人 · 非白手起家 ${notN} 人` +
    (waitN ? ` · 待核实 ${waitN} 人` : "") +
    ` · 合计 ${roster.length} 人`;

  const wealthSplit = document.getElementById("wealth-split");
  const ageSplit = document.getElementById("age-split");
  if (wealthSplit) wealthSplit.innerHTML = splitText;
  if (ageSplit) ageSplit.innerHTML = splitText;

  document.getElementById("wealth-list").innerHTML = wealthSectionsHtml(
    wealthGroups,
    "组内按身价从高到低。",
    "Within group: net worth high→low."
  );
  document.getElementById("age-list").innerHTML = wealthSectionsHtml(
    ageGroups,
    "组内按年龄，年轻在前。",
    "Within group: youngest first."
  );
  document.getElementById("u30-list").innerHTML = u30list
    .slice()
    .sort((a, b) => (a.ageOnList || 99) - (b.ageOnList || 99))
    .map(founderCard)
    .join("");
  document.getElementById("u40-list").innerHTML = u40list
    .slice()
    .sort((a, b) => (a.ageOnList || 99) - (b.ageOnList || 99))
    .map(founderCard)
    .join("");
  document.getElementById("watch-list").innerHTML = watchlist
    .slice()
    .sort((a, b) => (a.ageOnList || 99) - (b.ageOnList || 99))
    .map(watchCard)
    .join("");
  document.getElementById("counts").innerHTML =
    `Local U40 wealth ${roster.length} (self-made ${selfN} / not ${notN}` +
    (waitN ? ` / unverified ${waitN}` : "") +
    `) · U30 ${u30list.length} · U40 ${u40list.length} · Watch ${watchlist.length}` +
    `<br/>本地U40富豪榜 ${roster.length}（白手 ${selfN} / 非白手 ${notN}` +
    (waitN ? ` / 待核实 ${waitN}` : "") +
    `）· 创业U30 ${u30list.length} · 创业U40 ${u40list.length} · 观察 ${watchlist.length}`;
}

async function loadAll() {
  const [p, w, n, u30, u40, st] = await Promise.all([
    fetch("/api/people"),
    fetch("/api/watchlist"),
    fetch("/api/news"),
    fetch("/api/u30"),
    fetch("/api/u40"),
    fetch("/api/stats")
  ]);
  people = (await p.json()).people || [];
  watchlist = (await w.json()).watchlist || [];
  newsDoc = await n.json();
  u30list = (await u30.json()).u30 || [];
  u40list = (await u40.json()).u40 || [];
  statsDoc = await st.json();
  renderStats();
  renderPeople();
  renderNews();
  if (newsDoc.lastRefreshAt) {
    document.getElementById("news-status").innerHTML =
      `Last refresh: ${new Date(newsDoc.lastRefreshAt).toLocaleString()}<br/>上次刷新：${new Date(newsDoc.lastRefreshAt).toLocaleString()}`;
  }
}

document.querySelectorAll("nav button").forEach((btn) => {
  btn.addEventListener("click", () => showPage(btn.dataset.page));
});

document.getElementById("refresh").addEventListener("click", async () => {
  const btn = document.getElementById("refresh");
  btn.disabled = true;
  document.getElementById("news-status").textContent = "正在按此刻截止拉取… / Pulling items before now…";
  try {
    const res = await fetch("/api/refresh", { method: "POST" });
    const data = await res.json();
    if (data.news) newsDoc = data.news;
    renderNews();
    document.getElementById("news-status").innerHTML = `${data.noteZh}<br/>${data.noteEn}`;
  } catch (err) {
    document.getElementById("news-status").textContent =
      "刷新失败，请确认本地服务还在跑。 / Refresh failed; keep the local server running.";
  } finally {
    btn.disabled = false;
  }
});

loadAll();
