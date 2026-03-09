import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent } from '../components/ui/card';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '../components/ui/dialog';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  Plus, Pencil, Trash2, FileText, Search, BookOpen, FileQuestion, Users, 
  Briefcase, Settings, Upload, File, Image, Table, FileSpreadsheet, X,
  CheckCircle, AlertCircle, Eye, Loader2
} from 'lucide-react';
import { toast } from 'sonner';
import { motion, AnimatePresence } from 'framer-motion';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const CATEGORIES = [
  { value: 'onboarding', label: 'Onboarding', icon: BookOpen },
  { value: 'sales', label: 'Sales & Scripts', icon: FileText },
  { value: 'product', label: 'Product Knowledge', icon: FileQuestion },
  { value: 'underwriting', label: 'Underwriting Guides', icon: File },
  { value: 'recruiting', label: 'Recruiting & Leadership', icon: Users },
  { value: 'operations', label: 'Operations', icon: Briefcase },
  { value: 'general', label: 'General', icon: Settings },
];

const FILE_TYPE_ICONS = {
  pdf: FileText,
  docx: FileText,
  xlsx: FileSpreadsheet,
  png: Image,
  jpg: Image,
  jpeg: Image,
  webp: Image,
};

const getCategoryIcon = (category) => {
  const cat = CATEGORIES.find(c => c.value === category);
  return cat ? cat.icon : FileText;
};

const getCategoryLabel = (category) => {
  const cat = CATEGORIES.find(c => c.value === category);
  return cat ? cat.label : category;
};

const getFileIcon = (fileType) => {
  return FILE_TYPE_ICONS[fileType] || FileText;
};

export default function KnowledgeBaseManager() {
  const { getAuthHeader, user } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingDoc, setEditingDoc] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  const [viewDoc, setViewDoc] = useState(null);
  const [activeTab, setActiveTab] = useState('text');
  
  // Form state
  const [formTitle, setFormTitle] = useState('');
  const [formCategory, setFormCategory] = useState('general');
  const [formContent, setFormContent] = useState('');
  const [formTags, setFormTags] = useState('');
  const [formCarrier, setFormCarrier] = useState('');
  const [submitting, setSubmitting] = useState(false);
  
  // File upload state
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`${API}/atlas-ai/knowledge-base`, getAuthHeader());
      setDocuments(response.data);
    } catch (error) {
      console.error('Failed to fetch knowledge base:', error);
      toast.error('Failed to load knowledge base');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setFormTitle('');
    setFormCategory('general');
    setFormContent('');
    setFormTags('');
    setFormCarrier('');
    setEditingDoc(null);
    setSelectedFile(null);
    setActiveTab('text');
  };

  const openAddDialog = () => {
    resetForm();
    setIsDialogOpen(true);
  };

  const openEditDialog = (doc) => {
    setFormTitle(doc.title);
    setFormCategory(doc.category);
    setFormContent(doc.content);
    setFormTags(doc.tags?.join(', ') || '');
    setFormCarrier(doc.carrier || '');
    setEditingDoc(doc);
    setActiveTab('text');
    setIsDialogOpen(true);
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      const allowedTypes = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.ms-excel',
        'image/png',
        'image/jpeg',
        'image/jpg',
        'image/webp'
      ];
      
      if (!allowedTypes.includes(file.type)) {
        toast.error('Invalid file type. Allowed: PDF, DOCX, XLSX, PNG, JPG, WEBP');
        return;
      }
      
      // Validate file size (50MB)
      if (file.size > 50 * 1024 * 1024) {
        toast.error('File too large. Maximum size is 50MB.');
        return;
      }
      
      setSelectedFile(file);
      // Auto-fill title from filename
      if (!formTitle) {
        setFormTitle(file.name.replace(/\.[^/.]+$/, ''));
      }
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile || !formTitle.trim()) {
      toast.error('Please provide a title and select a file');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('title', formTitle.trim());
    formData.append('category', formCategory);
    formData.append('tags', formTags);
    formData.append('carrier', formCarrier);

    try {
      const response = await axios.post(
        `${API}/atlas-ai/knowledge-base/upload`,
        formData,
        {
          ...getAuthHeader(),
          headers: {
            ...getAuthHeader().headers,
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(progress);
          },
        }
      );

      toast.success(response.data.message || 'Document uploaded successfully');
      setIsDialogOpen(false);
      resetForm();
      fetchDocuments();
    } catch (error) {
      console.error('Upload failed:', error);
      toast.error(error.response?.data?.detail || 'Failed to upload document');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleTextSubmit = async () => {
    if (!formTitle.trim() || !formContent.trim()) {
      toast.error('Title and content are required');
      return;
    }

    setSubmitting(true);

    const payload = {
      title: formTitle.trim(),
      category: formCategory,
      content: formContent.trim(),
      tags: formTags.split(',').map(t => t.trim()).filter(t => t)
    };

    try {
      if (editingDoc) {
        await axios.put(
          `${API}/atlas-ai/knowledge-base/${editingDoc.id}`,
          payload,
          getAuthHeader()
        );
        toast.success('Document updated successfully');
      } else {
        await axios.post(
          `${API}/atlas-ai/knowledge-base`,
          payload,
          getAuthHeader()
        );
        toast.success('Document added successfully');
      }
      
      setIsDialogOpen(false);
      resetForm();
      fetchDocuments();
    } catch (error) {
      console.error('Failed to save document:', error);
      toast.error(editingDoc ? 'Failed to update document' : 'Failed to add document');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (docId) => {
    try {
      await axios.delete(`${API}/atlas-ai/knowledge-base/${docId}`, getAuthHeader());
      toast.success('Document deleted');
      setDeleteConfirm(null);
      fetchDocuments();
    } catch (error) {
      console.error('Failed to delete document:', error);
      toast.error('Failed to delete document');
    }
  };

  // Filter documents
  const filteredDocs = documents.filter(doc => {
    const matchesSearch = searchQuery === '' || 
      doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.content?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.carrier?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.tags?.some(t => t.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesCategory = filterCategory === 'all' || doc.category === filterCategory;
    
    return matchesSearch && matchesCategory;
  });

  if (user?.role !== 'admin') {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-slate-500">Only admins can manage the knowledge base.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-slate-900 dark:text-white">Knowledge Base</h2>
          <p className="text-sm text-slate-500">Upload carrier guides, underwriting manuals, and product documents for Atlas AI</p>
        </div>
        <Button onClick={openAddDialog} className="bg-gradient-to-r from-cyan-500 to-blue-600">
          <Plus className="h-4 w-4 mr-2" />
          Add Document
        </Button>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <Input
            placeholder="Search documents, carriers..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={filterCategory} onValueChange={setFilterCategory}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Filter by category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            {CATEGORIES.map(cat => (
              <SelectItem key={cat.value} value={cat.value}>{cat.label}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-cyan-50 to-blue-50 dark:from-cyan-950/30 dark:to-blue-950/30 border-0">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-cyan-600">{documents.length}</div>
            <div className="text-xs text-slate-500">Total Documents</div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-violet-50 to-purple-50 dark:from-violet-950/30 dark:to-purple-950/30 border-0">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-violet-600">
              {documents.filter(d => d.is_file_upload).length}
            </div>
            <div className="text-xs text-slate-500">File Uploads</div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-950/30 dark:to-orange-950/30 border-0">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-amber-600">
              {documents.filter(d => d.category === 'underwriting' || d.category === 'product').length}
            </div>
            <div className="text-xs text-slate-500">Carrier Guides</div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-emerald-50 to-green-50 dark:from-emerald-950/30 dark:to-green-950/30 border-0">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-emerald-600">
              {documents.filter(d => d.has_images).length}
            </div>
            <div className="text-xs text-slate-500">With Images/Charts</div>
          </CardContent>
        </Card>
      </div>

      {/* Documents Grid */}
      {loading ? (
        <div className="flex items-center justify-center h-48">
          <div className="animate-spin h-8 w-8 border-4 border-cyan-500 border-t-transparent rounded-full"></div>
        </div>
      ) : filteredDocs.length === 0 ? (
        <Card className="border-dashed border-2">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Upload className="h-12 w-12 text-slate-300 mb-4" />
            <h3 className="text-lg font-medium text-slate-700 dark:text-slate-300 mb-1">No documents found</h3>
            <p className="text-sm text-slate-500 mb-4 text-center max-w-md">
              {documents.length === 0 
                ? 'Upload carrier guides, underwriting manuals, and product documents to help Atlas AI answer questions accurately.'
                : 'Try adjusting your search or filters.'}
            </p>
            {documents.length === 0 && (
              <Button onClick={openAddDialog} variant="outline">
                <Upload className="h-4 w-4 mr-2" />
                Upload Document
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredDocs.map((doc) => {
            const CategoryIcon = getCategoryIcon(doc.category);
            const FileIcon = doc.is_file_upload ? getFileIcon(doc.file_type) : FileText;
            return (
              <motion.div
                key={doc.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <Card className="h-full hover:shadow-md transition-shadow group">
                  <CardContent className="p-4">
                    <div className="flex items-start gap-3 mb-3">
                      <div className={`p-2 rounded-lg ${doc.is_file_upload ? 'bg-violet-50 dark:bg-violet-950/30' : 'bg-cyan-50 dark:bg-cyan-950/30'}`}>
                        <FileIcon className={`h-4 w-4 ${doc.is_file_upload ? 'text-violet-600' : 'text-cyan-600'}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-slate-900 dark:text-white truncate">{doc.title}</h3>
                        <div className="flex items-center gap-2 mt-1 flex-wrap">
                          <Badge variant="secondary" className="text-xs">
                            {getCategoryLabel(doc.category)}
                          </Badge>
                          {doc.carrier && (
                            <Badge variant="outline" className="text-xs">
                              {doc.carrier}
                            </Badge>
                          )}
                          {doc.is_file_upload && (
                            <Badge variant="outline" className="text-xs text-violet-600 border-violet-300">
                              {doc.file_type?.toUpperCase()}
                            </Badge>
                          )}
                          {doc.has_images && (
                            <Badge variant="outline" className="text-xs text-amber-600 border-amber-300">
                              <Image className="h-3 w-3 mr-1" />
                              Images
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <p className="text-sm text-slate-600 dark:text-slate-400 line-clamp-2 mb-3">
                      {doc.content?.substring(0, 150)}...
                    </p>
                    
                    {doc.tags?.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-3">
                        {doc.tags.slice(0, 3).map((tag, idx) => (
                          <span key={idx} className="text-xs px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                            {tag}
                          </span>
                        ))}
                        {doc.tags.length > 3 && (
                          <span className="text-xs text-slate-400">+{doc.tags.length - 3}</span>
                        )}
                      </div>
                    )}
                    
                    <div className="flex gap-2 pt-2 border-t border-slate-100 dark:border-slate-800">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setViewDoc(doc)}
                        className="flex-1"
                      >
                        <Eye className="h-3.5 w-3.5 mr-1.5" />
                        View
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => openEditDialog(doc)}
                        className="flex-1"
                      >
                        <Pencil className="h-3.5 w-3.5 mr-1.5" />
                        Edit
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setDeleteConfirm(doc)}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950/30"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Add/Edit Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{editingDoc ? 'Edit Document' : 'Add Document to Knowledge Base'}</DialogTitle>
            <DialogDescription>
              {editingDoc 
                ? 'Update the document content.'
                : 'Upload a file or add text content. Atlas AI will use this to answer questions.'}
            </DialogDescription>
          </DialogHeader>
          
          {!editingDoc && (
            <Tabs value={activeTab} onValueChange={setActiveTab} className="mt-4">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="upload" className="flex items-center gap-2">
                  <Upload className="h-4 w-4" />
                  Upload File
                </TabsTrigger>
                <TabsTrigger value="text" className="flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  Text Entry
                </TabsTrigger>
              </TabsList>
              
              <TabsContent value="upload" className="space-y-4 mt-4">
                {/* File Upload Area */}
                <div
                  className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
                    selectedFile 
                      ? 'border-cyan-400 bg-cyan-50 dark:bg-cyan-950/20' 
                      : 'border-slate-300 dark:border-slate-700 hover:border-cyan-400'
                  }`}
                  onClick={() => fileInputRef.current?.click()}
                  style={{ cursor: 'pointer' }}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.docx,.xlsx,.xls,.png,.jpg,.jpeg,.webp"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                  
                  {selectedFile ? (
                    <div className="flex flex-col items-center">
                      <CheckCircle className="h-12 w-12 text-cyan-500 mb-3" />
                      <p className="font-medium text-slate-900 dark:text-white">{selectedFile.name}</p>
                      <p className="text-sm text-slate-500 mt-1">
                        {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="mt-2 text-red-600"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedFile(null);
                        }}
                      >
                        <X className="h-4 w-4 mr-1" />
                        Remove
                      </Button>
                    </div>
                  ) : (
                    <>
                      <Upload className="h-12 w-12 text-slate-400 mx-auto mb-3" />
                      <p className="font-medium text-slate-700 dark:text-slate-300">
                        Click to upload or drag and drop
                      </p>
                      <p className="text-sm text-slate-500 mt-1">
                        PDF, DOCX, XLSX, PNG, JPG, WEBP (max 50MB)
                      </p>
                    </>
                  )}
                </div>
                
                {isUploading && (
                  <div className="space-y-2">
                    <Progress value={uploadProgress} className="h-2" />
                    <p className="text-sm text-center text-slate-500">
                      {uploadProgress < 100 ? `Uploading... ${uploadProgress}%` : 'Processing document...'}
                    </p>
                  </div>
                )}
              </TabsContent>
              
              <TabsContent value="text" className="space-y-4 mt-4">
                <div className="space-y-2">
                  <Label htmlFor="content">Content *</Label>
                  <Textarea
                    id="content"
                    value={formContent}
                    onChange={(e) => setFormContent(e.target.value)}
                    placeholder="Paste or type the document content here. Include all relevant information about products, underwriting rules, rates, etc."
                    rows={12}
                    className="resize-none font-mono text-sm"
                  />
                </div>
              </TabsContent>
            </Tabs>
          )}
          
          {/* Common Fields */}
          <div className="space-y-4 mt-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="title">Title *</Label>
                <Input
                  id="title"
                  value={formTitle}
                  onChange={(e) => setFormTitle(e.target.value)}
                  placeholder="e.g., Americo Final Expense Underwriting Guide"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="category">Category *</Label>
                <Select value={formCategory} onValueChange={setFormCategory}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {CATEGORIES.map(cat => (
                      <SelectItem key={cat.value} value={cat.value}>{cat.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="carrier">Carrier (optional)</Label>
                <Input
                  id="carrier"
                  value={formCarrier}
                  onChange={(e) => setFormCarrier(e.target.value)}
                  placeholder="e.g., Americo, National Life Group"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="tags">Tags (comma-separated)</Label>
                <Input
                  id="tags"
                  value={formTags}
                  onChange={(e) => setFormTags(e.target.value)}
                  placeholder="e.g., final expense, underwriting, rates"
                />
              </div>
            </div>
          </div>
          
          {/* Edit mode - show content textarea */}
          {editingDoc && (
            <div className="space-y-2 mt-4">
              <Label htmlFor="edit-content">Content</Label>
              <Textarea
                id="edit-content"
                value={formContent}
                onChange={(e) => setFormContent(e.target.value)}
                rows={10}
                className="resize-none font-mono text-sm"
              />
            </div>
          )}
          
          <DialogFooter className="mt-6">
            <Button variant="outline" onClick={() => setIsDialogOpen(false)}>Cancel</Button>
            {activeTab === 'upload' && !editingDoc ? (
              <Button 
                onClick={handleFileUpload} 
                disabled={isUploading || !selectedFile || !formTitle.trim()} 
                className="bg-gradient-to-r from-cyan-500 to-blue-600"
              >
                {isUploading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4 mr-2" />
                    Upload & Process
                  </>
                )}
              </Button>
            ) : (
              <Button 
                onClick={handleTextSubmit} 
                disabled={submitting} 
                className="bg-gradient-to-r from-cyan-500 to-blue-600"
              >
                {submitting ? 'Saving...' : editingDoc ? 'Save Changes' : 'Add Document'}
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* View Document Dialog */}
      <Dialog open={!!viewDoc} onOpenChange={() => setViewDoc(null)}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {viewDoc?.title}
              {viewDoc?.carrier && (
                <Badge variant="outline">{viewDoc.carrier}</Badge>
              )}
            </DialogTitle>
            <DialogDescription>
              {getCategoryLabel(viewDoc?.category)} 
              {viewDoc?.is_file_upload && ` • ${viewDoc.file_type?.toUpperCase()} File`}
              {viewDoc?.has_images && ' • Contains Images/Charts'}
            </DialogDescription>
          </DialogHeader>
          
          <div className="mt-4 space-y-4">
            {viewDoc?.image_analyses?.length > 0 && (
              <div className="p-4 bg-amber-50 dark:bg-amber-950/30 rounded-lg border border-amber-200 dark:border-amber-800">
                <h4 className="font-semibold text-amber-800 dark:text-amber-200 mb-2 flex items-center gap-2">
                  <Image className="h-4 w-4" />
                  Image/Chart Analysis
                </h4>
                {viewDoc.image_analyses.map((analysis, idx) => (
                  <p key={idx} className="text-sm text-amber-700 dark:text-amber-300 whitespace-pre-wrap">
                    {analysis}
                  </p>
                ))}
              </div>
            )}
            
            <div className="p-4 bg-slate-50 dark:bg-slate-900 rounded-lg border max-h-[500px] overflow-y-auto">
              <pre className="text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap font-mono">
                {viewDoc?.content}
              </pre>
            </div>
            
            {viewDoc?.tags?.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {viewDoc.tags.map((tag, idx) => (
                  <Badge key={idx} variant="secondary">{tag}</Badge>
                ))}
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deleteConfirm} onOpenChange={() => setDeleteConfirm(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Document</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{deleteConfirm?.title}"? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteConfirm(null)}>Cancel</Button>
            <Button
              variant="destructive"
              onClick={() => handleDelete(deleteConfirm?.id)}
            >
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
