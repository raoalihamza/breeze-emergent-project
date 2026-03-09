import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { toast } from 'sonner';
import axios from 'axios';
import { motion } from 'framer-motion';
import { AlertCircle, ArrowLeft } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function Signup() {
  const { token } = useParams();
  const [inviteData, setInviteData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const { signup } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (token) {
      validateInvite();
    } else {
      setError('No invite token provided');
      setLoading(false);
    }
  }, [token]);

  const validateInvite = async () => {
    try {
      const response = await axios.get(`${API}/invites/validate/${token}`);
      if (response.data && response.data.valid !== false) {
        setInviteData(response.data);
        setEmail(response.data.recruit_email || '');
        const fullName = `${response.data.recruit_first_name || ''} ${response.data.recruit_last_name || ''}`.trim();
        setName(fullName || response.data.recruit_name || '');
      } else {
        setError(response.data?.message || 'Invalid invite link');
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Invalid or expired invite link';
      setError(errorMsg);
      toast.error(errorMsg);
    } finally {
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
      await signup(email, password, name, token);
      toast.success('Account created successfully!');
      navigate('/');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Signup failed');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500 mx-auto"></div>
          <p className="text-slate-400 mt-4">Validating invite...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-md"
        >
          <div className="backdrop-blur-sm bg-slate-900/50 rounded-2xl border border-cyan-500/20 shadow-2xl shadow-cyan-500/10 p-8 text-center">
            <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <AlertCircle className="h-8 w-8 text-red-400" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">Invalid Invite</h2>
            <p className="text-slate-400 mb-6">{error}</p>
            <p className="text-slate-500 text-sm mb-6">
              This invite link may have expired or already been used. Please contact your upline for a new invite.
            </p>
            <Link to="/login">
              <Button className="bg-cyan-500 hover:bg-cyan-600 text-white">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Go to Login
              </Button>
            </Link>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-8 bg-slate-50 dark:bg-slate-900">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-md"
      >
        <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-xl border border-slate-200 dark:border-slate-800 p-8">
          <div className="text-center mb-8">
            <div className="inline-flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 mb-4">
              <span className="text-2xl font-bold text-primary">B</span>
            </div>
            <h2 className="text-3xl font-bold text-slate-900 dark:text-slate-100" data-testid="signup-title">Join Atlas</h2>
            <p className="text-slate-600 dark:text-slate-400 mt-2">
              Invited by <span className="font-medium text-primary">{inviteData?.inviter_name}</span>
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6" data-testid="signup-form">
            <div className="space-y-2">
              <Label htmlFor="name">Full Name</Label>
              <Input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                data-testid="name-input"
                className="bg-slate-50 dark:bg-slate-900 border-transparent focus:bg-white dark:bg-slate-900 focus:border-primary focus:ring-2 focus:ring-primary/20"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                disabled
                data-testid="email-input"
                className="bg-slate-100 dark:bg-slate-800"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="npn">National Producer Number (NPN)</Label>
              <Input
                id="npn"
                type="text"
                value={inviteData?.recruit_npn || ''}
                disabled
                data-testid="npn-input"
                className="bg-slate-100 dark:bg-slate-800 font-mono"
              />
              <p className="text-xs text-slate-500 dark:text-slate-400">Pre-assigned to ensure uniqueness</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Minimum 8 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                data-testid="password-input"
                className="bg-slate-50 dark:bg-slate-900 border-transparent focus:bg-white dark:bg-slate-900 focus:border-primary focus:ring-2 focus:ring-primary/20"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm Password</Label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="Re-enter password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                data-testid="confirm-password-input"
                className="bg-slate-50 dark:bg-slate-900 border-transparent focus:bg-white dark:bg-slate-900 focus:border-primary focus:ring-2 focus:ring-primary/20"
              />
            </div>

            <Button
              type="submit"
              className="w-full rounded-full h-11 text-base font-medium"
              disabled={submitting}
              data-testid="signup-button"
            >
              {submitting ? 'Creating Account...' : 'Create Account'}
            </Button>
          </form>
        </div>
      </motion.div>
    </div>
  );
}
