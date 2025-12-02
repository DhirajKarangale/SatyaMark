require("dotenv").config();
const WebSocket = require("ws");
const process_task = require('../utils/process_task');

let wss = null;
let clients = new Map();
const PORT = process.env.PORT_WS;

function startws() {
  if (wss) return wss;

  wss = new WebSocket.Server({ port: PORT });

  wss.on("connection", (socket) => {

    socket.on("message", (msg) => {
      const data = JSON.parse(msg);
      process_task.getTask(data);

      if (data.clientId) {
        const id = String(data.clientId);
        clients.set(id, socket);
      }
    });

    socket.on("close", () => {
      for (const [id, s] of clients.entries()) {
        if (s === socket) clients.delete(id);
      }
    });
  });

  return wss;
}

function sendData(clientId, data) {
  const id = String(clientId);
  const socket = clients.get(id);
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(data));
  }
}

module.exports = { startws, sendData };