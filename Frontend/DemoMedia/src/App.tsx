import { useEffect } from "react";
import Home from "./components/Home";
import { init } from "satyamark-react";

export default function App() {
  useEffect(() => {
    init({ app_id: "APP123", user_id: "USER991" })
  }, []);

  return <Home />;
}