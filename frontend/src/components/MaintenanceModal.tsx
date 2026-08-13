import React, { useState } from 'react';
import { X, Wrench, AlertCircle } from 'lucide-react';
import { equipmentApi } from '../api/equipmentApi';

interface MaintenanceModalProps {
  isOpen: boolean;
  equipmentId: number;
  onClose: () => void;
  onSuccess: () => void;
}

export const MaintenanceModal: React.FC<MaintenanceModalProps> = ({
  isOpen,
  equipmentId,
  onClose,
  onSuccess,
}) => {
  const [maintenanceDate, setMaintenanceDate] = useState(new Date().toISOString().substring(0, 10));
  const [description, setDescription] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!description.trim()) {
      setError('A descrição / lista de itens da manutenção é obrigatória.');
      return;
    }

    setLoading(true);

    try {
      await equipmentApi.recordMaintenance(equipmentId, {
        maintenance_date: new Date(maintenanceDate).toISOString(),
        maintenance_type: 'Manutenção',
        description: description.trim(),
        notes: notes.trim() || undefined,
      });
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao registrar manutenção');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in-overlay">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-fade-in">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-950/40">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/10 border border-blue-500/20 text-blue-400 rounded-xl">
              <Wrench className="w-5 h-5" />
            </div>
            <h2 className="text-sm font-bold text-white tracking-wide">Registrar Manutenção</h2>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {error && (
          <div className="mx-6 mt-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-xs text-slate-300 mb-1">Data da Manutenção *</label>
            <input
              type="date"
              required
              value={maintenanceDate}
              onChange={(e) => setMaintenanceDate(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white input-focus-glow outline-none"
            />
          </div>

          <div>
            <label className="block text-xs text-slate-300 mb-1">Descrição / Itens Realizados *</label>
            <textarea
              required
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Ex: Troca de SSD, Limpeza interna, Troca de pasta térmica..."
              rows={4}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white input-focus-glow outline-none resize-none"
            />
          </div>

          <div>
            <label className="block text-xs text-slate-300 mb-1">Observações Técnicas</label>
            <input
              type="text"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Ex: Teste de estabilidade concluído."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white input-focus-glow outline-none"
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold transition-all cursor-pointer"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold btn-glow-transition shadow-lg shadow-blue-500/20 disabled:opacity-50 cursor-pointer flex items-center gap-2"
            >
              {loading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : 'Salvar Manutenção'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
