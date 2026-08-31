import { memo, useState, useEffect, useRef } from "react";
import { NavLink } from "react-router-dom";
import { m, AnimatePresence } from "framer-motion";
import { Home, MessageCircleCode, FileText, Menu, X, Github, ExternalLink, Package } from "lucide-react";
import { routeHome, routeChat, routeDoccu } from "../utils/Routes";

const navItems = [
  { name: "Home", path: routeHome, icon: <Home size={18} /> },
  { name: "Chat", path: routeChat, icon: <MessageCircleCode size={18} /> },
  { name: "Documentation", path: routeDoccu, icon: <FileText size={18} /> },
];

function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navRef = useRef<HTMLElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (navRef.current && !navRef.current.contains(event.target as Node)) {
        setMobileMenuOpen(false);
      }
    }

    if (mobileMenuOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    } else {
      document.removeEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [mobileMenuOpen]);

  return (
    <>
      {/* Desktop & Mobile Navbar */}
      <m.nav
        ref={navRef}
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="fixed top-0 left-0 right-0 z-50 
                    bg-slate-950/95 md:bg-slate-950/80 md:backdrop-blur-xl 
                    border-b border-white/10
                    shadow-lg shadow-black/20"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <NavLink
              to={routeHome}
              className="flex items-center gap-2 text-white font-bold text-xl hover:text-cyan-400 transition-colors"
            >
              <img src="/Logo.png" alt="SatyaMark Logo" className="w-8 h-8 object-contain" />
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
                      ? "bg-cyan-700 text-white"
                      : "text-gray-300 hover:bg-white/10 hover:text-white"
                    }`
                  }
                >
                  {item.icon}
                  <span>{item.name}</span>
                </NavLink>
              ))}

              <div className="w-px h-6 bg-white/30 mx-2" />

              <a
                href="https://github.com/DhirajKarangale/SatyaMark"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="View SatyaMark GitHub Repository"
                className="flex items-center gap-2 px-4 py-2 rounded-lg 
                  text-sm font-medium text-gray-300 
                  hover:bg-white/10 hover:text-white transition-all duration-200"
              >
                <Github size={18} />
                <span>GitHub</span>
              </a>

              <a
                href="https://www.npmjs.com/package/satyamark-react"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="View SatyaMark NPM Package"
                className="flex items-center gap-2 px-4 py-2 rounded-lg 
                  text-sm font-medium text-gray-300 
                  hover:bg-white/10 hover:text-white transition-all duration-200"
              >
                <Package size={18} />
                <span>NPM</span>
              </a>

              <a
                href="https://satyamark-demo-socialmedia.vercel.app/"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Try SatyaMark Live Demo"
                className="flex items-center gap-2 px-4 py-2 rounded-lg 
                  text-sm font-medium text-white
                  bg-linear-to-r from-cyan-600 to-blue-600 
                  hover:from-cyan-500 hover:to-blue-500
                  shadow-lg shadow-cyan-500/25 
                  transition-all duration-200 hover:scale-105"
              >
                <ExternalLink size={18} />
                <span>Live Demo</span>
              </a>
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-label={mobileMenuOpen ? "Close mobile menu" : "Open mobile menu"}
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
            <m.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
              className="md:hidden border-t border-white/10 
                                bg-slate-950 md:bg-slate-950/95 md:backdrop-blur-xl overflow-hidden"
            >
              <div className="px-4 py-3 space-y-1">
                {/* External links in mobile menu */}

                <a
                  href="https://github.com/DhirajKarangale/SatyaMark"
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="View SatyaMark GitHub Repository"
                  className="flex items-center gap-3 px-4 py-3 rounded-lg 
                                        text-base font-medium text-gray-300 
                                        hover:bg-white/10 hover:text-white transition-all duration-200"
                >
                  <Github size={18} />
                  <span>GitHub</span>
                </a>

                <a
                  href="https://www.npmjs.com/package/satyamark-react"
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="View SatyaMark NPM Package"
                  className="flex items-center gap-3 px-4 py-3 rounded-lg 
                                        text-base font-medium text-gray-300 
                                        hover:bg-white/10 hover:text-white transition-all duration-200"
                >
                  <Package size={18} />
                  <span>NPM</span>
                </a>

                <a
                  href="https://satyamark-demo-socialmedia.vercel.app/"
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label="Try SatyaMark Live Demo"
                  className="flex items-center gap-3 px-4 py-3 rounded-lg 
                                        text-base font-medium text-white 
                                        bg-linear-to-r from-cyan-600 to-blue-600
                                        hover:from-cyan-500 hover:to-blue-500 
                                        shadow-md shadow-cyan-500/20
                                        transition-all duration-200"
                >
                  <ExternalLink size={18} />
                  <span>Live Demo</span>
                </a>
              </div>
            </m.div>
          )}
        </AnimatePresence>
      </m.nav>

      {/* Mobile Bottom Navigation */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 
                      bg-slate-950/95 md:bg-slate-950/90 md:backdrop-blur-xl border-t border-white/10">
        <div className="flex items-center justify-around h-16 px-2">
          {[navItems[1], navItems[0], navItems[2]].map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex flex-col items-center justify-center w-full h-full gap-1 
                 text-xs font-medium transition-colors
                 ${isActive ? "text-cyan-400" : "text-gray-400 hover:text-gray-300"}`
              }
            >
              {item.icon}
              <span>{item.name}</span>
            </NavLink>
          ))}
        </div>
      </nav>
    </>
  );
}

export default memo(Navbar);
