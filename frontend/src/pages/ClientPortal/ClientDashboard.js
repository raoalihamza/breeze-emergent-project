import { useClientAuth } from './ClientPortalLayout';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { motion } from 'framer-motion';
import { 
  User, Mail, Phone, FileText, FolderOpen, Calendar, Shield,
  TrendingUp, DollarSign, Clock, ChevronRight, Download, Hash
} from 'lucide-react';
import { Link } from 'react-router-dom';

export default function ClientDashboard() {
  const { client, dashboardData } = useClientAuth();
  
  if (!dashboardData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="h-8 w-8 border-3 border-cyan-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const { advisor, policies, documents, important_dates, settings } = dashboardData;

  const formatCurrency = (amount) => {
    if (!amount) return '-';
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(amount);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  // Calculate monthly premium (use monthly_premium if available, else divide annual by 12)
  const totalMonthlyPremium = policies.reduce((sum, p) => {
    if (p.monthly_premium) return sum + p.monthly_premium;
    if (p.premium) return sum + (p.premium / 12);
    return sum;
  }, 0);
  const totalFaceAmount = policies.reduce((sum, p) => sum + (p.face_amount || 0), 0);
  const activePolicies = policies.filter(p => p.status === 'active').length;

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <motion.div 
        initial={{ opacity: 0, y: -10 }} 
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-center justify-between gap-4"
      >
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Welcome, {client?.first_name}
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            Your financial snapshot, powered by Breeze
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-400 dark:text-slate-500">
          <Clock className="h-3.5 w-3.5" />
          <span>Last updated: {new Date().toLocaleDateString()}</span>
        </div>
      </motion.div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm">
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Policies</span>
                <div className="p-1.5 rounded-lg bg-cyan-50 dark:bg-cyan-950/30">
                  <FileText className="h-3.5 w-3.5 text-cyan-600 dark:text-cyan-400" />
                </div>
              </div>
              <div className="text-2xl font-bold text-slate-900 dark:text-white">{activePolicies}</div>
              <p className="text-xs text-slate-400 mt-0.5">Active</p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
          <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm">
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Coverage</span>
                <div className="p-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/30">
                  <Shield className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" />
                </div>
              </div>
              <div className="text-2xl font-bold text-slate-900 dark:text-white">{formatCurrency(totalFaceAmount)}</div>
              <p className="text-xs text-slate-400 mt-0.5">Total Face Amount</p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm">
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Premium</span>
                <div className="p-1.5 rounded-lg bg-violet-50 dark:bg-violet-950/30">
                  <DollarSign className="h-3.5 w-3.5 text-violet-600 dark:text-violet-400" />
                </div>
              </div>
              <div className="text-2xl font-bold text-slate-900 dark:text-white">{formatCurrency(totalMonthlyPremium)}</div>
              <p className="text-xs text-slate-400 mt-0.5">Monthly Total</p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
          <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm">
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Documents</span>
                <div className="p-1.5 rounded-lg bg-amber-50 dark:bg-amber-950/30">
                  <FolderOpen className="h-3.5 w-3.5 text-amber-600 dark:text-amber-400" />
                </div>
              </div>
              <div className="text-2xl font-bold text-slate-900 dark:text-white">{documents.length}</div>
              <p className="text-xs text-slate-400 mt-0.5">Available</p>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left Column - Advisor & Policies */}
        <div className="lg:col-span-2 space-y-6">
          {/* My Advisor */}
          {advisor && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
              <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-blue-500/5" />
                <CardHeader className="pb-3 relative">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <User className="h-5 w-5 text-cyan-600 dark:text-cyan-400" />
                    My Advisor
                  </CardTitle>
                </CardHeader>
                <CardContent className="relative">
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0">
                      {advisor.profile_picture ? (
                        <img 
                          src={advisor.profile_picture} 
                          alt={advisor.name} 
                          className="h-16 w-16 rounded-xl object-cover ring-2 ring-cyan-500/20"
                        />
                      ) : (
                        <div className="h-16 w-16 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                          <User className="h-8 w-8 text-white" />
                        </div>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{advisor.name}</h3>
                      <p className="text-sm text-cyan-600 dark:text-cyan-400 font-medium">Life Insurance Advisor</p>
                      {advisor.npn && (
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 flex items-center gap-1">
                          <Hash className="h-3 w-3" />
                          NPN: {advisor.npn}
                        </p>
                      )}
                      <div className="mt-3 flex flex-wrap gap-3">
                        {advisor.email && (
                          <a href={`mailto:${advisor.email}`} className="flex items-center gap-1.5 text-xs text-slate-600 dark:text-slate-400 hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors">
                            <Mail className="h-3.5 w-3.5" />
                            {advisor.email}
                          </a>
                        )}
                        {advisor.phone && (
                          <a href={`tel:${advisor.phone}`} className="flex items-center gap-1.5 text-xs text-slate-600 dark:text-slate-400 hover:text-cyan-600 dark:hover:text-cyan-400 transition-colors">
                            <Phone className="h-3.5 w-3.5" />
                            {advisor.phone}
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* My Policies */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
            <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <FileText className="h-5 w-5 text-cyan-600 dark:text-cyan-400" />
                    My Policies
                  </CardTitle>
                  <Link to="/client-portal/policies">
                    <Button variant="ghost" size="sm" className="text-xs text-cyan-600 dark:text-cyan-400">
                      View All <ChevronRight className="h-3.5 w-3.5 ml-1" />
                    </Button>
                  </Link>
                </div>
              </CardHeader>
              <CardContent>
                {policies.length === 0 ? (
                  <div className="text-center py-8">
                    <FileText className="h-10 w-10 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
                    <p className="text-sm text-slate-500 dark:text-slate-400">No policies yet</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {policies.slice(0, 3).map((policy, index) => (
                      <div 
                        key={policy.id} 
                        className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700/50"
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className="font-semibold text-slate-900 dark:text-white">{policy.carrier}</h4>
                              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                                policy.status === 'active' 
                                  ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
                                  : policy.status === 'pending'
                                  ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
                                  : 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300'
                              }`}>
                                {policy.status}
                              </span>
                            </div>
                            <p className="text-sm text-slate-600 dark:text-slate-400">{policy.product_type}</p>
                            {policy.short_explanation && (
                              <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 italic">
                                "{policy.short_explanation}"
                              </p>
                            )}
                          </div>
                          <div className="text-right flex-shrink-0">
                            {policy.premium && (
                              <div className="text-sm font-semibold text-emerald-600 dark:text-emerald-400">
                                {formatCurrency(policy.premium)}/yr
                              </div>
                            )}
                            {policy.face_amount && (
                              <div className="text-xs text-slate-500 dark:text-slate-400">
                                {formatCurrency(policy.face_amount)} coverage
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Right Column - Important Dates & Recent Documents */}
        <div className="space-y-6">
          {/* Important Dates */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
            <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Calendar className="h-5 w-5 text-cyan-600 dark:text-cyan-400" />
                  Important Dates
                </CardTitle>
              </CardHeader>
              <CardContent>
                {important_dates.length === 0 ? (
                  <div className="text-center py-6">
                    <Calendar className="h-8 w-8 text-slate-300 dark:text-slate-600 mx-auto mb-2" />
                    <p className="text-xs text-slate-500 dark:text-slate-400">No upcoming dates</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {important_dates.map((date, index) => {
                      const isAnnualReview = date.type === 'annual_review';
                      return (
                        <div 
                          key={index} 
                          className={`flex items-center gap-3 p-3 rounded-lg ${
                            isAnnualReview 
                              ? 'bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-950/30 dark:to-orange-950/30 border border-amber-200 dark:border-amber-900/30' 
                              : 'bg-slate-50 dark:bg-slate-800/50'
                          }`}
                        >
                          <div className={`h-10 w-10 rounded-lg flex flex-col items-center justify-center ${
                            isAnnualReview 
                              ? 'bg-gradient-to-br from-amber-500/20 to-orange-500/20' 
                              : 'bg-gradient-to-br from-cyan-500/10 to-blue-500/10'
                          }`}>
                            <span className={`text-[10px] uppercase font-medium ${
                              isAnnualReview ? 'text-amber-600 dark:text-amber-400' : 'text-cyan-600 dark:text-cyan-400'
                            }`}>
                              {new Date(date.date).toLocaleDateString('en-US', { month: 'short' })}
                            </span>
                            <span className="text-sm font-bold text-slate-900 dark:text-white">
                              {new Date(date.date).getDate()}
                            </span>
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className={`text-sm font-medium truncate ${
                              isAnnualReview ? 'text-amber-700 dark:text-amber-400' : 'text-slate-900 dark:text-white'
                            }`}>
                              {date.description}
                            </p>
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                              {isAnnualReview ? 'Scheduled Review' : date.type === 'anniversary' ? 'Policy Anniversary' : date.type}
                            </p>
                          </div>
                          {isAnnualReview && (
                            <span className="text-xs px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400 font-medium">
                              Important
                            </span>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}

                {/* Annual Review Reminder - only show if no annual_review date in important_dates */}
                {!important_dates.some(d => d.type === 'annual_review') && (
                  <div className="mt-4 p-3 rounded-lg bg-gradient-to-r from-cyan-50 to-blue-50 dark:from-cyan-950/30 dark:to-blue-950/30 border border-cyan-100 dark:border-cyan-900/30">
                    <p className="text-xs text-cyan-700 dark:text-cyan-400 font-medium">
                      Annual Review Recommended
                    </p>
                    <p className="text-xs text-cyan-600/80 dark:text-cyan-500/80 mt-1">
                      Contact your advisor to schedule your annual policy review.
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>

          {/* Recent Documents */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.45 }}>
            <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <FolderOpen className="h-5 w-5 text-cyan-600 dark:text-cyan-400" />
                    Recent Documents
                  </CardTitle>
                  <Link to="/client-portal/documents">
                    <Button variant="ghost" size="sm" className="text-xs text-cyan-600 dark:text-cyan-400">
                      View All <ChevronRight className="h-3.5 w-3.5 ml-1" />
                    </Button>
                  </Link>
                </div>
              </CardHeader>
              <CardContent>
                {documents.length === 0 ? (
                  <div className="text-center py-6">
                    <FolderOpen className="h-8 w-8 text-slate-300 dark:text-slate-600 mx-auto mb-2" />
                    <p className="text-xs text-slate-500 dark:text-slate-400">No documents yet</p>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {documents.slice(0, 4).map((doc) => (
                      <div 
                        key={doc.id} 
                        className="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors group"
                      >
                        <div className="h-8 w-8 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
                          <FileText className="h-4 w-4 text-slate-500 dark:text-slate-400" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-slate-900 dark:text-white truncate">
                            {doc.file_name}
                          </p>
                          <p className="text-xs text-slate-500 dark:text-slate-400">
                            {formatDate(doc.created_at)}
                          </p>
                        </div>
                        <Download className="h-4 w-4 text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
