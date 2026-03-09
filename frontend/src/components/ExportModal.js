import { useState } from 'react';
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
import { RadioGroup, RadioGroupItem } from './ui/radio-group.jsx';
import { Download, FileJson, FileSpreadsheet, FileText } from 'lucide-react';

export function ExportModal({ open, onClose, onConfirm, loading }) {
  const [format, setFormat] = useState('json');

  const handleExport = () => {
    onConfirm(format);
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Download className="h-5 w-5 text-cyan-500" />
            Export Hierarchy
          </DialogTitle>
          <DialogDescription>
            Choose the format for your hierarchy export
          </DialogDescription>
        </DialogHeader>

        <div className="py-6">
          <RadioGroup value={format} onValueChange={setFormat}>
            <div className="space-y-3">
              {/* JSON Option */}
              <div className="flex items-center space-x-3 p-3 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/50 cursor-pointer transition-colors">
                <RadioGroupItem value="json" id="json" />
                <Label
                  htmlFor="json"
                  className="flex items-center gap-3 cursor-pointer flex-1"
                >
                  <div className="p-2 rounded-lg bg-blue-50 dark:bg-blue-900/30">
                    <FileJson className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div>
                    <div className="font-medium text-slate-900 dark:text-white">JSON</div>
                    <div className="text-xs text-slate-500 dark:text-slate-400">
                      Raw data format, ideal for backups
                    </div>
                  </div>
                </Label>
              </div>

              {/* CSV Option */}
              <div className="flex items-center space-x-3 p-3 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/50 cursor-pointer transition-colors">
                <RadioGroupItem value="csv" id="csv" />
                <Label
                  htmlFor="csv"
                  className="flex items-center gap-3 cursor-pointer flex-1"
                >
                  <div className="p-2 rounded-lg bg-emerald-50 dark:bg-emerald-900/30">
                    <FileText className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
                  </div>
                  <div>
                    <div className="font-medium text-slate-900 dark:text-white">CSV</div>
                    <div className="text-xs text-slate-500 dark:text-slate-400">
                      Comma-separated, opens in Excel
                    </div>
                  </div>
                </Label>
              </div>

              {/* XLSX Option */}
              <div className="flex items-center space-x-3 p-3 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/50 cursor-pointer transition-colors">
                <RadioGroupItem value="xlsx" id="xlsx" />
                <Label
                  htmlFor="xlsx"
                  className="flex items-center gap-3 cursor-pointer flex-1"
                >
                  <div className="p-2 rounded-lg bg-violet-50 dark:bg-violet-900/30">
                    <FileSpreadsheet className="h-5 w-5 text-violet-600 dark:text-violet-400" />
                  </div>
                  <div>
                    <div className="font-medium text-slate-900 dark:text-white">XLSX</div>
                    <div className="text-xs text-slate-500 dark:text-slate-400">
                      Excel format with formatting
                    </div>
                  </div>
                </Label>
              </div>

              {/* PDF Option */}
              <div className="flex items-center space-x-3 p-3 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/50 cursor-pointer transition-colors">
                <RadioGroupItem value="pdf" id="pdf" />
                <Label
                  htmlFor="pdf"
                  className="flex items-center gap-3 cursor-pointer flex-1"
                >
                  <div className="p-2 rounded-lg bg-red-50 dark:bg-red-900/30">
                    <FileText className="h-5 w-5 text-red-600 dark:text-red-400" />
                  </div>
                  <div>
                    <div className="font-medium text-slate-900 dark:text-white">PDF</div>
                    <div className="text-xs text-slate-500 dark:text-slate-400">
                      Printable document format
                    </div>
                  </div>
                </Label>
              </div>
            </div>
          </RadioGroup>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button onClick={handleExport} disabled={loading} data-testid="confirm-export">
            {loading ? 'Exporting...' : 'Export'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
