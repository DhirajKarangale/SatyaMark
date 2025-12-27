import React from "react";
import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";

function LayoutNavbar() {
    return (
        <div className="min-h-screen w-full bg-slate-950">
            <Navbar />

            {/* Main content with top padding for fixed navbar */}
            <main className="pt-16">
                <Outlet />
            </main>
        </div>
    );
}

export default React.memo(LayoutNavbar);