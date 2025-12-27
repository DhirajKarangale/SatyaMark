import React from "react";
import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";

function LayoutNavbar() {
    return (
        <div className="min-h-screen w-full bg-slate-950">
            <Navbar />

            <main className="pt-16 h-[calc(100vh-4rem)]">
                <Outlet />
            </main>
        </div>
    );
}

export default React.memo(LayoutNavbar);