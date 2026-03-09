import { useState, useEffect } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { toast } from 'sonner';
import { motion } from 'framer-motion';
import { Moon, Sun } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // Show session expired message if redirected due to token expiration
  useEffect(() => {
    if (searchParams.get('expired') === 'true') {
      toast.error('Your session has expired. Please log in again.');
    }
  }, [searchParams]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await login(email, password);
      toast.success('Welcome back!');
      navigate('/');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row bg-white dark:bg-slate-950 transition-colors duration-200">
      {/* Theme toggle button */}
      <button
        onClick={toggleTheme}
        className="fixed top-4 right-4 z-50 p-2 rounded-full bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
        title={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
      >
        {theme === 'light' ? (
          <Moon className="h-5 w-5 text-slate-700" />
        ) : (
          <Sun className="h-5 w-5 text-slate-300" />
        )}
      </button>

      {/* Left Side - Enhanced Atlas Network Visualization - 45% */}
      <div className="lg:w-[45%] relative overflow-hidden flex items-center justify-center px-8 py-16 lg:py-0 bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
        <style>{
          `
          @keyframes dataFlow1 {
            0%, 100% { stroke-dashoffset: 0; }
            50% { stroke-dashoffset: -100; }
          }
          
          @keyframes dataFlow2 {
            0%, 100% { stroke-dashoffset: 0; }
            50% { stroke-dashoffset: -150; }
          }
          
          @keyframes dataFlow3 {
            0%, 100% { stroke-dashoffset: 0; }
            50% { stroke-dashoffset: -120; }
          }
          
          @keyframes nodePulse {
            0%, 100% { opacity: 0.6; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.2); }
          }
          
          @keyframes nodeGlow {
            0%, 100% { opacity: 0.4; }
            50% { opacity: 0.9; }
          }
          
          @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-12px); }
          }
          
          @keyframes particleFloat {
            0% { transform: translate(0, 0); opacity: 0; }
            10% { opacity: 0.6; }
            90% { opacity: 0.6; }
            100% { transform: translate(0, -120px); opacity: 0; }
          }
          
          @keyframes scanline {
            0% { transform: translateY(-100%); }
            100% { transform: translateY(100%); }
          }
          
          @keyframes gridPulse {
            0%, 100% { opacity: 0.03; }
            50% { opacity: 0.08; }
          }
          
          @keyframes textGlow {
            0%, 100% { text-shadow: 0 0 20px rgba(35, 172, 213, 0.6), 0 0 40px rgba(35, 172, 213, 0.4); }
            50% { text-shadow: 0 0 30px rgba(35, 172, 213, 0.9), 0 0 60px rgba(35, 172, 213, 0.6), 0 0 80px rgba(35, 172, 213, 0.4); }
          }
          
          @keyframes cornerGlow {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 0.8; }
          }
          
          .data-line-1 { animation: dataFlow1 6s ease-in-out infinite; }
          .data-line-2 { animation: dataFlow2 8s ease-in-out infinite; }
          .data-line-3 { animation: dataFlow3 10s ease-in-out infinite; }
          .node-pulse { animation: nodePulse 3s ease-in-out infinite; }
          .node-glow { animation: nodeGlow 2.5s ease-in-out infinite; }
          .float-animation { animation: float 5s ease-in-out infinite; }
          .particle { animation: particleFloat 8s linear infinite; }
          .scanline { animation: scanline 4s linear infinite; }
          .grid-pulse { animation: gridPulse 4s ease-in-out infinite; }
          .text-glow { animation: textGlow 3s ease-in-out infinite; }
          .corner-glow { animation: cornerGlow 2s ease-in-out infinite; }
          `
        }</style>
        
        {/* Animated Scanline Effect */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none z-20">
          <div className="scanline absolute inset-x-0 h-40 bg-gradient-to-b from-transparent via-cyan-500/10 to-transparent blur-sm" />
        </div>
        
        {/* Floating Particles */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none z-10">
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className="particle absolute w-1 h-1 bg-cyan-400 rounded-full shadow-lg shadow-cyan-500/50"
              style={{
                left: `${10 + Math.random() * 80}%`,
                top: `${10 + Math.random() * 80}%`,
                animationDelay: `${Math.random() * 8}s`,
                animationDuration: `${6 + Math.random() * 4}s`,
              }}
            />
          ))}
        </div>

        {/* Tech Corner Accents */}
        <div className="absolute top-8 left-8 w-16 h-16 border-t-2 border-l-2 border-cyan-500/40 corner-glow pointer-events-none z-30" />
        <div className="absolute top-8 right-8 w-16 h-16 border-t-2 border-r-2 border-cyan-500/40 corner-glow pointer-events-none z-30" style={{ animationDelay: '0.5s' }} />
        <div className="absolute bottom-8 left-8 w-16 h-16 border-b-2 border-l-2 border-cyan-500/40 corner-glow pointer-events-none z-30" style={{ animationDelay: '1s' }} />
        <div className="absolute bottom-8 right-8 w-16 h-16 border-b-2 border-r-2 border-cyan-500/40 corner-glow pointer-events-none z-30" style={{ animationDelay: '1.5s' }} />
        
        <svg
          className="absolute inset-0 w-full h-full"
          viewBox="0 0 1000 1000"
          preserveAspectRatio="xMidYMid slice"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <radialGradient id="nodeGrad1">
              <stop offset="0%" style={{ stopColor: '#FFFFFF', stopOpacity: 1 }} />
              <stop offset="40%" style={{ stopColor: '#23ACD5', stopOpacity: 0.9 }} />
              <stop offset="100%" style={{ stopColor: '#23ACD5', stopOpacity: 0 }} />
            </radialGradient>
            
            <radialGradient id="nodeGrad2">
              <stop offset="0%" style={{ stopColor: '#23ACD5', stopOpacity: 1 }} />
              <stop offset="100%" style={{ stopColor: '#1B8CA4', stopOpacity: 0 }} />
            </radialGradient>
            
            <linearGradient id="lineGrad1" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" style={{ stopColor: '#23ACD5', stopOpacity: 0 }} />
              <stop offset="50%" style={{ stopColor: '#23ACD5', stopOpacity: 0.7 }} />
              <stop offset="100%" style={{ stopColor: '#23ACD5', stopOpacity: 0 }} />
            </linearGradient>
            
            <linearGradient id="lineGrad2" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style={{ stopColor: '#23ACD5', stopOpacity: 0 }} />
              <stop offset="50%" style={{ stopColor: '#2EC4F0', stopOpacity: 0.6 }} />
              <stop offset="100%" style={{ stopColor: '#23ACD5', stopOpacity: 0 }} />
            </linearGradient>
            
            <filter id="nodeGlow">
              <feGaussianBlur stdDeviation="8" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
            
            <filter id="lineGlow">
              <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
            
            <radialGradient id="vignette">
              <stop offset="0%" style={{ stopColor: '#000000', stopOpacity: 0 }} />
              <stop offset="70%" style={{ stopColor: '#000000', stopOpacity: 0 }} />
              <stop offset="100%" style={{ stopColor: '#000000', stopOpacity: 0.5 }} />
            </radialGradient>
          </defs>
          
          {/* Enhanced Grid with Pulse */}
          <g className="grid-pulse">
            {[...Array(10)].map((_, i) => (
              <line
                key={`v${i}`}
                x1={100 * i}
                y1="0"
                x2={100 * i}
                y2="1000"
                stroke="#23ACD5"
                strokeWidth="1"
              />
            ))}
            {[...Array(10)].map((_, i) => (
              <line
                key={`h${i}`}
                x1="0"
                y1={100 * i}
                x2="1000"
                y2={100 * i}
                stroke="#23ACD5"
                strokeWidth="1"
              />
            ))}
          </g>
          
          {/* Enhanced Connection Lines */}
          <g filter="url(#lineGlow)">
            <line x1="600" y1="250" x2="750" y2="180" stroke="url(#lineGrad1)" strokeWidth="2.5" opacity="0.5" className="data-line-1" strokeDasharray="10 5" />
            <line x1="750" y1="180" x2="850" y2="320" stroke="url(#lineGrad1)" strokeWidth="2.5" opacity="0.5" className="data-line-2" strokeDasharray="10 5" />
            <line x1="850" y1="320" x2="800" y2="520" stroke="url(#lineGrad2)" strokeWidth="2.5" opacity="0.4" className="data-line-3" strokeDasharray="10 5" />
            <line x1="600" y1="250" x2="700" y2="400" stroke="url(#lineGrad1)" strokeWidth="2.5" opacity="0.5" className="data-line-1" strokeDasharray="10 5" />
            <line x1="700" y1="400" x2="800" y2="520" stroke="url(#lineGrad2)" strokeWidth="2.5" opacity="0.4" className="data-line-2" strokeDasharray="10 5" />
            <line x1="550" y1="450" x2="700" y2="400" stroke="url(#lineGrad1)" strokeWidth="2" opacity="0.4" className="data-line-3" strokeDasharray="8 4" />
            <line x1="700" y1="400" x2="750" y2="650" stroke="url(#lineGrad2)" strokeWidth="2" opacity="0.35" className="data-line-1" strokeDasharray="8 4" />
            <line x1="850" y1="320" x2="920" y2="480" stroke="url(#lineGrad1)" strokeWidth="2" opacity="0.4" className="data-line-2" strokeDasharray="8 4" />
            <line x1="800" y1="520" x2="920" y2="480" stroke="url(#lineGrad2)" strokeWidth="2" opacity="0.35" className="data-line-3" strokeDasharray="8 4" />
            <line x1="450" y1="350" x2="550" y2="450" stroke="url(#lineGrad1)" strokeWidth="1.5" opacity="0.3" className="data-line-2" strokeDasharray="6 3" />
            <line x1="600" y1="250" x2="550" y2="450" stroke="url(#lineGrad2)" strokeWidth="1.5" opacity="0.3" className="data-line-1" strokeDasharray="6 3" />
            <line x1="750" y1="650" x2="800" y2="780" stroke="url(#lineGrad1)" strokeWidth="1.5" opacity="0.3" className="data-line-3" strokeDasharray="6 3" />
            <line x1="920" y1="480" x2="950" y2="620" stroke="url(#lineGrad2)" strokeWidth="1.5" opacity="0.3" className="data-line-2" strokeDasharray="6 3" />
            <line x1="200" y1="400" x2="350" y2="500" stroke="url(#lineGrad1)" strokeWidth="1.5" opacity="0.2" className="data-line-1" strokeDasharray="6 3" />
            <line x1="350" y1="500" x2="450" y2="350" stroke="url(#lineGrad2)" strokeWidth="1.5" opacity="0.2" className="data-line-3" strokeDasharray="6 3" />
          </g>
          
          {/* Enhanced Nodes */}
          <g>
            <g className="float-animation" style={{ animationDelay: '0s' }}>
              <circle cx="750" cy="180" r="10" fill="url(#nodeGrad1)" filter="url(#nodeGlow)" className="node-pulse" style={{ animationDelay: '0s' }} />
              <circle cx="750" cy="180" r="20" fill="url(#nodeGrad2)" opacity="0.4" className="node-glow" />
            </g>
            
            <g className="float-animation" style={{ animationDelay: '1s' }}>
              <circle cx="600" cy="250" r="9" fill="url(#nodeGrad1)" filter="url(#nodeGlow)" className="node-pulse" style={{ animationDelay: '1s' }} />
              <circle cx="600" cy="250" r="18" fill="url(#nodeGrad2)" opacity="0.4" className="node-glow" />
            </g>
            
            <g className="float-animation" style={{ animationDelay: '2s' }}>
              <circle cx="850" cy="320" r="9" fill="url(#nodeGrad1)" filter="url(#nodeGlow)" className="node-pulse" style={{ animationDelay: '2s' }} />
              <circle cx="850" cy="320" r="18" fill="url(#nodeGrad2)" opacity="0.4" className="node-glow" />
            </g>
            
            <g className="float-animation" style={{ animationDelay: '0.5s' }}>
              <circle cx="700" cy="400" r="8" fill="url(#nodeGrad1)" filter="url(#nodeGlow)" className="node-pulse" style={{ animationDelay: '1.5s' }} />
              <circle cx="700" cy="400" r="16" fill="url(#nodeGrad2)" opacity="0.4" className="node-glow" />
            </g>
            
            <g className="float-animation" style={{ animationDelay: '1.5s' }}>
              <circle cx="800" cy="520" r="9" fill="url(#nodeGrad1)" filter="url(#nodeGlow)" className="node-pulse" style={{ animationDelay: '2.5s' }} />
              <circle cx="800" cy="520" r="18" fill="url(#nodeGrad2)" opacity="0.4" className="node-glow" />
            </g>
            
            <g className="float-animation" style={{ animationDelay: '2.5s' }}>
              <circle cx="550" cy="450" r="7" fill="url(#nodeGrad1)" filter="url(#nodeGlow)" className="node-pulse" style={{ animationDelay: '0.5s' }} />
              <circle cx="550" cy="450" r="14" fill="url(#nodeGrad2)" opacity="0.35" className="node-glow" />
            </g>
            
            <g className="float-animation" style={{ animationDelay: '3s' }}>
              <circle cx="920" cy="480" r="7" fill="url(#nodeGrad1)" filter="url(#nodeGlow)" className="node-pulse" style={{ animationDelay: '3s' }} />
              <circle cx="920" cy="480" r="14" fill="url(#nodeGrad2)" opacity="0.35" className="node-glow" />
            </g>
            
            <g className="float-animation" style={{ animationDelay: '1.2s' }}>
              <circle cx="750" cy="650" r="7" fill="url(#nodeGrad1)" filter="url(#nodeGlow)" className="node-pulse" style={{ animationDelay: '2s' }} />
              <circle cx="750" cy="650" r="14" fill="url(#nodeGrad2)" opacity="0.35" className="node-glow" />
            </g>
            
            <g className="float-animation" style={{ animationDelay: '3.5s' }}>
              <circle cx="450" cy="350" r="6" fill="url(#nodeGrad1)" filter="url(#nodeGlow)" className="node-pulse" style={{ animationDelay: '1s' }} />
              <circle cx="450" cy="350" r="12" fill="url(#nodeGrad2)" opacity="0.3" className="node-glow" />
            </g>
            
            <g className="float-animation" style={{ animationDelay: '4s' }}>
              <circle cx="800" cy="780" r="6" fill="url(#nodeGrad1)" filter="url(#nodeGlow)" className="node-pulse" style={{ animationDelay: '3.5s' }} />
              <circle cx="800" cy="780" r="12" fill="url(#nodeGrad2)" opacity="0.3" className="node-glow" />
            </g>
            
            <g className="float-animation" style={{ animationDelay: '4.5s' }}>
              <circle cx="950" cy="620" r="6" fill="url(#nodeGrad1)" filter="url(#nodeGlow)" className="node-pulse" style={{ animationDelay: '2.8s' }} />
              <circle cx="950" cy="620" r="12" fill="url(#nodeGrad2)" opacity="0.3" className="node-glow" />
            </g>
            
            <g className="float-animation" style={{ animationDelay: '5s' }}>
              <circle cx="200" cy="400" r="5" fill="url(#nodeGrad1)" filter="url(#nodeGlow)" className="node-pulse" style={{ animationDelay: '4s' }} />
              <circle cx="200" cy="400" r="10" fill="url(#nodeGrad2)" opacity="0.25" className="node-glow" />
            </g>
            
            <g className="float-animation" style={{ animationDelay: '5.5s' }}>
              <circle cx="350" cy="500" r="5" fill="url(#nodeGrad1)" filter="url(#nodeGlow)" className="node-pulse" style={{ animationDelay: '4.5s' }} />
              <circle cx="350" cy="500" r="10" fill="url(#nodeGrad2)" opacity="0.25" className="node-glow" />
            </g>
          </g>
          
          <rect x="0" y="0" width="1000" height="1000" fill="url(#vignette)" />
        </svg>

        {/* Enhanced Atlas Title */}
        <div className="relative z-10 text-center lg:text-left max-w-lg">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-4xl sm:text-5xl lg:text-7xl font-bold mb-4 lg:mb-6 text-glow leading-tight" style={{
              background: 'linear-gradient(135deg, #FFFFFF 0%, #23ACD5 50%, #FFFFFF 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              letterSpacing: '0.05em'
            }}>
              WELCOME TO<br className="sm:hidden" /> ATLAS
            </h1>
            <div className="h-0.5 w-24 lg:w-32 bg-gradient-to-r from-transparent via-cyan-500 to-transparent mb-4 lg:mb-6" />
            <p className="text-sm sm:text-base lg:text-lg text-cyan-100/80 max-w-md font-light tracking-wide">
              The official internal agent portal for Breeze Financial Group.
            </p>
          </motion.div>
        </div>
      </div>

      {/* Right Side - Enhanced Login Form - 55% */}
      <div className="lg:w-[55%] flex items-center justify-center px-8 py-16 bg-white dark:bg-slate-950 relative">
        {/* Subtle Grid Background */}
        <div className="absolute inset-0 opacity-5 dark:opacity-10" style={{
          backgroundImage: 'linear-gradient(#23ACD5 1px, transparent 1px), linear-gradient(90deg, #23ACD5 1px, transparent 1px)',
          backgroundSize: '50px 50px'
        }} />
        
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="w-full max-w-md relative z-10"
        >
          {/* Glassmorphism Container */}
          <div className="backdrop-blur-sm bg-white/50 dark:bg-slate-900/50 rounded-2xl border border-slate-200/50 dark:border-cyan-500/20 shadow-2xl shadow-cyan-500/10 p-8">
            <div className="mb-8">
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">Access Portal</h2>
              <div className="h-1 w-16 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full mb-4" />
              <p className="text-slate-600 dark:text-slate-400">Authenticate to continue</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <Label htmlFor="email" className="text-slate-700 dark:text-slate-300 font-medium">Email Address</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="agent@breezefg.com"
                  className="mt-2 bg-white/80 dark:bg-slate-800/80 border-slate-300 dark:border-cyan-500/30 text-slate-900 dark:text-white focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 transition-all"
                />
              </div>

              <div>
                <div className="flex justify-between items-center">
                  <Label htmlFor="password" className="text-slate-700 dark:text-slate-300 font-medium">Password</Label>
                  <Link 
                    to="/forgot-password" 
                    className="text-sm text-cyan-500 hover:text-cyan-400 transition-colors"
                    data-testid="forgot-password-link"
                  >
                    Forgot Password?
                  </Link>
                </div>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="••••••••••••"
                  className="mt-2 bg-white/80 dark:bg-slate-800/80 border-slate-300 dark:border-cyan-500/30 text-slate-900 dark:text-white focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20 transition-all"
                />
              </div>

              <Button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-cyan-500 via-blue-500 to-cyan-600 hover:from-cyan-600 hover:via-blue-600 hover:to-cyan-700 text-white rounded-xl py-6 text-lg font-bold shadow-lg shadow-cyan-500/30 hover:shadow-cyan-500/50 transition-all duration-300 transform hover:scale-[1.02]"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    AUTHENTICATING...
                  </span>
                ) : (
                  'ENTER'
                )}
              </Button>
            </form>

            <div className="mt-8 pt-6 border-t border-slate-200 dark:border-cyan-500/20">
              <p className="text-center text-sm text-slate-600 dark:text-slate-400">
                Secure access portal • <span className="text-cyan-500 font-medium">256-bit encryption</span>
              </p>
            </div>
          </div>
          
          {/* Tech Accent Lines */}
          <div className="absolute -right-4 top-1/2 w-24 h-0.5 bg-gradient-to-r from-cyan-500/50 to-transparent corner-glow" />
          <div className="absolute -left-4 top-1/3 w-24 h-0.5 bg-gradient-to-l from-cyan-500/50 to-transparent corner-glow" style={{ animationDelay: '1s' }} />
        </motion.div>
      </div>
    </div>
  );
}
