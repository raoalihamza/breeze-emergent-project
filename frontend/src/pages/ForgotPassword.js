import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { toast } from 'sonner';
import { motion } from 'framer-motion';
import { Mail, ArrowLeft, CheckCircle } from 'lucide-react';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      await axios.post(`${API}/api/auth/forgot-password`, { email });
      setSubmitted(true);
      toast.success('Password reset email sent');
    } catch (error) {
      if (error.response?.status === 429) {
        toast.error('Too many requests. Please try again later.');
      } else {
        // Show success even on error to prevent email enumeration
        setSubmitted(true);
        toast.success('Password reset email sent');
      }
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
          {!submitted ? (
            <>
              <div className="mb-8 text-center">
                <div className="w-16 h-16 bg-cyan-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Mail className="h-8 w-8 text-cyan-400" />
                </div>
                <h2 className="text-2xl font-bold text-white mb-2">Forgot Password?</h2>
                <p className="text-slate-400">Enter your email and we'll send you a reset link</p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <Label htmlFor="email" className="text-slate-300 font-medium">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    placeholder="agent@breezefg.com"
                    className="mt-2 bg-slate-800/80 border-cyan-500/30 text-white focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20"
                    data-testid="forgot-password-email"
                  />
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white rounded-xl py-6 text-lg font-bold shadow-lg shadow-cyan-500/30 hover:shadow-cyan-500/50 transition-all"
                  data-testid="forgot-password-submit"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Sending...
                    </span>
                  ) : (
                    'Send Reset Link'
                  )}
                </Button>
              </form>
            </>
          ) : (
            <div className="text-center">
              <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="h-8 w-8 text-green-400" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Check Your Email</h2>
              <p className="text-slate-400 mb-6">
                If an account exists with <span className="text-cyan-400">{email}</span>, 
                you'll receive a password reset link shortly.
              </p>
              <p className="text-slate-500 text-sm">
                Didn't receive the email? Check your spam folder or try again.
              </p>
            </div>
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
