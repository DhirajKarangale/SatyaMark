import { useEffect } from "react";
import Home from "./components/Home";
import { connect } from "./satyamark/satyamark_connect";

function App() {
  useEffect(() => {
    connect({ app_id: "APP123", user_id: "USER999" });
  }, []);

  return <Home />
}

export default App;
