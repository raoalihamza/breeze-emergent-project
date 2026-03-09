import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { BarChart3, TrendingUp, Zap, MessageSquare, X } from 'lucide-react';
import { toast } from 'sonner';
import { motion } from 'framer-motion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function AtlasQuestionLog() {
  const navigate = useNavigate();
  const { getAuthHeader } = useAuth();
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState(null);
  const [selectedTab, setSelectedTab] = useState('top-questions');

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/atlas-ai/question-analytics`, getAuthHeader());
      setAnalytics(response.data);
    } catch (error) {
      toast.error('Failed to load analytics');
      console.error('Analytics error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 z-50 bg-white dark:bg-slate-950 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500 mx-auto mb-4"></div>
          <p className="text-slate-600 dark:text-slate-400">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 bg-white dark:bg-slate-950 overflow-y-auto"
    >
      <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600">
              <BarChart3 className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white">Atlas AI Question Log</h1>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Anonymous analytics • What agents are asking</p>
            </div>
          </div>
          <Button
            onClick={() => navigate('/resources')}
            variant="ghost"
            size="icon"
            className="rounded-full"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Summary Stats */}
        {analytics?.summary && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-cyan-100 dark:bg-cyan-900/30">
                    <MessageSquare className="h-5 w-5 text-cyan-600 dark:text-cyan-400" />
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 dark:text-slate-400">Total Questions</p>
                    <p className="text-2xl font-bold text-slate-900 dark:text-white">{analytics.summary.total_questions_asked.toLocaleString()}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-violet-100 dark:bg-violet-900/30">
                    <TrendingUp className="h-5 w-5 text-violet-600 dark:text-violet-400" />
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 dark:text-slate-400">Unique Questions</p>
                    <p className="text-2xl font-bold text-slate-900 dark:text-white">{analytics.summary.unique_questions}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-emerald-100 dark:bg-emerald-900/30">
                    <Zap className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 dark:text-slate-400">Cache Hit Rate</p>
                    <p className="text-2xl font-bold text-slate-900 dark:text-white">{analytics.summary.cache_hit_rate}%</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-amber-100 dark:bg-amber-900/30">
                    <BarChart3 className="h-5 w-5 text-amber-600 dark:text-amber-400" />
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 dark:text-slate-400">Last 7 Days</p>
                    <p className="text-2xl font-bold text-slate-900 dark:text-white">{analytics.summary.questions_last_7_days}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          <Button
            onClick={() => setSelectedTab('top-questions')}
            variant={selectedTab === 'top-questions' ? 'default' : 'outline'}
            size="sm"
            className="whitespace-nowrap"
          >
            Top Questions
          </Button>
          <Button
            onClick={() => setSelectedTab('topics')}
            variant={selectedTab === 'topics' ? 'default' : 'outline'}
            size="sm"
            className="whitespace-nowrap"
          >
            Topics
          </Button>
          <Button
            onClick={() => setSelectedTab('complexity')}
            variant={selectedTab === 'complexity' ? 'default' : 'outline'}
            size="sm"
            className="whitespace-nowrap"
          >
            Complexity
          </Button>
        </div>

        {/* Content */}
        <Card>
          <CardContent className="p-6">
            {selectedTab === 'top-questions' && analytics?.top_questions && (
              <div className="space-y-3">
                <h3 className="font-semibold text-lg mb-4">Most Asked Questions</h3>
                {analytics.top_questions.map((q, idx) => (
                  <div key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-slate-50 dark:bg-slate-800">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-cyan-100 dark:bg-cyan-900/30 flex items-center justify-center">
                      <span className="text-sm font-bold text-cyan-600 dark:text-cyan-400">{idx + 1}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-slate-900 dark:text-white">{q.question_preview}</p>
                      <div className="flex items-center gap-3 mt-1 text-xs text-slate-500 dark:text-slate-400">
                        <span>Asked {q.ask_count}x</span>
                        <span>•</span>
                        <span className="capitalize">{q.complexity}</span>
                        <span>•</span>
                        <span>{q.topic}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {selectedTab === 'topics' && analytics?.topic_distribution && (
              <div className="space-y-4">
                <h3 className="font-semibold text-lg mb-4">Questions by Topic</h3>
                {analytics.topic_distribution.map((topic, idx) => (
                  <div key={idx} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-900 dark:text-white">{topic.topic}</span>
                      <span className="text-sm text-slate-500 dark:text-slate-400">{topic.total_asks} asks</span>
                    </div>
                    <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-cyan-500 to-blue-600 h-2 rounded-full"
                        style={{ width: `${(topic.total_asks / analytics.summary.total_questions_asked) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {selectedTab === 'complexity' && analytics?.complexity_distribution && (
              <div className="space-y-4">
                <h3 className="font-semibold text-lg mb-4">Question Complexity Breakdown</h3>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {analytics.complexity_distribution.map((c, idx) => (
                    <Card key={idx}>
                      <CardContent className="p-4 text-center">
                        <p className="text-3xl font-bold text-slate-900 dark:text-white mb-2">{c.count}</p>
                        <p className="text-sm text-slate-500 dark:text-slate-400 capitalize">{c.complexity} Questions</p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
                <div className="mt-6 p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
                  <p className="text-sm text-blue-900 dark:text-blue-100">
                    <strong>Cost Optimization:</strong> Simple questions use Claude Haiku (90% cheaper), 
                    while complex questions use Claude Sonnet for best quality.
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
}
