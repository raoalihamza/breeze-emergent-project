import { AlertCircle, X } from 'lucide-react';
import { Button } from './ui/button.jsx';

export default function ImpersonationBanner({ impersonatedUser, onStopImpersonation }) {
  if (!impersonatedUser) return null;

  return (
    <div className="bg-gradient-to-r from-amber-500 to-orange-500 text-white px-4 py-2.5 flex items-center justify-between shadow-lg">
      <div className="flex items-center gap-3">
        <AlertCircle className="h-5 w-5 animate-pulse" />
        <div>
          <p className="text-sm font-semibold">
            Viewing as: {impersonatedUser.name}
          </p>
          <p className="text-xs opacity-90">
            {impersonatedUser.role} • {impersonatedUser.email}
          </p>
        </div>
      </div>
      <Button
        variant="ghost"
        size="sm"
        onClick={onStopImpersonation}
        className="text-white hover:bg-white/20 h-8"
      >
        <X className="h-4 w-4 mr-1" />
        Exit View
      </Button>
    </div>
  );
}
