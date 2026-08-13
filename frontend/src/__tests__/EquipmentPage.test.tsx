import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from '../context/AuthContext';
import { EquipmentListPage } from '../pages/EquipmentListPage';
import { EquipmentDetailPage } from '../pages/EquipmentDetailPage';
import { authApi } from '../api/authApi';
import { equipmentApi } from '../api/equipmentApi';

vi.mock('../api/authApi', () => ({
  authApi: {
    getMe: vi.fn(),
    login: vi.fn(),
    refresh: vi.fn(),
    logout: vi.fn(),
  },
}));

vi.mock('../api/equipmentApi', () => ({
  equipmentApi: {
    getEquipments: vi.fn(),
    getEquipmentDetail: vi.fn(),
    createEquipment: vi.fn(),
    updateEquipment: vi.fn(),
    getTags: vi.fn(),
    createTag: vi.fn(),
    recordMovement: vi.fn(),
    recordMaintenance: vi.fn(),
    updateMaintenance: vi.fn(),
    deleteMaintenance: vi.fn(),
  },
}));

describe('Páginas e Componentes de Equipamentos (Frontend)', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('Renderiza EquipmentListPage com filtros múltiplos, busca e navegação para o Dashboard', async () => {
    (authApi.getMe as ReturnType<typeof vi.fn>).mockResolvedValue({
      id: 1,
      email: 'tecnico@empresa.com',
      role: 'tecnico',
      is_active: true,
    });
    (equipmentApi.getTags as ReturnType<typeof vi.fn>).mockResolvedValue([
      { id: 1, category: 'tipo', name: 'Notebook' },
      { id: 2, category: 'localizacao', name: 'TI' },
      { id: 3, category: 'situacao', name: 'Em uso' },
    ]);
    (equipmentApi.getEquipments as ReturnType<typeof vi.fn>).mockResolvedValue({
      items: [
        {
          id: 1,
          serial_number: 'SN-TEST-001',
          patrimony_number: 'PAT-101',
          description: 'Dell OptiPlex 7090',
          equipment_type: 'Desktop',
          location: 'TI',
          status: 'Em uso',
          movements: [],
          maintenances: [],
          created_at: '2026-08-13T00:00:00Z',
        },
      ],
      total: 1,
      page: 1,
      limit: 25,
      pages: 1,
    });

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/equipamentos']}>
          <Routes>
            <Route path="/equipamentos" element={<EquipmentListPage />} />
            <Route path="/dashboard" element={<div>Tela Dashboard</div>} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Equipamentos')).toBeInTheDocument();
      expect(screen.getByText('Dell OptiPlex 7090')).toBeInTheDocument();
      expect(screen.getByText('PAT-101')).toBeInTheDocument();
    });

    // Testar botão Voltar ao Dashboard (RN-EQ-06)
    const backDashBtn = screen.getByTestId('back-to-dashboard-btn');
    fireEvent.click(backDashBtn);

    await waitFor(() => {
      expect(screen.getByText('Tela Dashboard')).toBeInTheDocument();
    });
  });

  it('Renderiza EquipmentDetailPage em tela única, com botão Voltar para Equipamentos, modo de edição em lote e histórico', async () => {
    (authApi.getMe as ReturnType<typeof vi.fn>).mockResolvedValue({
      id: 1,
      email: 'tecnico@empresa.com',
      role: 'tecnico',
      is_active: true,
    });
    (equipmentApi.getTags as ReturnType<typeof vi.fn>).mockResolvedValue([
      { id: 1, category: 'tipo', name: 'Notebook' },
      { id: 2, category: 'localizacao', name: 'TI' },
      { id: 3, category: 'situacao', name: 'Em uso' },
    ]);
    (equipmentApi.getEquipmentDetail as ReturnType<typeof vi.fn>).mockResolvedValue({
      id: 1,
      serial_number: 'SN-DET-01',
      patrimony_number: 'PAT-DET-01',
      description: 'ThinkPad X1 Carbon',
      equipment_type: 'Notebook',
      location: 'TI',
      status: 'Em uso',
      windows_key: 'XXXXX-YYYYY-ZZZZZ',
      notes: 'Nota técnica',
      movements: [
        {
          id: 1,
          equipment_id: 1,
          origin_location: 'Estoque',
          destination_location: 'TI',
          movement_date: '2026-08-13T00:00:00Z',
          created_at: '2026-08-13T00:00:00Z',
        },
      ],
      maintenances: [
        {
          id: 1,
          equipment_id: 1,
          maintenance_date: '2026-08-13T00:00:00Z',
          maintenance_type: 'Manutenção',
          description: 'Limpeza de pasta térmica',
          created_at: '2026-08-13T00:00:00Z',
        },
      ],
      created_at: '2026-08-13T00:00:00Z',
    });

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/equipamentos/1']}>
          <Routes>
            <Route path="/equipamentos/:id" element={<EquipmentDetailPage />} />
            <Route path="/equipamentos" element={<div>Listagem de Equipamentos</div>} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'ThinkPad X1 Carbon' })).toBeInTheDocument();
      expect(screen.getByText('•••••••••••••••••••••••••')).toBeInTheDocument();
      expect(screen.getByText('Limpeza de pasta térmica')).toBeInTheDocument();
    });

    // Testar modo de edição em lote (RN-EQ-08)
    const editBtn = screen.getByTestId('edit-equipment-btn');
    fireEvent.click(editBtn);

    await waitFor(() => {
      expect(screen.getByText('Salvar alterações')).toBeInTheDocument();
      expect(screen.getByText('Cancelar')).toBeInTheDocument();
    });

    // Cancelar edição
    const cancelBtn = screen.getByText('Cancelar');
    fireEvent.click(cancelBtn);

    await waitFor(() => {
      expect(screen.getByTestId('edit-equipment-btn')).toBeInTheDocument();
    });

    // Testar botão Voltar para Equipamentos (RN-EQ-06 / RN-20)
    const backEqBtn = screen.getByTestId('back-to-equipments-btn');
    fireEvent.click(backEqBtn);

    await waitFor(() => {
      expect(screen.getByText('Listagem de Equipamentos')).toBeInTheDocument();
    });
  });
});
