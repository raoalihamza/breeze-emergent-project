import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { TrendingUp, X } from 'lucide-react';
import { toast } from 'sonner';
import { motion } from 'framer-motion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function ActivityTracker() {
  const navigate = useNavigate();
  const { getAuthHeader } = useAuth();
  const [kpiDate, setKpiDate] = useState(new Date().toISOString().split('T')[0]);
  const [dialsMade, setDialsMade] = useState('');
  const [contactsMade, setContactsMade] = useState('');
  const [appointmentsSet, setAppointmentsSet] = useState('');
  const [presentationsGiven, setPresentationsGiven] = useState('');
  const [salesMade, setSalesMade] = useState('');
  const [kpiHistory, setKpiHistory] = useState([]);

  useEffect(() => {
    fetchKPIHistory();
  }, []);

  const fetchKPIHistory = async () => {
    try {
      const response = await axios.get(`${API}/kpi`, getAuthHeader());
      setKpiHistory(response.data);
      const todayEntry = response.data.find(k => k.date === kpiDate);
      if (todayEntry) {
        setDialsMade(todayEntry.dials_made.toString());
        setContactsMade(todayEntry.contacts_made.toString());
        setAppointmentsSet(todayEntry.appointments_set.toString());
        setPresentationsGiven(todayEntry.presentations_given.toString());
        setSalesMade(todayEntry.sales_made.toString());
      }
    } catch (error) {
      console.error('Failed to load KPI history:', error);
    }
  };

  const saveKPI = async () => {
    try {
      await axios.post(`${API}/kpi`, {
        date: kpiDate,
        dials_made: parseInt(dialsMade) || 0,
        contacts_made: parseInt(contactsMade) || 0,
        appointments_set: parseInt(appointmentsSet) || 0,
        presentations_given: parseInt(presentationsGiven) || 0,
        sales_made: parseInt(salesMade) || 0
      }, getAuthHeader());
      toast.success('KPI saved!');
      fetchKPIHistory();
    } catch (error) {
      toast.error('Failed to save');
    }
  };

  const loadKpiForDate = (date) => {
    setKpiDate(date);
    const entry = kpiHistory.find(k => k.date === date);
    if (entry) {
      setDialsMade(entry.dials_made.toString());
      setContactsMade(entry.contacts_made.toString());
      setAppointmentsSet(entry.appointments_set.toString());
      setPresentationsGiven(entry.presentations_given.toString());
      setSalesMade(entry.sales_made.toString());
    } else {
      setDialsMade('');
      setContactsMade('');
      setAppointmentsSet('');
      setPresentationsGiven('');
      setSalesMade('');
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
            <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600">
              <TrendingUp className="h-6 w-6 text-white" />
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white">Daily Activity Tracker</h1>
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
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 mb-6">
              <Label className="text-sm font-medium">Select Date:</Label>
              <Input
                type="date"
                value={kpiDate}
                onChange={(e) => loadKpiForDate(e.target.value)}
                className="h-9 w-full sm:w-48"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
              {[
                { label: 'Dials', value: dialsMade, setter: setDialsMade },
                { label: 'Contacts', value: contactsMade, setter: setContactsMade },
                { label: 'Appts Set', value: appointmentsSet, setter: setAppointmentsSet },
                { label: 'Presentations', value: presentationsGiven, setter: setPresentationsGiven },
                { label: 'Sales', value: salesMade, setter: setSalesMade }
              ].map((field, i) => (
                <div key={i} className="space-y-2">
                  <Label className="text-xs font-medium">{field.label}</Label>
                  <Input
                    type="number"
                    min="0"
                    value={field.value}
                    onChange={(e) => field.setter(e.target.value)}
                  />
                </div>
              ))}
            </div>

            <Button onClick={saveKPI} className="w-full sm:w-auto bg-gradient-to-r from-blue-500 to-indigo-600">
              Save Entry
            </Button>

            {kpiHistory.length > 0 && (
              <div className="mt-6 pt-6 border-t border-slate-200 dark:border-slate-700">
                <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">Recent Entries</h4>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {kpiHistory.slice(0, 7).map((entry) => (
                    <div key={entry.id} className="flex flex-wrap items-center gap-2 sm:gap-4 py-2 px-3 sm:px-4 rounded-xl bg-slate-50 dark:bg-slate-800 text-xs sm:text-sm">
                      <span className="font-medium w-20 sm:w-24">{new Date(entry.date).toLocaleDateString()}</span>
                      <span className="text-slate-500">D:{entry.dials_made}</span>
                      <span className="text-slate-500">C:{entry.contacts_made}</span>
                      <span className="text-slate-500">A:{entry.appointments_set}</span>
                      <span className="text-slate-500">P:{entry.presentations_given}</span>
                      <span className="font-bold text-emerald-600 dark:text-emerald-400 ml-auto">Sales: {entry.sales_made}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
}
