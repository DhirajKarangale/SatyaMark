const wsUrl = "wss://satyamark.onrender.com";
// const wsUrl = "ws://localhost:1000";
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

    // console.log("Send: ", data);
    socket.send(JSON.stringify(data));

    return jobId;
}

export function receiveData(data: any) {
    // console.log("Received:", data);

    for (const cb of Array.from(listeners)) {
        try {
            cb(data);
        } catch (err) {
            console.error("listener error", err);
        }
    }
}


/*

{
    "jobId": "APP123_USER999_1765119655256",
    "clientId": "USER999",
    "image_url": "https://picsum.photos/600/400?99",
    "image_hash": "f12bd6449274fe7c898d7b91b2eb35faba2bad53720182454ad68bb656633844",
    "mark": "AI",
    "reason": "High GAN artifacts and manipulation detected despite weak sensor and present EXIF.",
    "confidence": 0.7
}

*/