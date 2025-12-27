import { memo, useState, useRef, useEffect } from "react";
import { Send, Paperclip, X, AlertCircle } from "lucide-react";
import { motion } from "framer-motion";
import { jobStore } from "../store/jobStore";
import { getDataId } from "../utils/GenerateIds";
import { process } from "../process/satyamark_process";
import { isSocketConnected, onConnectionChange } from "../process/satyamark_connect";
import Alert from "./Alert";

function ChatInput() {
    const [text, setText] = useState("");
    const [msg, setMsg] = useState("");

    const [localImage, setLocalImage] = useState<string | null>(null);
    const [imageUrl, setImageUrl] = useState<string | null>(null);
    const [uploading, setUploading] = useState(false);
    const [connected, setConnected] = useState(isSocketConnected());

    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const CLOUD_NAME = import.meta.env.VITE_CLOUD_NAME;
    const UPLOAD_PRESET = import.meta.env.VITE_UPLOAD_PRESET;

    useEffect(() => {
        if (!textareaRef.current) return;
        textareaRef.current.style.height = "auto";
        textareaRef.current.style.height =
            Math.min(textareaRef.current.scrollHeight, 120) + "px";
    }, [text]);

    useEffect(() => {
        return onConnectionChange(setConnected);
    }, []);

    const isValid = connected && (text.trim().length > 0 || imageUrl);

    function getErrorMessage(error: unknown): string {
        if (error instanceof Error) return error.message;
        if (typeof error === "string") return error;
        return "Something went wrong. Please try again.";
    }

    const uploadImage = async (file: File) => {
        try {
            setUploading(true);

            const formData = new FormData();
            formData.append("file", file);
            formData.append("upload_preset", UPLOAD_PRESET);

            const res = await fetch(
                `https://api.cloudinary.com/v1_1/${CLOUD_NAME}/image/upload`,
                { method: "POST", body: formData }
            );

            const data = await res.json();
            setImageUrl(data.secure_url);
        } catch {
            setMsg("Image upload failed");
            setLocalImage(null);
        } finally {
            setUploading(false);
        }
    };

    const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setLocalImage(URL.createObjectURL(file));
        uploadImage(file);

        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
    };

    const send = async () => {
        if (!isValid || uploading) return;

        const currentText = text;
        const currentImage = imageUrl;

        try {
            const jobId = await process(
                currentText,
                currentImage ?? "",
                getDataId()
            );
            if (jobId) jobStore.add(jobId);

            setText("");
            setLocalImage(null);
            setImageUrl(null);
        } catch (error) {
            setMsg(getErrorMessage(error));
        }
    };

    return (
        <>
            <motion.div
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.35, ease: "easeOut" }}
                className="w-full bg-slate-900/50 border border-white/10 
                    backdrop-blur-sm rounded-2xl shadow-lg"
            >
                {/* Connection Status Bar */}
                {!connected && (
                    <div className="px-4 py-2 bg-red-500/10 border-b border-red-500/20 
                        rounded-t-2xl flex items-center gap-2 text-red-400 text-sm">
                        <AlertCircle size={16} />
                        <span>Disconnected from server. Reconnecting...</span>
                    </div>
                )}

                <div className="p-4 space-y-3">
                    {/* IMAGE PREVIEW */}
                    {localImage && (
                        <div className="relative w-fit">
                            <div className="relative rounded-xl overflow-hidden border border-white/20">
                                <img
                                    src={localImage}
                                    className="max-h-48 w-auto object-contain"
                                    alt="Preview"
                                />

                                {uploading && (
                                    <div className="absolute inset-0 bg-black/60 backdrop-blur-sm
                                        flex items-center justify-center">
                                        <div className="flex flex-col items-center gap-2">
                                            <div className="w-8 h-8 border-2 border-cyan-400/30
                                                border-t-cyan-400 rounded-full animate-spin" />
                                            <span className="text-sm text-gray-300">Uploading...</span>
                                        </div>
                                    </div>
                                )}
                            </div>

                            {!uploading && (
                                <button
                                    onClick={() => {
                                        setLocalImage(null);
                                        setImageUrl(null);
                                    }}
                                    className="absolute -top-2 -right-2
                                        bg-red-500 hover:bg-red-600
                                        rounded-full p-1.5
                                        shadow-lg transition-colors"
                                >
                                    <X size={14} className="text-white" />
                                </button>
                            )}
                        </div>
                    )}

                    {/* INPUT ROW */}
                    <div className="flex gap-3 items-end">
                        {/* TEXTAREA */}
                        <div className="flex-1 bg-white/5 rounded-xl px-4 py-3 
                            border border-white/10 focus-within:border-cyan-500/50 
                            transition-colors">
                            <textarea
                                ref={textareaRef}
                                value={text}
                                onChange={(e) => setText(e.target.value)}
                                onKeyDown={(e) => {
                                    if (e.key === "Enter" && !e.shiftKey) {
                                        e.preventDefault();
                                        if (isValid && !uploading) send();
                                    }
                                }}
                                placeholder="Enter text or upload an image to verify..."
                                rows={1}
                                className="w-full resize-none bg-transparent text-white 
                                    placeholder:text-gray-500 outline-none
                                    max-h-[120px] overflow-y-auto custom-scroll"
                            />
                        </div>

                        {/* ACTIONS */}
                        <div className="flex gap-2">
                            <button
                                onClick={() => fileInputRef.current?.click()}
                                disabled={uploading}
                                className="w-11 h-11 rounded-xl flex justify-center items-center
                                    bg-white/5 hover:bg-white/10 border border-white/10
                                    text-gray-300 hover:text-white
                                    disabled:opacity-50 disabled:cursor-not-allowed
                                    transition-all duration-200"
                                title="Upload image"
                            >
                                <Paperclip size={20} />
                            </button>

                            <motion.button
                                onClick={send}
                                disabled={!isValid || uploading}
                                whileTap={{ scale: 0.95 }}
                                className={`w-11 h-11 rounded-xl flex justify-center items-center
                                    transition-all duration-200
                                    ${isValid && !uploading
                                        ? "bg-linear-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white shadow-lg shadow-cyan-500/25"
                                        : "bg-slate-700 text-gray-500 cursor-not-allowed"
                                    }`}
                                title="Send"
                            >
                                <Send size={20} />
                            </motion.button>
                        </div>
                    </div>

                    {/* Helper Text */}
                    <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>
                            {text.length > 0 && `${text.length} characters`}
                        </span>
                        <span>
                            Press Enter to send • Shift+Enter for new line
                        </span>
                    </div>
                </div>

                <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    hidden
                    onChange={onFileChange}
                />
            </motion.div>

            <Alert
                isOpen={msg !== ""}
                message={msg}
                onClose={() => setMsg("")}
                onConfirm={() => setMsg("")}
            />
        </>
    );
}

// export default memo(ChatInput);
//                 <div className="flex gap-2 items-start">
//                     {/* TEXTAREA */}
//                     <motion.textarea
//                         ref={textareaRef}
//                         value={text}
//                         onChange={(e) => setText(e.target.value)}
//                         onKeyDown={(e) => {
//                             if (e.key === "Enter" && !e.shiftKey) {
//                                 e.preventDefault();
//                                 if (isValid && !uploading) send();
//                             }
//                         }}
//                         placeholder="Type a message..."
//                         rows={1}
//                         className="flex-1 resize-none bg-transparent text-white outline-none
//                         max-h-[120px] overflow-y-auto custom-scroll"
//                     />

//                     {/* ACTIONS */}
//                     <div className="flex flex-col gap-2">
//                         <button
//                             onClick={() => fileInputRef.current?.click()}
//                             disabled={uploading}
//                             className="w-10 h-10 rounded-lg flex justify-center items-center
//                             bg-white/5 hover:bg-white/10 text-white/80"
//                         >
//                             <Paperclip size={18} />
//                         </button>

//                         <motion.button
//                             onClick={send}
//                             disabled={!isValid || uploading}
//                             whileTap={{ scale: 0.9 }}
//                             className={`w-10 h-10 rounded-lg flex justify-center items-center
//                             ${isValid && !uploading
//                                     ? "bg-cyan-500 hover:bg-cyan-400"
//                                     : "bg-zinc-700 cursor-not-allowed"}`}
//                         >
//                             <Send size={18} />
//                         </motion.button>
//                     </div>
//                 </div>

//                 <input
//                     ref={fileInputRef}
//                     type="file"
//                     accept="image/*"
//                     hidden
//                     onChange={onFileChange}
//                 />
//             </motion.div >

//     <Alert
//         isOpen={msg !== ""}
//         message={msg}
//         onClose={() => setMsg("")}
//         onConfirm={() => setMsg("")}
//     />
//         </>
//     );
// }

export default memo(ChatInput);
