import BaseService, { handleServiceError } from './baseService';
import apiClient from './apiClient';
import { 
  SensusCreate, 
  SensusResponse, 
  SensusFilter, 
  SensusStats 
} from '../types/Sensus';
import { ApiResponse } from '../types/Common';

export class SensusService extends BaseService<SensusResponse, SensusCreate> {
  constructor() {
    super('/sensus');
  }

  // Override getAll to support custom filters
  async getAllSensus(filters?: SensusFilter): Promise<ApiResponse<SensusResponse[]>> {
    try {
      const params: Record<string, any> = {};
      
      if (filters?.tanggal_mulai) params.tanggal_mulai = filters.tanggal_mulai;
      if (filters?.tanggal_akhir) params.tanggal_akhir = filters.tanggal_akhir;
      if (filters?.bangsal_id) params.bangsal_id = filters.bangsal_id.toString();
      if (filters?.limit) params.limit = filters.limit.toString();
      if (filters?.offset) params.offset = filters.offset.toString();

      return this.getAll(params);
    } catch (error) {
      return handleServiceError(error, 'Get sensus data');
    }
  }

  // Override base methods untuk custom behavior
  async getSensusById(id: number): Promise<ApiResponse<SensusResponse>> {
    try {
      return this.getById(id);
    } catch (error) {
      return handleServiceError(error, 'Get sensus by ID');
    }
  }

  async createSensus(data: SensusCreate): Promise<ApiResponse<SensusResponse>> {
    try {
      return this.create(data);
    } catch (error) {
      return handleServiceError(error, 'Create sensus');
    }
  }

  async updateSensus(id: number, data: Partial<SensusCreate>): Promise<ApiResponse<SensusResponse>> {
    try {
      return this.update(id, data);
    } catch (error) {
      return handleServiceError(error, 'Update sensus');
    }
  }

  async deleteSensus(id: number): Promise<ApiResponse<null>> {
    try {
      return this.delete(id);
    } catch (error) {
      return handleServiceError(error, 'Delete sensus');
    }
  }

  // Custom methods specific to sensus
  async getDashboardStats(filters?: SensusFilter): Promise<ApiResponse<SensusStats>> {
    try {
      const params: Record<string, any> = {};
      
      if (filters?.tanggal_mulai) params.tanggal_mulai = filters.tanggal_mulai;
      if (filters?.tanggal_akhir) params.tanggal_akhir = filters.tanggal_akhir;
      if (filters?.bangsal_id) params.bangsal_id = filters.bangsal_id.toString();

      const queryString = this.buildQueryString(params);
      const url = `/dashboard/stats${queryString}`;
      
      // Use direct apiClient for custom endpoints
      return apiClient.get<ApiResponse<SensusStats>>(url);
    } catch (error) {
      return handleServiceError(error, 'Get dashboard stats');
    }
  }

  async getChartData(filters?: SensusFilter): Promise<ApiResponse<any[]>> {
    try {
      const params: Record<string, any> = {};
      
      if (filters?.tanggal_mulai) params.tanggal_mulai = filters.tanggal_mulai;
      if (filters?.tanggal_akhir) params.tanggal_akhir = filters.tanggal_akhir;
      if (filters?.bangsal_id) params.bangsal_id = filters.bangsal_id.toString();

      const queryString = this.buildQueryString(params);
      const url = `${this.baseUrl}/chart${queryString}`;
      
      // Use direct apiClient for custom endpoints  
      return apiClient.get<ApiResponse<any[]>>(url);
    } catch (error) {
      return handleServiceError(error, 'Get chart data');
    }
  }

  // Export dengan custom filters
  async exportSensusData(filters?: SensusFilter, format: 'csv' | 'excel' = 'csv'): Promise<Blob> {
    try {
      const params: Record<string, any> = {};
      
      if (filters?.tanggal_mulai) params.tanggal_mulai = filters.tanggal_mulai;
      if (filters?.tanggal_akhir) params.tanggal_akhir = filters.tanggal_akhir;
      if (filters?.bangsal_id) params.bangsal_id = filters.bangsal_id.toString();

      return this.exportData('/export', params, format);
    } catch (error) {
      handleServiceError(error, 'Export sensus data');
      throw error;
    }
  }
}

// Export singleton instance
export const sensusService = new SensusService();
export default sensusService;
