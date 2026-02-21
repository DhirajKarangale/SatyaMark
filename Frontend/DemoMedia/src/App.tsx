import { useState, useEffect } from "react";
import { init, onConnected } from "satyamark-react";
import Home from "./components/Home";

export default function App() {
  const [isConnectedToSatyamark, setIsConnectedToSatyamark] = useState(false);

  function getUserId() {
    const time = Date.now().toString(36); 
    const random = crypto.getRandomValues(new Uint32Array(1))[0].toString(36);
    return `${time}${random}`;
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