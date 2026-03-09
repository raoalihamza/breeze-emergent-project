import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from './ui/dialog.jsx';
import { Button } from './ui/button.jsx';
import { Label } from './ui/label.jsx';
import { Input } from './ui/input.jsx';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select.jsx';
import { Loader2, UserX, UserCheck, DollarSign, Users, Trash2, Edit } from 'lucide-react';

// Reassign Agent Modal
export function ReassignAgentModal({ open, onClose, agent, allUsers, onConfirm, loading }) {
  const [selectedUpline, setSelectedUpline] = useState('');

  // Filter out the agent themselves and their downline from potential uplines
  const availableUplines = allUsers.filter(u => 
    u.id !== agent?.id && 
    u.status === 'active'
  );

  const handleSubmit = () => {
    if (selectedUpline) {
      onConfirm(agent.id, selectedUpline === 'none' ? null : selectedUpline);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Users className="h-5 w-5 text-blue-500" />
            Reassign Agent
          </DialogTitle>
          <DialogDescription>
            Change the upline for <span className="font-semibold text-slate-900 dark:text-white">{agent?.name}</span>
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="upline">New Upline</Label>
            <Select value={selectedUpline} onValueChange={setSelectedUpline}>
              <SelectTrigger id="upline" data-testid="upline-select">
                <SelectValue placeholder="Select new upline" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="none">None (Top Level)</SelectItem>
                {availableUplines.map((user) => (
                  <SelectItem key={user.id} value={user.id}>
                    {user.name} ({user.role})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {agent?.upline_name && (
            <div className="text-xs text-slate-500 dark:text-slate-400 bg-slate-50 dark:bg-slate-800 p-2 rounded">
              Current upline: <span className="font-medium">{agent.upline_name}</span>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={loading || !selectedUpline} data-testid="confirm-reassign">
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Updating...
              </>
            ) : (
              'Reassign'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// Toggle Status Modal
export function ToggleStatusModal({ open, onClose, agent, onConfirm, loading }) {
  const isActive = agent?.status === 'active';
  const newStatus = isActive ? 'disabled' : 'active';

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {isActive ? (
              <UserX className="h-5 w-5 text-red-500" />
            ) : (
              <UserCheck className="h-5 w-5 text-emerald-500" />
            )}
            {isActive ? 'Disable' : 'Enable'} Agent
          </DialogTitle>
          <DialogDescription>
            Are you sure you want to {isActive ? 'disable' : 'enable'}{' '}
            <span className="font-semibold text-slate-900 dark:text-white">{agent?.name}</span>?
          </DialogDescription>
        </DialogHeader>

        <div className="py-4">
          {isActive ? (
            <div className="text-sm text-slate-600 dark:text-slate-400 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg border border-red-200 dark:border-red-800">
              <p className="font-medium text-red-900 dark:text-red-300 mb-1">⚠️ Warning</p>
              <p>This agent will not be able to log in until their account is re-enabled.</p>
            </div>
          ) : (
            <div className="text-sm text-slate-600 dark:text-slate-400 bg-emerald-50 dark:bg-emerald-900/20 p-3 rounded-lg border border-emerald-200 dark:border-emerald-800">
              <p>This agent will regain access to their account.</p>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button
            onClick={() => onConfirm(agent.id, newStatus)}
            disabled={loading}
            variant={isActive ? 'destructive' : 'default'}
            data-testid="confirm-status-toggle"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Updating...
              </>
            ) : (
              `${isActive ? 'Disable' : 'Enable'} Account`
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// Change Commission Modal
export function ChangeCommissionModal({ open, onClose, agent, onConfirm, loading }) {
  const [commission, setCommission] = useState(() => 
    agent?.comp_percentage?.toString() || '0'
  );

  const handleSubmit = () => {
    const value = parseFloat(commission);
    if (!isNaN(value) && value >= 0 && value <= 200) {
      onConfirm(agent.id, value);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5 text-violet-500" />
            Change Commission
          </DialogTitle>
          <DialogDescription>
            Update commission level for <span className="font-semibold text-slate-900 dark:text-white">{agent?.name}</span>
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="commission">Commission Percentage</Label>
            <div className="flex items-center gap-2">
              <input
                id="commission"
                type="number"
                min="0"
                max="200"
                step="0.5"
                value={commission}
                onChange={(e) => setCommission(e.target.value)}
                className="flex h-10 w-full rounded-md border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 px-3 py-2 text-sm ring-offset-white file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-slate-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 dark:ring-offset-slate-950"
                data-testid="commission-input"
              />
              <span className="text-lg font-bold text-slate-600 dark:text-slate-400">%</span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400">Range: 0% - 200%</p>
          </div>

          <div className="text-xs text-slate-500 dark:text-slate-400 bg-slate-50 dark:bg-slate-800 p-2 rounded">
            Current commission: <span className="font-medium">{agent?.comp_percentage}%</span>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={loading} data-testid="confirm-commission">
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Updating...
              </>
            ) : (
              'Update Commission'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// Delete User Modal
export function DeleteUserModal({ open, onClose, agent, onConfirm, loading }) {
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Trash2 className="h-5 w-5 text-red-500" />
            Delete User
          </DialogTitle>
          <DialogDescription>
            Are you sure you want to permanently delete{' '}
            <span className="font-semibold text-slate-900 dark:text-white">{agent?.name}</span>?
          </DialogDescription>
        </DialogHeader>

        <div className="py-4">
          <div className="text-sm text-slate-600 dark:text-slate-400 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg border border-red-200 dark:border-red-800">
            <p className="font-medium text-red-900 dark:text-red-300 mb-2">⚠️ Warning: This action cannot be undone</p>
            <ul className="text-xs space-y-1 text-red-800 dark:text-red-400">
              <li>• All user data will be permanently deleted</li>
              <li>• Any downline agents will be reassigned to the user&apos;s upline</li>
              <li>• Historical records and commissions will be preserved</li>
            </ul>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button
            onClick={() => onConfirm(agent.id)}
            disabled={loading}
            variant="destructive"
            data-testid="confirm-delete"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Deleting...
              </>
            ) : (
              'Delete User'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// Edit Agent Details Modal
export function EditAgentDetailsModal({ open, onClose, agent, onConfirm, loading }) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    npn: ''
  });
  const [errors, setErrors] = useState({});

  // Initialize form with agent data when modal opens
  useEffect(() => {
    if (agent && open) {
      setFormData({
        name: agent.name || '',
        email: agent.email || '',
        npn: agent.npn || ''
      });
      setErrors({});
    }
  }, [agent, open]);

  const validateForm = () => {
    const newErrors = {};

    // Validate name
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    } else if (formData.name.trim().length < 2) {
      newErrors.name = 'Name must be at least 2 characters';
    }

    // Validate email
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    // Validate NPN (optional but if provided, must be valid)
    if (formData.npn && formData.npn.trim().length > 0 && formData.npn.trim().length < 4) {
      newErrors.npn = 'NPN must be at least 4 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error for this field when user types
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleSubmit = () => {
    if (validateForm()) {
      // Only send changed fields
      const updates = {};
      if (formData.name !== agent.name) updates.name = formData.name.trim();
      if (formData.email !== agent.email) updates.email = formData.email.trim();
      if (formData.npn !== (agent.npn || '')) updates.npn = formData.npn.trim();

      if (Object.keys(updates).length > 0) {
        onConfirm(agent.id, updates);
      } else {
        onClose();
      }
    }
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Edit className="h-5 w-5 text-blue-500" />
            Edit Agent Details
          </DialogTitle>
          <DialogDescription>
            Update information for <span className="font-semibold text-slate-900 dark:text-white">{agent?.name}</span>
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Name Field */}
          <div className="space-y-2">
            <Label htmlFor="edit-name">
              Full Name <span className="text-red-500">*</span>
            </Label>
            <Input
              id="edit-name"
              data-testid="edit-name-input"
              placeholder="Enter full name"
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              className={errors.name ? 'border-red-500' : ''}
              disabled={loading}
            />
            {errors.name && (
              <p className="text-xs text-red-500">{errors.name}</p>
            )}
          </div>

          {/* Email Field */}
          <div className="space-y-2">
            <Label htmlFor="edit-email">
              Email Address <span className="text-red-500">*</span>
            </Label>
            <Input
              id="edit-email"
              data-testid="edit-email-input"
              type="email"
              placeholder="Enter email address"
              value={formData.email}
              onChange={(e) => handleChange('email', e.target.value)}
              className={errors.email ? 'border-red-500' : ''}
              disabled={loading}
            />
            {errors.email && (
              <p className="text-xs text-red-500">{errors.email}</p>
            )}
          </div>

          {/* NPN Field */}
          <div className="space-y-2">
            <Label htmlFor="edit-npn">
              NPN (National Producer Number)
            </Label>
            <Input
              id="edit-npn"
              data-testid="edit-npn-input"
              placeholder="Enter NPN"
              value={formData.npn}
              onChange={(e) => handleChange('npn', e.target.value)}
              className={errors.npn ? 'border-red-500' : ''}
              disabled={loading}
            />
            {errors.npn && (
              <p className="text-xs text-red-500">{errors.npn}</p>
            )}
          </div>

          {/* Info Note */}
          <div className="text-xs text-slate-500 dark:text-slate-400 bg-slate-50 dark:bg-slate-800 p-3 rounded">
            <strong>Note:</strong> Changing the email or NPN will be reflected immediately. Make sure the new values are correct.
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={loading} data-testid="confirm-edit-details">
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Updating...
              </>
            ) : (
              'Save Changes'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
