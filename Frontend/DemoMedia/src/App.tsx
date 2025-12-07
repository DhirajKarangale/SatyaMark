import { useEffect } from "react";
import Home from "./components/Home";
import { connect, sendData } from "./satyamark/satyamark_connect";

function App() {
  useEffect(() => {
    connect({ app_id: "APP123", user_id: "USER999" });
  }, []);

  return (
    <>
      <div className="w-full h-min py-2 flex justify-center items-center">
        <button
          className="w-max h-max px-4 py-2 bg-amber-400 text-white font-bold border-2 border-amber-500 rounded-sm"
          onClick={() => sendData("India won 2025 cricket worldcup", "")}
        >
          Send
        </button>
      </div>

      <Home />
    </>
  );
}

export default App;
