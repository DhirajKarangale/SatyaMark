const WebSocket = require("ws");
const crypto = require("crypto");
const redisEventBus = require("./redisEventBus");
const process_task = require("../utils/process_task");
const { generateSessionId, generateHmacSecret } = require("../utils/generateIds");

function heartbeat() {
  this.isAlive = true;
}

let wss = null;
const clients = new Map();

function startws(server) {
  if (wss) return wss;

  wss = new WebSocket.Server({ server, maxPayload: 1024 * 1024 });

  wss.on("connection", (socket) => {
    socket.isAlive = true;
    socket.on('pong', heartbeat);
    socket.on("message", (msg) => {

      let data;
      try {
        data = JSON.parse(msg.toString());
      } catch {
        return;
      }

      if (!data) return;

      if (data.type === "handshake" && data.clientId) {
        clientRegistration(data, socket);
        return;
      }

      // Issue 16: Respond to application-level ping
      if (data.type === "ping") {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({ type: "pong" }));
        }
        return;
      }

      // Issue 7: Validate clientId matches registered socket
      if (data.clientId !== socket.clientId) {
        return;
      }

      // Issue 1: Verify HMAC signature
      if (!verifyHmac(data, socket.hmacSecret)) {
        console.log("HMAC verification failed for client:", socket.clientId);
        return;
      }

      process_task.getTask(data, socket.sessionId);
    });

    socket.on("close", () => {
      for (const [id, s] of clients.entries()) {
        if (s === socket) {
          clients.delete(id);
          console.log("Connection Closed: ", id);
          break;
        }
      }
    });
  });

  const interval = setInterval(function ping() {
    wss.clients.forEach(function each(ws) {
      if (ws.isAlive === false) {
        // Find and remove from clients map if it exists
        for (const [id, s] of clients.entries()) {
          if (s === ws) {
            clients.delete(id);
            break;
          }
        }
        return ws.terminate();
      }

      ws.isAlive = false;
      ws.ping();
    });
  }, 30000);

  wss.on('close', function close() {
    clearInterval(interval);
  });

  redisEventBus.on("sendData", ({ clientId, payload }) => {
    const socket = clients.get(String(clientId));
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(payload));
    }
  });

  // Issue 1: HMAC verification using timing-safe comparison
  function verifyHmac(data, secret) {
    if (!secret || !data.hmac) return false;

    const signString = `${data.clientId}:${data.sessionId}:${data.jobId}`;
    const expected = crypto.createHmac("sha256", secret)
      .update(signString)
      .digest("base64");

    try {
      return crypto.timingSafeEqual(
        Buffer.from(data.hmac, "base64"),
        Buffer.from(expected, "base64")
      );
    } catch {
      return false;
    }
  }

  function clientRegistration(data, socket) {
    let sessionId = data.sessionId;

    // Issue 1: Always generate HMAC secret per connection, stored on socket
    const hmacSecret = generateHmacSecret();

    if (!sessionId) {
      sessionId = generateSessionId(data.app_id);

      socket.send(JSON.stringify({
        type: "session_created",
        sessionId,
        hmacSecret,
      }));
    } else {
      // Returning user: confirm session and issue new HMAC secret
      socket.send(JSON.stringify({
        type: "session_confirmed",
        hmacSecret,
      }));
    }

    socket.sessionId = sessionId;
    socket.clientId = String(data.clientId);
    socket.hmacSecret = hmacSecret;

    const existing = clients.get(String(data.clientId));
    if (existing && existing !== socket) {
      existing.close();
    }
    clients.set(String(data.clientId), socket);

    console.log("Client registered:", data.clientId);
  }

  return wss;
}

module.exports = { startws };