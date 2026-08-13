export interface EquipmentMovement {
  id: number;
  equipment_id: number;
  origin_location: string;
  destination_location: string;
  movement_date: string;
  notes?: string | null;
  created_at: string;
}

export interface EquipmentMaintenance {
  id: number;
  equipment_id: number;
  maintenance_date: string;
  maintenance_type: string;
  description: string;
  notes?: string | null;
  created_at: string;
}

export interface EquipmentTag {
  id: number;
  category: 'tipo' | 'localizacao' | 'situacao' | string;
  name: string;
  created_at: string;
}

export interface Equipment {
  id: number;
  serial_number: string;
  patrimony_number?: string | null;
  hostname?: string | null;
  description: string;
  brand?: string | null;
  product_number?: string | null;
  equipment_type: string;
  location: string;
  status: string;
  windows_key?: string | null;
  last_maintenance_at?: string | null;
  notes?: string | null;
  created_at: string;
  movements: EquipmentMovement[];
  maintenances: EquipmentMaintenance[];
}

export interface EquipmentCreatePayload {
  serial_number: string;
  patrimony_number?: string | null;
  hostname?: string | null;
  description: string;
  brand?: string | null;
  product_number?: string | null;
  equipment_type: string;
  location: string;
  status: string;
  windows_key?: string | null;
  last_maintenance_at?: string | null;
  notes?: string | null;
}

export interface EquipmentListResponse {
  items: Equipment[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface EquipmentFilterParams {
  page?: number;
  limit?: number;
  type?: string | string[];
  location?: string | string[];
  status?: string | string[];
  patrimony_number?: string | string[];
  serial_number?: string | string[];
  product_number?: string | string[];
  search?: string;
  sort_by?: string;
  sort_dir?: 'asc' | 'desc';
}
