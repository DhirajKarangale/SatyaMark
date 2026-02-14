const WebSocket = require("ws");
const eventBus = require("./eventBus");
const process_task = require("../utils/process_task");
const { isAllowed } = require("../utils/rateLimiter");
const { generateSessionId } = require("../utils/generateIds");

let wss = null;
const clients = new Map();

function startws(server) {
  if (wss) return wss;

  wss = new WebSocket.Server({ server });

  wss.on("connection", (socket) => {
    socket.on("message", (msg) => {
      let data;
      try {
        data = JSON.parse(msg.toString());
      } catch {
        return;
      }

      if (data.type === "handshake" && data.clientId) {
        clientRegistration(data, socket);
        return;
      }

      if (!checkRateLimiter(data, socket)) return;

      process_task.getTask(data);
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

  eventBus.on("sendData", ({ clientId, payload }) => {
    const socket = clients.get(String(clientId));
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(payload));
    }
  });

  function clientRegistration(data, socket) {
    let sessionId = data.sessionId;

    if (!sessionId) {
      sessionId = generateSessionId(data.appId);

      socket.send(JSON.stringify({
        type: "session_created",
        sessionId
      }));
    }

    socket.sessionId = sessionId;
    socket.clientId = String(data.clientId);

    const existing = clients.get(String(data.clientId));
    if (existing && existing !== socket) {
      existing.close();
    }
    clients.set(String(data.clientId), socket);

    console.log("Client registered:", data.clientId);
  }

  function checkRateLimiter(data, socket) {
    if (!socket.sessionId) {
      socket.send(JSON.stringify({
        type: "RateLimiter",
        msg: "Session not established"
      }));
      return false;
    }

    if (data.sessionId !== socket.sessionId) {
      socket.send(JSON.stringify({
        type: "RateLimiter",
        msg: "Invalid session"
      }));
      return false;
    }

    if (!isAllowed(socket.sessionId)) {
      socket.send(JSON.stringify({
        type: "RateLimiter",
        msg: "Rate limit exceeded"
      }));
      return false;
    }

    return true;
  }

  return wss;
}

module.exports = { startws };