require("dotenv").config();
const http = require("http");
const app = require("./starter/callback");
const { startws, sendData } = require("./starter/ws-server");

const PORT = process.env.PORT_CALLBACK;
const server = http.createServer(app);

startws();
server.listen(PORT, () => { console.log(`Server running on port ${PORT}`); });