import { memo } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";

function NotFound() {
  const navigate = useNavigate();

  return (
    <div className="w-full flex-1 flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="max-w-xl w-full border border-white/15 backdrop-blur-sm
        rounded-2xl p-8 text-center flex flex-col gap-6"
      >
        <h1 className="text-6xl font-bold bg-linear-to-r from-emerald-400 via-blue-500 to-emerald-400 bg-clip-text text-transparent">
          404
        </h1>

        <h2 className="text-white text-2xl font-semibold">
          Page Not Found
        </h2>

        <p className="text-gray-400">
          The page you're trying to access doesn't exist or may have been moved.
        </p>

        <div className="flex justify-center pt-2">
          <button
            onClick={() => navigate("/")}
            aria-label="Go to Homepage"
            className="px-6 py-3 rounded-xl bg-cyan-500 text-black font-medium hover:bg-cyan-400 transition cursor-pointer"
          >
            Go to Home
          </button>
        </div>
      </motion.div>
    </div>
  );
}

export default memo(NotFound);