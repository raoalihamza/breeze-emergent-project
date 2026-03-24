import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Button } from './ui/button';
import ImpersonationBanner from './ImpersonationBanner';
import {
  LayoutDashboard,
  Users,
  TrendingUp,
  BookOpen,
  Building2,
  UserPlus,
  User,
  LogOut,
  Menu,
  Moon,
  Sun,
  ChevronRight,
  Shield,
  UserCircle,
  FileText,
  Ticket,
  Database
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Layout({ children }) {
  const { user, logout, impersonatedUser, stopImpersonation } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Brand color for all icons - #23ACD5
  const brandStyle = {
    gradient: 'from-[#23ACD5] to-[#1a9bc4]',
    iconColor: 'text-white'
  };

  const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'My Team', href: '/team', icon: Users },
    { name: 'Production', href: '/production', icon: TrendingUp },
    { name: 'Book of Business', href: '/book-of-business', icon: BookOpen },
    { name: 'Client Portal', href: '/my-clients', icon: UserCircle },
    { name: 'Resources', href: '/resources', icon: BookOpen },
    { name: 'Carriers', href: '/carriers', icon: Building2 },
    { name: 'Recruiting', href: '/recruiting', icon: UserPlus },
    { name: 'Tickets', href: '/my-tickets', icon: Ticket },
    { name: 'Profile', href: '/profile', icon: User },
  ];

  // Add admin-only navigation items
  const adminNavigation = user?.role === 'admin' 
    ? [
        { name: 'Manage Tickets', href: '/admin-tickets', icon: Ticket },
        { name: 'Audit Log', href: '/audit-log', icon: Shield },
        { name: 'Zinnia', href: '/zinnia-admin', icon: Database }
      ]
    : [];

  const allNavigation = [...navigation, ...adminNavigation];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#020617] transition-colors duration-200">
      {/* Mobile overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-30 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>
      
      {/* Enhanced Sidebar */}
      <aside
        className={`fixed left-0 top-0 z-40 h-screen w-72 border-r border-white/5 
          bg-white dark:bg-slate-950/80 backdrop-blur-2xl 
          shadow-2xl shadow-black/20 dark:shadow-cyan-500/5
          transition-transform duration-300 lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        data-testid="sidebar"
      >
        <div className="flex h-full flex-col relative overflow-hidden">
          {/* Subtle gradient overlay for depth */}
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/10 dark:to-black/30 pointer-events-none" />
          
          {/* Logo Area */}
          <div className="relative flex h-20 items-center gap-4 border-b border-slate-200/50 dark:border-white/5 px-6">
            <motion.div 
              className="relative flex items-center gap-3"
              whileHover={{ scale: 1.02 }}
              transition={{ type: "spring", stiffness: 400, damping: 17 }}
            >
              <img 
                src="/breeze-logo.jpeg" 
                alt="Breeze Financial Group" 
                className="h-12 w-auto object-contain drop-shadow-lg"
              />
              {/* Glow effect behind logo */}
              <div className="absolute inset-0 bg-cyan-400/10 blur-2xl rounded-full -z-10" />
            </motion.div>
            <div className="flex flex-col -ml-1">
              <span 
                className="text-2xl font-bold tracking-wide text-slate-900 dark:text-white"
                style={{ 
                  letterSpacing: '0.05em',
                  textShadow: '0 2px 8px rgba(0, 0, 0, 0.3), 0 4px 16px rgba(6, 182, 212, 0.2)'
                }}
              >
                ATLAS
              </span>
              <span className="text-[9px] uppercase tracking-widest text-slate-500 dark:text-slate-400 -mt-0.5">
                Agency OS
              </span>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1.5 px-4 py-6 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-300 dark:scrollbar-thumb-slate-700">
            {allNavigation.map((item, index) => {
              const isActive = location.pathname === item.href;
              const Icon = item.icon;
              const isComingSoon = item.comingSoon;
              
              const navItem = (
                <div
                  data-testid={`nav-${item.name.toLowerCase().replace(' ', '-')}`}
                  className={`group relative flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200 overflow-hidden ${
                    isComingSoon
                      ? 'text-slate-400 dark:text-slate-500 bg-slate-50 dark:bg-slate-900/30 cursor-not-allowed'
                      : isActive
                        ? 'text-slate-900 dark:text-white bg-slate-100/80 dark:bg-white/10'
                        : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-white/5'
                  }`}
                >
                  {/* Active indicator bar */}
                  {isActive && !isComingSoon && (
                    <motion.div
                      layoutId="activeIndicator"
                      className={`absolute left-0 top-1/2 -translate-y-1/2 h-6 w-0.5 rounded-r-full bg-gradient-to-b ${brandStyle.gradient}`}
                      transition={{ type: "spring", stiffness: 500, damping: 30 }}
                    />
                  )}
                  
                  {/* Modern Icon Container */}
                  <div className={`relative flex items-center justify-center w-8 h-8 rounded-lg transition-all duration-300 ${
                    isComingSoon
                      ? 'bg-slate-100 dark:bg-slate-800/50'
                      : `bg-gradient-to-br ${brandStyle.gradient} group-hover:scale-105`
                  }`}
                  style={{
                    boxShadow: isComingSoon ? undefined : `0 2px 8px -2px rgba(0, 0, 0, 0.15)`
                  }}
                  >
                    <Icon 
                      className={`h-4 w-4 transition-all duration-300 relative z-10 ${
                        isComingSoon 
                          ? 'text-slate-400 dark:text-slate-500' 
                          : `${brandStyle.iconColor}`
                      }`} 
                      strokeWidth={1.75} 
                    />
                  </div>
                  
                  {/* Label */}
                  <span className="flex-1 font-medium">{item.name}</span>
                  
                  {/* Coming Soon Badge */}
                  {isComingSoon && (
                    <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-slate-200 dark:bg-slate-800 text-slate-500 dark:text-slate-400 font-semibold">
                      Coming Soon
                    </span>
                  )}
                  
                  {/* Hover arrow */}
                  {!isComingSoon && (
                    <ChevronRight 
                      className={`h-4 w-4 transition-all duration-300 ${
                        isActive 
                          ? 'opacity-100 translate-x-0 text-slate-600 dark:text-slate-300' 
                          : 'opacity-0 -translate-x-2 group-hover:opacity-70 group-hover:translate-x-0'
                      }`} 
                    />
                  )}
                  
                  {/* Hover highlight effect */}
                  {!isComingSoon && (
                    <div className={`absolute inset-0 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 bg-gradient-to-r from-[#23ACD5]/5 to-transparent pointer-events-none`} />
                  )}
                </div>
              );
              
              return (
                <motion.div
                  key={item.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  {isComingSoon ? navItem : <Link to={item.href}>{navItem}</Link>}
                </motion.div>
              );
            })}
          </nav>

          {/* User Section - Floating Card Style */}
          <div className="relative border-t border-slate-200/50 dark:border-white/5 p-4 bg-slate-50/50 dark:bg-black/20 backdrop-blur-md">
            <motion.div 
              className="flex items-center gap-3 rounded-xl p-3 transition-all duration-300 hover:bg-slate-100 dark:hover:bg-white/5 cursor-pointer group"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {/* Avatar with gradient border */}
              <div className="relative">
                <div className="h-11 w-11 rounded-full bg-gradient-to-br from-cyan-400 to-blue-600 p-[2px] shadow-lg shadow-cyan-500/20">
                  <div className="h-full w-full rounded-full bg-slate-100 dark:bg-slate-900 flex items-center justify-center">
                    <User className="h-5 w-5 text-cyan-600 dark:text-cyan-400" />
                  </div>
                </div>
                {/* Online indicator */}
                <div className="absolute -bottom-0.5 -right-0.5 h-3.5 w-3.5 rounded-full bg-emerald-500 border-2 border-white dark:border-slate-900 shadow-lg" />
              </div>
              
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-slate-900 dark:text-white truncate group-hover:text-cyan-600 dark:group-hover:text-cyan-300 transition-colors" data-testid="user-name">
                  {user?.name}
                </p>
                <p className="text-[10px] text-slate-500 dark:text-slate-400 uppercase tracking-wider font-medium">
                  {user?.role}
                </p>
              </div>
            </motion.div>
            
            {/* Logout Button */}
            <motion.button
              onClick={handleLogout}
              data-testid="logout-button"
              className="mt-3 w-full flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium
                text-red-600 dark:text-red-400 
                bg-red-50 dark:bg-red-950/20 
                border border-red-200/50 dark:border-red-500/10
                hover:bg-red-100 dark:hover:bg-red-950/40 
                hover:border-red-300 dark:hover:border-red-500/20
                transition-all duration-300"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <LogOut className="h-4 w-4" />
              <span>Logout</span>
            </motion.button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="lg:ml-72 transition-all duration-300">
        {/* Impersonation Banner */}
        {impersonatedUser && (
          <ImpersonationBanner 
            impersonatedUser={impersonatedUser}
            onStopImpersonation={stopImpersonation}
          />
        )}

        {/* Top Bar */}
        <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-slate-200 dark:border-white/5 bg-white/80 dark:bg-slate-950/80 backdrop-blur-xl px-4 lg:px-6">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            data-testid="toggle-sidebar-button"
            className="hover:bg-slate-100 dark:hover:bg-white/5 lg:hidden"
          >
            <Menu className="h-5 w-5" />
          </Button>
          <div className="flex-1 text-center lg:text-left flex justify-center lg:justify-start">
            <img 
              src="/breeze-logo.jpeg" 
              alt="Breeze Financial Group" 
              className="h-8 w-auto object-contain lg:hidden"
            />
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            className="hover:bg-slate-100 dark:hover:bg-white/5"
            title={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
          >
            {theme === 'light' ? (
              <Moon className="h-5 w-5" />
            ) : (
              <Sun className="h-5 w-5" />
            )}
          </Button>
        </header>

        {/* Page Content */}
        <main className="p-4 lg:p-6">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {children}
          </motion.div>
        </main>
      </div>
    </div>
  );
}
