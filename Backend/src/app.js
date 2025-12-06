require("dotenv").config();
const http = require("http");
const app = require("./starter/callback");
const { startws } = require("./starter/ws-server");

const PORT = process.env.PORT;  
const server = http.createServer(app);

startws(server);   

server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});