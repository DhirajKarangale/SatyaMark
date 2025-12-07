let socket: WebSocket | null = null;
import { urlBase } from "./APIs";

const wsUrl = urlBase.replace(/^http/, "ws");

export function connect() {
    socket = new WebSocket(wsUrl);
    socket.onopen = () => { };
    socket.onmessage = (event) => { receiveData(JSON.parse(event.data)); };
    socket.onclose = () => { };
}

export function sendData(data: any) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(data));
    } else {
        console.warn("Socket not ready");
    }
}

export function receiveData(data: any) {
    console.log("Received:", data);
}