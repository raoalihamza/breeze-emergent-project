import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription } from '../components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  Users, Plus, Search, Mail, Phone, Calendar, Send, Eye, 
  Copy, Check, Clock, FileText, Upload, Trash2, Shield,
  ExternalLink, MoreHorizontal, UserCheck, UserX, Edit, Save, X, ChevronDown
} from 'lucide-react';
import { toast } from 'sonner';
import { motion } from 'framer-motion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function MyClients() {
  const { getAuthHeader, user } = useAuth();
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [carriers, setCarriers] = useState([]);
  
  // Create client modal
  const [createOpen, setCreateOpen] = useState(false);
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [submitting, setSubmitting] = useState(false);
  
  // Invite modal
  const [inviteOpen, setInviteOpen] = useState(false);
  const [selectedClient, setSelectedClient] = useState(null);
  const [inviteLink, setInviteLink] = useState('');
  const [copied, setCopied] = useState(false);
  const [sendingEmail, setSendingEmail] = useState(false);
  
  // Client detail modal
  const [detailOpen, setDetailOpen] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [editFirstName, setEditFirstName] = useState('');
  const [editLastName, setEditLastName] = useState('');
  const [editEmail, setEditEmail] = useState('');
  const [editPhone, setEditPhone] = useState('');
  const [updating, setUpdating] = useState(false);
  const [clientPolicies, setClientPolicies] = useState([]);
  const [clientDocuments, setClientDocuments] = useState([]);
  
  // Add policy modal
  const [addPolicyOpen, setAddPolicyOpen] = useState(false);
  const [policyCarrier, setPolicyCarrier] = useState('');
  const [policyType, setPolicyType] = useState('');
  const [policyNumber, setPolicyNumber] = useState('');
  const [policyPremium, setPolicyPremium] = useState('');
  const [submittingPolicy, setSubmittingPolicy] = useState(false);
  
  // Add document modal
  const [addDocumentOpen, setAddDocumentOpen] = useState(false);
  const [documentFile, setDocumentFile] = useState(null);
  const [documentType, setDocumentType] = useState('Policy');
  const [documentName, setDocumentName] = useState('');
  const [submittingDocument, setSubmittingDocument] = useState(false);

  // Quick action modal (upload policy + email invite)
  const [quickActionOpen, setQuickActionOpen] = useState(false);
  const [policyFile, setPolicyFile] = useState(null);
  const [uploadingPolicy, setUploadingPolicy] = useState(false);

  useEffect(() => {
    fetchClients();
    fetchCarriers();
  }, []);

  const fetchClients = async () => {
    try {
      const response = await axios.get(`${API}/portal/clients`, getAuthHeader());
      setClients(response.data);
    } catch (error) {
      toast.error('Failed to load clients');
    } finally {
      setLoading(false);
    }
  };

  const fetchCarriers = async () => {
    try {
      const response = await axios.get(`${API}/carriers`, getAuthHeader());
      setCarriers(response.data);
    } catch (error) {
      console.error('Failed to load carriers');
    }
  };

  const handleCreateClient = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    
    try {
      const response = await axios.post(`${API}/portal/clients`, {
        first_name: firstName,
        last_name: lastName,
        email: email,
        phone: phone || null
      }, getAuthHeader());
      
      toast.success('Client created successfully');
      setClients([response.data, ...clients]);
      resetCreateForm();
      setCreateOpen(false);
      
      // Ask if they want to send invite
      setSelectedClient(response.data);
      handleGenerateInvite(response.data.id);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create client');
    } finally {
      setSubmitting(false);
    }
  };

  const handleGenerateInvite = async (clientId) => {
    try {
      const response = await axios.post(`${API}/portal/clients/${clientId}/invite`, {}, getAuthHeader());
      const baseUrl = window.location.origin;
      const link = `${baseUrl}/client-portal/setup/${response.data.invite_token}`;
      setInviteLink(link);
      setInviteOpen(true);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to generate invite');
    }
  };

  const handleCopyLink = () => {
    navigator.clipboard.writeText(inviteLink);
    setCopied(true);
    toast.success('Link copied to clipboard');
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSendInviteEmail = async () => {
    if (!selectedClient) return;
    
    setSendingEmail(true);
    try {
      await axios.post(
        `${API}/portal/clients/${selectedClient.id}/send-invite-email`,
        {},
        getAuthHeader()
      );
      toast.success(`Invite email sent to ${selectedClient.email}`);
      setInviteOpen(false);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to send email');
    } finally {
      setSendingEmail(false);
    }
  };

  const handleQuickUploadAndEmail = async () => {
    if (!policyFile) {
      toast.error('Please attach a policy PDF');
      return;
    }
    
    setUploadingPolicy(true);
    try {
      // Upload the policy document
      const formData = new FormData();
      formData.append('file', policyFile);
      formData.append('document_type', 'Policy');
      formData.append('file_name', policyFile.name);
      
      await axios.post(
        `${API}/portal/clients/${selectedClient.id}/documents`,
        formData,
        {
          ...getAuthHeader(),
          headers: {
            ...getAuthHeader().headers,
            'Content-Type': 'multipart/form-data',
          }
        }
      );
      
      toast.success('Policy uploaded successfully');
      
      // Now send the invite email
      await axios.post(
        `${API}/portal/clients/${selectedClient.id}/send-invite-email`,
        {},
        getAuthHeader()
      );
      
      toast.success(`Portal invite sent to ${selectedClient.email}`);
      
      // Refresh client documents if we're viewing details
      if (detailOpen && selectedClient) {
        const docsRes = await axios.get(`${API}/portal/documents/client/${selectedClient.id}`, getAuthHeader());
        setClientDocuments(docsRes.data);
      }
      
      setPolicyFile(null);
      setQuickActionOpen(false);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to complete action');
    } finally {
      setUploadingPolicy(false);
    }
  };

  const handleViewClient = async (client) => {
    setSelectedClient(client);
    setEditFirstName(client.first_name);
    setEditLastName(client.last_name);
    setEditEmail(client.email);
    setEditPhone(client.phone || '');
    setEditMode(false);
    setDetailOpen(true);
    
    try {
      const [policiesRes, docsRes] = await Promise.all([
        axios.get(`${API}/portal/policies/client/${client.id}`, getAuthHeader()),
        axios.get(`${API}/portal/documents/client/${client.id}`, getAuthHeader())
      ]);
      setClientPolicies(policiesRes.data);
      setClientDocuments(docsRes.data);
    } catch (error) {
      console.error('Failed to load client details');
    }
  };

  const handleUpdateClient = async () => {
    setUpdating(true);
    try {
      const response = await axios.put(
        `${API}/portal/clients/${selectedClient.id}`,
        {
          first_name: editFirstName,
          last_name: editLastName,
          email: editEmail,
          phone: editPhone || null
        },
        getAuthHeader()
      );
      
      toast.success('Client updated successfully');
      setClients(clients.map(c => c.id === selectedClient.id ? response.data : c));
      setSelectedClient(response.data);
      setEditMode(false);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update client');
    } finally {
      setUpdating(false);
    }
  };

  const handleDeleteClient = async (clientId) => {
    if (!window.confirm('Delete this client and all their data? This cannot be undone.')) return;
    
    try {
      await axios.delete(`${API}/portal/clients/${clientId}`, getAuthHeader());
      toast.success('Client deleted');
      setClients(clients.filter(c => c.id !== clientId));
      setDetailOpen(false);
    } catch (error) {
      toast.error('Failed to delete client');
    }
  };

  const resetCreateForm = () => {
    setFirstName('');
    setLastName('');
    setEmail('');
    setPhone('');
  };
  
  const handleAddPolicy = async (e) => {
    e.preventDefault();
    setSubmittingPolicy(true);
    
    try {
      const response = await axios.post(`${API}/portal/clients/${selectedClient.id}/policies`, {
        carrier: policyCarrier,
        product_type: policyType,
        policy_number: policyNumber,
        monthly_premium: policyPremium ? parseFloat(policyPremium) : null,
        premium: policyPremium ? parseFloat(policyPremium) * 12 : null,
        is_visible: true
      }, getAuthHeader());
      
      toast.success('Policy added successfully');
      setClientPolicies([...clientPolicies, response.data]);
      setPolicyCarrier('');
      setPolicyType('');
      setPolicyNumber('');
      setPolicyPremium('');
      setAddPolicyOpen(false);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add policy');
    } finally {
      setSubmittingPolicy(false);
    }
  };
  
  const handleAddDocument = async (e) => {
    e.preventDefault();
    setSubmittingDocument(true);
    
    try {
      const formData = new FormData();
      formData.append('file', documentFile);
      formData.append('document_type', documentType);
      formData.append('file_name', documentName || documentFile.name);
      
      const response = await axios.post(
        `${API}/portal/clients/${selectedClient.id}/documents`,
        formData,
        {
          ...getAuthHeader(),
          headers: {
            ...getAuthHeader().headers,
            'Content-Type': 'multipart/form-data',
          }
        }
      );
      
      toast.success('Document uploaded successfully');
      setClientDocuments([...clientDocuments, response.data]);
      setDocumentFile(null);
      setDocumentType('Policy');
      setDocumentName('');
      setAddDocumentOpen(false);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to upload document');
    } finally {
      setSubmittingDocument(false);
    }
  };

  const filteredClients = clients.filter(c => {
    const matchesSearch = !searchTerm || 
      `${c.first_name} ${c.last_name}`.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.email?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || c.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status) => {
    switch (status) {
      case 'active':
        return <span className="px-2 py-0.5 text-xs rounded-full bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">Active</span>;
      case 'invited':
        return <span className="px-2 py-0.5 text-xs rounded-full bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">Invited</span>;
      case 'inactive':
        return <span className="px-2 py-0.5 text-xs rounded-full bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">Inactive</span>;
      default:
        return <span className="px-2 py-0.5 text-xs rounded-full bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">{status}</span>;
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Never';
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-2 border-cyan-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-5" data-testid="my-clients-page">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="flex items-center gap-3">
          <div className="h-8 w-1 bg-gradient-to-b from-cyan-500 to-blue-500 rounded-full" />
          <div>
            <h1 className="text-xl font-bold text-slate-900 dark:text-white">Client Portal</h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">Manage your clients' portal access</p>
          </div>
        </motion.div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3">
        <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Total</span>
              <Users className="h-4 w-4 text-cyan-500" />
            </div>
            <div className="text-2xl font-bold text-slate-900 dark:text-white">{clients.length}</div>
          </CardContent>
        </Card>
        <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Active</span>
              <UserCheck className="h-4 w-4 text-emerald-500" />
            </div>
            <div className="text-2xl font-bold text-slate-900 dark:text-white">{clients.filter(c => c.status === 'active').length}</div>
          </CardContent>
        </Card>
        <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Pending</span>
              <Clock className="h-4 w-4 text-amber-500" />
            </div>
            <div className="text-2xl font-bold text-slate-900 dark:text-white">{clients.filter(c => c.status === 'invited').length}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-2">
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <Input
            placeholder="Search clients..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9 h-9 bg-white dark:bg-slate-900"
            data-testid="search-clients"
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[130px] h-9 bg-white dark:bg-slate-900">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="invited">Invited</SelectItem>
            <SelectItem value="inactive">Inactive</SelectItem>
          </SelectContent>
        </Select>
        <span className="text-xs text-slate-500 ml-auto">{filteredClients.length} clients</span>
      </div>

      {/* Client List */}
      {filteredClients.length === 0 ? (
        <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
          <CardContent className="py-12 text-center">
            <Users className="h-10 w-10 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
            <p className="text-slate-500 dark:text-slate-400">
              {searchTerm || statusFilter !== 'all' ? 'No clients match filters' : 'No portal clients yet'}
            </p>
            {!searchTerm && statusFilter === 'all' && (
              <p className="text-xs text-slate-400 mt-2">
                Create a client to give them access to their portal.
              </p>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {filteredClients.map((client, index) => (
            <motion.div
              key={client.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.03 }}
              data-testid={`portal-client-${client.id}`}
            >
              <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50 hover:border-cyan-500/30 transition-colors">
                <CardContent className="p-4">
                  <div className="flex items-center gap-4">
                    {/* Avatar */}
                    <div className="h-10 w-10 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center flex-shrink-0">
                      <span className="text-white font-semibold text-sm">
                        {client.first_name?.[0]}{client.last_name?.[0]}
                      </span>
                    </div>

                    {/* Client Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-slate-900 dark:text-white truncate">
                          {client.first_name} {client.last_name}
                        </h3>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setSelectedClient(client);
                            setQuickActionOpen(true);
                          }}
                          className="h-5 w-5 p-0 hover:bg-cyan-100 dark:hover:bg-cyan-900/30"
                          title="Quick Actions"
                        >
                          <ChevronDown className="h-3.5 w-3.5 text-cyan-600 dark:text-cyan-400" />
                        </Button>
                        {getStatusBadge(client.status)}
                      </div>
                      <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
                        <span className="flex items-center gap-1">
                          <Mail className="h-3 w-3" />
                          {client.email}
                        </span>
                        {client.phone && (
                          <span className="flex items-center gap-1">
                            <Phone className="h-3 w-3" />
                            {client.phone}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Last Login */}
                    <div className="text-right flex-shrink-0 hidden sm:block">
                      <p className="text-xs text-slate-400">Last login</p>
                      <p className="text-sm font-medium text-slate-600 dark:text-slate-300">
                        {formatDate(client.last_login_at)}
                      </p>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-1 flex-shrink-0">
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        onClick={() => handleViewClient(client)}
                        className="h-8 w-8 p-0"
                        title="View Details"
                      >
                        <Eye className="h-3.5 w-3.5" />
                      </Button>
                      {client.status !== 'active' && (
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          onClick={() => {
                            setSelectedClient(client);
                            handleGenerateInvite(client.id);
                          }}
                          className="h-8 w-8 p-0 text-cyan-600 hover:text-cyan-700"
                          title="Send Invite"
                        >
                          <Send className="h-3.5 w-3.5" />
                        </Button>
                      )}
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        onClick={() => handleDeleteClient(client.id)}
                        className="h-8 w-8 p-0 text-red-500 hover:text-red-600"
                        title="Delete"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}

      {/* Invite Link Modal */}
      <Dialog open={inviteOpen} onOpenChange={setInviteOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Send className="h-5 w-5 text-cyan-500" />
              Invite Link Generated
            </DialogTitle>
            <DialogDescription>
              Share this link with {selectedClient?.first_name} to give them portal access.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            {/* Email Option - Preferred */}
            {selectedClient?.email && (
              <div className="p-4 rounded-lg bg-cyan-50 dark:bg-cyan-950/30 border-2 border-cyan-200 dark:border-cyan-900">
                <div className="flex items-start gap-3 mb-3">
                  <div className="p-2 rounded-lg bg-cyan-100 dark:bg-cyan-900/50">
                    <Mail className="h-4 w-4 text-cyan-600 dark:text-cyan-400" />
                  </div>
                  <div className="flex-1">
                    <h4 className="text-sm font-semibold text-slate-900 dark:text-white">
                      Send via Email (Recommended)
                    </h4>
                    <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                      We'll send a professional email to {selectedClient.email}
                    </p>
                  </div>
                </div>
                <Button
                  onClick={handleSendInviteEmail}
                  disabled={sendingEmail}
                  className="w-full bg-gradient-to-r from-cyan-500 to-blue-500"
                  data-testid="send-email-btn"
                >
                  {sendingEmail ? (
                    <>
                      <Clock className="h-4 w-4 mr-2 animate-spin" />
                      Sending...
                    </>
                  ) : (
                    <>
                      <Mail className="h-4 w-4 mr-2" />
                      Send Email Invite
                    </>
                  )}
                </Button>
              </div>
            )}

            {/* Manual Link Option */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-slate-200 dark:border-slate-700" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-white dark:bg-slate-900 px-2 text-slate-500 dark:text-slate-400">
                  Or copy link manually
                </span>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
              <p className="text-xs text-slate-500 dark:text-slate-400 mb-2">Invite Link:</p>
              <div className="flex items-center gap-2">
                <code className="flex-1 text-xs bg-white dark:bg-slate-900 p-2 rounded border border-slate-200 dark:border-slate-700 overflow-x-auto">
                  {inviteLink}
                </code>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={handleCopyLink}
                  className="flex-shrink-0"
                  data-testid="copy-invite-link"
                >
                  {copied ? <Check className="h-4 w-4 text-emerald-500" /> : <Copy className="h-4 w-4" />}
                </Button>
              </div>
            </div>
            <div className="p-3 rounded-lg bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/30">
              <p className="text-xs text-amber-700 dark:text-amber-400">
                <strong>Note:</strong> This link expires in 7 days. The client will create their password when they first access it.
              </p>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Client Detail Modal */}
      <Dialog open={detailOpen} onOpenChange={setDetailOpen}>
        <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
          {selectedClient && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-3">
                  <div className="h-10 w-10 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                    <span className="text-white font-semibold">
                      {selectedClient.first_name?.[0]}{selectedClient.last_name?.[0]}
                    </span>
                  </div>
                  <div>
                    <span>{selectedClient.first_name} {selectedClient.last_name}</span>
                    <div className="mt-1">{getStatusBadge(selectedClient.status)}</div>
                  </div>
                </DialogTitle>
              </DialogHeader>
              
              <Tabs defaultValue="info" className="mt-4">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="info">Info</TabsTrigger>
                  <TabsTrigger value="policies">Policies ({clientPolicies.length})</TabsTrigger>
                  <TabsTrigger value="documents">Documents ({clientDocuments.length})</TabsTrigger>
                </TabsList>
                
                <TabsContent value="info" className="space-y-4 mt-4">
                  {!editMode ? (
                    <>
                      <div className="flex justify-end mb-2">
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => setEditMode(true)}
                          className="gap-2"
                        >
                          <Edit className="h-3.5 w-3.5" />
                          Edit Info
                        </Button>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label className="text-xs text-slate-500">Email</Label>
                          <p className="text-sm font-medium">{selectedClient.email}</p>
                        </div>
                        <div>
                          <Label className="text-xs text-slate-500">Phone</Label>
                          <p className="text-sm font-medium">{selectedClient.phone || '-'}</p>
                        </div>
                        <div>
                          <Label className="text-xs text-slate-500">Created</Label>
                          <p className="text-sm font-medium">{formatDate(selectedClient.created_at)}</p>
                        </div>
                        <div>
                          <Label className="text-xs text-slate-500">Last Login</Label>
                          <p className="text-sm font-medium">{formatDate(selectedClient.last_login_at)}</p>
                        </div>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="flex justify-end gap-2 mb-2">
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => {
                            setEditMode(false);
                            setEditFirstName(selectedClient.first_name);
                            setEditLastName(selectedClient.last_name);
                            setEditEmail(selectedClient.email);
                            setEditPhone(selectedClient.phone || '');
                          }}
                          disabled={updating}
                        >
                          <X className="h-3.5 w-3.5 mr-1" />
                          Cancel
                        </Button>
                        <Button 
                          size="sm"
                          onClick={handleUpdateClient}
                          disabled={updating}
                          className="bg-gradient-to-r from-cyan-500 to-blue-500"
                        >
                          <Save className="h-3.5 w-3.5 mr-1" />
                          {updating ? 'Saving...' : 'Save Changes'}
                        </Button>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label className="text-xs">First Name *</Label>
                          <Input
                            value={editFirstName}
                            onChange={(e) => setEditFirstName(e.target.value)}
                            className="mt-1"
                            disabled={updating}
                          />
                        </div>
                        <div>
                          <Label className="text-xs">Last Name *</Label>
                          <Input
                            value={editLastName}
                            onChange={(e) => setEditLastName(e.target.value)}
                            className="mt-1"
                            disabled={updating}
                          />
                        </div>
                        <div>
                          <Label className="text-xs">Email *</Label>
                          <Input
                            type="email"
                            value={editEmail}
                            onChange={(e) => setEditEmail(e.target.value)}
                            className="mt-1"
                            disabled={updating}
                          />
                        </div>
                        <div>
                          <Label className="text-xs">Phone</Label>
                          <Input
                            type="tel"
                            value={editPhone}
                            onChange={(e) => setEditPhone(e.target.value)}
                            placeholder="(555) 123-4567"
                            className="mt-1"
                            disabled={updating}
                          />
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4 pt-2 border-t border-slate-200 dark:border-slate-700">
                        <div>
                          <Label className="text-xs text-slate-500">Created</Label>
                          <p className="text-sm font-medium">{formatDate(selectedClient.created_at)}</p>
                        </div>
                        <div>
                          <Label className="text-xs text-slate-500">Last Login</Label>
                          <p className="text-sm font-medium">{formatDate(selectedClient.last_login_at)}</p>
                        </div>
                      </div>
                    </>
                  )}
                  
                  {selectedClient.status !== 'active' && (
                    <Button 
                      onClick={() => handleGenerateInvite(selectedClient.id)}
                      className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 mt-4"
                    >
                      <Send className="h-4 w-4 mr-2" />
                      Generate New Invite Link
                    </Button>
                  )}
                </TabsContent>
                
                <TabsContent value="policies" className="space-y-3 mt-4">
                  <Button 
                    size="sm" 
                    onClick={() => setAddPolicyOpen(true)}
                    className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 mb-3"
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Add Policy
                  </Button>
                  
                  {clientPolicies.length === 0 ? (
                    <div className="text-center py-8">
                      <FileText className="h-10 w-10 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
                      <p className="text-sm text-slate-500">No policies added yet</p>
                    </div>
                  ) : (
                    clientPolicies.map((policy) => (
                      <div key={policy.id} className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="font-medium">{policy.carrier}</h4>
                            <p className="text-xs text-slate-500">{policy.product_type} • Policy #{policy.policy_number}</p>
                            <p className="text-xs text-emerald-600 dark:text-emerald-400 mt-1">
                              ${policy.monthly_premium}/mo
                            </p>
                          </div>
                          <span className={`text-xs px-2 py-0.5 rounded-full ${
                            policy.is_visible 
                              ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
                              : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'
                          }`}>
                            {policy.is_visible ? 'Visible' : 'Hidden'}
                          </span>
                        </div>
                      </div>
                    ))
                  )}
                </TabsContent>
                
                <TabsContent value="documents" className="space-y-3 mt-4">
                  <Button 
                    size="sm" 
                    onClick={() => setAddDocumentOpen(true)}
                    className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 mb-3"
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Document
                  </Button>
                  
                  {clientDocuments.length === 0 ? (
                    <div className="text-center py-8">
                      <FileText className="h-10 w-10 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
                      <p className="text-sm text-slate-500">No documents uploaded yet</p>
                    </div>
                  ) : (
                    clientDocuments.map((doc) => (
                      <div key={doc.id} className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <FileText className="h-4 w-4 text-slate-400" />
                            <div>
                              <h4 className="font-medium text-sm">{doc.file_name}</h4>
                              <p className="text-xs text-slate-500">{doc.document_type} • {formatDate(doc.created_at)}</p>
                            </div>
                          </div>
                          <span className={`text-xs px-2 py-0.5 rounded-full ${
                            doc.is_visible 
                              ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
                              : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'
                          }`}>
                            {doc.is_visible ? 'Visible' : 'Hidden'}
                          </span>
                        </div>
                      </div>
                    ))
                  )}
                </TabsContent>
              </Tabs>
            </>
          )}
        </DialogContent>
      </Dialog>
      
      {/* Add Policy Dialog */}
      <Dialog open={addPolicyOpen} onOpenChange={setAddPolicyOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Add New Policy</DialogTitle>
            <DialogDescription>
              Add a policy for {selectedClient?.first_name} {selectedClient?.last_name}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleAddPolicy} className="space-y-4">
            <div className="space-y-1">
              <Label className="text-xs">Carrier *</Label>
              <select
                value={policyCarrier}
                onChange={(e) => setPolicyCarrier(e.target.value)}
                required
                className="w-full h-9 px-3 rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900"
              >
                <option value="">Select Carrier</option>
                {carriers.map(c => <option key={c.id} value={c.name}>{c.name}</option>)}
              </select>
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Product Type *</Label>
              <select
                value={policyType}
                onChange={(e) => setPolicyType(e.target.value)}
                required
                className="w-full h-9 px-3 rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900"
              >
                <option value="">Select Type</option>
                <option value="IUL">IUL</option>
                <option value="Term">Term</option>
                <option value="Whole Life">Whole Life</option>
                <option value="FEX">FEX</option>
                <option value="Annuity">Annuity</option>
              </select>
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Policy Number *</Label>
              <Input
                value={policyNumber}
                onChange={(e) => setPolicyNumber(e.target.value)}
                required
                className="h-9"
                placeholder="POL-123456"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Monthly Premium</Label>
              <Input
                type="number"
                step="0.01"
                value={policyPremium}
                onChange={(e) => setPolicyPremium(e.target.value)}
                className="h-9"
                placeholder="250.00"
              />
            </div>
            <Button
              type="submit"
              className="w-full bg-gradient-to-r from-cyan-500 to-blue-500"
              disabled={submittingPolicy}
            >
              {submittingPolicy ? 'Adding...' : 'Add Policy'}
            </Button>
          </form>
        </DialogContent>
      </Dialog>
      
      {/* Add Document Dialog */}
      <Dialog open={addDocumentOpen} onOpenChange={setAddDocumentOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Upload Document</DialogTitle>
            <DialogDescription>
              Upload a document for {selectedClient?.first_name} {selectedClient?.last_name}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleAddDocument} className="space-y-4">
            <div className="space-y-1">
              <Label className="text-xs">Document Type *</Label>
              <select
                value={documentType}
                onChange={(e) => setDocumentType(e.target.value)}
                required
                className="w-full h-9 px-3 rounded-md border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900"
              >
                <option value="Policy">Policy</option>
                <option value="Application">Application</option>
                <option value="Illustration">Illustration</option>
                <option value="Statement">Statement</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Document Name (Optional)</Label>
              <Input
                value={documentName}
                onChange={(e) => setDocumentName(e.target.value)}
                className="h-9"
                placeholder="Leave empty to use file name"
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">File *</Label>
              <Input
                type="file"
                onChange={(e) => setDocumentFile(e.target.files[0])}
                required
                className="h-9"
                accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
              />
              <p className="text-xs text-slate-500 mt-1">Accepted: PDF, DOC, DOCX, JPG, PNG</p>
            </div>
            <Button
              type="submit"
              className="w-full bg-gradient-to-r from-cyan-500 to-blue-500"
              disabled={submittingDocument}
            >
              {submittingDocument ? 'Uploading...' : 'Upload Document'}
            </Button>
          </form>
        </DialogContent>
      </Dialog>

      {/* Quick Action Dialog - Upload Policy + Email Invite */}
      <Dialog open={quickActionOpen} onOpenChange={setQuickActionOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-cyan-500" />
              Attach Policy & Send Invite
            </DialogTitle>
            <DialogDescription>
              Upload {selectedClient?.first_name}'s policy document and we'll email them their portal link.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            {/* File Upload */}
            <div className="space-y-2">
              <Label className="text-sm font-medium">
                Policy Document (PDF) <span className="text-red-500">*</span>
              </Label>
              <div className="flex flex-col gap-2">
                <Input
                  type="file"
                  onChange={(e) => setPolicyFile(e.target.files[0])}
                  accept=".pdf"
                  required
                  className="h-10"
                  disabled={uploadingPolicy}
                />
                {policyFile && (
                  <div className="flex items-center gap-2 p-2 rounded bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800">
                    <Check className="h-4 w-4 text-emerald-600" />
                    <span className="text-xs text-emerald-700 dark:text-emerald-400">
                      {policyFile.name}
                    </span>
                  </div>
                )}
              </div>
              <p className="text-xs text-slate-500">Required: PDF format only</p>
            </div>

            {/* Action Button */}
            <Button
              onClick={handleQuickUploadAndEmail}
              disabled={!policyFile || uploadingPolicy}
              className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 h-11"
            >
              {uploadingPolicy ? (
                <>
                  <Clock className="h-4 w-4 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Mail className="h-4 w-4 mr-2" />
                  Upload Policy & Email Client Portal Link
                </>
              )}
            </Button>

            {/* Info */}
            <div className="p-3 rounded-lg bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800">
              <p className="text-xs text-blue-700 dark:text-blue-400">
                <strong>This will:</strong>
              </p>
              <ul className="text-xs text-blue-600 dark:text-blue-400 mt-1 space-y-1 ml-4 list-disc">
                <li>Upload the policy to {selectedClient?.first_name}'s documents</li>
                <li>Email them a secure link to access their portal</li>
                <li>Allow them to view all their policies and documents</li>
              </ul>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
