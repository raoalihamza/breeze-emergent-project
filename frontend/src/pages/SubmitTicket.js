import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { motion } from 'framer-motion';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { FileText, AlertCircle, CheckCircle, ArrowRight } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

const getAuthHeader = () => ({
  headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
});

export default function SubmitTicket() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [ticketType, setTicketType] = useState('');
  const [affectedAgentId, setAffectedAgentId] = useState('');
  const [affectedAgent, setAffectedAgent] = useState(null);
  const [requestedUplineId, setRequestedUplineId] = useState('');
  const [requestedCommission, setRequestedCommission] = useState('');
  const [effectiveDate, setEffectiveDate] = useState('');
  const [reasonText, setReasonText] = useState('');
  const [acknowledged, setAcknowledged] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  
  const [agents, setAgents] = useState([]);
  const [uplines, setUplines] = useState([]);

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await axios.get(`${API}/users`, getAuthHeader());
      setAgents(response.data.filter(u => u.role !== 'admin'));
    } catch (error) {
      toast.error('Failed to load agents');
    }
  };

  useEffect(() => {
    if (affectedAgentId) {
      const agent = agents.find(a => a.id === affectedAgentId);
      setAffectedAgent(agent);
      
      // For hierarchy moves, filter uplines with higher commission
      if (ticketType === 'HIERARCHY_MOVE' && agent) {
        setUplines(agents.filter(a => a.id !== affectedAgentId && a.comp_percentage > agent.comp_percentage));
      }
    }
  }, [affectedAgentId, ticketType, agents]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!acknowledged) {
      toast.error('Please acknowledge the terms');
      return;
    }

    setSubmitting(true);
    try {
      await axios.post(`${API}/tickets`, {
        ticket_type: ticketType,
        affected_agent_id: affectedAgentId,
        requested_upline_id: ticketType === 'HIERARCHY_MOVE' ? requestedUplineId : null,
        requested_commission_level: ticketType === 'COMMISSION_CHANGE' ? parseFloat(requestedCommission) : null,
        effective_date: effectiveDate,
        reason_text: reasonText
      }, getAuthHeader());

      toast.success('Ticket submitted successfully');
      navigate('/my-tickets');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to submit ticket');
    } finally {
      setSubmitting(false);
    }
  };

  const ticketTypes = [
    {
      id: 'COMMISSION_CHANGE',
      title: 'Commission Change Request',
      description: 'Request a change to an agent\'s commission level',
      icon: FileText,
      color: 'cyan'
    },
    {
      id: 'HIERARCHY_MOVE',
      title: 'Hierarchy Move Request',
      description: 'Move an agent to a different upline',
      icon: ArrowRight,
      color: 'violet'
    },
    {
      id: 'REINSTATEMENT',
      title: 'Agent Reinstatement',
      description: 'Request to reinstate a deactivated agent',
      icon: CheckCircle,
      color: 'emerald'
    }
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-5">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="h-8 w-1 bg-gradient-to-b from-cyan-500 to-blue-500 rounded-full" />
        <div>
          <h1 className="text-xl font-bold text-slate-900 dark:text-white">Submit a Ticket</h1>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            For commission, hierarchy, or reinstatement requests only
          </p>
        </div>
      </div>

      {step === 1 && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
          <h2 className="text-lg font-semibold">Step 1: Select Ticket Type</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {ticketTypes.map((type) => {
              const Icon = type.icon;
              return (
                <Card
                  key={type.id}
                  className={`cursor-pointer transition-all ${
                    ticketType === type.id
                      ? 'border-cyan-500 bg-cyan-50 dark:bg-cyan-950/40'
                      : 'border-slate-200 dark:border-slate-800 hover:border-cyan-300'
                  }`}
                  onClick={() => {
                    setTicketType(type.id);
                    setStep(2);
                  }}
                >
                  <CardContent className="p-6">
                    <div className={`p-3 rounded-lg bg-${type.color}-50 dark:bg-${type.color}-950/30 w-fit mb-3`}>
                      <Icon className={`h-6 w-6 text-${type.color}-600 dark:text-${type.color}-400`} />
                    </div>
                    <h3 className="font-semibold mb-2">{type.title}</h3>
                    <p className="text-sm text-slate-500 dark:text-slate-400">{type.description}</p>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </motion.div>
      )}

      {step === 2 && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold">Step 2: Request Details</h2>
                <Button variant="outline" size="sm" onClick={() => setStep(1)}>
                  Back
                </Button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Agent Selection */}
                <div className="space-y-1">
                  <Label>Agent {ticketType === 'HIERARCHY_MOVE' ? 'Being Moved' : 'Affected'} *</Label>
                  <select
                    value={affectedAgentId}
                    onChange={(e) => setAffectedAgentId(e.target.value)}
                    required
                    className="w-full h-10 px-3 rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900"
                  >
                    <option value="">Select Agent</option>
                    {agents.map(agent => (
                      <option key={agent.id} value={agent.id}>
                        {agent.name} ({agent.comp_percentage}%)
                      </option>
                    ))}
                  </select>
                </div>

                {/* Current Info Display */}
                {affectedAgent && (
                  <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/50">
                    <h4 className="text-sm font-medium mb-2">Current Information</h4>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <span className="text-slate-500">Commission:</span> {affectedAgent.comp_percentage}%
                      </div>
                      <div>
                        <span className="text-slate-500">Upline:</span> {affectedAgent.upline_name || 'None'}
                      </div>
                    </div>
                  </div>
                )}

                {/* Commission Change Fields */}
                {ticketType === 'COMMISSION_CHANGE' && (
                  <div className="space-y-1">
                    <Label>Requested New Commission Level (%) *</Label>
                    <Input
                      type="number"
                      step="0.01"
                      value={requestedCommission}
                      onChange={(e) => setRequestedCommission(e.target.value)}
                      required
                      placeholder="85.00"
                    />
                  </div>
                )}

                {/* Hierarchy Move Fields */}
                {ticketType === 'HIERARCHY_MOVE' && affectedAgent && (
                  <>
                    <div className="space-y-1">
                      <Label>Requested New Upline *</Label>
                      <select
                        value={requestedUplineId}
                        onChange={(e) => setRequestedUplineId(e.target.value)}
                        required
                        className="w-full h-10 px-3 rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900"
                      >
                        <option value="">Select Upline</option>
                        {uplines.map(upline => (
                          <option key={upline.id} value={upline.id}>
                            {upline.name} ({upline.comp_percentage}%)
                          </option>
                        ))}
                      </select>
                      <p className="text-xs text-slate-500 mt-1">
                        Only showing uplines with higher commission than {affectedAgent.comp_percentage}%
                      </p>
                    </div>
                  </>
                )}

                {/* Reinstatement Fields */}
                {ticketType === 'REINSTATEMENT' && (
                  <>
                    <div className="space-y-1">
                      <Label>Requested Upline Placement *</Label>
                      <select
                        value={requestedUplineId}
                        onChange={(e) => setRequestedUplineId(e.target.value)}
                        required
                        className="w-full h-10 px-3 rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900"
                      >
                        <option value="">Select Upline</option>
                        {agents.map(agent => (
                          <option key={agent.id} value={agent.id}>
                            {agent.name} ({agent.comp_percentage}%)
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="space-y-1">
                      <Label>Requested Commission Level (%) *</Label>
                      <Input
                        type="number"
                        step="0.01"
                        value={requestedCommission}
                        onChange={(e) => setRequestedCommission(e.target.value)}
                        required
                        placeholder="75.00"
                      />
                    </div>
                  </>
                )}

                {/* Common Fields */}
                <div className="space-y-1">
                  <Label>Effective Date *</Label>
                  <Input
                    type="date"
                    value={effectiveDate}
                    onChange={(e) => setEffectiveDate(e.target.value)}
                    required
                  />
                </div>

                <div className="space-y-1">
                  <Label>Reason / Context *</Label>
                  <Textarea
                    value={reasonText}
                    onChange={(e) => setReasonText(e.target.value)}
                    required
                    rows={4}
                    placeholder="Please provide detailed context for this request..."
                  />
                </div>

                {/* Acknowledgement */}
                <div className="flex items-start gap-3 p-4 rounded-lg border border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-950/20">
                  <input
                    type="checkbox"
                    checked={acknowledged}
                    onChange={(e) => setAcknowledged(e.target.checked)}
                    className="mt-1"
                  />
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <AlertCircle className="h-4 w-4 text-amber-600 dark:text-amber-400" />
                      <span className="font-medium text-sm">Acknowledgement Required</span>
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-300">
                      I understand this request is subject to Admin approval and may be denied.
                    </p>
                  </div>
                </div>

                {/* Submit Button */}
                <Button
                  type="submit"
                  className="w-full bg-gradient-to-r from-cyan-500 to-blue-500"
                  disabled={submitting || !acknowledged}
                >
                  {submitting ? 'Submitting...' : 'Submit Ticket'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  );
}
