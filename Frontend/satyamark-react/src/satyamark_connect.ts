const wsUrl = "wss://satyamark.onrender.com";
// const wsUrl = "ws://localhost:1000";
let socket: WebSocket | null = null;
let storedConnectionData: SatyaMarkConnectionData | null = null;

export type SatyaMarkConnectionData = {
    app_id: string;
    user_id: string;
};

type ConnectedCallback = (data: SatyaMarkConnectionData) => void;
type ReceiveCallback = (data: any) => void;

const listeners: ReceiveCallback[] = [];
let onConnectedCb: ConnectedCallback | null = null;

export function onReceive(cb: ReceiveCallback) {
    listeners.push(cb);
    return () => {
        const idx = listeners.indexOf(cb);
        if (idx !== -1) listeners.splice(idx, 1);
    };
}

export function onConnected(cb: ConnectedCallback) {
    onConnectedCb = cb;
}

export function init(connectionData: SatyaMarkConnectionData, options?: { onConnected?: ConnectedCallback }) {
    if (socket && socket.readyState == WebSocket.OPEN && storedConnectionData == connectionData) {
        console.log("Already Connected: ", connectionData);
        return;
    }

    socket = new WebSocket(wsUrl);
    onConnectedCb = options?.onConnected ?? onConnectedCb;

    socket.onopen = () => {
        console.log("Connected to server: ", connectionData.user_id);

        safeSend({
            type: "handshake",
            clientId: connectionData.user_id,
            appId: connectionData.app_id
        });

        onConnectedCb?.(connectionData);
    };

    socket.onmessage = (event) => {
        receiveData(JSON.parse(event.data));
    };

    socket.onclose = () => {
        console.log("Server connection closed");
    };

    storedConnectionData = connectionData;
}

function isSocketOpen() {
    return socket && socket.readyState === WebSocket.OPEN;
}

function assert(condition: any, message: string): asserts condition {
    if (!condition) throw new Error(message);
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

function uniqueTimestamp() {
    const now = new Date();

    const yyyy = now.getFullYear();
    const MM = String(now.getMonth() + 1).padStart(2, "0");
    const dd = String(now.getDate()).padStart(2, "0");

    const hh = String(now.getHours()).padStart(2, "0");
    const mm = String(now.getMinutes()).padStart(2, "0");
    const ss = String(now.getSeconds()).padStart(2, "0");
    const ms = String(now.getMilliseconds()).padStart(3, "0");

    const micro = String(Math.floor(Math.random() * 1000)).padStart(3, "0");

    return `${yyyy}${MM}${dd}${hh}${mm}${ss}${ms}${micro}`;
}

export function sendData(text: string, image_url: string, dataId: string) {
    if (!storedConnectionData) {
        console.log("No connectionData found. Call connect() first.");
        return;
    }

    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.log("Socket not ready");
        return;
    }

    assert(storedConnectionData, "Call init() before sendData()");
    assert(isSocketOpen(), "WebSocket is not ready");
    assert(dataId, "dataId is required");
    assert(text || image_url, "Provide text or image_url");

    if (text) assert(text.trim().length >= 3, "Text must be at least 3 characters");

    const { app_id, user_id } = storedConnectionData;
    const timestamp = uniqueTimestamp();
    const jobId = `${app_id}_${user_id}_${dataId}_${timestamp}`;

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

    for (const cb of Array.from(listeners)) {
        try {
            cb(data);
        } catch (err) {
            console.log("listener error", err);
        }
    }
}