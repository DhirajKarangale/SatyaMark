import { SocketClient } from "./socketClient";
import { generateJobId } from "../utils/generateIds";
import { emitMessage, emitConnection } from "./eventBus";
import { getSessionId, setSessionId, clearSession } from "../utils/manageSessions";

const isDev = true;

type ConnectionContext = {
  app_id: string;
  user_id: string;
};

let context: ConnectionContext | null = null;
let socketClient: SocketClient | null = null;

/* -------------------------------------------------------------------------- */
/*                          WebSocket URL Resolution                          */
/* -------------------------------------------------------------------------- */

async function resolveWsUrl(): Promise<string> {
  if (isDev) {
    const wsUrl = "ws://localhost:1000";
    return wsUrl;
  }

  const res = await fetch(
    "https://dhirajkarangale.github.io/SatyaMark/ws.json",
    { cache: "no-store" }
  );

  const data = await res.json();
  const wsUrl = data.wsUrl;

  if (!wsUrl) throw new Error("WebSocket URL resolution failed");

  return wsUrl;
}

/* -------------------------------------------------------------------------- */
/*                                Connection                                  */
/* -------------------------------------------------------------------------- */

export async function init(newContext: ConnectionContext) {
  if (!newContext?.app_id || !newContext?.user_id) {
    throw new Error("init() requires valid app_id and user_id");
  }
  
  context = newContext;

  const url = await resolveWsUrl();

  socketClient = new SocketClient(url, {
    onOpen: async () => {
      const sessionId = await getSessionId();

      socketClient?.send({
        type: "handshake",
        clientId: context?.user_id,
        app_id: context?.app_id,
        sessionId,
      });

      emitConnection(context);
    },

    onMessage: async (data) => {
      if (data.type === "session_created" && data.sessionId) {
        await setSessionId(data.sessionId);
        return;
      }

      if (data.type === "RateLimiter") {
        if (data.msg === "Invalid session") {
          clearSession();
          socketClient?.close();
          emitConnection(null);
          init(context!);
        }
        return;
      }

      if (data.clientId === context?.user_id) {
        emitMessage(data);
      }
    },

    onClose: () => {
      emitConnection(null);
    },

    onError: () => {
      socketClient?.close();
    },
  });

  socketClient.connect();
}

/* -------------------------------------------------------------------------- */
/*                                  Sending                                   */
/* -------------------------------------------------------------------------- */

export async function sendJob(text: string, imageUrl: string, dataId: string): Promise<string> {
  if (!context) throw new Error("Satyamark is not ready Call init() first");

  if (!text && !imageUrl) {
    throw new Error("Provide text or imageUrl");
  }

  if (text && text.trim().length < 3) {
    throw new Error("Text must be at least 3 characters");
  }

  const jobId = generateJobId(context.app_id, context.user_id, dataId);
  const sessionId = await getSessionId();

  socketClient?.send({
    clientId: context.user_id,
    sessionId,
    jobId,
    text,
    image_url: imageUrl,
  });

  return jobId;
}
