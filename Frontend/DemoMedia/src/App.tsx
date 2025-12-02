import { useEffect } from "react";
import { connect, sendData } from "./utils/WebSocketService";

function App() {
  useEffect(() => {
    connect();
  }, []);

  return (
    <button onClick={() => sendData({ msg: "Hello from client", clientId: "123" })}>
      Send
    </button>
  );
}

export default App;
