import React from 'react';
import { AlertCircle, ShieldAlert, X } from 'lucide-react';

interface AlertBannerProps {
  message: string;
  isRateLimit?: boolean;
  onClose?: () => void;
}

export const AlertBanner: React.FC<AlertBannerProps> = ({
  message,
  isRateLimit = false,
  onClose,
}) => {
  if (!message) return null;

  return (
    <div
      role="alert"
      className={`p-4 rounded-xl flex items-start gap-3 text-sm transition-all duration-300 ${
        isRateLimit
          ? 'bg-amber-950/70 border border-amber-500/40 text-amber-200 shadow-lg shadow-amber-900/20'
          : 'bg-red-950/70 border border-red-500/40 text-red-200 shadow-glow-error'
      }`}
    >
      <div className="shrink-0 mt-0.5">
        {isRateLimit ? (
          <ShieldAlert className="w-5 h-5 text-amber-400 animate-pulse" />
        ) : (
          <AlertCircle className="w-5 h-5 text-red-400" />
        )}
      </div>
      <div className="flex-1 font-medium leading-relaxed">{message}</div>
      {onClose && (
        <button
          onClick={onClose}
          type="button"
          aria-label="Fechar alerta"
          className="shrink-0 p-1 hover:bg-white/10 rounded-lg transition-colors text-slate-400 hover:text-white"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
};
