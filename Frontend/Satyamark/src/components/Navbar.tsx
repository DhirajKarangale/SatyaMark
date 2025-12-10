import { memo } from "react";
import { NavLink } from "react-router-dom";
import { motion } from "framer-motion";

import { Home, Info, FileText } from "lucide-react";
import { routeHome, routeAbout, routeDoccu } from "../utils/Routes";

const navItems = [
    { name: "About", path: routeAbout, icon: <Info size={20} /> },
    { name: "Home", path: routeHome, icon: <Home size={20} /> },
    { name: "Documentation", path: routeDoccu, icon: <FileText size={20} /> },
];

function Navbar() {
    return (
        <>
            {/* Desktop Sidebar */}
            <motion.div
                initial={{ x: -80, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ duration: 0.4, ease: "easeOut" }}
                className="hidden lg:flex fixed left-0 top-0 h-full w-56 bg-gradient-to-b 
                from-white/5 to-white/2 backdrop-blur-xl border-r border-white/10 
                shadow-[0_8px_32px_0_rgba(31,38,135,0.37)] p-4 z-5"
            >
                <div className="flex flex-col gap-4">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) =>
                                `relative rounded-lg text-white text-base font-medium
            transition-all duration-300 overflow-hidden
            ${isActive ? "bg-cyan-600" : "hover:bg-white/10"}`
                            }
                        >
                            <motion.div
                                whileHover={{ y: -3, scale: 1.03 }}
                                whileTap={{ scale: 0.95 }}
                                transition={{ type: "spring", stiffness: 200, damping: 15 }}
                                className="flex items-center gap-3 px-4 py-3 w-full"
                            >
                                <motion.div>
                                    {item.icon}
                                </motion.div>

                                <span className="select-none">{item.name}</span>
                            </motion.div>

                            {/* Glow */}
                            <motion.div
                                className="absolute inset-0 rounded-lg pointer-events-none"
                                initial={{ opacity: 0 }}
                                whileHover={{ opacity: 0.15 }}
                                transition={{ duration: 0.2 }}
                                style={{
                                    background:
                                        "radial-gradient(circle at center, rgba(255,255,255,0.4), transparent 70%)",
                                }}
                            />
                        </NavLink>
                    ))}

                </div>
            </motion.div>

            {/* Mobile Bottom Nav */}
            <motion.div
                initial={{ y: 40, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.35, ease: "easeOut" }}
                className="lg:hidden fixed bottom-0 left-0 w-full h-10 p-0 m-0 z-5 bg-gradient-to-b 
                from-white/5 to-white/2 backdrop-blur-xl border-r border-white/10 
                shadow-[0_8px_32px_0_rgba(31,38,135,0.37)]"
            >
                <div className="flex justify-around items-center px-0 py-1">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) =>
                                `relative flex flex-col items-center justify-center text-white text-xs
            font-medium transition-all duration-200 w-full py-2
            ${isActive ? "bg-cyan-600 text-cyan-400 rounded-md" : "hover:text-cyan-300"}`
                            }
                        >
                            <motion.div
                                whileHover={{ y: -2, scale: 1.1 }}
                                whileTap={{ scale: 0.92 }}
                                transition={{ type: "spring", stiffness: 250, damping: 14 }}
                                className="flex flex-col items-center w-full"
                            >
                                {item.icon}
                            </motion.div>

                            {/* Glow */}
                            <motion.div
                                className="absolute inset-0 pointer-events-none rounded-md"
                                initial={{ opacity: 0 }}
                                whileHover={{ opacity: 0.1 }}
                                transition={{ duration: 0.15 }}
                                style={{
                                    background:
                                        "radial-gradient(circle at center, rgba(255,255,255,0.4), transparent 65%)",
                                }}
                            />
                        </NavLink>
                    ))}
                </div>
            </motion.div>
        </>
    );
}

export default memo(Navbar);
