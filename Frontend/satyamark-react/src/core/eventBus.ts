/* -------------------------------------------------------------------------- */
/*                                   Types                                    */
/* -------------------------------------------------------------------------- */

export type ServerMessage = {
  type?: string;
  jobId?: string;
  mark?: string;
  dataId?: string;
  clientId?: string;
  sessionId?: string;
  msg?: string;
};

export type ConnectionContext = {
  app_id: string;
  user_id: string;
};

/* -------------------------------------------------------------------------- */
/*                              Internal Storage                              */
/* -------------------------------------------------------------------------- */

const messageListeners = new Set<(data: ServerMessage) => void>();
const connectionListeners = new Set<
  (context: ConnectionContext | null) => void
>();

/* -------------------------------------------------------------------------- */
/*                           Message Event Handling                           */
/* -------------------------------------------------------------------------- */

export function onMessage(
  cb: (data: ServerMessage) => void
): () => void {
  messageListeners.add(cb);
  return () => messageListeners.delete(cb);
}

export function emitMessage(data: ServerMessage) {
  messageListeners.forEach((cb) => {
    try {
      cb(data);
    } catch (err) {
      console.error("Message listener error:", err);
    }
  });
}

/* -------------------------------------------------------------------------- */
/*                         Connection Event Handling                          */
/* -------------------------------------------------------------------------- */

export function onConnected(
  cb: (context: ConnectionContext | null) => void
): () => void {
  connectionListeners.add(cb);
  return () => connectionListeners.delete(cb);
}

export function emitConnection(context: ConnectionContext | null) {
  connectionListeners.forEach((cb) => {
    console.log("emitConnection");
    try {
      cb(context);
    } catch (err) {
      console.log("Connection listener error:", err);
    }
  });
}