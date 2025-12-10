import { memo } from "react";
import GradientText from "../reactbits/GradientText/GradientText";

type ResultData = {
    id: string | number;
    mark: string;
    confidence: number | string;
    reason: string;
    urls?: string[];
};

function ResultCard({ data }: { data: ResultData | null }) {
    if (!data) {
        return (
            <div
                className="w-full h-full border border-white/20 !bg-transparent
                backdrop-blur-sm rounded-xl p-4 flex items-center justify-center"
            >
                <GradientText
                    colors={["#40ffaa", "#4079ff", "#40ffaa", "#4079ff", "#40ffaa"]}
                    animationSpeed={6}
                    showBorder={false}
                    className="text-3xl font-semibold">
                    Welcome to Satyamark
                </GradientText>
            </div>
        );
    }

    return (
        <div
            className="w-full h-full  bg-white/5 border border-white/20 backdrop-blur-sm 
            flex flex-col gap-4 overflow-y-auto custom-scroll rounded-xl p-4"
        >

            {/* TOP ROW */}
            <div className="flex justify-between items-center w-full">
                <div className="text-white text-lg font-semibold">
                    ID: {data.id}
                </div>

                <div className="flex items-center gap-4">
                    <span className="text-cyan-400 font-medium">
                        Mark: {data.mark}
                    </span>
                    <span className="text-green-400 font-medium">
                        Confidence: {data.confidence}
                    </span>
                </div>
            </div>

            {/* REASON */}
            <div className="text-gray-300 whitespace-pre-wrap leading-relaxed">
                {data.reason}
            </div>

            {/* URLS (optional) */}
            {data.urls && data.urls.length > 0 && (
                <div className="flex flex-col gap-2">
                    <div className="text-white font-semibold">Sources:</div>

                    <div className="flex flex-col gap-1">
                        {data.urls.map((url, index) => (
                            <a
                                key={index}
                                href={url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-cyan-400 hover:text-cyan-300 underline break-all"
                            >
                                {url}
                            </a>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

export default memo(ResultCard);