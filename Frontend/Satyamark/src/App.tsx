import { lazy, Suspense, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { LazyMotion, domAnimation } from "framer-motion";

import LayoutNavbar from './components/LayoutNavbar';
import { init } from "./process/satyamark_connect";
import { getUserId } from './utils/GenerateIds';
import { routeHome, routeChat, routeChatWithId, routeDoccu } from './utils/Routes';

const Home = lazy(() => import('./pages/Home'));
const Chat = lazy(() => import('./pages/Chat'));
const Documentation = lazy(() => import('./pages/Documentation'));
const NotFound = lazy(() => import('./pages/NotFound'));

function App() {
  useEffect(() => {
    init({ app_id: "SatyaMark", user_id: getUserId() })
  }, []);

  return (
    <LazyMotion features={domAnimation}>
      <Router>
        <Suspense fallback={
          <div className="flex h-screen w-full items-center justify-center bg-slate-950 text-cyan-400">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-cyan-400/30 border-t-cyan-400"></div>
          </div>
        }>
          <Routes>
            <Route element={<LayoutNavbar />}>
              <Route path={routeHome} element={<Home />} />
              <Route path={routeChat} element={<Chat />} />
              <Route path={routeChatWithId} element={<Chat />} />
              <Route path={routeDoccu} element={<Documentation />} />
              <Route path="*" element={<NotFound />} />
            </Route>
          </Routes>
        </Suspense>
      </Router>
    </LazyMotion>
  )
}

export default App