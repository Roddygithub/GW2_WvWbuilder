import { Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Login from './pages/Login'
import Register from './pages/Register'
import DashboardRedesigned from './pages/DashboardRedesigned'
import TagsManager from './pages/TagsManager'
import GW2Test from './pages/GW2Test'
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
        <Route path="/compositions" element={<ProtectedRoute><div data-testid="page-compositions">Compositions Page (stub)</div></ProtectedRoute>} />
        <Route path="/builder" element={<ProtectedRoute><div data-testid="page-builder">Builder Page (stub)</div></ProtectedRoute>} />
        <Route path="/builds" element={<ProtectedRoute><div data-testid="page-builds">Builds Page (stub)</div></ProtectedRoute>} />
        <Route path="/teams" element={<ProtectedRoute><div data-testid="page-teams">Teams Page (stub)</div></ProtectedRoute>} />
        <Route path="/settings" element={<ProtectedRoute><div data-testid="page-settings">Settings Page (stub)</div></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute><div data-testid="page-profile">Profile Page (stub)</div></ProtectedRoute>} />
      </Routes>
    </QueryClientProvider>
  )
}

export default App
