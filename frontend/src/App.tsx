import { Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import { ThemeProvider } from '@/components/theme-provider'
import Layout from '@/components/layout/layout'
import HomePage from '@/pages/home'
import BuilderPage from '@/pages/builder'
import CompositionsPage from '@/pages/compositions'
import AboutPage from '@/pages/about'
import NotFoundPage from '@/pages/not-found'

function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="gw2-wvwbuilder-theme">
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/builder" element={<BuilderPage />} />
          <Route path="/compositions" element={<CompositionsPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
        <Toaster />
      </Layout>
    </ThemeProvider>
  )
}

export default App
