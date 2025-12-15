import { memo } from "react";
import ChatInput from "../components/ChatInput";
import ResultCard from "../components/ResultCard";

function Home() {
    return (
        <div className="w-full h-full flex flex-col gap-2 justify-between items-center py-2 bg-red-5001">
            <ResultCard />
            <ChatInput />
        </div>
    );
}

export default memo(Home);