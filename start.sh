#!/bin/zsh
cd "$(dirname "$0")"
PORT=8787
if lsof -nP -iTCP:$PORT -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Already running: http://127.0.0.1:$PORT"
  exit 0
fi
nohup /opt/homebrew/bin/node server.js >> /tmp/wealth-tracker.log 2>&1 &
echo "Started PID $! — open http://127.0.0.1:$PORT"
