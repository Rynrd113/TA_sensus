import apiClient from './apiClient';
import { 
  SensusCreate, 
  SensusResponse, 
  SensusFilter, 
  SensusStats 
} from '../types/Sensus';
import { ApiResponse } from '../types/Common';

export class SensusService {
  private baseUrl = '/sensus/'; // Add trailing slash

  // Get all sensus data with optional filters
  async getAllSensus(filters?: SensusFilter): Promise<ApiResponse<SensusResponse[]>> {
    const params = new URLSearchParams();
    
    if (filters?.tanggal_mulai) params.append('tanggal_mulai', filters.tanggal_mulai);
    if (filters?.tanggal_akhir) params.append('tanggal_akhir', filters.tanggal_akhir);
    if (filters?.bangsal_id) params.append('bangsal_id', filters.bangsal_id.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());
    if (filters?.offset) params.append('offset', filters.offset.toString());

    const queryString = params.toString();
    const url = queryString ? `${this.baseUrl}?${queryString}` : this.baseUrl;
    
    return apiClient.get<ApiResponse<SensusResponse[]>>(url);
  }

  // Get sensus by ID
  async getSensusById(id: number): Promise<ApiResponse<SensusResponse>> {
    return apiClient.get<ApiResponse<SensusResponse>>(`${this.baseUrl}/${id}`);
  }

  // Create new sensus data
  async createSensus(data: SensusCreate): Promise<ApiResponse<SensusResponse>> {
    return apiClient.post<ApiResponse<SensusResponse>>(this.baseUrl, data);
  }

  // Update sensus data
  async updateSensus(id: number, data: Partial<SensusCreate>): Promise<ApiResponse<SensusResponse>> {
    return apiClient.put<ApiResponse<SensusResponse>>(`${this.baseUrl}/${id}`, data);
  }

  // Delete sensus data
  async deleteSensus(id: number): Promise<ApiResponse<null>> {
    return apiClient.delete<ApiResponse<null>>(`${this.baseUrl}/${id}`);
  }

  // Get dashboard statistics
  async getDashboardStats(filters?: SensusFilter): Promise<ApiResponse<SensusStats>> {
    const params = new URLSearchParams();
    
    if (filters?.tanggal_mulai) params.append('tanggal_mulai', filters.tanggal_mulai);
    if (filters?.tanggal_akhir) params.append('tanggal_akhir', filters.tanggal_akhir);
    if (filters?.bangsal_id) params.append('bangsal_id', filters.bangsal_id.toString());

    const queryString = params.toString();
    const url = queryString ? `${this.baseUrl}/stats?${queryString}` : `${this.baseUrl}/stats`;
    
    return apiClient.get<ApiResponse<SensusStats>>(url);
  }

  // Get sensus data for charts
  async getChartData(filters?: SensusFilter): Promise<ApiResponse<any[]>> {
    const params = new URLSearchParams();
    
    if (filters?.tanggal_mulai) params.append('tanggal_mulai', filters.tanggal_mulai);
    if (filters?.tanggal_akhir) params.append('tanggal_akhir', filters.tanggal_akhir);
    if (filters?.bangsal_id) params.append('bangsal_id', filters.bangsal_id.toString());

    const queryString = params.toString();
    const url = queryString ? `${this.baseUrl}/chart?${queryString}` : `${this.baseUrl}/chart`;
    
    return apiClient.get<ApiResponse<any[]>>(url);
  }

  // Export sensus data
  async exportData(filters?: SensusFilter, format: 'csv' | 'excel' = 'csv'): Promise<Blob> {
    const params = new URLSearchParams();
    
    if (filters?.tanggal_mulai) params.append('tanggal_mulai', filters.tanggal_mulai);
    if (filters?.tanggal_akhir) params.append('tanggal_akhir', filters.tanggal_akhir);
    if (filters?.bangsal_id) params.append('bangsal_id', filters.bangsal_id.toString());
    params.append('format', format);

    const queryString = params.toString();
    const url = queryString ? `${this.baseUrl}/export?${queryString}` : `${this.baseUrl}/export`;
    
    const response = await apiClient.get(url, {
      responseType: 'blob'
    });
    
    return response as Blob;
  }
}

// Export singleton instance
export const sensusService = new SensusService();
export default sensusService;
