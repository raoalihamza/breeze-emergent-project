import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { FileSpreadsheet, X } from 'lucide-react';
import { toast } from 'sonner';
import { motion } from 'framer-motion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function CEOReport() {
  const navigate = useNavigate();
  const { getAuthHeader } = useAuth();
  const [ceoReport, setCeoReport] = useState(null);
  const [loadingReport, setLoadingReport] = useState(false);

  const generateCEOReport = async () => {
    setLoadingReport(true);
    try {
      const response = await axios.get(`${API}/kpi/weekly-report`, getAuthHeader());
      setCeoReport(response.data);
    } catch (error) {
      toast.error('Failed to generate report');
    } finally {
      setLoadingReport(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 bg-white dark:bg-slate-950 overflow-y-auto"
    >
      <div className="max-w-4xl mx-auto p-4 sm:p-6 lg:p-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600">
              <FileSpreadsheet className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white">Weekly CEO Report</h1>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">AI-powered performance analysis</p>
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

        {/* Content */}
        <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/80">
          <CardContent className="p-4 sm:p-6">
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Generate an AI-powered analysis of your weekly performance metrics
              </p>
              <Button
                onClick={generateCEOReport}
                disabled={loadingReport}
                className="w-full sm:w-auto bg-gradient-to-r from-violet-500 to-purple-600"
              >
                {loadingReport ? 'Generating...' : 'Generate Report'}
              </Button>
            </div>

            {ceoReport && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                {/* Week Date Range */}
                <div className="text-sm text-slate-500 dark:text-slate-400 font-medium">
                  Report Period: {ceoReport.week_start} to {ceoReport.week_end}
                </div>

                {/* Executive Summary */}
                <div className="p-5 rounded-xl bg-gradient-to-br from-violet-50 to-purple-50 dark:from-violet-950/30 dark:to-purple-950/30 border border-violet-200 dark:border-violet-800">
                  <h3 className="text-lg font-bold text-violet-900 dark:text-violet-100 mb-3 flex items-center gap-2">
                    <FileSpreadsheet className="h-5 w-5" />
                    Executive Summary
                  </h3>
                  <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                    {ceoReport.executive_summary}
                  </p>
                </div>

                {/* What Went Well */}
                {ceoReport.what_went_well && ceoReport.what_went_well.length > 0 && (
                  <div className="p-5 rounded-xl bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-800">
                    <h3 className="text-lg font-bold text-green-900 dark:text-green-100 mb-3">
                      ✅ What Went Well
                    </h3>
                    <ul className="space-y-2">
                      {ceoReport.what_went_well.map((item, idx) => (
                        <li key={idx} className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed flex gap-2">
                          <span className="text-green-500 font-bold">•</span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Patterns Identified */}
                {ceoReport.patterns && ceoReport.patterns.length > 0 && (
                  <div className="p-5 rounded-xl bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800">
                    <h3 className="text-lg font-bold text-blue-900 dark:text-blue-100 mb-3">
                      📊 Patterns Identified
                    </h3>
                    <ul className="space-y-2">
                      {ceoReport.patterns.map((item, idx) => (
                        <li key={idx} className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed flex gap-2">
                          <span className="text-blue-500 font-bold">•</span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Focus Areas */}
                {ceoReport.focus_areas && ceoReport.focus_areas.length > 0 && (
                  <div className="p-5 rounded-xl bg-orange-50 dark:bg-orange-950/20 border border-orange-200 dark:border-orange-800">
                    <h3 className="text-lg font-bold text-orange-900 dark:text-orange-100 mb-3">
                      🎯 Focus Areas
                    </h3>
                    <ul className="space-y-2">
                      {ceoReport.focus_areas.map((item, idx) => (
                        <li key={idx} className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed flex gap-2">
                          <span className="text-orange-500 font-bold">•</span>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Self-Reflection Questions */}
                {ceoReport.self_reflection_questions && ceoReport.self_reflection_questions.length > 0 && (
                  <div className="p-5 rounded-xl bg-purple-50 dark:bg-purple-950/20 border border-purple-200 dark:border-purple-800">
                    <h3 className="text-lg font-bold text-purple-900 dark:text-purple-100 mb-3">
                      💭 Self-Reflection Questions
                    </h3>
                    <ol className="space-y-3 list-decimal list-inside">
                      {ceoReport.self_reflection_questions.map((item, idx) => (
                        <li key={idx} className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                          {item}
                        </li>
                      ))}
                    </ol>
                  </div>
                )}

                {/* KPI Summary (if available) */}
                {ceoReport.improvements && ceoReport.improvements.length > 0 && (
                  <div className="p-5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                    <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100 mb-3">
                      📈 Week-over-Week Improvements
                    </h3>
                    <ul className="space-y-1">
                      {ceoReport.improvements.map((item, idx) => (
                        <li key={idx} className="text-sm text-green-600 dark:text-green-400">
                          ↑ {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {ceoReport.declines && ceoReport.declines.length > 0 && (
                  <div className="p-5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                    <h3 className="text-lg font-bold text-slate-900 dark:text-slate-100 mb-3">
                      📉 Week-over-Week Declines
                    </h3>
                    <ul className="space-y-1">
                      {ceoReport.declines.map((item, idx) => (
                        <li key={idx} className="text-sm text-red-600 dark:text-red-400">
                          ↓ {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </motion.div>
            )}

            {!ceoReport && !loadingReport && (
              <div className="text-center py-12 text-slate-500 dark:text-slate-400">
                <FileSpreadsheet className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p className="text-sm">Click "Generate Report" to create your weekly analysis</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
}
