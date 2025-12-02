let socket: WebSocket | null = null;

export function connect() {
    socket = new WebSocket("ws://localhost:2402");
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