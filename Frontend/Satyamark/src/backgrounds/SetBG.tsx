import React, { useMemo } from "react";
import { useLocation } from "react-router-dom";

import BGAurora from "./BGAurora";
import BGSquares from "./BGSquares";
import BGHyperspeed from "./BGHyperspeed";


function SetBG() {
    const location = useLocation();

    const isAuth = location.pathname === "about";

    const Background = useMemo(() => {
        if (isAuth) return BGHyperspeed;
        const backgrounds = [BGAurora, BGSquares];
        const randomIndex = Math.floor(Math.random() * backgrounds.length);
        return backgrounds[randomIndex];
    }, [isAuth]);


    return (
        <div className="fixed inset-0 -z-100">
            <Background />
        </div>
    );
}

export default React.memo(SetBG);