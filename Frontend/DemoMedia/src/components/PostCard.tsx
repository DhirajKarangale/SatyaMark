import { useState, useRef, useEffect } from "react";
import { type PostData } from "../utils/PostData";
import { process } from "satyamark-react";
import { registerStatus } from "satyamark-react";

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
                try {
                    id = await process(cardRef.current, postData.id);

                    if (id) {
                        if (!mounted) return;
                        setJobId(id);
                        break;
                    }
                } catch (error) {
                    console.log("------------ ", error);
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
        if (!jobId || !cardRef.current) return;
        registerStatus(jobId, cardRef.current, { iconSize: 20 });
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

            <div
                style={{
                    width: "100%",
                    display: "flex",
                    justifyContent: "flex-end",
                    marginTop: "12px",
                    paddingTop: "12px",
                    borderTop: "1px solid #2a2d33",
                }}
                data-status-container
            ></div>

        </div>
    );
}
