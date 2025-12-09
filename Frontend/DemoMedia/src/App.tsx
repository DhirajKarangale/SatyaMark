import { useEffect } from "react";
import { init } from './satyamark/satyamark_connect'
import Home from "./components/Home";

export default function App() {
  useEffect(() => {
    init({ app_id: "APP123", user_id: "USER999" })
  }, []);

  return <Home />;
}