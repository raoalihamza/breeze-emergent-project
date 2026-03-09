import { useState, useEffect } from 'react';
import { useClientAuth } from './ClientPortalLayout';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { motion } from 'framer-motion';
import { FileText, Shield, DollarSign, Calendar, Building2 } from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function ClientPolicies() {
  const { client, getAuthHeader } = useClientAuth();
  const [policies, setPolicies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPolicies();
  }, []);

  const fetchPolicies = async () => {
    try {
      const response = await axios.get(`${API}/portal/my-policies`, getAuthHeader());
      setPolicies(response.data);
    } catch (error) {
      console.error('Failed to load policies:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    if (!amount) return '-';
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(amount);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="h-8 w-8 border-3 border-cyan-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-3">
          <div className="h-8 w-1 bg-gradient-to-b from-cyan-500 to-blue-500 rounded-full" />
          <div>
            <h1 className="text-xl font-bold text-slate-900 dark:text-white">My Policies</h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">Your insurance protection overview</p>
          </div>
        </div>
      </motion.div>

      {policies.length === 0 ? (
        <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm">
          <CardContent className="py-16 text-center">
            <FileText className="h-12 w-12 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">No Policies Yet</h3>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Your advisor will add your policy information here once available.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {policies.map((policy, index) => (
            <motion.div
              key={policy.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-blue-500/5" />
                <CardContent className="p-6 relative">
                  <div className="flex flex-col md:flex-row md:items-start gap-4">
                    {/* Policy Icon */}
                    <div className="flex-shrink-0">
                      <div className="h-14 w-14 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                        <Shield className="h-7 w-7 text-white" />
                      </div>
                    </div>

                    {/* Policy Details */}
                    <div className="flex-1 min-w-0">
                      <div className="flex flex-wrap items-center gap-2 mb-2">
                        <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                          {policy.carrier}
                        </h3>
                        <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                          policy.status === 'active' 
                            ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
                            : policy.status === 'pending'
                            ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
                            : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                        }`}>
                          {policy.status.charAt(0).toUpperCase() + policy.status.slice(1)}
                        </span>
                      </div>
                      
                      <p className="text-sm font-medium text-cyan-600 dark:text-cyan-400 mb-3">
                        {policy.product_type}
                      </p>

                      {/* Policy Info Grid */}
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
                        {policy.face_amount && (
                          <div>
                            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1 flex items-center gap-1">
                              <Shield className="h-3 w-3" />
                              Face Amount
                            </p>
                            <p className="text-sm font-semibold text-slate-900 dark:text-white">
                              {formatCurrency(policy.face_amount)}
                            </p>
                          </div>
                        )}
                        
                        {policy.premium && (
                          <div>
                            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1 flex items-center gap-1">
                              <DollarSign className="h-3 w-3" />
                              Annual Premium
                            </p>
                            <p className="text-sm font-semibold text-emerald-600 dark:text-emerald-400">
                              {formatCurrency(policy.premium)}
                            </p>
                          </div>
                        )}
                        
                        {policy.issue_date && (
                          <div>
                            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1 flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              Issue Date
                            </p>
                            <p className="text-sm font-semibold text-slate-900 dark:text-white">
                              {formatDate(policy.issue_date)}
                            </p>
                          </div>
                        )}
                        
                        {policy.policy_number && (
                          <div>
                            <p className="text-xs text-slate-500 dark:text-slate-400 mb-1 flex items-center gap-1">
                              <FileText className="h-3 w-3" />
                              Policy #
                            </p>
                            <p className="text-sm font-semibold text-slate-900 dark:text-white">
                              {policy.policy_number}
                            </p>
                          </div>
                        )}
                      </div>

                      {/* Why This Policy Exists */}
                      {policy.short_explanation && (
                        <div className="p-4 rounded-xl bg-gradient-to-r from-cyan-50 to-blue-50 dark:from-cyan-950/30 dark:to-blue-950/30 border border-cyan-100 dark:border-cyan-900/30">
                          <p className="text-xs font-medium text-cyan-700 dark:text-cyan-400 mb-1">
                            Why This Policy Exists
                          </p>
                          <p className="text-sm text-slate-700 dark:text-slate-300">
                            {policy.short_explanation}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}

      {/* Disclaimer */}
      <div className="text-center py-4">
        <p className="text-xs text-slate-400 dark:text-slate-500 max-w-lg mx-auto">
          Policy information is provided for reference only. For detailed coverage information, 
          riders, or policy changes, please contact your advisor directly.
        </p>
      </div>
    </div>
  );
}
