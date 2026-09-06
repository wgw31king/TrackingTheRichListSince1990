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
  const who = source === "hurun" ? "胡润" : "福布斯";
  const whoEn = source === "hurun" ? "Hurun" : "Forbes";
  return {
    summaryZh: `${who}官方渠道出现这条榜单相关消息，数字仍以成交或年榜为准。`,
    summaryEn: `${whoEn} published this list-related item; priced deals and annual lists still govern the numbers.`
  };
}

module.exports = { bilingual, summaryFromTitle, hasHan };
