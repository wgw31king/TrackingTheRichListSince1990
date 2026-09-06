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

function ageOf(iso) {
  const birth = new Date(iso);
  const now = new Date();
  let age = now.getFullYear() - birth.getFullYear();
  const m = now.getMonth() - birth.getMonth();
  if (m < 0 || (m === 0 && now.getDate() < birth.getDate())) age -= 1;
  return age;
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

function renderPeople() {
  const byWealth = people
    .slice()
    .filter((p) => p.netWorthUsd != null)
    .sort((a, b) => b.netWorthUsd - a.netWorthUsd);
  const byAge = people
    .slice()
    .filter((p) => p.netWorthUsd != null)
    .sort((a, b) => String(b.birthDate).localeCompare(String(a.birthDate)));
  document.getElementById("wealth-list").innerHTML = byWealth.map(personCard).join("");
  document.getElementById("age-list").innerHTML = byAge.map(personCard).join("");
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
    `富豪榜 ${byWealth.length} · U30 ${u30list.length} · U40 ${u40list.length} · 观察 ${watchlist.length}<br/>Wealth ${byWealth.length} · U30 ${u30list.length} · U40 ${u40list.length} · Watch ${watchlist.length}`;
}

async function loadAll() {
  const [p, w, n, u30, u40] = await Promise.all([
    fetch("/api/people"),
    fetch("/api/watchlist"),
    fetch("/api/news"),
    fetch("/api/u30"),
    fetch("/api/u40")
  ]);
  people = (await p.json()).people || [];
  watchlist = (await w.json()).watchlist || [];
  newsDoc = await n.json();
  u30list = (await u30.json()).u30 || [];
  u40list = (await u40.json()).u40 || [];
  renderPeople();
  renderNews();
  if (newsDoc.lastRefreshAt) {
    document.getElementById("news-status").innerHTML =
      `上次刷新：${new Date(newsDoc.lastRefreshAt).toLocaleString()}<br/>Last refresh: ${new Date(newsDoc.lastRefreshAt).toLocaleString()}`;
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
