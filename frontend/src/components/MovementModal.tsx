import React, { useState } from 'react';
import { X, ArrowRightLeft, AlertCircle } from 'lucide-react';
import { equipmentApi } from '../api/equipmentApi';
import { EquipmentTag } from '../types/equipment';

interface MovementModalProps {
  isOpen: boolean;
  equipmentId: number;
  currentLocation: string;
  locations: EquipmentTag[];
  onClose: () => void;
  onSuccess: () => void;
}

export const MovementModal: React.FC<MovementModalProps> = ({
  isOpen,
  equipmentId,
  currentLocation,
  locations,
  onClose,
  onSuccess,
}) => {
  const [destinationLocation, setDestinationLocation] = useState(locations[0]?.name || 'TI');
  const [movementDate, setMovementDate] = useState(new Date().toISOString().substring(0, 10));
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await equipmentApi.recordMovement(equipmentId, {
        origin_location: currentLocation,
        destination_location: destinationLocation,
        movement_date: new Date(movementDate).toISOString(),
        notes: notes.trim() || undefined,
      });
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao registrar movimentação');
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
              <ArrowRightLeft className="w-5 h-5" />
            </div>
            <h2 className="text-sm font-bold text-white tracking-wide">Registrar Movimentação</h2>
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
            <label className="block text-xs text-slate-400 mb-1">Origem (Atual)</label>
            <input
              type="text"
              disabled
              value={currentLocation}
              className="w-full bg-slate-950/50 border border-slate-800/80 rounded-xl px-3 py-2 text-xs text-slate-400 cursor-not-allowed"
            />
          </div>

          <div>
            <label className="block text-xs text-slate-300 mb-1">Destino *</label>
            <select
              value={destinationLocation}
              onChange={(e) => setDestinationLocation(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white input-focus-glow outline-none"
            >
              {locations.map((loc) => (
                <option key={loc.id} value={loc.name}>{loc.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs text-slate-300 mb-1">Data da Movimentação *</label>
            <input
              type="date"
              required
              value={movementDate}
              onChange={(e) => setMovementDate(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white input-focus-glow outline-none"
            />
          </div>

          <div>
            <label className="block text-xs text-slate-300 mb-1">Observações</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Ex: Equipamento transferido para utilização no estúdio 2."
              rows={3}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white input-focus-glow outline-none resize-none"
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
              {loading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : 'Salvar Movimentação'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
