import { Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Login from './pages/Login'
import Register from './pages/Register'
import DashboardRedesigned from './pages/DashboardRedesigned'
import TagsManager from './pages/TagsManager'
import GW2Test from './pages/GW2Test'
import BuilderPage from './pages/builder'
import CompositionsPage from './pages/compositions'
import ComingSoon from './pages/ComingSoon'
import ProtectedRoute from './components/ProtectedRoute'

// Create QueryClient instance
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Routes>
        {/* Auth Routes */}
        <Route path="/" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        {/* Test Routes */}
        <Route path="/gw2-test" element={<GW2Test />} />
        
        {/* Protected Routes */}
        <Route path="/dashboard" element={<ProtectedRoute><DashboardRedesigned /></ProtectedRoute>} />
        <Route path="/tags" element={<ProtectedRoute><TagsManager /></ProtectedRoute>} />
        
        {/* Functional Pages */}
        <Route path="/compositions" element={<ProtectedRoute><CompositionsPage /></ProtectedRoute>} />
        <Route path="/builder" element={<ProtectedRoute><BuilderPage /></ProtectedRoute>} />
        
        {/* Coming Soon Pages */}
        <Route path="/builds" element={
          <ProtectedRoute>
            <ComingSoon 
              pageName="Builds Library" 
              description="Parcourez et partagez des builds de personnages optimisés pour le WvW."
              features={[
                "Bibliothèque de builds communautaires",
                "Filtrage par profession et rôle",
                "Import/Export de builds",
                "Notation et commentaires",
                "Synchronisation avec l'API GW2"
              ]}
            />
          </ProtectedRoute>
        } />
        <Route path="/teams" element={
          <ProtectedRoute>
            <ComingSoon 
              pageName="Teams Manager" 
              description="Gérez vos équipes WvW et coordonnez vos membres."
              features={[
                "Création et gestion d'équipes",
                "Attribution de rôles",
                "Calendrier des événements",
                "Communication intégrée",
                "Statistiques d'équipe"
              ]}
            />
          </ProtectedRoute>
        } />
        <Route path="/settings" element={
          <ProtectedRoute>
            <ComingSoon 
              pageName="Settings" 
              description="Personnalisez votre expérience GW2 WvW Builder."
              features={[
                "Préférences d'affichage",
                "Notifications",
                "Clé API Guild Wars 2",
                "Paramètres de confidentialité",
                "Langue et région"
              ]}
            />
          </ProtectedRoute>
        } />
        <Route path="/profile" element={
          <ProtectedRoute>
            <ComingSoon 
              pageName="User Profile" 
              description="Consultez et modifiez votre profil utilisateur."
              features={[
                "Informations personnelles",
                "Compte GW2 lié",
                "Historique d'activités",
                "Compositions favorites",
                "Badges et réalisations"
              ]}
            />
          </ProtectedRoute>
        } />
      </Routes>
    </QueryClientProvider>
  )
}

export default App
