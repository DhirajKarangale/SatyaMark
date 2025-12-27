import { memo, useState, useEffect } from "react";
import Alert from "../components/Alert";
import { jobStore } from "../store/jobStore";
import ChatInput from "../components/ChatInput";
import ResultCard from "../components/ResultCard";
import { resultBus } from "../store/resultBus";
import { useNavigate, useLocation } from "react-router-dom";

function Chat() {
    const navigate = useNavigate();
    const location = useLocation();
    const [showAlert, setShowAlert] = useState<boolean>(false);
    const urlBase = import.meta.env.VITE_URL_BASE;

    useEffect(() => {
        const run = async () => {
            const parts = location.pathname.split("/").filter(Boolean);
            if (parts.length < 3) return;

            const [, type, id] = parts;

            if (jobStore.has(id)) return;

            jobStore.add(id);
            navigate("/chat", { replace: true });

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
        <div className="min-h-screen bg-slate-950 flex flex-col">
            {/* Page Header */}
            <div className="bg-linear-to-b from-slate-900 to-slate-950 border-b border-white/10">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">
                        Live Verification
                    </h1>
                    <p className="text-gray-400">
                        Submit text or images to verify their authenticity in real-time
                    </p>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 flex flex-col max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
                {/* Results Area - Scrollable */}
                <div className="flex-1 min-h-0 overflow-y-auto mb-6 custom-scroll">
                    <ResultCard />
                </div>

                {/* Input Area - Fixed at bottom */}
                <div className="shrink-0">
                    <ChatInput />
                </div>
            </div>

            <Alert
                isOpen={showAlert}
                message="There was an error processing your request. Please try again later."
                onClose={() => setShowAlert(false)}
                onConfirm={() => setShowAlert(false)}
            />
        </div>
    );
}

export default memo(Chat);