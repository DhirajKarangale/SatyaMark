import React from "react";

interface PostCardProps {
  avatar?: string;
  username: string;
  handle: string;
  content: string;
}

const PostCard: React.FC<PostCardProps> = ({ avatar, username, handle, content }) => {
  return (
    <div className="bg-black border-b border-gray-800 px-5 py-4 hover:bg-gray-900 transition">
      <div className="flex gap-4">
        <img
          src={avatar || "https://abs.twimg.com/sticky/default_profile_images/default_profile_400x400.png"}
          alt="avatar"
          className="w-12 h-12 rounded-full hover:opacity-80 transition"
        />

        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-gray-100">{username}</span>
            <span className="text-gray-500 text-sm">@{handle}</span>
          </div>

          <p className="text-gray-200 mt-1 leading-relaxed">{content}</p>
        </div>
      </div>
    </div>
  );
};

const Home = () => {
  const posts = [
    {
      username: "SatyaMark AI",
      handle: "satyamark",
      content: "AI Image Verification now detects GAN fingerprints with higher accuracy.",
    },
    {
      username: "SatyaMark AI",
      handle: "satyamark",
      content: "Text Fact Check pipeline upgraded: multi-LLM consensus is now faster.",
    },
    {
      username: "SatyaMark AI",
      handle: "satyamark",
      content: "Video deepfake analysis is rolling out with frame-accurate tamper detection.",
    },
  ];

  return (
    <div className="min-h-screen bg-black text-white flex justify-center">
      <div className="w-full max-w-2xl border-x border-gray-800 min-h-screen">
        <header className="px-5 py-4 border-b border-gray-800 sticky top-0 bg-black/90 backdrop-blur-md z-10">
          <h1 className="text-2xl font-bold text-gray-100">Satyamark Demo</h1>
        </header>

        {posts.map((p, i) => (
          <PostCard key={i} {...p} />
        ))}
      </div>
    </div>
  );
};

export default Home;