import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Home from './pages/Home';
import About from './pages/About';
import NotFound from "./pages/NotFound";
import Documentation from './pages/Documentation';

import SetBG from './backgrounds/SetBG';
import LayoutNavbar from './components/LayoutNavbar';

import { useEffect } from "react";
import { init } from "./process/satyamark_connect";
import { getUserId } from './utils/GenerateIds';

import { routeHome, routeHomeWithId, routeAbout, routeDoccu } from './utils/Routes';

function App() {
  useEffect(() => {
    init({ app_id: "Satyamark", user_id: getUserId() })
  }, []);

  return (
    <Router>
      <SetBG />

      <Routes>
        <Route element={<LayoutNavbar />}>
          <Route path={routeHome} element={<Home />} />
          <Route path={routeHomeWithId} element={<Home />} />
          <Route path={routeAbout} element={<About />} />
          <Route path={routeDoccu} element={<Documentation />} />
          <Route path="*" element={<NotFound />} />
        </Route>

      </Routes>
    </Router>
  )
}

export default App