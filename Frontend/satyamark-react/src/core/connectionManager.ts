import { SocketClient } from "./socketClient";
import { generateJobId } from "../utils/generateIds";
import { emitMessage, emitConnection } from "./eventBus";
import { getSessionId, setSessionId, clearSession } from "../utils/manageSessions";
import { initIcons } from "./status_controller";

const isDev = false;

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
      const sessionId = await getSessionId();

      socketClient?.send({
        type: "handshake",
        clientId: ctx.user_id,
        app_id: ctx.app_id,
        sessionId,
      });

      if (sessionId) {
        isConnected = true;
        isConnecting = false;
        emitConnection(ctx);
      }
    },

    onMessage: async (data) => {
      if (data.type === "session_created" && data.sessionId) {
        await setSessionId(data.sessionId);
        if (!isConnected) {
          isConnected = true;
          isConnecting = false;
          emitConnection(getContext());
        }
        return;
      }

      if (data.type === "RateLimiter") {
        if (data.msg === "Invalid session") {
          clearSession();
          socketClient?.close();
        }

        throw new Error(data.msg);
      }

      if (data.clientId === context?.user_id) {
        emitMessage(data);
      }
    },

    onClose: () => {
      if (!isConnected && !isConnecting) return;

      isConnected = false;
      isConnecting = false;

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
  const sessionId = await getSessionId();

  socketClient?.send({
    clientId: ctx.user_id,
    sessionId,
    jobId,
    text,
    image_url: imageUrl,
  });

  return jobId;
}
