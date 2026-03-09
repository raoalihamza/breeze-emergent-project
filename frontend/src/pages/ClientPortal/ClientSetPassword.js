import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { toast } from 'sonner';
import { motion } from 'framer-motion';
import { Shield, Lock, Eye, EyeOff, CheckCircle, User, AlertCircle } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function ClientSetPassword() {
  const navigate = useNavigate();
  const { token } = useParams();
  const [loading, setLoading] = useState(true);
  const [validating, setValidating] = useState(true);
  const [inviteData, setInviteData] = useState(null);
  const [error, setError] = useState(null);
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    // Force light mode for client portal
    document.documentElement.classList.remove('dark');
    validateToken();
  }, [token]);

  const validateToken = async () => {
    try {
      const response = await axios.get(`${API}/portal/invite/validate/${token}`);
      setInviteData(response.data);
    } catch (error) {
      setError(error.response?.data?.detail || 'Invalid or expired invite link');
    } finally {
      setValidating(false);
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (password !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }
    
    if (password.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }
    
    setSubmitting(true);
    
    try {
      const response = await axios.post(`${API}/portal/auth/set-password`, {
        invite_token: token,
        password
      });
      
      localStorage.setItem('portal_token', response.data.token);
      localStorage.setItem('portal_client', JSON.stringify(response.data.client));
      
      toast.success('Account activated successfully!');
      navigate('/client-portal/dashboard');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to set password');
    } finally {
      setSubmitting(false);
    }
  };

  const passwordStrength = () => {
    if (password.length === 0) return { level: 0, text: '', color: '' };
    if (password.length < 6) return { level: 1, text: 'Weak', color: 'bg-red-500' };
    if (password.length < 10) return { level: 2, text: 'Fair', color: 'bg-amber-500' };
    if (password.length < 14) return { level: 3, text: 'Good', color: 'bg-cyan-500' };
    return { level: 4, text: 'Strong', color: 'bg-emerald-500' };
  };

  const strength = passwordStrength();

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-cyan-50/30 to-blue-50/40 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 flex items-center justify-center">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 border-3 border-cyan-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-slate-600 dark:text-slate-400">Validating invite...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-cyan-50/30 to-blue-50/40 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 flex items-center justify-center p-4">
        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="max-w-md w-full">
          <Card className="border-red-200 dark:border-red-900/50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl">
            <CardContent className="pt-6 text-center">
              <div className="h-14 w-14 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center mx-auto mb-4">
                <AlertCircle className="h-7 w-7 text-red-500" />
              </div>
              <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">Invalid Invite Link</h2>
              <p className="text-slate-600 dark:text-slate-400 mb-6">{error}</p>
              <Button onClick={() => navigate('/client-portal/login')} variant="outline">
                Go to Login
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-cyan-50/30 to-blue-50/40 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#8882_1px,transparent_1px),linear-gradient(to_bottom,#8882_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none opacity-30" />
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md relative z-10"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Shield className="h-6 w-6 text-white" />
            </div>
            <div className="text-left">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent">
                Breeze Client Portal
              </h1>
              <p className="text-xs text-slate-500 dark:text-slate-400">Activate your account</p>
            </div>
          </div>
        </div>

        <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl shadow-xl">
          <CardHeader className="text-center pb-2">
            <CardTitle className="text-xl text-slate-900 dark:text-white">Set Your Password</CardTitle>
            <CardDescription>
              Welcome, {inviteData?.client_first_name}! Create a secure password to access your portal.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Advisor Info */}
            <div className="mb-6 p-4 rounded-xl bg-gradient-to-r from-cyan-50 to-blue-50 dark:from-cyan-950/30 dark:to-blue-950/30 border border-cyan-100 dark:border-cyan-900/30">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-full bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center">
                  <User className="h-5 w-5 text-white" />
                </div>
                <div>
                  <p className="text-xs text-cyan-700 dark:text-cyan-400 font-medium">Your Advisor</p>
                  <p className="text-sm font-semibold text-slate-900 dark:text-white">{inviteData?.agent_name}</p>
                </div>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm text-slate-700 dark:text-slate-300">Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Create a strong password"
                    className="pl-10 pr-10 h-11 bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700"
                    required
                    minLength={8}
                    data-testid="new-password-input"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                
                {/* Password Strength Indicator */}
                {password.length > 0 && (
                  <div className="space-y-1">
                    <div className="flex gap-1">
                      {[1, 2, 3, 4].map((level) => (
                        <div
                          key={level}
                          className={`h-1 flex-1 rounded-full transition-colors ${
                            strength.level >= level ? strength.color : 'bg-slate-200 dark:bg-slate-700'
                          }`}
                        />
                      ))}
                    </div>
                    <p className="text-xs text-slate-500 dark:text-slate-400">Password strength: {strength.text}</p>
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirmPassword" className="text-sm text-slate-700 dark:text-slate-300">Confirm Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                  <Input
                    id="confirmPassword"
                    type={showPassword ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Confirm your password"
                    className="pl-10 h-11 bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700"
                    required
                    data-testid="confirm-password-input"
                  />
                  {confirmPassword && password === confirmPassword && (
                    <CheckCircle className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-emerald-500" />
                  )}
                </div>
              </div>

              <Button
                type="submit"
                className="w-full h-11 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white font-medium"
                disabled={submitting || password !== confirmPassword || password.length < 8}
                data-testid="activate-account-button"
              >
                {submitting ? (
                  <div className="flex items-center gap-2">
                    <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Activating...
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4" />
                    Activate Account
                  </div>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        <div className="mt-6 text-center">
          <p className="text-xs text-slate-400 dark:text-slate-500">
            Secure portal powered by Breeze Wealth Management
          </p>
        </div>
      </motion.div>
    </div>
  );
}
