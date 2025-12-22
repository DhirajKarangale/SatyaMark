import React from "react";
import { Outlet } from "react-router-dom";

import Navbar from "./Navbar";

function LayoutNavbar() {
    return (
        <div className="flex flex-col lg:flex-row min-h-screen w-full relative pb-10 md:pb-5 sm:pb-7 lg:pb-0">
            <div className="lg:w-56 shrink-0">
                <Navbar />
            </div>

            <main className="flex-1 px-0 py-0 sm:px-3 sm:py-3 md:px-4 md:py-4">
                <Outlet />
            </main>
        </div>
    );
}

export default React.memo(LayoutNavbar);