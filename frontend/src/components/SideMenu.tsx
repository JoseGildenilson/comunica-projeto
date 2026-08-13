import React, { useState } from 'react';
import { createPortal } from 'react-dom';
import { useAuth } from '../hooks/useAuth';
import { 
  Menu, 
  X, 
  HardDrive, 
  User as UserIcon, 
  LogOut, 
  ShieldCheck 
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const SideMenu: React.FC = () => {
  // Inicialmente oculto por padrão (RN-01)
  const [isOpen, setIsOpen] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const closeMenu = () => {
    setIsClosing(true);
    setTimeout(() => {
      setIsOpen(false);
      setIsClosing(false);
    }, 300); // Sincronizado com o tempo da animação CSS (0.3s)
  };

  const toggleMenu = () => {
    if (isOpen) {
      closeMenu();
    } else {
      setIsOpen(true);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login', { replace: true });
  };

  const isTecnico = user?.role === 'tecnico';

  return (
    <>
      {/* Botão de alternância do Menu (RN-01) */}
      <button
        onClick={toggleMenu}
        aria-label="Toggle Menu"
        data-testid="toggle-menu-btn"
        className="p-2 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/60 text-slate-300 hover:text-white transition-all shadow-md flex items-center justify-center cursor-pointer"
      >
        {isOpen && !isClosing ? <X className="w-5 h-5 text-blue-400" /> : <Menu className="w-5 h-5 text-blue-400" />}
      </button>

      {/* Portal para renderizar o menu e overlay fora do contexto do header (evita bugs com backdrop-blur no elemento pai) */}
      {(isOpen || isClosing) && createPortal(
        <>
          {/* Overlay translúcido para focar no menu e capturar cliques */}
          <div
            onClick={closeMenu}
            className={`fixed inset-0 bg-slate-950/70 backdrop-blur-sm z-[100] ${
              isClosing ? 'animate-fade-out-overlay' : 'animate-fade-in-overlay'
            }`}
          />

          {/* Gaveta do Menu Lateral */}
          <aside
            data-testid="side-menu"
            className={`fixed top-0 left-0 bottom-0 w-72 bg-slate-950 border-r border-slate-800 shadow-[4px_0_24px_rgba(0,0,0,0.6)] z-[101] p-6 flex flex-col justify-between ${
              isClosing ? 'animate-slide-out-left' : 'animate-slide-in-left'
            }`}
          >
            <div>
              {/* Header do Menu */}
              <div className="flex items-center justify-between pb-6 border-b border-slate-800/80">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-600/20 text-blue-400 border border-blue-500/30 rounded-xl">
                    <HardDrive className="w-6 h-6" />
                  </div>
                  <div>
                    <h2 className="text-sm font-bold text-white tracking-wide">Menu Principal</h2>
                    <p className="text-[11px] text-slate-400">Gestão Interna</p>
                  </div>
                </div>
                <button
                  onClick={closeMenu}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Informações do Usuário (RN-02) */}
              <div className="my-6 p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400">
                  <UserIcon className="w-5 h-5" />
                </div>
                <div className="overflow-hidden">
                  <p className="text-xs text-slate-400 truncate">Usuário Conectado</p>
                  <p className="text-xs font-semibold text-slate-200 truncate" title={user?.email}>
                    {user?.email}
                  </p>
                  <div className="mt-1 inline-flex items-center gap-1 px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-bold uppercase text-[9px]">
                    <ShieldCheck className="w-3 h-3 text-blue-400" />
                    {user?.role}
                  </div>
                </div>
              </div>

              {/* Itens do Menu (RN-04 / Cenário 3) */}
              <nav className="space-y-2">
                {isTecnico && (
                  <button
                    onClick={() => {
                      closeMenu();
                      // Wait for animation to finish before navigating, or navigate immediately
                      setTimeout(() => navigate('/equipamentos'), 300);
                    }}
                    data-testid="patrimonio-menu-item"
                    className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-blue-600/10 hover:bg-blue-600/20 border border-blue-500/30 text-blue-300 font-medium text-xs transition-all group cursor-pointer"
                  >
                    <HardDrive className="w-4 h-4 text-blue-400 group-hover:scale-110 transition-transform" />
                    <span>Painel de Patrimônio</span>
                  </button>
                )}
              </nav>
            </div>

            {/* Footer do Menu - Botão de Logout */}
            <div className="pt-4 border-t border-slate-800/80">
              <button
                onClick={handleLogout}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-slate-800 hover:bg-red-500/20 text-slate-300 hover:text-red-300 rounded-xl text-xs font-semibold transition-all border border-slate-700/60 hover:border-red-500/30 cursor-pointer"
              >
                <LogOut className="w-4 h-4 text-red-400" />
                <span>Encerrar Sessão</span>
              </button>
            </div>
          </aside>
        </>,
        document.body
      )}
    </>
  );
};
