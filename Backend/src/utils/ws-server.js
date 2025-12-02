require("dotenv").config();
const WebSocket = require("ws");

let wss = null;
let clients = new Map();
const PORT = process.env.PORT;

function initWebSocketServer() {
  if (wss) return wss;

  wss = new WebSocket.Server({ port: PORT });

  wss.on("connection", (socket) => {

    socket.on("message", (msg) => {
      const data = JSON.parse(msg);
      receivedData(data);
      
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

function receivedData(data) {
  console.log("Data Rec: ", data);
  
}

module.exports = { initWebSocketServer, sendData };