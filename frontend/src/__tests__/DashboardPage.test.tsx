import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { DashboardPage } from '../pages/DashboardPage';
import { authApi } from '../api/authApi';
import { dashboardApi } from '../api/dashboardApi';

vi.mock('../api/authApi', () => ({
  authApi: {
    getMe: vi.fn(),
    login: vi.fn(),
    refresh: vi.fn(),
    logout: vi.fn(),
  },
}));

vi.mock('../api/dashboardApi', () => ({
  dashboardApi: {
    getMetrics: vi.fn(),
  },
}));

describe('Página DashboardPage', () => {
  it('Renderiza visão completa de Técnico com os 3 cards e item de menu de patrimônio', async () => {
    (authApi.getMe as ReturnType<typeof vi.fn>).mockResolvedValue({
      id: 1,
      email: 'tecnico@empresa.com',
      role: 'tecnico',
      is_active: true,
    });
    (dashboardApi.getMetrics as ReturnType<typeof vi.fn>).mockResolvedValue({
      tickets_pending: 5,
      tickets_in_progress: 2,
      equipments_total: 10,
    });

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/dashboard']}>
          <Routes>
            <Route path="/dashboard" element={<DashboardPage />} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Tickets Pendentes')).toBeInTheDocument();
      expect(screen.getByText('Tickets em Andamento')).toBeInTheDocument();
      expect(screen.getByText('Equipamentos')).toBeInTheDocument();
    });

    // Abrir Menu Lateral (RN-01)
    const toggleBtn = screen.getByTestId('toggle-menu-btn');
    fireEvent.click(toggleBtn);

    await waitFor(() => {
      expect(screen.getByTestId('patrimonio-menu-item')).toBeInTheDocument();
    });
  });

  it('Renderiza visão limitada do Colaborador (sem card de equipamentos e sem menu de patrimônio)', async () => {
    (authApi.getMe as ReturnType<typeof vi.fn>).mockResolvedValue({
      id: 2,
      email: 'colaborador@empresa.com',
      role: 'colaborador',
      is_active: true,
    });
    (dashboardApi.getMetrics as ReturnType<typeof vi.fn>).mockResolvedValue({
      tickets_pending: 1,
      tickets_in_progress: 1,
      equipments_total: null,
    });

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/dashboard']}>
          <Routes>
            <Route path="/dashboard" element={<DashboardPage />} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Tickets Pendentes')).toBeInTheDocument();
      expect(screen.getByText('Tickets em Andamento')).toBeInTheDocument();
      expect(screen.queryByText('Equipamentos')).not.toBeInTheDocument();
    });

    // Abrir Menu Lateral
    const toggleBtn = screen.getByTestId('toggle-menu-btn');
    fireEvent.click(toggleBtn);

    await waitFor(() => {
      expect(screen.queryByTestId('patrimonio-menu-item')).not.toBeInTheDocument();
    });
  });

  it('Executa logout a partir do menu lateral e redireciona para login', async () => {
    (authApi.getMe as ReturnType<typeof vi.fn>).mockResolvedValue({
      id: 1,
      email: 'tecnico@empresa.com',
      role: 'tecnico',
      is_active: true,
    });
    (dashboardApi.getMetrics as ReturnType<typeof vi.fn>).mockResolvedValue({
      tickets_pending: 0,
      tickets_in_progress: 0,
      equipments_total: 0,
    });
    (authApi.logout as ReturnType<typeof vi.fn>).mockResolvedValue({ message: 'Logout realizado com sucesso.' });

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/dashboard']}>
          <Routes>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/login" element={<div>Tela de Login</div>} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('toggle-menu-btn')).toBeInTheDocument();
    });

    const toggleBtn = screen.getByTestId('toggle-menu-btn');
    fireEvent.click(toggleBtn);

    const logoutBtn = await screen.findByRole('button', { name: /encerrar sessão/i });
    fireEvent.click(logoutBtn);

    await waitFor(() => {
      expect(authApi.logout).toHaveBeenCalled();
      expect(screen.getByText('Tela de Login')).toBeInTheDocument();
    });
  });
});
