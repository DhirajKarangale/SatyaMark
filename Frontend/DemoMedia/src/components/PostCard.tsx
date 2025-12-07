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

    return (
        <div className="w-full bg-[#16181c] border border-gray-800 rounded-2xl p-4 text-white hover:bg-[#1d1f23] transition">

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
