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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in-overlay">
      <div className="bg-zinc-950 border border-zinc-800 rounded-2xl shadow-dropdown w-full max-w-md overflow-hidden animate-fade-in">
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-zinc-800 bg-zinc-900/60">
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-zinc-900 border border-zinc-800 text-zinc-300 rounded-lg">
              <ArrowRightLeft className="w-4 h-4" />
            </div>
            <h2 className="text-xs font-bold text-zinc-100 tracking-tight uppercase">Registrar Movimentação</h2>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors cursor-pointer">
            <X className="w-4 h-4" />
          </button>
        </div>

        {error && (
          <div className="mx-5 mt-3.5 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="p-5 space-y-3.5">
          <div>
            <label className="block text-[11px] font-medium text-zinc-400 mb-1">Origem (Atual)</label>
            <input
              type="text"
              disabled
              value={currentLocation}
              className="w-full bg-zinc-900/40 border border-zinc-800/80 rounded-lg px-3 py-1.5 text-xs text-zinc-400 cursor-not-allowed font-mono"
            />
          </div>

          <div>
            <label className="block text-[11px] font-medium text-zinc-300 mb-1">Destino *</label>
            <select
              value={destinationLocation}
              onChange={(e) => setDestinationLocation(e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-1.5 text-xs text-zinc-100 focus:border-zinc-500 outline-none"
            >
              {locations.map((loc) => (
                <option key={loc.id} value={loc.name}>{loc.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-medium text-zinc-300 mb-1">Data da Movimentação *</label>
            <input
              type="date"
              required
              value={movementDate}
              onChange={(e) => setMovementDate(e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-1.5 text-xs text-zinc-100 focus:border-zinc-500 outline-none font-mono"
            />
          </div>

          <div>
            <label className="block text-[11px] font-medium text-zinc-300 mb-1">Observações</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Ex: Equipamento transferido para o estúdio 2."
              rows={2}
              className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-3 py-1.5 text-xs text-zinc-100 focus:border-zinc-500 outline-none resize-none placeholder:text-zinc-500"
            />
          </div>

          <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-zinc-800">
            <button
              type="button"
              onClick={onClose}
              className="px-3.5 py-1.5 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-zinc-300 rounded-xl text-xs font-medium transition-all cursor-pointer"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-1.5 bg-zinc-100 hover:bg-white text-zinc-950 rounded-xl text-xs font-semibold transition-all shadow-sm disabled:opacity-50 cursor-pointer flex items-center gap-1.5 active:scale-[0.99]"
            >
              {loading ? <div className="w-3.5 h-3.5 border-2 border-zinc-400 border-t-zinc-950 rounded-full animate-spin" /> : 'Salvar Movimentação'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
