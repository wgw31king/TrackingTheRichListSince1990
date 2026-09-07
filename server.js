const http = require("http");
const fs = require("fs");
const path = require("path");
const { refreshNews, loadNews } = require("./lib/refreshNews");

const ROOT = __dirname;
const PUBLIC = path.join(ROOT, "public");
const PORT = Number(process.env.PORT || 8787);

function send(res, status, body, type = "application/json; charset=utf-8") {
  res.writeHead(status, {
    "content-type": type,
    "cache-control": "no-store"
  });
  res.end(body);
}

function sendJson(res, status, obj) {
  send(res, status, JSON.stringify(obj, null, 2));
}

function readPeople() {
  return JSON.parse(fs.readFileSync(path.join(ROOT, "data", "people.json"), "utf8"));
}

function readWatchlist() {
  const file = path.join(ROOT, "data", "watchlist.json");
  if (!fs.existsSync(file)) return [];
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function readJsonList(name) {
  const file = path.join(ROOT, "data", name);
  if (!fs.existsSync(file)) return [];
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function readStats() {
  const file = path.join(ROOT, "data", "stats.json");
  if (!fs.existsSync(file)) return {};
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function mime(file) {
  const ext = path.extname(file);
  return (
    {
      ".html": "text/html; charset=utf-8",
      ".css": "text/css; charset=utf-8",
      ".js": "text/javascript; charset=utf-8",
      ".json": "application/json; charset=utf-8",
      ".svg": "image/svg+xml"
    }[ext] || "application/octet-stream"
  );
}

function serveStatic(req, res) {
  let urlPath = decodeURIComponent(req.url.split("?")[0]);
  if (urlPath === "/") urlPath = "/index.html";
  const file = path.normalize(path.join(PUBLIC, urlPath));
  if (!file.startsWith(PUBLIC)) {
    send(res, 403, "Forbidden", "text/plain");
    return;
  }
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) {
    send(res, 404, "Not found", "text/plain");
    return;
  }
  send(res, 200, fs.readFileSync(file), mime(file));
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://127.0.0.1:${PORT}`);

  if (req.method === "GET" && url.pathname === "/api/people") {
    sendJson(res, 200, { people: readPeople() });
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/watchlist") {
    sendJson(res, 200, { watchlist: readWatchlist() });
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/u30") {
    sendJson(res, 200, { u30: readJsonList("u30.json") });
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/u40") {
    sendJson(res, 200, { u40: readJsonList("u40.json") });
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/stats") {
    sendJson(res, 200, readStats());
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/news") {
    sendJson(res, 200, loadNews());
    return;
  }

  if (req.method === "POST" && url.pathname === "/api/refresh") {
    try {
      const result = await refreshNews(new Date());
      sendJson(res, 200, { ok: true, ...result, news: loadNews() });
    } catch (err) {
      sendJson(res, 500, { ok: false, error: String(err.message || err) });
    }
    return;
  }

  if (req.method === "GET" || req.method === "HEAD") {
    serveStatic(req, res);
    return;
  }

  send(res, 405, "Method not allowed", "text/plain");
});

if (process.argv.includes("--refresh-once")) {
  refreshNews(new Date())
    .then((r) => {
      console.log(JSON.stringify(r, null, 2));
      process.exit(0);
    })
    .catch((err) => {
      console.error(err);
      process.exit(1);
    });
} else {
  server.listen(PORT, "127.0.0.1", () => {
    console.log(`Wealth tracker: http://127.0.0.1:${PORT}`);
    console.log("Open that address, then use 榜单消息 → 刷新.");
  });
}
