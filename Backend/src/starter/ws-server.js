const WebSocket = require("ws");
const eventBus = require("./eventBus");
const process_task = require("../utils/process_task");

let wss = null;
const clients = new Map();

function startws(server) {
  if (wss) return wss;

  wss = new WebSocket.Server({ server });

  wss.on("connection", (socket) => {
    console.log("Client connected");

    socket.on("message", (msg) => {
      let data;
      try {
        data = JSON.parse(msg);
      } catch {
        return;
      }

      if (data.clientId) clients.set(String(data.clientId), socket);

      process_task.getTask(data);
    });

    socket.on("close", () => {
      for (const [id, s] of clients.entries()) {
        if (s === socket) clients.delete(id);
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