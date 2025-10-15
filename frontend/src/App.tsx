import { Routes, Route } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import DashboardRedesigned from './pages/DashboardRedesigned'
import TagsManager from './pages/TagsManager'
import GW2Test from './pages/GW2Test'
import BuilderV2Page from './pages/BuilderV2'
import CompositionsPage from './pages/compositions'
import CompositionCreate from './pages/CompositionCreate'
import ComingSoon from './pages/ComingSoon'
import ProtectedRoute from './components/ProtectedRoute'
import MainLayout from './components/layout/MainLayout'

function App() {
  return (
    <Routes>
      {/* Auth Routes */}
      <Route path="/" element={<Login />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      {/* Test Routes */}
      <Route path="/gw2-test" element={<GW2Test />} />
      
      {/* Protected Routes */}
      {/* Dashboard has its own layout (Sidebar + Header integrated) */}
      <Route path="/dashboard" element={<ProtectedRoute><DashboardRedesigned /></ProtectedRoute>} />
      <Route path="/tags" element={<ProtectedRoute><MainLayout><TagsManager /></MainLayout></ProtectedRoute>} />
      
      {/* Functional Pages */}
      <Route path="/compositions" element={<ProtectedRoute><MainLayout><CompositionsPage /></MainLayout></ProtectedRoute>} />
      {/* Create Composition */}
      <Route path="/compositions/new" element={
        <ProtectedRoute>
          <MainLayout>
            <CompositionCreate />
          </MainLayout>
        </ProtectedRoute>
      } />
      <Route path="/builder" element={<ProtectedRoute><BuilderV2Page /></ProtectedRoute>} />
      
      {/* Coming Soon Pages */}
      <Route path="/builds" element={
        <ProtectedRoute>
          <MainLayout>
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
          </MainLayout>
        </ProtectedRoute>
      } />
      <Route path="/teams" element={
        <ProtectedRoute>
          <MainLayout>
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
          </MainLayout>
        </ProtectedRoute>
      } />
      <Route path="/settings" element={
        <ProtectedRoute>
          <MainLayout>
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
          </MainLayout>
        </ProtectedRoute>
      } />
      <Route path="/profile" element={
        <ProtectedRoute>
          <MainLayout>
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
          </MainLayout>
        </ProtectedRoute>
      } />
    </Routes>
  )
}

export default App
