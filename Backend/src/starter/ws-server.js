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





















// require("dotenv").config();
// const WebSocket = require("ws");
// const eventBus = require("./eventBus"); 
// const process_task = require("../utils/process_task")

// let wss = null;
// const clients = new Map();
// const PORT = process.env.PORT_WS || 8080;

// function startws() {
//   if (wss) return wss;

//   wss = new WebSocket.Server({ port: PORT });

//   wss.on("connection", (socket) => {
//     socket.on("message", (msg) => {
//       let data;
//       try {
//         data = JSON.parse(msg);
//       } catch (err) {
//         console.log("Invalid JSON from websocket client:", err);
//         return;
//       }

//       if (data && data.clientId) {
//         clients.set(String(data.clientId), socket);
//       }

//       process_task.getTask(data);
//     });

//     socket.on("close", () => {
//       for (const [id, s] of clients.entries()) {
//         if (s === socket) clients.delete(id);
//       }
//     });

//     socket.on("error", (err) => {
//       console.log("WebSocket error:", err);
//     });
//   });

//   eventBus.on("sendData", ({ clientId, payload }) => {
//     const id = String(clientId);
//     const socket = clients.get(id);
//     if (!socket) {
//       console.log(`No socket for client ${id}`);
//       return;
//     }
//     if (socket.readyState === WebSocket.OPEN) {
//       try {
//         socket.send(JSON.stringify(payload));
//       } catch (err) {
//         console.log("Failed to send message:", err);
//       }
//     } else {
//       console.log(`Socket not open for client ${id}`);
//     }
//   });

//   return wss;
// }

// module.exports = { startws };