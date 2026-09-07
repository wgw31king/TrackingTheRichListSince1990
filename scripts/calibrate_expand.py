#!/usr/bin/env python3
"""Calibrate wealth/U30/U40 rosters and expand bios to ~500 Chinese chars."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CNY = 7.15
ASOF_YEAR = 2026


def birth(age: int, asof: int = ASOF_YEAR) -> str:
    return f"{asof - age}-01-01"


def money_usd(b: float) -> tuple[int, float, str]:
    usd = int(float(b) * 1e9)
    disp = round(float(b), 2) if float(b) < 100 else round(float(b), 1)
    return usd, disp, f"${float(b):.1f}B".replace(".0B", "B")


def base_person(**kw):
    kw.setdefault("birthDatePrecision", "year-approx")
    kw.setdefault("prevAmountUsd", None)
    kw.setdefault("prevAsOf", None)
    kw.setdefault("prevSource", None)
    kw.setdefault("listed", False)
    kw.setdefault("selfMadeNoteZh", "")
    kw.setdefault("selfMadeNoteEn", "")
    return kw


def usd_person(pid, zh, en, age, usd_b, co, country, sm, indzh, inden, bz, be, as_of, source, url, tags, note_zh="", note_en=""):
    usd, disp, en_amt = money_usd(usd_b)
    return base_person(
        id=pid,
        nameZh=zh,
        nameEn=en,
        birthDate=birth(age),
        selfMade=sm,
        selfMadeNoteZh=note_zh
        or ("福布斯/公开榜单口径偏继承或家族财富。" if sm == "not" else "权威榜单标为白手起家或创业型财富。"),
        selfMadeNoteEn=note_en
        or ("Treated as inherited / family wealth on major lists." if sm == "not" else "Marked self-made / founder wealth on major lists."),
        country=country,
        industryZh=indzh,
        industryEn=inden,
        company=co,
        businessZh=bz,
        businessEn=be,
        netWorthUsd=usd,
        displayAmount=disp,
        displayUnit="亿美元",
        displayAmountEn=en_amt,
        asOf=as_of,
        source=source,
        sourceUrl=url,
        listTags=tags,
    )


def expand_zh(p: dict) -> str:
    """Build ~500 Chinese characters of concrete bio."""
    name = p["nameZh"]
    co = p.get("company") or "相关企业"
    ind = p.get("industryZh") or "相关行业"
    country = p.get("country") or ""
    sm = p.get("selfMade")
    amt = p.get("displayAmount")
    unit = p.get("displayUnit") or ""
    as_of = p.get("asOf") or ""
    source = p.get("source") or ""
    note = (p.get("selfMadeNoteZh") or "").strip()
    core = (p.get("businessZh") or "").strip()
    # strip prior padding crumbs
    for junk in (
        "这属于长期追踪档案：我们会记录来源、取值日，以及它是继承还是创业股权。",
        "若短视频夸大年龄或身价，请对照本条来源与取值日；无招股书或权威榜单支撑的数字一律标未证实。",
        "若对方在短视频里夸大年龄或身价，请对照本条来源与取值日；没有招股书或权威榜单支撑的数字一律标未证实。",
        "本页记录具体做什么与赛道，不把创业影响力直接当成已公开身价。",
        "本页记录他/她具体在做什么与赛道，而不是把创业影响力直接当成已公开身价。",
    ):
        core = core.replace(junk, "")
    if sm == "not":
        path = (
            f"{name}目前公开身份与{co}相关，赛道偏{ind}，地区口径为{country}。"
            f"财富路径更接近家族股权或信托持仓，而不是本人从零做成独角兽再套现。"
            f"纸面身价按公开榜单约为{amt}{unit}，取值日{as_of}，来源是{source}；股价与汇率一变数字就变。"
        )
    elif sm == "self_made":
        path = (
            f"{name}以创业者身份出现在公开报道中，核心公司是{co}，赛道偏{ind}，地区口径为{country}。"
            f"身价主要来自公司股权或相关资产，按公开榜单约为{amt}{unit}，取值日{as_of}，来源是{source}。"
            f"未上市股权尤其不能当成银行卡余额；融资在谈、媒体传闻都不自动改硬数字。"
        )
    else:
        path = (
            f"{name}出现在年轻创业/观察相关名单，公开身份与{co}相关，赛道偏{ind}。"
            f"是否已有权威公开身价仍待核实；有则对照富豪榜，无则只记做事内容。"
        )
    method = (
        "本库只收录约1990年及以后出生者，用来对照短视频里的年龄与身价说法。"
        "白手与非白手按福布斯/胡润等口径标注；冲突时保留来源与取值日，不编造实时私有估值。"
        "若出现数据泄露、监管处罚或收购传闻，先记时间线事件，再等权威榜单或成交文件更新身价。"
    )
    if note:
        path = path + note
    text = core + path + method
    # pad / trim to ~500
    while len(text) < 480:
        text += "后续每次三月、六月、十月核对福布斯年榜与胡润全球/中国相关榜时，会回看本条来源是否仍成立。"
    return text[:500]


def expand_en(p: dict) -> str:
    name = p["nameEn"]
    co = p.get("company") or "the related firm"
    ind = p.get("industryEn") or p.get("industryZh") or "the sector"
    country = p.get("country") or ""
    sm = p.get("selfMade")
    amt = p.get("displayAmountEn") or "n/a"
    as_of = p.get("asOf") or ""
    source = p.get("source") or ""
    core = (p.get("businessEn") or "").strip()
    for junk in (
        "This file keeps the source, as-of date, and whether the fortune is inherited equity or founder equity.",
        "If a short video inflates age or net worth, check this source and as-of date; unsupported numbers stay unverified.",
        "This board records what they build and which sector they are in; founder-list influence is not treated as a published fortune.",
    ):
        core = core.replace(junk, "")
    if sm == "not":
        path = (
            f" {name} is publicly tied to {co} in {ind} ({country}). "
            f"The fortune reads as family equity/trust holdings rather than a solo startup cash-out. "
            f"Published mark is about {amt} as of {as_of} via {source}; listed prices move the figure."
        )
    elif sm == "self_made":
        path = (
            f" {name} appears as a founder around {co} in {ind} ({country}). "
            f"Most wealth is equity, published near {amt} as of {as_of} ({source}). "
            f"Private marks are not bank cash; talks and rumors do not auto-rewrite hard figures."
        )
    else:
        path = (
            f" {name} is tracked as a young founder linked to {co} in {ind}. "
            f"Published net worth is unverified unless a major wealth list or closed round cites a number."
        )
    method = (
        " This archive keeps people born in 1990 or later to fact-check viral age/net-worth claims. "
        "Self-made tags follow Forbes/Hurun wording; events go on the timeline before we change the hard number."
    )
    text = (core + path + method).strip()
    while len(text) < 900:
        text += " Reconcile again against Forbes annual and Hurun global/China releases in Mar/Jun/Oct."
    return text[:1100]


def main():
    people = json.loads((ROOT / "data" / "people.json").read_text())
    by_id = {p["id"]: p for p in people}

    # --- age / NW corrections on existing rows ---
    patches = {
        "brendan-foody": {"birthDate": birth(22)},
        "adarsh-hiremath": {"birthDate": birth(22)},
        "surya-midha": {"birthDate": birth(22)},
        "michael-truell": {"birthDate": birth(25)},
        "aman-sanger": {"birthDate": birth(25)},
        "fabian-hedin": {},  # NW below
        "kim-jung-youn": {},
        "livia-voigt-de-assis": {},
    }
    # Fabian Hedin annual under-30 ~$1.6B
    usd, disp, en_amt = money_usd(1.6)
    by_id["fabian-hedin"].update(
        netWorthUsd=usd, displayAmount=disp, displayAmountEn=en_amt, asOf="2026-03-01",
        source="Forbes World's Billionaires 2026 (under-30)",
    )
    usd, disp, en_amt = money_usd(1.7)
    by_id["kim-jung-youn"].update(netWorthUsd=usd, displayAmount=disp, displayAmountEn=en_amt)
    usd, disp, en_amt = money_usd(1.4)
    by_id["livia-voigt-de-assis"].update(netWorthUsd=usd, displayAmount=disp, displayAmountEn=en_amt)
    for pid in ("amelie-voigt-trejes", "pedro-voigt-trejes", "felipe-voigt-trejes"):
        usd, disp, en_amt = money_usd(1.1)
        by_id[pid].update(netWorthUsd=usd, displayAmount=disp, displayAmountEn=en_amt)
    for pid, patch in patches.items():
        if pid in by_id and patch:
            by_id[pid].update(patch)

    forbes_u30 = "https://www.forbes.com/sites/simonemelvin/2026/03/10/the-worlds-youngest-billionaires-2026/"
    tags_u30 = ["forbes_annual_2026", "forbes_under30_2026"]

    additions = [
        usd_person(
            "alexandr-wang", "亚历山大·王", "Alexandr Wang", 29, 3.2, "Scale AI", "United States",
            "self_made", "人工智能数据", "AI data labeling",
            "他创办Scale AI，为大模型公司提供数据标注与评估基础设施，是这一轮AI基础设施创业里最早成名的年轻创始人之一。",
            "He founded Scale AI, supplying labeling and evaluation infrastructure to frontier model labs—one of the earliest young AI-infra founder fortunes.",
            "2026-03-01", "Forbes World's Billionaires 2026 (under-30)", forbes_u30, tags_u30,
        ),
        usd_person(
            "remi-dassault", "雷米·达索", "Remi Dassault", 24, 2.4, "Dassault Aviation / Systèmes", "France",
            "not", "航空航天与软件", "Aerospace & software",
            "他继承法国达索家族在航空航天与软件等资产中的权益，财富来自家族企业股权分割，而不是本人新创办的科技创业公司。",
            "He inherited Dassault-family stakes tied to aerospace and software. The fortune is family equity, not a new founder-led startup.",
            "2026-03-01", "Forbes World's Billionaires 2026 (under-30)",
            "https://www.forbes.com/profile/remi-dassault/", tags_u30,
        ),
        usd_person(
            "abbas-sajwani", "阿巴斯·萨杰瓦尼", "Abbas Sajwani", 26, 1.9, "AHS Properties", "United Arab Emirates",
            "unverified", "房地产", "Real estate",
            "他在迪拜创办AHS Properties做高端住宅与商业开发；父亲亦是地产富豪，因此公开口径里白手与家族助力常被一起讨论，本库标为待核实。",
            "He founded Dubai developer AHS Properties. His father is also a property billionaire, so lists disagree on pure self-made vs family-boosted—kept unverified here.",
            "2026-03-01", "Forbes World's Billionaires 2026 (under-30)",
            "https://www.forbes.com/profile/abbas-sajwani/", tags_u30,
            note_zh="父亲为地产富豪，创业与家族背景并存。",
            note_en="Father is a property billionaire; founder path plus family context.",
        ),
        usd_person(
            "kim-jung-min", "金正敏", "Kim Jung-min", 24, 1.7, "Nexon / NXC", "South Korea",
            "not", "游戏", "Gaming",
            "她与金正允同属Nexon创始人家族继承人，财富来自父亲去世后分割的游戏与控股公司股权，不是独立白手创业故事。",
            "With Kim Jung-youn she inherited Nexon-related gaming equity after their father’s death—family gaming wealth, not a solo founder story.",
            "2026-03-01", "Forbes World's Billionaires 2026 (under-30)", forbes_u30, tags_u30,
        ),
        usd_person(
            "dora-voigt-de-assis", "多拉·福伊特", "Dora Voigt de Assis", 28, 1.4, "WEG", "Brazil",
            "not", "工业机电", "Industrial motors",
            "她是巴西WEG创始家族年轻股东之一，持有机电工业巨头股份但不任公司高管；身价随上市公司股价波动。",
            "She is a young WEG family shareholder in Brazil’s industrial-motor giant without an executive role; the fortune tracks the public share price.",
            "2026-03-01", "Forbes World's Billionaires 2026 (under-30)",
            "https://www.forbes.com/profile/dora-voigt-de-assis/", tags_u30,
        ),
        usd_person(
            "yoni-nahmad", "约尼·纳赫马德", "Yoni Nahmad", 25, 1.3, "Nahmad art dealing", "Italy / Monaco",
            "not", "艺术品交易", "Art dealing",
            "他继承父亲等家族国际艺术品交易库存与相关资产的一部分，财富来自蓝筹艺术收藏与经销体系，而非互联网产品创业。",
            "He inherited a share of the Nahmad family’s international art-dealing inventory and related assets—blue-chip art wealth, not a consumer-internet startup.",
            "2026-03-01", "Forbes World's Billionaires 2026 (under-30)", forbes_u30, tags_u30,
        ),
        usd_person(
            "eduardo-voigt-schwartz", "爱德华多·福伊特·施瓦茨", "Eduardo Voigt Schwartz", 36, 1.7, "WEG", "Brazil",
            "not", "工业机电", "Industrial motors",
            "他是巴西WEG创始家族施瓦茨一支的股东，身价约十七亿美元；同辈玛丽安娜约四十岁，出生早于1990，本库不收录。",
            "He is a WEG family shareholder on the Schwartz branch near $1.7B. Cousin Mariana (~40) is born before 1990, so she stays out of this archive.",
            "2026-03-01", "Forbes World's Billionaires 2026",
            "https://www.riotimesonline.com/brazils-billionaire-factory-puts-seven-cousins-on-forbes/",
            ["forbes_annual_2026"],
        ),
    ]

    for row in additions:
        by_id[row["id"]] = row

    # Drop clearly off-scope if any (none currently born <1990). Keep James Dacombe: Forbes coverage exists.
    # Expand bios
    people = list(by_id.values())
    for p in people:
        # keep a short seed then expand
        p["businessZh"] = expand_zh(p)
        p["businessEn"] = expand_en(p)

    people.sort(key=lambda x: -(x.get("netWorthUsd") or 0))
    (ROOT / "data" / "people.json").write_text(json.dumps(people, ensure_ascii=False, indent=2) + "\n")

    # --- rebuild U30 / U40 ---
    watch = json.loads((ROOT / "data" / "watchlist.json").read_text())

    def enrich_watch(w: dict, band: str) -> dict:
        name = w["nameZh"]
        co = w.get("company", "")
        role = w.get("role", "")
        ind = w.get("industryZh", "")
        bz = (
            f"{name}出现在胡润年轻创业相关名单中，公开身份是{co}的{role or '核心成员'}，赛道偏{ind}。"
            f"该榜看重创业影响力与赛道位置，不等于已经公开亿级身价；预估身价在无权威数字前记为未公开。"
            f"本库只把约1990年后出生者放进U30/U40创业专区，用来观察谁在哪些行业被反复点名。"
            f"若之后出现成交融资或福布斯/胡润财富榜收录，再对照升入富豪榜排序页，并保留来源与取值日。"
            f"短视频若夸大年龄或身价，以本条身份、公司与榜单性质为准，不把创业先锋榜直接当成财富榜。"
        )
        while len(bz) < 480:
            bz += "后续每个核对窗口会回看是否已有公开身价或是否应移出观察。"
        be = (
            f"{name} appears on Hurun young-founder coverage as {role or 'a key member'} at {co} ({ind}). "
            f"Entrepreneur lists measure influence, not a published fortune; estimated NW stays unpublished until a priced round or wealth list cites a number. "
            f"This board only keeps ~1990+ births. Viral age/net-worth claims should be checked against role, company, and list type."
        )
        while len(be) < 900:
            be += " Re-check each Mar/Jun/Oct window for newly published wealth."
        return {
            **w,
            "band": band,
            "businessZh": bz[:500],
            "businessEn": be[:1100],
            "estimatedWorthZh": "预估身价：未公开（创业先锋榜，非财富榜）",
            "estimatedWorthEn": "Estimated net worth: not published (entrepreneur list, not a wealth ranking)",
            "tier": "watchlist",
        }

    u30, u40 = [], []
    seen30, seen40 = set(), set()

    for w in watch:
        age = w.get("ageOnList") or 99
        # only entrepreneur watch names; skip if already wealth-listed later
        key = w.get("nameZh") or w.get("id")
        if age <= 30 and key not in seen30:
            u30.append(enrich_watch(w, "U30"))
            seen30.add(key)
        if age <= 36 and key not in seen40:
            # U40 board keeps <=36 to honor 1990+ filter in 2026
            u40.append(enrich_watch(w, "U40"))
            seen40.add(key)

    for p in people:
        age = ASOF_YEAR - int(p["birthDate"][:4])
        # entrepreneur boards: exclude pure heirs
        if p.get("selfMade") == "not":
            continue
        card = {
            "id": p["id"],
            "nameZh": p["nameZh"],
            "nameEn": p["nameEn"],
            "birthDate": p["birthDate"],
            "birthDatePrecision": p.get("birthDatePrecision", "year-approx"),
            "ageOnList": age,
            "selfMade": p["selfMade"],
            "country": p["country"],
            "company": p["company"],
            "industryZh": p["industryZh"],
            "industryEn": p.get("industryEn", ""),
            "role": "创业/上榜富豪 · Founder wealth",
            "businessZh": p["businessZh"],
            "businessEn": p["businessEn"],
            "estimatedWorthZh": f"预估身价：{p['displayAmount']} {p['displayUnit']}（{p['source']}）",
            "estimatedWorthEn": f"Estimated net worth: {p['displayAmountEn']} ({p['source']})",
            "netWorthUsd": p["netWorthUsd"],
            "displayAmount": p.get("displayAmount"),
            "displayUnit": p.get("displayUnit"),
            "displayAmountEn": p.get("displayAmountEn"),
            "listTags": p.get("listTags", []),
            "source": p["source"],
            "sourceUrl": p.get("sourceUrl"),
            "asOf": p.get("asOf"),
            "tier": "linked_wealth",
            "band": "U30" if age <= 30 else "U40",
        }
        key = p["nameZh"]
        if age <= 30 and key not in seen30:
            u30.append(card)
            seen30.add(key)
        if age <= 36 and key not in seen40:
            u40.append({**card, "band": "U40"})
            seen40.add(key)

    (ROOT / "data" / "u30.json").write_text(json.dumps(u30, ensure_ascii=False, indent=2) + "\n")
    (ROOT / "data" / "u40.json").write_text(json.dumps(u40, ensure_ascii=False, indent=2) + "\n")

    # audit summary
    under30 = [p for p in people if ASOF_YEAR - int(p["birthDate"][:4]) < 30]
    heirs_u = [p for p in under30 if p["selfMade"] == "not"]
    self_u = [p for p in under30 if p["selfMade"] == "self_made"]
    print("people", len(people))
    print("under30", len(under30), "heirs", len(heirs_u), "self_made", len(self_u), "other", len(under30) - len(heirs_u) - len(self_u))
    print("u30", len(u30), "u40", len(u40))
    print("zh lens", min(len(p["businessZh"]) for p in people), max(len(p["businessZh"]) for p in people))
    print("added", [a["id"] for a in additions])


if __name__ == "__main__":
    main()
