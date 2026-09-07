const PAIRS = [
  ["billionaire", "亿万富豪"],
  ["billionaires", "亿万富豪"],
  ["rich list", "富豪榜"],
  ["net worth", "身价"],
  ["valuation", "估值"],
  ["unicorn", "独角兽"],
  ["self-made", "白手起家"],
  ["founder", "创始人"],
  ["ipo", "上市"],
  ["funding", "融资"],
  ["data breach", "数据泄露"],
  ["富豪榜", "rich list"],
  ["百富榜", "China Rich List"],
  ["全球富豪榜", "Global Rich List"],
  ["独角兽", "unicorn"],
  ["身价", "net worth"],
  ["估值", "valuation"],
  ["白手起家", "self-made"],
  ["创始人", "founder"],
  ["上市", "IPO"],
  ["融资", "funding"],
  ["数据泄露", "data breach"]
];

function hasHan(text) {
  return /[\u4e00-\u9fff]/.test(text);
}

function applyPairs(text, toZh) {
  let out = text;
  for (const [en, zh] of PAIRS) {
    const from = toZh ? en : zh;
    const to = toZh ? zh : en;
    out = out.replace(new RegExp(from.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"), "ig"), to);
  }
  return out;
}

function bilingual(title) {
  const clean = String(title || "").replace(/\s+/g, " ").trim();
  if (!clean) {
    return { titleZh: "无标题", titleEn: "Untitled" };
  }
  if (hasHan(clean)) {
    return {
      titleZh: clean,
      titleEn: applyPairs(clean, false)
    };
  }
  return {
    titleZh: applyPairs(clean, true),
    titleEn: clean
  };
}

function summaryFromTitle(titleZh, titleEn, source) {
  const who = source === "hurun" ? "胡润" : source === "newfortune" ? "新财富" : "福布斯";
  const whoEn = source === "hurun" ? "Hurun" : source === "newfortune" ? "New Fortune" : "Forbes";
  const summaryZh = (
    `《${titleZh}》来自${who}相关渠道的榜单/身价消息。` +
    `阅读时请分清：这是年榜快照、实时估值，还是融资传闻；本库只把成交或权威榜单数字写入富豪榜硬字段。` +
    `若稿件涉及1990年后出生者，可对照本站富豪榜、U30/U40创业榜与观察名单，核对年龄、白手标签与取值日。` +
    `短视频夸大「三十岁身价几十亿」时，优先查原文是否给出可核验来源，而不是只看标题情绪。` +
    `胡润全球U40白手约108人，但大量37–40岁出生早于1990，不能直接当成「1990后全球亿万富豪」总人数。`
  ).slice(0, 520);
  const summaryEn = (
    `“${titleEn}” is a ${whoEn} list/net-worth related item. ` +
    `Separate annual snapshots, realtime marks, and funding rumors; this archive only hard-codes closed deals or authoritative list figures. ` +
    `For people born 1990+, cross-check the wealth roster, U30/U40 founder boards, and watchlist. ` +
    `Hurun’s Global U40 has ~108 self-made under 40, but many ages 37–40 were born before 1990 and fall outside this archive.`
  ).slice(0, 1100);
  return { summaryZh, summaryEn };
}

module.exports = { bilingual, summaryFromTitle, hasHan };
