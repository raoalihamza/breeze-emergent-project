import { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { toast } from 'sonner';
import { motion } from 'framer-motion';
import { KeyRound, ArrowLeft, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [verifying, setVerifying] = useState(true);
  const [tokenValid, setTokenValid] = useState(false);
  const [tokenError, setTokenError] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const verifyToken = async () => {
      if (!token) {
        setTokenError('No reset token provided');
        setVerifying(false);
        return;
      }

      try {
        const response = await axios.get(`${API}/api/auth/verify-reset-token?token=${token}`);
        if (response.data.valid) {
          setTokenValid(true);
        } else {
          setTokenError(response.data.message || 'Invalid reset link');
        }
      } catch (error) {
        setTokenError('Invalid or expired reset link');
      } finally {
        setVerifying(false);
      }
    };

    verifyToken();
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (password.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }

    if (password !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    setLoading(true);
    
    try {
      await axios.post(`${API}/api/auth/reset-password`, { 
        token, 
        password 
      });
      setSuccess(true);
      toast.success('Password reset successfully');
      setTimeout(() => navigate('/login'), 3000);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to reset password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <div className="backdrop-blur-sm bg-slate-900/50 rounded-2xl border border-cyan-500/20 shadow-2xl shadow-cyan-500/10 p-8">
          {verifying ? (
            <div className="text-center py-8">
              <Loader2 className="h-12 w-12 text-cyan-400 animate-spin mx-auto mb-4" />
              <p className="text-slate-400">Verifying reset link...</p>
            </div>
          ) : !tokenValid && !success ? (
            <div className="text-center">
              <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <AlertCircle className="h-8 w-8 text-red-400" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Invalid Link</h2>
              <p className="text-slate-400 mb-6">{tokenError}</p>
              <Link to="/forgot-password">
                <Button className="bg-cyan-500 hover:bg-cyan-600 text-white">
                  Request New Reset Link
                </Button>
              </Link>
            </div>
          ) : success ? (
            <div className="text-center">
              <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="h-8 w-8 text-green-400" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Password Reset!</h2>
              <p className="text-slate-400 mb-6">
                Your password has been successfully reset. Redirecting to login...
              </p>
            </div>
          ) : (
            <>
              <div className="mb-8 text-center">
                <div className="w-16 h-16 bg-cyan-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <KeyRound className="h-8 w-8 text-cyan-400" />
                </div>
                <h2 className="text-2xl font-bold text-white mb-2">Reset Password</h2>
                <p className="text-slate-400">Enter your new password below</p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <Label htmlFor="password" className="text-slate-300 font-medium">New Password</Label>
                  <Input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    placeholder="••••••••••••"
                    className="mt-2 bg-slate-800/80 border-cyan-500/30 text-white focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
                    data-testid="reset-password-input"
                  />
                  <p className="text-slate-500 text-xs mt-1">Must be at least 8 characters</p>
                </div>

                <div>
                  <Label htmlFor="confirmPassword" className="text-slate-300 font-medium">Confirm Password</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    placeholder="••••••••••••"
                    className="mt-2 bg-slate-800/80 border-cyan-500/30 text-white focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
                    data-testid="reset-password-confirm"
                  />
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white rounded-xl py-6 text-lg font-bold shadow-lg shadow-cyan-500/30 hover:shadow-cyan-500/50 transition-all"
                  data-testid="reset-password-submit"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <Loader2 className="h-5 w-5 animate-spin" />
                      Resetting...
                    </span>
                  ) : (
                    'Reset Password'
                  )}
                </Button>
              </form>
            </>
          )}

          <div className="mt-8 pt-6 border-t border-cyan-500/20">
            <Link 
              to="/login" 
              className="flex items-center justify-center gap-2 text-cyan-400 hover:text-cyan-300 transition-colors"
              data-testid="back-to-login"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Login
            </Link>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
