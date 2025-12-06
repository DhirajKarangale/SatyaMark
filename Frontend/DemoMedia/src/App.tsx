import { useEffect } from "react";
import { connect, sendData } from "./utils/ws-service";

function App() {
  useEffect(() => {
    connect();
  }, []);

  return (
    <button onClick={() => sendData({
      clientId: "123",
      jobId: "456",
      text: "John cena is my favourate wrestler",
      // image_url: "https://picsum.photos/200/300/?blur",
    })}>
      Send
    </button>
  );
}

export default App;
