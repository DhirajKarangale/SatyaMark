// ws-server.js
const WebSocket = require("ws");
const redis = require("redis");
const jwt = require("jsonwebtoken");
const { promisify } = require("util");
require("dotenv").config();

const REDIS_URL = process.env.REDIS_URL;
const JWT_SECRET = process.env.JWT_SECRET || "dev-jwt-secret";

const r = redis.createClient({ url: REDIS_URL });
r.connect().catch(console.error);

const wss = new WebSocket.Server({ noServer: true });

// map userId -> set of ws (in-memory)
const userSockets = new Map();

function addSocket(userId, ws) {
  const s = userSockets.get(userId) || new Set();
  s.add(ws);
  userSockets.set(userId, s);
}
function removeSocket(userId, ws) {
  const s = userSockets.get(userId);
  if (!s) return;
  s.delete(ws);
  if (s.size === 0) userSockets.delete(userId);
}

wss.on("connection", (ws, req, userId) => {
  addSocket(userId, ws);

  ws.on("close", () => {
    removeSocket(userId, ws);
  });
});

// helper to broadcast result to a user
function notifyUser(userId, payload) {
  const s = userSockets.get(userId);
  if (!s) return;
  const msg = JSON.stringify(payload);
  for (const ws of s) {
    if (ws.readyState === WebSocket.OPEN) ws.send(msg);
  }
}

module.exports = { wss, notifyUser };