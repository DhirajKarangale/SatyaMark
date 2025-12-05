require("dotenv").config();
const http = require("http");
const app = require("./starter/callback");
const { startws } = require("./starter/ws-server");

const PORT = process.env.PORT;  // use Render PORT
const server = http.createServer(app);

startws(server);   // pass server to WS

server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});














// require("dotenv").config();
// const http = require("http");
// const app = require("./starter/callback");
// const { startws, sendData } = require("./starter/ws-server");

// const PORT = process.env.PORT_CALLBACK;
// const server = http.createServer(app);

// startws();
// server.listen(PORT, () => { console.log(`Server running on port ${PORT}`); });