import { useState, useEffect } from 'react';
import { useClientAuth } from './ClientPortalLayout';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { toast } from 'sonner';
import { motion } from 'framer-motion';
import { 
  FolderOpen, FileText, Download, File, Image, 
  FileSpreadsheet, Presentation, Clock
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const DOC_TYPE_LABELS = {
  'policy': { label: 'Policy Document', color: 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-400' },
  'statement': { label: 'Statement', color: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' },
  'illustration': { label: 'Illustration', color: 'bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-400' },
  'other': { label: 'Other', color: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300' }
};

const getFileIcon = (fileName) => {
  const ext = fileName?.split('.').pop()?.toLowerCase();
  switch (ext) {
    case 'pdf':
      return <FileText className="h-5 w-5" />;
    case 'png':
    case 'jpg':
    case 'jpeg':
    case 'gif':
      return <Image className="h-5 w-5" />;
    case 'xls':
    case 'xlsx':
    case 'csv':
      return <FileSpreadsheet className="h-5 w-5" />;
    case 'ppt':
    case 'pptx':
      return <Presentation className="h-5 w-5" />;
    default:
      return <File className="h-5 w-5" />;
  }
};

export default function ClientDocuments() {
  const { client, getAuthHeader } = useClientAuth();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`${API}/portal/my-documents`, getAuthHeader());
      setDocuments(response.data);
    } catch (error) {
      console.error('Failed to load documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (doc) => {
    setDownloading(doc.id);
    try {
      const response = await axios.get(`${API}/portal/my-documents/download/${doc.id}`, {
        ...getAuthHeader(),
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', doc.file_name);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success('Document downloaded');
    } catch (error) {
      toast.error('Failed to download document');
    } finally {
      setDownloading(null);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    });
  };

  // Group documents by type
  const groupedDocs = documents.reduce((acc, doc) => {
    const type = doc.document_type || 'other';
    if (!acc[type]) acc[type] = [];
    acc[type].push(doc);
    return acc;
  }, {});

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="h-8 w-8 border-3 border-cyan-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-3">
          <div className="h-8 w-1 bg-gradient-to-b from-cyan-500 to-blue-500 rounded-full" />
          <div>
            <h1 className="text-xl font-bold text-slate-900 dark:text-white">Documents Vault</h1>
            <p className="text-xs text-slate-500 dark:text-slate-400">Your secure document storage</p>
          </div>
        </div>
      </motion.div>

      {documents.length === 0 ? (
        <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm">
          <CardContent className="py-16 text-center">
            <FolderOpen className="h-12 w-12 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">No Documents Yet</h3>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Your advisor will upload documents here when available.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {/* All Documents */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <FolderOpen className="h-5 w-5 text-cyan-600 dark:text-cyan-400" />
                  All Documents
                  <span className="text-sm font-normal text-slate-500 dark:text-slate-400">
                    ({documents.length})
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {documents.map((doc, index) => {
                    const typeConfig = DOC_TYPE_LABELS[doc.document_type] || DOC_TYPE_LABELS['other'];
                    
                    return (
                      <motion.div
                        key={doc.id}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="flex items-center gap-4 p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700/50 hover:border-cyan-500/30 transition-colors group"
                      >
                        {/* File Icon */}
                        <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-800 dark:to-slate-700 flex items-center justify-center text-slate-500 dark:text-slate-400">
                          {getFileIcon(doc.file_name)}
                        </div>

                        {/* File Info */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-medium text-slate-900 dark:text-white truncate">
                              {doc.file_name}
                            </h4>
                            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${typeConfig.color}`}>
                              {typeConfig.label}
                            </span>
                          </div>
                          <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
                            <span className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {formatDate(doc.created_at)}
                            </span>
                            {doc.uploaded_by_name && (
                              <span>Uploaded by {doc.uploaded_by_name}</span>
                            )}
                          </div>
                        </div>

                        {/* Download Button */}
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDownload(doc)}
                          disabled={downloading === doc.id}
                          className="flex-shrink-0 opacity-70 group-hover:opacity-100 transition-opacity"
                          data-testid={`download-doc-${doc.id}`}
                        >
                          {downloading === doc.id ? (
                            <div className="h-4 w-4 border-2 border-slate-300 border-t-slate-600 rounded-full animate-spin" />
                          ) : (
                            <>
                              <Download className="h-4 w-4 mr-1" />
                              Download
                            </>
                          )}
                        </Button>
                      </motion.div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Documents by Type */}
          {Object.keys(groupedDocs).length > 1 && (
            <div className="grid md:grid-cols-2 gap-4">
              {Object.entries(groupedDocs).map(([type, docs], groupIndex) => {
                const typeConfig = DOC_TYPE_LABELS[type] || DOC_TYPE_LABELS['other'];
                
                return (
                  <motion.div
                    key={type}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 + groupIndex * 0.1 }}
                  >
                    <Card className="border-slate-200/80 dark:border-slate-800/50 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm h-full">
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm flex items-center gap-2">
                          <span className={`px-2 py-0.5 rounded-full text-xs ${typeConfig.color}`}>
                            {typeConfig.label}
                          </span>
                          <span className="text-slate-500 dark:text-slate-400">
                            ({docs.length})
                          </span>
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="pt-0">
                        <div className="space-y-1">
                          {docs.slice(0, 3).map((doc) => (
                            <div 
                              key={doc.id}
                              className="flex items-center gap-2 p-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/50 cursor-pointer transition-colors"
                              onClick={() => handleDownload(doc)}
                            >
                              <div className="h-6 w-6 rounded bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-400">
                                {getFileIcon(doc.file_name)}
                              </div>
                              <span className="text-sm text-slate-700 dark:text-slate-300 truncate flex-1">
                                {doc.file_name}
                              </span>
                              <Download className="h-3.5 w-3.5 text-slate-400" />
                            </div>
                          ))}
                          {docs.length > 3 && (
                            <p className="text-xs text-slate-500 dark:text-slate-400 text-center pt-2">
                              +{docs.length - 3} more
                            </p>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Security Notice */}
      <div className="text-center py-4">
        <p className="text-xs text-slate-400 dark:text-slate-500 max-w-lg mx-auto">
          All documents are stored securely and encrypted. Downloads are logged for security purposes.
        </p>
      </div>
    </div>
  );
}
