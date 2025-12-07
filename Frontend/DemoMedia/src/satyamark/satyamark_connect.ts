// const wsUrl = "wss://satyamark.onrender.com";
const wsUrl = "ws://localhost:1000";
let socket: WebSocket | null = null;
let storedConnectionData: SatyaMarkConnectionData | null = null;

export type SatyaMarkConnectionData = {
    app_id: string;
    user_id: string;
};

type ReceiveCallback = (data: any) => void;
const listeners: ReceiveCallback[] = [];

export function onReceive(cb: ReceiveCallback) {
    listeners.push(cb);
    return () => {
        const idx = listeners.indexOf(cb);
        if (idx !== -1) listeners.splice(idx, 1);
    };
}

export function connect(connectionData: SatyaMarkConnectionData) {
    storedConnectionData = connectionData;

    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        console.log("Connected to server");

        safeSend({
            type: "handshake",
            clientId: connectionData.user_id,
            appId: connectionData.app_id
        });
    };

    socket.onmessage = (event) => {
        receiveData(JSON.parse(event.data));
    };

    socket.onclose = () => {
        console.log("Server connection closed");
    };
}

function safeSend(msg: any) {
    if (!storedConnectionData) {
        console.warn("No connectionData found. Call connect() first.");
        return;
    }

    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.warn("Socket not ready");
        return;
    }

    socket.send(JSON.stringify(msg));
}

export function sendData(text: string, image_url: string) {
    if (!storedConnectionData) {
        console.warn("No connectionData found. Call connect() first.");
        return;
    }

    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.warn("Socket not ready");
        return;
    }

    const { app_id, user_id } = storedConnectionData;
    const timestamp = Date.now();
    const jobId = `${app_id}_${user_id}_${timestamp}`;

    const data = {
        clientId: user_id,
        jobId: jobId,
        text,
        image_url
    };

    socket.send(JSON.stringify(data));

    return jobId;
}

export function receiveData(data: any) {
    if (!storedConnectionData || data.clientId != storedConnectionData.user_id) return;

    const payload = {
        jobId: data.jobId,
        dataId: data.dataId,
        mark: data.mark,
    }

    for (const cb of Array.from(listeners)) {
        try {
            cb(payload);
        } catch (err) {
            console.error("listener error", err);
        }
    }
}