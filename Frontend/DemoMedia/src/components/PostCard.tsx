import { useState, useRef, useEffect } from "react";
import { process } from "../satyamark/satyamark_process";
import { onReceive } from "../satyamark/satyamark_connect";
import { type PostData } from "../utils/PostData";

type PostCardProps = {
    postData: PostData;
};

const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date
        .toLocaleDateString("en-GB", {
            day: "2-digit",
            month: "short",
            year: "numeric",
        })
        .replace(",", "");
};

export default function PostCard({ postData }: PostCardProps) {
    const { title, description, imageURL, userName, date } = postData;
    const [jobId, setJobId] = useState<string | null>(null);
    const cardRef = useRef<HTMLDivElement | null>(null);

    useEffect(() => {
        let mounted = true;

        const run = async () => {
            if (!cardRef.current) return;

            let attempt = 0;
            let id: string | null | undefined = null;

            while (mounted && !id) {
                attempt++;
                id = await process(cardRef.current, postData.id);

                if (id) {
                    if (!mounted) return;
                    setJobId(id);
                    break;
                }

                await new Promise((resolve) => setTimeout(resolve, 1000));
            }
        };

        run();

        return () => {
            mounted = false;
        };
    }, []);

    useEffect(() => {
        if (!jobId) return;

        const unsubscribe = onReceive((data) => {
            if (!data || !data.jobId || data.jobId !== jobId) return;

            const container = cardRef.current?.querySelector("[data-status-container]");
            if (!container) return;

            let icon = container.querySelector("img") as HTMLImageElement;
            if (!icon) {
                icon = document.createElement("img");
                icon.className = "w-5 h-5 object-contain";
                icon.alt = "status";
                container.appendChild(icon);
            }

            let image = "/pending.png";

            switch (data.mark?.toLowerCase()) {
                case "correct":
                    image = "/correct.png";
                    break;
                case "incorrect":
                    image = "/incorrect.png";
                    break;
                case "insufficient":
                    image = "/insufficient.png";
                    break;
                case "ai":
                    image = "/ai.png";
                    break;
                case "real":
                    image = "/real.png";
                    break;
                case "subjective":
                    image = "/subjective.png";
                    break;
                default:
                    image = "/pending.png";
            }

            icon.src = image;

            console.log("Data Received: ", data);
        });

        return () => unsubscribe();
    }, [jobId]);

    return (
        <div
            ref={cardRef}
            className="w-full bg-[#16181c] border border-gray-800 rounded-2xl p-4 text-white hover:bg-[#1d1f23] transition">

            {/* USER AREA */}
            <div className="flex items-center justify-between mb-3">
                <span className="font-semibold text-md">{userName}</span>
                <span className="text-xs text-gray-400">{formatDate(date)}</span>
            </div>

            {/* CONTENT AREA */}
            <div className="space-y-3">
                <h3 className="text-base font-semibold hidden">{title}</h3>

                {imageURL && (
                    <img
                        src={imageURL}
                        alt="post"
                        className="w-full rounded-xl border border-gray-800"
                    />
                )}

                {description && (
                    <p className="text-sm text-gray-300 whitespace-pre-line">
                        {description}
                    </p>
                )}
            </div>

            <div className="w-full flex justify-end mt-4 pt-3 border-t border-[#2a2d33]" data-status-container></div>

        </div>
    );
}
