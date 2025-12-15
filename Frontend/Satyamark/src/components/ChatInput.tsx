import { memo, useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";
import { motion } from "framer-motion";
import { jobStore } from "../store/jobStore";
import { getDataId } from "../utils/GenerateIds";
import { process_satyamark } from "satyamark-react";

function ChatInput() {
    const [text, setText] = useState("");
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        if (!textareaRef.current) return;
        textareaRef.current.style.height = "auto";
        textareaRef.current.style.height =
            Math.min(textareaRef.current.scrollHeight, 120) + "px";
    }, [text]);

    const isValid = text.trim().length > 0;

    const send = async () => {
        if (!isValid) return;
        setText("");
        const jobId = await process_satyamark(text, "", getDataId());
        if (!jobId) return;
        console.log("Data sent successfully: ", jobId)
        jobStore.add(jobId);
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, ease: "easeOut" }}
            className="w-full bg-white/5 border border-white/20 
                backdrop-blur-sm rounded-xl p-3 flex flex-col gap-2"
        >
            {/* TEXTAREA — no focus glow anymore */}
            <motion.textarea
                ref={textareaRef}
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Type a message..."
                rows={1}
                className="w-full resize-none bg-transparent text-white outline-none
                    max-h-[120px] overflow-y-auto custom-scroll"
                whileFocus={{
                    scale: 1,
                }}
                transition={{ duration: 0.2 }}
            />

            {/* SEND BUTTON */}
            <div className="flex justify-end">
                <motion.button
                    onClick={send}
                    disabled={!isValid}
                    whileHover={isValid ? { scale: 1.05 } : {}}
                    whileTap={isValid ? { scale: 0.9 } : {}}
                    animate={{
                        scale: isValid ? 1 : 0.95,
                        opacity: isValid ? 1 : 0.4,
                    }}
                    transition={{ duration: 0.2 }}
                    className={`
                        w-12 h-10 py-2 rounded-lg flex justify-center items-center
                        text-white
                        ${isValid
                            ? "bg-cyan-500 hover:bg-cyan-400"
                            : "bg-zinc-700 cursor-not-allowed"}
                    `}
                >
                    <Send size={22} />
                </motion.button>
            </div>
        </motion.div>
    );
}

export default memo(ChatInput);
