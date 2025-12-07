import { useState, useEffect } from "react";
import { init } from "satyamark";
import Home from "./components/Home";

export default function App() {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    init({ app_id: "APP123", user_id: "USER999" }, "ws://localhost:1000")
      .then(() => setReady(true))
      .catch(console.error);
  }, []);

  if (!ready) return <div>Connecting…</div>;

  return <Home />;
}