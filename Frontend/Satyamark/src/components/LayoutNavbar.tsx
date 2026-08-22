import React from "react";
import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";

function LayoutNavbar() {
    return (
        <div className="flex flex-col min-h-[100dvh] w-full bg-slate-950">
            <Navbar />

            <main className="flex flex-col flex-1 pt-16 pb-16 md:pb-0">
                <Outlet />
            </main>
        </div>
    );
}

export default React.memo(LayoutNavbar);