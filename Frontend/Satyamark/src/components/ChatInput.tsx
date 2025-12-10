import { memo, useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";

function ChatInput({
    onSend,
}: {
    onSend: (message: string) => void;
}) {
    const [text, setText] = useState("");
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        if (!textareaRef.current) return;
        textareaRef.current.style.height = "auto";
        textareaRef.current.style.height =
            Math.min(textareaRef.current.scrollHeight, 120) + "px";
    }, [text]);

    const isValid = text.trim().length > 0;

    const send = () => {
        if (!isValid) return;
        onSend(text);
        setText("");
    };

    return (
        <div className="w-full bg-white/5 border border-white/20 
            backdrop-blur-sm rounded-xl p-3 flex flex-col gap-2">

            <textarea
                ref={textareaRef}
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Type a message..."
                rows={1}
                className="w-full resize-none bg-transparent1 text-white outline-none
                max-h-[120px] overflow-y-auto custom-scroll"
            />

            <div className="flex justify-end">
                <button
                    onClick={send}
                    disabled={!isValid}
                    className={`
                            w-12 h-10 py-2 rounded-lg flex justify-center items-center
                            text-white transition-all duration-150
                            ${isValid
                            ? "bg-cyan-500 hover:bg-cyan-400 active:scale-95"
                            : "bg-zinc-700 opacity-40 cursor-not-allowed"}
                        `}
                >
                    <Send size={22} />
                </button>
            </div>
        </div>
    );
}

export default memo(ChatInput);