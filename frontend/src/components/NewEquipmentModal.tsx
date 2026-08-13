import React, { useState, useEffect } from 'react';
import { X, Plus, HardDrive, Check, AlertCircle } from 'lucide-react';
import { equipmentApi } from '../api/equipmentApi';
import { EquipmentCreatePayload, EquipmentTag } from '../types/equipment';

interface NewEquipmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const NewEquipmentModal: React.FC<NewEquipmentModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [types, setTypes] = useState<EquipmentTag[]>([]);
  const [locations, setLocations] = useState<EquipmentTag[]>([]);
  const [statuses, setStatuses] = useState<EquipmentTag[]>([]);

  // Form State
  const [serialNumber, setSerialNumber] = useState('');
  const [patrimonyNumber, setPatrimonyNumber] = useState('');
  const [hostname, setHostname] = useState('');
  const [description, setDescription] = useState('');
  const [brand, setBrand] = useState('');
  const [productNumber, setProductNumber] = useState('');
  const [equipmentType, setEquipmentType] = useState('Desktop');
  const [location, setLocation] = useState('TI');
  const [status, setStatus] = useState('Em uso');
  const [windowsKey, setWindowsKey] = useState('');
  const [notes, setNotes] = useState('');

  // New Tag inline input state
  const [newTagInput, setNewTagInput] = useState<{ category: string; value: string } | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetchTags();
      resetForm();
    }
  }, [isOpen]);

  const fetchTags = async () => {
    try {
      const allTags = await equipmentApi.getTags();
      setTypes(allTags.filter((t) => t.category === 'tipo'));
      setLocations(allTags.filter((t) => t.category === 'localizacao'));
      setStatuses(allTags.filter((t) => t.category === 'situacao'));
    } catch (err) {
      console.error('Erro ao carregar tags:', err);
    }
  };

  const resetForm = () => {
    setSerialNumber('');
    setPatrimonyNumber('');
    setHostname('');
    setDescription('');
    setBrand('');
    setProductNumber('');
    setEquipmentType('Desktop');
    setLocation('TI');
    setStatus('Em uso');
    setWindowsKey('');
    setNotes('');
    setError(null);
    setNewTagInput(null);
  };

  const handleCreateTag = async (category: string) => {
    if (!newTagInput || !newTagInput.value.trim()) return;
    try {
      const created = await equipmentApi.createTag(category, newTagInput.value.trim());
      await fetchTags();
      if (category === 'tipo') setEquipmentType(created.name);
      if (category === 'localizacao') setLocation(created.name);
      if (category === 'situacao') setStatus(created.name);
      setNewTagInput(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao criar nova tag');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!serialNumber.trim() || !description.trim()) {
      setError('Número de série e descrição são obrigatórios.');
      return;
    }

    setLoading(true);
    try {
      const payload: EquipmentCreatePayload = {
        serial_number: serialNumber.trim(),
        patrimony_number: patrimonyNumber.trim() || null,
        hostname: hostname.trim() || null,
        description: description.trim(),
        brand: brand.trim() || null,
        product_number: productNumber.trim() || null,
        equipment_type: equipmentType,
        location: location,
        status: status,
        windows_key: windowsKey.trim() || null,
        notes: notes.trim() || null,
      };

      await equipmentApi.createEquipment(payload);
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao cadastrar equipamento');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-slate-950/80 backdrop-blur-md animate-fade-in-overlay overflow-y-auto">
      {/* Formulário amplo ocupando a maior parte da área útil (RN-EQ-13) */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden animate-fade-in my-auto">
        {/* Header */}
        <div className="flex items-center justify-between px-8 py-5 border-b border-slate-800 bg-slate-950/50">
          <div className="flex items-center gap-3.5">
            <div className="p-2.5 bg-blue-500/10 border border-blue-500/20 text-blue-400 rounded-2xl">
              <HardDrive className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white tracking-wide">Novo Equipamento</h2>
              <p className="text-xs text-slate-400">Preencha as informações para cadastrar um novo ativo de patrimônio</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Alert Error */}
        {error && (
          <div className="mx-8 mt-6 p-4 rounded-2xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-center gap-3">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Form Body - Área Ampla */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-8 space-y-8">
          {/* Seção: Identificação */}
          <div className="space-y-4">
            <h3 className="text-xs font-bold text-blue-400 uppercase tracking-wider">1. Identificação Principal</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div>
                <label className="block text-xs font-semibold text-slate-200 mb-1.5">Nº de Série (SN) *</label>
                <input
                  type="text"
                  required
                  value={serialNumber}
                  onChange={(e) => setSerialNumber(e.target.value)}
                  placeholder="ex: SN12345678"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white input-focus-glow outline-none font-mono"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-200 mb-1.5">Nº de Patrimônio</label>
                <input
                  type="text"
                  value={patrimonyNumber}
                  onChange={(e) => setPatrimonyNumber(e.target.value)}
                  placeholder="ex: PAT-10342"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white input-focus-glow outline-none font-mono"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-200 mb-1.5">Descrição / Modelo *</label>
              <input
                type="text"
                required
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="ex: Dell OptiPlex 7090 Core i7 16GB SSD 512GB"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white input-focus-glow outline-none"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div>
                <label className="block text-xs font-semibold text-slate-200 mb-1.5">Marca</label>
                <input
                  type="text"
                  value={brand}
                  onChange={(e) => setBrand(e.target.value)}
                  placeholder="ex: Dell, Lenovo, HP, Apple"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white input-focus-glow outline-none"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-200 mb-1.5">Nº do Produto</label>
                <input
                  type="text"
                  value={productNumber}
                  onChange={(e) => setProductNumber(e.target.value)}
                  placeholder="ex: 20L50001BR"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white input-focus-glow outline-none font-mono"
                />
              </div>
            </div>
          </div>

          {/* Seção: Categorização e Estado Atual */}
          <div className="space-y-4 pt-4 border-t border-slate-800/80">
            <h3 className="text-xs font-bold text-blue-400 uppercase tracking-wider">2. Categoria, Localização & Situação</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              {/* Tipo */}
              <div>
                <label className="block text-xs font-semibold text-slate-200 mb-1.5">Tipo *</label>
                {newTagInput?.category === 'tipo' ? (
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newTagInput.value}
                      onChange={(e) => setNewTagInput({ category: 'tipo', value: e.target.value })}
                      placeholder="Novo tipo"
                      className="w-full bg-slate-950 border border-blue-500 rounded-xl px-3 py-2 text-xs text-white outline-none"
                    />
                    <button type="button" onClick={() => handleCreateTag('tipo')} className="px-3 bg-blue-600 rounded-xl text-white">
                      <Check className="w-4 h-4" />
                    </button>
                  </div>
                ) : (
                  <div className="space-y-1.5">
                    <select
                      value={equipmentType}
                      onChange={(e) => setEquipmentType(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white input-focus-glow outline-none"
                    >
                      {types.map((t) => (
                        <option key={t.id} value={t.name}>{t.name}</option>
                      ))}
                    </select>
                    <button
                      type="button"
                      onClick={() => setNewTagInput({ category: 'tipo', value: '' })}
                      className="text-[11px] text-blue-400 hover:underline flex items-center gap-1 cursor-pointer"
                    >
                      <Plus className="w-3.5 h-3.5" /> + Criar novo tipo
                    </button>
                  </div>
                )}
              </div>

              {/* Localização */}
              <div>
                <label className="block text-xs font-semibold text-slate-200 mb-1.5">Localização Inicial *</label>
                {newTagInput?.category === 'localizacao' ? (
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newTagInput.value}
                      onChange={(e) => setNewTagInput({ category: 'localizacao', value: e.target.value })}
                      placeholder="Nova localização"
                      className="w-full bg-slate-950 border border-blue-500 rounded-xl px-3 py-2 text-xs text-white outline-none"
                    />
                    <button type="button" onClick={() => handleCreateTag('localizacao')} className="px-3 bg-blue-600 rounded-xl text-white">
                      <Check className="w-4 h-4" />
                    </button>
                  </div>
                ) : (
                  <div className="space-y-1.5">
                    <select
                      value={location}
                      onChange={(e) => setLocation(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white input-focus-glow outline-none"
                    >
                      {locations.map((l) => (
                        <option key={l.id} value={l.name}>{l.name}</option>
                      ))}
                    </select>
                    <button
                      type="button"
                      onClick={() => setNewTagInput({ category: 'localizacao', value: '' })}
                      className="text-[11px] text-blue-400 hover:underline flex items-center gap-1 cursor-pointer"
                    >
                      <Plus className="w-3.5 h-3.5" /> + Criar nova localização
                    </button>
                  </div>
                )}
              </div>

              {/* Situação */}
              <div>
                <label className="block text-xs font-semibold text-slate-200 mb-1.5">Situação *</label>
                {newTagInput?.category === 'situacao' ? (
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newTagInput.value}
                      onChange={(e) => setNewTagInput({ category: 'situacao', value: e.target.value })}
                      placeholder="Nova situação"
                      className="w-full bg-slate-950 border border-blue-500 rounded-xl px-3 py-2 text-xs text-white outline-none"
                    />
                    <button type="button" onClick={() => handleCreateTag('situacao')} className="px-3 bg-blue-600 rounded-xl text-white">
                      <Check className="w-4 h-4" />
                    </button>
                  </div>
                ) : (
                  <div className="space-y-1.5">
                    <select
                      value={status}
                      onChange={(e) => setStatus(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white input-focus-glow outline-none"
                    >
                      {statuses.map((s) => (
                        <option key={s.id} value={s.name}>{s.name}</option>
                      ))}
                    </select>
                    <button
                      type="button"
                      onClick={() => setNewTagInput({ category: 'situacao', value: '' })}
                      className="text-[11px] text-blue-400 hover:underline flex items-center gap-1 cursor-pointer"
                    >
                      <Plus className="w-3.5 h-3.5" /> + Criar nova situação
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Seção: Rede & Licenciamento */}
          <div className="space-y-4 pt-4 border-t border-slate-800/80">
            <h3 className="text-xs font-bold text-blue-400 uppercase tracking-wider">3. Rede & Licenciamento</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div>
                <label className="block text-xs font-semibold text-slate-200 mb-1.5">Hostname</label>
                <input
                  type="text"
                  value={hostname}
                  onChange={(e) => setHostname(e.target.value)}
                  placeholder="ex: DESKTOP-TI01"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white input-focus-glow outline-none font-mono"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-200 mb-1.5">Chave Windows</label>
                <input
                  type="text"
                  value={windowsKey}
                  onChange={(e) => setWindowsKey(e.target.value)}
                  placeholder="ex: VK9X2-N8Y4R-W3M2T-K7P1Q-L9Z0A"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white input-focus-glow outline-none font-mono"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-200 mb-1.5">Observações Gerais</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Observações técnicas gerais, configurações específicas..."
                rows={3}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-white input-focus-glow outline-none resize-none"
              />
            </div>
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-end gap-3 pt-6 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold transition-all cursor-pointer"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold btn-glow-transition shadow-lg shadow-blue-500/20 disabled:opacity-50 cursor-pointer flex items-center gap-2"
            >
              {loading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : 'Cadastrar Equipamento'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
