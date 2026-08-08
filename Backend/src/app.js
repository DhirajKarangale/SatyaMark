require("dotenv").config();
const http = require("http");
const app = require("./starter/callback");
const { startws } = require("./starter/ws-server");
const { startRateLimiterCleanup } = require("./utils/rateLimiter");
const { startJobTransfer } = require("./redis/jobTransfer");
const { startJanitorCycle } = require("./redis/jobJanitor");
const { startEnqueueJob } = require("./utils/enqueueJob");
const { initRedisClients } = require("./redis/redisClient");
const redisEventBus = require("./starter/redisEventBus");

const PORT = process.env.PORT;
const server = http.createServer(app);

startws(server);

process.on("unhandledRejection", (err) => {
  console.log("Unhandled Rejection:", err);
});

process.on("uncaughtException", (err) => {
  console.log("Uncaught Exception:", err);
});

server.listen(PORT, async () => {
  console.log(`Server running on port ${PORT}`);
  
  await initRedisClients();
  await redisEventBus.init();
  
  startRateLimiterCleanup();
  startEnqueueJob();
  startJobTransfer();
  startJanitorCycle();
});