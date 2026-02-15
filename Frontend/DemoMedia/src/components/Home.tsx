import PostCard from "./PostCard";
import posts from "../data/posts.json";
import { type PostData } from "../utils/PostData";

export default function Home({ isConnectedToSatyamark }: { isConnectedToSatyamark: boolean }) {
    const typedPosts = posts as PostData[];

    if (false && !isConnectedToSatyamark) {
        return (
            <div className="min-h-screen bg-black flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    {/* Spinner */}
                    <div className="w-12 h-12 border-4 border-gray-700 border-t-white rounded-full animate-spin" />

                    {/* Text */}
                    <p className="text-gray-400 text-sm tracking-wide">
                        Connecting to SatyaMark...
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-black text-white flex justify-center">

            <div className="w-full max-w-2xl px-4 py-6 space-y-6">

                {/* PAGE TITLE */}
                <h1 className="text-2xl font-bold text-center tracking-wide">
                    Social Media
                </h1>

                {/* POSTS FEED */}
                <div className="space-y-4">
                    {typedPosts.map((post) => (
                        <PostCard key={post.id} postData={post} />
                    ))}
                </div>

            </div>
        </div>
    );
}
