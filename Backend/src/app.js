require("dotenv").config();
const http = require("http");
const app = require("./starter/callback");
const { startws } = require("./starter/ws-server");
const { startRateLimiterCleanup } = require("./utils/rateLimiter");

const PORT = process.env.PORT;
const server = http.createServer(app);

startws(server);

process.on("unhandledRejection", (err) => {
  console.log("Unhandled Rejection:", err);
});

process.on("uncaughtException", (err) => {
  console.log("Uncaught Exception:", err);
});

server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  startRateLimiterCleanup();
});