import { preloadIcons } from "./utils/iconLoader";
import { encrypt, decrypt } from "./satyamark_encryption";
import { setCookie, getCookie } from "./satyamark_storage";

const wsUrlLocal = "ws://localhost:1000";
let wsUrl: string | null = null;

let socket: WebSocket | null = null;
let storedConnectionData: SatyaMarkConnectionData | null = null;

export type SatyaMarkConnectionData = {
    app_id: string;
    user_id: string;
};

type ConnectedCallback = (data: SatyaMarkConnectionData | null) => void;
type ReceiveCallback = (data: any) => void;

const listeners: ReceiveCallback[] = [];
let onConnectedCb: ConnectedCallback | null = null;

async function getWsUrl() {
    if (wsUrl) return wsUrl;

    const res = await fetch(
        "https://dhirajkarangale.github.io/SatyaMark/ws.json",
        { cache: "no-store" }
    );

    const data = await res.json();
    wsUrl = data.wsUrl;
    // wsUrl = wsUrlLocal;
    return wsUrl;
}

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

export async function init(connectionData: SatyaMarkConnectionData, options?: { onConnected?: ConnectedCallback }) {
    preloadIcons();

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

    onConnectedCb = options?.onConnected ?? onConnectedCb;

    socket.onopen = async () => {
        console.log("Connected to server: ", connectionData.user_id);
        const sessionId = await getSessionId();

        safeSend({
            type: "handshake",
            clientId: connectionData.user_id,
            appId: connectionData.app_id,
            sessionId: sessionId
        });

        onConnectedCb?.(connectionData);
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === "session_created" && data.sessionId) {
            setSessionId(data);
            return;
        }

        if (data.type === "RateLimiter") {
            console.warn("Rate limited:", data.msg);

            if (data.msg === "Invalid session") {
                setCookie("satya_session", "", -1);
                socket?.close();
                onConnectedCb?.(null);
                init(storedConnectionData!);
            }

            return;
        }

        receiveData(data);
    };

    socket.onclose = () => {
        console.log("Server connection closed");
    };

    storedConnectionData = connectionData;
}

async function ensureConnection() {
    if (
        socket &&
        (socket.readyState === WebSocket.OPEN ||
            socket.readyState === WebSocket.CONNECTING)
    ) {
        return;
    }

    if (!storedConnectionData) {
        console.log("No connection data available");
        return;
    }

    await init(storedConnectionData);

    await waitForOpen();
}

function waitForOpen(): Promise<void> {
    return new Promise((resolve, reject) => {
        if (!socket) return reject();

        if (socket.readyState === WebSocket.OPEN) {
            return resolve();
        }

        socket.addEventListener("open", () => resolve(), { once: true });
        socket.addEventListener("error", reject, { once: true });
    });
}

function isSocketOpen() {
    return socket && socket.readyState === WebSocket.OPEN;
}

function assert(condition: any, message: string): asserts condition {
    if (!condition) throw new Error(message);
}

function safeSend(msg: any) {
    if (!storedConnectionData) {
        console.warn("No connectionData found.");
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

async function getSessionId() {
    let sessionId = getCookie("satya_session");

    if (sessionId) {
        try {
            sessionId = await decrypt(sessionId);
        } catch {
            sessionId = "";
        }
    } else {
        sessionId = "";
    }

    return sessionId;
}

async function setSessionId(data: any) {
    const encrypted = await encrypt(data.sessionId);
    setCookie("satya_session", encrypted);
}

export async function sendData(text: string, image_url: string, dataId: string) {
    if (!storedConnectionData) {
        console.log("No connectionData found. Call connect() first.");
        return;
    }

    await ensureConnection();

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

    const sessionId = await getSessionId();

    const data = {
        clientId: user_id,
        sessionId: sessionId,
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