import React, { useState, useEffect } from 'react';
import {
  X,
  Plus,
  Tag as TagIcon,
  MapPin,
  Laptop,
  CheckCircle,
  AlertCircle,
  Edit2,
  Trash2,
  Check,
} from 'lucide-react';
import { equipmentApi } from '../api/equipmentApi';
import { EquipmentTag } from '../types/equipment';

interface ManageTagsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onTagsUpdated?: () => void;
}

type CategoryType = 'tipo' | 'localizacao' | 'situacao';

const CATEGORIES: { id: CategoryType; label: string; icon: React.FC<{ className?: string }> }[] = [
  { id: 'tipo', label: 'Tipos de Equipamento', icon: Laptop },
  { id: 'localizacao', label: 'Localizações', icon: MapPin },
  { id: 'situacao', label: 'Situações (Status)', icon: TagIcon },
];

export const ManageTagsModal: React.FC<ManageTagsModalProps> = ({
  isOpen,
  onClose,
  onTagsUpdated,
}) => {
  const [activeCategory, setActiveCategory] = useState<CategoryType>('tipo');
  const [tags, setTags] = useState<EquipmentTag[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // New tag input
  const [newTagName, setNewTagName] = useState('');
  const [addingTag, setAddingTag] = useState(false);

  // Editing state
  const [editingTagId, setEditingTagId] = useState<number | null>(null);
  const [editingTagName, setEditingTagName] = useState('');
  const [savingEdit, setSavingEdit] = useState(false);

  // Deleting state
  const [deletingTagId, setDeletingTagId] = useState<number | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetchTags();
      setError(null);
      setSuccessMsg(null);
      setNewTagName('');
      setEditingTagId(null);
      setDeletingTagId(null);
    }
  }, [isOpen]);

  const fetchTags = async () => {
    setLoading(true);
    try {
      const data = await equipmentApi.getTags();
      setTags(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao carregar tags.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const currentCategoryTags = tags.filter((t) => t.category === activeCategory);

  const handleAddTag = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTagName.trim()) return;

    setError(null);
    setSuccessMsg(null);
    setAddingTag(true);

    try {
      await equipmentApi.createTag(activeCategory, newTagName.trim());
      setNewTagName('');
      setSuccessMsg('Tag cadastrada com sucesso.');
      await fetchTags();
      if (onTagsUpdated) onTagsUpdated();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao cadastrar tag.');
    } finally {
      setAddingTag(false);
    }
  };

  const handleStartEdit = (tag: EquipmentTag) => {
    setEditingTagId(tag.id);
    setEditingTagName(tag.name);
    setError(null);
    setSuccessMsg(null);
  };

  const handleCancelEdit = () => {
    setEditingTagId(null);
    setEditingTagName('');
  };

  const handleSaveEdit = async (tagId: number) => {
    if (!editingTagName.trim()) {
      setError('O nome da tag não pode ser vazio.');
      return;
    }

    setError(null);
    setSuccessMsg(null);
    setSavingEdit(true);

    try {
      await equipmentApi.updateTag(tagId, editingTagName.trim());
      setEditingTagId(null);
      setEditingTagName('');
      setSuccessMsg('Tag renomeada com sucesso.');
      await fetchTags();
      if (onTagsUpdated) onTagsUpdated();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao renomear tag.');
    } finally {
      setSavingEdit(false);
    }
  };

  const handleDeleteTag = async (tagId: number) => {
    setError(null);
    setSuccessMsg(null);

    try {
      await equipmentApi.deleteTag(tagId);
      setDeletingTagId(null);
      setSuccessMsg('Tag excluída com sucesso.');
      await fetchTags();
      if (onTagsUpdated) onTagsUpdated();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao excluir tag.');
    }
  };

  return (
    <div
      data-testid="manage-tags-modal"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/70 backdrop-blur-sm animate-fade-in-overlay overflow-y-auto"
    >
      <div className="bg-zinc-950 border border-zinc-800 rounded-2xl shadow-dropdown w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden animate-fade-in my-auto">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-zinc-800 bg-zinc-900/60">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-zinc-900 border border-zinc-800 text-zinc-300 rounded-lg">
              <TagIcon className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-zinc-100 tracking-tight">Gerenciador de Tags</h2>
              <p className="text-[11px] text-zinc-500 font-mono">CADASTRO E MANUTENÇÃO DE CATEGORIAS</p>
            </div>
          </div>
          <button
            onClick={onClose}
            data-testid="close-tags-modal-btn"
            className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Feedback Banners */}
        {error && (
          <div className="mx-6 mt-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {successMsg && (
          <div className="mx-6 mt-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center gap-2">
            <CheckCircle className="w-4 h-4 shrink-0" />
            <span>{successMsg}</span>
          </div>
        )}

        {/* Category Tabs */}
        <div className="flex border-b border-zinc-800 bg-zinc-900/40 px-6 pt-2">
          {CATEGORIES.map((cat) => {
            const Icon = cat.icon;
            const count = tags.filter((t) => t.category === cat.id).length;
            const isActive = activeCategory === cat.id;

            return (
              <button
                key={cat.id}
                onClick={() => {
                  setActiveCategory(cat.id);
                  setError(null);
                  setSuccessMsg(null);
                  setEditingTagId(null);
                  setDeletingTagId(null);
                }}
                data-testid={`tab-${cat.id}`}
                className={`flex items-center gap-2 px-4 py-3 text-xs font-semibold border-b-2 transition-all cursor-pointer ${
                  isActive
                    ? 'border-white text-white bg-zinc-900/60'
                    : 'border-transparent text-zinc-400 hover:text-zinc-200'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{cat.label}</span>
                <span className="px-1.5 py-0.2 rounded bg-zinc-800 text-[10px] text-zinc-300 font-mono">
                  {count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Body Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5 custom-scrollbar">
          {/* Add Tag Form */}
          <form onSubmit={handleAddTag} className="flex gap-2">
            <input
              type="text"
              value={newTagName}
              onChange={(e) => setNewTagName(e.target.value)}
              placeholder={`Adicionar novo ${
                activeCategory === 'tipo'
                  ? 'tipo de equipamento'
                  : activeCategory === 'localizacao'
                  ? 'local'
                  : 'status'
              }...`}
              className="flex-1 bg-zinc-900 border border-zinc-800 rounded-xl px-3.5 py-2 text-xs text-zinc-100 placeholder:text-zinc-500 focus:border-zinc-500 outline-none"
            />
            <button
              type="submit"
              disabled={addingTag || !newTagName.trim()}
              data-testid="add-tag-btn"
              className="px-4 py-2 bg-zinc-100 hover:bg-white text-zinc-950 rounded-xl text-xs font-semibold transition-all shadow-sm disabled:opacity-50 cursor-pointer flex items-center gap-1.5 active:scale-[0.99]"
            >
              {addingTag ? (
                <div className="w-3.5 h-3.5 border-2 border-zinc-400 border-t-zinc-950 rounded-full animate-spin" />
              ) : (
                <>
                  <Plus className="w-3.5 h-3.5" />
                  <span>Adicionar</span>
                </>
              )}
            </button>
          </form>

          {/* Tags List */}
          <div className="space-y-2">
            <h3 className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider font-mono">
              Tags Cadastradas ({currentCategoryTags.length})
            </h3>

            {loading ? (
              <div className="py-10 flex flex-col items-center justify-center gap-2 text-zinc-500 text-xs">
                <div className="w-5 h-5 border-2 border-zinc-800 border-t-white rounded-full animate-spin" />
                <span>Carregando tags...</span>
              </div>
            ) : currentCategoryTags.length === 0 ? (
              <div className="py-8 text-center bg-zinc-900/30 border border-zinc-800/80 rounded-xl">
                <p className="text-xs text-zinc-400">Nenhuma tag cadastrada nesta categoria.</p>
                <p className="text-[11px] text-zinc-500 mt-1">Utilize o campo acima para adicionar.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {currentCategoryTags.map((tag) => {
                  const isEditingThis = editingTagId === tag.id;
                  const isConfirmingDelete = deletingTagId === tag.id;

                  if (isEditingThis) {
                    return (
                      <div
                        key={tag.id}
                        className="flex items-center gap-1.5 p-2 bg-zinc-900 border border-zinc-700 rounded-xl"
                      >
                        <input
                          type="text"
                          value={editingTagName}
                          onChange={(e) => setEditingTagName(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleSaveEdit(tag.id);
                            if (e.key === 'Escape') handleCancelEdit();
                          }}
                          autoFocus
                          className="flex-1 bg-zinc-950 border border-zinc-700 rounded-lg px-2.5 py-1 text-xs text-white outline-none focus:border-zinc-400"
                        />
                        <button
                          type="button"
                          onClick={() => handleSaveEdit(tag.id)}
                          disabled={savingEdit}
                          data-testid={`save-tag-btn-${tag.id}`}
                          className="p-1.5 bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 rounded-lg transition-colors cursor-pointer"
                          title="Salvar"
                        >
                          <Check className="w-3.5 h-3.5" />
                        </button>
                        <button
                          type="button"
                          onClick={handleCancelEdit}
                          data-testid={`cancel-tag-btn-${tag.id}`}
                          className="p-1.5 bg-zinc-800 text-zinc-400 hover:text-white rounded-lg transition-colors cursor-pointer"
                          title="Cancelar"
                        >
                          <X className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    );
                  }

                  if (isConfirmingDelete) {
                    return (
                      <div
                        key={tag.id}
                        className="flex items-center justify-between gap-2 p-2 bg-red-500/10 border border-red-500/30 rounded-xl text-xs text-red-400"
                      >
                        <span className="truncate">Excluir &quot;{tag.name}&quot;?</span>
                        <div className="flex items-center gap-1 shrink-0">
                          <button
                            type="button"
                            onClick={() => handleDeleteTag(tag.id)}
                            data-testid={`confirm-delete-tag-btn-${tag.id}`}
                            className="px-2 py-0.5 bg-red-500 text-white text-[11px] font-semibold rounded hover:bg-red-600 transition-colors cursor-pointer"
                          >
                            Sim
                          </button>
                          <button
                            type="button"
                            onClick={() => setDeletingTagId(null)}
                            data-testid={`cancel-delete-tag-btn-${tag.id}`}
                            className="px-2 py-0.5 bg-zinc-800 text-zinc-300 text-[11px] rounded hover:bg-zinc-700 transition-colors cursor-pointer"
                          >
                            Não
                          </button>
                        </div>
                      </div>
                    );
                  }

                  return (
                    <div
                      key={tag.id}
                      data-testid={`tag-item-${tag.id}`}
                      className="flex items-center justify-between gap-2 p-2.5 bg-zinc-900/60 border border-zinc-800 rounded-xl hover:border-zinc-700 transition-colors"
                    >
                      <span className="text-xs font-medium text-zinc-200 truncate">{tag.name}</span>
                      <div className="flex items-center gap-1 shrink-0">
                        <button
                          type="button"
                          onClick={() => handleStartEdit(tag)}
                          data-testid={`edit-tag-btn-${tag.id}`}
                          className="p-1 text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800 rounded-lg transition-colors cursor-pointer"
                          title="Renomear tag"
                        >
                          <Edit2 className="w-3.5 h-3.5" />
                        </button>
                        <button
                          type="button"
                          onClick={() => setDeletingTagId(tag.id)}
                          data-testid={`delete-tag-btn-${tag.id}`}
                          className="p-1 text-zinc-500 hover:text-red-400 hover:bg-zinc-800 rounded-lg transition-colors cursor-pointer"
                          title="Excluir tag"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-3.5 border-t border-zinc-800 bg-zinc-900/40 text-[11px] text-zinc-500">
          <span>* A renomeação atualiza automaticamente os equipamentos associados.</span>
          <button
            type="button"
            onClick={onClose}
            className="px-3.5 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-200 rounded-xl text-xs font-medium transition-colors cursor-pointer"
          >
            Fechar
          </button>
        </div>
      </div>
    </div>
  );
};
