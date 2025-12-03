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
      text: "",
      image_url: "https://picsum.photos/seed/picsum/200/300",
    })}>
      Send
    </button>
  );
}

export default App;
