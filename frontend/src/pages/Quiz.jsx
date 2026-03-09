import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { GraduationCap, X } from 'lucide-react';
import { motion } from 'framer-motion';
import ProductQuiz from '../components/ProductQuiz';

export default function Quiz() {
  const navigate = useNavigate();

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
            <div className="p-3 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600">
              <GraduationCap className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white">Product Knowledge Quiz</h1>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">10 questions • 70% to pass</p>
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

        {/* Quiz Component */}
        <ProductQuiz />
      </div>
    </motion.div>
  );
}
