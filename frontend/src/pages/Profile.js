import { useState, useRef, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { User, Mail, Shield, Calendar, Key, Upload, MapPin, Plus, X, Clock, TrendingUp, Zap, Phone } from 'lucide-react';
import { toast } from 'sonner';
import { motion } from 'framer-motion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const US_STATES = [
  'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
  'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
  'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
  'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
  'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
];

export default function Profile() {
  const { user, getAuthHeader } = useAuth();
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [updating, setUpdating] = useState(false);
  const [profilePicture, setProfilePicture] = useState(user?.profile_picture || null);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);
  const [extendedProfile, setExtendedProfile] = useState(null);
  const [licensedStates, setLicensedStates] = useState([]);
  const [newState, setNewState] = useState('');
  const [newLicenseNumber, setNewLicenseNumber] = useState('');
  const [savingStates, setSavingStates] = useState(false);
  const [phone, setPhone] = useState('');
  const [savingPhone, setSavingPhone] = useState(false);

  useEffect(() => { 
    fetchExtendedProfile(); 
  }, []);

  const fetchExtendedProfile = async () => {
    try {
      const response = await axios.get(`${API}/user/profile-extended`, getAuthHeader());
      setExtendedProfile(response.data);
      setLicensedStates(response.data.licensed_states || []);
      setPhone(user?.phone || response.data.phone || '');
    } catch (error) {
      console.error('Failed to fetch extended profile:', error);
    }
  };

  const handleAddState = () => {
    if (!newState) { toast.error('Please select a state'); return; }
    if (licensedStates.some(s => s.state === newState)) { toast.error('State already added'); return; }
    setLicensedStates([...licensedStates, { state: newState, license_number: newLicenseNumber || null }]);
    setNewState(''); setNewLicenseNumber('');
    toast.success(`${newState} added! Click Save to persist.`);
  };

  const handleRemoveState = (stateToRemove) => {
    setLicensedStates(licensedStates.filter(s => s.state !== stateToRemove));
  };

  const handleSaveLicensedStates = async () => {
    setSavingStates(true);
    try {
      await axios.put(`${API}/user/licensed-states`, { licensed_states: licensedStates }, getAuthHeader());
      toast.success('Licensed states saved!');
      fetchExtendedProfile();
    } catch (error) {
      toast.error('Failed to save');
    } finally {
      setSavingStates(false);
    }
  };

  const handleSavePhone = async () => {
    setSavingPhone(true);
    try {
      await axios.put(`${API}/user/phone`, { phone: phone }, getAuthHeader());
      toast.success('Phone number saved!');
      fetchExtendedProfile();
    } catch (error) {
      toast.error('Failed to save phone number');
    } finally {
      setSavingPhone(false);
    }
  };

  const handlePasswordReset = async (e) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) { toast.error('Passwords do not match'); return; }
    if (newPassword.length < 8) { toast.error('Password must be at least 8 characters'); return; }
    setUpdating(true);
    try {
      await axios.post(`${API}/auth/reset-password`, { new_password: newPassword }, getAuthHeader());
      toast.success('Password updated!');
      setNewPassword(''); setConfirmPassword('');
    } catch (error) {
      toast.error('Failed to update password');
    } finally {
      setUpdating(false);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (!file.type.startsWith('image/')) { toast.error('Please select an image'); return; }
    if (file.size > 5 * 1024 * 1024) { toast.error('Image must be less than 5MB'); return; }
    const reader = new FileReader();
    reader.onloadend = () => uploadProfilePicture(reader.result);
    reader.readAsDataURL(file);
  };

  const uploadProfilePicture = async (base64Image) => {
    setUploading(true);
    try {
      const response = await axios.post(`${API}/auth/profile-picture`, { profile_picture: base64Image }, getAuthHeader());
      setProfilePicture(response.data.profile_picture);
      toast.success('Profile picture updated!');
      window.location.reload();
    } catch (error) {
      toast.error('Failed to upload');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-5" data-testid="profile-page">
      {/* Header */}
      <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="flex items-center gap-3">
        <div className="h-8 w-1 bg-gradient-to-b from-cyan-500 to-blue-500 rounded-full"></div>
        <div>
          <h1 className="text-xl font-bold text-slate-900 dark:text-white">Profile</h1>
          <p className="text-xs text-slate-500 dark:text-slate-400">Manage your account settings</p>
        </div>
      </motion.div>

      <div className="grid lg:grid-cols-3 gap-4">
        {/* Left Column - Photo & Account Info */}
        <div className="lg:col-span-2 space-y-4">
          {/* Profile Photo & Basic Info */}
          <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
            <CardContent className="p-4">
              <div className="flex items-start gap-4">
                <div className="relative flex-shrink-0">
                  {profilePicture ? (
                    <img src={profilePicture} alt="Profile" className="w-20 h-20 rounded-xl object-cover border-2 border-cyan-500/20" />
                  ) : (
                    <div className="w-20 h-20 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center text-white text-2xl font-bold">
                      {user?.name?.charAt(0)}
                    </div>
                  )}
                  <input ref={fileInputRef} type="file" accept="image/*" onChange={handleFileSelect} className="hidden" />
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={uploading}
                    className="absolute -bottom-1 -right-1 p-1.5 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
                  >
                    <Upload className="h-3 w-3 text-slate-600 dark:text-slate-400" />
                  </button>
                </div>
                <div className="flex-1 min-w-0">
                  <h2 className="text-lg font-bold text-slate-900 dark:text-white truncate">{user?.name}</h2>
                  <p className="text-sm text-slate-500 dark:text-slate-400">{user?.email}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-50 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-400 capitalize">{user?.role}</span>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400">{user?.comp_percentage}% comp</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Account Details Grid */}
          <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
            <CardContent className="p-4">
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
                <User className="h-4 w-4 text-cyan-500" /> Account Details
              </h3>
              <div className="grid grid-cols-2 gap-3">
                <InfoItem icon={Mail} label="Email" value={user?.email} />
                <InfoItem icon={Shield} label="Role" value={user?.role} capitalize />
                <InfoItem icon={Zap} label="Commission" value={`${user?.comp_percentage}%`} />
                {user?.npn && <InfoItem label="NPN" value={user?.npn} mono />}
                {user?.upline_name && <InfoItem icon={User} label="Upline" value={user?.upline_name} />}
                <InfoItem icon={Calendar} label="Member Since" value={new Date(user?.created_at).toLocaleDateString()} />
                {extendedProfile?.last_login && <InfoItem icon={Clock} label="Last Login" value={new Date(extendedProfile.last_login).toLocaleDateString()} />}
                {extendedProfile?.last_production_date && <InfoItem icon={TrendingUp} label="Last Production" value={new Date(extendedProfile.last_production_date).toLocaleDateString()} />}
              </div>
            </CardContent>
          </Card>

          {/* Phone Number */}
          <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
            <CardContent className="p-4">
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
                <Phone className="h-4 w-4 text-cyan-500" /> Contact Phone Number
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mb-3">
                This phone number will be visible to your clients in their portal
              </p>
              <div className="flex gap-2">
                <Input
                  type="tel"
                  placeholder="(555) 123-4567"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="flex-1"
                  data-testid="phone-input"
                />
                <Button
                  onClick={handleSavePhone}
                  disabled={savingPhone}
                  size="sm"
                  className="bg-gradient-to-r from-cyan-500 to-blue-500"
                  data-testid="save-phone-btn"
                >
                  {savingPhone ? 'Saving...' : 'Save'}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Licensed States */}
          <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
            <CardContent className="p-4">
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
                <MapPin className="h-4 w-4 text-cyan-500" /> Licensed States
                {licensedStates.length > 0 && <span className="ml-auto text-[10px] bg-cyan-100 dark:bg-cyan-900/30 text-cyan-700 dark:text-cyan-400 px-1.5 py-0.5 rounded-full">{licensedStates.length}</span>}
              </h3>
              
              {licensedStates.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-3">
                  {licensedStates.map((ls) => (
                    <div key={ls.state} className="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                      <span className="text-sm font-medium text-slate-900 dark:text-white">{ls.state}</span>
                      {ls.license_number && <span className="text-xs text-slate-400 font-mono">{ls.license_number}</span>}
                      <button onClick={() => handleRemoveState(ls.state)} className="p-0.5 hover:bg-red-100 dark:hover:bg-red-900/30 rounded">
                        <X className="h-3 w-3 text-red-500" />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              <div className="flex gap-2">
                <select
                  value={newState}
                  onChange={(e) => setNewState(e.target.value)}
                  className="flex-1 h-9 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 text-sm"
                >
                  <option value="">Select state</option>
                  {US_STATES.filter(s => !licensedStates.some(ls => ls.state === s)).map(state => (
                    <option key={state} value={state}>{state}</option>
                  ))}
                </select>
                <Input
                  placeholder="License # (opt)"
                  value={newLicenseNumber}
                  onChange={(e) => setNewLicenseNumber(e.target.value)}
                  className="w-32 h-9"
                />
                <Button size="sm" variant="outline" onClick={handleAddState} className="h-9 px-3">
                  <Plus className="h-4 w-4" />
                </Button>
              </div>

              <Button onClick={handleSaveLicensedStates} disabled={savingStates} size="sm" className="mt-3 bg-gradient-to-r from-cyan-500 to-blue-500">
                {savingStates ? 'Saving...' : 'Save States'}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Right Column - Password */}
        <div className="space-y-4">
          <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
            <CardContent className="p-4">
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
                <Key className="h-4 w-4 text-cyan-500" /> Change Password
              </h3>
              <form onSubmit={handlePasswordReset} className="space-y-3" data-testid="password-reset-form">
                <div className="space-y-1">
                  <Label className="text-xs">New Password</Label>
                  <Input
                    type="password"
                    placeholder="Min 8 characters"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                    className="h-9"
                    data-testid="new-password-input"
                  />
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Confirm Password</Label>
                  <Input
                    type="password"
                    placeholder="Re-enter"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    className="h-9"
                    data-testid="confirm-new-password-input"
                  />
                </div>
                <Button type="submit" disabled={updating} size="sm" className="w-full" data-testid="update-password-button">
                  {updating ? 'Updating...' : 'Update Password'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function InfoItem({ icon: Icon, label, value, mono, capitalize }) {
  return (
    <div className="py-2 px-3 rounded-lg bg-slate-50 dark:bg-slate-800">
      <div className="flex items-center gap-1.5 mb-0.5">
        {Icon && <Icon className="h-3 w-3 text-slate-400" />}
        <span className="text-[10px] text-slate-500 uppercase tracking-wide">{label}</span>
      </div>
      <span className={`text-sm text-slate-900 dark:text-white ${mono ? 'font-mono' : ''} ${capitalize ? 'capitalize' : ''}`}>{value}</span>
    </div>
  );
}
