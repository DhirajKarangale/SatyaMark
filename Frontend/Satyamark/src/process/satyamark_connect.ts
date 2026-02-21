import { getSessionId, setSessionId, clearSession } from "./manageSessions";

let socket: WebSocket | null = null;
let storedConnectionData: SatyaMarkConnectionData | null = null;

let isConnected = false;
type ConnectionListener = (connected: boolean) => void;
const connectionListeners: ConnectionListener[] = [];

const isDev = true;

async function getWsUrl() {
    const wsUrlLocal = "ws://localhost:1000";
    if (isDev) return wsUrlLocal;

    const res = await fetch(
        "https://dhirajkarangale.github.io/SatyaMark/ws.json",
        { cache: "no-store" }
    );

    const data = await res.json();
    return data.wsUrl;
}

export function onConnectionChange(cb: ConnectionListener) {
    connectionListeners.push(cb);
    return () => {
        const i = connectionListeners.indexOf(cb);
        if (i !== -1) connectionListeners.splice(i, 1);
    };
}

function notifyConnectionState(state: boolean) {
    isConnected = state;
    connectionListeners.forEach(cb => cb(state));
}

export function isSocketConnected() {
    return isConnected;
}

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

export async function init(connectionData: SatyaMarkConnectionData) {
    if (socket && socket.readyState == WebSocket.OPEN && storedConnectionData == connectionData) {
        console.log("Already Connected: ", connectionData);
        return;
    }

    const url = await getWsUrl();
    if (url) {
        socket = new WebSocket(url);
    }
    else {
        console.error("WebSocket endpoint resolution failed. Unable to establish connection.");
        return;
    }

    socket.onopen = async () => {
        const sessionId = await getSessionId();
        safeSend({
            type: "handshake",
            clientId: connectionData.user_id,
            app_id: connectionData.app_id,
            sessionId,
        });

        notifyConnectionState(true);

        console.log("Connected to server: ", connectionData.user_id);
    };

    socket.onmessage = async (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "session_created" && data.sessionId) {
            await setSessionId(data.sessionId);
            return;
        }

        if (data.type === "RateLimiter") {
            if (data.msg === "Invalid session") {
                clearSession();
                socket?.close();
                socket = null;
            }

            throw new Error(data.msg);
        }

        receiveData(JSON.parse(data));
    };

    socket.onclose = () => {
        console.log("Server connection closed");
    };

    storedConnectionData = connectionData;
}

function safeSend(msg: any) {
    if (!storedConnectionData) {
        console.log("No connectionData found. Call connect() first.");
        return;
    }

    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.log("Socket not ready");
        return;
    }

    socket.send(JSON.stringify(msg));
}

function generateJobId(app_id: string, user_id: string, dataId: string) {
    const timestamp = Date.now().toString(36);
    const random = crypto.getRandomValues(new Uint32Array(1))[0].toString(36);

    const jobId = `${app_id}_${user_id}_${dataId}_${timestamp}_${random}`;

    return jobId;
}

export async function sendData(text: string, image_url: string, dataId: string) {
    if (!storedConnectionData) {
        console.log("No connectionData found. Call connect() first.");
        return;
    }

    if (!socket || socket.readyState !== WebSocket.OPEN) {
        console.log("Socket not ready");
        return;
    }

    const { app_id, user_id } = storedConnectionData;
    const jobId = generateJobId(app_id, user_id, dataId);
    const sessionId = await getSessionId();

    const data = {
        clientId: user_id,
        jobId: jobId,
        text,
        image_url,
        sessionId
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