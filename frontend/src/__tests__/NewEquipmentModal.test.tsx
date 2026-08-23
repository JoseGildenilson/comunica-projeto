import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { NewEquipmentModal } from '../components/NewEquipmentModal';
import { equipmentApi } from '../api/equipmentApi';
import { EquipmentTag } from '../types/equipment';

vi.mock('../api/equipmentApi', () => ({
  equipmentApi: {
    getTags: vi.fn(),
    createTag: vi.fn(),
    createEquipment: vi.fn(),
  },
}));

const mockTags: EquipmentTag[] = [
  { id: 1, category: 'tipo', name: 'Desktop', created_at: '2026-08-01T00:00:00Z' },
  { id: 2, category: 'localizacao', name: 'TI', created_at: '2026-08-01T00:00:00Z' },
  { id: 3, category: 'situacao', name: 'Em uso', created_at: '2026-08-01T00:00:00Z' },
];

describe('Componente NewEquipmentModal', () => {
  const onClose = vi.fn();
  const onSuccess = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(equipmentApi.getTags).mockResolvedValue([...mockTags]);
  });

  it('Não renderiza quando isOpen é false', () => {
    const { container } = render(
      <NewEquipmentModal isOpen={false} onClose={onClose} onSuccess={onSuccess} />
    );
    expect(container.firstChild).toBeNull();
  });

  it('Renderiza botões de criar tag inline sem duplicar + e permite cadastro rápido', async () => {
    vi.mocked(equipmentApi.createTag).mockResolvedValue({
      id: 4,
      category: 'tipo',
      name: 'Servidor',
      created_at: '2026-08-23T00:00:00Z',
    });

    render(
      <NewEquipmentModal isOpen={true} onClose={onClose} onSuccess={onSuccess} />
    );

    await waitFor(() => {
      expect(screen.getByText('Novo Equipamento')).toBeInTheDocument();
    });

    const createTipoBtn = screen.getByTestId('inline-create-tipo-btn');
    const createLocBtn = screen.getByTestId('inline-create-localizacao-btn');
    const createSitBtn = screen.getByTestId('inline-create-situacao-btn');

    expect(createTipoBtn.textContent).toContain('Criar tipo');
    expect(createTipoBtn.textContent).not.toContain('++');
    expect(createLocBtn.textContent).toContain('Criar local');
    expect(createLocBtn.textContent).not.toContain('++');
    expect(createSitBtn.textContent).toContain('Criar situação');
    expect(createSitBtn.textContent).not.toContain('++');

    // Clicar para criar tipo inline
    fireEvent.click(createTipoBtn);

    const input = screen.getByPlaceholderText('Novo tipo');
    expect(input).toBeInTheDocument();

    fireEvent.change(input, { target: { value: 'Servidor' } });
    const saveBtn = screen.getByTitle('Salvar Tipo');
    fireEvent.click(saveBtn);

    await waitFor(() => {
      expect(equipmentApi.createTag).toHaveBeenCalledWith('tipo', 'Servidor');
    });
  });
});
