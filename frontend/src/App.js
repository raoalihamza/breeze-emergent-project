import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { Toaster } from './components/ui/sonner';
import Login from './pages/Login';
import Signup from './pages/Signup';
import AdminSignup from './pages/AdminSignup';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import Dashboard from './pages/Dashboard';
import MyTeam from './pages/MyTeam';
import Production from './pages/Production';
import Resources from './pages/Resources';
import CommissionCalculator from './pages/CommissionCalculator';
import ActivityTracker from './pages/ActivityTracker';
import CEOReport from './pages/CEOReport';
import Quiz from './pages/Quiz';
import AtlasQuestionLog from './pages/AtlasQuestionLog';
import Carriers from './pages/Carriers';
import CarrierDetail from './pages/CarrierDetail';
import Recruiting from './pages/Recruiting';
import Profile from './pages/Profile';
import BookOfBusiness from './pages/BookOfBusiness';
import MyClients from './pages/MyClients';
import AuditLog from './pages/AuditLog';
import MyTickets from './pages/MyTickets';
import AdminTickets from './pages/AdminTickets';
import Layout from './components/Layout';
// Client Portal imports
import {
  ClientLogin,
  ClientSetPassword,
  ClientPortalLayout,
  ClientDashboard,
  ClientPolicies,
  ClientDocuments
} from './pages/ClientPortal';
import '@/App.css';

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  return <Layout>{children}</Layout>;
}

function App() {
  return (
    <ThemeProvider>
      <div className="App noise-texture">
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/reset-password" element={<ResetPassword />} />
              <Route path="/signup/:token" element={<Signup />} />
              <Route path="/admin-signup/:token" element={<AdminSignup />} />
              <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="/team" element={<ProtectedRoute><MyTeam /></ProtectedRoute>} />
              <Route path="/production" element={<ProtectedRoute><Production /></ProtectedRoute>} />
              <Route path="/book-of-business" element={<ProtectedRoute><BookOfBusiness /></ProtectedRoute>} />
              <Route path="/my-clients" element={<ProtectedRoute><MyClients /></ProtectedRoute>} />
              <Route path="/resources" element={<ProtectedRoute><Resources /></ProtectedRoute>} />
              <Route path="/commission-calculator" element={<ProtectedRoute><CommissionCalculator /></ProtectedRoute>} />
              <Route path="/activity-tracker" element={<ProtectedRoute><ActivityTracker /></ProtectedRoute>} />
              <Route path="/ceo-report" element={<ProtectedRoute><CEOReport /></ProtectedRoute>} />
              <Route path="/quiz" element={<ProtectedRoute><Quiz /></ProtectedRoute>} />
              <Route path="/atlas-question-log" element={<ProtectedRoute><AtlasQuestionLog /></ProtectedRoute>} />
              <Route path="/carriers" element={<ProtectedRoute><Carriers /></ProtectedRoute>} />
              <Route path="/carriers/:carrierId" element={<ProtectedRoute><CarrierDetail /></ProtectedRoute>} />
              <Route path="/recruiting" element={<ProtectedRoute><Recruiting /></ProtectedRoute>} />
              <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
              <Route path="/audit-log" element={<ProtectedRoute><AuditLog /></ProtectedRoute>} />
              <Route path="/my-tickets" element={<ProtectedRoute><MyTickets /></ProtectedRoute>} />
              <Route path="/admin-tickets" element={<ProtectedRoute><AdminTickets /></ProtectedRoute>} />
              
              {/* Client Portal Routes */}
              <Route path="/client-portal/login" element={<ClientLogin />} />
              <Route path="/client-portal/setup/:token" element={<ClientSetPassword />} />
              <Route path="/client-portal" element={<ClientPortalLayout />}>
                <Route path="dashboard" element={<ClientDashboard />} />
                <Route path="policies" element={<ClientPolicies />} />
                <Route path="documents" element={<ClientDocuments />} />
                <Route index element={<Navigate to="dashboard" replace />} />
              </Route>
            </Routes>
          </BrowserRouter>
          <Toaster position="top-right" richColors />
        </AuthProvider>
      </div>
    </ThemeProvider>
  );
}

export default App;
