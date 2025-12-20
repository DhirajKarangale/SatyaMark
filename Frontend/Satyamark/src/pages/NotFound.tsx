import { memo } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import GradientText from "../reactbits/GradientText/GradientText";

function NotFound() {
    const navigate = useNavigate();

    return (
        <div className="w-full h-full flex items-center justify-center px-4">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, ease: "easeOut" }}
                className="
                    max-w-xl w-full border border-white/15 backdrop-blur-sm
                    rounded-2xl p-8
                    text-center flex flex-col gap-6
                "
            >
                <GradientText
                    colors={["#40ffaa", "#4079ff", "#40ffaa"]}
                    animationSpeed={6}
                    showBorder={false}
                    className="text-6xl font-bold bg-transparent"
                >
                    404
                </GradientText>

                <h2 className="text-white text-2xl font-semibold">
                    Page Not Found
                </h2>

                <p className="text-gray-400">
                    The page you’re trying to access doesn’t exist or may have been moved.
                </p>

                <div className="flex justify-center pt-2">
                    <button
                        onClick={() => navigate("/")}
                        className="
                            px-6 py-3 rounded-xl
                            bg-cyan-500 text-black font-medium
                            hover:bg-cyan-400 transition
                        "
                    >
                        Go to Home
                    </button>
                </div>
            </motion.div>
        </div>
    );
}

export default memo(NotFound);