import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Building2, Search, CheckCircle, Circle, ChevronRight } from 'lucide-react';
import { motion } from 'framer-motion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function Carriers() {
  const { getAuthHeader } = useAuth();
  const navigate = useNavigate();
  const [carriers, setCarriers] = useState([]);
  const [mySettings, setMySettings] = useState({});
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterAppointed, setFilterAppointed] = useState('all');

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    try {
      const [carriersRes, settingsRes] = await Promise.all([
        axios.get(`${API}/carriers`, getAuthHeader()),
        axios.get(`${API}/carriers/my-settings`, getAuthHeader())
      ]);
      setCarriers(carriersRes.data);
      setMySettings(settingsRes.data);
    } catch (error) {
      console.error('Failed to load carriers:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredCarriers = carriers.filter(carrier => {
    const matchesSearch = carrier.name.toLowerCase().includes(searchTerm.toLowerCase());
    if (filterAppointed === 'appointed') return matchesSearch && mySettings[carrier.id]?.is_appointed;
    if (filterAppointed === 'not-appointed') return matchesSearch && !mySettings[carrier.id]?.is_appointed;
    return matchesSearch;
  });

  const sortedCarriers = [...filteredCarriers].sort((a, b) => {
    const aAppointed = mySettings[a.id]?.is_appointed ? 1 : 0;
    const bAppointed = mySettings[b.id]?.is_appointed ? 1 : 0;
    if (bAppointed !== aAppointed) return bAppointed - aAppointed;
    return a.name.localeCompare(b.name);
  });

  const appointedCount = carriers.filter(c => mySettings[c.id]?.is_appointed).length;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-2 border-cyan-500 border-t-transparent"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-5" data-testid="carriers-page">
      {/* Header */}
      <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="flex items-center gap-3">
        <div className="h-8 w-1 bg-gradient-to-b from-cyan-500 to-blue-500 rounded-full"></div>
        <div>
          <h1 className="text-xl font-bold text-slate-900 dark:text-white">Carriers</h1>
          <p className="text-xs text-slate-500 dark:text-slate-400">{carriers.length} carriers • {appointedCount} appointed</p>
        </div>
      </motion.div>

      {/* Stats Row */}
      <div className="grid grid-cols-3 gap-3">
        <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Total</span>
              <div className="p-1.5 rounded-lg bg-cyan-50 dark:bg-cyan-950/30">
                <Building2 className="h-3.5 w-3.5 text-cyan-600 dark:text-cyan-400" />
              </div>
            </div>
            <div className="text-2xl font-bold text-slate-900 dark:text-white">{carriers.length}</div>
          </CardContent>
        </Card>
        <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Appointed</span>
              <div className="p-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/30">
                <CheckCircle className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400" />
              </div>
            </div>
            <div className="text-2xl font-bold text-slate-900 dark:text-white">{appointedCount}</div>
          </CardContent>
        </Card>
        <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Pending</span>
              <div className="p-1.5 rounded-lg bg-amber-50 dark:bg-amber-950/30">
                <Circle className="h-3.5 w-3.5 text-amber-600 dark:text-amber-400" />
              </div>
            </div>
            <div className="text-2xl font-bold text-slate-900 dark:text-white">{carriers.length - appointedCount}</div>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-wrap items-center gap-2">
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <Input
            placeholder="Search carriers..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9 h-9 bg-white dark:bg-slate-900"
            data-testid="carrier-search"
          />
        </div>
        <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1">
          {[
            { key: 'all', label: 'All' },
            { key: 'appointed', label: 'Appointed' },
            { key: 'not-appointed', label: 'Pending' }
          ].map((filter) => (
            <button
              key={filter.key}
              onClick={() => setFilterAppointed(filter.key)}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all ${
                filterAppointed === filter.key
                  ? 'bg-white dark:bg-slate-700 text-cyan-600 dark:text-cyan-400 shadow-sm'
                  : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'
              }`}
            >
              {filter.label}
            </button>
          ))}
        </div>
        <span className="text-xs text-slate-500 ml-auto">{sortedCarriers.length} results</span>
      </div>

      {/* Carrier Grid */}
      {sortedCarriers.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {sortedCarriers.map((carrier, index) => {
            const settings = mySettings[carrier.id] || {};
            const isAppointed = settings.is_appointed;
            const writingNumber = settings.writing_number;
            
            return (
              <motion.div
                key={carrier.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.03 }}
              >
                <Card
                  className={`cursor-pointer transition-all duration-200 h-full overflow-hidden group ${
                    isAppointed
                      ? 'ring-1 ring-emerald-500/50 border-emerald-200 dark:border-emerald-800/50'
                      : 'border-slate-200/80 dark:border-slate-800/50 hover:border-cyan-500/50'
                  } bg-white dark:bg-slate-900/50`}
                  onClick={() => navigate(`/carriers/${carrier.id}`)}
                  data-testid={`carrier-card-${carrier.slug}`}
                >
                  <CardContent className="p-0">
                    {/* Color Bar */}
                    <div className="h-1.5 w-full" style={{ backgroundColor: carrier.primary_color }}></div>
                    
                    <div className="p-4">
                      <div className="flex items-start gap-3">
                        {/* Logo */}
                        <div className="w-12 h-12 rounded-lg flex items-center justify-center bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 flex-shrink-0 p-1.5">
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
                            className="w-full h-full rounded flex items-center justify-center text-white font-bold text-xs"
                            style={{ 
                              backgroundColor: carrier.primary_color,
                              display: carrier.logo_url ? 'none' : 'flex'
                            }}
                          >
                            {carrier.name.substring(0, 2).toUpperCase()}
                          </div>
                        </div>
                        
                        {/* Info */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-0.5">
                            <h3 className="font-semibold text-sm text-slate-900 dark:text-white group-hover:text-cyan-600 dark:group-hover:text-cyan-400 transition-colors truncate">
                              {carrier.name}
                            </h3>
                            {isAppointed && (
                              <CheckCircle className="h-3.5 w-3.5 text-emerald-500 flex-shrink-0" />
                            )}
                          </div>
                          
                          {/* Products */}
                          {carrier.products && carrier.products.length > 0 && (
                            <div className="flex flex-wrap gap-1 mb-2">
                              {carrier.products.slice(0, 3).map((product, idx) => (
                                <span
                                  key={idx}
                                  className="text-[10px] px-1.5 py-0.5 rounded"
                                  style={{
                                    backgroundColor: `${carrier.primary_color}15`,
                                    color: carrier.primary_color
                                  }}
                                >
                                  {product}
                                </span>
                              ))}
                              {carrier.products.length > 3 && (
                                <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-500">
                                  +{carrier.products.length - 3}
                                </span>
                              )}
                            </div>
                          )}
                          
                          {/* Writing Number or Status */}
                          <div className="text-xs text-slate-500 dark:text-slate-400">
                            {writingNumber ? (
                              <span className="font-mono">Writing #: {writingNumber}</span>
                            ) : isAppointed ? (
                              <span className="text-emerald-600 dark:text-emerald-400">Appointed</span>
                            ) : (
                              <span className="text-slate-400">Not appointed</span>
                            )}
                          </div>
                        </div>
                        
                        {/* Arrow */}
                        <ChevronRight className="h-4 w-4 text-slate-300 dark:text-slate-600 group-hover:text-cyan-500 transition-colors flex-shrink-0" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </div>
      ) : (
        <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
          <CardContent className="py-12 text-center">
            <Building2 className="h-10 w-10 text-slate-300 dark:text-slate-600 mx-auto mb-3" />
            <p className="text-sm text-slate-500 dark:text-slate-400">No carriers found</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
