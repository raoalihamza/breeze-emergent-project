import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { TrendingUp, DollarSign, FileText, Users, Calendar, ChevronDown, Target, Award } from 'lucide-react';
import { toast } from 'sonner';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { format, subDays, startOfMonth, endOfMonth } from 'date-fns';
import DirectLegChart from '../components/DirectLegChart';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function Production() {
  const { user, getAuthHeader } = useAuth();
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('personal');
  const [dateRange, setDateRange] = useState('month');
  
  const [startDate, setStartDate] = useState(format(startOfMonth(new Date()), 'yyyy-MM-dd'));
  const [endDate, setEndDate] = useState(format(endOfMonth(new Date()), 'yyyy-MM-dd'));
  
  const [personalData, setPersonalData] = useState(null);
  const [teamData, setTeamData] = useState(null);
  const [directLegsData, setDirectLegsData] = useState(null);

  useEffect(() => {
    fetchData();
  }, [startDate, endDate, activeTab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'personal') {
        const response = await axios.get(`${API}/production/personal`, {
          ...getAuthHeader(),
          params: { start_date: startDate, end_date: endDate }
        });
        setPersonalData(response.data);
      } else {
        const [teamResponse, legsResponse] = await Promise.all([
          axios.get(`${API}/production/team`, {
            ...getAuthHeader(),
            params: { start_date: startDate, end_date: endDate }
          }),
          axios.get(`${API}/production/direct-legs`, {
            ...getAuthHeader(),
            params: { start_date: startDate, end_date: endDate }
          })
        ]);
        setTeamData(teamResponse.data);
        setDirectLegsData(legsResponse.data);
      }
    } catch (error) {
      toast.error('Failed to load production data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleDrillDown = async (legId, start, end) => {
    try {
      const response = await axios.get(`${API}/production/leg-breakdown/${legId}`, {
        ...getAuthHeader(),
        params: { start_date: start, end_date: end }
      });
      return response.data;
    } catch (error) {
      toast.error('Failed to load leg breakdown');
      console.error(error);
      return null;
    }
  };

  const prepareChartData = (clients) => {
    if (!clients || clients.length === 0) return [];
    
    const dataMap = {};
    
    clients.forEach(client => {
      const date = client.date_issued || client.date_submitted || client.created_at?.split('T')[0];
      if (!date) return;
      
      if (!dataMap[date]) {
        dataMap[date] = { date, submitted: 0, issued: 0 };
      }
      
      const premium = client.premium || client.annual_premium || 0;
      
      if (client.status === 'Issued') {
        dataMap[date].issued += premium;
      }
      if (client.status in ['Pending Approval/Issue', 'Issued', 'Missed Payment']) {
        dataMap[date].submitted += premium;
      }
    });
    
    return Object.values(dataMap).sort((a, b) => new Date(a.date) - new Date(b.date));
  };

  const getQuickDateRange = (range) => {
    const today = new Date();
    let start, end;
    
    switch (range) {
      case 'today':
        start = end = format(today, 'yyyy-MM-dd');
        break;
      case 'week':
        start = format(subDays(today, 7), 'yyyy-MM-dd');
        end = format(today, 'yyyy-MM-dd');
        break;
      case 'month':
        start = format(startOfMonth(today), 'yyyy-MM-dd');
        end = format(endOfMonth(today), 'yyyy-MM-dd');
        break;
      case 'quarter':
        start = format(subDays(today, 90), 'yyyy-MM-dd');
        end = format(today, 'yyyy-MM-dd');
        break;
      case 'year':
        start = format(new Date(today.getFullYear(), 0, 1), 'yyyy-MM-dd');
        end = format(today, 'yyyy-MM-dd');
        break;
      default:
        return;
    }
    
    setDateRange(range);
    setStartDate(start);
    setEndDate(end);
  };

  const currentData = activeTab === 'personal' ? personalData : teamData;

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg px-3 py-2">
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">{label}</p>
          {payload.map((p, i) => (
            <p key={i} className="text-sm font-semibold" style={{ color: p.color }}>
              {p.name}: ${p.value?.toLocaleString()}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-2 border-cyan-500 border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-5" data-testid="production-page">
      {/* Compact Header with Date Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center gap-3"
        >
          <div className="h-8 w-1 bg-gradient-to-b from-cyan-500 to-blue-500 rounded-full"></div>
          <div>
            <h1 className="text-xl font-bold text-slate-900 dark:text-white">Production</h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">Track sales performance</p>
          </div>
        </motion.div>

        {/* Date Range Pills */}
        <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1">
          {['today', 'week', 'month', 'quarter', 'year'].map((range) => (
            <button
              key={range}
              onClick={() => getQuickDateRange(range)}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all capitalize ${
                dateRange === range
                  ? 'bg-white dark:bg-slate-700 text-cyan-600 dark:text-cyan-400 shadow-sm'
                  : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="bg-slate-100 dark:bg-slate-800 p-1 h-auto">
          <TabsTrigger 
            value="personal"
            className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-700 data-[state=active]:text-cyan-600 dark:data-[state=active]:text-cyan-400 data-[state=active]:shadow-sm px-4 py-2 text-sm"
          >
            <DollarSign className="h-4 w-4 mr-1.5" />
            Personal
          </TabsTrigger>
          <TabsTrigger 
            value="team"
            className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-700 data-[state=active]:text-cyan-600 dark:data-[state=active]:text-cyan-400 data-[state=active]:shadow-sm px-4 py-2 text-sm"
          >
            <Users className="h-4 w-4 mr-1.5" />
            Team
          </TabsTrigger>
        </TabsList>

        {/* Personal Production Tab */}
        <TabsContent value="personal" className="space-y-4 mt-4">
          {/* Compact Stats Row */}
          <div className="grid grid-cols-3 gap-3">
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
              <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Submitted</span>
                    <div className="p-1.5 rounded-lg bg-cyan-50 dark:bg-cyan-950/30">
                      <Target className="h-3.5 w-3.5 text-cyan-600 dark:text-cyan-400" />
                    </div>
                  </div>
                  <div className="text-2xl font-bold text-slate-900 dark:text-white">
                    ${currentData?.submitted_ap?.toLocaleString() || 0}
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
              <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Issued</span>
                    <div className="p-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/30">
                      <TrendingUp className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" />
                    </div>
                  </div>
                  <div className="text-2xl font-bold text-slate-900 dark:text-white">
                    ${currentData?.issued_ap?.toLocaleString() || 0}
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
              <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Policies</span>
                    <div className="p-1.5 rounded-lg bg-violet-50 dark:bg-violet-950/30">
                      <FileText className="h-3.5 w-3.5 text-violet-600 dark:text-violet-400" />
                    </div>
                  </div>
                  <div className="text-2xl font-bold text-slate-900 dark:text-white">
                    {currentData?.total_policies || 0}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* Chart */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
            <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
              <CardHeader className="pb-2 pt-4 px-4">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 rounded-lg bg-cyan-50 dark:bg-cyan-950/30">
                    <TrendingUp className="h-3.5 w-3.5 text-cyan-600 dark:text-cyan-400" />
                  </div>
                  <CardTitle className="text-sm font-semibold text-slate-900 dark:text-white">Production Trend</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="px-4 pb-4 pt-2">
                {personalData?.clients && personalData.clients.length > 0 ? (
                  <div className="h-56">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={prepareChartData(personalData.clients)} margin={{ top: 5, right: 5, left: 0, bottom: 5 }}>
                        <defs>
                          <linearGradient id="submittedGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3}/>
                            <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                          </linearGradient>
                          <linearGradient id="issuedGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                            <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" className="dark:stroke-slate-700" />
                        <XAxis 
                          dataKey="date" 
                          tick={{ fontSize: 10, fill: '#94a3b8' }}
                          axisLine={{ stroke: '#e2e8f0' }}
                          tickLine={false}
                          tickFormatter={(value) => format(new Date(value), 'MMM d')}
                        />
                        <YAxis 
                          tick={{ fontSize: 10, fill: '#94a3b8' }}
                          axisLine={false}
                          tickLine={false}
                          tickFormatter={(value) => `$${value >= 1000 ? `${(value/1000).toFixed(0)}k` : value}`}
                          width={45}
                        />
                        <Tooltip content={<CustomTooltip />} />
                        <Area type="monotone" dataKey="submitted" stroke="#06b6d4" strokeWidth={2} fill="url(#submittedGradient)" name="Submitted" />
                        <Area type="monotone" dataKey="issued" stroke="#10b981" strokeWidth={2} fill="url(#issuedGradient)" name="Issued" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <div className="h-56 flex items-center justify-center text-slate-500 dark:text-slate-400 text-sm">
                    No production data for selected period
                  </div>
                )}
                <div className="flex items-center justify-center gap-6 mt-3 text-xs text-slate-500 dark:text-slate-400">
                  <div className="flex items-center gap-1.5">
                    <div className="w-3 h-0.5 bg-cyan-500 rounded"></div>
                    <span>Submitted</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div className="w-3 h-0.5 bg-emerald-500 rounded"></div>
                    <span>Issued</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        {/* Team Production Tab */}
        <TabsContent value="team" className="space-y-4 mt-4">
          {/* Stats Row */}
          <div className="grid grid-cols-3 gap-3">
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
              <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Team Submitted</span>
                    <div className="p-1.5 rounded-lg bg-cyan-50 dark:bg-cyan-950/30">
                      <Target className="h-3.5 w-3.5 text-cyan-600 dark:text-cyan-400" />
                    </div>
                  </div>
                  <div className="text-2xl font-bold text-slate-900 dark:text-white">
                    ${currentData?.submitted_ap?.toLocaleString() || 0}
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
              <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Team Issued</span>
                    <div className="p-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/30">
                      <TrendingUp className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" />
                    </div>
                  </div>
                  <div className="text-2xl font-bold text-slate-900 dark:text-white">
                    ${currentData?.issued_ap?.toLocaleString() || 0}
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
              <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Policies</span>
                    <div className="p-1.5 rounded-lg bg-violet-50 dark:bg-violet-950/30">
                      <FileText className="h-3.5 w-3.5 text-violet-600 dark:text-violet-400" />
                    </div>
                  </div>
                  <div className="text-2xl font-bold text-slate-900 dark:text-white">
                    {currentData?.total_policies || 0}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* Analytics + Chart Grid */}
          <div className="grid lg:grid-cols-5 gap-4">
            {/* Analytics Cards */}
            {teamData?.analytics && (
              <div className="lg:col-span-2 space-y-3">
                <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.15 }}>
                  <Card className="border-slate-200/80 dark:border-slate-800/50 bg-gradient-to-br from-blue-50 to-white dark:from-blue-950/20 dark:to-slate-900/50">
                    <CardContent className="p-4">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900/50">
                          <Users className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                        </div>
                        <div className="flex-1">
                          <p className="text-xs text-slate-500 dark:text-slate-400">Writing Agents</p>
                          <div className="flex items-baseline gap-1">
                            <span className="text-xl font-bold text-slate-900 dark:text-white">{teamData.analytics.writing_agents}</span>
                            <span className="text-sm text-slate-400">/ {teamData.analytics.total_active_agents}</span>
                          </div>
                        </div>
                        <span className="text-sm font-semibold text-blue-600 dark:text-blue-400">{teamData.analytics.writing_agent_percentage}%</span>
                      </div>
                      <div className="mt-2 bg-slate-200 dark:bg-slate-700 rounded-full h-1.5 overflow-hidden">
                        <div className="bg-blue-500 h-full rounded-full" style={{ width: `${teamData.analytics.writing_agent_percentage}%` }} />
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>

                <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}>
                  <Card className="border-slate-200/80 dark:border-slate-800/50 bg-gradient-to-br from-emerald-50 to-white dark:from-emerald-950/20 dark:to-slate-900/50">
                    <CardContent className="p-4">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-emerald-100 dark:bg-emerald-900/50">
                          <DollarSign className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                        </div>
                        <div className="flex-1">
                          <p className="text-xs text-slate-500 dark:text-slate-400">Avg AP per Writer</p>
                          <span className="text-xl font-bold text-emerald-600 dark:text-emerald-400">
                            ${teamData.analytics.avg_submitted_per_writer?.toLocaleString()}
                          </span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>

              </div>
            )}

            {/* Chart */}
            <motion.div 
              initial={{ opacity: 0, y: 10 }} 
              animate={{ opacity: 1, y: 0 }} 
              transition={{ delay: 0.2 }}
              className={teamData?.analytics ? 'lg:col-span-3' : 'lg:col-span-5'}
            >
              <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50 h-full">
                <CardHeader className="pb-2 pt-4 px-4">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-cyan-50 dark:bg-cyan-950/30">
                      <TrendingUp className="h-3.5 w-3.5 text-cyan-600 dark:text-cyan-400" />
                    </div>
                    <CardTitle className="text-sm font-semibold text-slate-900 dark:text-white">Team Production</CardTitle>
                  </div>
                </CardHeader>
                <CardContent className="px-4 pb-4 pt-2">
                  {teamData?.clients && teamData.clients.length > 0 ? (
                    <div className="h-48">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={prepareChartData(teamData.clients)} margin={{ top: 5, right: 5, left: 0, bottom: 5 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" className="dark:stroke-slate-700" />
                          <XAxis 
                            dataKey="date"
                            tick={{ fontSize: 10, fill: '#94a3b8' }}
                            axisLine={{ stroke: '#e2e8f0' }}
                            tickLine={false}
                            tickFormatter={(value) => format(new Date(value), 'MMM d')}
                          />
                          <YAxis 
                            tick={{ fontSize: 10, fill: '#94a3b8' }}
                            axisLine={false}
                            tickLine={false}
                            tickFormatter={(value) => `$${value >= 1000 ? `${(value/1000).toFixed(0)}k` : value}`}
                            width={45}
                          />
                          <Tooltip content={<CustomTooltip />} />
                          <Bar dataKey="submitted" fill="#06b6d4" name="Submitted" radius={[4, 4, 0, 0]} />
                          <Bar dataKey="issued" fill="#10b981" name="Issued" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  ) : (
                    <div className="h-48 flex items-center justify-center text-slate-500 dark:text-slate-400 text-sm">
                      No team data for selected period
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* Direct Legs Production Breakdown Chart - Enhanced */}
          <DirectLegChart 
            directLegsData={directLegsData} 
            onDrillDown={handleDrillDown}
            startDate={startDate}
            endDate={endDate}
          />

          {/* Leaderboard */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
              <CardHeader className="pb-2 pt-4 px-4">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 rounded-lg bg-amber-50 dark:bg-amber-950/30">
                    <Award className="h-3.5 w-3.5 text-amber-600 dark:text-amber-400" />
                  </div>
                  <CardTitle className="text-sm font-semibold text-slate-900 dark:text-white">Agent Leaderboard</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="px-4 pb-4 pt-2">
                {teamData?.agents && teamData.agents.length > 0 ? (
                  <div className="space-y-2">
                    {teamData.agents.slice(0, 5).map((agent, index) => (
                      <div 
                        key={agent.agent_id}
                        className={`flex items-center gap-3 p-3 rounded-lg border transition-all ${
                          index === 0 
                            ? 'bg-amber-50 dark:bg-amber-950/20 border-amber-200 dark:border-amber-800/50' 
                            : 'bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700/50'
                        }`}
                      >
                        <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${
                          index === 0 ? 'bg-amber-500 text-white' :
                          index === 1 ? 'bg-slate-400 text-white' :
                          index === 2 ? 'bg-amber-700 text-white' :
                          'bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300'
                        }`}>
                          {index + 1}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-sm text-slate-900 dark:text-white truncate">
                              {agent.agent_name}
                            </span>
                            {agent.agent_id === user.id && (
                              <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-100 dark:bg-cyan-900/50 text-cyan-700 dark:text-cyan-300">You</span>
                            )}
                          </div>
                          <span className="text-xs text-slate-500 dark:text-slate-400">{agent.policies} policies</span>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-bold text-slate-900 dark:text-white">${agent.submitted_ap.toLocaleString()}</div>
                          <div className="text-xs text-emerald-600 dark:text-emerald-400">${agent.issued_ap.toLocaleString()} issued</div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="py-8 text-center text-slate-500 dark:text-slate-400 text-sm">
                    No team data available
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
