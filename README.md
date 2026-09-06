# Tracking The Rich List Since 1990

本地追踪 **1990 年及以后出生** 的人（含 00 后）。

## 两层数据（重要）

1. **富豪榜**（`data/people.json`）  
   有可引用身价：福布斯实时/年榜、胡润百富或中国 U40 企业家财富、新财富等。

2. **观察名单**（`data/watchlist.json`）  
   胡润 U40「创业先锋」等：人在榜，但**没有公开身价**。不当富豪排序。

U30 / U40 / 独角兽 ≠ 自动有身价。身价只认成交估值或权威富豪榜。

## 怎么跑

```bash
cd ~/wealth-tracker
node server.js
```

打开 http://127.0.0.1:8787

导航：榜单消息 → 按身价 → 按年龄 → 观察名单

## 推送仓库

```bash
git remote add origin https://github.com/wgw31king/TrackingTheRichListSince1990.git
git push -u origin main
```

若本机 `.git` 初始化失败，在项目目录手动 `git init` 后再推。
