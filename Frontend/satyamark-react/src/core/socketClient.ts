type SocketHandlers = {
  onOpen: () => void;
  onMessage: (data: any) => void;
  onClose: () => void;
  onError: () => void;
};

export class SocketClient {
  private socket: WebSocket | null = null;
  private url: string;
  private handlers: SocketHandlers;

  constructor(url: string, handlers: SocketHandlers) {
    this.url = url;
    this.handlers = handlers;
  }

  connect() {
    this.socket = new WebSocket(this.url);

    this.socket.onopen = () => this.handlers.onOpen();
    this.socket.onmessage = (event) =>
      this.handlers.onMessage(JSON.parse(event.data));
    this.socket.onclose = () => this.handlers.onClose();
    this.socket.onerror = () => this.handlers.onError();
  }

  send(payload: any) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      throw new Error("Socket not ready");
    }

    this.socket.send(JSON.stringify(payload));
  }

  close() {
    this.socket?.close();
    this.socket = null;
  }

  isOpen() {
    return this.socket?.readyState === WebSocket.OPEN;
  }
}
