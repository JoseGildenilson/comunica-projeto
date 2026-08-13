import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  HardDrive,
  Eye,
  EyeOff,
  ArrowRightLeft,
  Wrench,
  MapPin,
  Tag as TagIcon,
  Calendar,
  Key,
  Clock,
  Edit,
  Trash2,
  Save,
  X,
  AlertCircle,
  Plus,
} from 'lucide-react';
import { equipmentApi } from '../api/equipmentApi';
import { Equipment, EquipmentMaintenance, EquipmentTag } from '../types/equipment';
import { MovementModal } from '../components/MovementModal';
import { MaintenanceModal } from '../components/MaintenanceModal';
import { EditMaintenanceModal } from '../components/EditMaintenanceModal';

export const EquipmentDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [equipment, setEquipment] = useState<Equipment | null>(null);
  const [types, setTypes] = useState<EquipmentTag[]>([]);
  const [locations, setLocations] = useState<EquipmentTag[]>([]);
  const [statuses, setStatuses] = useState<EquipmentTag[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Toggle mask for Windows Key
  const [showWindowsKey, setShowWindowsKey] = useState(false);

  // Batch Editing Mode State (RN-EQ-08 / RN-7.3)
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({
    serial_number: '',
    patrimony_number: '',
    hostname: '',
    description: '',
    brand: '',
    product_number: '',
    equipment_type: '',
    location: '',
    status: '',
    windows_key: '',
    last_maintenance_at: '',
    notes: '',
  });

  // Modals state
  const [isMovementModalOpen, setIsMovementModalOpen] = useState(false);
  const [isMaintenanceModalOpen, setIsMaintenanceModalOpen] = useState(false);
  const [editingMaintenance, setEditingMaintenance] = useState<EquipmentMaintenance | null>(null);

  useEffect(() => {
    if (id) {
      fetchEquipmentDetail(parseInt(id, 10));
      fetchTags();
    }
  }, [id]);

  const fetchTags = async () => {
    try {
      const tags = await equipmentApi.getTags();
      setTypes(tags.filter((t) => t.category === 'tipo'));
      setLocations(tags.filter((t) => t.category === 'localizacao'));
      setStatuses(tags.filter((t) => t.category === 'situacao'));
    } catch (err) {
      console.error('Erro ao buscar tags:', err);
    }
  };

  const fetchEquipmentDetail = async (eqId: number) => {
    setLoading(true);
    setError(null);
    try {
      const data = await equipmentApi.getEquipmentDetail(eqId);
      setEquipment(data);
      initEditForm(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao carregar detalhes do equipamento');
    } finally {
      setLoading(false);
    }
  };

  const initEditForm = (data: Equipment) => {
    setEditForm({
      serial_number: data.serial_number || '',
      patrimony_number: data.patrimony_number || '',
      hostname: data.hostname || '',
      description: data.description || '',
      brand: data.brand || '',
      product_number: data.product_number || '',
      equipment_type: data.equipment_type || '',
      location: data.location || '',
      status: data.status || '',
      windows_key: data.windows_key || '',
      last_maintenance_at: data.last_maintenance_at
        ? new Date(data.last_maintenance_at).toISOString().substring(0, 10)
        : '',
      notes: data.notes || '',
    });
  };

  const handleStartEdit = () => {
    if (equipment) {
      initEditForm(equipment);
      setIsEditing(true);
      setError(null);
    }
  };

  const handleCancelEdit = () => {
    if (equipment) {
      initEditForm(equipment);
    }
    setIsEditing(false);
    setError(null);
  };

  const handleSaveEdit = async () => {
    if (!equipment) return;
    setError(null);
    setSaving(true);

    try {
      const updated = await equipmentApi.updateEquipment(equipment.id, {
        serial_number: editForm.serial_number.trim(),
        patrimony_number: editForm.patrimony_number.trim() || null,
        hostname: editForm.hostname.trim() || null,
        description: editForm.description.trim(),
        brand: editForm.brand.trim() || null,
        product_number: editForm.product_number.trim() || null,
        equipment_type: editForm.equipment_type,
        location: editForm.location,
        status: editForm.status,
        windows_key: editForm.windows_key.trim() || null,
        last_maintenance_at: editForm.last_maintenance_at
          ? new Date(editForm.last_maintenance_at).toISOString()
          : null,
        notes: editForm.notes.trim() || null,
      });

      setEquipment(updated);
      setIsEditing(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao salvar alterações do equipamento');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteMaintenance = async (maintId: number) => {
    if (!equipment) return;
    if (!window.confirm('Deseja realmente excluir este registro de manutenção?')) return;

    try {
      await equipmentApi.deleteMaintenance(equipment.id, maintId);
      fetchEquipmentDetail(equipment.id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao excluir manutenção');
    }
  };

  const formatDate = (dateStr?: string | null) => {
    if (!dateStr) return 'Não registrada';
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center text-slate-400">
        <div className="w-8 h-8 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mb-2" />
        <p className="text-xs">Carregando detalhes do equipamento...</p>
      </div>
    );
  }

  if (error && !equipment) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-6 text-center">
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-2xl max-w-md space-y-3">
          <p className="text-sm font-semibold text-red-400">{error || 'Equipamento não encontrado'}</p>
          <button
            onClick={() => navigate('/equipamentos')}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs font-semibold"
          >
            Voltar para Equipamentos
          </button>
        </div>
      </div>
    );
  }

  if (!equipment) return null;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Top Header com Botão Voltar para Equipamentos (RN-EQ-06 / RN-20) */}
      <header className="sticky top-0 z-40 bg-slate-950/80 backdrop-blur-md border-b border-slate-800/80 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/equipamentos')}
              data-testid="back-to-equipments-btn"
              className="p-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-xl text-slate-400 hover:text-white transition-colors cursor-pointer flex items-center gap-2 text-xs font-semibold"
              title="Voltar para a listagem de Equipamentos"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Voltar para equipamentos</span>
            </button>

            <div>
              <h1 className="text-lg font-bold text-white tracking-wide">{equipment.description}</h1>
              <p className="text-xs text-slate-400">Visão Geral & Histórico Técnico</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {!isEditing ? (
              <>
                <button
                  onClick={handleStartEdit}
                  data-testid="edit-equipment-btn"
                  className="px-4 py-2 bg-slate-900 hover:bg-slate-800 border border-blue-500/40 text-blue-400 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all cursor-pointer shadow-sm"
                >
                  <Edit className="w-4 h-4" />
                  <span>Editar equipamento</span>
                </button>

                <button
                  onClick={() => setIsMovementModalOpen(true)}
                  className="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-700/60 text-slate-200 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all cursor-pointer"
                >
                  <ArrowRightLeft className="w-4 h-4 text-blue-400" />
                  <span className="hidden sm:inline">Movimentar</span>
                </button>

                <button
                  onClick={() => setIsMaintenanceModalOpen(true)}
                  className="px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold btn-glow-transition shadow-lg shadow-blue-500/20 flex items-center gap-2 cursor-pointer"
                >
                  <Wrench className="w-4 h-4" />
                  <span>Manutenção</span>
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={handleCancelEdit}
                  disabled={saving}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5"
                >
                  <X className="w-4 h-4" />
                  <span>Cancelar</span>
                </button>

                <button
                  onClick={handleSaveEdit}
                  disabled={saving}
                  className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-semibold btn-glow-transition shadow-lg shadow-emerald-500/20 flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                >
                  {saving ? (
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : (
                    <>
                      <Save className="w-4 h-4" />
                      <span>Salvar alterações</span>
                    </>
                  )}
                </button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Main Content Area - Tela Única sem Abas de Informação (RN-EQ-07 / RN-7.1) */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-6 py-6 space-y-6">
        {error && (
          <div className="p-4 rounded-2xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-center gap-3">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Grid de Seções 1, 2 e 3 em Modo Leitura ou Edição Simultânea (RN-EQ-08) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Seção 1: Identificação */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 space-y-4">
            <div className="flex items-center gap-2 border-b border-slate-800/80 pb-3">
              <HardDrive className="w-4 h-4 text-blue-400" />
              <h2 className="text-xs font-bold text-slate-200 uppercase tracking-wider">Identificação</h2>
            </div>

            <div className="space-y-3.5">
              <div>
                <span className="text-slate-400 block text-[11px] font-semibold mb-1">Nº PATRIMÔNIO</span>
                {isEditing ? (
                  <input
                    type="text"
                    value={editForm.patrimony_number}
                    onChange={(e) => setEditForm({ ...editForm, patrimony_number: e.target.value })}
                    className="w-full bg-slate-950 border border-blue-500/60 rounded-xl px-3 py-1.5 text-xs text-white outline-none font-mono"
                  />
                ) : (
                  <span className="text-sm font-extrabold text-white">{equipment.patrimony_number || 'N/A'}</span>
                )}
              </div>

              <div>
                <span className="text-slate-400 block text-[11px] font-semibold mb-1">Nº SÉRIE (SN)</span>
                {isEditing ? (
                  <input
                    type="text"
                    required
                    value={editForm.serial_number}
                    onChange={(e) => setEditForm({ ...editForm, serial_number: e.target.value })}
                    className="w-full bg-slate-950 border border-blue-500/60 rounded-xl px-3 py-1.5 text-xs text-white outline-none font-mono"
                  />
                ) : (
                  <span className="text-xs font-mono text-slate-200">{equipment.serial_number}</span>
                )}
              </div>

              <div>
                <span className="text-slate-400 block text-[11px] font-semibold mb-1">DESCRIÇÃO</span>
                {isEditing ? (
                  <input
                    type="text"
                    required
                    value={editForm.description}
                    onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                    className="w-full bg-slate-950 border border-blue-500/60 rounded-xl px-3 py-1.5 text-xs text-white outline-none"
                  />
                ) : (
                  <span className="text-xs font-semibold text-slate-200">{equipment.description}</span>
                )}
              </div>

              <div>
                <span className="text-slate-400 block text-[11px] font-semibold mb-1">TIPO</span>
                {isEditing ? (
                  <select
                    value={editForm.equipment_type}
                    onChange={(e) => setEditForm({ ...editForm, equipment_type: e.target.value })}
                    className="w-full bg-slate-950 border border-blue-500/60 rounded-xl px-3 py-1.5 text-xs text-white outline-none"
                  >
                    {types.map((t) => (
                      <option key={t.id} value={t.name}>{t.name}</option>
                    ))}
                  </select>
                ) : (
                  <span className="text-xs font-semibold text-blue-400">{equipment.equipment_type}</span>
                )}
              </div>

              <div>
                <span className="text-slate-400 block text-[11px] font-semibold mb-1">MARCA & PRODUTO</span>
                {isEditing ? (
                  <div className="grid grid-cols-2 gap-2">
                    <input
                      type="text"
                      placeholder="Marca"
                      value={editForm.brand}
                      onChange={(e) => setEditForm({ ...editForm, brand: e.target.value })}
                      className="w-full bg-slate-950 border border-blue-500/60 rounded-xl px-2 py-1 text-xs text-white outline-none"
                    />
                    <input
                      type="text"
                      placeholder="Produto"
                      value={editForm.product_number}
                      onChange={(e) => setEditForm({ ...editForm, product_number: e.target.value })}
                      className="w-full bg-slate-950 border border-blue-500/60 rounded-xl px-2 py-1 text-xs text-white outline-none"
                    />
                  </div>
                ) : (
                  <span className="text-xs text-slate-300">
                    {equipment.brand || 'N/A'} {equipment.product_number ? `(${equipment.product_number})` : ''}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Seção 2: Localização e Situação */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 space-y-4">
            <div className="flex items-center gap-2 border-b border-slate-800/80 pb-3">
              <MapPin className="w-4 h-4 text-blue-400" />
              <h2 className="text-xs font-bold text-slate-200 uppercase tracking-wider">Localização & Situação</h2>
            </div>

            <div className="space-y-4 text-xs">
              <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-xl space-y-1">
                <span className="text-slate-400 text-[11px] font-semibold flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5 text-blue-400" />
                  LOCALIZAÇÃO ATUAL
                </span>
                {isEditing ? (
                  <select
                    value={editForm.location}
                    onChange={(e) => setEditForm({ ...editForm, location: e.target.value })}
                    className="w-full bg-slate-900 border border-blue-500/60 rounded-xl px-3 py-1.5 text-xs text-white outline-none mt-1"
                  >
                    {locations.map((l) => (
                      <option key={l.id} value={l.name}>{l.name}</option>
                    ))}
                  </select>
                ) : (
                  <p className="text-sm font-bold text-white">{equipment.location}</p>
                )}
              </div>

              <div className="p-3 bg-slate-950/60 border border-slate-800 rounded-xl space-y-1">
                <span className="text-slate-400 text-[11px] font-semibold flex items-center gap-1">
                  <TagIcon className="w-3.5 h-3.5 text-indigo-400" />
                  SITUAÇÃO DO PATRIMÔNIO
                </span>
                {isEditing ? (
                  <select
                    value={editForm.status}
                    onChange={(e) => setEditForm({ ...editForm, status: e.target.value })}
                    className="w-full bg-slate-900 border border-blue-500/60 rounded-xl px-3 py-1.5 text-xs text-white outline-none mt-1"
                  >
                    {statuses.map((s) => (
                      <option key={s.id} value={s.name}>{s.name}</option>
                    ))}
                  </select>
                ) : (
                  <p className="text-sm font-bold text-blue-300">{equipment.status}</p>
                )}
              </div>

              <div>
                <span className="text-slate-400 block text-[11px] font-semibold mb-1">HOSTNAME</span>
                {isEditing ? (
                  <input
                    type="text"
                    value={editForm.hostname}
                    onChange={(e) => setEditForm({ ...editForm, hostname: e.target.value })}
                    className="w-full bg-slate-950 border border-blue-500/60 rounded-xl px-3 py-1.5 text-xs text-white outline-none font-mono"
                  />
                ) : (
                  <span className="font-mono text-slate-300">{equipment.hostname || 'Não informado'}</span>
                )}
              </div>
            </div>
          </div>

          {/* Seção 3: Informações Técnicas & Licenciamento */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 space-y-4">
            <div className="flex items-center gap-2 border-b border-slate-800/80 pb-3">
              <Key className="w-4 h-4 text-blue-400" />
              <h2 className="text-xs font-bold text-slate-200 uppercase tracking-wider">Técnica & Licença</h2>
            </div>

            <div className="space-y-3.5 text-xs">
              <div>
                <span className="text-slate-400 block text-[11px] font-semibold mb-1">ÚLTIMA MANUTENÇÃO</span>
                {isEditing ? (
                  <input
                    type="date"
                    value={editForm.last_maintenance_at}
                    onChange={(e) => setEditForm({ ...editForm, last_maintenance_at: e.target.value })}
                    className="w-full bg-slate-950 border border-blue-500/60 rounded-xl px-3 py-1.5 text-xs text-white outline-none"
                  />
                ) : (
                  <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5 text-blue-400" />
                    {formatDate(equipment.last_maintenance_at)}
                  </span>
                )}
              </div>

              {/* Chave Windows com máscara e botão Eye (RN-EQ-14) */}
              <div>
                <span className="text-slate-400 block text-[11px] font-semibold mb-1">CHAVE WINDOWS</span>
                {isEditing ? (
                  <input
                    type="text"
                    value={editForm.windows_key}
                    onChange={(e) => setEditForm({ ...editForm, windows_key: e.target.value })}
                    placeholder="XXXXX-XXXXX-XXXXX-XXXXX-XXXXX"
                    className="w-full bg-slate-950 border border-blue-500/60 rounded-xl px-3 py-1.5 text-xs text-white outline-none font-mono"
                  />
                ) : (
                  <div className="flex items-center justify-between bg-slate-950 border border-slate-800 rounded-xl px-3 py-2">
                    <span className="font-mono text-slate-200 truncate">
                      {equipment.windows_key
                        ? showWindowsKey
                          ? equipment.windows_key
                          : '•••••••••••••••••••••••••'
                        : 'Nenhuma chave registrada'}
                    </span>
                    {equipment.windows_key && (
                      <button
                        onClick={() => setShowWindowsKey(!showWindowsKey)}
                        className="p-1 text-slate-400 hover:text-white transition-colors cursor-pointer"
                        title={showWindowsKey ? 'Ocultar Chave' : 'Mostrar Chave'}
                      >
                        {showWindowsKey ? <EyeOff className="w-4 h-4 text-blue-400" /> : <Eye className="w-4 h-4" />}
                      </button>
                    )}
                  </div>
                )}
              </div>

              <div>
                <span className="text-slate-400 block text-[11px] font-semibold mb-1">OBSERVAÇÕES</span>
                {isEditing ? (
                  <textarea
                    value={editForm.notes}
                    onChange={(e) => setEditForm({ ...editForm, notes: e.target.value })}
                    rows={3}
                    className="w-full bg-slate-950 border border-blue-500/60 rounded-xl px-3 py-1.5 text-xs text-white outline-none resize-none"
                  />
                ) : (
                  <p className="text-slate-300 bg-slate-950/40 p-2.5 rounded-xl border border-slate-800/60 leading-relaxed text-[11px]">
                    {equipment.notes || 'Sem observações'}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Seção 4: Históricos na Mesma Tela (Movimentações e Manutenções) (RN-EQ-07 / RN-EQ-09 & RN-EQ-10) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
          {/* Bloco: Histórico de Movimentações */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <ArrowRightLeft className="w-4 h-4 text-blue-400" />
                <h2 className="text-sm font-bold text-white tracking-wide">Movimentações ({equipment.movements.length})</h2>
              </div>
            </div>

            {equipment.movements.length === 0 ? (
              <p className="text-xs text-slate-500 py-6 text-center">Nenhuma movimentação registrada.</p>
            ) : (
              <div className="space-y-3 max-h-80 overflow-y-auto pr-1 custom-scrollbar">
                {equipment.movements.map((mov) => (
                  <div key={mov.id} className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-xl space-y-1 text-xs">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 font-semibold text-slate-200">
                        <span>{mov.origin_location}</span>
                        <ArrowRightLeft className="w-3 h-3 text-blue-400" />
                        <span className="text-blue-300 font-bold">{mov.destination_location}</span>
                      </div>
                      <span className="text-slate-500 text-[10px] flex items-center gap-1">
                        <Calendar className="w-3 h-3 text-slate-500" />
                        {formatDate(mov.movement_date)}
                      </span>
                    </div>
                    {mov.notes && <p className="text-slate-400 text-[11px]">{mov.notes}</p>}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Bloco: Histórico de Manutenções com Múltiplos Itens, Edição e Exclusão (RN-EQ-09 & RN-EQ-10) */}
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Wrench className="w-4 h-4 text-blue-400" />
                <h2 className="text-sm font-bold text-white tracking-wide">Manutenções ({equipment.maintenances.length})</h2>
              </div>

              <button
                onClick={() => setIsMaintenanceModalOpen(true)}
                className="text-xs text-blue-400 hover:text-blue-300 font-semibold flex items-center gap-1 cursor-pointer"
              >
                <Plus className="w-3.5 h-3.5" /> Adicionar
              </button>
            </div>

            {equipment.maintenances.length === 0 ? (
              <p className="text-xs text-slate-500 py-6 text-center">Nenhuma manutenção técnica registrada.</p>
            ) : (
              <div className="space-y-3 max-h-80 overflow-y-auto pr-1 custom-scrollbar">
                {equipment.maintenances.map((maint) => (
                  <div key={maint.id} className="p-3.5 bg-slate-950/60 border border-slate-800/80 rounded-xl space-y-2 text-xs">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded bg-blue-500/10 border border-blue-500/20 text-blue-400 font-bold text-[10px]">
                          Manutenção
                        </span>
                        <span className="text-slate-400 text-[11px] flex items-center gap-1">
                          <Calendar className="w-3.5 h-3.5 text-slate-500" />
                          {formatDate(maint.maintenance_date)}
                        </span>
                      </div>

                      {/* Botões de Ação Editar e Excluir Manutenção (RN-EQ-10 / Cenários 11 e 12) */}
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => setEditingMaintenance(maint)}
                          className="p-1 text-slate-400 hover:text-blue-400 transition-colors cursor-pointer"
                          title="Editar manutenção"
                        >
                          <Edit className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleDeleteMaintenance(maint.id)}
                          className="p-1 text-slate-400 hover:text-red-400 transition-colors cursor-pointer"
                          title="Excluir manutenção"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>

                    <p className="text-slate-200 font-medium leading-relaxed whitespace-pre-line text-xs">
                      {maint.description}
                    </p>

                    {maint.notes && (
                      <p className="text-slate-400 text-[11px] bg-slate-900/50 p-2 rounded-lg border border-slate-800/60">
                        Obs: {maint.notes}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Modais */}
      <MovementModal
        isOpen={isMovementModalOpen}
        equipmentId={equipment.id}
        currentLocation={equipment.location}
        locations={locations}
        onClose={() => setIsMovementModalOpen(false)}
        onSuccess={() => fetchEquipmentDetail(equipment.id)}
      />

      <MaintenanceModal
        isOpen={isMaintenanceModalOpen}
        equipmentId={equipment.id}
        onClose={() => setIsMaintenanceModalOpen(false)}
        onSuccess={() => fetchEquipmentDetail(equipment.id)}
      />

      <EditMaintenanceModal
        isOpen={Boolean(editingMaintenance)}
        equipmentId={equipment.id}
        maintenance={editingMaintenance}
        onClose={() => setEditingMaintenance(null)}
        onSuccess={() => fetchEquipmentDetail(equipment.id)}
      />
    </div>
  );
};
