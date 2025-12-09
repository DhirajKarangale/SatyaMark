import { memo } from "react";
import { NavLink } from "react-router-dom";
import { motion } from "framer-motion";

import { Home, Info, FileText } from "lucide-react";
import { routeHome, routeAbout, routeDoccu } from "../utils/Routes";

const navItems = [
    { name: "About", path: routeAbout, icon: Info },
    { name: "Home", path: routeHome, icon: Home },
    { name: "Documentation", path: routeDoccu, icon: FileText },
];

function Navbar() {
    return (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 pointer-events-none w-full flex justify-center">
            <div
                className="
                backdrop-blur-3xl bg-white/10
                shadow-[0_8px_60px_rgba(0,0,0,0.45)]
                px-6 py-3 rounded-full flex gap-8 sm:gap-10
                border border-white/20
                pointer-events-auto
                "
            >
                {navItems.map(({ name, path, icon: Icon }) => (
                    <NavLink key={name} to={path} className="relative">
                        {({ isActive }) => (
                            <motion.div
                                initial={{ scale: 1, opacity: 0.8 }}
                                animate={{
                                    scale: isActive ? 1.25 : 1,
                                    opacity: isActive ? 1 : 0.75
                                }}
                                whileHover={{ scale: 1.15, opacity: 1 }}
                                transition={{
                                    type: "spring",
                                    stiffness: 250,
                                    damping: 15
                                }}
                                className="flex items-center justify-center"
                            >
                                <Icon
                                    size={18}   
                                    className={`
                                        transition-all duration-300
                                        ${isActive
                                            ? "text-blue-400 drop-shadow-[0_0_8px_rgba(56,189,248,0.6)]"
                                            : "text-white/70 hover:text-white"
                                        }
                                    `}
                                />
                            </motion.div>
                        )}
                    </NavLink>
                ))}
            </div>
        </div>
    );
}

export default memo(Navbar);
