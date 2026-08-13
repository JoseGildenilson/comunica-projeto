import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Search, X, Check } from 'lucide-react';

interface MultiSelectFilterDropdownProps {
  label: string;
  options: string[];
  selectedValues: string[];
  onChange: (values: string[]) => void;
  placeholder?: string;
  testId?: string;
}

export const MultiSelectFilterDropdown: React.FC<MultiSelectFilterDropdownProps> = ({
  label,
  options,
  selectedValues,
  onChange,
  placeholder = 'Pesquisar...',
  testId,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Fechar dropdown ao clicar fora
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const filteredOptions = options.filter((opt) =>
    opt.toLowerCase().includes(search.toLowerCase())
  );

  const toggleOption = (option: string) => {
    if (selectedValues.includes(option)) {
      onChange(selectedValues.filter((item) => item !== option));
    } else {
      onChange([...selectedValues, option]);
    }
  };

  const handleClearAll = () => {
    onChange([]);
  };

  // Texto do botão principal do filtro (RN-04 / Seção 3.4)
  const getButtonText = () => {
    if (selectedValues.length === 0) return label;
    if (selectedValues.length === 1) return `${label}: ${selectedValues[0]}`;
    return `${label} (${selectedValues.length})`;
  };

  return (
    <div className="relative inline-block text-left" ref={dropdownRef} data-testid={testId}>
      {/* Botão Gatilho */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={`px-3 py-1.5 rounded-xl border text-xs font-semibold flex items-center justify-between gap-2 transition-all cursor-pointer ${
          selectedValues.length > 0
            ? 'bg-blue-600/15 border-blue-500/50 text-blue-400 shadow-sm shadow-blue-500/10'
            : 'bg-slate-950 border-slate-800 text-slate-300 hover:border-slate-700'
        }`}
      >
        <span className="truncate max-w-[140px]">{getButtonText()}</span>
        <ChevronDown className={`w-3.5 h-3.5 transition-transform duration-200 ${isOpen ? 'rotate-180 text-blue-400' : 'text-slate-400'}`} />
      </button>

      {/* Painel Dropdown Estilo Google Sheets */}
      {isOpen && (
        <div className="absolute left-0 mt-1.5 w-64 bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl z-50 p-3 space-y-2.5 animate-fade-in">
          {/* Busca Interna */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={placeholder}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-8 pr-2.5 py-1.5 text-xs text-white outline-none input-focus-glow placeholder:text-slate-500"
            />
            {search && (
              <button
                type="button"
                onClick={() => setSearch('')}
                className="absolute right-2 top-2 text-slate-500 hover:text-white"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* Lista de Opções com Checkboxes */}
          <div className="max-h-48 overflow-y-auto space-y-1 pr-1 custom-scrollbar">
            {filteredOptions.length === 0 ? (
              <p className="text-[11px] text-slate-500 py-2 text-center">Nenhuma opção encontrada</p>
            ) : (
              filteredOptions.map((opt) => {
                const isSelected = selectedValues.includes(opt);
                return (
                  <label
                    key={opt}
                    onClick={() => toggleOption(opt)}
                    className="flex items-center gap-2.5 px-2.5 py-1.5 rounded-lg text-xs text-slate-200 hover:bg-slate-800/80 cursor-pointer select-none transition-colors"
                  >
                    <div
                      className={`w-4 h-4 rounded border flex items-center justify-center transition-colors ${
                        isSelected
                          ? 'bg-blue-600 border-blue-500 text-white'
                          : 'bg-slate-950 border-slate-700 hover:border-slate-500'
                      }`}
                    >
                      {isSelected && <Check className="w-3 h-3 stroke-[3]" />}
                    </div>
                    <span className="truncate">{opt}</span>
                  </label>
                );
              })
            )}
          </div>

          {/* Rodapé com botão Desmarcar Tudo (RN-11) */}
          <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px]">
            <span className="text-slate-400">
              {selectedValues.length} {selectedValues.length === 1 ? 'selecionado' : 'selecionados'}
            </span>
            {selectedValues.length > 0 && (
              <button
                type="button"
                onClick={handleClearAll}
                className="text-blue-400 hover:text-blue-300 font-semibold cursor-pointer"
              >
                Desmarcar tudo
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
