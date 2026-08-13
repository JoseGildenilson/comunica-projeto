import axios from 'axios';
import {
  Equipment,
  EquipmentCreatePayload,
  EquipmentFilterParams,
  EquipmentListResponse,
  EquipmentMaintenance,
  EquipmentMovement,
  EquipmentTag,
} from '../types/equipment';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export const equipmentHttpClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/equipments`,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const equipmentApi = {
  getEquipments: async (params?: EquipmentFilterParams): Promise<EquipmentListResponse> => {
    const response = await equipmentHttpClient.get<EquipmentListResponse>('', {
      params,
      paramsSerializer: {
        indexes: null, // serializa arrays como ?type=Notebook&type=Desktop
      },
    });
    return response.data;
  },

  getEquipmentDetail: async (id: number): Promise<Equipment> => {
    const response = await equipmentHttpClient.get<Equipment>(`/${id}`);
    return response.data;
  },

  createEquipment: async (payload: EquipmentCreatePayload): Promise<Equipment> => {
    const response = await equipmentHttpClient.post<Equipment>('', payload);
    return response.data;
  },

  updateEquipment: async (id: number, payload: Partial<EquipmentCreatePayload>): Promise<Equipment> => {
    const response = await equipmentHttpClient.put<Equipment>(`/${id}`, payload);
    return response.data;
  },

  getTags: async (category?: string): Promise<EquipmentTag[]> => {
    const response = await equipmentHttpClient.get<EquipmentTag[]>('/tags', {
      params: category ? { category } : undefined,
    });
    return response.data;
  },

  createTag: async (category: string, name: string): Promise<EquipmentTag> => {
    const response = await equipmentHttpClient.post<EquipmentTag>('/tags', { category, name });
    return response.data;
  },

  recordMovement: async (
    equipmentId: number,
    payload: { origin_location: string; destination_location: string; movement_date: string; notes?: string }
  ): Promise<EquipmentMovement> => {
    const response = await equipmentHttpClient.post<EquipmentMovement>(`/${equipmentId}/movements`, payload);
    return response.data;
  },

  recordMaintenance: async (
    equipmentId: number,
    payload: { maintenance_date: string; maintenance_type?: string; description: string; notes?: string }
  ): Promise<EquipmentMaintenance> => {
    const response = await equipmentHttpClient.post<EquipmentMaintenance>(`/${equipmentId}/maintenances`, payload);
    return response.data;
  },

  updateMaintenance: async (
    equipmentId: number,
    maintenanceId: number,
    payload: { maintenance_date?: string; maintenance_type?: string; description?: string; notes?: string }
  ): Promise<EquipmentMaintenance> => {
    const response = await equipmentHttpClient.put<EquipmentMaintenance>(
      `/${equipmentId}/maintenances/${maintenanceId}`,
      payload
    );
    return response.data;
  },

  deleteMaintenance: async (equipmentId: number, maintenanceId: number): Promise<{ message: string }> => {
    const response = await equipmentHttpClient.delete<{ message: string }>(
      `/${equipmentId}/maintenances/${maintenanceId}`
    );
    return response.data;
  },
};
