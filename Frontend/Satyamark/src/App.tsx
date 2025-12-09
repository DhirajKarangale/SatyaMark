import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Home from './pages/Home';
import About from './pages/About';
import Documentation from './pages/Documentation';

import SetBG from './backgrounds/SetBG';
import LayoutNavbar from './components/LayoutNavbar';

import { routeHome, routeAbout, routeDoccu } from './utils/Routes';

function App() {

  return (
    <Router>
      <SetBG />

      <Routes>
        <Route element={<LayoutNavbar />}>
          <Route path={routeHome} element={<Home />} />
          <Route path={routeAbout} element={<About />} />
          <Route path={routeDoccu} element={<Documentation />} />
        </Route>

      </Routes>
    </Router>
  )
}

export default App
