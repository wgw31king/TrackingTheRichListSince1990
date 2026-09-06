#!/usr/bin/env python3
"""Rebuild people.json + u30/u40 boards with long bilingual bios."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CNY = 7.15


def birth(age: int, asof: int = 2026) -> str:
    return f"{asof - age}-01-01"


def P(**kw):
    kw.setdefault("birthDatePrecision", "year-approx")
    kw.setdefault("prevAmountUsd", None)
    kw.setdefault("prevAsOf", None)
    kw.setdefault("prevSource", None)
    kw.setdefault("listed", False)
    kw.setdefault("selfMadeNoteZh", "")
    kw.setdefault("selfMadeNoteEn", "")
    return kw


def usd_row(pid, zh, en, age, usd_b, co, country, sm, indzh, inden, bz, be, as_of, source, url, tags, note_zh="", note_en=""):
    usd = int(float(usd_b) * 1e9)
    return P(
        id=pid,
        nameZh=zh,
        nameEn=en,
        birthDate=birth(age),
        selfMade=sm,
        selfMadeNoteZh=note_zh
        or ("福布斯/胡润口径为继承财富。" if sm == "not" else "权威榜单标为白手起家或创业型财富。"),
        selfMadeNoteEn=note_en
        or ("Classified as inherited on major lists." if sm == "not" else "Marked self-made / founder wealth on major lists."),
        country=country,
        industryZh=indzh,
        industryEn=inden,
        company=co,
        businessZh=bz,
        businessEn=be,
        netWorthUsd=usd,
        displayAmount=round(float(usd_b), 2) if float(usd_b) < 100 else round(float(usd_b), 1),
        displayUnit="亿美元",
        displayAmountEn=f"${float(usd_b):.1f}B".replace(".0B", "B"),
        asOf=as_of,
        source=source,
        sourceUrl=url,
        listTags=tags,
    )


def cny_row(pid, zh, en, age, cny_yi, co, country, sm, indzh, inden, bz, be, as_of, source, url, tags):
    usd = int(cny_yi * 1e8 / CNY)
    return P(
        id=pid,
        nameZh=zh,
        nameEn=en,
        birthDate=birth(age, 2025),
        selfMade=sm,
        selfMadeNoteZh="胡润中国榜口径的创业型/上榜财富。",
        selfMadeNoteEn="Wealth figure from Hurun China lists.",
        country=country,
        industryZh=indzh,
        industryEn=inden,
        company=co,
        businessZh=bz,
        businessEn=be,
        netWorthUsd=usd,
        displayAmount=cny_yi,
        displayUnit="亿元人民币",
        displayAmountEn=f"CNY {cny_yi}B",
        asOf=as_of,
        source=source,
        sourceUrl=url,
        listTags=tags,
    )


people: list[dict] = []

# --- Forbes under-30 heirs (2026) ---
heirs = [
    ("amelie-voigt-trejes", "阿梅莉·福伊特", "Amelie Voigt Trejes", 20, 1.1, "WEG", "Brazil", "工业机电", "Industrial motors",
     "她通过家族信托持有巴西机电巨头WEG约2%股份，属于继承型财富，本人不负责公司日常经营。这笔身价会随上市公司股价波动，不能当成自己创业赚到的现金。",
     "She holds about a 2% stake in Brazil’s industrial-motor giant WEG through a family trust. The fortune is inherited, not self-built, and moves with the public share price."),
    ("johannes-von-baumbach", "约翰内斯·冯·鲍姆巴赫", "Johannes von Baumbach", 20, 6.4, "Boehringer Ingelheim", "Germany", "制药", "Pharmaceuticals",
     "他是德国制药家族勃林格殷格翰的继承人之一，财富来自家族持有的非上市药企股权，而不是本人创办的公司。同家族多位兄弟姐妹也因此登上年轻富豪榜。",
     "He is an heir to Germany’s Boehringer Ingelheim pharmaceutical fortune. The money is family equity in a private drugmaker, not a company he founded."),
    ("livia-voigt-de-assis", "莉维娅·福伊特", "Livia Voigt de Assis", 21, 1.2, "WEG", "Brazil", "工业机电", "Industrial motors",
     "她同样来自巴西WEG创始家族旁系，身价来自继承的公司股份。公开报道强调这是家族工业资产，而不是科技创业故事。",
     "She is another WEG family heir in Brazil. Public reports treat this as inherited industrial equity, not a tech founding story."),
    ("clemente-del-vecchio", "克莱门特·德尔·韦基奥", "Clemente Del Vecchio", 21, 6.8, "EssilorLuxottica", "Italy", "眼镜零售", "Eyewear",
     "他继承意大利眼镜巨头EssilorLuxottica（雷朋、Oakley等品牌）家族股权，是全球30岁以下身价最高档的继承人之一。财富随该集团市值变化。",
     "He inherited a stake in EssilorLuxottica, the Italian eyewear group behind Ray-Ban and Oakley. Among under-30 fortunes, this is top-tier inherited wealth."),
    ("kim-jung-youn", "金正允", "Kim Jung-youn", 22, 1.5, "Nexon / NXC", "South Korea", "游戏", "Gaming",
     "她来自韩国游戏公司Nexon控制人家族，财富主要是继承的游戏与控股公司股权，不是独立白手创业。",
     "She comes from the family that controls Korean game company Nexon. The fortune is inherited gaming equity, not a solo self-made startup."),
    ("kevin-david-lehmann", "凯文·大卫·莱曼", "Kevin David Lehmann", 23, 4.9, "dm-drogerie markt", "Germany", "零售", "Retail",
     "他是德国连锁药店dm的继承人，身价来自家族零售帝国股份。这是欧洲典型的家族企业传承路径，不是科技估值故事。",
     "He is an heir to Germany’s dm drugstore chain. The wealth is a European family-retail stake, not a venture-capital AI story."),
    ("pedro-voigt-trejes", "佩德罗·福伊特", "Pedro Voigt Trejes", 23, 1.0, "WEG", "Brazil", "工业机电", "Industrial motors",
     "他又是WEG家族年轻继承人之一，公开身价约十亿美元量级，来源仍是家族机电工业股份。",
     "Another young WEG family heir, with a fortune around one billion dollars from the same industrial-motor company stake."),
    ("felipe-voigt-trejes", "费利佩·福伊特", "Felipe Voigt Trejes", 23, 1.0, "WEG", "Brazil", "工业机电", "Industrial motors",
     "他与双胞胎兄弟佩德罗同为巴西WEG创始家族年轻继承人，身价来自家族机电工业股份，本人不负责公司日常经营。",
     "Twin brother of Pedro and another young WEG heir in Brazil. The fortune is inherited industrial equity, not a company he operates day to day."),
    ("luca-del-vecchio", "卢卡·德尔·韦基奥", "Luca Del Vecchio", 24, 6.8, "EssilorLuxottica", "Italy", "眼镜零售", "Eyewear",
     "他与兄弟克莱门特同为EssilorLuxottica继承人，各自身价都在近七十亿美元量级，属于全球最年轻的顶级继承人富豪。",
     "With his brother Clemente, he is an EssilorLuxottica heir. Each is near seven billion dollars—among the richest under-30 inherited fortunes."),
    ("franz-von-baumbach", "弗朗茨·冯·鲍姆巴赫", "Franz von Baumbach", 24, 6.6, "Boehringer Ingelheim", "Germany", "制药", "Pharmaceuticals",
     "他同样继承勃林格殷格翰家族药业股权，身价与同辈兄弟姐妹接近，反映的是家族资产分割，而不是个人创业估值。",
     "He also holds Boehringer Ingelheim family pharmaceutical equity. His fortune tracks siblings’ inherited stakes, not a personal startup valuation."),
    ("katharina-von-baumbach", "卡塔琳娜·冯·鲍姆巴赫", "Katharina von Baumbach", 26, 6.6, "Boehringer Ingelheim", "Germany", "制药", "Pharmaceuticals",
     "她是勃林格殷格翰家族年轻继承人之一，财富来自德国大型非上市制药企业的家族股份，属于继承而非白手创业。",
     "She is a young Boehringer Ingelheim heir. The fortune is a stake in Germany’s large private drugmaker, inherited rather than self-made."),
    ("maximilian-von-baumbach", "马克西米利安·冯·鲍姆巴赫", "Maximilian von Baumbach", 28, 6.6, "Boehringer Ingelheim", "Germany", "制药", "Pharmaceuticals",
     "他又一位勃林格殷格翰年轻继承人，身价来自家族制药股权。在福布斯30岁以下榜单中，该家族多人同时上榜。",
     "Another Boehringer Ingelheim heir on the Forbes under-30 list. The family stake, not a new company, drives the number."),
    ("zahan-mistry", "扎汉·米斯特里", "Zahan Mistry", 27, 3.5, "Tata Sons", "India", "综合财团", "Conglomerate",
     "他与塔塔家族相关，财富来自印度塔塔集团控股体系中的继承权益，属于大型多元化财团传承。",
     "His fortune is tied to inherited interests around India’s Tata Sons conglomerate structure, not a new founder-led startup."),
    ("firoz-mistry", "菲罗兹·米斯特里", "Firoz Mistry", 29, 3.1, "Tata Sons", "Ireland / India", "综合财团", "Conglomerate",
     "他继承塔塔子孙公司相关权益，公开报道将其列为继承型年轻富豪，主业是多元化财团而非单一科技产品。",
     "He inherited interests linked to Tata Sons. Coverage treats him as an heir to a diversified conglomerate, not a single tech product founder."),
    ("alexandra-andresen", "亚历山德拉·安德烈森", "Alexandra Andresen", 29, 2.5, "Ferd", "Norway", "投资", "Investments",
     "她的财富来自挪威家族投资公司Ferd的继承股份，属于北欧家族资本传承，并不是互联网创业估值故事。",
     "Her fortune comes from Norway’s family investment firm Ferd. It is inherited Nordic family capital, not a venture-startup valuation story."),
    ("wang-zelong", "王泽龙", "Wang Zelong", 29, 1.2, "中核华原钛白", "China", "化工", "Chemicals",
     "公开报道称他持有中核华原钛白等相关化工资产权益，属于年轻继承人路径；具体持股细节以福布斯年度口径为准。",
     "Reports link his fortune to CNNC Hua Yuan titanium-dioxide related chemical assets. Treat as a young heir path; Forbes annual figures govern."),
]

for pid, zh, en, age, b, co, country, indzh, inden, bz, be in heirs:
    people.append(
        usd_row(
            pid, zh, en, age, b, co, country, "not", indzh, inden, bz, be,
            "2026-03-01", "Forbes World's Billionaires 2026 (under-30)",
            "https://www.forbes.com/sites/simonemelvin/2026/03/10/the-worlds-youngest-billionaires-2026/",
            ["forbes_annual_2026", "forbes_under30_2026"],
        )
    )

# --- Self-made / founder wealth (Forbes + Hurun U40 age<=36) ---
founders = [
    ("justin-sun", "孙宇晨", "Justin Sun", 36, 8.5, "TRON / HTX", "Grenada / China-born", "加密货币", "Cryptocurrency",
     "他创办波场TRON并深度参与火币等加密生态，财富主要押在代币与相关平台权益上。数字会随加密行情剧烈波动，福布斯实时页常有大幅跳动，不能当成已兑现现金。",
     "He founded TRON and is tied to crypto venues such as HTX. Most of the fortune sits in tokens and related equity, so Forbes’ realtime number swings hard with crypto markets and is not cash in hand.",
     "2026-09-05", "Forbes realtime", "https://www.forbes.com/profile/justin-sun/", ["forbes_realtime", "hurun_china_rich_2025"]),
    ("john-collison", "约翰·科里森", "John Collison", 35, 13.0, "Stripe", "Ireland / United States", "金融科技支付", "Fintech payments",
     "他与哥哥帕特里克共同创办Stripe，为全球互联网公司提供支付与金融基础设施。胡润U40白手起家榜将其身价估在约一百三十亿美元，财富主要来自未上市股权。",
     "With his brother Patrick he cofounded Stripe, the payments backbone for internet companies. Hurun’s U40 self-made list put him around thirteen billion dollars, mostly private equity.",
     "2026-01-15", "Hurun Global U40 Self-Made 2026", "https://www.hurun.net/en-us/info/detail?num=I149SMJVNS8L", ["hurun_global_u40_2026"]),
    ("ankur-jain", "安库尔·贾恩", "Ankur Jain", 35, 3.8, "Bilt Rewards", "United States", "金融科技", "Fintech",
     "他创办Bilt Rewards，把租房支付与积分奖励结合起来，面向美国租客与房东生态。胡润U40将其身价估在约三十八亿美元，属于金融科技创业路径。",
     "He founded Bilt Rewards, tying rent payments to loyalty points for U.S. renters. Hurun U40 estimated about $3.8 billion—fintech founder wealth.",
     "2026-01-15", "Hurun Global U40 Self-Made 2026", "https://www.hurun.net/en-us/info/detail?num=I149SMJVNS8L", ["hurun_global_u40_2026"]),
    ("christopher-olah", "克里斯托弗·奥拉", "Christopher Olah", 33, 3.7, "Anthropic", "United States", "人工智能", "Artificial intelligence",
     "他是Anthropic联合创始人之一，公司做大模型与AI安全方向。胡润U40按Anthropic高估值把几位联合创始人各估到约三十七亿美元量级。",
     "He is an Anthropic cofounder working on frontier models and AI safety. Hurun U40 priced several cofounders around $3.7 billion each on Anthropic’s private valuation.",
     "2026-01-15", "Hurun Global U40 Self-Made 2026", "https://www.hurun.net/en-us/info/detail?num=I149SMJVNS8L", ["hurun_global_u40_2026"]),
    ("sam-mccandlish", "山姆·麦坎德利什", "Sam McCandlish", 35, 3.7, "Anthropic", "United States", "人工智能", "Artificial intelligence",
     "他同样是Anthropic联合创始人，财富与公司未上市股权绑定。身价会随新一轮融资与模型商业化进度大幅变化，属于典型AI创富案例。",
     "Also an Anthropic cofounder, with wealth tied to private equity. The number can jump with new funding rounds—classic AI founder wealth.",
     "2026-01-15", "Hurun Global U40 Self-Made 2026", "https://www.hurun.net/en-us/info/detail?num=I149SMJVNS8L", ["hurun_global_u40_2026"]),
    ("palmer-luckey", "帕尔默·拉奇", "Palmer Luckey", 33, 5.0, "Anduril Industries", "United States", "国防科技", "Defense tech",
     "他早年做Oculus，后创办Anduril做自主防务与AI军工系统。胡润把Anduril估在约六百亿美元量级融资叙事中，他的个人身价随防务科技估值上升。",
     "After Oculus he founded Anduril for autonomous defense systems. Hurun places Anduril in a ~$60B valuation narrative; his fortune tracks defense-tech pricing.",
     "2026-01-15", "Hurun Global U40 / Anduril coverage", "https://www.hurun.net/en-us/info/detail?num=I149SMJVNS8L", ["hurun_global_u40_2026"]),
    ("aravind-srinivas", "阿拉温德·斯里尼瓦斯", "Aravind Srinivas", 31, 2.4, "Perplexity AI", "India / United States", "AI 搜索", "AI search",
     "他联合创办Perplexity，做带引用的AI问答搜索引擎。胡润U40在公司约九十亿美元估值叙事下，将其个人身价估在约二十四亿美元。",
     "He cofounded Perplexity, an AI answer engine with citations. Hurun U40 put him near $2.4 billion against a multi-billion private valuation.",
     "2026-01-15", "Hurun Global U40 Self-Made 2026", "https://www.hurun.net/en-us/info/detail?num=I149SMJVNS8L", ["hurun_global_u40_2026"]),
    ("andy-fang", "方爱民", "Andy Fang", 33, 2.1, "DoorDash", "United States", "本地生活配送", "Food delivery",
     "他是DoorDash联合创始人，做外卖与本地即时配送平台，公司已上市。身价主要来自公开市场持股，会随股价每日波动。",
     "He cofounded DoorDash, the food-delivery platform now public. Most of the fortune is listed equity and moves with the stock.",
     "2026-01-15", "Hurun Global U40 Self-Made 2026", "https://www.hurun.net/en-us/info/detail?num=I149SMJVNS8L", ["hurun_global_u40_2026"]),
    ("stanley-tang", "唐维伦", "Stanley Tang", 33, 2.0, "DoorDash", "United States", "本地生活配送", "Food delivery",
     "他同样是DoorDash联合创始人，业务覆盖美国等多地外卖配送。公开市场股权是身价主体，和方爱民同属配送赛道创富。",
     "Also a DoorDash cofounder in U.S. food delivery. Public equity drives the fortune, same delivery-sector path as Andy Fang.",
     "2026-01-15", "Hurun Global U40 Self-Made 2026", "https://www.hurun.net/en-us/info/detail?num=I149SMJVNS8L", ["hurun_global_u40_2026"]),
    ("michael-truell", "迈克尔·特鲁尔", "Michael Truell", 26, 2.6, "Cursor / Anysphere", "United States", "AI 编程工具", "AI coding tools",
     "他与MIT同学创办Cursor（Anysphere），做AI代码编辑器，服务大量专业开发者。SpaceX约六百亿美元全股票收购叙事后，福布斯按SpaceX股票估算其身价。",
     "He cofounded Cursor (Anysphere), the AI code editor used by millions of developers. After SpaceX’s ~$60B all-stock deal story, Forbes prices him in SpaceX shares.",
     "2026-09-06", "Forbes realtime", "https://www.forbes.com/profile/michael-truell/", ["forbes_realtime", "hurun_global_u40_2026"]),
    ("aman-sanger", "阿曼·桑格", "Aman Sanger", 26, 2.6, "Cursor / Anysphere", "United States", "AI 编程工具", "AI coding tools",
     "他是Cursor联合创始人，从MIT同学团队把产品做成高增长AI编程工具。身价与收购后持有的SpaceX相关权益绑定，属于软件工具赛道创富。",
     "Cursor cofounder from the MIT team that scaled an AI coding tool. His fortune is tied to SpaceX-related equity after the acquisition narrative.",
     "2026-09-06", "Forbes realtime", "https://www.forbes.com/profile/aman-sanger/", ["forbes_realtime", "hurun_global_u40_2026"]),
    ("sualeh-asif", "苏阿莱赫·阿西夫", "Sualeh Asif", 26, 2.6, "Cursor / Anysphere", "Pakistan / United States", "AI 编程工具", "AI coding tools",
     "他出生于巴基斯坦卡拉奇，在MIT与同学创办Cursor并负责产品方向。公开身价同样来自收购交易后的股票估算，不是中国互联网流量故事。",
     "Born in Karachi, he cofounded Cursor at MIT and led product. Public fortune estimates come from post-deal stock math, not China consumer-internet traffic.",
     "2026-09-06", "Forbes realtime", "https://www.forbes.com/profile/sualeh-asif/", ["forbes_realtime", "hurun_global_u40_2026"]),
    ("arvid-lunnemark", "阿尔维德·伦内马克", "Arvid Lunnemark", 26, 2.6, "Cursor / Anysphere", "Sweden / United States", "AI 编程工具", "AI coding tools",
     "这位瑞典籍联合创始人参与创办Cursor后转做更安全的AI系统研究。福布斯仍按其Cursor/SpaceX相关权益估算身价，属欧洲出身、美国创业路径。",
     "The Swedish cofounder helped build Cursor then moved toward safer-AI research. Forbes still prices Cursor/SpaceX-related equity—Europe-born, U.S. startup path.",
     "2026-09-06", "Forbes realtime", "https://www.forbes.com/profile/arvid-lunnemark/", ["forbes_realtime", "hurun_global_u40_2026"]),
    ("luana-lopes-lara", "卢安娜·洛佩斯·拉拉", "Luana Lopes Lara", 29, 2.6, "Kalshi", "Brazil / United States", "预测市场", "Prediction markets",
     "她从芭蕾舞者转到MIT，再与同学创办受监管的预测市场Kalshi，让用户交易现实事件结果。身价按约12%股权与公司高估值估算，会随新一轮融资变化。",
     "A former ballerina who studied at MIT and cofounded regulated prediction market Kalshi. Fortune estimates use about a 12% stake and can jump with new rounds.",
     "2026-05-07", "Forbes Kalshi coverage", "https://www.forbes.com/sites/aliciapark/2026/05/07/kalshi-billionaire-cofounders-double-their-net-worths-with-another-funding-round/", ["forbes_realtime", "hurun_global_u40_2026"]),
    ("tarek-mansour", "塔雷克·曼苏尔", "Tarek Mansour", 29, 2.6, "Kalshi", "United States", "预测市场", "Prediction markets",
     "他是Kalshi联合创始人兼CEO，做美国受监管事件合约交易平台。与洛佩斯·拉拉同属预测市场赛道，身价同样按大额融资后的股权估算。",
     "Kalshi’s cofounder-CEO built a U.S.-regulated event-contract exchange. Same prediction-market path as Lopes Lara; wealth is equity after large funding rounds.",
     "2026-05-07", "Forbes Kalshi coverage", "https://www.forbes.com/sites/aliciapark/2026/05/07/kalshi-billionaire-cofounders-double-their-net-worths-with-another-funding-round/", ["forbes_realtime", "hurun_global_u40_2026"]),
    ("brendan-foody", "布伦丹·福迪", "Brendan Foody", 23, 2.2, "Mercor", "United States", "AI 训练数据", "AI training data",
     "他把领域专家匹配给前沿AI实验室，做训练与评估数据业务。公司上一笔硬估值仍是约一百亿美元C轮；二百亿美元新一轮多为在谈，福布斯人物页仍按约二十二亿美元估。",
     "He matches domain experts to frontier AI labs for training data. The last closed company price is still the ~$10B round; $20B talk is not closed, and Forbes still shows about $2.2B.",
     "2026-09-05", "Forbes realtime", "https://www.forbes.com/profile/brendan-foody/", ["forbes_realtime", "hurun_global_u40_2026"]),
    ("adarsh-hiremath", "阿达什·希雷马特", "Adarsh Hiremath", 23, 2.2, "Mercor", "United States", "AI 训练数据", "AI training data",
     "他是Mercor联合创始人兼CTO，负责技术体系。身价与Foody、Midha一样，按约22%股权和一百亿美元成交估值估算，泄露事件记时间线但不自动改硬数字。",
     "Mercor cofounder-CTO. Like his cofounders, fortune math uses ~22% of the $10B closed valuation; the breach is timeline news, not an automatic markdown.",
     "2026-09-05", "Forbes realtime", "https://www.forbes.com/profile/adarsh-hiremath/", ["forbes_realtime", "hurun_global_u40_2026"]),
    ("surya-midha", "苏里亚·米达", "Surya Midha", 23, 2.2, "Mercor", "United States", "AI 训练数据", "AI training data",
     "他是三人中最年轻的联合创始人，现任董事长。公开叙事称其为最年轻白手起家亿万富豪之一，但身价仍是未上市股权纸面值，不是已套现现金。",
     "Youngest of the three cofounders and now chairman. Coverage calls him among the youngest self-made billionaires, but the number is still private-equity paper wealth.",
     "2026-09-05", "Forbes realtime", "https://www.forbes.com/profile/surya-midha/", ["forbes_realtime", "hurun_global_u40_2026"]),
    ("alakh-pandey", "阿拉赫·潘迪", "Alakh Pandey", 33, 1.7, "Physics Wallah", "India", "在线教育", "Edtech",
     "他创办Physics Wallah，用低价在线课程服务印度大规模备考学生。胡润U40将其估在约十七亿美元，属于本地教育刚需创业，而不是硅谷纯软件故事。",
     "He founded Physics Wallah, low-cost online exam prep for Indian students. Hurun U40 estimated about $1.7 billion—local edtech demand, not a pure Silicon Valley SaaS story.",
     "2026-01-15", "Hurun Global U40 Self-Made 2026", "https://www.hurun.net/en-us/info/detail?num=I149SMJVNS8L", ["hurun_global_u40_2026"]),
    ("ritesh-agarwal", "里特什·阿加瓦尔", "Ritesh Agarwal", 32, 1.2, "OYO", "India", "酒店住宿", "Hospitality",
     "他从布巴内斯瓦尔起步创办OYO，做标准化连锁住宿网络，业务覆盖多国。胡润U40将其列入白手起家年轻富豪，身价随酒店与资本周期波动。",
     "He built OYO from Bhubaneswar into a multi-country standardized hotel network. Hurun U40 lists him as a young self-made billionaire; hospitality cycles move the number.",
     "2026-01-15", "Hurun Global U40 Self-Made 2026", "https://www.hurun.net/en-us/info/detail?num=I149SMJVNS8L", ["hurun_global_u40_2026"]),
    ("lucy-guo", "露西·郭", "Lucy Guo", 31, 1.3, "Scale AI / Passes", "United States", "AI 数据与创作者", "AI data / creators",
     "她联合创办Scale AI做数据标注，后继续创业。胡润U40将其估在约十三亿美元；曾是最年轻白手起家女性富豪叙事中的关键人物之一。",
     "She cofounded Scale AI for data labeling and kept building. Hurun U40 estimated about $1.3 billion; she featured in youngest self-made woman narratives.",
     "2026-01-15", "Hurun Global U40 Self-Made 2026", "https://www.hurun.net/en-us/info/detail?num=I149SMJVNS8L", ["hurun_global_u40_2026"]),
    ("shayne-coplan", "谢恩·科普兰", "Shayne Coplan", 28, 1.0, "Polymarket", "United States", "预测市场", "Prediction markets",
     "他创办Polymarket，用加密与区块链机制做事件预测交易。ICE入股后公司估值抬升，福布斯按约11%股权将其估到约十亿美元量级。",
     "He founded Polymarket, a crypto-native prediction market. After ICE’s investment lifted the valuation, Forbes estimated about $1 billion on roughly an 11% stake.",
     "2026-08-25", "Forbes realtime", "https://www.forbes.com/profile/shayne-coplan/", ["forbes_realtime", "forbes_under30_2026"]),
    ("fabian-hedin", "法比安·赫丁", "Fabian Hedin", 26, 1.0, "Lovable", "Sweden", "AI 软件", "AI software",
     "公开报道将其列为瑞典AI创业年轻富豪之一，与Lovable等AI软件产品相关。具体持股与最新估值仍以福布斯/胡润更新为准，此处按公开年轻白手叙事收录。",
     "Coverage lists him among young Swedish AI software founders tied to Lovable. Exact stake math follows Forbes/Hurun updates; included from public young self-made narratives.",
     "2026-03-01", "Forbes under-30 / AI founder coverage", "https://www.forbes.com/sites/simonemelvin/2026/03/10/the-worlds-youngest-billionaires-2026/", ["forbes_under30_2026"]),
    ("kylie-jenner", "凯莉·詹娜", "Kylie Jenner", 28, 1.2, "Kylie Cosmetics", "United States", "美妆消费", "Beauty",
     "她把个人影响力做成美妆品牌Kylie Cosmetics并多次交易股权。胡润U40女性白手榜将其估在约十二亿美元；公众人物品牌估值争议较大，需看交易口径。",
     "She turned influence into Kylie Cosmetics and sold stakes over time. Hurun U40 put her near $1.2 billion; celebrity-brand valuations are debated and deal-dependent.",
     "2026-01-15", "Hurun Global U40 Self-Made 2026", "https://www.hurun.net/en-us/info/detail?num=I149SMJVNS8L", ["hurun_global_u40_2026"]),
    ("james-dacombe", "詹姆斯·达科姆", "James Dacombe", 25, 1.0, "Olix / CoMind", "United Kingdom", "AI 芯片", "AI chips",
     "他辍学创业，后做AI芯片公司Olix，并仍与脑机相关项目有关。福布斯报道将其称为欧洲最年轻白手起家亿万富豪之一，身价来自新一轮融资估值估算。",
     "A school dropout who later founded AI-chip firm Olix and stays tied to brain-tech work. Forbes called him among Europe’s youngest self-made billionaires on funding math.",
     "2026-08-15", "Forbes Olix coverage", "https://www.forbes.com/sites/aliciapark/2026/08-15/british-ai-chip-founder-becomes-europes-youngest-self-made-billionaire/", ["forbes_realtime"]),
]

for t in founders:
    pid, zh, en, age, b, co, country, indzh, inden, bz, be, as_of, source, url, tags = t
    people.append(usd_row(pid, zh, en, age, b, co, country, "self_made", indzh, inden, bz, be, as_of, source, url, tags))

# China CNY wealth (1990+)
china = [
    ("wang-xingxing", "王兴兴", "Wang Xingxing", 35, 183.12, "宇树科技 Unitree", "China", "self_made", "人形与四足机器人", "Humanoid and quadruped robots",
     "他在杭州创办宇树，先做四足机器狗再做人形机器人，靠产品销售与公司股权变富。科创板发行价口径下持股市值约一百八十三亿元人民币，但仍有限售，纸面富贵不等于立刻可变现。",
     "He founded Unitree in Hangzhou, scaling from quadruped robots to humanoids. At the STAR Market issue price his stake was about CNY 18.3 billion, still lock-up constrained and not instantly liquid cash.",
     "2026-08-06", "Unitree IPO issue price / New Fortune", "https://finance.sina.com.cn/jjxw/2026-08-07/doc-inimnenr0041608.shtml", ["new_fortune_2026", "hurun_u40_2025"]),
    ("liu-jingkang", "刘靖康", "Liu Jingkang", 34, 385, "影石 Insta360", "China", "self_made", "消费电子", "Consumer electronics",
     "他创办影石Insta360，做全景相机与运动影像硬件，产品卖到全球消费电子渠道。胡润中国U40企业家财富榜将其个人财富记到约三百八十五亿元人民币。",
     "He founded Insta360 for panoramic and action cameras sold worldwide. Hurun’s China U40 wealth list put his fortune near CNY 38.5 billion.",
     "2025-09-01", "Hurun China U40 wealth / Rich List 2025", "https://hurun.net/zh-CN/Info/Detail?num=QXFSSPDDALAN", ["hurun_china_rich_2025", "hurun_u40_wealth_2025"]),
    ("zhang-junjie", "张俊杰", "Zhang Junjie", 30, 135, "霸王茶姬 Chagee", "China", "self_made", "餐饮", "Food & beverage",
     "他创办霸王茶姬，把新茶饮做成大规模连锁品牌，并冲刺资本市场。胡润称其为百富榜上少见的U30创业者，个人财富约一百三十五亿元人民币。",
     "He founded Chagee and scaled a new-tea chain toward public markets. Hurun called him a rare U30 founder on the China Rich List, near CNY 13.5 billion.",
     "2025-09-01", "Hurun China Rich List 2025", "https://hurun.net/zh-CN/Info/Detail?num=QXFSSPDDALAN", ["hurun_china_rich_2025", "hurun_u40_wealth_2025"]),
    ("wang-shuo", "王硕", "Wang Shuo", 35, 90, "Deel", "China / United States / Singapore", "self_made", "企业服务", "Enterprise HR/payroll",
     "他参与创办Deel，做跨境用工、合规与薪酬支付，服务远程与全球化团队。胡润中国榜将其财富记在约九十亿元人民币量级。",
     "He helped build Deel for cross-border hiring, compliance, and payroll for remote teams. Hurun China’s figure is about CNY 9 billion.",
     "2025-09-01", "Hurun China Rich List 2025", "https://hurun.net/zh-CN/Info/Detail?num=QXFSSPDDALAN", ["hurun_china_rich_2025", "hurun_global_u40_2026"]),
    ("yang-zhilin", "杨植麟", "Yang Zhilin", 32, 73, "月之暗面 Moonshot / Kimi", "China", "self_made", "人工智能", "Artificial intelligence",
     "他创办月之暗面，推出大模型产品Kimi，面向中文用户做长文本与智能助手。胡润U40企业家财富榜给出约七十三亿元人民币个人财富口径。",
     "He founded Moonshot AI and the Kimi model for Chinese users needing long-context assistants. Hurun’s U40 wealth list cites about CNY 7.3 billion.",
     "2025-09-01", "Hurun China U40 wealth 2025", "https://hurun.net/zh-CN/Info/Detail?num=QXFSSPDDALAN", ["hurun_u40_wealth_2025", "hurun_china_rich_2025"]),
    ("nie-yunchen", "聂云宸", "Nie Yunchen", 34, 70, "喜茶 Heytea", "China", "self_made", "餐饮", "Food & beverage",
     "他创办喜茶，把新式茶饮做成全国连锁并影响整个茶饮赛道定价与产品形态。胡润将其个人财富记在约七十亿元人民币。",
     "He founded Heytea and helped define China’s new-tea category nationwide. Hurun cites about CNY 7 billion in personal wealth.",
     "2025-09-01", "Hurun China Rich List 2025", "https://hurun.net/zh-CN/Info/Detail?num=QXFSSPDDALAN", ["hurun_china_rich_2025", "hurun_u40_wealth_2025"]),
    ("lu-jianxia", "陆剑霞", "Lu Jianxia", 32, 35, "Manner", "China", "self_made", "餐饮", "Coffee retail",
     "她联合创办Manner咖啡，用社区店模型做平价精品咖啡连锁。胡润常把夫妇财富合并披露，此处按可分拆下限口径记她一侧约三十五亿元，需继续核实。",
     "She cofounded Manner Coffee’s neighborhood espresso chain. Hurun often lists couple wealth together; this file uses a split lower-bound near CNY 3.5 billion pending finer disclosure.",
     "2025-09-01", "Hurun China Rich List 2025 (couple line item)", "https://hurun.net/zh-CN/Info/Detail?num=QXFSSPDDALAN", ["hurun_china_rich_2025", "hurun_global_u40_2026"]),
]

# Replace wang-xingxing if duplicate: founders didn't include wang-xingxing in USD list with conflict - china list has IPO figure which is better for display
# Remove justin duplicate issues - only one each via dict
by_id = {p["id"]: p for p in people}
for t in china:
    pid, zh, en, age, cny, co, country, sm, indzh, inden, bz, be, as_of, source, url, tags = t
    by_id[pid] = cny_row(pid, zh, en, age, cny, co, country, sm, indzh, inden, bz, be, as_of, source, url, tags)

# Fix james URL typo
if "james-dacombe" in by_id:
    by_id["james-dacombe"]["sourceUrl"] = (
        "https://www.forbes.com/sites/aliciapark/2026/08/15/"
        "british-ai-chip-founder-becomes-europes-youngest-self-made-billionaire/"
    )

people = list(by_id.values())
(ROOT / "data" / "people.json").write_text(json.dumps(people, ensure_ascii=False, indent=2) + "\n")
print("people", len(people))

# --- U30 / U40 boards from watchlist + young wealth ---
watch = json.loads((ROOT / "data" / "watchlist.json").read_text())


def enrich_watch(w: dict, band: str) -> dict:
    name = w["nameZh"]
    co = w.get("company", "")
    role = w.get("role", "")
    ind = w.get("industryZh", "")
    est = w.get("estimatedWorthNoteZh")
    bz = (
        f"{name}出现在胡润{band}相关年轻创业名单中，目前公开身份是{co}的{role or '核心成员'}，赛道偏{ind}。"
        f"该榜强调创业影响力，不等于已经公开亿级身价；若尚无福布斯/胡润财富数字，这里只作观察，预估身价标记为未公开。"
        f"后续若出现融资成交或权威富豪榜收录，再升入身价排序页。"
    )
    be = (
        f"{name} appears on Hurun’s {band} young-founder coverage as {role or 'a key member'} at {co}, in {ind}. "
        f"Entrepreneur lists measure influence, not a published billionaire fortune. "
        f"Estimated net worth stays unpublished here until a priced round or a major wealth list cites a number."
    )
    # trim/pad to ~100-200 Chinese chars
    if len(bz) < 100:
        bz += "这是长期追踪用的雷达名单，用来看1990年后谁在哪些赛道被官方创业榜反复点名。"
    return {
        **w,
        "band": band,
        "businessZh": bz[:200],
        "businessEn": be,
        "estimatedWorthZh": "预估身价：未公开（创业先锋榜，非财富榜）",
        "estimatedWorthEn": "Estimated net worth: not published (entrepreneur list, not a wealth ranking)",
    }


u30 = []
u40 = []
for w in watch:
    age = w.get("ageOnList") or 99
    if age <= 30:
        u30.append(enrich_watch(w, "U30/U40年轻段"))
    if age <= 40:
        u40.append(enrich_watch(w, "U40"))

# Add self-made / founder wealth people to U boards (exclude pure heirs).
# U30/U40 here = entrepreneurship boards; inherited fortunes stay on wealth pages only.
for p in people:
    if p.get("selfMade") == "not":
        continue
    age = 2026 - int(p["birthDate"][:4])
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
    if age <= 30:
        u30.append(card)
    if age <= 36:
        u40.append(card)

(ROOT / "data" / "u30.json").write_text(json.dumps(u30, ensure_ascii=False, indent=2) + "\n")
(ROOT / "data" / "u40.json").write_text(json.dumps(u40, ensure_ascii=False, indent=2) + "\n")
print("u30", len(u30), "u40", len(u40))
