import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Calculator, X } from 'lucide-react';
import { toast } from 'sonner';
import { motion } from 'framer-motion';

const ResultItem = ({ label, value, highlight, green }) => (
  <div className={`p-2 rounded-lg ${highlight ? 'bg-cyan-100 dark:bg-cyan-900/50' : green ? 'bg-emerald-100 dark:bg-emerald-900/50' : 'bg-slate-100 dark:bg-slate-800'}`}>
    <div className="text-[10px] text-slate-500 dark:text-slate-400 uppercase tracking-wider">{label}</div>
    <div className={`text-sm font-bold ${highlight ? 'text-cyan-700 dark:text-cyan-300' : green ? 'text-emerald-700 dark:text-emerald-300' : 'text-slate-700 dark:text-slate-300'}`}>{value}</div>
  </div>
);

export default function CommissionCalculator() {
  const navigate = useNavigate();
  const [iulCompLevel, setIulCompLevel] = useState('');
  const [iulAP, setIulAP] = useState('');
  const [iulTP, setIulTP] = useState('');
  const [iulResults, setIulResults] = useState(null);
  const [termCompLevel, setTermCompLevel] = useState('');
  const [termAP, setTermAP] = useState('');
  const [termResults, setTermResults] = useState(null);

  const calculateIUL = () => {
    const compPercent = parseFloat(iulCompLevel) / 100;
    const ap = parseFloat(iulAP);
    const tp = parseFloat(iulTP);
    if (!compPercent || !ap || !tp) {
      toast.error('Please fill all IUL fields');
      return;
    }
    const lesserOf = Math.min(ap, tp);
    const totalFirstYear = lesserOf * compPercent;
    const advance9Month = Math.min(totalFirstYear * 0.75, 3500);
    setIulResults({
      totalFirstYear: totalFirstYear.toFixed(2),
      advance9Month: advance9Month.toFixed(2),
      asEarned: (totalFirstYear - advance9Month).toFixed(2),
      lesserOf: lesserOf.toFixed(2)
    });
  };

  const calculateTerm = () => {
    const compPercent = parseFloat(termCompLevel) / 100;
    const ap = parseFloat(termAP);
    if (!compPercent || !ap) {
      toast.error('Please fill all Term/FEX fields');
      return;
    }
    const totalFirstYear = ap * compPercent;
    const advance9Month = Math.min(totalFirstYear * 0.75, 3500);
    setTermResults({
      totalFirstYear: totalFirstYear.toFixed(2),
      advance9Month: advance9Month.toFixed(2),
      asEarned: (totalFirstYear - advance9Month).toFixed(2)
    });
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
            <div className="p-3 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600">
              <Calculator className="h-6 w-6 text-white" />
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white">Commission Calculator</h1>
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
            <Tabs defaultValue="iul">
              <TabsList className="mb-6 bg-slate-100 dark:bg-slate-800 p-1 w-full sm:w-auto">
                <TabsTrigger value="iul" className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-700 flex-1 sm:flex-none">IUL</TabsTrigger>
                <TabsTrigger value="term" className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-700 flex-1 sm:flex-none">Term/FEX</TabsTrigger>
              </TabsList>

              <TabsContent value="iul" className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label className="text-xs font-medium">Comp Level (%)</Label>
                    <Input type="number" placeholder="75" value={iulCompLevel} onChange={(e) => setIulCompLevel(e.target.value)} />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs font-medium">Annual Premium</Label>
                    <Input type="number" placeholder="10000" value={iulAP} onChange={(e) => setIulAP(e.target.value)} />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs font-medium">Target Premium</Label>
                    <Input type="number" placeholder="8000" value={iulTP} onChange={(e) => setIulTP(e.target.value)} />
                  </div>
                </div>
                <Button onClick={calculateIUL} className="w-full sm:w-auto bg-gradient-to-r from-emerald-500 to-teal-600">
                  Calculate
                </Button>
                {iulResults && (
                  <div className="grid grid-cols-2 gap-3 p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800">
                    <ResultItem label="Lesser of AP & TP" value={`$${iulResults.lesserOf}`} />
                    <ResultItem label="Total First Year" value={`$${iulResults.totalFirstYear}`} highlight />
                    <ResultItem label="9-Month Advance" value={`$${iulResults.advance9Month}`} green />
                    <ResultItem label="As-Earned (10-12)" value={`$${iulResults.asEarned}`} />
                  </div>
                )}
              </TabsContent>

              <TabsContent value="term" className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label className="text-xs font-medium">Comp Level (%)</Label>
                    <Input type="number" placeholder="100" value={termCompLevel} onChange={(e) => setTermCompLevel(e.target.value)} />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-xs font-medium">Annual Premium</Label>
                    <Input type="number" placeholder="5000" value={termAP} onChange={(e) => setTermAP(e.target.value)} />
                  </div>
                </div>
                <Button onClick={calculateTerm} className="w-full sm:w-auto bg-gradient-to-r from-emerald-500 to-teal-600">
                  Calculate
                </Button>
                {termResults && (
                  <div className="grid grid-cols-3 gap-3 p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800">
                    <ResultItem label="Total First Year" value={`$${termResults.totalFirstYear}`} highlight />
                    <ResultItem label="9-Month Advance" value={`$${termResults.advance9Month}`} green />
                    <ResultItem label="As-Earned" value={`$${termResults.asEarned}`} />
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
}
