import { useEffect } from "react";
import { init, onConnected } from "satyamark-react";
import Home from "./components/Home";

export default function App() {
  function uniqueTimestamp() {
    const now = new Date();

    const yyyy = now.getFullYear();
    const MM = String(now.getMonth() + 1).padStart(2, "0");
    const dd = String(now.getDate()).padStart(2, "0");

    const hh = String(now.getHours()).padStart(2, "0");
    const mm = String(now.getMinutes()).padStart(2, "0");
    const ss = String(now.getSeconds()).padStart(2, "0");
    const ms = String(now.getMilliseconds()).padStart(3, "0");

    const micro = String(Math.floor(Math.random() * 1000)).padStart(3, "0");

    return `${yyyy}${MM}${dd}${hh}${mm}${ss}${ms}${micro}`;
  }

  function getUserId() {
    const uuid = crypto.randomUUID();
    const time = uniqueTimestamp();
    const id = `${uuid}_${time}`;
    return id;
  }

  onConnected((data: any) => {
    console.log("Connected:", data);
  });

  useEffect(() => {
    init({ app_id: "APP123", user_id: getUserId() })
  }, []);

  return <Home />;
}