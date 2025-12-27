import React from "react";
import { Outlet } from "react-router-dom";

import Navbar from "./Navbar";

function LayoutNavbar() {
    return (
        <div className="flex flex-col lg:flex-row h-dvh w-full relative pb-10 lg:pb-0">
            <div className="lg:w-56 shrink-0">
                <Navbar />
            </div>

            <main className="flex-1 min-h-0">
                <Outlet />
            </main>
        </div>
    );
}

export default React.memo(LayoutNavbar);