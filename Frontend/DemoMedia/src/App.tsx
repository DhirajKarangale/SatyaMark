import { useEffect } from "react";
import { connect, sendData } from "./utils/ws-service";
import Home from "./components/Home";

function App() {
  useEffect(() => {
    connect();
  }, []);

  return (
    // <button
    //   className="w-max h-max bg-amber-400 text-white font-bold"
    // onClick={() => sendData({
    //   clientId: "123",
    //   jobId: "456",
    //   text: "John cena is my favourate wrestler",
    //   // image_url: "https://picsum.photos/200/300/?blur",
    // })}>
    //   Send
    // </button>


    <>

      <Home />
    </>
  );
}

export default App;
