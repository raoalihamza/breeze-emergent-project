import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { 
  GraduationCap, Trophy, Target, CheckCircle, XCircle, 
  ArrowRight, RotateCcw, ChevronLeft, Award, Zap, 
  BookOpen, Shield, Users, TrendingUp, Star, Activity
} from 'lucide-react';
import { toast } from 'sonner';
import { motion, AnimatePresence } from 'framer-motion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const PRODUCTS = [
  { id: 'IUL', name: 'Indexed Universal Life', icon: TrendingUp, color: 'from-purple-500 to-indigo-500', description: 'Permanent coverage with cash value growth' },
  { id: 'FIA', name: 'Fixed Indexed Annuity', icon: Shield, color: 'from-emerald-500 to-teal-500', description: 'Principal protection with index-linked growth' },
  { id: 'Term', name: 'Term Life Insurance', icon: Target, color: 'from-blue-500 to-cyan-500', description: 'Affordable temporary coverage' },
  { id: 'Final Expense', name: 'Final Expense', icon: BookOpen, color: 'from-amber-500 to-orange-500', description: 'Simplified coverage for end-of-life costs' },
];

const DIFFICULTIES = [
  { id: 'Easy', name: 'Easy', description: 'Foundational knowledge', color: 'from-green-400 to-emerald-500', target: 'New agents (0-60 days)' },
  { id: 'Intermediate', name: 'Intermediate', description: 'Applied knowledge', color: 'from-yellow-400 to-orange-500', target: 'Experienced agents (3-6 months)' },
  { id: 'Expert', name: 'Expert', description: 'Advanced mastery', color: 'from-red-400 to-pink-500', target: 'Top producers & specialists' },
];

export default function ProductQuiz() {
  const { getAuthHeader } = useAuth();
  
  // Quiz state
  const [quizState, setQuizState] = useState('select'); // 'select', 'quiz', 'results'
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [selectedDifficulty, setSelectedDifficulty] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackData, setFeedbackData] = useState(null);
  const [answers, setAnswers] = useState([]);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [checkingAnswer, setCheckingAnswer] = useState(false);
  
  // Progress state
  const [progress, setProgress] = useState(null);
  const [loadingProgress, setLoadingProgress] = useState(true);

  useEffect(() => {
    fetchProgress();
  }, []);

  const fetchProgress = async () => {
    try {
      const response = await axios.get(`${API}/quiz/progress`, getAuthHeader());
      setProgress(response.data);
    } catch (error) {
      console.error('Failed to fetch progress:', error);
    } finally {
      setLoadingProgress(false);
    }
  };

  const startQuiz = async () => {
    if (!selectedProduct || !selectedDifficulty) {
      toast.error('Please select a product and difficulty level');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.get(
        `${API}/quiz/questions?product=${selectedProduct}&difficulty=${selectedDifficulty}`,
        getAuthHeader()
      );
      setQuestions(response.data);
      setAnswers([]);
      setCurrentQuestionIndex(0);
      setSelectedAnswer(null);
      setShowFeedback(false);
      setQuizState('quiz');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to load quiz questions');
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!selectedAnswer) {
      toast.error('Please select an answer');
      return;
    }

    setCheckingAnswer(true);
    try {
      const response = await axios.post(
        `${API}/quiz/check-answer`,
        { question_id: questions[currentQuestionIndex].id, selected_answer: selectedAnswer },
        getAuthHeader()
      );
      setFeedbackData(response.data);
      setShowFeedback(true);
      setAnswers([...answers, { question_id: questions[currentQuestionIndex].id, selected_answer: selectedAnswer }]);
    } catch (error) {
      toast.error('Failed to check answer');
    } finally {
      setCheckingAnswer(false);
    }
  };

  const nextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setSelectedAnswer(null);
      setShowFeedback(false);
      setFeedbackData(null);
    } else {
      submitQuiz();
    }
  };

  const submitQuiz = async () => {
    setLoading(true);
    try {
      // Use the answers array directly - it already contains all 10 answers from submitAnswer calls
      const submission = {
        product: selectedProduct,
        difficulty: selectedDifficulty,
        answers: answers
      };
      
      const response = await axios.post(`${API}/quiz/submit`, submission, getAuthHeader());
      setResults(response.data);
      setQuizState('results');
      fetchProgress(); // Refresh progress data
    } catch (error) {
      toast.error('Failed to submit quiz');
    } finally {
      setLoading(false);
    }
  };

  const resetQuiz = () => {
    setQuizState('select');
    setSelectedProduct(null);
    setSelectedDifficulty(null);
    setQuestions([]);
    setCurrentQuestionIndex(0);
    setSelectedAnswer(null);
    setShowFeedback(false);
    setAnswers([]);
    setResults(null);
  };

  const retakeQuiz = () => {
    setQuestions([]);
    setCurrentQuestionIndex(0);
    setSelectedAnswer(null);
    setShowFeedback(false);
    setAnswers([]);
    setResults(null);
    startQuiz();
  };

  // Helper to get stats for a product/difficulty combo
  const getStats = (product, difficulty) => {
    if (!progress?.product_stats?.[product]?.[difficulty]) {
      return { attempts: 0, passed: 0, best_score: 0 };
    }
    return progress.product_stats[product][difficulty];
  };

  // Selection Screen
  if (quizState === 'select') {
    return (
      <div className="space-y-6">
        {/* Progress Overview */}
        {progress && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6"
          >
            <Card className="border-slate-200 dark:border-slate-800/50 bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm">
              <CardContent className="p-4 text-center">
                <div className="flex items-center justify-center mb-2">
                  <Target className="h-5 w-5 text-cyan-500" />
                </div>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">{progress.total_quizzes_taken}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400">Quizzes Taken</p>
              </CardContent>
            </Card>
            <Card className="border-slate-200 dark:border-slate-800/50 bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm">
              <CardContent className="p-4 text-center">
                <div className="flex items-center justify-center mb-2">
                  <Trophy className="h-5 w-5 text-emerald-500" />
                </div>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">{progress.total_passed}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400">Quizzes Passed</p>
              </CardContent>
            </Card>
            <Card className="border-slate-200 dark:border-slate-800/50 bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm">
              <CardContent className="p-4 text-center">
                <div className="flex items-center justify-center mb-2">
                  <Zap className="h-5 w-5 text-amber-500" />
                </div>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">{progress.current_streak}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400">Current Streak</p>
              </CardContent>
            </Card>
            <Card className="border-slate-200 dark:border-slate-800/50 bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm">
              <CardContent className="p-4 text-center">
                <div className="flex items-center justify-center mb-2">
                  <Award className="h-5 w-5 text-purple-500" />
                </div>
                <p className="text-2xl font-bold text-slate-900 dark:text-white">{progress.achievements?.length || 0}</p>
                <p className="text-xs text-slate-500 dark:text-slate-400">Achievements</p>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Achievements */}
        {progress?.achievements?.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card className="border-slate-200 dark:border-slate-800/50 bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm mb-6">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Star className="h-5 w-5 text-amber-500" />
                  Your Achievements
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {progress.achievements.map((achievement, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1.5 rounded-full text-xs font-medium bg-gradient-to-r from-amber-500/10 to-orange-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20"
                    >
                      🏆 {achievement}
                    </span>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Product Selection */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h3 className="text-lg font-semibold mb-4 text-slate-900 dark:text-white">Select Product Category</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {PRODUCTS.map((product) => {
              const Icon = product.icon;
              const isSelected = selectedProduct === product.id;
              return (
                <motion.div
                  key={product.id}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Card
                    className={`cursor-pointer transition-all duration-300 ${
                      isSelected
                        ? 'ring-2 ring-cyan-500 border-cyan-500 dark:border-cyan-500 bg-cyan-500/5'
                        : 'border-slate-200 dark:border-slate-800/50 hover:border-cyan-500/50'
                    } bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm`}
                    onClick={() => setSelectedProduct(product.id)}
                    data-testid={`product-${product.id.toLowerCase().replace(' ', '-')}`}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start gap-4">
                        <div className={`p-3 rounded-xl bg-gradient-to-br ${product.color} bg-opacity-10`}>
                          <Icon className="h-6 w-6 text-white" />
                        </div>
                        <div className="flex-1">
                          <h4 className="font-semibold text-slate-900 dark:text-white">{product.name}</h4>
                          <p className="text-sm text-slate-500 dark:text-slate-400">{product.description}</p>
                        </div>
                        {isSelected && (
                          <CheckCircle className="h-5 w-5 text-cyan-500" />
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </motion.div>

        {/* Difficulty Selection */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h3 className="text-lg font-semibold mb-4 text-slate-900 dark:text-white">Select Difficulty Level</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {DIFFICULTIES.map((diff) => {
              const isSelected = selectedDifficulty === diff.id;
              const stats = selectedProduct ? getStats(selectedProduct, diff.id) : null;
              return (
                <motion.div
                  key={diff.id}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Card
                    className={`cursor-pointer transition-all duration-300 ${
                      isSelected
                        ? 'ring-2 ring-cyan-500 border-cyan-500 dark:border-cyan-500 bg-cyan-500/5'
                        : 'border-slate-200 dark:border-slate-800/50 hover:border-cyan-500/50'
                    } bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm`}
                    onClick={() => setSelectedDifficulty(diff.id)}
                    data-testid={`difficulty-${diff.id.toLowerCase()}`}
                  >
                    <CardContent className="p-4">
                      <div className={`h-1 w-full rounded-full bg-gradient-to-r ${diff.color} mb-3`} />
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <h4 className="font-semibold text-slate-900 dark:text-white">{diff.name}</h4>
                          <p className="text-sm text-slate-500 dark:text-slate-400">{diff.description}</p>
                        </div>
                        {isSelected && (
                          <CheckCircle className="h-5 w-5 text-cyan-500" />
                        )}
                      </div>
                      <p className="text-xs text-slate-400 dark:text-slate-500 mb-2">{diff.target}</p>
                      {stats && stats.attempts > 0 && (
                        <div className="pt-2 border-t border-slate-200 dark:border-slate-800 space-y-1">
                          <p className="text-xs text-slate-500 dark:text-slate-400">
                            Best Score: <span className="font-semibold text-cyan-600 dark:text-cyan-400">{stats.best_score}%</span>
                          </p>
                          <p className="text-xs text-slate-500 dark:text-slate-400">
                            Passed: {stats.passed}/{stats.attempts}
                          </p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </motion.div>

        {/* Start Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="flex justify-center pt-4"
        >
          <Button
            onClick={startQuiz}
            disabled={!selectedProduct || !selectedDifficulty || loading}
            className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white px-8 py-6 text-lg rounded-xl shadow-lg shadow-cyan-500/25"
            data-testid="start-quiz-button"
          >
            {loading ? 'Loading...' : 'Start Quiz'}
            <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
        </motion.div>
      </div>
    );
  }

  // Quiz Screen
  if (quizState === 'quiz' && questions.length > 0) {
    const currentQuestion = questions[currentQuestionIndex];
    const progressPercent = ((currentQuestionIndex + 1) / questions.length) * 100;
    const correctSoFar = answers.filter((a, idx) => {
      // We need to check against the submitted results, but we don't have them yet
      // Just show the count of answered questions
      return true;
    }).length;

    return (
      <div className="max-w-3xl mx-auto">
        {/* Progress Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-slate-600 dark:text-slate-400">
              Question {currentQuestionIndex + 1} of {questions.length}
            </span>
            <span className="text-sm font-medium text-slate-600 dark:text-slate-400">
              {selectedProduct} • {selectedDifficulty}
            </span>
          </div>
          <Progress value={progressPercent} className="h-2" />
          <div className="flex items-center justify-between mt-2">
            <span className="text-xs text-slate-500 dark:text-slate-400">
              {currentQuestion.category}
            </span>
            <span className="text-xs text-slate-500 dark:text-slate-400">
              {answers.length} answered
            </span>
          </div>
        </motion.div>

        {/* Question Card */}
        <AnimatePresence mode="wait">
          <motion.div
            key={currentQuestionIndex}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            transition={{ duration: 0.3 }}
          >
            <Card className="border-slate-200 dark:border-slate-800/50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm shadow-xl">
              <CardContent className="p-6">
                <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-6 leading-relaxed">
                  {currentQuestion.question}
                </h3>

                <div className="space-y-3">
                  {Object.entries(currentQuestion.options).map(([key, value]) => {
                    const isSelected = selectedAnswer === key;
                    const isCorrect = showFeedback && feedbackData && key === feedbackData.correct_answer;
                    const isWrong = showFeedback && feedbackData && isSelected && key !== feedbackData.correct_answer;

                    return (
                      <motion.button
                        key={key}
                        whileHover={!showFeedback ? { scale: 1.01 } : {}}
                        whileTap={!showFeedback ? { scale: 0.99 } : {}}
                        onClick={() => !showFeedback && setSelectedAnswer(key)}
                        disabled={showFeedback || checkingAnswer}
                        className={`w-full p-4 rounded-xl text-left transition-all duration-200 border ${
                          isCorrect
                            ? 'bg-emerald-500/10 border-emerald-500 text-emerald-700 dark:text-emerald-300'
                            : isWrong
                            ? 'bg-red-500/10 border-red-500 text-red-700 dark:text-red-300'
                            : isSelected
                            ? 'bg-cyan-500/10 border-cyan-500 text-cyan-700 dark:text-cyan-300'
                            : 'bg-slate-50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700 hover:border-cyan-500/50'
                        }`}
                        data-testid={`answer-${key}`}
                      >
                        <div className="flex items-center gap-3">
                          <span className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                            isCorrect
                              ? 'bg-emerald-500 text-white'
                              : isWrong
                              ? 'bg-red-500 text-white'
                              : isSelected
                              ? 'bg-cyan-500 text-white'
                              : 'bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300'
                          }`}>
                            {key}
                          </span>
                          <span className="flex-1 text-slate-700 dark:text-slate-200">{value}</span>
                          {isCorrect && <CheckCircle className="h-5 w-5 text-emerald-500" />}
                          {isWrong && <XCircle className="h-5 w-5 text-red-500" />}
                        </div>
                      </motion.button>
                    );
                  })}
                </div>

                {/* Feedback */}
                {showFeedback && feedbackData && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`mt-6 p-4 rounded-xl ${
                      feedbackData.is_correct
                        ? 'bg-emerald-500/10 border border-emerald-500/30'
                        : 'bg-red-500/10 border border-red-500/30'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      {feedbackData.is_correct ? (
                        <CheckCircle className="h-5 w-5 text-emerald-500 mt-0.5" />
                      ) : (
                        <XCircle className="h-5 w-5 text-red-500 mt-0.5" />
                      )}
                      <div>
                        <p className={`font-semibold ${
                          feedbackData.is_correct
                            ? 'text-emerald-700 dark:text-emerald-300'
                            : 'text-red-700 dark:text-red-300'
                        }`}>
                          {feedbackData.is_correct ? 'Correct!' : 'Incorrect'}
                        </p>
                        <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                          {feedbackData.explanation || `The correct answer is ${feedbackData.correct_answer}.`}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                )}

                {/* Action Buttons */}
                <div className="mt-6 flex justify-end gap-3">
                  {!showFeedback ? (
                    <Button
                      onClick={submitAnswer}
                      disabled={!selectedAnswer || checkingAnswer}
                      className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white"
                      data-testid="submit-answer-button"
                    >
                      {checkingAnswer ? 'Checking...' : 'Submit Answer'}
                    </Button>
                  ) : (
                    <Button
                      onClick={nextQuestion}
                      className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white"
                      data-testid="next-question-button"
                    >
                      {currentQuestionIndex < questions.length - 1 ? 'Next Question' : 'See Results'}
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </AnimatePresence>
      </div>
    );
  }

  // Results Screen
  if (quizState === 'results' && results) {
    const passed = results.passed;
    
    return (
      <div className="max-w-3xl mx-auto">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          {/* Score Card */}
          <Card className={`border-2 ${
            passed 
              ? 'border-emerald-500 bg-gradient-to-br from-emerald-500/10 to-teal-500/10' 
              : 'border-red-500 bg-gradient-to-br from-red-500/10 to-orange-500/10'
          } backdrop-blur-sm mb-6`}>
            <CardContent className="p-8 text-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: 'spring' }}
                className={`w-24 h-24 mx-auto rounded-full flex items-center justify-center mb-6 ${
                  passed ? 'bg-emerald-500' : 'bg-red-500'
                }`}
              >
                {passed ? (
                  <Trophy className="h-12 w-12 text-white" />
                ) : (
                  <XCircle className="h-12 w-12 text-white" />
                )}
              </motion.div>
              
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
                {results.score}/{results.total_questions}
              </h2>
              <p className={`text-xl font-semibold mb-4 ${
                passed ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'
              }`}>
                {results.percentage}% - {passed ? 'PASSED' : 'FAILED'}
              </p>
              <p className="text-slate-600 dark:text-slate-400">
                {passed 
                  ? 'Great job! You demonstrated strong knowledge in this area.' 
                  : 'Keep studying! You need 70% to pass. Review the explanations below.'}
              </p>
            </CardContent>
          </Card>

          {/* Category Breakdown */}
          {results.category_scores && Object.keys(results.category_scores).length > 0 && (
            <Card className="border-slate-200 dark:border-slate-800/50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm mb-6">
              <CardHeader>
                <CardTitle className="text-lg">Performance by Category</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Object.entries(results.category_scores).map(([category, data]) => {
                    const percent = data.total > 0 ? (data.correct / data.total) * 100 : 0;
                    return (
                      <div key={category}>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{category}</span>
                          <span className="text-sm text-slate-500 dark:text-slate-400">
                            {data.correct}/{data.total} ({Math.round(percent)}%)
                          </span>
                        </div>
                        <Progress 
                          value={percent} 
                          className={`h-2 ${percent >= 70 ? 'bg-emerald-100' : 'bg-red-100'}`} 
                        />
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Question Review */}
          <Card className="border-slate-200 dark:border-slate-800/50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm mb-6">
            <CardHeader>
              <CardTitle className="text-lg">Question Review</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {results.question_results?.map((result, idx) => (
                  <div 
                    key={idx}
                    className={`p-4 rounded-lg border ${
                      result.is_correct 
                        ? 'bg-emerald-500/5 border-emerald-500/30' 
                        : 'bg-red-500/5 border-red-500/30'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      {result.is_correct ? (
                        <CheckCircle className="h-5 w-5 text-emerald-500 mt-0.5 flex-shrink-0" />
                      ) : (
                        <XCircle className="h-5 w-5 text-red-500 mt-0.5 flex-shrink-0" />
                      )}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-slate-900 dark:text-white mb-1">
                          Q{idx + 1}: {result.question}
                        </p>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mb-2">
                          Your answer: <span className={result.is_correct ? 'text-emerald-600' : 'text-red-600'}>{result.selected_answer}</span>
                          {!result.is_correct && (
                            <> • Correct: <span className="text-emerald-600">{result.correct_answer}</span></>
                          )}
                        </p>
                        <p className="text-xs text-slate-600 dark:text-slate-400">
                          {result.explanation}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Action Buttons */}
          <div className="flex flex-wrap justify-center gap-4">
            <Button
              onClick={retakeQuiz}
              variant="outline"
              className="border-slate-200 dark:border-slate-700"
              data-testid="retake-quiz-button"
            >
              <RotateCcw className="mr-2 h-4 w-4" />
              Retake Quiz
            </Button>
            <Button
              onClick={() => {
                setSelectedDifficulty(null);
                setQuizState('select');
                setResults(null);
              }}
              variant="outline"
              className="border-slate-200 dark:border-slate-700"
            >
              Try Different Difficulty
            </Button>
            <Button
              onClick={resetQuiz}
              className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white"
              data-testid="back-to-selection-button"
            >
              <ChevronLeft className="mr-2 h-4 w-4" />
              Back to Selection
            </Button>
          </div>
        </motion.div>
      </div>
    );
  }

  // Loading state
  return (
    <div className="flex items-center justify-center h-64">
      <div className="relative">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-500"></div>
        <div className="absolute inset-0 flex items-center justify-center">
          <Activity className="h-5 w-5 text-cyan-500 animate-pulse" />
        </div>
      </div>
    </div>
  );
}
