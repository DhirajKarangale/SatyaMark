import { SocketClient } from "./socketClient";
import { generateJobId } from "../utils/generateIds";
import { emitMessage, emitConnection } from "./eventBus";
import { getSessionData, setSessionData, clearSession } from "../utils/manageSessions";
import { initIcons } from "./status_controller";

const isDev = true;

type ConnectionContext = {
  app_id: string;
  user_id: string;
};

let context: ConnectionContext | null = null;
let socketClient: SocketClient | null = null;

let isConnecting = false;
let isConnected = false;
let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
let reconnectAttempts = 0;

let hmacSecret: string = "";
let handshakeTimer: ReturnType<typeof setTimeout> | null = null;
let pingInterval: ReturnType<typeof setInterval> | null = null;
let pongTimeout: ReturnType<typeof setTimeout> | null = null;

/* -------------------------------------------------------------------------- */
/*                          WebSocket URL Resolution                          */
/* -------------------------------------------------------------------------- */

async function resolveWsUrl(): Promise<string> {
  if (isDev) {
    const wsUrl = "ws://localhost:2402";
    return wsUrl;
  }

  const res = await fetch(
    "https://dhirajkarangale.github.io/SatyaMark/ws.json",
    { cache: "no-store" }
  );

  const data = await res.json();
  const wsUrl = data.wsUrl;

  if (!wsUrl) throw new Error("Satyamark: WebSocket URL resolution failed");

  return wsUrl;
}

/* -------------------------------------------------------------------------- */
/*                          HMAC Signing (Issue 1)                            */
/* -------------------------------------------------------------------------- */

async function signPayload(fields: string): Promise<string> {
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

/* -------------------------------------------------------------------------- */
/*                                Connection                                  */
/* -------------------------------------------------------------------------- */

export async function init(newContext: ConnectionContext) {
  context = newContext;
  initIcons();
  await connect();
}

async function connect() {
  if (isConnecting || isConnected) return;

  isConnecting = true;

  let url;
  try {
    url = await resolveWsUrl();
  } catch (error) {
    console.error("Satyamark: Failed to resolve WebSocket URL", error);
    isConnecting = false;
    scheduleReconnect();
    return;
  }

  socketClient = new SocketClient(url, {
    onOpen: async () => {
      reconnectAttempts = 0;
      const ctx = getContext();
      const { sessionId } = await getSessionData();

      socketClient?.send({
        type: "handshake",
        clientId: ctx.user_id,
        app_id: ctx.app_id,
        sessionId,
      });

      // Issue 5: Handshake timeout — if no response in 10s, reconnect
      handshakeTimer = setTimeout(() => {
        console.warn("Satyamark: Handshake timeout. Reconnecting...");
        handshakeTimer = null;
        socketClient?.close();
      }, 10000);
    },

    onMessage: async (data) => {
      // Issue 16: Handle pong response
      if (data.type === "pong") {
        if (pongTimeout) {
          clearTimeout(pongTimeout);
          pongTimeout = null;
        }
        return;
      }

      // Issue 1: Handle session_created (new user) or session_confirmed (returning user)
      if ((data.type === "session_created" || data.type === "session_confirmed") && data.hmacSecret) {
        if (handshakeTimer) {
          clearTimeout(handshakeTimer);
          handshakeTimer = null;
        }

        hmacSecret = data.hmacSecret;

        if (data.type === "session_created" && data.sessionId) {
          await setSessionData(data.sessionId, data.hmacSecret);
        } else {
          // Returning user: update hmacSecret in cookie, keep existing sessionId
          const { sessionId } = await getSessionData();
          await setSessionData(sessionId, data.hmacSecret);
        }

        if (!isConnected) {
          isConnected = true;
          isConnecting = false;
          emitConnection(getContext());
          startPing();
        }
        return;
      }

      // Issue 4: Don't throw on RateLimiter errors — handle gracefully
      if (data.type === "RateLimiter") {
        console.warn("Satyamark RateLimiter:", data.msg);

        if (data.msg === "Invalid session") {
          clearSession();
          socketClient?.close();
        }
        return;
      }

      if (data.clientId === context?.user_id) {
        emitMessage(data);
      }
    },

    onClose: () => {
      stopPing();
      if (handshakeTimer) {
        clearTimeout(handshakeTimer);
        handshakeTimer = null;
      }

      if (!isConnected && !isConnecting) return;

      isConnected = false;
      isConnecting = false;
      hmacSecret = "";

      emitConnection(null);
      scheduleReconnect();
    },

    onError: () => {
      socketClient?.close();
    },
  });

  try {
    socketClient.connect();
  } catch (error) {
    console.error("Satyamark: Failed to connect WebSocket", error);
    isConnecting = false;
    scheduleReconnect();
  }
}

/* -------------------------------------------------------------------------- */
/*                    Application-Level Keepalive (Issue 16)                   */
/* -------------------------------------------------------------------------- */

function startPing() {
  stopPing();
  pingInterval = setInterval(() => {
    if (!socketClient || !isConnected) return;

    try {
      socketClient.send({ type: "ping" });
    } catch {
      return;
    }

    pongTimeout = setTimeout(() => {
      console.warn("Satyamark: Pong timeout. Reconnecting...");
      pongTimeout = null;
      socketClient?.close();
    }, 5000);
  }, 25000);
}

function stopPing() {
  if (pingInterval) {
    clearInterval(pingInterval);
    pingInterval = null;
  }
  if (pongTimeout) {
    clearTimeout(pongTimeout);
    pongTimeout = null;
  }
}

/* -------------------------------------------------------------------------- */
/*                              Reconnection                                  */
/* -------------------------------------------------------------------------- */

function scheduleReconnect() {
  if (reconnectTimer || !context) return;

  const baseDelay = 2000;
  const maxDelay = 30000;
  const delay = Math.min(baseDelay * Math.pow(2, reconnectAttempts), maxDelay);

  reconnectAttempts++;

  reconnectTimer = setTimeout(() => {
    reconnectTimer = null;
    void connect();
  }, delay);
}

function getContext(): ConnectionContext {
  if (!context?.app_id || !context?.user_id) {
    throw new Error("Satyamark: Invalid app_id and user_id in init()");
  }

  return context;
}

/* -------------------------------------------------------------------------- */
/*                                  Sending                                   */
/* -------------------------------------------------------------------------- */

export async function sendJob(text: string, imageUrl: string, dataId: string): Promise<string> {
  const ctx = getContext();
  const jobId = generateJobId(ctx.app_id, ctx.user_id, dataId);
  const { sessionId } = await getSessionData();

  // Issue 18: Derive type from content
  const hasImage = typeof imageUrl === "string" && imageUrl.trim().length > 0;
  const type = hasImage ? "image" : "text";

  // Issue 1: HMAC signing — sign clientId:sessionId:jobId
  const signString = `${ctx.user_id}:${sessionId}:${jobId}`;
  const hmac = await signPayload(signString);

  socketClient?.send({
    clientId: ctx.user_id,
    sessionId,
    jobId,
    text,
    image_url: imageUrl,
    type,
    hmac,
  });

  return jobId;
}
