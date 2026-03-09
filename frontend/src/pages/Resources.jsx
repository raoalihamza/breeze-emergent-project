import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent } from '../components/ui/card';
import { 
  Calculator, TrendingUp, FileSpreadsheet, GraduationCap, Bot, 
  Sparkles, Database, BookOpen, MessageSquare, Target, Users, 
  Zap, ChevronRight, ArrowUpRight, BarChart3
} from 'lucide-react';
import { motion } from 'framer-motion';
import AtlasAI from '../components/AtlasAI';
import KnowledgeBaseManager from '../components/KnowledgeBaseManager';

// Tool Card Component with Hover Glow Effect
const ToolCard = ({ icon: Icon, title, description, onClick, gradient, glowColor, badge, disabled }) => (
  <motion.button
    onClick={disabled ? undefined : onClick}
    disabled={disabled}
    whileHover={disabled ? {} : { scale: 1.02, y: -2 }}
    whileTap={disabled ? {} : { scale: 0.98 }}
    className={`group relative w-full text-left p-3 sm:p-4 rounded-2xl border transition-all duration-300 ${
      disabled 
        ? 'opacity-50 cursor-not-allowed bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-slate-800'
        : 'bg-white dark:bg-slate-900/80 border-slate-200/80 dark:border-slate-800/50 hover:border-transparent hover:shadow-xl'
    }`}
  >
    {/* Colored Glow Effect on Hover */}
    {!disabled && (
      <>
        <div className={`absolute -inset-0.5 rounded-2xl opacity-0 group-hover:opacity-30 blur-lg transition-opacity duration-300 ${gradient}`}></div>
        <div className={`absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 ${gradient}`}></div>
      </>
    )}
    
    <div className="relative flex items-start gap-3 sm:gap-4">
      <div className={`p-2 sm:p-3 rounded-xl ${disabled ? 'bg-slate-200 dark:bg-slate-800' : gradient} group-hover:scale-110 transition-transform duration-300 flex-shrink-0`}>
        <Icon className={`h-4 w-4 sm:h-5 sm:w-5 ${disabled ? 'text-slate-400' : 'text-white'}`} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          <h3 className="text-sm sm:text-base font-semibold text-slate-900 dark:text-white group-hover:text-white transition-colors">{title}</h3>
          {badge && (
            <span className="px-2 py-0.5 text-[9px] sm:text-[10px] font-bold uppercase tracking-wider rounded-full bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-400">
              {badge}
            </span>
          )}
        </div>
        <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 group-hover:text-white/80 transition-colors mt-0.5">{description}</p>
      </div>
      {!disabled && (
        <ChevronRight className="h-4 w-4 sm:h-5 sm:w-5 text-slate-300 group-hover:text-white group-hover:translate-x-1 transition-all flex-shrink-0" />
      )}
    </div>
  </motion.button>
);

// Link Card for external resources with Hover Glow
const LinkCard = ({ icon: Icon, title, description, url, gradient }) => (
  <motion.a
    href={url}
    target="_blank"
    rel="noopener noreferrer"
    whileHover={{ scale: 1.02, y: -2 }}
    whileTap={{ scale: 0.98 }}
    className="group relative block p-3 sm:p-4 rounded-2xl border border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/80 hover:border-transparent hover:shadow-xl transition-all duration-300"
  >
    {/* Colored Glow Effect on Hover */}
    <div className={`absolute -inset-0.5 rounded-2xl opacity-0 group-hover:opacity-30 blur-lg transition-opacity duration-300 ${gradient}`}></div>
    <div className={`absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 ${gradient}`}></div>
    
    <div className="relative flex items-center gap-2 sm:gap-3">
      <div className={`p-2 sm:p-2.5 rounded-xl ${gradient} group-hover:scale-110 transition-transform duration-300 flex-shrink-0`}>
        <Icon className="h-3 w-3 sm:h-4 sm:w-4 text-white" />
      </div>
      <div className="flex-1 min-w-0">
        <h3 className="text-xs sm:text-sm font-medium text-slate-900 dark:text-white group-hover:text-white transition-colors truncate">{title}</h3>
        <p className="text-[10px] sm:text-xs text-slate-500 dark:text-slate-400 group-hover:text-white/70 transition-colors truncate">{description}</p>
      </div>
      <ArrowUpRight className="h-3 w-3 sm:h-4 sm:w-4 text-slate-300 group-hover:text-white group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all flex-shrink-0" />
    </div>
  </motion.a>
);

export default function Resources() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [showAtlasAI, setShowAtlasAI] = useState(false);
  const [showKnowledgeBase, setShowKnowledgeBase] = useState(false);

  // Render Atlas AI full screen
  if (showAtlasAI) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 bg-white dark:bg-slate-950"
      >
        <AtlasAI onBack={() => setShowAtlasAI(false)} />
      </motion.div>
    );
  }

  // Render Knowledge Base full screen
  if (showKnowledgeBase) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 bg-white dark:bg-slate-950 overflow-y-auto"
      >
        <div className="max-w-6xl mx-auto p-4 sm:p-6 lg:p-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600">
                <Database className="h-6 w-6 text-white" />
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white">Knowledge Base Management</h1>
            </div>
            <button
              onClick={() => setShowKnowledgeBase(false)}
              className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <ChevronRight className="h-5 w-5 rotate-180" />
            </button>
          </div>
          <KnowledgeBaseManager />
        </div>
      </motion.div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-4 sm:space-y-6 p-4 sm:p-0">
      {/* Header */}
      <motion.div 
        initial={{ opacity: 0, y: -10 }} 
        animate={{ opacity: 1, y: 0 }} 
        className="flex items-center justify-between"
      >
        <div className="flex items-center gap-2 sm:gap-3">
          <div className="h-8 w-1 sm:h-10 sm:w-1.5 bg-gradient-to-b from-cyan-500 via-blue-500 to-violet-500 rounded-full"></div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white">Resource Hub</h1>
            <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 hidden sm:block">Tools, training, and everything you need to succeed</p>
          </div>
        </div>
      </motion.div>

      {/* Atlas AI Hero Card */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="border-0 overflow-hidden bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
          <CardContent className="p-0">
            <div className="relative">
              {/* Animated background */}
              <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-cyan-500/20 via-transparent to-violet-500/20"></div>
              <div className="absolute top-0 right-0 w-64 h-64 sm:w-96 sm:h-96 bg-cyan-500/10 rounded-full blur-3xl"></div>
              <div className="absolute bottom-0 left-0 w-48 h-48 sm:w-64 sm:h-64 bg-violet-500/10 rounded-full blur-3xl"></div>
              
              <div className="relative p-4 sm:p-6 flex flex-col sm:flex-row items-start sm:items-center gap-4 sm:gap-6">
                {/* Atlas AI Button */}
                <button
                  onClick={() => setShowAtlasAI(true)}
                  data-testid="atlas-ai-btn"
                  className="group relative flex-shrink-0 w-full sm:w-auto"
                >
                  {/* Glow rings */}
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-cyan-500 to-blue-500 opacity-75 blur-lg group-hover:opacity-100 transition-opacity"></div>
                  <div className="absolute -inset-1 rounded-2xl bg-gradient-to-r from-cyan-400 via-blue-500 to-violet-500 opacity-50 blur animate-pulse"></div>
                  
                  {/* Button content */}
                  <div className="relative flex items-center gap-3 sm:gap-4 px-4 py-3 sm:px-6 sm:py-5 rounded-2xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-2xl shadow-cyan-500/30 group-hover:shadow-cyan-500/50 transition-all">
                    <div className="h-10 w-10 sm:h-12 sm:w-12 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center group-hover:scale-110 transition-transform">
                      <Bot className="h-5 w-5 sm:h-7 sm:w-7" />
                    </div>
                    <div className="text-left flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-lg sm:text-xl font-bold">Atlas AI</span>
                        <Sparkles className="h-4 w-4 sm:h-5 sm:w-5 text-amber-300 animate-pulse" />
                      </div>
                      <p className="text-xs sm:text-sm text-cyan-100/90">Your 24/7 AI Assistant</p>
                    </div>
                    <ChevronRight className="h-5 w-5 sm:h-6 sm:w-6 group-hover:translate-x-1 transition-transform" />
                  </div>
                </button>
                
                {/* Description */}
                <div className="flex-1 text-white">
                  <h2 className="text-base sm:text-lg font-semibold mb-2">Breeze's AI Operating Assistant</h2>
                  <p className="text-xs sm:text-sm text-slate-300 leading-relaxed mb-3 sm:mb-4">
                    Get instant answers about onboarding, sales scripts, underwriting, carrier products, and operations. 
                    Aligned to The Breeze Way.
                  </p>
                  <div className="flex flex-wrap gap-2 sm:gap-4">
                    {['Scripts', 'Underwriting', 'Products', 'Training'].map((tag) => (
                      <span key={tag} className="px-2 py-1 text-[10px] sm:text-xs rounded-full bg-white/10 text-white/80">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Tools Grid */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h2 className="text-xs sm:text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3 sm:mb-4">Tools & Calculators</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
          <ToolCard
            icon={Calculator}
            title="Commission Calculator"
            description="Calculate your IUL and Term commissions"
            onClick={() => navigate('/commission-calculator')}
            gradient="bg-gradient-to-br from-emerald-500 to-teal-600"
          />
          <ToolCard
            icon={TrendingUp}
            title="Activity Tracker"
            description="Log your daily dials, contacts, and sales"
            onClick={() => navigate('/activity-tracker')}
            gradient="bg-gradient-to-br from-blue-500 to-indigo-600"
          />
          <ToolCard
            icon={FileSpreadsheet}
            title="CEO Report"
            description="Generate AI-powered weekly performance analysis"
            onClick={() => navigate('/ceo-report')}
            gradient="bg-gradient-to-br from-violet-500 to-purple-600"
            badge="AI"
          />
          <ToolCard
            icon={GraduationCap}
            title="Product Quiz"
            description="Test your insurance product knowledge"
            onClick={() => navigate('/quiz')}
            gradient="bg-gradient-to-br from-amber-500 to-orange-600"
          />
          {user?.role === 'admin' && (
            <ToolCard
              icon={Database}
              title="Knowledge Base"
              description="Manage Atlas AI training documents"
              onClick={() => setShowKnowledgeBase(true)}
              gradient="bg-gradient-to-br from-cyan-500 to-blue-600"
              badge="Admin"
            />
          )}
          {user?.role === 'admin' && (
            <ToolCard
              icon={BarChart3}
              title="Atlas AI Question Log"
              description="View what agents are asking (anonymous)"
              onClick={() => navigate('/atlas-question-log')}
              gradient="bg-gradient-to-br from-indigo-500 to-purple-600"
              badge="Admin"
            />
          )}
        </div>
      </motion.div>

      {/* Quick Links */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <h2 className="text-xs sm:text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-3 sm:mb-4">Quick Links & Resources</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2 sm:gap-3">
          <LinkCard
            icon={BookOpen}
            title="Prospecting Playbook"
            description="Master PDF Guide"
            url="https://customer-assets.emergentagent.com/job_60c446d2-55bd-4b91-8ce3-888669a24884/artifacts/y2i22f3b_Master%20Breeze%20Prospecting%20Playbook.pdf"
            gradient="bg-gradient-to-br from-rose-500 to-pink-600"
          />
          <LinkCard
            icon={MessageSquare}
            title="IUL Script"
            description="Interactive Notion Doc"
            url="https://www.notion.so/Breeze-IUL-Script-247423bc43ce8013b4facd3fd4f57f52"
            gradient="bg-gradient-to-br from-cyan-500 to-blue-600"
          />
          <LinkCard
            icon={Target}
            title="Blitz Training"
            description="Training Matrix"
            url="https://start.blitztrainingmatrix.com/"
            gradient="bg-gradient-to-br from-amber-500 to-orange-600"
          />
          <LinkCard
            icon={Zap}
            title="Insurance ToolKits"
            description="Tools & Resources"
            url="https://insurancetoolkits.com/signup"
            gradient="bg-gradient-to-br from-violet-500 to-purple-600"
          />
          <LinkCard
            icon={Users}
            title="Breeze Leadz"
            description="Purchase Leads"
            url="https://www.breezeleadz.com/"
            gradient="bg-gradient-to-br from-emerald-500 to-teal-600"
          />
          <LinkCard
            icon={MessageSquare}
            title="Agency Chat"
            description="Telegram Group"
            url="https://t.me/+DfodmWykl5JjOWFh"
            gradient="bg-gradient-to-br from-blue-500 to-indigo-600"
          />
        </div>
      </motion.div>
    </div>
  );
}
