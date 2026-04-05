import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Progress } from '../components/ui/progress';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '../components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '../components/ui/alert-dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../components/ui/dropdown-menu';
import {
  Database,
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Activity,
  Users,
  FileText,
  Search,
  ChevronLeft,
  ChevronRight,
  RotateCcw,
  UserCheck,
  Ban,
  Zap,
  ChevronDown,
} from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// ── Helpers ──────────────────────────────────────────────────────────────────
const formatTs = (ts) => {
  if (!ts) return '—';
  return new Date(ts).toLocaleString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
};

const timeAgo = (ts) => {
  if (!ts) return 'Never';
  const diff = Date.now() - new Date(ts).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'Just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
};

export default function ZinniaAdmin() {
  const { getAuthHeader } = useAuth();

  // ── Sync Status Tab ────────────────────────────────────────────────────────
  const [syncStatus, setSyncStatus] = useState(null);
  const [logs, setLogs] = useState([]);
  const [logsLoading, setLogsLoading] = useState(true);
  const [deepSyncDialogOpen, setDeepSyncDialogOpen] = useState(false);
  const [deepSyncing, setDeepSyncing] = useState(false);
  const [matchingStatus, setMatchingStatus] = useState(null);
  const [runningMatch, setRunningMatch] = useState(false);
  const [runningLinkProd, setRunningLinkProd] = useState(false);

  // ── Failed Syncs Tab ───────────────────────────────────────────────────────
  const [failedLogs, setFailedLogs] = useState([]);
  const [failedLoading, setFailedLoading] = useState(true);

  // ── Unmatched Tab ──────────────────────────────────────────────────────────
  const [unmatched, setUnmatched] = useState([]);
  const [unmatchedTotal, setUnmatchedTotal] = useState(0);
  const [unmatchedPage, setUnmatchedPage] = useState(1);
  const [unmatchedTotalPages, setUnmatchedTotalPages] = useState(1);
  const [unmatchedSearch, setUnmatchedSearch] = useState('');
  const [unmatchedLoading, setUnmatchedLoading] = useState(true);
  const [dismissedIds, setDismissedIds] = useState(new Set());
  const searchDebounceRef = useRef(null);

  // ── Matched Tab ────────────────────────────────────────────────────────────
  const [matched, setMatched] = useState([]);
  const [matchedTotal, setMatchedTotal] = useState(0);
  const [matchedPage, setMatchedPage] = useState(1);
  const [matchedTotalPages, setMatchedTotalPages] = useState(1);
  const [matchedSearch, setMatchedSearch] = useState('');
  const [matchedLoading, setMatchedLoading] = useState(true);
  const matchedSearchDebounceRef = useRef(null);

  // ── Match Modal ────────────────────────────────────────────────────────────
  const [matchModal, setMatchModal] = useState({ open: false, record: null });
  const [userSearch, setUserSearch] = useState('');
  const [userResults, setUserResults] = useState([]);
  const [userSearching, setUserSearching] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [matchingId, setMatchingId] = useState(null);
  const userSearchDebounceRef = useRef(null);

  // ── Derived: is any sync running right now? (server-driven) ───────────────
  const anySyncRunning = ['agents', 'production', 'cases'].some(
    (t) => syncStatus?.[t]?.is_running === true
  );

  // ── Data Fetchers ──────────────────────────────────────────────────────────
  const fetchSyncStatus = useCallback(async () => {
    try {
      const res = await fetch(`${API}/zinnia/sync/status`, {
        headers: getAuthHeader().headers,
      });
      if (res.ok) setSyncStatus(await res.json());
    } catch {}
  }, [getAuthHeader]);

  const fetchMatchingStatus = useCallback(async () => {
    try {
      const res = await fetch(`${API}/zinnia/match/status`, {
        headers: getAuthHeader().headers,
      });
      if (res.ok) setMatchingStatus(await res.json());
    } catch {}
  }, [getAuthHeader]);

  const fetchLogs = useCallback(async () => {
    setLogsLoading(true);
    try {
      const res = await fetch(`${API}/zinnia/logs?since=2025-11-01T00:00:00&limit=100`, {
        headers: getAuthHeader().headers,
      });
      if (res.ok) setLogs(await res.json());
    } catch {
      toast.error('Failed to load sync logs');
    } finally {
      setLogsLoading(false);
    }
  }, [getAuthHeader]);

  const fetchFailedLogs = useCallback(async () => {
    setFailedLoading(true);
    try {
      const res = await fetch(
        `${API}/zinnia/logs?since=2025-11-01T00:00:00&status=failed&limit=100`,
        { headers: getAuthHeader().headers }
      );
      if (res.ok) setFailedLogs(await res.json());
    } catch {
      toast.error('Failed to load failed syncs');
    } finally {
      setFailedLoading(false);
    }
  }, [getAuthHeader]);

  const fetchUnmatched = useCallback(async (page = 1, search = '') => {
    setUnmatchedLoading(true);
    try {
      const params = new URLSearchParams({ page, page_size: 25 });
      if (search) params.set('search', search);
      const res = await fetch(`${API}/zinnia/unmatched?${params}`, {
        headers: getAuthHeader().headers,
      });
      if (res.ok) {
        const data = await res.json();
        setUnmatched(data.data || []);
        setUnmatchedTotal(data.total || 0);
        setUnmatchedTotalPages(data.total_pages || 1);
      }
    } catch {
      toast.error('Failed to load unmatched records');
    } finally {
      setUnmatchedLoading(false);
    }
  }, [getAuthHeader]);

  const fetchMatched = useCallback(async (page = 1, search = '') => {
    setMatchedLoading(true);
    try {
      const params = new URLSearchParams({ page, page_size: 25 });
      if (search) params.set('search', search);
      const res = await fetch(`${API}/zinnia/matched?${params}`, {
        headers: getAuthHeader().headers,
      });
      if (res.ok) {
        const data = await res.json();
        setMatched(data.data || []);
        setMatchedTotal(data.total || 0);
        setMatchedTotalPages(data.total_pages || 1);
      }
    } catch {
      toast.error('Failed to load matched agents');
    } finally {
      setMatchedLoading(false);
    }
  }, [getAuthHeader]);

  // ── Initial load ───────────────────────────────────────────────────────────
  useEffect(() => {
    fetchSyncStatus();
    fetchLogs();
    fetchFailedLogs();
    fetchUnmatched(1, '');
    fetchMatched(1, '');
    fetchMatchingStatus();
    return () => {
      clearTimeout(searchDebounceRef.current);
      clearTimeout(matchedSearchDebounceRef.current);
      clearTimeout(userSearchDebounceRef.current);
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Adaptive polling: 5s when syncing/matching, 30s when idle ────────────
  const anyMatchingRunning = matchingStatus?.status === 'running';

  useEffect(() => {
    const interval = (anySyncRunning || anyMatchingRunning) ? 5000 : 30000;
    const id = setInterval(() => {
      fetchSyncStatus();
      fetchMatchingStatus();
    }, interval);
    return () => clearInterval(id);
  }, [anySyncRunning, anyMatchingRunning, fetchSyncStatus, fetchMatchingStatus]);

  // ── Refresh — re-fetch everything from our DB only ─────────────────────────
  const handleRefresh = async () => {
    await Promise.all([
      fetchSyncStatus(),
      fetchMatchingStatus(),
      fetchLogs(),
      fetchFailedLogs(),
      fetchUnmatched(unmatchedPage, unmatchedSearch),
      fetchMatched(matchedPage, matchedSearch),
    ]);
    toast.success('Data refreshed from database');
  };

  // ── Deep Sync — triggers SmartOffice re-fetch (fire-and-forget) ───────────
  const handleDeepSync = async () => {
    setDeepSyncing(true);
    try {
      const res = await fetch(`${API}/zinnia/sync/deep`, {
        method: 'POST',
        headers: getAuthHeader().headers,
      });
      const data = await res.json();
      if (res.ok && data.status === 'started') {
        toast.success('Deep sync started — running in background');
        setDeepSyncDialogOpen(false);
        await fetchSyncStatus();
      } else if (data.status === 'already_running') {
        toast.error(`Sync already in progress: ${data.message}`);
        setDeepSyncDialogOpen(false);
      } else {
        toast.error('Failed to start deep sync');
      }
    } catch {
      toast.error('Failed to start deep sync');
    } finally {
      setDeepSyncing(false);
    }
  };

  // ── Retry (Failed Syncs tab) — refreshes data from DB only ────────────────
  const handleRetry = async () => {
    await Promise.all([fetchFailedLogs(), fetchLogs(), fetchSyncStatus()]);
    toast.success('Data refreshed from database');
  };

  // ── Run Matching (DB only — no SmartOffice call) ───────────────────────────
  const handleRunMatching = async () => {
    setRunningMatch(true);
    try {
      const res = await fetch(`${API}/zinnia/match/agents`, {
        method: 'POST',
        headers: getAuthHeader().headers,
      });
      const data = await res.json();
      if (res.ok && data.status === 'started') {
        toast.success('Agent matching started in background');
        await fetchMatchingStatus();
      } else if (data.status === 'already_running') {
        toast.error('Matching is already in progress');
      } else {
        toast.error('Failed to start matching');
      }
    } catch {
      toast.error('Failed to start matching');
    } finally {
      setRunningMatch(false);
    }
  };

  // ── Link Production to Agents ─────────────────────────────────────────────
  const handleLinkProduction = async () => {
    setRunningLinkProd(true);
    try {
      const res = await fetch(`${API}/zinnia/link/production`, {
        method: 'POST',
        headers: getAuthHeader().headers,
      });
      const data = await res.json();
      if (res.ok) {
        toast.success(`Matched ${data.matched_policy_number + data.matched_name_fuzzy} out of ${data.total} policies`);
      } else {
        toast.error('Failed to link production');
      }
    } catch {
      toast.error('Failed to link production');
    } finally {
      setRunningLinkProd(false);
    }
  };

  // ── Unmatched search / pagination ─────────────────────────────────────────
  const handleUnmatchedSearch = (val) => {
    setUnmatchedSearch(val);
    setUnmatchedPage(1);
    clearTimeout(searchDebounceRef.current);
    searchDebounceRef.current = setTimeout(() => fetchUnmatched(1, val), 300);
  };

  const handleUnmatchedPageChange = (newPage) => {
    setUnmatchedPage(newPage);
    fetchUnmatched(newPage, unmatchedSearch);
  };

  // ── Matched search / pagination ───────────────────────────────────────────
  const handleMatchedSearch = (val) => {
    setMatchedSearch(val);
    setMatchedPage(1);
    clearTimeout(matchedSearchDebounceRef.current);
    matchedSearchDebounceRef.current = setTimeout(() => fetchMatched(1, val), 300);
  };

  const handleMatchedPageChange = (newPage) => {
    setMatchedPage(newPage);
    fetchMatched(newPage, matchedSearch);
  };

  // ── Dismiss ────────────────────────────────────────────────────────────────
  const handleDismiss = async (record) => {
    try {
      const res = await fetch(`${API}/zinnia/unmatched/${record.smartoffice_id}/dismiss`, {
        method: 'POST',
        headers: getAuthHeader().headers,
      });
      if (res.ok) {
        setDismissedIds((prev) => new Set([...prev, record.smartoffice_id]));
        toast.success(`${record.first_name} ${record.last_name} dismissed`);
      } else {
        toast.error('Failed to dismiss');
      }
    } catch {
      toast.error('Failed to dismiss');
    }
  };

  // ── Match Modal ────────────────────────────────────────────────────────────
  const openMatchModal = (record) => {
    setMatchModal({ open: true, record });
    setUserSearch('');
    setUserResults([]);
    setUserSearching(false);
    setSelectedUser(null);
  };

  const handleUserSearch = (val) => {
    setUserSearch(val);
    setSelectedUser(null);
    clearTimeout(userSearchDebounceRef.current);
    if (!val.trim()) { setUserResults([]); setUserSearching(false); return; }
    setUserSearching(true);
    userSearchDebounceRef.current = setTimeout(async () => {
      try {
        const res = await fetch(
          `${API}/zinnia/users/search?q=${encodeURIComponent(val)}`,
          { headers: getAuthHeader().headers }
        );
        if (res.ok) setUserResults(await res.json());
        else setUserResults([]);
      } catch {
        setUserResults([]);
      } finally {
        setUserSearching(false);
      }
    }, 300);
  };

  const handleConfirmMatch = async () => {
    if (!selectedUser || !matchModal.record) return;
    setMatchingId(matchModal.record.smartoffice_id);
    try {
      const res = await fetch(
        `${API}/zinnia/unmatched/${matchModal.record.smartoffice_id}/match`,
        {
          method: 'POST',
          headers: { ...getAuthHeader().headers, 'Content-Type': 'application/json' },
          body: JSON.stringify({ atlas_user_id: selectedUser.id }),
        }
      );
      if (res.ok) {
        toast.success(`Matched to ${selectedUser.name}`);
        setMatchModal({ open: false, record: null });
        fetchUnmatched(unmatchedPage, unmatchedSearch);
      } else {
        toast.error('Match failed');
      }
    } catch {
      toast.error('Match failed');
    } finally {
      setMatchingId(null);
    }
  };

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <div className="max-w-6xl mx-auto space-y-5">

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        className="flex items-center justify-between"
      >
        <div className="flex items-center gap-3">
          <div className="h-8 w-1 bg-gradient-to-b from-cyan-500 to-blue-500 rounded-full" />
          <div>
            <h1 className="text-xl font-bold text-slate-900 dark:text-white">Zinnia Admin</h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              SmartOffice sync monitoring &amp; agent matching
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Live status badge */}
          <span className={`flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full ${
            anySyncRunning
              ? 'bg-cyan-500/20 text-cyan-400'
              : 'bg-slate-500/20 text-slate-400'
          }`}>
            <span className={`w-1.5 h-1.5 rounded-full ${
              anySyncRunning ? 'bg-cyan-400 animate-pulse' : 'bg-slate-400'
            }`} />
            {anySyncRunning ? 'Syncing...' : 'Idle'}
          </span>

          {/* Refresh + Deep Sync dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                size="sm"
                className="bg-cyan-600 hover:bg-cyan-700 text-white gap-1.5"
                disabled={deepSyncing}
              >
                <RefreshCw className="h-3.5 w-3.5" />
                Refresh
                <ChevronDown className="h-3 w-3 opacity-70" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-52 dark:bg-slate-900 dark:border-slate-700">
              <DropdownMenuItem
                onClick={handleRefresh}
                className="gap-2 cursor-pointer"
              >
                <div>
                  <div className="text-sm font-medium">Refresh</div>
                  <div className="text-xs text-slate-500 dark:text-slate-400">Reload data from database</div>
                </div>
              </DropdownMenuItem>
              <DropdownMenuSeparator className="dark:bg-slate-700" />
              <DropdownMenuItem
                onClick={() => setDeepSyncDialogOpen(true)}
                disabled={anySyncRunning}
                className="gap-2 cursor-pointer"
              >
                <div>
                  <div className="text-sm font-medium">Deep Sync</div>
                  <div className="text-xs text-slate-500 dark:text-slate-400">
                    {anySyncRunning ? 'Sync in progress...' : 'Re-fetch from SmartOffice'}
                  </div>
                </div>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </motion.div>

      {/* Tabs */}
      <Tabs defaultValue="sync-status" className="w-full">
        <TabsList className="bg-slate-100 dark:bg-slate-800 p-1 h-auto">
          <TabsTrigger
            value="sync-status"
            className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-700 data-[state=active]:text-cyan-600 dark:data-[state=active]:text-cyan-400 px-4 py-2 text-sm"
          >
            <Activity className="h-4 w-4 mr-1.5" />
            Sync Status
          </TabsTrigger>
          <TabsTrigger
            value="failed"
            className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-700 data-[state=active]:text-cyan-600 dark:data-[state=active]:text-cyan-400 px-4 py-2 text-sm"
          >
            <AlertTriangle className="h-4 w-4 mr-1.5" />
            Failed Syncs
            {failedLogs.length > 0 && (
              <span className="ml-1.5 bg-red-500/20 text-red-400 text-xs px-1.5 py-0.5 rounded-full">
                {failedLogs.length}
              </span>
            )}
          </TabsTrigger>
          <TabsTrigger
            value="unmatched"
            className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-700 data-[state=active]:text-cyan-600 dark:data-[state=active]:text-cyan-400 px-4 py-2 text-sm"
          >
            <Users className="h-4 w-4 mr-1.5" />
            Unmatched Records
            {unmatchedTotal > 0 && (
              <span className="ml-1.5 bg-amber-500/20 text-amber-400 text-xs px-1.5 py-0.5 rounded-full">
                {unmatchedTotal.toLocaleString()}
              </span>
            )}
          </TabsTrigger>
          <TabsTrigger
            value="matched"
            className="data-[state=active]:bg-white dark:data-[state=active]:bg-slate-700 data-[state=active]:text-cyan-600 dark:data-[state=active]:text-cyan-400 px-4 py-2 text-sm"
          >
            <UserCheck className="h-4 w-4 mr-1.5" />
            Matched Agents
            {matchedTotal > 0 && (
              <span className="ml-1.5 bg-green-500/20 text-green-400 text-xs px-1.5 py-0.5 rounded-full">
                {matchedTotal.toLocaleString()}
              </span>
            )}
          </TabsTrigger>
        </TabsList>

        {/* ── TAB 1: Sync Status ─────────────────────────────────────────────── */}
        <TabsContent value="sync-status" className="mt-4 space-y-4">

          {/* Stat Cards */}
          {!syncStatus && (
            <div className="flex items-center justify-center py-10">
              <div className="animate-spin rounded-full h-6 w-6 border-2 border-cyan-500 border-t-transparent" />
            </div>
          )}
          {syncStatus && <div className="grid grid-cols-3 gap-3 items-stretch" style={{ gridTemplateColumns: 'repeat(3, minmax(0, 1fr))' }}>
            {[
              { type: 'agents',     label: 'Agents',     icon: Users },
              { type: 'production', label: 'Policies',   icon: FileText },
              { type: 'cases',      label: 'Activities', icon: Database },
            ].map(({ type, label, icon: Icon }, i) => {
              const typeStatus  = syncStatus?.[type];
              const dbCount     = typeStatus?.total_records;
              const isRunning   = typeStatus?.is_running === true;
              const progress    = typeStatus?.progress || {};
              const lastSyncTs  = typeStatus?.last_sync_time;

              return (
                <motion.div
                  key={type}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="w-full min-w-0 h-full"
                >
                  <Card className="w-full h-full border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">
                          {label}
                        </span>
                        <div className={`p-1.5 rounded-lg ${
                          isRunning
                            ? 'bg-cyan-500/20'
                            : 'bg-cyan-50 dark:bg-cyan-950/30'
                        }`}>
                          <Icon className={`h-3.5 w-3.5 ${
                            isRunning
                              ? 'text-cyan-400 animate-pulse'
                              : 'text-cyan-600 dark:text-cyan-400'
                          }`} />
                        </div>
                      </div>

                      <div className="text-2xl font-bold text-slate-900 dark:text-white">
                        {dbCount != null ? dbCount.toLocaleString() : '—'}
                      </div>

                      {/* Last synced time */}
                      <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                        {isRunning
                          ? 'Syncing now...'
                          : `Last synced: ${timeAgo(lastSyncTs)}`
                        }
                      </p>

                      {/* Live progress bar */}
                      {isRunning && progress.total_pages > 0 && (
                        <div className="mt-2 space-y-1">
                          <Progress
                            value={progress.percent || 0}
                            className="h-1.5 bg-slate-200 dark:bg-slate-700"
                          />
                          <p className="text-xs text-cyan-500 dark:text-cyan-400">
                            Page {progress.current_page?.toLocaleString()} /{' '}
                            {progress.total_pages?.toLocaleString()} &nbsp;·&nbsp;
                            {progress.percent}%
                          </p>
                        </div>
                      )}

                      {/* Idle: show last run fetch count */}
                      {!isRunning && typeStatus?.last_sync_fetched > 0 && (
                        <p className="text-xs text-cyan-600 dark:text-cyan-500 mt-0.5">
                          Last run fetched {typeStatus.last_sync_fetched.toLocaleString()}
                        </p>
                      )}
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </div>}

          {/* Matching Status Card */}
          <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`p-1.5 rounded-lg ${matchingStatus?.status === 'running' ? 'bg-violet-500/20' : 'bg-violet-50 dark:bg-violet-950/30'}`}>
                    <UserCheck className={`h-3.5 w-3.5 ${matchingStatus?.status === 'running' ? 'text-violet-400 animate-pulse' : 'text-violet-500 dark:text-violet-400'}`} />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-slate-900 dark:text-white">Agent Matching</p>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      {matchingStatus?.status === 'running'
                        ? `Running... ${matchingStatus.total_processed?.toLocaleString() ?? 0} processed`
                        : matchingStatus?.status === 'complete'
                        ? `Last run: ${matchingStatus.matched_by_npn ?? 0} NPN · ${matchingStatus.matched_by_name ?? 0} name · ${matchingStatus.unmatched ?? 0} unmatched`
                        : 'Links SmartOffice agents to Atlas users (DB only)'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={handleRunMatching}
                    disabled={runningMatch || matchingStatus?.status === 'running'}
                    className="h-8 text-xs border-violet-500/40 text-violet-600 dark:text-violet-400 hover:bg-violet-500/10"
                  >
                    {runningMatch || matchingStatus?.status === 'running' ? (
                      <><RefreshCw className="h-3 w-3 mr-1.5 animate-spin" /> Running...</>
                    ) : (
                      <><UserCheck className="h-3 w-3 mr-1.5" /> Run Matching</>
                    )}
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={handleLinkProduction}
                    disabled={runningLinkProd}
                    className="h-8 text-xs border-cyan-500/40 text-cyan-600 dark:text-cyan-400 hover:bg-cyan-500/10"
                  >
                    {runningLinkProd ? (
                      <><RefreshCw className="h-3 w-3 mr-1.5 animate-spin" /> Linking...</>
                    ) : (
                      <><FileText className="h-3 w-3 mr-1.5" /> Link Production</>
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Sync History Table */}
          <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
            <CardHeader className="pb-3 pt-5 px-5">
              <CardTitle className="text-sm font-semibold text-slate-900 dark:text-white">
                Sync History (since Nov 2025)
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {logsLoading ? (
                <div className="flex items-center justify-center py-10">
                  <div className="animate-spin rounded-full h-6 w-6 border-2 border-cyan-500 border-t-transparent" />
                </div>
              ) : logs.length === 0 ? (
                <div className="text-center py-10 text-slate-500 dark:text-slate-400 text-sm">
                  No sync history found
                </div>
              ) : (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-200/80 dark:border-slate-800/50">
                      <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Type</th>
                      <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Status</th>
                      <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Records</th>
                      <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Timestamp</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logs.map((log, idx) => (
                      <tr
                        key={log.id || idx}
                        className="border-b border-slate-100 dark:border-slate-800/30 hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors"
                      >
                        <td className="px-5 py-3 text-slate-900 dark:text-white capitalize">{log.sync_type}</td>
                        <td className="px-5 py-3">
                          {log.status === 'success' ? (
                            <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-green-500/10 text-green-500">
                              <CheckCircle className="h-3 w-3" /> Success
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-red-500/10 text-red-500">
                              <XCircle className="h-3 w-3" /> Failed
                            </span>
                          )}
                        </td>
                        <td className="px-5 py-3 text-slate-600 dark:text-slate-300">
                          {log.details?.total_fetched?.toLocaleString() ?? log.details?.error ?? '—'}
                        </td>
                        <td className="px-5 py-3 text-slate-500 dark:text-slate-400 text-xs">
                          {formatTs(log.timestamp)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ── TAB 2: Failed Syncs ───────────────────────────────────────────── */}
        <TabsContent value="failed" className="mt-4">
          <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
            <CardHeader className="pb-3 pt-5 px-5 flex flex-row items-center justify-between">
              <CardTitle className="text-sm font-semibold text-slate-900 dark:text-white">
                Failed Syncs (since Nov 2025)
              </CardTitle>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Failures are retried automatically by the cron scheduler.
              </p>
            </CardHeader>
            <CardContent className="p-0">
              {failedLoading ? (
                <div className="flex items-center justify-center py-10">
                  <div className="animate-spin rounded-full h-6 w-6 border-2 border-cyan-500 border-t-transparent" />
                </div>
              ) : failedLogs.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-14 gap-2">
                  <CheckCircle className="h-10 w-10 text-green-500/60" />
                  <p className="text-slate-500 dark:text-slate-400 text-sm">No failed syncs</p>
                </div>
              ) : (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-200/80 dark:border-slate-800/50">
                      <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Type</th>
                      <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Error</th>
                      <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Timestamp</th>
                      <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {failedLogs.map((log, idx) => (
                      <tr
                        key={log.id || idx}
                        className="border-b border-slate-100 dark:border-slate-800/30 hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors"
                      >
                        <td className="px-5 py-3">
                          <span className="capitalize text-slate-900 dark:text-white font-medium">{log.sync_type}</span>
                        </td>
                        <td className="px-5 py-3 text-red-500 dark:text-red-400 max-w-xs truncate text-xs">
                          {log.details?.error || 'Unknown error'}
                        </td>
                        <td className="px-5 py-3 text-slate-500 dark:text-slate-400 text-xs">
                          {formatTs(log.timestamp)}
                        </td>
                        <td className="px-5 py-3">
                          {/* Refresh from DB — does NOT call SmartOffice */}
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={handleRetry}
                            className="h-7 text-xs"
                          >
                            <RotateCcw className="h-3 w-3 mr-1" />
                            Refresh
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ── TAB 3: Unmatched Records ──────────────────────────────────────── */}
        <TabsContent value="unmatched" className="mt-4 space-y-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <Input
              value={unmatchedSearch}
              onChange={(e) => handleUnmatchedSearch(e.target.value)}
              placeholder="Search by name or NPN..."
              className="pl-9 bg-white dark:bg-slate-900/50 border-slate-200/80 dark:border-slate-800/50"
            />
          </div>

          <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
            <CardContent className="p-0">
              {unmatchedLoading ? (
                <div className="flex items-center justify-center py-10">
                  <div className="animate-spin rounded-full h-6 w-6 border-2 border-cyan-500 border-t-transparent" />
                </div>
              ) : unmatched.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-14 gap-2">
                  <UserCheck className="h-10 w-10 text-cyan-500/60" />
                  <p className="text-slate-500 dark:text-slate-400 text-sm">No unmatched records</p>
                </div>
              ) : (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-200/80 dark:border-slate-800/50">
                      <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Name</th>
                      <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">NPN</th>
                      <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Type</th>
                      <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Reason</th>
                      <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {unmatched.map((record, idx) => {
                      const dismissed = dismissedIds.has(record.smartoffice_id);
                      return (
                        <tr
                          key={record.smartoffice_id || idx}
                          className={`border-b border-slate-100 dark:border-slate-800/30 transition-colors ${
                            dismissed ? 'opacity-40' : 'hover:bg-slate-50 dark:hover:bg-slate-800/30'
                          }`}
                        >
                          <td className="px-5 py-3 text-slate-900 dark:text-white font-medium">
                            {record.first_name} {record.last_name}
                          </td>
                          <td className="px-5 py-3 text-slate-500 dark:text-slate-400 text-xs font-mono">
                            {record.npn || <span className="text-slate-400 italic">none</span>}
                          </td>
                          <td className="px-5 py-3 text-slate-600 dark:text-slate-300 text-xs capitalize">
                            {record.contact_type || '—'}
                          </td>
                          <td className="px-5 py-3 max-w-xs">
                            <span className="text-xs text-amber-600 dark:text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full">
                              {record.reason}
                            </span>
                          </td>
                          <td className="px-5 py-3">
                            <div className="flex items-center gap-2">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => openMatchModal(record)}
                                disabled={dismissed}
                                className="h-7 text-xs border-cyan-500/50 text-cyan-600 dark:text-cyan-400 hover:bg-cyan-500/10"
                              >
                                <UserCheck className="h-3 w-3 mr-1" />
                                Match
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleDismiss(record)}
                                disabled={dismissed}
                                className="h-7 text-xs border-slate-300/50 text-slate-500 dark:text-slate-400 hover:bg-slate-500/10"
                              >
                                <Ban className="h-3 w-3 mr-1" />
                                Dismiss
                              </Button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              )}
            </CardContent>
          </Card>

          {unmatchedTotalPages > 1 && (
            <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
              <span>
                Showing {((unmatchedPage - 1) * 25) + 1}–{Math.min(unmatchedPage * 25, unmatchedTotal)} of{' '}
                {unmatchedTotal.toLocaleString()} records
              </span>
              <div className="flex items-center gap-1">
                <Button size="sm" variant="outline" onClick={() => handleUnmatchedPageChange(unmatchedPage - 1)} disabled={unmatchedPage === 1} className="h-7 w-7 p-0">
                  <ChevronLeft className="h-3.5 w-3.5" />
                </Button>
                <span className="px-2">{unmatchedPage} / {unmatchedTotalPages}</span>
                <Button size="sm" variant="outline" onClick={() => handleUnmatchedPageChange(unmatchedPage + 1)} disabled={unmatchedPage === unmatchedTotalPages} className="h-7 w-7 p-0">
                  <ChevronRight className="h-3.5 w-3.5" />
                </Button>
              </div>
            </div>
          )}
        </TabsContent>

        {/* ── TAB 4: Matched Agents ─────────────────────────────────────────── */}
        <TabsContent value="matched" className="mt-4 space-y-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <Input
              value={matchedSearch}
              onChange={(e) => handleMatchedSearch(e.target.value)}
              placeholder="Search by name or NPN..."
              className="pl-9 bg-white dark:bg-slate-900/50 border-slate-200/80 dark:border-slate-800/50"
            />
          </div>

          <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white dark:bg-slate-900/50">
            <CardContent className="p-0">
              {matchedLoading ? (
                <div className="flex items-center justify-center py-10">
                  <div className="animate-spin rounded-full h-6 w-6 border-2 border-cyan-500 border-t-transparent" />
                </div>
              ) : matched.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-14 gap-2">
                  <UserCheck className="h-10 w-10 text-slate-400/40" />
                  <p className="text-slate-500 dark:text-slate-400 text-sm">No matched agents yet</p>
                  <p className="text-slate-400 dark:text-slate-500 text-xs">Run agent matching to link SmartOffice contacts to Atlas users</p>
                </div>
              ) : (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-200/80 dark:border-slate-800/50">
                      <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Name</th>
                      <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">NPN</th>
                      <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Match Type</th>
                      <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Atlas User ID</th>
                      <th className="text-left px-5 py-3 text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Matched At</th>
                    </tr>
                  </thead>
                  <tbody>
                    {matched.map((agent, idx) => (
                      <tr
                        key={agent.smartoffice_id || idx}
                        className="border-b border-slate-100 dark:border-slate-800/30 hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors"
                      >
                        <td className="px-5 py-3 text-slate-900 dark:text-white font-medium">
                          {agent.first_name} {agent.last_name}
                        </td>
                        <td className="px-5 py-3 text-slate-500 dark:text-slate-400 text-xs font-mono">
                          {agent.npn || <span className="italic text-slate-400">none</span>}
                        </td>
                        <td className="px-5 py-3">
                          {agent.match_type === 'npn' && (
                            <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-500">NPN</span>
                          )}
                          {agent.match_type === 'name_exact' && (
                            <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400">Name Exact</span>
                          )}
                          {agent.match_type?.startsWith('name_fuzzy') && (
                            <span className="text-xs px-2 py-0.5 rounded-full bg-violet-500/10 text-violet-400">
                              Fuzzy {agent.match_type.split(':')[1] ? `(${Math.round(agent.match_type.split(':')[1] * 100)}%)` : ''}
                            </span>
                          )}
                          {agent.match_type === 'manual' && (
                            <span className="text-xs px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400">Manual</span>
                          )}
                          {!agent.match_type && <span className="text-slate-400">—</span>}
                        </td>
                        <td className="px-5 py-3 text-slate-500 dark:text-slate-400 text-xs font-mono truncate max-w-[160px]">
                          {agent.atlas_user_id || '—'}
                        </td>
                        <td className="px-5 py-3 text-slate-500 dark:text-slate-400 text-xs">
                          {formatTs(agent.matched_at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </CardContent>
          </Card>

          {matchedTotalPages > 1 && (
            <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
              <span>
                Showing {((matchedPage - 1) * 25) + 1}–{Math.min(matchedPage * 25, matchedTotal)} of{' '}
                {matchedTotal.toLocaleString()} records
              </span>
              <div className="flex items-center gap-1">
                <Button size="sm" variant="outline" onClick={() => handleMatchedPageChange(matchedPage - 1)} disabled={matchedPage === 1} className="h-7 w-7 p-0">
                  <ChevronLeft className="h-3.5 w-3.5" />
                </Button>
                <span className="px-2">{matchedPage} / {matchedTotalPages}</span>
                <Button size="sm" variant="outline" onClick={() => handleMatchedPageChange(matchedPage + 1)} disabled={matchedPage === matchedTotalPages} className="h-7 w-7 p-0">
                  <ChevronRight className="h-3.5 w-3.5" />
                </Button>
              </div>
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* ── Deep Sync Confirmation Dialog ─────────────────────────────────── */}
      <AlertDialog open={deepSyncDialogOpen} onOpenChange={setDeepSyncDialogOpen}>
        <AlertDialogContent className="dark:bg-slate-900 dark:border-slate-700 max-w-md">
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2 text-slate-900 dark:text-white">
              <Zap className="h-5 w-5 text-amber-500" />
              Deep Sync - SmartOffice Re-fetch
            </AlertDialogTitle>
            <AlertDialogDescription asChild>
              <div className="space-y-3 text-sm">
                <p className="text-slate-600 dark:text-slate-300">
                  This will fetch fresh data directly from SmartOffice and update your database.
                </p>
                <div className="rounded-lg bg-amber-500/10 border border-amber-500/20 p-3 space-y-1.5">
                  <p className="text-amber-600 dark:text-amber-400 font-medium text-xs uppercase tracking-wide">
                    Before you proceed
                  </p>
                  <ul className="text-xs text-slate-600 dark:text-slate-300 space-y-1 list-disc list-inside">
                    <li>Estimated time: <strong>30–60 minutes</strong></li>
                    <li>App remains fully functional during sync</li>
                    <li>Existing data stays visible throughout</li>
                    <li>All other features work normally</li>
                    <li>Some records may appear outdated until sync completes</li>
                    <li>Use only when cron has failed or urgent refresh needed</li>
                  </ul>
                </div>
              </div>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel
              className="dark:bg-slate-800 dark:border-slate-700 dark:text-white dark:hover:bg-slate-700"
              disabled={deepSyncing}
            >
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeepSync}
              disabled={deepSyncing}
              className="bg-amber-600 hover:bg-amber-700 text-white"
            >
              {deepSyncing ? (
                <><RefreshCw className="h-3.5 w-3.5 mr-1.5 animate-spin" /> Starting...</>
              ) : (
                <>Start Deep Sync</>
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* ── Match Modal ───────────────────────────────────────────────────── */}
      <Dialog open={matchModal.open} onOpenChange={(o) => !o && setMatchModal({ open: false, record: null })}>
        <DialogContent className="bg-white dark:bg-slate-900 border-slate-200/80 dark:border-slate-800/50 max-w-md">
          <DialogHeader>
            <DialogTitle className="text-slate-900 dark:text-white">
              Match Agent to Atlas User
            </DialogTitle>
          </DialogHeader>

          {matchModal.record && (
            <div className="space-y-4">
              <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/50 text-sm">
                <p className="text-slate-900 dark:text-white font-medium">
                  {matchModal.record.first_name} {matchModal.record.last_name}
                </p>
                <p className="text-slate-500 dark:text-slate-400 text-xs mt-0.5">
                  NPN: {matchModal.record.npn || 'none'} · {matchModal.record.contact_type}
                </p>
              </div>

              <div className="space-y-2">
                <label className="text-xs font-medium text-slate-700 dark:text-slate-300">
                  Search Atlas Users
                </label>
                <div className="relative">
                  {userSearching ? (
                    <div className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 rounded-full border-2 border-cyan-500 border-t-transparent animate-spin" />
                  ) : (
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                  )}
                  <Input
                    value={userSearch}
                    onChange={(e) => handleUserSearch(e.target.value)}
                    placeholder="Search by name or NPN..."
                    className="pl-9 bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700"
                  />
                </div>

                {/* Results list */}
                {!userSearching && userResults.length > 0 && (
                  <div className="border border-slate-200 dark:border-slate-700 rounded-lg overflow-hidden">
                    {userResults.map((u) => (
                      <button
                        key={u.id}
                        onClick={() => { setSelectedUser(u); setUserResults([]); setUserSearch(u.name); }}
                        className={`w-full text-left px-3 py-2.5 text-sm hover:bg-slate-50 dark:hover:bg-slate-800/50 border-b last:border-0 border-slate-100 dark:border-slate-700/50 transition-colors ${
                          selectedUser?.id === u.id ? 'bg-cyan-50 dark:bg-cyan-950/30' : ''
                        }`}
                      >
                        <span className="text-slate-900 dark:text-white font-medium">{u.name}</span>
                        <span className="text-slate-500 dark:text-slate-400 text-xs ml-2">{u.email}</span>
                        {u.npn && (
                          <span className="text-slate-400 dark:text-slate-500 text-xs ml-2 font-mono">NPN: {u.npn}</span>
                        )}
                      </button>
                    ))}
                  </div>
                )}

                {/* No results state */}
                {!userSearching && userSearch.trim() && userResults.length === 0 && !selectedUser && (
                  <p className="text-xs text-slate-500 dark:text-slate-400 px-1">
                    No Atlas users found for &quot;{userSearch}&quot;
                  </p>
                )}

                {selectedUser && (
                  <div className="flex items-center gap-2 p-2 rounded-lg bg-cyan-50 dark:bg-cyan-950/30 text-xs text-cyan-700 dark:text-cyan-400">
                    <CheckCircle className="h-3.5 w-3.5 shrink-0" />
                    Selected: <span className="font-medium">{selectedUser.name}</span>
                  </div>
                )}
              </div>
            </div>
          )}

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setMatchModal({ open: false, record: null })}
              className="text-sm"
            >
              Cancel
            </Button>
            <Button
              onClick={handleConfirmMatch}
              disabled={!selectedUser || matchingId !== null}
              className="bg-cyan-600 hover:bg-cyan-700 text-white text-sm"
            >
              {matchingId ? (
                <><RefreshCw className="h-3.5 w-3.5 mr-1.5 animate-spin" /> Matching...</>
              ) : (
                <><UserCheck className="h-3.5 w-3.5 mr-1.5" /> Confirm Match</>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
