import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { TrendingUp, Users, FileText, Target, Activity, Zap, ArrowUpRight, Trophy } from 'lucide-react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function Dashboard() {
  const { user, getAuthHeader } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [leaderboard, setLeaderboard] = useState([]);
  const [productionData, setProductionData] = useState([]);
  const [teamGrowthData, setTeamGrowthData] = useState([]);
  const [productionDays, setProductionDays] = useState(7);
  const [teamDays, setTeamDays] = useState(7);
  const [chartsLoading, setChartsLoading] = useState(true);

  useEffect(() => {
    fetchStats();
    fetchLeaderboard();
  }, []);

  useEffect(() => {
    fetchProductionTrend();
  }, [productionDays]);

  useEffect(() => {
    fetchTeamGrowth();
  }, [teamDays]);

  const fetchStats = async () => {
    try {
      const [productionRes, teamRes] = await Promise.all([
        axios.get(`${API}/production/stats`, getAuthHeader()),
        axios.get(`${API}/hierarchy/downline`, getAuthHeader())
      ]);
      setStats({
        production: productionRes.data,
        teamSize: teamRes.data.length
      });
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchLeaderboard = async () => {
    try {
      const res = await axios.get(`${API}/leaderboard/top-producers`, getAuthHeader());
      setLeaderboard(res.data || []);
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error);
      setLeaderboard([]);
    }
  };

  const fetchProductionTrend = async () => {
    try {
      const res = await axios.get(`${API}/charts/production-trend?days=${productionDays}`, getAuthHeader());
      setProductionData(res.data);
    } catch (error) {
      console.error('Failed to fetch production trend:', error);
    }
  };

  const fetchTeamGrowth = async () => {
    try {
      const res = await axios.get(`${API}/charts/team-growth?days=${teamDays}`, getAuthHeader());
      setTeamGrowthData(res.data);
    } catch (error) {
      console.error('Failed to fetch team growth:', error);
    } finally {
      setChartsLoading(false);
    }
  };

  const statCards = [
    {
      title: 'Submitted AP',
      value: `$${stats?.production.total_submitted_ap.toLocaleString() || 0}`,
      icon: Target,
      color: 'cyan'
    },
    {
      title: 'Issued AP',
      value: `$${stats?.production.total_issued_ap.toLocaleString() || 0}`,
      icon: TrendingUp,
      color: 'emerald'
    },
    {
      title: 'Policies',
      value: stats?.production.total_policies || 0,
      icon: FileText,
      color: 'violet'
    },
    {
      title: 'Team Size',
      value: stats?.teamSize || 0,
      icon: Users,
      color: 'amber'
    }
  ];

  const quickActions = [
    {
      title: 'View My Team',
      description: 'Hierarchy & performance',
      icon: Users,
      href: '/team',
      color: 'cyan',
      testId: 'quick-action-team'
    },
    {
      title: 'Invite Recruits',
      description: 'Generate invite links',
      icon: Target,
      href: '/recruiting',
      color: 'violet',
      testId: 'quick-action-recruiting'
    },
    {
      title: 'Resources',
      description: 'Scripts & training',
      icon: FileText,
      href: '/resources',
      color: 'emerald',
      testId: 'quick-action-resources'
    }
  ];

  const getColorClasses = (color) => {
    const colors = {
      cyan: {
        bg: 'bg-cyan-50 dark:bg-cyan-950/30',
        icon: 'text-cyan-600 dark:text-cyan-400',
        border: 'border-cyan-200 dark:border-cyan-800/50',
        gradient: 'from-cyan-500 to-blue-500'
      },
      emerald: {
        bg: 'bg-emerald-50 dark:bg-emerald-950/30',
        icon: 'text-emerald-600 dark:text-emerald-400',
        border: 'border-emerald-200 dark:border-emerald-800/50',
        gradient: 'from-emerald-500 to-green-500'
      },
      violet: {
        bg: 'bg-violet-50 dark:bg-violet-950/30',
        icon: 'text-violet-600 dark:text-violet-400',
        border: 'border-violet-200 dark:border-violet-800/50',
        gradient: 'from-violet-500 to-purple-500'
      },
      amber: {
        bg: 'bg-amber-50 dark:bg-amber-950/30',
        icon: 'text-amber-600 dark:text-amber-400',
        border: 'border-amber-200 dark:border-amber-800/50',
        gradient: 'from-amber-500 to-orange-500'
      }
    };
    return colors[color];
  };

  const TimeToggle = ({ value, onChange, testId }) => (
    <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-0.5" data-testid={testId}>
      <button
        onClick={() => onChange(7)}
        className={`px-2.5 py-1 text-xs font-medium rounded-md transition-all ${
          value === 7
            ? 'bg-white dark:bg-slate-700 text-cyan-600 dark:text-cyan-400 shadow-sm'
            : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'
        }`}
      >
        7D
      </button>
      <button
        onClick={() => onChange(30)}
        className={`px-2.5 py-1 text-xs font-medium rounded-md transition-all ${
          value === 30
            ? 'bg-white dark:bg-slate-700 text-cyan-600 dark:text-cyan-400 shadow-sm'
            : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'
        }`}
      >
        30D
      </button>
    </div>
  );

  const CustomTooltip = ({ active, payload, label, formatter }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg px-3 py-2">
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">{label}</p>
          <p className="text-sm font-semibold text-slate-900 dark:text-white">
            {formatter ? formatter(payload[0].value) : payload[0].value}
          </p>
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="relative">
          <div className="animate-spin rounded-full h-10 w-10 border-2 border-cyan-500 border-t-transparent"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-5" data-testid="dashboard">
      {/* Compact Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div className="flex items-center gap-3">
          <div className="h-8 w-1 bg-gradient-to-b from-cyan-500 to-blue-500 rounded-full"></div>
          <div>
            <h1 className="text-xl font-bold text-slate-900 dark:text-white">
              Welcome back, {user?.name}
            </h1>
            <div className="flex items-center gap-1.5 mt-0.5">
              <Activity className="h-3 w-3 text-cyan-500" />
              <span className="text-xs text-slate-500 dark:text-slate-400">
                System Status: <span className="text-cyan-500 font-medium">Active</span>
              </span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Compact Stat Cards - 4 columns */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {statCards.map((stat, index) => {
          const Icon = stat.icon;
          const colors = getColorClasses(stat.color);
          return (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Card 
                className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50 hover:shadow-md transition-shadow duration-200" 
                data-testid={`stat-card-${index}`}
              >
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                      {stat.title}
                    </span>
                    <div className={`p-1.5 rounded-lg ${colors.bg}`}>
                      <Icon className={`h-3.5 w-3.5 ${colors.icon}`} strokeWidth={2} />
                    </div>
                  </div>
                  <div className="text-2xl font-bold text-slate-900 dark:text-white">
                    {stat.value}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>

      {/* Company-Wide Leaderboard */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
          <CardHeader className="pb-3 pt-5 px-5">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 shadow-lg">
                <Trophy className="h-5 w-5 text-white" />
              </div>
              <div>
                <CardTitle className="text-xl font-bold text-slate-900 dark:text-white">
                  Top Producers Leaderboard
                </CardTitle>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                  Company-wide rankings by submitted AP
                </p>
              </div>
            </div>
          </CardHeader>
          
          <CardContent className="px-5 pb-5">
            {loading ? (
              <div className="py-12 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500 mx-auto"></div>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-3">Loading leaderboard...</p>
              </div>
            ) : leaderboard && leaderboard.length > 0 ? (
              <div className="space-y-2">
                {leaderboard.map((agent, index) => {
                  const isTop3 = index < 3;
                  const rankColors = {
                    0: { bg: 'bg-gradient-to-r from-amber-50 to-yellow-50 dark:from-amber-950/30 dark:to-yellow-950/30', border: 'border-amber-300 dark:border-amber-700', rank: 'bg-gradient-to-br from-amber-400 to-yellow-500 text-white', icon: '🥇' },
                    1: { bg: 'bg-gradient-to-r from-slate-50 to-gray-50 dark:from-slate-800/30 dark:to-gray-800/30', border: 'border-slate-300 dark:border-slate-600', rank: 'bg-gradient-to-br from-slate-300 to-gray-400 text-slate-800', icon: '🥈' },
                    2: { bg: 'bg-gradient-to-r from-orange-50 to-amber-50 dark:from-orange-950/30 dark:to-amber-950/30', border: 'border-orange-300 dark:border-orange-700', rank: 'bg-gradient-to-br from-orange-400 to-amber-500 text-white', icon: '🥉' }
                  };
                  const colors = isTop3 ? rankColors[index] : { bg: 'bg-white dark:bg-slate-900/50', border: 'border-slate-200 dark:border-slate-700', rank: 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400' };
                  
                  return (
                    <motion.div
                      key={agent.agent_id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className={`relative p-4 rounded-xl border-2 ${colors.border} ${colors.bg} ${isTop3 ? 'shadow-md hover:shadow-lg' : 'hover:shadow-sm'} transition-all duration-200`}
                    >
                      {/* Top 3 Badge */}
                      {isTop3 && (
                        <div className="absolute -top-2 -right-2 text-2xl animate-bounce">
                          {colors.icon}
                        </div>
                      )}
                      
                      <div className="flex items-center gap-4">
                        {/* Rank */}
                        <div className={`flex-shrink-0 w-10 h-10 rounded-xl ${colors.rank} flex items-center justify-center font-bold ${isTop3 ? 'text-lg shadow-lg' : 'text-sm'}`}>
                          {index + 1}
                        </div>
                        
                        {/* Agent Info */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className={`font-bold ${isTop3 ? 'text-base' : 'text-sm'} text-slate-900 dark:text-white truncate`}>
                              {agent.agent_name}
                            </h3>
                            {isTop3 && (
                              <span className="text-xs px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 font-medium">
                                Top {index + 1}
                              </span>
                            )}
                          </div>
                          <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
                            <span className="flex items-center gap-1">
                              <Users className="h-3 w-3" />
                              <span className="font-medium">Upline:</span> {agent.upline_name || 'N/A'}
                            </span>
                          </div>
                        </div>
                        
                        {/* Stats */}
                        <div className="flex items-center gap-4">
                          {/* Submitted AP */}
                          <div className="text-right">
                            <div className="text-xs text-slate-500 dark:text-slate-400 mb-0.5">Submitted AP</div>
                            <div className={`font-bold ${isTop3 ? 'text-lg' : 'text-base'} text-emerald-600 dark:text-emerald-400`}>
                              ${agent.submitted_ap?.toLocaleString() || '0'}
                            </div>
                          </div>
                          
                          {/* Policies */}
                          <div className="text-right">
                            <div className="text-xs text-slate-500 dark:text-slate-400 mb-0.5">Policies</div>
                            <div className={`font-bold ${isTop3 ? 'text-lg' : 'text-base'} text-cyan-600 dark:text-cyan-400`}>
                              {agent.policy_count || 0}
                            </div>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            ) : (
              <div className="py-12 text-center">
                <Trophy className="h-12 w-12 mx-auto text-slate-300 dark:text-slate-600 mb-3" />
                <p className="text-slate-500 dark:text-slate-400 text-sm">No production data available</p>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
