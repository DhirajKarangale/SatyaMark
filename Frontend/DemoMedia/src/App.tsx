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
      text: "I am alien",
      image_url: "",
    })}>
      Send
    </button>
  );
}

export default App;
