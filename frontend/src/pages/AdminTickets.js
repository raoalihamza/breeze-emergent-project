import { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { motion } from 'framer-motion';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { FileText, Clock, CheckCircle, XCircle, Filter } from 'lucide-react';
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

export default function AdminTickets() {
  const [tickets, setTickets] = useState([]);
  const [filteredTickets, setFilteredTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [detailOpen, setDetailOpen] = useState(false);
  
  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  
  const [actionStatus, setActionStatus] = useState('');
  const [resolutionNotes, setResolutionNotes] = useState('');
  const [finalCommission, setFinalCommission] = useState('');
  const [finalUplineId, setFinalUplineId] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchTickets();
  }, []);

  useEffect(() => {
    let filtered = tickets;
    if (statusFilter !== 'all') {
      filtered = filtered.filter(t => t.status === statusFilter);
    }
    if (typeFilter !== 'all') {
      filtered = filtered.filter(t => t.ticket_type === typeFilter);
    }
    setFilteredTickets(filtered);
  }, [tickets, statusFilter, typeFilter]);

  const fetchTickets = async () => {
    try {
      console.log('Fetching tickets from:', `${API}/api/tickets`);
      const response = await axios.get(`${API}/api/tickets`, getAuthHeader());
      console.log('Tickets response:', response.data);
      setTickets(response.data);
      setFilteredTickets(response.data);
    } catch (error) {
      console.error('Failed to load tickets:', error);
      toast.error('Failed to load tickets');
    } finally {
      setLoading(false);
    }
  };

  const viewDetail = (ticket) => {
    setSelectedTicket(ticket);
    setActionStatus('');
    setResolutionNotes('');
    setFinalCommission(ticket.requested_commission_level || '');
    setFinalUplineId(ticket.requested_upline_id || '');
    setDetailOpen(true);
  };

  const handleAction = async () => {
    if (!actionStatus) {
      toast.error('Please select an action');
      return;
    }
    
    if (['DENIED', 'RESOLVED'].includes(actionStatus) && !resolutionNotes) {
      toast.error('Resolution notes required');
      return;
    }

    setSubmitting(true);
    try {
      await axios.put(`${API}/api/tickets/${selectedTicket.id}/status`, {
        status: actionStatus,
        admin_resolution_notes: resolutionNotes,
        final_commission_level: finalCommission ? parseFloat(finalCommission) : null,
        final_upline_id: finalUplineId || null
      }, getAuthHeader());

      toast.success(`Ticket ${actionStatus.toLowerCase()}`);
      setDetailOpen(false);
      fetchTickets();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Action failed');
    } finally {
      setSubmitting(false);
    }
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

  return (
    <div className="max-w-7xl mx-auto space-y-5">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="h-8 w-1 bg-gradient-to-b from-cyan-500 to-blue-500 rounded-full" />
        <div>
          <h1 className="text-xl font-bold text-slate-900 dark:text-white">Tickets Management</h1>
          <p className="text-xs text-slate-500 dark:text-slate-400">Admin-only governance workflow</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        {[
          { label: 'Total', value: tickets.length, icon: FileText, color: 'slate' },
          { label: 'Submitted', value: tickets.filter(t => t.status === 'SUBMITTED').length, icon: Clock, color: 'blue' },
          { label: 'Under Review', value: tickets.filter(t => t.status === 'UNDER_REVIEW').length, icon: Clock, color: 'amber' },
          { label: 'Resolved', value: tickets.filter(t => t.status === 'RESOLVED').length, icon: CheckCircle, color: 'emerald' },
          { label: 'Denied', value: tickets.filter(t => t.status === 'DENIED').length, icon: XCircle, color: 'red' }
        ].map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label}>
              <CardContent className="p-3">
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

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-4 flex-wrap">
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-slate-500" />
              <span className="text-sm font-medium">Filters:</span>
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="h-9 px-3 rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm"
            >
              <option value="all">All Status</option>
              <option value="SUBMITTED">Submitted</option>
              <option value="UNDER_REVIEW">Under Review</option>
              <option value="APPROVED">Approved</option>
              <option value="DENIED">Denied</option>
              <option value="RESOLVED">Resolved</option>
            </select>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="h-9 px-3 rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm"
            >
              <option value="all">All Types</option>
              <option value="COMMISSION_CHANGE">Commission Change</option>
              <option value="HIERARCHY_MOVE">Hierarchy Move</option>
              <option value="REINSTATEMENT">Reinstatement</option>
            </select>
            <span className="text-sm text-slate-500 ml-auto">{filteredTickets.length} tickets</span>
          </div>
        </CardContent>
      </Card>

      {/* Tickets List */}
      {loading ? (
        <Card><CardContent className="p-8 text-center text-slate-500">Loading...</CardContent></Card>
      ) : filteredTickets.length === 0 ? (
        <Card>
          <CardContent className="p-8 text-center">
            <FileText className="h-10 w-10 text-slate-300 mx-auto mb-3" />
            <p className="text-slate-500">No tickets found</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {filteredTickets.map((ticket) => (
            <motion.div key={ticket.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
              <Card className="hover:border-cyan-500/50 transition-colors cursor-pointer" onClick={() => viewDetail(ticket)}>
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
                        Agent: {ticket.affected_agent_name} | Submitted by: {ticket.submitted_by_agent_name}
                      </div>
                      <div className="text-xs text-slate-500 mt-1">
                        {formatDate(ticket.created_at)}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}

      {/* Detail & Action Dialog */}
      <Dialog open={detailOpen} onOpenChange={setDetailOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Ticket Review & Action</DialogTitle>
          </DialogHeader>
          {selectedTicket && (
            <div className="space-y-4">
              {/* Ticket Info */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-xs text-slate-500 uppercase mb-1">Type</div>
                  <div className="font-medium">{getTicketTypeLabel(selectedTicket.ticket_type)}</div>
                </div>
                <div>
                  <div className="text-xs text-slate-500 uppercase mb-1">Current Status</div>
                  <span className={`text-xs px-2 py-1 rounded-full ${statusColors[selectedTicket.status]}`}>
                    {selectedTicket.status.replace('_', ' ')}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-xs text-slate-500 uppercase mb-1">Submitted By</div>
                  <div>{selectedTicket.submitted_by_agent_name}</div>
                </div>
                <div>
                  <div className="text-xs text-slate-500 uppercase mb-1">Affected Agent</div>
                  <div>{selectedTicket.affected_agent_name}</div>
                </div>
              </div>

              {selectedTicket.requested_commission_level && (
                <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/50">
                  <div className="text-xs text-slate-500 uppercase mb-2">Commission Change Request</div>
                  <div className="text-lg font-semibold">{selectedTicket.current_commission_level}% → {selectedTicket.requested_commission_level}%</div>
                </div>
              )}

              {selectedTicket.requested_upline_name && (
                <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/50">
                  <div className="text-xs text-slate-500 uppercase mb-2">Hierarchy Move Request</div>
                  <div className="text-lg font-semibold">{selectedTicket.current_upline_name || 'None'} → {selectedTicket.requested_upline_name}</div>
                </div>
              )}

              <div>
                <div className="text-xs text-slate-500 uppercase mb-1">Reason</div>
                <div className="text-sm whitespace-pre-wrap p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50">{selectedTicket.reason_text}</div>
              </div>

              {/* Admin Actions */}
              {selectedTicket.status !== 'RESOLVED' && selectedTicket.status !== 'DENIED' && (
                <div className="border-t pt-4 space-y-4">
                  <h3 className="font-semibold">Admin Action</h3>
                  
                  <div className="space-y-1">
                    <Label>Action *</Label>
                    <select
                      value={actionStatus}
                      onChange={(e) => setActionStatus(e.target.value)}
                      className="w-full h-10 px-3 rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900"
                    >
                      <option value="">Select Action</option>
                      <option value="UNDER_REVIEW">Mark Under Review</option>
                      <option value="APPROVED">Approve</option>
                      <option value="DENIED">Deny</option>
                      <option value="RESOLVED">Resolve (Apply Changes)</option>
                    </select>
                  </div>

                  {['RESOLVED', 'APPROVED'].includes(actionStatus) && selectedTicket.requested_commission_level && (
                    <div className="space-y-1">
                      <Label>Final Commission Level (%)</Label>
                      <Input
                        type="number"
                        step="0.01"
                        value={finalCommission}
                        onChange={(e) => setFinalCommission(e.target.value)}
                        placeholder={selectedTicket.requested_commission_level}
                      />
                    </div>
                  )}

                  {['DENIED', 'RESOLVED'].includes(actionStatus) && (
                    <div className="space-y-1">
                      <Label>Resolution Notes *</Label>
                      <Textarea
                        value={resolutionNotes}
                        onChange={(e) => setResolutionNotes(e.target.value)}
                        rows={4}
                        placeholder="Explain your decision..."
                      />
                    </div>
                  )}

                  <Button
                    onClick={handleAction}
                    disabled={!actionStatus || submitting}
                    className="w-full bg-gradient-to-r from-cyan-500 to-blue-500"
                  >
                    {submitting ? 'Processing...' : 'Submit Action'}
                  </Button>
                </div>
              )}

              {/* Previous Resolution */}
              {selectedTicket.admin_resolution_notes && (
                <div className="p-4 rounded-lg bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800">
                  <div className="text-xs text-slate-500 uppercase mb-2">Resolution</div>
                  <div className="text-sm whitespace-pre-wrap mb-2">{selectedTicket.admin_resolution_notes}</div>
                  {selectedTicket.resolved_by_admin_name && (
                    <div className="text-xs text-slate-500">
                      By {selectedTicket.resolved_by_admin_name} on {formatDate(selectedTicket.resolved_at)}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
