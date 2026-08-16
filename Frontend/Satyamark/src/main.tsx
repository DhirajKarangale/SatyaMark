import { createRoot } from 'react-dom/client'
import { HelmetProvider } from 'react-helmet-async'
import { Analytics } from "@vercel/analytics/react"
import { SpeedInsights } from "@vercel/speed-insights/react"
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <HelmetProvider>
    <App />
    <Analytics />
    <SpeedInsights />
  </HelmetProvider>
)
