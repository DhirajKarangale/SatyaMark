import { useState, useEffect } from "react";
import { init, onConnected } from "satyamark-react";
import Home from "./components/Home";

export default function App() {
  const [isConnectedToSatyamark, setIsConnectedToSatyamark] = useState(false);

  function getUserId() {
    let id = localStorage.getItem("satyamark_demo_user_id");
    if (!id) {
      const time = Date.now().toString(36); 
      const random = crypto.getRandomValues(new Uint32Array(1))[0].toString(36);
      id = `${time}${random}`;
      localStorage.setItem("satyamark_demo_user_id", id);
    }
    return id;
  }

  useEffect(() => {
    const unsubscribe = onConnected((data: any) => {
      setIsConnectedToSatyamark(!!data);
      console.log("Connected:", data);
    });

    return () => {
      unsubscribe();
    };
  }, []);

  useEffect(() => {
    init({ app_id: "APP123", user_id: getUserId() })
  }, []);

  return <Home isConnectedToSatyamark={isConnectedToSatyamark} />;
}