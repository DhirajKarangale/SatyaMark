import PostCard from "./PostCard";
import posts from "../data/posts.json";
import { type PostData } from "../utils/PostData";

export default function Home() {
    const typedPosts = posts as PostData[];

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
