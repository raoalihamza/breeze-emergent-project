import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card.jsx';
import { Button } from './ui/button.jsx';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog.jsx';
import { Users, DollarSign, TrendingUp, TrendingDown, BarChart3, Percent, ArrowLeft } from 'lucide-react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ComposedChart, Cell } from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';

const TIER_COLORS = {
  top: '#10b981',     // Green
  middle: '#06b6d4',  // Cyan
  bottom: '#f97316'   // Orange
};

export default function DirectLegChart({ directLegsData, onDrillDown, startDate, endDate }) {
  const [viewMode, setViewMode] = useState('percentage'); // 'percentage' or 'amount'
  const [drillDownData, setDrillDownData] = useState(null);
  const [showDrillDown, setShowDrillDown] = useState(false);

  if (!directLegsData || !directLegsData.legs || directLegsData.legs.length === 0) {
    return null;
  }

  const handleBarClick = async (data) => {
    const breakdown = await onDrillDown(data.leg_id, startDate, endDate);
    setDrillDownData(breakdown);
    setShowDrillDown(true);
  };

  const getBarColor = (tier) => TIER_COLORS[tier] || TIER_COLORS.middle;

  const getGrowthIndicator = (growth) => {
    if (growth > 0) {
      return (
        <div className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400">
          <TrendingUp className="h-3.5 w-3.5" />
          <span className="text-xs font-semibold">+{growth}%</span>
        </div>
      );
    } else if (growth < 0) {
      return (
        <div className="flex items-center gap-1 text-red-600 dark:text-red-400">
          <TrendingDown className="h-3.5 w-3.5" />
          <span className="text-xs font-semibold">{growth}%</span>
        </div>
      );
    }
    return <span className="text-xs text-slate-400">-</span>;
  };

  return (
    <>
      <motion.div 
        initial={{ opacity: 0, y: 10 }} 
        animate={{ opacity: 1, y: 0 }} 
        transition={{ delay: 0.3 }}
      >
        <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
          <CardHeader className="pb-2 pt-4 px-4">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <div className="p-1.5 rounded-lg bg-violet-50 dark:bg-violet-950/30">
                  <Users className="h-4 w-4 text-violet-600 dark:text-violet-400" />
                </div>
                <div>
                  <CardTitle className="text-base font-semibold text-slate-900 dark:text-white">
                    Direct Leg Contribution
                  </CardTitle>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                    Each leg's production including their entire downline
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1 text-xs text-slate-500 dark:text-slate-400">
                  <span>Total:</span>
                  <span className="font-bold text-slate-900 dark:text-white">
                    ${directLegsData.total_team_production?.toLocaleString()}
                  </span>
                  {directLegsData.total_growth_percentage !== 0 && (
                    <span className="ml-1">
                      {getGrowthIndicator(directLegsData.total_growth_percentage)}
                    </span>
                  )}
                </div>
                <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 p-0.5 rounded-lg">
                  <Button
                    size="sm"
                    variant={viewMode === 'percentage' ? 'default' : 'ghost'}
                    onClick={() => setViewMode('percentage')}
                    className="h-7 px-2 text-xs"
                  >
                    <Percent className="h-3 w-3" />
                  </Button>
                  <Button
                    size="sm"
                    variant={viewMode === 'amount' ? 'default' : 'ghost'}
                    onClick={() => setViewMode('amount')}
                    className="h-7 px-2 text-xs"
                  >
                    <DollarSign className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent className="px-4 pb-4 pt-2">
            <div className="h-80 sm:h-96">
              <ResponsiveContainer width="100%" height="100%">
                <ComposedChart 
                  data={directLegsData.legs} 
                  margin={{ top: 20, right: 30, left: 10, bottom: 80 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" className="dark:stroke-slate-700" />
                  <XAxis 
                    dataKey="leg_name"
                    angle={-45}
                    textAnchor="end"
                    height={80}
                    tick={{ fontSize: 11, fill: '#64748b' }}
                    axisLine={{ stroke: '#e2e8f0' }}
                    tickLine={false}
                  />
                  <YAxis 
                    yAxisId="left"
                    tick={{ fontSize: 10, fill: '#94a3b8' }}
                    axisLine={false}
                    tickLine={false}
                    tickFormatter={(value) => viewMode === 'percentage' ? `${value}%` : `$${value >= 1000 ? `${(value/1000).toFixed(0)}k` : value}`}
                    width={50}
                  />
                  <YAxis 
                    yAxisId="right"
                    orientation="right"
                    tick={{ fontSize: 10, fill: '#94a3b8' }}
                    axisLine={false}
                    tickLine={false}
                    tickFormatter={(value) => viewMode === 'amount' ? `${value}%` : `$${value >= 1000 ? `${(value/1000).toFixed(0)}k` : value}`}
                    width={50}
                  />
                  <Tooltip 
                    content={({ active, payload }) => {
                      if (active && payload && payload.length) {
                        const data = payload[0].payload;
                        return (
                          <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg p-3">
                            <p className="font-semibold text-slate-900 dark:text-white mb-2">
                              {data.leg_name}
                            </p>
                            <div className="space-y-1.5 text-xs">
                              <div className="flex justify-between gap-4">
                                <span className="text-slate-500 dark:text-slate-400">Production:</span>
                                <span className="font-semibold text-violet-600 dark:text-violet-400">
                                  ${data.production?.toLocaleString()}
                                </span>
                              </div>
                              <div className="flex justify-between gap-4">
                                <span className="text-slate-500 dark:text-slate-400">Percentage:</span>
                                <span className="font-semibold text-cyan-600 dark:text-cyan-400">
                                  {data.percentage}%
                                </span>
                              </div>
                              {data.growth_percentage !== 0 && (
                                <div className="flex justify-between gap-4">
                                  <span className="text-slate-500 dark:text-slate-400">Growth:</span>
                                  {getGrowthIndicator(data.growth_percentage)}
                                </div>
                              )}
                              <div className="flex justify-between gap-4">
                                <span className="text-slate-500 dark:text-slate-400">Team Size:</span>
                                <span className="font-medium text-slate-600 dark:text-slate-300">
                                  {data.team_size} agent{data.team_size !== 1 ? 's' : ''}
                                </span>
                              </div>
                              <div className="flex justify-between gap-4">
                                <span className="text-slate-500 dark:text-slate-400">Policies:</span>
                                <span className="font-medium text-slate-600 dark:text-slate-300">
                                  {data.policies}
                                </span>
                              </div>
                              <div className="flex justify-between gap-4 pt-1 border-t border-slate-200 dark:border-slate-700">
                                <span className="text-slate-500 dark:text-slate-400">Tier:</span>
                                <span className="font-medium capitalize" style={{ color: getBarColor(data.tier) }}>
                                  {data.tier}
                                </span>
                              </div>
                            </div>
                            <p className="text-xs text-slate-400 mt-2 italic">Click to drill down</p>
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <Bar 
                    yAxisId="left"
                    dataKey={viewMode === 'percentage' ? 'percentage' : 'production'} 
                    radius={[8, 8, 0, 0]}
                    maxBarSize={60}
                    onClick={handleBarClick}
                    cursor="pointer"
                  >
                    {directLegsData.legs.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={getBarColor(entry.tier)} />
                    ))}
                  </Bar>
                  <Line 
                    yAxisId="right"
                    type="monotone" 
                    dataKey={viewMode === 'amount' ? 'percentage' : 'production'}
                    stroke="#8b5cf6"
                    strokeWidth={2}
                    dot={{ fill: '#8b5cf6', r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
            
            {/* Legend */}
            <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex flex-wrap gap-3">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded" style={{ backgroundColor: TIER_COLORS.top }} />
                    <span className="text-xs text-slate-600 dark:text-slate-400">Top Performers</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded" style={{ backgroundColor: TIER_COLORS.middle }} />
                    <span className="text-xs text-slate-600 dark:text-slate-400">Mid Tier</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded" style={{ backgroundColor: TIER_COLORS.bottom }} />
                    <span className="text-xs text-slate-600 dark:text-slate-400">Growth Opportunity</span>
                  </div>
                </div>
                <div className="text-xs text-slate-500 dark:text-slate-400 italic">
                  Click any bar to view team breakdown
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Drill-Down Modal */}
      <Dialog open={showDrillDown} onOpenChange={setShowDrillDown}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowDrillDown(false)}
                className="h-8 w-8 p-0"
              >
                <ArrowLeft className="h-4 w-4" />
              </Button>
              <DialogTitle className="text-lg">
                {drillDownData?.leg_name}'s Team Breakdown
              </DialogTitle>
            </div>
          </DialogHeader>
          
          {drillDownData && (
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                <span className="text-sm font-medium text-slate-600 dark:text-slate-400">Total Production:</span>
                <span className="text-xl font-bold text-slate-900 dark:text-white">
                  ${drillDownData.total_production?.toLocaleString()}
                </span>
              </div>

              <div className="space-y-2">
                {drillDownData.agents?.map((agent, idx) => (
                  <motion.div
                    key={agent.agent_id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className="flex items-center justify-between p-3 border border-slate-200 dark:border-slate-700 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
                  >
                    <div className="flex items-center gap-3 flex-1">
                      <div className={`h-2 w-2 rounded-full ${agent.is_leg ? 'bg-violet-500' : 'bg-cyan-500'}`} />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-slate-900 dark:text-white truncate">
                          {agent.agent_name}
                        </p>
                        {agent.team_size > 1 && (
                          <p className="text-xs text-slate-500 dark:text-slate-400">
                            Team of {agent.team_size}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="text-sm font-bold text-slate-900 dark:text-white">
                          ${agent.production?.toLocaleString()}
                        </p>
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                          {agent.percentage}%
                        </p>
                      </div>
                      <div className="text-xs text-slate-500 dark:text-slate-400">
                        {agent.policies} {agent.policies === 1 ? 'policy' : 'policies'}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}
