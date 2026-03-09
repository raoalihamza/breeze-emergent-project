import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Shield, Calendar, User, Activity, ChevronRight, FileText } from 'lucide-react';
import { toast } from 'sonner';
import { motion } from 'framer-motion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const ACTION_LABELS = {
  'hierarchy_change': 'Hierarchy Change',
  'status_change': 'Status Change',
  'commission_change': 'Commission Change',
  'role_change': 'Role Change'
};

const ACTION_COLORS = {
  'hierarchy_change': 'blue',
  'status_change': 'emerald',
  'commission_change': 'violet',
  'role_change': 'amber'
};

export default function AuditLog() {
  const { getAuthHeader } = useAuth();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchAuditLogs();
  }, [filter]);

  const fetchAuditLogs = async () => {
    try {
      const url = filter === 'all' 
        ? `${API}/admin/audit-logs` 
        : `${API}/admin/audit-logs?action=${filter}`;
      const response = await axios.get(url, getAuthHeader());
      setLogs(response.data);
    } catch (error) {
      toast.error('Failed to load audit logs');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderDetails = (action, details) => {
    switch (action) {
      case 'hierarchy_change':
        return (
          <div className="text-xs text-slate-500 dark:text-slate-400 space-y-0.5">
            <div>From: {details.old_upline_name || 'None'} → To: {details.new_upline_name || 'None'}</div>
          </div>
        );
      case 'status_change':
        return (
          <div className="text-xs text-slate-500 dark:text-slate-400">
            {details.old_status} → {details.new_status}
          </div>
        );
      case 'commission_change':
        return (
          <div className="text-xs text-slate-500 dark:text-slate-400">
            {details.old_commission}% → {details.new_commission}%
          </div>
        );
      case 'role_change':
        return (
          <div className="text-xs text-slate-500 dark:text-slate-400">
            {details.old_role} → {details.new_role}
          </div>
        );
      default:
        return null;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-2 border-cyan-500 border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-5" data-testid="audit-log-page">
      {/* Header */}
      <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="flex items-center gap-3">
        <div className="h-8 w-1 bg-gradient-to-b from-cyan-500 to-blue-500 rounded-full"></div>
        <div>
          <h1 className="text-xl font-bold text-slate-900 dark:text-white">Audit Log</h1>
          <p className="text-xs text-slate-500 dark:text-slate-400">Track all administrative actions</p>
        </div>
      </motion.div>

      {/* Filter Tabs */}
      <div className="flex gap-2 flex-wrap">
        {['all', 'hierarchy_change', 'status_change', 'commission_change', 'role_change'].map((actionType) => (
          <button
            key={actionType}
            onClick={() => setFilter(actionType)}
            className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-all ${
              filter === actionType
                ? 'bg-cyan-500 text-white shadow-md'
                : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700'
            }`}
            data-testid={`filter-${actionType}`}
          >
            {actionType === 'all' ? 'All' : ACTION_LABELS[actionType]}
          </button>
        ))}
      </div>

      {/* Logs */}
      <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
        <CardContent className="p-0">
          {logs.length > 0 ? (
            <div className="divide-y divide-slate-100 dark:divide-slate-800">
              {logs.map((log, index) => {
                const color = ACTION_COLORS[log.action] || 'slate';
                return (
                  <motion.div
                    key={log.id || index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.03 }}
                    className="p-4 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
                    data-testid={`audit-log-${index}`}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`p-2 rounded-lg bg-${color}-50 dark:bg-${color}-950/30 flex-shrink-0`}>
                        <Activity className={`h-4 w-4 text-${color}-600 dark:text-${color}-400`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`text-xs px-2 py-0.5 rounded-full bg-${color}-100 dark:bg-${color}-900/30 text-${color}-700 dark:text-${color}-400 font-medium`}>
                            {ACTION_LABELS[log.action]}
                          </span>
                          <span className="text-xs text-slate-400">•</span>
                          <span className="text-xs text-slate-500 dark:text-slate-400">{formatDate(log.created_at)}</span>
                        </div>
                        <div className="text-sm font-medium text-slate-900 dark:text-white mb-1">
                          {log.target_user_name}
                        </div>
                        {renderDetails(log.action, log.details)}
                        <div className="text-xs text-slate-400 mt-1.5 flex items-center gap-1">
                          <User className="h-3 w-3" />
                          <span>by {log.admin_name}</span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          ) : (
            <div className="py-16 text-center">
              <FileText className="h-12 w-12 mx-auto text-slate-300 dark:text-slate-600 mb-3" />
              <p className="text-slate-500 dark:text-slate-400 text-sm">No audit logs found</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
