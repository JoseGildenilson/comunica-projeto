import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  HardDrive,
  Plus,
  Search,
  RotateCcw,
  SlidersHorizontal,
  ChevronLeft,
  ChevronRight,
  ArrowLeft,
  Monitor,
  Laptop,
  Smartphone,
  Printer,
  Calendar,
  MapPin,
  Tag as TagIcon,
} from 'lucide-react';
import { equipmentApi } from '../api/equipmentApi';
import { Equipment, EquipmentFilterParams, EquipmentTag } from '../types/equipment';
import { SideMenu } from '../components/SideMenu';
import { NewEquipmentModal } from '../components/NewEquipmentModal';
import { MultiSelectFilterDropdown } from '../components/MultiSelectFilterDropdown';

export const EquipmentListPage: React.FC = () => {
  const navigate = useNavigate();

  // Data states
  const [equipments, setEquipments] = useState<Equipment[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Tag filter options
  const [types, setTypes] = useState<EquipmentTag[]>([]);
  const [locations, setLocations] = useState<EquipmentTag[]>([]);
  const [statuses, setStatuses] = useState<EquipmentTag[]>([]);

  // Multi-select filter states (RN-09 / RN-12)
  const [filterTypes, setFilterTypes] = useState<string[]>([]);
  const [filterLocations, setFilterLocations] = useState<string[]>([]);
  const [filterStatuses, setFilterStatuses] = useState<string[]>([]);
  const [filterPatrimonies, setFilterPatrimonies] = useState<string[]>([]);
  const [filterSerials, setFilterSerials] = useState<string[]>([]);
  const [filterProducts, setFilterProducts] = useState<string[]>([]);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');

  // Text inputs for adding Patrimony, Serial or Product filter chips
  const [inputPatrimony, setInputPatrimony] = useState('');
  const [inputSerial, setInputSerial] = useState('');
  const [inputProduct, setInputProduct] = useState('');

  // Modals
  const [isNewModalOpen, setIsNewModalOpen] = useState(false);

  useEffect(() => {
    fetchTags();
  }, []);

  useEffect(() => {
    fetchEquipments();
  }, [
    page,
    filterTypes,
    filterLocations,
    filterStatuses,
    filterPatrimonies,
    filterSerials,
    filterProducts,
    search,
    sortBy,
    sortDir,
  ]);

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

  const fetchEquipments = async () => {
    setLoading(true);
    try {
      const params: EquipmentFilterParams = {
        page,
        limit: 25,
        type: filterTypes.length > 0 ? filterTypes : undefined,
        location: filterLocations.length > 0 ? filterLocations : undefined,
        status: filterStatuses.length > 0 ? filterStatuses : undefined,
        patrimony_number: filterPatrimonies.length > 0 ? filterPatrimonies : undefined,
        serial_number: filterSerials.length > 0 ? filterSerials : undefined,
        product_number: filterProducts.length > 0 ? filterProducts : undefined,
        search: search || undefined,
        sort_by: sortBy,
        sort_dir: sortDir,
      };

      const res = await equipmentApi.getEquipments(params);
      setEquipments(res.items);
      setTotal(res.total);
      setPages(res.pages);
    } catch (err) {
      console.error('Erro ao buscar equipamentos:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClearFilters = () => {
    setFilterTypes([]);
    setFilterLocations([]);
    setFilterStatuses([]);
    setFilterPatrimonies([]);
    setFilterSerials([]);
    setFilterProducts([]);
    setInputPatrimony('');
    setInputSerial('');
    setInputProduct('');
    setSearch('');
    setSortBy('created_at');
    setSortDir('desc');
    setPage(1);
  };

  const hasActiveFilters =
    filterTypes.length > 0 ||
    filterLocations.length > 0 ||
    filterStatuses.length > 0 ||
    filterPatrimonies.length > 0 ||
    filterSerials.length > 0 ||
    filterProducts.length > 0 ||
    Boolean(search);

  const getEquipmentIcon = (type: string) => {
    const t = type.toLowerCase();
    if (t.includes('notebook') || t.includes('laptop')) return <Laptop className="w-5 h-5 text-blue-400" />;
    if (t.includes('monitor') || t.includes('tela')) return <Monitor className="w-5 h-5 text-indigo-400" />;
    if (t.includes('impressora')) return <Printer className="w-5 h-5 text-amber-400" />;
    if (t.includes('celular') || t.includes('tablet')) return <Smartphone className="w-5 h-5 text-emerald-400" />;
    return <HardDrive className="w-5 h-5 text-blue-400" />;
  };

  const formatDate = (dateStr?: string | null) => {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString('pt-BR');
  };

  const handleAddTextFilter = (
    value: string,
    currentList: string[],
    setList: (val: string[]) => void,
    clearInput: () => void
  ) => {
    if (!value.trim()) return;
    if (!currentList.includes(value.trim())) {
      setList([...currentList, value.trim()]);
      setPage(1);
    }
    clearInput();
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Top Header */}
      <header className="sticky top-0 z-40 bg-slate-950/80 backdrop-blur-md border-b border-slate-800/80 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <SideMenu />
            
            {/* Botão ← Voltar ao Dashboard */}
            <button
              onClick={() => navigate('/dashboard')}
              data-testid="back-to-dashboard-btn"
              className="p-2 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-xl text-slate-400 hover:text-white transition-colors cursor-pointer flex items-center gap-2 text-xs font-semibold"
              title="Voltar ao Dashboard"
            >
              <ArrowLeft className="w-4 h-4" />
              <span className="hidden sm:inline">Voltar ao Dashboard</span>
            </button>

            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-xl font-extrabold text-white tracking-wide">Equipamentos</h1>
                <span className="px-2.5 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-semibold">
                  {total} {total === 1 ? 'equipamento' : 'equipamentos'}
                </span>
              </div>
              <p className="text-xs text-slate-400">Gestão centralizada de patrimônio e ativos de TI</p>
            </div>
          </div>

          <button
            onClick={() => setIsNewModalOpen(true)}
            data-testid="new-equipment-btn"
            className="px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold btn-glow-transition shadow-lg shadow-blue-500/20 flex items-center gap-2 cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>Novo Equipamento</span>
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-6 space-y-6">
        {/* Barra de Filtros Sempre Visível estilo Google Sheets */}
        <section className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
              <SlidersHorizontal className="w-4 h-4 text-blue-400" />
              <span>Filtros Avançados & Seleção Múltipla</span>
            </div>

            {hasActiveFilters && (
              <button
                onClick={handleClearFilters}
                className="text-xs text-slate-400 hover:text-red-400 flex items-center gap-1.5 transition-colors cursor-pointer"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Limpar filtros</span>
              </button>
            )}
          </div>

          {/* Grid de Dropdowns de Seleção Múltipla */}
          <div className="flex flex-wrap items-center gap-3">
            {/* Filtro Múltiplo: Tipo */}
            <MultiSelectFilterDropdown
              label="Tipo"
              options={types.map((t) => t.name)}
              selectedValues={filterTypes}
              onChange={(vals) => { setFilterTypes(vals); setPage(1); }}
              placeholder="Pesquisar tipo..."
              testId="filter-type-dropdown"
            />

            {/* Filtro Múltiplo: Localização */}
            <MultiSelectFilterDropdown
              label="Localização"
              options={locations.map((l) => l.name)}
              selectedValues={filterLocations}
              onChange={(vals) => { setFilterLocations(vals); setPage(1); }}
              placeholder="Pesquisar localização..."
              testId="filter-location-dropdown"
            />

            {/* Filtro Múltiplo: Situação */}
            <MultiSelectFilterDropdown
              label="Situação"
              options={statuses.map((s) => s.name)}
              selectedValues={filterStatuses}
              onChange={(vals) => { setFilterStatuses(vals); setPage(1); }}
              placeholder="Pesquisar situação..."
              testId="filter-status-dropdown"
            />

            {/* Filtro Textual Múltiplo: Nº Patrimônio */}
            <div className="flex items-center bg-slate-950 border border-slate-800 rounded-xl px-2.5 py-1 text-xs">
              <input
                type="text"
                placeholder="Adicionar Patrimônio..."
                value={inputPatrimony}
                onChange={(e) => setInputPatrimony(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddTextFilter(inputPatrimony, filterPatrimonies, setFilterPatrimonies, () => setInputPatrimony(''));
                  }
                }}
                className="bg-transparent text-slate-200 outline-none w-32 placeholder:text-slate-500"
              />
              {filterPatrimonies.length > 0 && (
                <span className="ml-1 px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 font-bold text-[10px]">
                  {filterPatrimonies.length}
                </span>
              )}
            </div>

            {/* Filtro Textual Múltiplo: Nº Série */}
            <div className="flex items-center bg-slate-950 border border-slate-800 rounded-xl px-2.5 py-1 text-xs">
              <input
                type="text"
                placeholder="Adicionar Série..."
                value={inputSerial}
                onChange={(e) => setInputSerial(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddTextFilter(inputSerial, filterSerials, setFilterSerials, () => setInputSerial(''));
                  }
                }}
                className="bg-transparent text-slate-200 outline-none w-28 placeholder:text-slate-500"
              />
              {filterSerials.length > 0 && (
                <span className="ml-1 px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 font-bold text-[10px]">
                  {filterSerials.length}
                </span>
              )}
            </div>

            {/* Filtro Textual Múltiplo: Nº Produto */}
            <div className="flex items-center bg-slate-950 border border-slate-800 rounded-xl px-2.5 py-1 text-xs">
              <input
                type="text"
                placeholder="Adicionar Produto..."
                value={inputProduct}
                onChange={(e) => setInputProduct(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddTextFilter(inputProduct, filterProducts, setFilterProducts, () => setInputProduct(''));
                  }
                }}
                className="bg-transparent text-slate-200 outline-none w-28 placeholder:text-slate-500"
              />
              {filterProducts.length > 0 && (
                <span className="ml-1 px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 font-bold text-[10px]">
                  {filterProducts.length}
                </span>
              )}
            </div>

            {/* Busca Geral */}
            <div className="relative flex-1 min-w-[180px]">
              <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
              <input
                type="text"
                placeholder="Pesquisar..."
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-8 pr-2.5 py-1.5 text-xs text-slate-200 outline-none input-focus-glow placeholder:text-slate-500"
              />
            </div>
          </div>

          {/* Chips de Valores Selecionados */}
          {(filterPatrimonies.length > 0 || filterSerials.length > 0 || filterProducts.length > 0) && (
            <div className="flex items-center gap-2 flex-wrap pt-2 border-t border-slate-800/60 text-[11px]">
              {filterPatrimonies.map((pat) => (
                <span key={pat} className="px-2 py-0.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-200 flex items-center gap-1">
                  Patrimônio: {pat}
                  <button onClick={() => setFilterPatrimonies(filterPatrimonies.filter((p) => p !== pat))} className="hover:text-red-400">×</button>
                </span>
              ))}
              {filterSerials.map((ser) => (
                <span key={ser} className="px-2 py-0.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-200 flex items-center gap-1">
                  Série: {ser}
                  <button onClick={() => setFilterSerials(filterSerials.filter((s) => s !== ser))} className="hover:text-red-400">×</button>
                </span>
              ))}
              {filterProducts.map((prod) => (
                <span key={prod} className="px-2 py-0.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-200 flex items-center gap-1">
                  Produto: {prod}
                  <button onClick={() => setFilterProducts(filterProducts.filter((pr) => pr !== prod))} className="hover:text-red-400">×</button>
                </span>
              ))}
            </div>
          )}
        </section>

        {/* Área de Ordenação */}
        <div className="flex items-center justify-between text-xs text-slate-400 px-1">
          <div className="flex items-center gap-2">
            <span>Ordenar por:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded-lg px-2 py-1 text-slate-200 outline-none cursor-pointer"
            >
              <option value="created_at">Mais recentes / Antigos</option>
              <option value="last_maintenance_at">Última manutenção</option>
              <option value="serial_number">Nº Série</option>
              <option value="patrimony_number">Nº Patrimônio</option>
              <option value="equipment_type">Tipo</option>
              <option value="location">Localização</option>
            </select>

            <button
              onClick={() => setSortDir(sortDir === 'asc' ? 'desc' : 'asc')}
              className="px-2 py-1 bg-slate-900 border border-slate-800 rounded-lg text-slate-300 hover:text-white transition-colors cursor-pointer"
            >
              {sortDir === 'asc' ? '↑ Crescente' : '↓ Decrescente'}
            </button>
          </div>

          <div>
            Página <strong className="text-white">{page}</strong> de <strong className="text-white">{pages}</strong>
          </div>
        </div>

        {/* Listagem com Cores Intercaladas (Zebra Striping) & Layout Horizontal Limpo Restaurado */}
        {loading ? (
          <div className="py-20 flex flex-col items-center justify-center gap-3 text-slate-500">
            <div className="w-8 h-8 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin" />
            <p className="text-xs">Carregando patrimônio...</p>
          </div>
        ) : equipments.length === 0 ? (
          <div className="py-16 text-center bg-slate-900/30 border border-slate-800/60 rounded-2xl space-y-2">
            <HardDrive className="w-10 h-10 text-slate-600 mx-auto" />
            <p className="text-sm font-semibold text-slate-300">Nenhum equipamento encontrado</p>
            <p className="text-xs text-slate-500">Tente ajustar os filtros de pesquisa para visualizar outros ativos.</p>
          </div>
        ) : (
          <div className="space-y-4 sm:space-y-5">
            {equipments.map((item, index) => {
              // Intercalação de cores nos blocos com alto contraste, respiro interno ajustado e tamanho de fonte refinado
              const isEven = index % 2 === 0;
              const cardBg = isEven
                ? 'bg-slate-900 border-2 border-slate-700/90 shadow-xl shadow-black/50'
                : 'bg-slate-900/60 border-2 border-slate-800/90 shadow-lg shadow-black/40';

              return (
                <div
                  key={item.id}
                  onClick={() => navigate(`/equipamentos/${item.id}`)}
                  style={{ animationDelay: `${index * 40}ms` }}
                  data-testid={`equipment-card-${item.id}`}
                  className={`${cardBg} hover:border-blue-500/80 rounded-2xl p-5 sm:px-6 sm:py-5 transition-all duration-200 hover:shadow-2xl hover:shadow-blue-500/10 cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4 sm:gap-5 animate-slide-in-right opacity-0`}
                >
                  {/* Lado Esquerdo: Ícone + Título Refinado + Metadados Inline */}
                  <div className="flex items-start sm:items-center gap-4">
                    <div className="p-3 bg-slate-950/90 border border-slate-700/80 rounded-xl shrink-0 shadow-inner">
                      {getEquipmentIcon(item.equipment_type)}
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <h3 className="text-sm sm:text-base font-bold text-white tracking-wide">{item.description}</h3>
                        {item.brand && (
                          <span className="text-[10px] px-2 py-0.5 rounded-md bg-slate-800 border border-slate-700 text-slate-300 font-medium">
                            {item.brand}
                          </span>
                        )}
                        <span className="text-[10px] px-2 py-0.5 rounded-md bg-blue-500/15 border border-blue-500/40 text-blue-400 font-bold">
                          {item.equipment_type}
                        </span>
                      </div>

                      {/* Metadados Inline Organizados com Excelente Respiro */}
                      <div className="flex items-center gap-3 text-xs text-slate-300 flex-wrap pt-0.5">
                        <span className="flex items-center gap-1">
                          <MapPin className="w-3.5 h-3.5 text-blue-400" />
                          <strong className="text-slate-200 font-semibold">{item.location}</strong>
                        </span>
                        <span className="text-slate-600">·</span>
                        <span className="flex items-center gap-1">
                          <TagIcon className="w-3.5 h-3.5 text-indigo-400" />
                          <strong className="text-slate-200 font-semibold">{item.status}</strong>
                        </span>
                        {item.patrimony_number && (
                          <>
                            <span className="text-slate-600">·</span>
                            <span>Patrimônio: <strong className="text-slate-100 font-semibold">{item.patrimony_number}</strong></span>
                          </>
                        )}
                        <span className="text-slate-600">·</span>
                        <span>SN: <strong className="text-slate-100 font-mono font-semibold">{item.serial_number}</strong></span>
                      </div>
                    </div>
                  </div>

                  {/* Lado Direito: Data da Última Manutenção */}
                  <div className="text-right shrink-0 border-t md:border-t-0 border-slate-800/90 pt-2.5 md:pt-0 flex md:flex-col justify-between items-center md:items-end text-xs text-slate-400">
                    <span className="text-[11px] text-slate-400 font-medium uppercase tracking-wider">Última Manutenção</span>
                    <span className="flex items-center gap-1 text-slate-100 font-bold mt-0.5 text-xs sm:text-sm">
                      <Calendar className="w-3.5 h-3.5 text-blue-400" />
                      {formatDate(item.last_maintenance_at)}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Paginação */}
        {pages > 1 && (
          <div className="flex items-center justify-between pt-4 border-t border-slate-800">
            <button
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              className="px-3.5 py-2 bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 disabled:opacity-40 rounded-xl text-xs flex items-center gap-1 transition-colors cursor-pointer"
            >
              <ChevronLeft className="w-4 h-4" /> Anterior
            </button>

            <span className="text-xs text-slate-400">
              Página <strong className="text-white">{page}</strong> de <strong className="text-white">{pages}</strong>
            </span>

            <button
              disabled={page >= pages}
              onClick={() => setPage((p) => Math.min(pages, p + 1))}
              className="px-3.5 py-2 bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 disabled:opacity-40 rounded-xl text-xs flex items-center gap-1 transition-colors cursor-pointer"
            >
              Próxima <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </main>

      {/* Modal de Cadastro de Equipamento */}
      <NewEquipmentModal
        isOpen={isNewModalOpen}
        onClose={() => setIsNewModalOpen(false)}
        onSuccess={() => {
          fetchEquipments();
          fetchTags();
        }}
      />
    </div>
  );
};
