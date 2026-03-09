import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Shield, Eye, EyeOff, CheckCircle, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import { motion } from 'framer-motion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function AdminSignup() {
  const { token } = useParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  
  const [inviteData, setInviteData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [phone, setPhone] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => { validateToken(); }, [token]);

  const validateToken = async () => {
    try {
      const response = await axios.get(`${API}/admin-invites/validate/${token}`);
      setInviteData(response.data);
    } catch (error) {
      setError(error.response?.data?.detail || 'Invalid or expired invite link');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (password.length < 8) {
      toast.error('Password must be at least 8 characters'); return;
    }
    if (password !== confirmPassword) {
      toast.error('Passwords do not match'); return;
    }

    setSubmitting(true);
    try {
      const response = await axios.post(`${API}/auth/register-admin`, {
        invite_token: token,
        password,
        phone: phone || null
      });
      
      login(response.data.token, response.data.user);
      toast.success('Welcome to Atlas!');
      navigate('/');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Registration failed');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-2 border-violet-500 border-t-transparent"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center p-4">
        <Card className="max-w-md w-full border-red-200 dark:border-red-800">
          <CardContent className="p-6 text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h2 className="text-lg font-bold text-slate-900 dark:text-white mb-2">Invalid Invite</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">{error}</p>
            <Button onClick={() => navigate('/login')} variant="outline">Go to Login</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-50 via-white to-purple-50 dark:from-slate-950 dark:via-slate-900 dark:to-violet-950 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <Card className="border-violet-200 dark:border-violet-800 shadow-xl shadow-violet-500/10">
          <CardContent className="p-6">
            {/* Header */}
            <div className="text-center mb-6">
              <div className="w-14 h-14 mx-auto mb-3 rounded-xl bg-gradient-to-br from-violet-500 to-purple-500 flex items-center justify-center">
                <Shield className="h-7 w-7 text-white" />
              </div>
              <h1 className="text-xl font-bold text-slate-900 dark:text-white">Admin Registration</h1>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Complete your account setup</p>
            </div>

            {/* Invite Info */}
            <div className="p-3 rounded-lg bg-violet-50 dark:bg-violet-950/30 border border-violet-200 dark:border-violet-800 mb-4">
              <div className="flex items-center gap-3">
                <CheckCircle className="h-4 w-4 text-violet-500 flex-shrink-0" />
                <div className="text-sm">
                  <p className="font-medium text-violet-900 dark:text-violet-100">
                    {inviteData.first_name} {inviteData.last_name}
                  </p>
                  <p className="text-xs text-violet-600 dark:text-violet-400">{inviteData.email}</p>
                </div>
              </div>
              <p className="text-xs text-violet-600 dark:text-violet-400 mt-2">
                Invited by {inviteData.inviter_name}
              </p>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1">
                <Label className="text-xs">Phone (optional)</Label>
                <Input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="(555) 123-4567"
                  className="h-10"
                />
              </div>

              <div className="space-y-1">
                <Label className="text-xs">Password</Label>
                <div className="relative">
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Min 8 characters"
                    required
                    className="h-10 pr-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <div className="space-y-1">
                <Label className="text-xs">Confirm Password</Label>
                <Input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Re-enter password"
                  required
                  className={`h-10 ${password && confirmPassword && password !== confirmPassword ? 'border-red-500' : ''}`}
                />
                {password && confirmPassword && password !== confirmPassword && (
                  <p className="text-xs text-red-500">Passwords do not match</p>
                )}
              </div>

              <Button
                type="submit"
                className="w-full h-10 bg-gradient-to-r from-violet-500 to-purple-500 hover:from-violet-600 hover:to-purple-600"
                disabled={submitting || !password || !confirmPassword || password !== confirmPassword}
              >
                {submitting ? 'Creating Account...' : 'Complete Registration'}
              </Button>
            </form>

            <p className="text-center text-xs text-slate-500 dark:text-slate-400 mt-4">
              Already have an account?{' '}
              <a href="/login" className="text-violet-600 dark:text-violet-400 hover:underline">Sign in</a>
            </p>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
