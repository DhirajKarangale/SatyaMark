import { getSessionData, setSessionData, clearSession } from "./manageSessions";

let socket: WebSocket | null = null;
let storedConnectionData: SatyaMarkConnectionData | null = null;
let hmacSecret: string = "";

let isConnected = false;
let reconnectAttempts = 0;
type ConnectionListener = (connected: boolean) => void;
const connectionListeners: ConnectionListener[] = [];

const isDev = import.meta.env.VITE_IS_DEV === "true";
const wsUrlLocal = import.meta.env.VITE_WS_URL_BASE;

async function getWsUrl() {
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

async function signPayload(fields: string): Promise<string> {
    if (!hmacSecret) {
        const data = await getSessionData();
        if (data.hmacSecret) {
            hmacSecret = data.hmacSecret;
        }
    }

    if (!hmacSecret) return "";

    const encoder = new TextEncoder();
    const key = await crypto.subtle.importKey(
        "raw",
        encoder.encode(hmacSecret),
        { name: "HMAC", hash: "SHA-256" },
        false,
        ["sign"]
    );
    const signature = await crypto.subtle.sign("HMAC", key, encoder.encode(fields));
    return btoa(String.fromCharCode(...new Uint8Array(signature)));
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
        console.log("WebSocket endpoint resolution failed. Unable to establish connection.");
        return;
    }

    socket.onopen = async () => {
        const { sessionId } = await getSessionData();
        safeSend({
            type: "handshake",
            clientId: connectionData.user_id,
            app_id: connectionData.app_id,
            sessionId,
        });

        if (sessionId) {
            notifyConnectionState(true);
        }

        reconnectAttempts = 0;
        console.log("Connected to server: ", connectionData.user_id);
    };

    socket.onmessage = async (event) => {
        const data = JSON.parse(event.data);

        if ((data.type === "session_created" || data.type === "session_confirmed") && data.hmacSecret) {
            hmacSecret = data.hmacSecret;

            if (data.type === "session_created" && data.sessionId) {
                await setSessionData(data.sessionId, data.hmacSecret);
            } else {
                const { sessionId } = await getSessionData();
                await setSessionData(sessionId, data.hmacSecret);
            }

            if (!isConnected) {
                notifyConnectionState(true);
            }
            return;
        }

        if (data.type === "RateLimiter") {
            if (data.msg === "Invalid session") {
                clearSession();
                socket?.close();
                socket = null;
            }
            console.error("RateLimiter Error:", data.msg);
            receiveData({ type: "error", error: data.msg });
            return;
        }

        receiveData(data);
    };

    socket.onclose = () => {
        console.log("Server connection closed");
        notifyConnectionState(false);
        setTimeout(() => {
            if (storedConnectionData) {
                console.log("Attempting to reconnect...");
                init(storedConnectionData);
            }
        }, Math.min(1000 * Math.pow(2, reconnectAttempts++), 30000));
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
        throw new Error("No connectionData found. Call connect() first.");
    }

    if (!socket || socket.readyState !== WebSocket.OPEN) {
        throw new Error("Socket not ready");
    }

    const { app_id, user_id } = storedConnectionData;
    const jobId = generateJobId(app_id, user_id, dataId);
    const { sessionId } = await getSessionData();

    const signString = `${user_id}:${sessionId}:${jobId}`;
    const hmac = await signPayload(signString);

    const data = {
        clientId: user_id,
        jobId: jobId,
        text,
        image_url,
        sessionId,
        hmac
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