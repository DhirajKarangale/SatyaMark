import { memo, useState } from "react";
import { NavLink } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Home, MessageCircleCode, FileText, Menu, X, Github } from "lucide-react";
import { routeHome, routeChat, routeDoccu } from "../utils/Routes";

const navItems = [
    { name: "Home", path: routeHome, icon: <Home size={18} /> },
    { name: "Chat", path: routeChat, icon: <MessageCircleCode size={18} /> },
    { name: "Documentation", path: routeDoccu, icon: <FileText size={18} /> },
];

function Navbar() {
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    return (
        <>
            {/* Desktop & Mobile Navbar */}
            <motion.nav
                initial={{ y: -20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.4, ease: "easeOut" }}
                className="fixed top-0 left-0 right-0 z-50 
                    bg-slate-950/80 backdrop-blur-xl 
                    border-b border-white/10
                    shadow-lg shadow-black/20"
            >
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center justify-between h-16">
                        {/* Logo / Brand */}
                        <NavLink
                            to={routeHome}
                            className="flex items-center gap-2 text-white font-bold text-xl 
                                hover:text-cyan-400 transition-colors"
                        >
                            <div className="w-8 h-8 rounded-lg bg-linear-to-br from-cyan-400 to-blue-600 
                                flex items-center justify-center text-white font-bold text-sm">
                                S
                            </div>
                            <span className="hidden sm:block">SatyaMark</span>
                        </NavLink>

                        {/* Desktop Navigation */}
                        <div className="hidden md:flex items-center gap-1">
                            {navItems.map((item) => (
                                <NavLink
                                    key={item.path}
                                    to={item.path}
                                    className={({ isActive }) =>
                                        `flex items-center gap-2 px-4 py-2 rounded-lg 
                                        text-sm font-medium transition-all duration-200
                                        ${isActive
                                            ? "bg-cyan-600 text-white"
                                            : "text-gray-300 hover:bg-white/10 hover:text-white"
                                        }`
                                    }
                                >
                                    {item.icon}
                                    <span>{item.name}</span>
                                </NavLink>
                            ))}

                            <a
                                href="https://github.com/DhirajKarangale/SatyaMark"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-2 px-4 py-2 rounded-lg 
                                    text-sm font-medium text-gray-300 
                                    hover:bg-white/10 hover:text-white transition-all duration-200 ml-2"
                            >
                                <Github size={18} />
                                <span>GitHub</span>
                            </a>
                        </div>

                        {/* Mobile Menu Button */}
                        <button
                            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                            className="md:hidden p-2 rounded-lg text-gray-300 
                                hover:bg-white/10 hover:text-white transition-colors"
                        >
                            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
                        </button>
                    </div>
                </div>

                {/* Mobile Menu */}
                <AnimatePresence>
                    {mobileMenuOpen && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: "auto" }}
                            exit={{ opacity: 0, height: 0 }}
                            transition={{ duration: 0.2 }}
                            className="md:hidden border-t border-white/10 
                                bg-slate-950/95 backdrop-blur-xl overflow-hidden"
                        >
                            <div className="px-4 py-3 space-y-1">
                                {navItems.map((item) => (
                                    <NavLink
                                        key={item.path}
                                        to={item.path}
                                        onClick={() => setMobileMenuOpen(false)}
                                        className={({ isActive }) =>
                                            `flex items-center gap-3 px-4 py-3 rounded-lg 
                                            text-base font-medium transition-all duration-200
                                            ${isActive
                                                ? "bg-cyan-600 text-white"
                                                : "text-gray-300 hover:bg-white/10 hover:text-white"
                                            }`
                                        }
                                    >
                                        {item.icon}
                                        <span>{item.name}</span>
                                    </NavLink>
                                ))}

                                <a
                                    href="https://github.com/DhirajKarangale/SatyaMark"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex items-center gap-3 px-4 py-3 rounded-lg 
                                        text-base font-medium text-gray-300 
                                        hover:bg-white/10 hover:text-white transition-all duration-200"
                                >
                                    <Github size={18} />
                                    <span>GitHub</span>
                                </a>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </motion.nav>
        </>
    );
}

export default memo(Navbar);
