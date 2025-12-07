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
    const [result, setResult] = useState<any | null>(null);
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
            if (!data || !data.jobId || data.jobId != jobId) return;
            setResult(data);
            console.log("PostCard got its data:", data);
        });

        return () => { unsubscribe(); };
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

            {/* BOTTOM ACTION AREA */}
            <div className="mt-4 pt-3 border-t border-gray-800 flex justify-end">
                <div className="w-3 h-3 rounded-full bg-blue-500" />
            </div>
        </div>
    );
}
