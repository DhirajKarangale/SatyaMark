const { initWebSocketServer, sendData } = require('./ws-server');

initWebSocketServer()

setTimeout(() => {
    sendData("123", "Hello from backend test");
}, 10000);