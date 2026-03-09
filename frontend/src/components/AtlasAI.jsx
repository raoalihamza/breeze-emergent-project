import { useState, useRef, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { ScrollArea } from '../components/ui/scroll-area';
import { Send, Bot, User, Sparkles, BookOpen, FileText, Users, Briefcase, Settings, ArrowLeft, Loader2, Copy, Check, ExternalLink } from 'lucide-react';
import { toast } from 'sonner';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const QUICK_CHIPS = [
  { label: 'Onboarding', icon: BookOpen, query: 'What are the first steps for a new agent?' },
  { label: 'Scripts', icon: FileText, query: 'Give me an IUL opening script' },
  { label: 'Recruiting', icon: Users, query: 'How do I vet a potential recruit?' },
  { label: 'Operations', icon: Briefcase, query: "What's the contracting process?" },
  { label: 'Resources', icon: Settings, query: 'Where can I find the Builder SOP?' },
];

// Custom component to render code blocks with copy button
const CodeBlock = ({ children, className }) => {
  const [copied, setCopied] = useState(false);
  const isScript = className?.includes('script') || className?.includes('language-script');
  
  const handleCopy = async () => {
    const text = String(children).replace(/\n$/, '');
    await navigator.clipboard.writeText(text);
    setCopied(true);
    toast.success('Copied to clipboard!');
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`relative group my-3 ${isScript ? 'bg-gradient-to-r from-cyan-50 to-blue-50 dark:from-cyan-950/30 dark:to-blue-950/30 border border-cyan-200 dark:border-cyan-800' : 'bg-slate-100 dark:bg-slate-800'} rounded-lg`}>
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 rounded-t-lg">
        <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
          {isScript ? '📋 Script' : 'Code'}
        </span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1 px-2 py-1 text-xs rounded hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
        >
          {copied ? (
            <>
              <Check className="h-3 w-3 text-emerald-500" />
              <span className="text-emerald-500">Copied</span>
            </>
          ) : (
            <>
              <Copy className="h-3 w-3" />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>
      <pre className="p-3 overflow-x-auto text-sm">
        <code className={`${isScript ? 'text-slate-800 dark:text-slate-200' : ''}`}>{children}</code>
      </pre>
    </div>
  );
};

// Custom link component
const CustomLink = ({ href, children }) => (
  <a 
    href={href} 
    target="_blank" 
    rel="noopener noreferrer"
    className="inline-flex items-center gap-1 text-cyan-600 dark:text-cyan-400 hover:text-cyan-700 dark:hover:text-cyan-300 underline underline-offset-2 font-medium"
  >
    {children}
    <ExternalLink className="h-3 w-3" />
  </a>
);

// Custom blockquote for warnings and tips
const CustomBlockquote = ({ children }) => {
  const text = String(children?.props?.children || children || '');
  const isWarning = text.includes('⚠️') || text.toLowerCase().includes('important') || text.toLowerCase().includes('warning');
  const isTip = text.includes('💡') || text.toLowerCase().includes('tip') || text.toLowerCase().includes('pro tip');
  
  let style = 'border-slate-300 bg-slate-50 dark:border-slate-600 dark:bg-slate-800/50';
  if (isWarning) {
    style = 'border-amber-400 bg-amber-50 dark:border-amber-600 dark:bg-amber-950/30';
  } else if (isTip) {
    style = 'border-emerald-400 bg-emerald-50 dark:border-emerald-600 dark:bg-emerald-950/30';
  }
  
  return (
    <blockquote className={`my-3 pl-4 py-2 pr-3 border-l-4 rounded-r-lg ${style}`}>
      {children}
    </blockquote>
  );
};

// Custom table components
const CustomTable = ({ children }) => (
  <div className="my-3 overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-700">
    <table className="w-full text-sm">{children}</table>
  </div>
);

const CustomThead = ({ children }) => (
  <thead className="bg-slate-100 dark:bg-slate-800">{children}</thead>
);

const CustomTh = ({ children }) => (
  <th className="px-3 py-2 text-left font-semibold text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-700">{children}</th>
);

const CustomTd = ({ children }) => (
  <td className="px-3 py-2 border-b border-slate-100 dark:border-slate-800">{children}</td>
);

// Custom list items for checklists
const CustomLi = ({ children, ...props }) => {
  const text = String(children?.[0] || children || '');
  const isChecklist = text.startsWith('[ ]') || text.startsWith('[x]') || text.startsWith('[X]');
  
  if (isChecklist) {
    const isChecked = text.startsWith('[x]') || text.startsWith('[X]');
    const content = text.replace(/^\[[ xX]\]\s*/, '');
    return (
      <li className="flex items-start gap-2 my-1 list-none" {...props}>
        <div className={`mt-0.5 h-4 w-4 rounded border flex items-center justify-center flex-shrink-0 ${isChecked ? 'bg-emerald-500 border-emerald-500' : 'border-slate-300 dark:border-slate-600'}`}>
          {isChecked && <Check className="h-3 w-3 text-white" />}
        </div>
        <span className={isChecked ? 'line-through text-slate-400' : ''}>{content}</span>
      </li>
    );
  }
  
  return <li className="my-0.5" {...props}>{children}</li>;
};

export default function AtlasAI({ onBack }) {
  const { getAuthHeader } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const scrollRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const sendMessage = async (messageText) => {
    if (!messageText.trim()) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: messageText.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await axios.post(
        `${API}/atlas-ai/chat`,
        {
          message: messageText.trim(),
          session_id: sessionId
        },
        getAuthHeader()
      );

      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, aiMessage]);
      
      if (!sessionId) {
        setSessionId(response.data.session_id);
      }
    } catch (error) {
      console.error('Chat error:', error);
      toast.error('Failed to get response from Atlas AI');
      
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'I encountered an error. Please try again or contact support if the issue persists.',
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(inputValue);
  };

  const handleChipClick = (query) => {
    sendMessage(query);
  };

  const copyFullResponse = async (content) => {
    await navigator.clipboard.writeText(content);
    toast.success('Response copied to clipboard!');
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-slate-50 via-white to-slate-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      {/* Header */}
      <div className="flex-shrink-0 border-b border-slate-200/80 dark:border-slate-800/80 bg-white/90 dark:bg-slate-900/90 backdrop-blur-md">
        <div className="flex items-center gap-4 px-6 py-4">
          {onBack && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onBack}
              className="h-9 px-3 hover:bg-slate-100 dark:hover:bg-slate-800"
              data-testid="atlas-ai-back-btn"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
          )}
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="h-11 w-11 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                <Bot className="h-6 w-6 text-white" />
              </div>
              <div className="absolute -bottom-0.5 -right-0.5 h-3.5 w-3.5 bg-emerald-500 rounded-full border-2 border-white dark:border-slate-900 animate-pulse"></div>
            </div>
            <div>
              <h1 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
                Atlas AI
                <Sparkles className="h-4 w-4 text-amber-500" />
              </h1>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Your 24/7 Breeze assistant
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 overflow-hidden">
        <ScrollArea className="h-full" ref={scrollRef}>
          <div className="px-6 py-6 space-y-6 min-h-full max-w-4xl mx-auto">
            {messages.length === 0 ? (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex flex-col items-center justify-center py-12 text-center"
              >
                <div className="h-20 w-20 rounded-2xl bg-gradient-to-br from-cyan-500/10 to-blue-600/10 flex items-center justify-center mb-6 shadow-inner">
                  <Bot className="h-10 w-10 text-cyan-500" />
                </div>
                <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
                  How can I help?
                </h2>
                <p className="text-sm text-slate-500 dark:text-slate-400 max-w-md mb-8">
                  Ask about onboarding, sales scripts, underwriting, products, operations, or Breeze resources.
                </p>
                
                <div className="space-y-3 w-full max-w-lg">
                  <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">Try asking:</p>
                  <div className="grid gap-2">
                    {[
                      'What do I say in the first 2 minutes of an IUL call?',
                      'How do I book a 1-on-1 with Brandon?',
                      'What are the contracting steps?',
                      'Give me objection responses for "I need to think about it"'
                    ].map((example, idx) => (
                      <button
                        key={idx}
                        onClick={() => sendMessage(example)}
                        className="w-full text-left p-3.5 rounded-xl bg-white dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 text-sm text-slate-600 dark:text-slate-300 hover:bg-cyan-50 dark:hover:bg-cyan-950/30 hover:border-cyan-300 dark:hover:border-cyan-700 hover:text-cyan-700 dark:hover:text-cyan-300 transition-all shadow-sm hover:shadow"
                      >
                        "{example}"
                      </button>
                    ))}
                  </div>
                </div>
              </motion.div>
            ) : (
              <AnimatePresence mode="popLayout">
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    {message.role === 'assistant' && (
                      <div className="flex-shrink-0 h-9 w-9 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-md">
                        <Bot className="h-5 w-5 text-white" />
                      </div>
                    )}
                    <div
                      className={`max-w-[85%] ${
                        message.role === 'user'
                          ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-2xl rounded-tr-md px-4 py-3 shadow-md'
                          : message.isError
                          ? 'bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 rounded-2xl rounded-tl-md px-4 py-3'
                          : 'bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 rounded-2xl rounded-tl-md shadow-sm'
                      }`}
                    >
                      {message.role === 'assistant' ? (
                        <div className="relative group">
                          {/* Copy button for full response */}
                          <button
                            onClick={() => copyFullResponse(message.content)}
                            className="absolute -top-2 -right-2 opacity-0 group-hover:opacity-100 p-1.5 rounded-lg bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 transition-all shadow-sm"
                            title="Copy response"
                          >
                            <Copy className="h-3.5 w-3.5 text-slate-500" />
                          </button>
                          <div className="prose prose-sm dark:prose-invert max-w-none px-4 py-3 prose-headings:font-bold prose-headings:text-slate-800 dark:prose-headings:text-slate-100 prose-p:my-2 prose-ul:my-2 prose-ol:my-2 prose-li:my-0.5 prose-strong:text-slate-800 dark:prose-strong:text-slate-100">
                            <ReactMarkdown
                              remarkPlugins={[remarkGfm]}
                              components={{
                                code: ({ node, inline, className, children, ...props }) => {
                                  if (inline) {
                                    return <code className="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-700 text-cyan-600 dark:text-cyan-400 text-sm font-mono" {...props}>{children}</code>;
                                  }
                                  return <CodeBlock className={className}>{children}</CodeBlock>;
                                },
                                a: CustomLink,
                                blockquote: CustomBlockquote,
                                table: CustomTable,
                                thead: CustomThead,
                                th: CustomTh,
                                td: CustomTd,
                                li: CustomLi,
                                h1: ({ children }) => <h1 className="text-lg font-bold mt-4 mb-2 pb-1 border-b border-slate-200 dark:border-slate-700">{children}</h1>,
                                h2: ({ children }) => <h2 className="text-base font-bold mt-3 mb-2">{children}</h2>,
                                h3: ({ children }) => <h3 className="text-sm font-bold mt-2 mb-1">{children}</h3>,
                              }}
                            >
                              {message.content}
                            </ReactMarkdown>
                          </div>
                        </div>
                      ) : (
                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                      )}
                    </div>
                    {message.role === 'user' && (
                      <div className="flex-shrink-0 h-9 w-9 rounded-xl bg-slate-200 dark:bg-slate-700 flex items-center justify-center shadow-sm">
                        <User className="h-5 w-5 text-slate-600 dark:text-slate-300" />
                      </div>
                    )}
                  </motion.div>
                ))}
                {isLoading && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex gap-4 justify-start"
                  >
                    <div className="flex-shrink-0 h-9 w-9 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-md">
                      <Bot className="h-5 w-5 text-white" />
                    </div>
                    <div className="bg-white dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-2xl rounded-tl-md px-5 py-4 shadow-sm">
                      <div className="flex items-center gap-3">
                        <div className="flex gap-1">
                          <span className="w-2 h-2 bg-cyan-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                          <span className="w-2 h-2 bg-cyan-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                          <span className="w-2 h-2 bg-cyan-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                        </div>
                        <span className="text-sm text-slate-500 dark:text-slate-400">Thinking...</span>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            )}
          </div>
        </ScrollArea>
      </div>

      {/* Quick Chips */}
      {messages.length > 0 && (
        <div className="flex-shrink-0 px-6 py-2 border-t border-slate-200/80 dark:border-slate-800/80 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm">
          <div className="flex gap-2 overflow-x-auto pb-1 max-w-4xl mx-auto">
            {QUICK_CHIPS.map((chip) => (
              <button
                key={chip.label}
                onClick={() => handleChipClick(chip.query)}
                disabled={isLoading}
                className="flex-shrink-0 flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-cyan-100 dark:hover:bg-cyan-900/30 hover:text-cyan-700 dark:hover:text-cyan-400 transition-colors disabled:opacity-50 border border-transparent hover:border-cyan-200 dark:hover:border-cyan-800"
              >
                <chip.icon className="h-3 w-3" />
                {chip.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="flex-shrink-0 border-t border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900 px-6 py-4">
        <form onSubmit={handleSubmit} className="flex gap-3 max-w-4xl mx-auto">
          <Input
            ref={inputRef}
            type="text"
            placeholder="Ask Atlas AI anything..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={isLoading}
            className="flex-1 h-12 px-4 rounded-xl border-slate-200 dark:border-slate-700 focus:ring-2 focus:ring-cyan-500 focus:border-transparent bg-slate-50 dark:bg-slate-800/50"
            data-testid="atlas-ai-input"
          />
          <Button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="h-12 w-12 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 shadow-lg shadow-cyan-500/20 disabled:shadow-none"
            data-testid="atlas-ai-send-btn"
          >
            <Send className="h-5 w-5" />
          </Button>
        </form>
      </div>
    </div>
  );
}
