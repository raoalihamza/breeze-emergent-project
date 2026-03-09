import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { BookOpen, Plus, Download, Edit, Trash2, FileSpreadsheet, FileText, DollarSign, Users, TrendingUp, Calendar, Search, ArrowDown, ArrowUp, Send, Copy, Check, Upload } from 'lucide-react';
import { toast } from 'sonner';
import { motion } from 'framer-motion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const PRODUCT_TYPES = ['IUL', 'Term', 'FEX', 'Whole Life', 'Annuity'];
const STATUS_OPTIONS = [
  { value: 'Pending Approval/Issue', label: 'Pending', color: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400' },
  { value: 'Issued', label: 'Issued', color: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' },
  { value: 'Cancelled', label: 'Cancelled', color: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' },
  { value: 'Missed Payment', label: 'Missed Payment', color: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400' }
];
const LEAD_SOURCES = ['Breeze Lead', 'Warm Market', 'Referral', 'Beneficiary', 'Self-Generated', 'Other'];

export default function BookOfBusiness() {
  const { getAuthHeader, user } = useAuth();
  const [clients, setClients] = useState([]);
  const [filteredClients, setFilteredClients] = useState([]);
  const [carriers, setCarriers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [editingClient, setEditingClient] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [productTypeFilter, setProductTypeFilter] = useState('all');
  const [sortOrder, setSortOrder] = useState('newest');
  
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [birthDate, setBirthDate] = useState('');
  const [state, setState] = useState('');
  const [carrier, setCarrier] = useState('');
  const [product, setProduct] = useState('');
  const [productType, setProductType] = useState('');
  const [policyNumber, setPolicyNumber] = useState('');
  const [monthlyPremium, setMonthlyPremium] = useState('');
  const [premium, setPremium] = useState('');
  const [targetPremium, setTargetPremium] = useState('');
  const [status, setStatus] = useState('');
  const [dateSubmitted, setDateSubmitted] = useState('');
  const [dateIssued, setDateIssued] = useState('');
  const [leadSource, setLeadSource] = useState('');
  const [leadSourceOther, setLeadSourceOther] = useState('');
  const [clientWhy, setClientWhy] = useState('');
  const [beneficiaries, setBeneficiaries] = useState([{ name: '', phone_number: '' }]);
  const [additionalNotes, setAdditionalNotes] = useState('');
  const [coverageAmount, setCoverageAmount] = useState('');
  const [policyFile, setPolicyFile] = useState(null);
  const [policyFileName, setPolicyFileName] = useState('');
  const [submitting, setSubmitting] = useState(false);
  
  // Portal invite state
  const [inviteOpen, setInviteOpen] = useState(false);
  const [inviteClientId, setInviteClientId] = useState(null);
  const [inviteClientName, setInviteClientName] = useState('');
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteLink, setInviteLink] = useState('');
  const [inviteCopied, setInviteCopied] = useState(false);
  const [inviteStep, setInviteStep] = useState(1); // 1 = enter email, 2 = show link
  const [inviteLoading, setInviteLoading] = useState(false);
  const [invitePolicyFile, setInvitePolicyFile] = useState(null);
  const [invitePolicyFileName, setInvitePolicyFileName] = useState('');

  useEffect(() => { 
    fetchClients(); 
    fetchCarriers();
  }, []);
  useEffect(() => { filterClients(); }, [clients, searchTerm, statusFilter, productTypeFilter, sortOrder]);

  const fetchCarriers = async () => {
    try {
      const response = await axios.get(`${API}/carriers`, getAuthHeader());
      setCarriers(response.data);
    } catch (error) {
      console.error('Failed to load carriers:', error);
    }
  };

  const fetchClients = async () => {
    try {
      const response = await axios.get(`${API}/clients`, getAuthHeader());
      setClients(response.data);
    } catch (error) {
      toast.error('Failed to load clients');
    } finally {
      setLoading(false);
    }
  };

  const filterClients = () => {
    let filtered = [...clients];
    
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(c => 
        c.first_name?.toLowerCase().includes(term) ||
        c.last_name?.toLowerCase().includes(term) ||
        c.carrier?.toLowerCase().includes(term) ||
        c.policy_number?.toLowerCase().includes(term)
      );
    }
    
    if (statusFilter !== 'all') filtered = filtered.filter(c => c.status === statusFilter);
    if (productTypeFilter !== 'all') filtered = filtered.filter(c => c.product_type === productTypeFilter);
    
    filtered.sort((a, b) => {
      const dateA = new Date(a.date_submitted || a.created_at || 0);
      const dateB = new Date(b.date_submitted || b.created_at || 0);
      return sortOrder === 'newest' ? dateB - dateA : dateA - dateB;
    });
    
    setFilteredClients(filtered);
  };

  const resetForm = () => {
    setFirstName(''); setLastName(''); setEmail(''); setPhone(''); setBirthDate(''); setState('');
    setCarrier(''); setProduct(''); setProductType(''); setPolicyNumber('');
    setMonthlyPremium(''); setPremium(''); setTargetPremium(''); setStatus(''); setDateSubmitted('');
    setDateIssued(''); setLeadSource(''); setLeadSourceOther(''); setClientWhy('');
    setBeneficiaries([{ name: '', phone_number: '' }]); setAdditionalNotes('');
    setCoverageAmount(''); setPolicyFile(null); setPolicyFileName('');
    setEditingClient(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    const data = {
      first_name: firstName, last_name: lastName, email, phone, birth_date: birthDate, state,
      carrier, product, product_type: productType, policy_number: policyNumber,
      monthly_premium: productType === 'Annuity' ? null : (monthlyPremium ? parseFloat(monthlyPremium) : null),
      premium: productType === 'Annuity' ? (premium ? parseFloat(premium) : null) : null,
      target_premium: productType === 'IUL' ? (targetPremium ? parseFloat(targetPremium) : null) : null,
      coverage_amount: coverageAmount ? parseFloat(coverageAmount) : null,
      status, date_submitted: dateSubmitted || null, date_issued: dateIssued || null,
      lead_source: leadSource, lead_source_other: leadSource === 'Other' ? leadSourceOther : null,
      client_why: clientWhy, beneficiaries: beneficiaries.filter(b => b.name || b.phone_number),
      additional_notes: additionalNotes
    };

    try {
      if (editingClient) {
        await axios.put(`${API}/clients/${editingClient.id}`, data, getAuthHeader());
        toast.success('Client updated!');
      } else {
        await axios.post(`${API}/clients`, data, getAuthHeader());
        toast.success('Client added!');
      }
      fetchClients();
      setOpen(false);
      resetForm();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save client');
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = (client) => {
    setEditingClient(client);
    setFirstName(client.first_name || ''); setLastName(client.last_name || '');
    setEmail(client.email || ''); setPhone(client.phone || '');
    setBirthDate(client.birth_date || ''); setState(client.state || '');
    setCarrier(client.carrier || ''); setProduct(client.product || '');
    setProductType(client.product_type || ''); setPolicyNumber(client.policy_number || '');
    setMonthlyPremium(client.monthly_premium?.toString() || '');
    setPremium(client.premium?.toString() || '');
    setTargetPremium(client.target_premium?.toString() || '');
    setCoverageAmount(client.coverage_amount?.toString() || '');
    setStatus(client.status || ''); setDateSubmitted(client.date_submitted || '');
    setDateIssued(client.date_issued || ''); setLeadSource(client.lead_source || '');
    setLeadSourceOther(client.lead_source_other || ''); setClientWhy(client.client_why || '');
    setBeneficiaries(client.beneficiaries?.length > 0 ? client.beneficiaries : [{ name: '', phone_number: '' }]);
    setAdditionalNotes(client.additional_notes || '');
    setOpen(true);
  };

  const handleDelete = async (clientId) => {
    if (!window.confirm('Delete this client?')) return;
    try {
      await axios.delete(`${API}/clients/${clientId}`, getAuthHeader());
      toast.success('Client deleted');
      fetchClients();
    } catch (error) {
      toast.error('Failed to delete');
    }
  };

  const handleExport = async (format) => {
    try {
      const response = await axios.get(`${API}/clients/export/${format}`, { ...getAuthHeader(), responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `book_of_business.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success(`Exported as ${format.toUpperCase()}`);
    } catch (error) {
      toast.error('Export failed');
    }
  };

  // Portal invite functions
  const handleOpenInvite = (client) => {
    setInviteClientId(client.id);
    setInviteClientName(`${client.first_name} ${client.last_name}`);
    setInviteEmail('');
    setInviteLink('');
    setInviteStep(1);
    setInvitePolicyFile(null);
    setInvitePolicyFileName('');
    setInviteOpen(true);
  };

  const handleCreatePortalInvite = async () => {
    if (!inviteEmail) {
      toast.error('Please enter an email address');
      return;
    }
    
    setInviteLoading(true);
    try {
      // First create portal client from book of business
      const createRes = await axios.post(`${API}/portal/clients/from-book/${inviteClientId}`, {}, getAuthHeader());
      const portalClientId = createRes.data.portal_client.id;
      
      // If there's a policy PDF, upload it
      if (invitePolicyFile) {
        const reader = new FileReader();
        reader.onload = async () => {
          const base64Data = reader.result.split(',')[1];
          try {
            await axios.post(`${API}/portal/documents/upload`, {
              client_id: portalClientId,
              file_data: base64Data,
              file_name: invitePolicyFileName,
              document_type: 'policy',
              is_visible: true
            }, getAuthHeader());
          } catch (uploadError) {
            console.error('Failed to upload policy document:', uploadError);
          }
        };
        reader.readAsDataURL(invitePolicyFile);
      }
      
      // Then set email and generate invite
      const inviteRes = await axios.put(`${API}/portal/clients/${portalClientId}/email`, {
        email: inviteEmail,
        send_invite: true
      }, getAuthHeader());
      
      if (inviteRes.data.invite) {
        const baseUrl = window.location.origin;
        const link = `${baseUrl}/client-portal/setup/${inviteRes.data.invite.invite_token}`;
        setInviteLink(link);
        setInviteStep(2);
        toast.success('Portal invite created!');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create portal invite');
    } finally {
      setInviteLoading(false);
    }
  };

  const handleCopyInviteLink = () => {
    navigator.clipboard.writeText(inviteLink);
    setInviteCopied(true);
    toast.success('Link copied!');
    setTimeout(() => setInviteCopied(false), 2000);
  };

  const getStatusBadge = (statusValue) => {
    const config = STATUS_OPTIONS.find(s => s.value === statusValue);
    if (!config) return <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500">Legacy</span>;
    return <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${config.color}`}>{config.label}</span>;
  };

  const calculateTotals = () => {
    let lifePremium = 0, annuityPremium = 0, issued = 0;
    const lifeTypes = ['IUL', 'Term', 'FEX', 'Whole Life'];
    
    clients.forEach(c => {
      if (c.status === 'Issued') issued++;
      if (c.product_type === 'Annuity' && c.premium) annuityPremium += c.premium;
      else if (lifeTypes.includes(c.product_type)) {
        if (c.annual_premium) lifePremium += c.annual_premium;
        else if (c.monthly_premium) lifePremium += c.monthly_premium * 12;
      }
    });
    return { lifePremium, annuityPremium, issued };
  };

  const { lifePremium, annuityPremium, issued } = calculateTotals();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-2 border-cyan-500 border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-5" data-testid="book-of-business-page">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="flex items-center gap-3">
          <div className="h-8 w-1 bg-gradient-to-b from-cyan-500 to-blue-500 rounded-full"></div>
          <div>
            <h1 className="text-xl font-bold text-slate-900 dark:text-white">Book of Business</h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">Manage your client portfolio</p>
          </div>
        </motion.div>

        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => handleExport('csv')} size="sm" className="text-xs h-8">
            <FileText className="h-3.5 w-3.5 mr-1" />CSV
          </Button>
          <Button variant="outline" onClick={() => handleExport('xlsx')} size="sm" className="text-xs h-8">
            <FileSpreadsheet className="h-3.5 w-3.5 mr-1" />XLSX
          </Button>
          <Button variant="outline" onClick={() => handleExport('pdf')} size="sm" className="text-xs h-8">
            <Download className="h-3.5 w-3.5 mr-1" />PDF
          </Button>
          <Dialog open={open} onOpenChange={(isOpen) => { 
            setOpen(isOpen); 
            // Don't auto-reset when dialog closes - let user decide to cancel
            // Only reset after explicit save or when opening fresh
          }}>
            <DialogTrigger asChild>
              <Button size="sm" className="h-8 bg-gradient-to-r from-cyan-500 to-blue-500 text-white" data-testid="add-client-button">
                <Plus className="h-3.5 w-3.5 mr-1" />Add Client
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[85vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>{editingClient ? 'Edit Client' : 'Add New Client'}</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4" data-testid="client-form">
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label className="text-xs">First Name *</Label>
                    <Input value={firstName} onChange={(e) => setFirstName(e.target.value)} required className="h-9" />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Last Name *</Label>
                    <Input value={lastName} onChange={(e) => setLastName(e.target.value)} required className="h-9" />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Email *</Label>
                    <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className="h-9" placeholder="client@example.com" />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Phone Number *</Label>
                    <Input type="tel" value={phone} onChange={(e) => setPhone(e.target.value)} required className="h-9" placeholder="(555) 123-4567" />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Birth Date *</Label>
                    <Input type="date" value={birthDate} onChange={(e) => setBirthDate(e.target.value)} required className="h-9" />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">State *</Label>
                    <Input value={state} onChange={(e) => setState(e.target.value)} placeholder="CA" required className="h-9" />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label className="text-xs">Carrier *</Label>
                    <Select value={carrier} onValueChange={setCarrier} required>
                      <SelectTrigger className="h-9">
                        <SelectValue placeholder="Select carrier" />
                      </SelectTrigger>
                      <SelectContent>
                        {carriers.map((c) => (
                          <SelectItem key={c.id} value={c.name}>
                            {c.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Product *</Label>
                    <Input value={product} onChange={(e) => setProduct(e.target.value)} required className="h-9" />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Product Type *</Label>
                    <Select value={productType} onValueChange={setProductType}>
                      <SelectTrigger className="h-9"><SelectValue placeholder="Select type" /></SelectTrigger>
                      <SelectContent>
                        {PRODUCT_TYPES.map(type => <SelectItem key={type} value={type}>{type}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Policy Number *</Label>
                    <Input value={policyNumber} onChange={(e) => setPolicyNumber(e.target.value)} required className="h-9" />
                  </div>
                </div>

                {productType && productType !== 'Annuity' && (
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1">
                      <Label className="text-xs">Monthly Premium *</Label>
                      <Input type="number" step="0.01" value={monthlyPremium} onChange={(e) => setMonthlyPremium(e.target.value)} required className="h-9" />
                    </div>
                    <div className="space-y-1">
                      <Label className="text-xs">Annual (Auto)</Label>
                      <Input value={monthlyPremium ? `$${(parseFloat(monthlyPremium) * 12).toFixed(2)}` : '$0'} disabled className="h-9 bg-slate-50 dark:bg-slate-800" />
                    </div>
                  </div>
                )}

                {productType === 'IUL' && (
                  <div className="space-y-1 border-2 border-cyan-200 dark:border-cyan-800 rounded-lg p-3 bg-cyan-50/50 dark:bg-cyan-950/20">
                    <div className="flex items-center gap-2 mb-1">
                      <DollarSign className="h-4 w-4 text-cyan-600 dark:text-cyan-400" />
                      <Label className="text-xs font-semibold text-cyan-900 dark:text-cyan-100">Target Premium *</Label>
                    </div>
                    <Input 
                      type="number" 
                      step="0.01" 
                      value={targetPremium} 
                      onChange={(e) => setTargetPremium(e.target.value)} 
                      required 
                      placeholder="Enter target premium for IUL"
                      className="h-9 border-cyan-300 dark:border-cyan-700 focus:border-cyan-500 dark:focus:border-cyan-500" 
                    />
                    <p className="text-xs text-cyan-700 dark:text-cyan-400 mt-1">Required for IUL products</p>
                  </div>
                )}

                {productType === 'Annuity' && (
                  <div className="space-y-1">
                    <Label className="text-xs">Premium (Lump Sum) *</Label>
                    <Input type="number" step="0.01" value={premium} onChange={(e) => setPremium(e.target.value)} required className="h-9" />
                  </div>
                )}

                {/* Coverage Amount */}
                <div className="space-y-1">
                  <Label className="text-xs">Coverage Amount (Face Amount)</Label>
                  <div className="relative">
                    <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-slate-400" />
                    <Input 
                      type="number" 
                      step="0.01" 
                      value={coverageAmount} 
                      onChange={(e) => setCoverageAmount(e.target.value)} 
                      placeholder="e.g., 500000"
                      className="h-9 pl-8" 
                    />
                  </div>
                </div>

                {/* Policy PDF Upload */}
                <div className="space-y-1">
                  <Label className="text-xs">Policy PDF (Optional)</Label>
                  <div 
                    className={`border-2 border-dashed rounded-lg p-4 transition-colors cursor-pointer hover:border-cyan-400 ${
                      policyFile ? 'border-cyan-500 bg-cyan-50/50 dark:bg-cyan-950/20' : 'border-slate-200 dark:border-slate-700'
                    }`}
                    onClick={() => document.getElementById('policy-file-input').click()}
                    onDragOver={(e) => { e.preventDefault(); e.stopPropagation(); }}
                    onDrop={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      const file = e.dataTransfer.files[0];
                      if (file && file.type === 'application/pdf') {
                        setPolicyFile(file);
                        setPolicyFileName(file.name);
                      } else {
                        toast.error('Please upload a PDF file');
                      }
                    }}
                  >
                    <input
                      id="policy-file-input"
                      type="file"
                      accept=".pdf"
                      className="hidden"
                      onChange={(e) => {
                        const file = e.target.files[0];
                        if (file) {
                          setPolicyFile(file);
                          setPolicyFileName(file.name);
                        }
                      }}
                    />
                    <div className="text-center">
                      {policyFile ? (
                        <div className="flex items-center justify-center gap-2">
                          <FileText className="h-5 w-5 text-cyan-600 dark:text-cyan-400" />
                          <span className="text-sm text-slate-700 dark:text-slate-300">{policyFileName}</span>
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              setPolicyFile(null);
                              setPolicyFileName('');
                            }}
                            className="ml-2 text-red-500 hover:text-red-600 text-xs"
                          >
                            Remove
                          </button>
                        </div>
                      ) : (
                        <>
                          <Upload className="h-6 w-6 text-slate-400 mx-auto mb-1" />
                          <p className="text-xs text-slate-500 dark:text-slate-400">
                            Drop PDF here or <span className="text-cyan-600 dark:text-cyan-400">browse</span>
                          </p>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div className="space-y-1">
                    <Label className="text-xs">Status *</Label>
                    <Select value={status} onValueChange={setStatus}>
                      <SelectTrigger className="h-9"><SelectValue placeholder="Status" /></SelectTrigger>
                      <SelectContent>
                        {STATUS_OPTIONS.map(opt => <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Date Submitted</Label>
                    <Input type="date" value={dateSubmitted} onChange={(e) => setDateSubmitted(e.target.value)} className="h-9" />
                  </div>
                  <div className="space-y-1">
                    <Label className="text-xs">Date Issued</Label>
                    <Input type="date" value={dateIssued} onChange={(e) => setDateIssued(e.target.value)} className="h-9" />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <Label className="text-xs">Lead Source *</Label>
                    <Select value={leadSource} onValueChange={setLeadSource}>
                      <SelectTrigger className="h-9"><SelectValue placeholder="Source" /></SelectTrigger>
                      <SelectContent>
                        {LEAD_SOURCES.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                      </SelectContent>
                    </Select>
                  </div>
                  {leadSource === 'Other' && (
                    <div className="space-y-1">
                      <Label className="text-xs">Specify *</Label>
                      <Input value={leadSourceOther} onChange={(e) => setLeadSourceOther(e.target.value)} required className="h-9" />
                    </div>
                  )}
                </div>

                <div className="space-y-1">
                  <Label className="text-xs">Client's "Why"</Label>
                  <Textarea value={clientWhy} onChange={(e) => setClientWhy(e.target.value)} rows={2} className="text-sm" />
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label className="text-xs">Beneficiaries</Label>
                    <Button type="button" variant="ghost" size="sm" onClick={() => setBeneficiaries([...beneficiaries, { name: '', phone_number: '' }])} className="h-6 text-xs">
                      <Plus className="h-3 w-3 mr-1" />Add
                    </Button>
                  </div>
                  {beneficiaries.map((ben, i) => (
                    <div key={i} className="flex gap-2">
                      <Input placeholder="Name" value={ben.name} onChange={(e) => { const u = [...beneficiaries]; u[i].name = e.target.value; setBeneficiaries(u); }} className="h-8 text-sm" />
                      <Input placeholder="Phone" value={ben.phone_number} onChange={(e) => { const u = [...beneficiaries]; u[i].phone_number = e.target.value; setBeneficiaries(u); }} className="h-8 text-sm" />
                      {beneficiaries.length > 1 && (
                        <Button type="button" variant="ghost" size="sm" onClick={() => setBeneficiaries(beneficiaries.filter((_, idx) => idx !== i))} className="h-8 px-2">
                          <Trash2 className="h-3.5 w-3.5 text-red-500" />
                        </Button>
                      )}
                    </div>
                  ))}
                </div>

                <div className="space-y-1">
                  <Label className="text-xs">Additional Notes</Label>
                  <Textarea value={additionalNotes} onChange={(e) => setAdditionalNotes(e.target.value)} rows={2} className="text-sm" />
                </div>

                <div className="flex gap-2">
                  <Button 
                    type="button" 
                    variant="outline"
                    onClick={() => { 
                      setOpen(false); 
                      resetForm(); 
                    }} 
                    className="flex-1"
                    disabled={submitting}
                  >
                    Cancel
                  </Button>
                  <Button type="submit" className="flex-1 bg-gradient-to-r from-cyan-500 to-blue-500" disabled={submitting}>
                    {submitting ? 'Saving...' : (editingClient ? 'Update Client' : 'Add Client')}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3">
        <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
          <CardContent className="p-3 sm:p-4">
            <div className="flex items-center justify-between mb-1 sm:mb-2">
              <span className="text-[10px] sm:text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Clients</span>
              <div className="p-1 sm:p-1.5 rounded-lg bg-cyan-50 dark:bg-cyan-950/30">
                <Users className="h-3 sm:h-3.5 w-3 sm:w-3.5 text-cyan-600 dark:text-cyan-400" />
              </div>
            </div>
            <div className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white">{clients.length}</div>
          </CardContent>
        </Card>
        <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
          <CardContent className="p-3 sm:p-4">
            <div className="flex items-center justify-between mb-1 sm:mb-2">
              <span className="text-[10px] sm:text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Life Premium</span>
              <div className="p-1 sm:p-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/30">
                <TrendingUp className="h-3 sm:h-3.5 w-3 sm:w-3.5 text-emerald-600 dark:text-emerald-400" />
              </div>
            </div>
            <div className="text-lg sm:text-2xl font-bold text-slate-900 dark:text-white">${lifePremium.toLocaleString()}/yr</div>
            <p className="text-[9px] sm:text-[10px] text-slate-400 mt-0.5 hidden sm:block">Annual (IUL, Term, FEX, WL)</p>
          </CardContent>
        </Card>
        <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
          <CardContent className="p-3 sm:p-4">
            <div className="flex items-center justify-between mb-1 sm:mb-2">
              <span className="text-[10px] sm:text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Annuity</span>
              <div className="p-1 sm:p-1.5 rounded-lg bg-violet-50 dark:bg-violet-950/30">
                <DollarSign className="h-3 sm:h-3.5 w-3 sm:w-3.5 text-violet-600 dark:text-violet-400" />
              </div>
            </div>
            <div className="text-lg sm:text-2xl font-bold text-slate-900 dark:text-white">${annuityPremium.toLocaleString()}</div>
            <p className="text-[9px] sm:text-[10px] text-slate-400 mt-0.5 hidden sm:block">Total Premium</p>
          </CardContent>
        </Card>
        <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
          <CardContent className="p-3 sm:p-4">
            <div className="flex items-center justify-between mb-1 sm:mb-2">
              <span className="text-[10px] sm:text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Issued</span>
              <div className="p-1 sm:p-1.5 rounded-lg bg-amber-50 dark:bg-amber-950/30">
                <BookOpen className="h-3 sm:h-3.5 w-3 sm:w-3.5 text-amber-600 dark:text-amber-400" />
              </div>
            </div>
            <div className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white">{issued}</div>
            <p className="text-[9px] sm:text-[10px] text-slate-400 mt-0.5 hidden sm:block">Policies</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters Row */}
      <div className="flex flex-col sm:flex-row sm:flex-wrap items-stretch sm:items-center gap-2">
        <div className="relative flex-1 min-w-full sm:min-w-[200px] sm:max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <Input
            placeholder="Search clients..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9 h-9 bg-white dark:bg-slate-900"
            data-testid="search-input"
          />
        </div>
        <div className="flex items-center gap-2">
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="flex-1 sm:w-[140px] h-9 bg-white dark:bg-slate-900" data-testid="status-filter">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              {STATUS_OPTIONS.map(opt => <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>)}
            </SelectContent>
          </Select>
          <Select value={productTypeFilter} onValueChange={setProductTypeFilter}>
            <SelectTrigger className="flex-1 sm:w-[130px] h-9 bg-white dark:bg-slate-900" data-testid="product-filter">
              <SelectValue placeholder="Product" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Products</SelectItem>
              {PRODUCT_TYPES.map(type => <SelectItem key={type} value={type}>{type}</SelectItem>)}
            </SelectContent>
          </Select>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setSortOrder(sortOrder === 'newest' ? 'oldest' : 'newest')}
            className="h-9 bg-white dark:bg-slate-900 px-3"
            data-testid="sort-button"
          >
            {sortOrder === 'newest' ? <ArrowDown className="h-4 w-4 sm:mr-1" /> : <ArrowUp className="h-4 w-4 sm:mr-1" />}
            <span className="hidden sm:inline">{sortOrder === 'newest' ? 'Newest' : 'Oldest'}</span>
          </Button>
        </div>
        <span className="text-xs text-slate-500 text-center sm:ml-auto">{filteredClients.length} clients</span>
      </div>

      {/* Client List */}
      {filteredClients.length === 0 ? (
        <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
          <CardContent className="py-12 text-center">
            <BookOpen className="h-10 w-10 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
            <p className="text-slate-500 dark:text-slate-400">
              {searchTerm || statusFilter !== 'all' || productTypeFilter !== 'all' ? 'No clients match filters' : 'No clients yet'}
            </p>
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
              data-testid={`client-card-${client.id}`}
            >
              <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50 hover:border-cyan-500/30 transition-colors">
                <CardContent className="p-3 sm:p-4">
                  <div className="flex flex-col sm:flex-row sm:items-start gap-3 sm:gap-4">
                    {/* Client Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1 flex-wrap">
                        <h3 className="font-semibold text-sm sm:text-base text-slate-900 dark:text-white truncate">
                          {client.first_name} {client.last_name}
                        </h3>
                        {getStatusBadge(client.status)}
                      </div>
                      
                      {/* Agent Tag (Admin Only) */}
                      {user?.role === 'admin' && client.added_by_agent_name && (
                        <div className="mb-1">
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-400">
                            <Users className="h-3 w-3" />
                            {client.added_by_agent_name}
                          </span>
                        </div>
                      )}
                      
                      <div className="flex items-center gap-2 text-[11px] sm:text-xs text-slate-500 dark:text-slate-400 flex-wrap">
                        <span>{client.birth_date}</span>
                        <span>•</span>
                        <span>{client.state}</span>
                        <span>•</span>
                        <span className="truncate max-w-[120px]">{client.carrier}</span>
                        <span>•</span>
                        <span className="font-medium text-slate-700 dark:text-slate-300">{client.product_type}</span>
                      </div>
                    </div>

                    {/* Premium & Actions Row for Mobile */}
                    <div className="flex items-center justify-between sm:flex-col sm:items-end gap-2">
                      {/* Premium & Policy */}
                      <div className="text-left sm:text-right">
                        <div className="text-sm font-semibold text-emerald-600 dark:text-emerald-400">
                          {client.product_type === 'Annuity' 
                            ? (client.premium ? `$${client.premium.toLocaleString()}` : '-')
                            : (client.annual_premium ? `$${client.annual_premium.toLocaleString()}/yr` : client.monthly_premium ? `$${client.monthly_premium}/mo` : '-')
                          }
                        </div>
                        <div className="text-[10px] sm:text-xs text-slate-400">{client.policy_number}</div>
                      </div>

                      {/* Actions */}
                      <div className="flex gap-1 flex-shrink-0">
                        <Button 
                          variant="ghost" 
                          size="sm" 
                          onClick={() => handleOpenInvite(client)} 
                          className="h-8 w-8 p-0 text-cyan-600 hover:text-cyan-700" 
                          title="Invite to Portal"
                          data-testid={`invite-client-${client.id}`}
                        >
                          <Send className="h-3.5 w-3.5" />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => handleEdit(client)} className="h-8 w-8 p-0" data-testid={`edit-client-${client.id}`}>
                          <Edit className="h-3.5 w-3.5" />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => handleDelete(client.id)} className="h-8 w-8 p-0 text-red-500 hover:text-red-600" data-testid={`delete-client-${client.id}`}>
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </div>
                  </div>

                  {/* Additional Info Row */}
                  {(client.lead_source || client.date_submitted || client.client_why) && (
                    <div className="mt-2 pt-2 border-t border-slate-100 dark:border-slate-800 flex flex-wrap gap-x-3 sm:gap-x-4 gap-y-1 text-[10px] sm:text-xs text-slate-500 dark:text-slate-400">
                      {client.lead_source && <span>Lead: {client.lead_source === 'Other' ? client.lead_source_other : client.lead_source}</span>}
                      {client.date_submitted && <span className="hidden sm:inline">Submitted: {client.date_submitted}</span>}
                      {client.date_issued && <span className="hidden sm:inline">Issued: {client.date_issued}</span>}
                      {client.client_why && <span className="basis-full text-slate-600 dark:text-slate-300 mt-1 line-clamp-2">Why: {client.client_why}</span>}
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}

      {/* Portal Invite Modal */}
      <Dialog open={inviteOpen} onOpenChange={setInviteOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Send className="h-5 w-5 text-cyan-500" />
              Invite to Client Portal
            </DialogTitle>
          </DialogHeader>
          
          {inviteStep === 1 ? (
            <div className="space-y-4">
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Send <strong>{inviteClientName}</strong> an invite to view their policy in the client portal.
              </p>
              <div className="space-y-2">
                <Label className="text-xs">Client Email *</Label>
                <Input
                  type="email"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="client@example.com"
                  className="h-9"
                  data-testid="portal-invite-email"
                />
              </div>
              
              {/* Policy PDF Upload */}
              <div className="space-y-2">
                <Label className="text-xs">Attach Policy PDF (Optional)</Label>
                <div 
                  className={`border-2 border-dashed rounded-lg p-3 transition-colors cursor-pointer hover:border-cyan-400 ${
                    invitePolicyFile ? 'border-cyan-500 bg-cyan-50/50 dark:bg-cyan-950/20' : 'border-slate-200 dark:border-slate-700'
                  }`}
                  onClick={() => document.getElementById('invite-policy-file-input').click()}
                  onDragOver={(e) => { e.preventDefault(); e.stopPropagation(); }}
                  onDrop={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    const file = e.dataTransfer.files[0];
                    if (file && file.type === 'application/pdf') {
                      setInvitePolicyFile(file);
                      setInvitePolicyFileName(file.name);
                    } else {
                      toast.error('Please upload a PDF file');
                    }
                  }}
                >
                  <input
                    id="invite-policy-file-input"
                    type="file"
                    accept=".pdf"
                    className="hidden"
                    onChange={(e) => {
                      const file = e.target.files[0];
                      if (file) {
                        setInvitePolicyFile(file);
                        setInvitePolicyFileName(file.name);
                      }
                    }}
                  />
                  <div className="text-center">
                    {invitePolicyFile ? (
                      <div className="flex items-center justify-center gap-2">
                        <FileText className="h-4 w-4 text-cyan-600 dark:text-cyan-400" />
                        <span className="text-xs text-slate-700 dark:text-slate-300">{invitePolicyFileName}</span>
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            setInvitePolicyFile(null);
                            setInvitePolicyFileName('');
                          }}
                          className="ml-2 text-red-500 hover:text-red-600 text-xs"
                        >
                          Remove
                        </button>
                      </div>
                    ) : (
                      <>
                        <Upload className="h-5 w-5 text-slate-400 mx-auto mb-1" />
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                          Drop policy PDF or <span className="text-cyan-600 dark:text-cyan-400">browse</span>
                        </p>
                      </>
                    )}
                  </div>
                </div>
                <p className="text-xs text-slate-400">Client will see this in their Documents Vault</p>
              </div>
              
              <Button 
                onClick={handleCreatePortalInvite} 
                className="w-full bg-gradient-to-r from-cyan-500 to-blue-500" 
                disabled={inviteLoading || !inviteEmail}
                data-testid="generate-invite-btn"
              >
                {inviteLoading ? 'Creating...' : 'Generate Invite Link'}
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-900/30 text-center">
                <Check className="h-8 w-8 text-emerald-500 mx-auto mb-2" />
                <p className="text-sm font-medium text-emerald-700 dark:text-emerald-400">
                  Invite created for {inviteClientName}!
                </p>
                {invitePolicyFile && (
                  <p className="text-xs text-emerald-600 dark:text-emerald-500 mt-1">
                    Policy document attached
                  </p>
                )}
              </div>
              
              <div className="space-y-2">
                <Label className="text-xs text-slate-500">Share this link with your client:</Label>
                <div className="flex items-center gap-2">
                  <code className="flex-1 text-xs bg-slate-100 dark:bg-slate-800 p-2 rounded border overflow-x-auto">
                    {inviteLink}
                  </code>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={handleCopyInviteLink}
                    data-testid="copy-portal-link"
                  >
                    {inviteCopied ? <Check className="h-4 w-4 text-emerald-500" /> : <Copy className="h-4 w-4" />}
                  </Button>
                </div>
              </div>
              
              <div className="p-3 rounded-lg bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900/30">
                <p className="text-xs text-amber-700 dark:text-amber-400">
                  This link expires in 7 days. The client will create their own password.
                </p>
              </div>
              
              <Button variant="outline" onClick={() => setInviteOpen(false)} className="w-full">
                Done
              </Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
