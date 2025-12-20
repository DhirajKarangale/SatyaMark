import { memo, useState, useEffect } from "react";
import Alert from "../components/Alert";
import { jobStore } from "../store/jobStore";
import ChatInput from "../components/ChatInput";
import ResultCard from "../components/ResultCard";
import { resultBus } from "../store/resultBus";
import { useNavigate, useLocation } from "react-router-dom";

function Home() {
    const navigate = useNavigate();
    const location = useLocation();
    const [showAlert, setShowAlert] = useState<boolean>(false);
    const urlBase = import.meta.env.VITE_URL_BASE;

    useEffect(() => {
        const run = async () => {
            const parts = location.pathname.split("/").filter(Boolean);
            if (parts.length < 2) return;

            const [type, id] = parts;

            if (jobStore.has(id)) return;

            jobStore.add(id);
            navigate("/", { replace: true });

            const endpoint = type === "image" ? "getImageResult" : "getTextResult";

            try {
                const res = await fetch(`${urlBase}/${endpoint}?id=${id}`);
                const data = await res.json();
                jobStore.remove(id);
                if (data) resultBus.publish(data);
            } catch (err) {
                jobStore.remove(id);
                setShowAlert(true);
            }
        };

        run();
    }, []);

    return (
        <div className="w-full h-full flex flex-col gap-2 justify-between items-center py-2">
            <ResultCard />
            <ChatInput />

            <Alert
                isOpen={showAlert}
                message="There was an error processing your request. Please try again later."
                onClose={() => setShowAlert(false)}
                onConfirm={() => setShowAlert(false)}
            />

            <div className="w-full h-10 text-transparent text-center">-DK-</div>
        </div>
    );
}

export default memo(Home);