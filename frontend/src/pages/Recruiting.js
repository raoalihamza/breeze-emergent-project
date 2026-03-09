import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Copy, Check, Mail, Clock, UserPlus, Users, CheckCircle, XCircle, Shield, Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import { motion } from 'framer-motion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function Recruiting() {
  const { user, getAuthHeader } = useAuth();
  const [invites, setInvites] = useState([]);
  const [adminInvites, setAdminInvites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [adminOpen, setAdminOpen] = useState(false);
  const [recruitEmail, setRecruitEmail] = useState('');
  const [recruitFirstName, setRecruitFirstName] = useState('');
  const [recruitLastName, setRecruitLastName] = useState('');
  const [recruitNpn, setRecruitNpn] = useState('');
  const [confirmNpn, setConfirmNpn] = useState('');
  const [compPercentage, setCompPercentage] = useState('');
  const [message, setMessage] = useState('');
  const [creating, setCreating] = useState(false);
  const [copiedToken, setCopiedToken] = useState(null);
  
  // Admin invite state
  const [adminEmail, setAdminEmail] = useState('');
  const [adminFirstName, setAdminFirstName] = useState('');
  const [adminLastName, setAdminLastName] = useState('');
  const [adminMessage, setAdminMessage] = useState('');
  const [creatingAdmin, setCreatingAdmin] = useState(false);
  
  const isAdmin = user?.role === 'admin';
  
  const getCompOptions = () => {
    const maxComp = user?.comp_percentage ? user.comp_percentage - 5 : 95;
    const options = [];
    for (let i = 75; i <= maxComp; i += 5) {
      options.push(i);
    }
    return options;
  };

  useEffect(() => { fetchInvites(); }, []);

  const fetchInvites = async () => {
    try {
      const [invitesRes, adminInvitesRes] = await Promise.all([
        axios.get(`${API}/invites`, getAuthHeader()),
        isAdmin ? axios.get(`${API}/admin-invites`, getAuthHeader()) : Promise.resolve({ data: [] })
      ]);
      setInvites(invitesRes.data);
      setAdminInvites(adminInvitesRes.data);
    } catch (error) {
      toast.error('Failed to load invites');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateInvite = async (e) => {
    e.preventDefault();
    if (!recruitEmail || !recruitFirstName || !recruitLastName || !recruitNpn || !compPercentage) {
      toast.error('Please fill in all required fields'); return;
    }
    if (recruitNpn !== confirmNpn) {
      toast.error('NPN values do not match'); return;
    }
    
    setCreating(true);
    try {
      const response = await axios.post(`${API}/invites`, {
        recruit_email: recruitEmail,
        recruit_first_name: recruitFirstName,
        recruit_last_name: recruitLastName,
        recruit_npn: recruitNpn,
        comp_percentage: parseFloat(compPercentage),
        message: message || null
      }, getAuthHeader());
      toast.success('Invite created!');
      setInvites([response.data, ...invites]);
      setOpen(false);
      setRecruitEmail(''); setRecruitFirstName(''); setRecruitLastName('');
      setRecruitNpn(''); setConfirmNpn(''); setCompPercentage(''); setMessage('');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create invite');
    } finally {
      setCreating(false);
    }
  };

  const handleCreateAdminInvite = async (e) => {
    e.preventDefault();
    if (!adminEmail || !adminFirstName || !adminLastName) {
      toast.error('Please fill in all required fields'); return;
    }
    
    setCreatingAdmin(true);
    try {
      const response = await axios.post(`${API}/admin-invites`, {
        email: adminEmail,
        first_name: adminFirstName,
        last_name: adminLastName,
        message: adminMessage || null
      }, getAuthHeader());
      toast.success('Admin invite created!');
      setAdminInvites([response.data, ...adminInvites]);
      setAdminOpen(false);
      setAdminEmail(''); setAdminFirstName(''); setAdminLastName(''); setAdminMessage('');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create admin invite');
    } finally {
      setCreatingAdmin(false);
    }
  };

  const copyInviteLink = async (token, isAdminInvite = false) => {
    const path = isAdminInvite ? 'admin-signup' : 'signup';
    const link = `${window.location.origin}/${path}/${token}`;
    try {
      await navigator.clipboard.writeText(link);
      setCopiedToken(token);
      toast.success('Invite link copied!');
    } catch (err) {
      const textArea = document.createElement('textarea');
      textArea.value = link;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      document.body.appendChild(textArea);
      textArea.select();
      try {
        document.execCommand('copy');
        setCopiedToken(token);
        toast.success('Invite link copied!');
      } catch (fallbackErr) {
        toast.error('Failed to copy');
      }
      document.body.removeChild(textArea);
    }
    setTimeout(() => setCopiedToken(null), 2000);
  };

  const handleCancelInvite = async (inviteId, inviteName) => {
    if (!confirm(`Are you sure you want to cancel the invite for ${inviteName}?`)) {
      return;
    }

    try {
      await axios.delete(`${API}/invites/${inviteId}`, getAuthHeader());
      toast.success('Invite cancelled successfully');
      fetchInvites(); // Refresh the list
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to cancel invite');
    }
  };

  const stats = {
    total: invites.length,
    pending: invites.filter(i => i.status === 'pending').length,
    accepted: invites.filter(i => i.status === 'accepted').length
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-2 border-cyan-500 border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-5" data-testid="recruiting-page">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="flex items-center gap-3">
          <div className="h-8 w-1 bg-gradient-to-b from-cyan-500 to-blue-500 rounded-full"></div>
          <div>
            <h1 className="text-xl font-bold text-slate-900 dark:text-white">Recruiting</h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">Invite new agents to join your team</p>
          </div>
        </motion.div>

        <div className="flex items-center gap-2">
          {/* Admin Invite Button - Admin Only */}
          {isAdmin && (
            <Dialog open={adminOpen} onOpenChange={setAdminOpen}>
              <DialogTrigger asChild>
                <Button size="sm" variant="outline" className="h-9 border-violet-300 dark:border-violet-700 text-violet-600 dark:text-violet-400 hover:bg-violet-50 dark:hover:bg-violet-950/30" data-testid="create-admin-invite-button">
                  <Shield className="h-4 w-4 mr-1.5" />Invite Admin
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-md">
                <DialogHeader>
                  <DialogTitle className="text-base flex items-center gap-2">
                    <Shield className="h-4 w-4 text-violet-500" />
                    Invite New Admin
                  </DialogTitle>
                </DialogHeader>
                <form onSubmit={handleCreateAdminInvite} className="space-y-3" data-testid="create-admin-invite-form">
                  <div className="p-3 rounded-lg bg-violet-50 dark:bg-violet-950/30 border border-violet-200 dark:border-violet-800">
                    <p className="text-xs text-violet-700 dark:text-violet-300">This will create an invite link for a new admin with full system access.</p>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1">
                      <Label className="text-xs">First Name</Label>
                      <Input value={adminFirstName} onChange={(e) => setAdminFirstName(e.target.value)} required className="h-9" data-testid="admin-first-name-input" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-xs">Last Name</Label>
                      <Input value={adminLastName} onChange={(e) => setAdminLastName(e.target.value)} required className="h-9" data-testid="admin-last-name-input" />
                    </div>
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Email Address</Label>
                    <Input type="email" value={adminEmail} onChange={(e) => setAdminEmail(e.target.value)} required className="h-9" data-testid="admin-email-input" />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Message (optional)</Label>
                    <Input value={adminMessage} onChange={(e) => setAdminMessage(e.target.value)} placeholder="Welcome message..." className="h-9" />
                  </div>
                  <Button 
                    type="submit" 
                    className="w-full bg-gradient-to-r from-violet-500 to-purple-500" 
                    disabled={creatingAdmin || !adminEmail || !adminFirstName || !adminLastName}
                    data-testid="submit-admin-invite-button"
                  >
                    {creatingAdmin ? 'Creating...' : 'Create Admin Invite'}
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          )}

          {/* Agent Invite Button */}
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button size="sm" className="h-9 bg-gradient-to-r from-cyan-500 to-blue-500 text-white" data-testid="create-invite-button">
                <UserPlus className="h-4 w-4 mr-1.5" />Create Invite
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md max-h-[85vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle className="text-base">Create Invite Link</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleCreateInvite} className="space-y-3" data-testid="create-invite-form">
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label className="text-xs">First Name <span className="text-slate-400">(license)</span></Label>
                    <Input value={recruitFirstName} onChange={(e) => setRecruitFirstName(e.target.value)} required className="h-9" data-testid="recruit-first-name-input" />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Last Name <span className="text-slate-400">(license)</span></Label>
                    <Input value={recruitLastName} onChange={(e) => setRecruitLastName(e.target.value)} required className="h-9" data-testid="recruit-last-name-input" />
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Email Address</Label>
                  <Input type="email" value={recruitEmail} onChange={(e) => setRecruitEmail(e.target.value)} required className="h-9" data-testid="recruit-email-input" />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label className="text-xs">NPN</Label>
                    <Input value={recruitNpn} onChange={(e) => setRecruitNpn(e.target.value)} placeholder="12345678" required className="h-9" data-testid="recruit-npn-input" />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Confirm NPN</Label>
                    <Input 
                      value={confirmNpn} 
                      onChange={(e) => setConfirmNpn(e.target.value)} 
                      placeholder="Re-enter" 
                      required 
                      className={`h-9 ${recruitNpn && confirmNpn && recruitNpn !== confirmNpn ? 'border-red-500' : ''}`}
                      data-testid="confirm-npn-input" 
                    />
                  </div>
                </div>
                {recruitNpn && confirmNpn && recruitNpn !== confirmNpn && (
                  <p className="text-xs text-red-500">NPN values do not match</p>
                )}
                <div className="space-y-1">
                  <Label className="text-xs">Commission %</Label>
                  <Select value={compPercentage} onValueChange={setCompPercentage}>
                    <SelectTrigger className="h-9" data-testid="comp-percentage-select">
                      <SelectValue placeholder="Select level" />
                    </SelectTrigger>
                    <SelectContent>
                      {getCompOptions().map((comp) => (
                        <SelectItem key={comp} value={comp.toString()}>{comp}%</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <p className="text-[10px] text-slate-400">Range: 75% - {user?.comp_percentage ? user.comp_percentage - 5 : 95}%</p>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Message (optional)</Label>
                  <Input value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Welcome message..." className="h-9" data-testid="message-input" />
                </div>
                <Button 
                  type="submit" 
                  className="w-full bg-gradient-to-r from-cyan-500 to-blue-500" 
                  disabled={creating || !recruitEmail || !recruitFirstName || !recruitLastName || !recruitNpn || !confirmNpn || recruitNpn !== confirmNpn || !compPercentage}
                  data-testid="submit-invite-button"
                >
                  {creating ? 'Creating...' : 'Create Invite'}
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-3 gap-3">
        <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Total Invites</span>
              <div className="p-1.5 rounded-lg bg-cyan-50 dark:bg-cyan-950/30">
                <Users className="h-3.5 w-3.5 text-cyan-600 dark:text-cyan-400" />
              </div>
            </div>
            <div className="text-2xl font-bold text-slate-900 dark:text-white">{stats.total}</div>
          </CardContent>
        </Card>
        <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Pending</span>
              <div className="p-1.5 rounded-lg bg-amber-50 dark:bg-amber-950/30">
                <Clock className="h-3.5 w-3.5 text-amber-600 dark:text-amber-400" />
              </div>
            </div>
            <div className="text-2xl font-bold text-slate-900 dark:text-white">{stats.pending}</div>
          </CardContent>
        </Card>
        <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Accepted</span>
              <div className="p-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/30">
                <CheckCircle className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" />
              </div>
            </div>
            <div className="text-2xl font-bold text-slate-900 dark:text-white">{stats.accepted}</div>
          </CardContent>
        </Card>
      </div>

      {/* Admin Invites Section - Admin Only */}
      {isAdmin && adminInvites.length > 0 && (
        <Card className="border-violet-200 dark:border-violet-800/50 bg-gradient-to-r from-violet-50 to-purple-50 dark:from-violet-950/20 dark:to-purple-950/20">
          <CardContent className="p-4">
            <h3 className="text-sm font-semibold text-violet-900 dark:text-violet-100 mb-3 flex items-center gap-2">
              <Shield className="h-4 w-4 text-violet-500" />Admin Invites
              <span className="text-[10px] bg-violet-200 dark:bg-violet-800 text-violet-700 dark:text-violet-300 px-1.5 py-0.5 rounded-full ml-auto">{adminInvites.length}</span>
            </h3>
            
            <div className="space-y-2">
              {adminInvites.map((invite, index) => (
                <motion.div
                  key={invite.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.03 }}
                  className="p-3 sm:p-4 rounded-lg bg-white dark:bg-slate-900 border border-violet-200 dark:border-violet-800"
                  data-testid={`admin-invite-item-${invite.id}`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                    {/* Left: Icon + Info */}
                    <div className="flex items-start gap-3 flex-1 min-w-0">
                      <div className={`p-2 rounded-lg flex-shrink-0 ${
                        invite.status === 'accepted' 
                          ? 'bg-emerald-50 dark:bg-emerald-950/30' 
                          : 'bg-violet-50 dark:bg-violet-950/30'
                      }`}>
                        {invite.status === 'accepted' ? (
                          <CheckCircle className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                        ) : (
                          <Shield className="h-4 w-4 text-violet-600 dark:text-violet-400" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        {/* Name + Status Badge */}
                        <div className="flex flex-wrap items-center gap-2 mb-1">
                          <span className="font-semibold text-base text-slate-900 dark:text-white">
                            {invite.first_name} {invite.last_name}
                          </span>
                          <span className={`text-[10px] px-2 py-1 rounded-full font-medium whitespace-nowrap ${
                            invite.status === 'accepted' 
                              ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' 
                              : 'bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-400'
                          }`}>
                            {invite.status}
                          </span>
                        </div>
                        {/* Email + Date - Stack on mobile */}
                        <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-3 text-xs text-slate-500 dark:text-slate-400">
                          <span className="truncate">{invite.email}</span>
                          <span className="text-[11px]">{new Date(invite.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                    
                    {/* Right: Action Buttons */}
                    {invite.status === 'pending' && (
                      <div className="flex items-center gap-2 sm:flex-shrink-0 w-full sm:w-auto">
                        <Button
                          variant="outline"
                          size="sm"
                          className="flex-1 sm:flex-initial h-9 text-xs border-violet-300 dark:border-violet-700"
                          onClick={() => copyInviteLink(invite.token, true)}
                        >
                          {copiedToken === invite.token ? (
                            <><Check className="h-3.5 w-3.5 sm:mr-1" /><span className="hidden sm:inline ml-1">Copied</span></>
                          ) : (
                            <><Copy className="h-3.5 w-3.5 sm:mr-1" /><span className="hidden sm:inline ml-1">Copy</span></>
                          )}
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          className="flex-1 sm:flex-initial h-9 text-xs border-red-300 dark:border-red-700 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30"
                          onClick={() => handleCancelInvite(invite.id, invite.name)}
                          data-testid={`cancel-admin-invite-${invite.id}`}
                        >
                          <Trash2 className="h-3.5 w-3.5 sm:mr-1" /><span className="hidden sm:inline ml-1">Cancel</span>
                        </Button>
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Agent Invite List */}
      <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
        <CardContent className="p-4">
          <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
            <Mail className="h-4 w-4 text-cyan-500" />Agent Invites
          </h3>
          
          {invites && invites.length > 0 ? (
            <div className="space-y-2">
              {invites.map((invite, index) => (
                <motion.div
                  key={invite.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.03 }}
                  className="p-3 sm:p-4 rounded-lg border border-slate-200 dark:border-slate-700 hover:border-cyan-500/30 transition-colors"
                  data-testid={`invite-item-${invite.id}`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-center gap-3">
                    {/* Left: Icon + Info */}
                    <div className="flex items-start gap-3 flex-1 min-w-0">
                      <div className={`p-2 rounded-lg flex-shrink-0 ${
                        invite.status === 'accepted' 
                          ? 'bg-emerald-50 dark:bg-emerald-950/30' 
                          : invite.status === 'pending'
                          ? 'bg-amber-50 dark:bg-amber-950/30'
                          : 'bg-red-50 dark:bg-red-950/30'
                      }`}>
                        {invite.status === 'accepted' ? (
                          <CheckCircle className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                        ) : invite.status === 'pending' ? (
                          <Clock className="h-4 w-4 text-amber-600 dark:text-amber-400" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-600 dark:text-red-400" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        {/* Name + Status Badge */}
                        <div className="flex flex-wrap items-center gap-2 mb-1">
                          <span className="font-semibold text-base text-slate-900 dark:text-white">
                            {invite.recruit_first_name && invite.recruit_last_name 
                              ? `${invite.recruit_first_name} ${invite.recruit_last_name}`
                              : invite.recruit_name || 'Unknown'
                            }
                          </span>
                          <span className={`text-[10px] px-2 py-1 rounded-full font-medium whitespace-nowrap ${
                            invite.status === 'accepted' 
                              ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' 
                              : invite.status === 'pending'
                              ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
                              : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                          }`}>
                            {invite.status}
                          </span>
                        </div>
                        {/* Email + NPN + Comp + Date - Wrap on mobile */}
                        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-500 dark:text-slate-400">
                          <span className="truncate max-w-[200px]">{invite.recruit_email}</span>
                          {invite.recruit_npn && (
                            <span className="font-mono bg-slate-100 dark:bg-slate-800 px-1.5 py-0.5 rounded text-[10px] whitespace-nowrap">
                              NPN: {invite.recruit_npn}
                            </span>
                          )}
                          <span className="font-medium text-cyan-600 dark:text-cyan-400 whitespace-nowrap">{invite.comp_percentage}%</span>
                          <span className="text-[11px] whitespace-nowrap">{new Date(invite.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                    
                    {/* Right: Action Buttons */}
                    {invite.status === 'pending' && (
                      <div className="flex items-center gap-2 sm:flex-shrink-0 w-full sm:w-auto">
                        <Button
                          variant="outline"
                          size="sm"
                          className="flex-1 sm:flex-initial h-9 text-xs"
                          onClick={() => copyInviteLink(invite.token)}
                          data-testid={`copy-invite-link-${invite.id}`}
                        >
                          {copiedToken === invite.token ? (
                            <><Check className="h-3.5 w-3.5 sm:mr-1" /><span className="hidden sm:inline ml-1">Copied</span></>
                          ) : (
                            <><Copy className="h-3.5 w-3.5 sm:mr-1" /><span className="hidden sm:inline ml-1">Copy</span></>
                          )}
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          className="flex-1 sm:flex-initial h-9 text-xs border-red-300 dark:border-red-700 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30"
                          onClick={() => handleCancelInvite(
                            invite.id, 
                            invite.recruit_first_name && invite.recruit_last_name 
                              ? `${invite.recruit_first_name} ${invite.recruit_last_name}`
                              : invite.recruit_name || 'this recruit'
                          )}
                          data-testid={`cancel-invite-${invite.id}`}
                        >
                          <Trash2 className="h-3.5 w-3.5 sm:mr-1" /><span className="hidden sm:inline ml-1">Cancel</span>
                        </Button>
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <UserPlus className="h-10 w-10 mx-auto text-slate-300 dark:text-slate-600 mb-3" />
              <p className="text-sm text-slate-500 dark:text-slate-400">No invites yet. Create your first invite to start recruiting.</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
