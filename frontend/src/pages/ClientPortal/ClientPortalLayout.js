import { useState, useEffect, createContext, useContext } from 'react';
import { useNavigate, Outlet, Link, useLocation } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Shield, Home, FileText, FolderOpen, Calendar, LogOut, User,
  ChevronRight, Menu, X, Phone, Mail
} from 'lucide-react';
import { Button } from '../../components/ui/button';
import { Card, CardContent } from '../../components/ui/card';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Client Auth Context
const ClientAuthContext = createContext();

export function useClientAuth() {
  return useContext(ClientAuthContext);
}

export default function ClientPortalLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const [client, setClient] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    // Force light mode for client portal
    document.documentElement.classList.remove('dark');
    
    const token = localStorage.getItem('portal_token');
    if (!token) {
      navigate('/client-portal/login');
      return;
    }
    fetchDashboard();
  }, []);

  const getAuthHeader = () => ({
    headers: { Authorization: `Bearer ${localStorage.getItem('portal_token')}` }
  });

  const fetchDashboard = async () => {
    try {
      const response = await axios.get(`${API}/portal/dashboard`, getAuthHeader());
      setDashboardData(response.data);
      setClient(response.data.client);
    } catch (error) {
      if (error.response?.status === 401) {
        handleLogout();
      } else {
        toast.error('Failed to load dashboard');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('portal_token');
    localStorage.removeItem('portal_client');
    navigate('/client-portal/login');
  };

  const navItems = [
    { path: '/client-portal/dashboard', label: 'Dashboard', icon: Home },
    { path: '/client-portal/policies', label: 'My Policies', icon: FileText },
    { path: '/client-portal/documents', label: 'Documents', icon: FolderOpen },
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-cyan-50/30 to-blue-50/40 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="h-12 w-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-slate-600 dark:text-slate-400">Loading your portal...</span>
        </div>
      </div>
    );
  }

  return (
    <ClientAuthContext.Provider value={{ client, dashboardData, getAuthHeader, fetchDashboard }}>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-cyan-50/30 to-blue-50/40 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
        {/* Background Pattern */}
        <div className="fixed inset-0 bg-[linear-gradient(to_right,#8882_1px,transparent_1px),linear-gradient(to_bottom,#8882_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none opacity-20" />
        
        {/* Top Navigation Bar */}
        <header className="sticky top-0 z-50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border-b border-slate-200/80 dark:border-slate-800/50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              {/* Logo */}
              <div className="flex items-center gap-3">
                <img 
                  src="/breeze-logo.jpeg" 
                  alt="Breeze Financial Group" 
                  className="h-10 w-auto object-contain"
                />
                <div className="hidden sm:block border-l border-slate-300 pl-3">
                  <h1 className="text-base font-bold text-slate-900 dark:text-white">
                    Client Portal
                  </h1>
                  <p className="text-xs text-slate-500 dark:text-slate-400">Breeze Financial Group</p>
                </div>
              </div>

              {/* Desktop Navigation */}
              <nav className="hidden md:flex items-center gap-1">
                {navItems.map((item) => {
                  const isActive = location.pathname === item.path;
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                        isActive
                          ? 'bg-gradient-to-r from-cyan-500/10 to-blue-500/10 text-cyan-700 dark:text-cyan-400'
                          : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
                      }`}
                    >
                      <item.icon className="h-4 w-4" />
                      {item.label}
                    </Link>
                  );
                })}
              </nav>

              {/* User Menu */}
              <div className="flex items-center gap-3">
                <div className="hidden sm:block text-right">
                  <p className="text-sm font-medium text-slate-900 dark:text-white">
                    {client?.first_name} {client?.last_name}
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">{client?.email}</p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                  className="text-slate-600 dark:text-slate-400 hover:text-red-500"
                  data-testid="logout-button"
                >
                  <LogOut className="h-4 w-4" />
                </Button>
                
                {/* Mobile Menu Button */}
                <Button
                  variant="ghost"
                  size="sm"
                  className="md:hidden"
                  onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                >
                  {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
                </Button>
              </div>
            </div>
          </div>

          {/* Mobile Navigation */}
          <AnimatePresence>
            {mobileMenuOpen && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="md:hidden border-t border-slate-200 dark:border-slate-800 bg-white/95 dark:bg-slate-900/95"
              >
                <nav className="p-4 space-y-2">
                  {navItems.map((item) => {
                    const isActive = location.pathname === item.path;
                    return (
                      <Link
                        key={item.path}
                        to={item.path}
                        onClick={() => setMobileMenuOpen(false)}
                        className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                          isActive
                            ? 'bg-gradient-to-r from-cyan-500/10 to-blue-500/10 text-cyan-700 dark:text-cyan-400'
                            : 'text-slate-600 dark:text-slate-400'
                        }`}
                      >
                        <item.icon className="h-5 w-5" />
                        {item.label}
                      </Link>
                    );
                  })}
                </nav>
              </motion.div>
            )}
          </AnimatePresence>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 relative z-10">
          <Outlet />
        </main>

        {/* Footer */}
        <footer className="border-t border-slate-200/80 dark:border-slate-800/50 bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm mt-auto">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
                <Shield className="h-4 w-4" />
                <span>Secure Client Portal by Breeze Wealth Management</span>
              </div>
              {dashboardData?.settings?.global_disclaimer_text && (
                <p className="text-xs text-slate-400 dark:text-slate-500 text-center sm:text-right max-w-md">
                  {dashboardData.settings.global_disclaimer_text}
                </p>
              )}
            </div>
          </div>
        </footer>
      </div>
    </ClientAuthContext.Provider>
  );
}
