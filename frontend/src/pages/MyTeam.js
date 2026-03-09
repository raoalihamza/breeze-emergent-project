import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Card, CardContent } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Sheet, SheetContent, SheetHeader, SheetTitle } from '../components/ui/sheet';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '../components/ui/dropdown-menu.jsx';
import { Button } from '../components/ui/button.jsx';
import { Input } from '../components/ui/input.jsx';
import { Users, ChevronRight, ChevronDown, TrendingUp, UserPlus, Mail, Phone, Calendar, Clock, Zap, Network, Building2, MapPin, CheckCircle, MoreVertical, Download, Workflow, Search } from 'lucide-react';
import { toast } from 'sonner';
import { motion, AnimatePresence } from 'framer-motion';
import OrgChart from '../components/OrgChart';
import { ReassignAgentModal, ToggleStatusModal, ChangeCommissionModal, DeleteUserModal, EditAgentDetailsModal } from '../components/AdminControlModals';
import { ExportModal } from '../components/ExportModal';
import * as XLSX from 'xlsx';
import { jsPDF } from 'jspdf';
import 'jspdf-autotable';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

function TreeNode({ node, level = 0, onAgentClick }) {
  const [expanded, setExpanded] = useState(level < 2);

  return (
    <div className={level > 0 ? "ml-5 border-l border-slate-200 dark:border-slate-700 pl-3" : ""} data-testid={`tree-node-${node.id}`}>
      <div
        className="flex items-center gap-2 py-2 px-3 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/50 cursor-pointer group transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        {node.children && node.children.length > 0 ? (
          <div className="p-0.5">
            {expanded ? <ChevronDown className="h-4 w-4 text-slate-400" /> : <ChevronRight className="h-4 w-4 text-slate-400" />}
          </div>
        ) : (
          <div className="w-5" />
        )}
        <div className="flex-1 min-w-0" onClick={(e) => { e.stopPropagation(); onAgentClick(node); }}>
          <div className="font-medium text-sm text-slate-900 dark:text-white group-hover:text-cyan-600 dark:group-hover:text-cyan-400 truncate">
            {node.name}
          </div>
          <div className="text-xs text-slate-500 dark:text-slate-400">
            {node.role} • {node.comp_percentage}%{node.team_size > 0 && ` • ${node.team_size} team`}
          </div>
        </div>
        <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${
          node.status === 'active' 
            ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' 
            : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'
        }`}>
          {node.status === 'active' ? 'Active' : 'Inactive'}
        </span>
      </div>
      <AnimatePresence>
        {expanded && node.children && node.children.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
          >
            {node.children.map((child) => (
              <TreeNode key={child.id} node={child} level={level + 1} onAgentClick={onAgentClick} />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function MyTeam() {
  const { user, getAuthHeader, impersonateUser } = useAuth();
  const [hierarchyData, setHierarchyData] = useState(null);
  const [tableData, setTableData] = useState([]);
  const [filteredTableData, setFilteredTableData] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [agentDetails, setAgentDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);
  
  // Admin controls state
  const [orgTreeData, setOrgTreeData] = useState(null);
  const [allUsers, setAllUsers] = useState([]);
  const [reassignModalOpen, setReassignModalOpen] = useState(false);
  const [statusModalOpen, setStatusModalOpen] = useState(false);
  const [commissionModalOpen, setCommissionModalOpen] = useState(false);
  const [exportModalOpen, setExportModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [editDetailsModalOpen, setEditDetailsModalOpen] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [modalLoading, setModalLoading] = useState(false);

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    try {
      const promises = [
        axios.get(`${API}/hierarchy/tree`, getAuthHeader()),
        axios.get(`${API}/hierarchy/downline`, getAuthHeader()),
        axios.get(`${API}/hierarchy/stats`, getAuthHeader())
      ];

      // If admin, fetch additional data
      if (user?.role === 'admin') {
        promises.push(
          axios.get(`${API}/admin/org-tree`, getAuthHeader()),
          axios.get(`${API}/admin/users`, getAuthHeader())
        );
      }

      const results = await Promise.all(promises);
      
      setHierarchyData(results[0].data);
      
      // Sort table data alphabetically by first name
      const sortedTableData = (results[1].data || []).sort((a, b) => {
        const nameA = (a.name || '').toLowerCase();
        const nameB = (b.name || '').toLowerCase();
        return nameA.localeCompare(nameB);
      });
      
      setTableData(sortedTableData);
      setFilteredTableData(sortedTableData);
      setStats(results[2].data);
      
      if (user?.role === 'admin') {
        setOrgTreeData(results[3].data);
        setAllUsers(results[4].data);
      }
    } catch (error) {
      toast.error('Failed to load team data');
    } finally {
      setLoading(false);
    }
  };

  // Handle search in table view
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredTableData(tableData);
    } else {
      const query = searchQuery.toLowerCase();
      const filtered = tableData.filter(member => 
        (member.name || '').toLowerCase().includes(query) ||
        (member.email || '').toLowerCase().includes(query) ||
        (member.npn || '').toLowerCase().includes(query)
      );
      setFilteredTableData(filtered);
    }
  }, [searchQuery, tableData]);

  const handleAgentClick = async (agent) => {
    setDrawerOpen(true);
    setLoadingDetails(true);
    
    try {
      const endpoint = user?.role === 'admin' ? `${API}/users/${agent.id}/full-profile` : `${API}/users/${agent.id}`;
      const response = await axios.get(endpoint, getAuthHeader());
      setAgentDetails(response.data);
    } catch (error) {
      toast.error('Failed to load agent details');
    } finally {
      setLoadingDetails(false);
    }
  };

  // Admin action handlers
  const handleReassignAgent = async (agentId, newUplineId) => {
    setModalLoading(true);
    try {
      await axios.put(
        `${API}/admin/users/${agentId}/upline`,
        { new_upline_id: newUplineId },
        getAuthHeader()
      );
      toast.success('Agent reassigned successfully');
      setReassignModalOpen(false);
      fetchData(); // Refresh data
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to reassign agent');
    } finally {
      setModalLoading(false);
    }
  };

  const handleToggleStatus = async (agentId, newStatus) => {
    setModalLoading(true);
    try {
      await axios.put(
        `${API}/admin/users/${agentId}/status`,
        { status: newStatus },
        getAuthHeader()
      );
      toast.success(`Agent ${newStatus === 'active' ? 'enabled' : 'disabled'} successfully`);
      setStatusModalOpen(false);
      fetchData(); // Refresh data
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update agent status');
    } finally {
      setModalLoading(false);
    }
  };

  const handleChangeCommission = async (agentId, newCommission) => {
    setModalLoading(true);
    try {
      await axios.put(
        `${API}/admin/users/${agentId}/commission`,
        { comp_percentage: newCommission },
        getAuthHeader()
      );
      toast.success('Commission updated successfully');
      setCommissionModalOpen(false);
      fetchData(); // Refresh data
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update commission');
    } finally {
      setModalLoading(false);
    }
  };

  const handleEditAgentDetails = async (agentId, updates) => {
    setModalLoading(true);
    try {
      const response = await axios.put(
        `${API}/admin/users/${agentId}/details`,
        updates,
        getAuthHeader()
      );
      toast.success(response.data.message || 'Agent details updated successfully');
      setEditDetailsModalOpen(false);
      fetchData(); // Refresh data
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update agent details');
    } finally {
      setModalLoading(false);
    }
  };

  const handleExportHierarchy = async (format) => {
    setModalLoading(true);
    try {
      const response = await axios.get(`${API}/admin/hierarchy-export`, getAuthHeader());
      const data = response.data;
      const timestamp = new Date().toISOString().split('T')[0];

      if (format === 'json') {
        // JSON Export
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        downloadFile(blob, `hierarchy-export-${timestamp}.json`);
      } else if (format === 'csv') {
        // CSV Export
        const headers = ['Name', 'Email', 'Role', 'Status', 'Commission %', 'Upline', 'NPN', 'Date Joined'];
        const rows = data.users.map(u => [
          u.name,
          u.email,
          u.role,
          u.status,
          u.comp_percentage,
          u.upline_name || 'None',
          u.npn || '',
          u.date_joined || ''
        ]);
        
        const csvContent = [
          headers.join(','),
          ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
        ].join('\n');
        
        const blob = new Blob([csvContent], { type: 'text/csv' });
        downloadFile(blob, `hierarchy-export-${timestamp}.csv`);
      } else if (format === 'xlsx') {
        // XLSX Export
        const worksheet = XLSX.utils.json_to_sheet(
          data.users.map(u => ({
            'Name': u.name,
            'Email': u.email,
            'Role': u.role,
            'Status': u.status,
            'Commission %': u.comp_percentage,
            'Upline': u.upline_name || 'None',
            'NPN': u.npn || '',
            'Date Joined': u.date_joined || ''
          }))
        );
        
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Hierarchy');
        
        // Add metadata sheet
        const metaSheet = XLSX.utils.json_to_sheet([{
          'Exported At': data.exported_at,
          'Exported By': data.exported_by,
          'Total Users': data.total_users
        }]);
        XLSX.utils.book_append_sheet(workbook, metaSheet, 'Metadata');
        
        XLSX.writeFile(workbook, `hierarchy-export-${timestamp}.xlsx`);
      } else if (format === 'pdf') {
        // PDF Export (Simplified to avoid timeout)
        const doc = new jsPDF();
        
        // Title
        doc.setFontSize(20);
        doc.setTextColor(6, 182, 212);
        doc.text('Atlas - Hierarchy Export', 14, 20);
        
        // Metadata
        doc.setFontSize(10);
        doc.setTextColor(100);
        doc.text(`Exported: ${new Date(data.exported_at).toLocaleString()}`, 14, 32);
        doc.text(`By: ${data.exported_by}`, 14, 38);
        doc.text(`Total Users: ${data.total_users}`, 14, 44);
        
        // Table with basic data
        const tableData = data.users.slice(0, 50).map(u => [
          u.name,
          u.role,
          `${u.comp_percentage}%`,
          u.status
        ]);
        
        doc.autoTable({
          startY: 52,
          head: [['Name', 'Role', 'Commission', 'Status']],
          body: tableData,
          styles: { 
            fontSize: 9,
            cellPadding: 2
          },
          headStyles: { 
            fillColor: [6, 182, 212],
            textColor: 255
          },
          alternateRowStyles: {
            fillColor: [245, 247, 250]
          },
          margin: { top: 52 }
        });
        
        // Add note if data was truncated
        if (data.users.length > 50) {
          const finalY = doc.lastAutoTable.finalY || 52;
          doc.setFontSize(8);
          doc.setTextColor(150);
          doc.text(`Note: Showing first 50 of ${data.users.length} users. Download XLSX for complete data.`, 14, finalY + 10);
        }
        
        doc.save(`hierarchy-export-${timestamp}.pdf`);
      }
      
      setExportModalOpen(false);
      toast.success(`Hierarchy exported as ${format.toUpperCase()}`);
    } catch (error) {
      toast.error('Failed to export hierarchy');
    } finally {
      setModalLoading(false);
    }
  };

  const downloadFile = (blob, filename) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const openAdminMenu = (agent, action) => {
    setSelectedAgent(agent);
    if (action === 'reassign') setReassignModalOpen(true);
    else if (action === 'status') setStatusModalOpen(true);
    else if (action === 'commission') setCommissionModalOpen(true);
    else if (action === 'edit') setEditDetailsModalOpen(true);
    else if (action === 'impersonate') handleImpersonate(agent);
    else if (action === 'delete') setDeleteModalOpen(true);
  };

  const handleImpersonate = async (agent) => {
    try {
      await impersonateUser(agent.id);
      toast.success(`Now viewing as ${agent.name}`);
      // Redirect to dashboard
      setTimeout(() => {
        window.location.href = '/';
      }, 1000);
    } catch (error) {
      toast.error('Failed to impersonate user');
    }
  };

  const handleDeleteUser = async (agentId) => {
    setModalLoading(true);
    try {
      const response = await axios.delete(
        `${API}/admin/users/${agentId}`,
        getAuthHeader()
      );
      toast.success(response.data.message || 'User deleted successfully');
      setDeleteModalOpen(false);
      fetchData(); // Refresh data
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete user');
    } finally {
      setModalLoading(false);
    }
  };

  const isAdmin = user?.role === 'admin';
  const canViewLastLogin = user?.role === 'admin' || user?.role === 'leader';

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-2 border-cyan-500 border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-5" data-testid="my-team-page">
      {/* Header */}
      <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="flex items-center gap-3">
        <div className="h-8 w-1 bg-gradient-to-b from-cyan-500 to-blue-500 rounded-full"></div>
        <div>
          <h1 className="text-xl font-bold text-slate-900 dark:text-white">My Team</h1>
          <p className="text-xs text-slate-500 dark:text-slate-400">Manage hierarchy and performance</p>
        </div>
      </motion.div>

      {/* Stats Row */}
      {stats && (
        <div className="grid grid-cols-2 gap-3">
          {[
            { title: 'Direct', value: stats.direct_agents, icon: Users, color: 'cyan' },
            { title: 'Indirect', value: stats.indirect_agents, icon: TrendingUp, color: 'violet' },
            { title: 'Total', value: stats.total_downline, icon: Network, color: 'amber' },
            { title: 'New', value: stats.new_this_month, icon: UserPlus, color: 'emerald' }
          ].map((stat, i) => {
            const Icon = stat.icon;
            return (
              <motion.div key={stat.title} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}>
                <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">{stat.title}</span>
                      <div className={`p-1.5 rounded-lg bg-${stat.color}-50 dark:bg-${stat.color}-950/30`}>
                        <Icon className={`h-3.5 w-3.5 text-${stat.color}-600 dark:text-${stat.color}-400`} />
                      </div>
                    </div>
                    <div className="text-2xl font-bold text-slate-900 dark:text-white">{stat.value}</div>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Tabs */}
      <Tabs defaultValue="tree" className="w-full">
        <div className="flex items-center justify-between mb-4">
          <TabsList className="bg-slate-100 dark:bg-slate-800 p-1 h-auto">
            <TabsTrigger value="tree" data-testid="tree-view-tab" className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-700 data-[state=active]:text-cyan-600 dark:data-[state=active]:text-cyan-400 px-4 py-2 text-sm">
              <Network className="h-4 w-4 mr-1.5" />Tree
            </TabsTrigger>
            <TabsTrigger value="table" data-testid="table-view-tab" className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-700 data-[state=active]:text-cyan-600 dark:data-[state=active]:text-cyan-400 px-4 py-2 text-sm">
              <Users className="h-4 w-4 mr-1.5" />Table
            </TabsTrigger>
            {isAdmin && (
              <TabsTrigger value="org-chart" data-testid="org-chart-tab" className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-700 data-[state=active]:text-cyan-600 dark:data-[state=active]:text-cyan-400 px-4 py-2 text-sm">
                <Workflow className="h-4 w-4 mr-1.5" />Org Chart
              </TabsTrigger>
            )}
          </TabsList>

          {isAdmin && (
            <Button
              onClick={() => setExportModalOpen(true)}
              variant="outline"
              size="sm"
              className="gap-2"
              data-testid="export-hierarchy-btn"
            >
              <Download className="h-4 w-4" />
              Export
            </Button>
          )}
        </div>

        <TabsContent value="tree" className="mt-4">
          <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
            <CardContent className="p-4">
              {hierarchyData?.trees && hierarchyData.trees.length > 0 ? (
                <div className="overflow-x-auto">
                  <div className="min-w-max space-y-1">
                    {hierarchyData.trees.map((tree) => (
                      <TreeNode key={tree.id} node={tree} onAgentClick={handleAgentClick} />
                    ))}
                  </div>
                </div>
              ) : (
                <div className="py-12 text-center">
                  <Network className="h-10 w-10 mx-auto text-slate-300 dark:text-slate-600 mb-3" />
                  <p className="text-slate-500 dark:text-slate-400 text-sm">No team members yet</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="table" className="mt-4">
          <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
            {/* Search Bar */}
            <div className="p-4 border-b border-slate-200 dark:border-slate-700">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <Input
                  type="text"
                  placeholder="Search by name, email, or NPN..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 h-10"
                  data-testid="team-search-input"
                />
              </div>
              {searchQuery && (
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-2">
                  Found {filteredTableData.length} {filteredTableData.length === 1 ? 'member' : 'members'}
                </p>
              )}
            </div>
            
            <CardContent className="p-0">
              {filteredTableData && filteredTableData.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full" data-testid="team-table">
                    <thead>
                      <tr className="border-b border-slate-200 dark:border-slate-700">
                        <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase">Name</th>
                        <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase">Email</th>
                        <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase">Role</th>
                        <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase">NPN</th>
                        <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase">Comp</th>
                        {canViewLastLogin && <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase">Last Login</th>}
                        <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase">Status</th>
                        <th className="text-right py-3 px-4 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredTableData.map((member) => (
                        <tr
                          key={member.id}
                          className="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
                          data-testid={`team-member-row-${member.id}`}
                        >
                          <td className="py-3 px-4 text-sm font-medium text-slate-900 dark:text-white cursor-pointer" onClick={() => handleAgentClick(member)}>{member.name}</td>
                          <td className="py-3 px-4 text-sm text-slate-500 dark:text-slate-400">{member.email}</td>
                          <td className="py-3 px-4">
                            <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-50 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-400 capitalize">{member.role}</span>
                          </td>
                          <td className="py-3 px-4 text-sm text-slate-500 dark:text-slate-400 font-mono">{member.npn || '-'}</td>
                          <td className="py-3 px-4 text-sm font-semibold text-slate-900 dark:text-white">{member.comp_percentage}%</td>
                          {canViewLastLogin && (
                            <td className="py-3 px-4 text-xs text-slate-500 dark:text-slate-400">
                              {member.last_login ? new Date(member.last_login).toLocaleDateString() : 'Never'}
                            </td>
                          )}
                          <td className="py-3 px-4">
                            <span className={`text-xs px-2 py-0.5 rounded-full ${
                              member.status === 'active' 
                                ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' 
                                : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'
                            }`}>
                              {member.status === 'active' ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="sm" className="h-8 w-8 p-0" data-testid={`admin-menu-${member.id}`}>
                                  <MoreVertical className="h-4 w-4" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end">
                                {isAdmin && (
                                  <>
                                    <DropdownMenuItem onClick={() => openAdminMenu(member, 'edit')} data-testid="action-edit-details">
                                      Edit Details
                                    </DropdownMenuItem>
                                    <DropdownMenuItem onClick={() => openAdminMenu(member, 'impersonate')} data-testid="action-impersonate">
                                      View as Agent
                                    </DropdownMenuItem>
                                    <DropdownMenuItem onClick={() => openAdminMenu(member, 'reassign')} data-testid="action-reassign">
                                      Reassign Agent
                                    </DropdownMenuItem>
                                    <DropdownMenuItem onClick={() => openAdminMenu(member, 'commission')} data-testid="action-commission">
                                      Change Commission
                                    </DropdownMenuItem>
                                  </>
                                )}
                                <DropdownMenuItem onClick={() => openAdminMenu(member, 'status')} data-testid="action-status">
                                  {member.status === 'active' ? 'Disable' : 'Enable'} Account
                                </DropdownMenuItem>
                                {isAdmin && (
                                  <DropdownMenuItem 
                                    onClick={() => openAdminMenu(member, 'delete')} 
                                    data-testid="action-delete"
                                    className="text-red-600 dark:text-red-400 focus:text-red-600 dark:focus:text-red-400"
                                  >
                                    Delete User
                                  </DropdownMenuItem>
                                )}
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="py-12 text-center">
                  <Users className="h-10 w-10 mx-auto text-slate-300 dark:text-slate-600 mb-3" />
                  <p className="text-slate-500 dark:text-slate-400 text-sm">No team members yet</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Org Chart Tab (Admin Only) */}
        {isAdmin && (
          <TabsContent value="org-chart" className="mt-4">
            <OrgChart data={orgTreeData} onNodeClick={handleAgentClick} />
          </TabsContent>
        )}
      </Tabs>

      {/* Agent Profile Drawer */}
      <Sheet open={drawerOpen} onOpenChange={setDrawerOpen}>
        <SheetContent className="w-full sm:max-w-md overflow-y-auto">
          <SheetHeader>
            <SheetTitle className="flex items-center gap-2 text-base">
              <Users className="h-4 w-4 text-cyan-500" />
              Agent Profile
            </SheetTitle>
          </SheetHeader>
          
          {loadingDetails ? (
            <div className="flex items-center justify-center h-48">
              <div className="animate-spin rounded-full h-8 w-8 border-2 border-cyan-500 border-t-transparent"></div>
            </div>
          ) : agentDetails ? (
            <div className="mt-4 space-y-4">
              {/* Basic Info */}
              <div className="text-center pb-4 border-b border-slate-200 dark:border-slate-700">
                <div className="w-16 h-16 mx-auto rounded-full bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center text-white text-xl font-bold mb-2">
                  {agentDetails.name?.charAt(0)}
                </div>
                <h3 className="text-lg font-bold text-slate-900 dark:text-white">{agentDetails.name}</h3>
                <p className="text-xs text-cyan-600 dark:text-cyan-400 font-medium uppercase">{agentDetails.role}</p>
              </div>

              {/* Details Grid */}
              <div className="space-y-2">
                <InfoRow icon={Mail} label="Email" value={agentDetails.email} />
                {agentDetails.phone && <InfoRow icon={Phone} label="Phone" value={agentDetails.phone} />}
                {agentDetails.npn && <InfoRow label="NPN" value={agentDetails.npn} mono />}
                <InfoRow icon={Calendar} label="Joined" value={new Date(agentDetails.created_at).toLocaleDateString()} />
                {canViewLastLogin && agentDetails.last_login && (
                  <InfoRow icon={Clock} label="Last Login" value={new Date(agentDetails.last_login).toLocaleString()} />
                )}
                {agentDetails.upline_name && <InfoRow icon={Users} label="Upline" value={agentDetails.upline_name} />}
                <InfoRow icon={Zap} label="Commission" value={`${agentDetails.comp_percentage}%`} highlight />
                
                <div className="flex items-center justify-between py-2 px-3 rounded-lg bg-slate-50 dark:bg-slate-800">
                  <span className="text-xs text-slate-500">Status</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    agentDetails.status === 'active' 
                      ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' 
                      : 'bg-slate-200 text-slate-500 dark:bg-slate-700 dark:text-slate-400'
                  }`}>
                    {agentDetails.status === 'active' ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>

              {/* Licensed States - Admin Only */}
              {isAdmin && agentDetails.licensed_states?.length > 0 && (
                <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
                  <div className="flex items-center gap-2 mb-3">
                    <MapPin className="h-4 w-4 text-blue-500" />
                    <span className="text-sm font-medium text-slate-900 dark:text-white">Licensed States</span>
                    <span className="ml-auto text-[10px] bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 px-1.5 py-0.5 rounded-full">
                      {agentDetails.licensed_states.length}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    {agentDetails.licensed_states.map((ls) => (
                      <div key={ls.state} className="flex items-center gap-2 p-2 rounded-lg bg-slate-50 dark:bg-slate-800 text-sm">
                        <CheckCircle className="h-3 w-3 text-emerald-500 flex-shrink-0" />
                        <span className="font-medium text-slate-900 dark:text-white">{ls.state}</span>
                        {ls.license_number && <span className="text-xs text-slate-400 truncate">{ls.license_number}</span>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Appointed Carriers - Admin Only */}
              {isAdmin && agentDetails.appointed_carriers?.length > 0 && (
                <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
                  <div className="flex items-center gap-2 mb-3">
                    <Building2 className="h-4 w-4 text-emerald-500" />
                    <span className="text-sm font-medium text-slate-900 dark:text-white">Appointed Carriers</span>
                    <span className="ml-auto text-[10px] bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 px-1.5 py-0.5 rounded-full">
                      {agentDetails.appointed_carriers.length}
                    </span>
                  </div>
                  <div className="space-y-2">
                    {agentDetails.appointed_carriers.map((carrier) => (
                      <div key={carrier.carrier_id} className="flex items-center gap-2 p-2 rounded-lg bg-slate-50 dark:bg-slate-800">
                        <div 
                          className="w-6 h-6 rounded flex items-center justify-center text-white text-[10px] font-bold"
                          style={{ backgroundColor: carrier.primary_color }}
                        >
                          {carrier.carrier_name.substring(0, 2).toUpperCase()}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium text-slate-900 dark:text-white truncate">{carrier.carrier_name}</div>
                          {carrier.writing_number && <div className="text-[10px] text-slate-400 font-mono">#{carrier.writing_number}</div>}
                        </div>
                        <CheckCircle className="h-3.5 w-3.5 text-emerald-500 flex-shrink-0" />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* No Data Message - Admin Only */}
              {isAdmin && !agentDetails.licensed_states?.length && !agentDetails.appointed_carriers?.length && (
                <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
                  <p className="text-xs text-slate-400 text-center py-4">No licenses or carrier appointments on file</p>
                </div>
              )}
            </div>
          ) : null}
        </SheetContent>
      </Sheet>

      {/* Admin Control Modals */}
      {isAdmin && (
        <>
          <ReassignAgentModal
            open={reassignModalOpen}
            onClose={() => setReassignModalOpen(false)}
            agent={selectedAgent}
            allUsers={allUsers}
            onConfirm={handleReassignAgent}
            loading={modalLoading}
          />
          <ChangeCommissionModal
            key={selectedAgent?.id}
            open={commissionModalOpen}
            onClose={() => setCommissionModalOpen(false)}
            agent={selectedAgent}
            onConfirm={handleChangeCommission}
            loading={modalLoading}
          />
          <ExportModal
            open={exportModalOpen}
            onClose={() => setExportModalOpen(false)}
            onConfirm={handleExportHierarchy}
            loading={modalLoading}
          />
          <DeleteUserModal
            open={deleteModalOpen}
            onClose={() => setDeleteModalOpen(false)}
            agent={selectedAgent}
            onConfirm={handleDeleteUser}
            loading={modalLoading}
          />
          <EditAgentDetailsModal
            open={editDetailsModalOpen}
            onClose={() => setEditDetailsModalOpen(false)}
            agent={selectedAgent}
            onConfirm={handleEditAgentDetails}
            loading={modalLoading}
          />
        </>
      )}
      
      {/* Toggle Status Modal - Available for all users to manage downline */}
      <ToggleStatusModal
        open={statusModalOpen}
        onClose={() => setStatusModalOpen(false)}
        agent={selectedAgent}
        onConfirm={handleToggleStatus}
        loading={modalLoading}
      />
    </div>
  );
}

function InfoRow({ icon: Icon, label, value, mono, highlight }) {
  return (
    <div className={`flex items-center justify-between py-2 px-3 rounded-lg ${highlight ? 'bg-cyan-50 dark:bg-cyan-950/30' : 'bg-slate-50 dark:bg-slate-800'}`}>
      <div className="flex items-center gap-2">
        {Icon && <Icon className={`h-3.5 w-3.5 ${highlight ? 'text-cyan-500' : 'text-slate-400'}`} />}
        <span className="text-xs text-slate-500">{label}</span>
      </div>
      <span className={`text-sm ${mono ? 'font-mono' : ''} ${highlight ? 'font-bold text-cyan-600 dark:text-cyan-400' : 'text-slate-900 dark:text-white'}`}>{value}</span>
    </div>
  );
}
