import { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { motion } from 'framer-motion';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { FileText, Clock, CheckCircle, XCircle, Eye, Plus, ArrowRight, AlertCircle, X } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';

const API = process.env.REACT_APP_BACKEND_URL;

const getAuthHeader = () => ({
  headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
});

const statusColors = {
  SUBMITTED: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  UNDER_REVIEW: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
  APPROVED: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
  DENIED: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  RESOLVED: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
};

export default function MyTickets() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [detailOpen, setDetailOpen] = useState(false);
  
  // Submit ticket state
  const [submitOpen, setSubmitOpen] = useState(false);
  const [step, setStep] = useState(1);
  const [ticketType, setTicketType] = useState('');
  const [affectedAgentId, setAffectedAgentId] = useState('');
  const [affectedAgent, setAffectedAgent] = useState(null);
  const [requestedUplineId, setRequestedUplineId] = useState('');
  const [requestedCommission, setRequestedCommission] = useState('');
  const [reasonText, setReasonText] = useState('');
  const [acknowledged, setAcknowledged] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [agents, setAgents] = useState([]);
  const [allUsers, setAllUsers] = useState([]);
  const [uplines, setUplines] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    fetchCurrentUser();
    fetchTickets();
  }, []);

  useEffect(() => {
    if (currentUser) {
      fetchAgents();
    }
  }, [currentUser]);

  const fetchCurrentUser = async () => {
    try {
      const response = await axios.get(`${API}/api/auth/me`, getAuthHeader());
      setCurrentUser(response.data);
    } catch (error) {
      console.error('Failed to get current user');
    }
  };

  const fetchTickets = async () => {
    try {
      const response = await axios.get(`${API}/api/tickets`, getAuthHeader());
      setTickets(response.data);
    } catch (error) {
      toast.error('Failed to load tickets');
    } finally {
      setLoading(false);
    }
  };

  const fetchAgents = async () => {
    try {
      // Admins can see all users, others see their downline
      const isAdmin = currentUser?.role === 'admin';
      const endpoint = isAdmin ? `${API}/api/admin/users` : `${API}/api/hierarchy/downline`;
      const response = await axios.get(endpoint, getAuthHeader());
      
      setAllUsers(response.data);
      // Filter out admins from selectable agents, and exclude self
      setAgents(response.data.filter(u => u.role !== 'admin' && u.id !== currentUser?.id));
    } catch (error) {
      console.error('Failed to load agents:', error);
    }
  };

  useEffect(() => {
    if (affectedAgentId) {
      const agent = agents.find(a => a.id === affectedAgentId);
      setAffectedAgent(agent);
      
      if (ticketType === 'HIERARCHY_MOVE' && agent) {
        setUplines(allUsers.filter(a => a.id !== affectedAgentId && a.comp_percentage > agent.comp_percentage));
      }
    }
  }, [affectedAgentId, ticketType, agents, allUsers]);

  const viewDetail = (ticket) => {
    setSelectedTicket(ticket);
    setDetailOpen(true);
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    });
  };

  const getTicketTypeLabel = (type) => {
    const labels = {
      COMMISSION_CHANGE: 'Commission Change',
      HIERARCHY_MOVE: 'Hierarchy Move',
      REINSTATEMENT: 'Reinstatement'
    };
    return labels[type] || type;
  };

  const resetSubmitForm = () => {
    setStep(1);
    setTicketType('');
    setAffectedAgentId('');
    setAffectedAgent(null);
    setRequestedUplineId('');
    setRequestedCommission('');
    setReasonText('');
    setAcknowledged(false);
  };

  const openSubmitDialog = () => {
    resetSubmitForm();
    setSubmitOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!acknowledged) {
      toast.error('Please acknowledge the terms');
      return;
    }

    setSubmitting(true);
    try {
      await axios.post(`${API}/api/tickets`, {
        ticket_type: ticketType,
        affected_agent_id: affectedAgentId,
        requested_upline_id: ticketType === 'HIERARCHY_MOVE' ? requestedUplineId : (ticketType === 'REINSTATEMENT' ? requestedUplineId : null),
        requested_commission_level: ['COMMISSION_CHANGE', 'REINSTATEMENT'].includes(ticketType) ? parseFloat(requestedCommission) : null,
        reason_text: reasonText
      }, getAuthHeader());

      toast.success('Ticket submitted successfully');
      setSubmitOpen(false);
      resetSubmitForm();
      fetchTickets();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to submit ticket');
    } finally {
      setSubmitting(false);
    }
  };

  const ticketTypes = [
    {
      id: 'COMMISSION_CHANGE',
      title: 'Commission Change',
      description: 'Request a change to an agent\'s commission level',
      icon: FileText,
      color: 'cyan'
    },
    {
      id: 'HIERARCHY_MOVE',
      title: 'Hierarchy Move',
      description: 'Move an agent to a different upline',
      icon: ArrowRight,
      color: 'violet'
    },
    {
      id: 'REINSTATEMENT',
      title: 'Reinstatement',
      description: 'Request to reinstate a deactivated agent',
      icon: CheckCircle,
      color: 'emerald'
    }
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="h-8 w-1 bg-gradient-to-b from-cyan-500 to-blue-500 rounded-full" />
          <div>
            <h1 className="text-xl font-bold text-slate-900 dark:text-white">Tickets</h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">Submit and track your requests</p>
          </div>
        </div>
        <Button onClick={openSubmitDialog} className="bg-gradient-to-r from-cyan-500 to-blue-500" data-testid="submit-ticket-btn">
          <Plus className="h-4 w-4 mr-2" />
          Submit New Ticket
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Total', value: tickets.length, icon: FileText, color: 'slate' },
          { label: 'Pending', value: tickets.filter(t => t.status === 'SUBMITTED' || t.status === 'UNDER_REVIEW').length, icon: Clock, color: 'amber' },
          { label: 'Approved', value: tickets.filter(t => t.status === 'APPROVED' || t.status === 'RESOLVED').length, icon: CheckCircle, color: 'emerald' },
          { label: 'Denied', value: tickets.filter(t => t.status === 'DENIED').length, icon: XCircle, color: 'red' }
        ].map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label}>
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-slate-500 uppercase">{stat.label}</span>
                  <Icon className={`h-4 w-4 text-${stat.color}-500`} />
                </div>
                <div className="text-2xl font-bold">{stat.value}</div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Tickets List */}
      {loading ? (
        <Card><CardContent className="p-8 text-center text-slate-500">Loading...</CardContent></Card>
      ) : tickets.length === 0 ? (
        <Card>
          <CardContent className="p-8 text-center">
            <FileText className="h-10 w-10 text-slate-300 mx-auto mb-3" />
            <p className="text-slate-500">No tickets submitted yet</p>
            <Button onClick={openSubmitDialog} size="sm" className="mt-4">
              Submit Your First Ticket
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {tickets.map((ticket) => (
            <motion.div key={ticket.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
              <Card className="hover:border-cyan-500/50 transition-colors">
                <CardContent className="p-4">
                  <div className="flex flex-col sm:flex-row sm:items-center gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2 flex-wrap">
                        <span className="font-semibold">{getTicketTypeLabel(ticket.ticket_type)}</span>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${statusColors[ticket.status]}`}>
                          {ticket.status.replace('_', ' ')}
                        </span>
                      </div>
                      <div className="text-sm text-slate-600 dark:text-slate-300">
                        Agent: {ticket.affected_agent_name}
                      </div>
                      <div className="text-xs text-slate-500 mt-1">
                        Submitted {formatDate(ticket.created_at)}
                      </div>
                    </div>
                    <Button size="sm" variant="outline" onClick={() => viewDetail(ticket)}>
                      <Eye className="h-4 w-4 mr-1" />View
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}

      {/* View Detail Dialog */}
      <Dialog open={detailOpen} onOpenChange={setDetailOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Ticket Details</DialogTitle>
          </DialogHeader>
          {selectedTicket && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-xs text-slate-500 uppercase mb-1">Type</div>
                  <div className="font-medium">{getTicketTypeLabel(selectedTicket.ticket_type)}</div>
                </div>
                <div>
                  <div className="text-xs text-slate-500 uppercase mb-1">Status</div>
                  <span className={`text-xs px-2 py-1 rounded-full ${statusColors[selectedTicket.status]}`}>
                    {selectedTicket.status.replace('_', ' ')}
                  </span>
                </div>
              </div>

              <div>
                <div className="text-xs text-slate-500 uppercase mb-1">Affected Agent</div>
                <div>{selectedTicket.affected_agent_name}</div>
              </div>

              {selectedTicket.requested_commission_level && (
                <div>
                  <div className="text-xs text-slate-500 uppercase mb-1">Requested Commission</div>
                  <div>{selectedTicket.current_commission_level}% → {selectedTicket.requested_commission_level}%</div>
                </div>
              )}

              {selectedTicket.requested_upline_name && (
                <div>
                  <div className="text-xs text-slate-500 uppercase mb-1">Requested Upline</div>
                  <div>{selectedTicket.current_upline_name || 'None'} → {selectedTicket.requested_upline_name}</div>
                </div>
              )}

              <div>
                <div className="text-xs text-slate-500 uppercase mb-1">Reason</div>
                <div className="text-sm whitespace-pre-wrap">{selectedTicket.reason_text}</div>
              </div>

              {selectedTicket.admin_resolution_notes && (
                <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/50">
                  <div className="text-xs text-slate-500 uppercase mb-2">Admin Resolution</div>
                  <div className="text-sm whitespace-pre-wrap">{selectedTicket.admin_resolution_notes}</div>
                  {selectedTicket.resolved_by_admin_name && (
                    <div className="text-xs text-slate-500 mt-2">
                      Resolved by {selectedTicket.resolved_by_admin_name} on {formatDate(selectedTicket.resolved_at)}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Submit Ticket Dialog */}
      <Dialog open={submitOpen} onOpenChange={setSubmitOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Submit a Ticket</DialogTitle>
          </DialogHeader>

          {step === 1 && (
            <div className="space-y-4">
              <p className="text-sm text-slate-500">Select the type of request:</p>
              <div className="grid grid-cols-1 gap-3">
                {ticketTypes.map((type) => {
                  const Icon = type.icon;
                  return (
                    <div
                      key={type.id}
                      className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                        ticketType === type.id
                          ? 'border-cyan-500 bg-cyan-50 dark:bg-cyan-950/40'
                          : 'border-slate-200 dark:border-slate-700 hover:border-cyan-300'
                      }`}
                      onClick={() => {
                        setTicketType(type.id);
                        setStep(2);
                      }}
                      data-testid={`ticket-type-${type.id.toLowerCase()}`}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg bg-${type.color}-100 dark:bg-${type.color}-950/30`}>
                          <Icon className={`h-5 w-5 text-${type.color}-600 dark:text-${type.color}-400`} />
                        </div>
                        <div>
                          <h3 className="font-semibold text-slate-900 dark:text-white">{type.title}</h3>
                          <p className="text-xs text-slate-500">{type.description}</p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {step === 2 && (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-cyan-600">{getTicketTypeLabel(ticketType)}</span>
                <Button type="button" variant="ghost" size="sm" onClick={() => setStep(1)}>
                  <X className="h-4 w-4 mr-1" /> Change Type
                </Button>
              </div>

              {/* Agent Selection */}
              <div className="space-y-1">
                <Label>Agent {ticketType === 'HIERARCHY_MOVE' ? 'Being Moved' : 'Affected'} *</Label>
                <select
                  value={affectedAgentId}
                  onChange={(e) => setAffectedAgentId(e.target.value)}
                  required
                  className="w-full h-10 px-3 rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900"
                  data-testid="affected-agent-select"
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
                <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50">
                  <h4 className="text-xs font-medium mb-2 text-slate-500">Current Information</h4>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-slate-500">Commission:</span> {affectedAgent.comp_percentage}%
                    </div>
                    <div>
                      <span className="text-slate-500">Upline:</span> {allUsers.find(u => u.id === affectedAgent.upline_id)?.name || 'None'}
                    </div>
                    {affectedAgent.upline_id && (
                      <div className="col-span-2">
                        <span className="text-slate-500">Upline Commission:</span> {allUsers.find(a => a.id === affectedAgent.upline_id)?.comp_percentage || 'N/A'}%
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Commission Change Fields */}
              {ticketType === 'COMMISSION_CHANGE' && affectedAgent && (
                <div className="space-y-1">
                  <Label>Requested New Commission Level *</Label>
                  {(() => {
                    const upline = allUsers.find(a => a.id === affectedAgent.upline_id);
                    const maxCommission = upline ? upline.comp_percentage - 5 : 130;
                    const options = [];
                    for (let i = 75; i <= maxCommission; i += 5) {
                      options.push(i);
                    }
                    return (
                      <>
                        <select
                          value={requestedCommission}
                          onChange={(e) => setRequestedCommission(e.target.value)}
                          required
                          className="w-full h-10 px-3 rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900"
                          data-testid="requested-commission"
                        >
                          <option value="">Select Commission Level</option>
                          {options.map(level => (
                            <option key={level} value={level}>
                              {level}%
                            </option>
                          ))}
                        </select>
                        <p className="text-xs text-slate-500 mt-1">
                          Options range from 75% to {maxCommission}% (5% below upline's {upline?.comp_percentage || 'N/A'}%)
                        </p>
                      </>
                    );
                  })()}
                </div>
              )}

              {/* Hierarchy Move Fields */}
              {ticketType === 'HIERARCHY_MOVE' && affectedAgent && (
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
                      {allUsers.filter(u => u.role !== 'admin').map(agent => (
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

              {/* Reason Field */}
              <div className="space-y-1">
                <Label>Reason / Context *</Label>
                <Textarea
                  value={reasonText}
                  onChange={(e) => setReasonText(e.target.value)}
                  required
                  rows={3}
                  placeholder="Please provide detailed context for this request..."
                  data-testid="reason-text"
                />
              </div>

              {/* Acknowledgement */}
              <div className="flex items-start gap-3 p-3 rounded-lg border border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-950/20">
                <input
                  type="checkbox"
                  checked={acknowledged}
                  onChange={(e) => setAcknowledged(e.target.checked)}
                  className="mt-1"
                  data-testid="acknowledge-checkbox"
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
                data-testid="submit-ticket-form-btn"
              >
                {submitting ? 'Submitting...' : 'Submit Ticket'}
              </Button>
            </form>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
