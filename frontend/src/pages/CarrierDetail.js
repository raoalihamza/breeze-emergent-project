import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Card, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Switch } from '../components/ui/switch';
import { ChevronLeft, Building2, FileText, BookOpen, ExternalLink, CheckCircle, Circle, Save, Link as LinkIcon } from 'lucide-react';
import { toast } from 'sonner';
import { motion } from 'framer-motion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function CarrierDetail() {
  const { carrierId } = useParams();
  const navigate = useNavigate();
  const { getAuthHeader } = useAuth();
  
  const [carrier, setCarrier] = useState(null);
  const [settings, setSettings] = useState({ writing_number: '', is_appointed: false });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => { fetchData(); }, [carrierId]);

  const fetchData = async () => {
    try {
      const [carrierRes, settingsRes] = await Promise.all([
        axios.get(`${API}/carriers/${carrierId}`, getAuthHeader()),
        axios.get(`${API}/carriers/my-settings`, getAuthHeader())
      ]);
      setCarrier(carrierRes.data);
      const mySettings = settingsRes.data[carrierId] || { writing_number: '', is_appointed: false };
      setSettings({ writing_number: mySettings.writing_number || '', is_appointed: mySettings.is_appointed || false });
    } catch (error) {
      toast.error('Failed to load carrier');
      navigate('/carriers');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await axios.put(`${API}/carriers/my-settings`, {
        carrier_id: carrierId,
        writing_number: settings.writing_number || null,
        is_appointed: settings.is_appointed
      }, getAuthHeader());
      toast.success('Settings saved!');
      setHasChanges(false);
    } catch (error) {
      toast.error('Failed to save');
    } finally {
      setSaving(false);
    }
  };

  const updateSettings = (field, value) => {
    setSettings(prev => ({ ...prev, [field]: value }));
    setHasChanges(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-2 border-cyan-500 border-t-transparent"></div>
      </div>
    );
  }

  if (!carrier) {
    return (
      <div className="text-center py-12">
        <Building2 className="h-10 w-10 text-slate-300 mx-auto mb-3" />
        <p className="text-sm text-slate-500">Carrier not found</p>
        <Button onClick={() => navigate('/carriers')} size="sm" className="mt-3">Back</Button>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-5" data-testid="carrier-detail-page">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" onClick={() => navigate('/carriers')} className="h-8 px-2" data-testid="back-to-carriers">
          <ChevronLeft className="h-4 w-4" />
        </Button>
        <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="flex items-center gap-3 flex-1">
          <div className="w-16 h-16 rounded-lg flex items-center justify-center bg-white dark:bg-slate-800 border-2 border-slate-200 dark:border-slate-700 p-2">
            {carrier.logo_url ? (
              <img 
                src={carrier.logo_url} 
                alt={`${carrier.name} logo`}
                className="w-full h-full object-contain"
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.nextSibling.style.display = 'flex';
                }}
              />
            ) : null}
            <div
              className="w-full h-full rounded flex items-center justify-center text-white font-bold text-lg"
              style={{ 
                backgroundColor: carrier.primary_color,
                display: carrier.logo_url ? 'none' : 'flex'
              }}
            >
              {carrier.name.substring(0, 2).toUpperCase()}
            </div>
          </div>
          <div className="flex-1">
            <h1 className="text-xl font-bold text-slate-900 dark:text-white">{carrier.name}</h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">{carrier.description}</p>
          </div>
          <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
            settings.is_appointed
              ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
              : 'bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400'
          }`}>
            {settings.is_appointed ? <CheckCircle className="h-3.5 w-3.5" /> : <Circle className="h-3.5 w-3.5" />}
            {settings.is_appointed ? 'Appointed' : 'Not Appointed'}
          </div>
        </motion.div>
      </div>

      {/* Products */}
      {carrier.products && carrier.products.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {carrier.products.map((product, idx) => (
            <span
              key={idx}
              className="text-xs px-2 py-1 rounded-lg"
              style={{ backgroundColor: `${carrier.primary_color}15`, color: carrier.primary_color }}
            >
              {product}
            </span>
          ))}
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-4">
        {/* Settings Card */}
        <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50 lg:col-span-1">
          <CardContent className="p-4 space-y-4">
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white flex items-center gap-2">
              <div className="p-1.5 rounded-lg" style={{ backgroundColor: `${carrier.primary_color}15` }}>
                <Building2 className="h-3.5 w-3.5" style={{ color: carrier.primary_color }} />
              </div>
              My Settings
            </h3>

            <div className="flex items-center justify-between py-2">
              <div>
                <Label className="text-sm font-medium">Appointed</Label>
                <p className="text-[10px] text-slate-500">Mark if contracted</p>
              </div>
              <Switch
                checked={settings.is_appointed}
                onCheckedChange={(checked) => updateSettings('is_appointed', checked)}
                data-testid="appointed-switch"
              />
            </div>

            <div className="space-y-1.5">
              <Label className="text-xs">Writing Number</Label>
              <Input
                value={settings.writing_number}
                onChange={(e) => updateSettings('writing_number', e.target.value)}
                placeholder="Your agent ID"
                className="h-9"
                data-testid="writing-number-input"
              />
            </div>

            <Button
              onClick={handleSave}
              disabled={!hasChanges || saving}
              size="sm"
              className="w-full"
              style={hasChanges ? { backgroundColor: carrier.primary_color } : undefined}
              data-testid="save-settings-button"
            >
              <Save className="h-3.5 w-3.5 mr-1.5" />
              {saving ? 'Saving...' : 'Save'}
            </Button>
          </CardContent>
        </Card>

        {/* Resources & Portal */}
        <div className="lg:col-span-2 space-y-4">
          {/* Agent Portal */}
          {carrier.agent_portal_url && (
            <Card 
              className="border-0 overflow-hidden"
              style={{ 
                background: `linear-gradient(135deg, ${carrier.primary_color}, ${carrier.secondary_color || carrier.primary_color}dd)`,
              }}
            >
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-xl bg-white/20 backdrop-blur-sm">
                    <LinkIcon className="h-5 w-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-sm font-semibold text-white">Agent Portal</h3>
                    <p className="text-xs text-white/70">Access your carrier dashboard</p>
                  </div>
                  <Button
                    size="sm"
                    onClick={() => window.open(carrier.agent_portal_url, '_blank')}
                    className="bg-white/20 hover:bg-white/30 text-white border-0 backdrop-blur-sm h-9 px-4"
                    data-testid="agent-portal-button"
                  >
                    Open Portal <ExternalLink className="h-3.5 w-3.5 ml-1.5" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Resources */}
          <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
            <CardContent className="p-4">
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-3 flex items-center gap-2">
                <FileText className="h-4 w-4" style={{ color: carrier.primary_color }} />
                Resources
              </h3>

              {carrier.resources && carrier.resources.length > 0 ? (
                <div className="space-y-2">
                  {carrier.resources.map((resource, idx) => (
                    <a
                      key={idx}
                      href={resource.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-3 p-3 rounded-lg border border-slate-200 dark:border-slate-700 hover:border-cyan-500/50 transition-colors group"
                      data-testid={`resource-${idx}`}
                    >
                      <div className="p-1.5 rounded-lg" style={{ backgroundColor: `${carrier.primary_color}15` }}>
                        <FileText className="h-3.5 w-3.5" style={{ color: carrier.primary_color }} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-slate-900 dark:text-white group-hover:text-cyan-600 truncate">
                          {resource.name}
                        </div>
                        <div className="text-[10px] text-slate-500 capitalize">{resource.type?.replace('_', ' ')}</div>
                      </div>
                      <ExternalLink className="h-3.5 w-3.5 text-slate-400 group-hover:text-cyan-500" />
                    </a>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <FileText className="h-8 w-8 text-slate-300 dark:text-slate-600 mx-auto mb-2" />
                  <p className="text-xs text-slate-500">No resources available</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
