export type SatyaMarkConnectionData = { app_id: string; user_id: string };

let socket: WebSocket | null = null;
let storedConnectionData: SatyaMarkConnectionData | null = null;
const listeners: ((data: any) => void)[] = [];

export function init(connectionData: SatyaMarkConnectionData, wsUrl: string) {
  return new Promise<void>((resolve, reject) => {
    if (typeof window === "undefined") return resolve();

    storedConnectionData = connectionData;
    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      safeSend({
        type: "handshake",
        clientId: connectionData.user_id,
        appId: connectionData.app_id
      });
      resolve(); 
    };

    socket.onerror = reject;

    socket.onmessage = (event) => {
      receiveData(JSON.parse(event.data));
    };
  });
}

export function onReceive(cb: (d: any) => void) {
  listeners.push(cb);
  return () => { const i = listeners.indexOf(cb); if (i > -1) listeners.splice(i, 1); };
}

function safeSend(msg: any) {
  if (!socket || socket.readyState !== WebSocket.OPEN) return;
  socket.send(JSON.stringify(msg));
}

function uniqueId() { return `${Date.now()}${Math.floor(Math.random() * 10000)}`; }

export function sendData(text: string, image_url: string, dataId: string) {
  if (!storedConnectionData || !socket) return null;
  const { app_id, user_id } = storedConnectionData;
  const jobId = `${app_id}_${user_id}_${dataId}_${uniqueId()}`;
  socket.send(JSON.stringify({ clientId: user_id, jobId, text, image_url }));
  return jobId;
}

function receiveData(data: any) {
  if (!storedConnectionData || data.clientId !== storedConnectionData.user_id) return;
  const payload = { jobId: data.jobId, dataId: data.dataId, mark: data.mark };
  listeners.slice().forEach(cb => { try { cb(payload) } catch (e) { console.error(e) } });
}
