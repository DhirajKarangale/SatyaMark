const WebSocket = require("ws");
const redisEventBus = require("./redisEventBus");
const process_task = require("../utils/process_task");
const { generateSessionId } = require("../utils/generateIds");

function heartbeat() {
  this.isAlive = true;
}

let wss = null;
const clients = new Map();

function startws(server) {
  if (wss) return wss;

  wss = new WebSocket.Server({ server });

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

  function clientRegistration(data, socket) {
    let sessionId = data.sessionId;

    if (!sessionId) {
      sessionId = generateSessionId(data.app_id);

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

  return wss;
}

module.exports = { startws };