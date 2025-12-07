const WebSocket = require("ws");
const eventBus = require("./eventBus");
const process_task = require("../utils/process_task");

let wss = null;
const clients = new Map();

function startws(server) {
  if (wss) return wss;

  wss = new WebSocket.Server({ server });

  wss.on("connection", (socket) => {
    socket.on("message", (msg) => {
      let data;
      try {
        data = JSON.parse(msg);
      } catch {
        return;
      }

      if (data.type === "handshake" && data.clientId) {
        clients.set(String(data.clientId), socket);
        console.log("Client registered:", data.clientId);
        return;
      }

      console.log("Client message:", data.clientId);
      process_task.getTask(data);
    });

    socket.on("close", () => {
      for (const [id, s] of clients.entries()) {
        if (s === socket) clients.delete(id);
        console.log("Connection Closed: ", id);
      }
    });
  });

  eventBus.on("sendData", ({ clientId, payload }) => {
    const socket = clients.get(String(clientId));
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(payload));
    }
  });

  return wss;
}

module.exports = { startws };