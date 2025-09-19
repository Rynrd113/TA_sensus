import apiClient from './apiClient';
import { Bangsal, KamarBangsal, BangsalStats, BangsalFilter, ApiResponse } from '../types/Common';

export class BangsalService {
  private baseUrl = '/bangsal';

  // Core CRUD Operations
  async getAllBangsal(filter?: BangsalFilter): Promise<ApiResponse<Bangsal[]>> {
    const params = new URLSearchParams();
    if (filter?.departemen) params.append('departemen', filter.departemen);
    if (filter?.jenis_bangsal) params.append('jenis_bangsal', filter.jenis_bangsal);
    if (filter?.lantai !== undefined) params.append('lantai', filter.lantai.toString());
    if (filter?.status_operasional) params.append('status_operasional', filter.status_operasional);
    if (filter?.is_emergency_ready !== undefined) params.append('is_emergency_ready', filter.is_emergency_ready.toString());
    if (filter?.min_capacity) params.append('min_capacity', filter.min_capacity.toString());
    if (filter?.max_capacity) params.append('max_capacity', filter.max_capacity.toString());
    
    const queryString = params.toString() ? `?${params.toString()}` : '';
    return apiClient.get<ApiResponse<Bangsal[]>>(`${this.baseUrl}/${queryString}`);
  }

  async getBangsalById(id: number): Promise<ApiResponse<Bangsal>> {
    return apiClient.get<ApiResponse<Bangsal>>(`${this.baseUrl}/${id}`);
  }

  async createBangsal(data: Partial<Bangsal>): Promise<ApiResponse<Bangsal>> {
    return apiClient.post<ApiResponse<Bangsal>>(this.baseUrl, data);
  }

  async updateBangsal(id: number, data: Partial<Bangsal>): Promise<ApiResponse<Bangsal>> {
    return apiClient.put<ApiResponse<Bangsal>>(`${this.baseUrl}/${id}`, data);
  }

  async deleteBangsal(id: number): Promise<ApiResponse<any>> {
    return apiClient.delete<ApiResponse<any>>(`${this.baseUrl}/${id}`);
  }

  // Statistics and Analytics
  async getBangsalStatistics(): Promise<ApiResponse<BangsalStats>> {
    return apiClient.get<ApiResponse<BangsalStats>>(`${this.baseUrl}/statistics`);
  }

  async getBangsalSummary(): Promise<ApiResponse<any[]>> {
    return apiClient.get<ApiResponse<any[]>>(`${this.baseUrl}/summary`);
  }

  // Specialized Queries
  async getEmergencyReadyBangsal(): Promise<ApiResponse<Bangsal[]>> {
    return apiClient.get<ApiResponse<Bangsal[]>>(`${this.baseUrl}/emergency`);
  }

  async getBangsalByDepartment(department: string): Promise<ApiResponse<Bangsal[]>> {
    return apiClient.get<ApiResponse<Bangsal[]>>(`${this.baseUrl}/by-department?department=${encodeURIComponent(department)}`);
  }

  async getBangsalByFloor(floor: number): Promise<ApiResponse<Bangsal[]>> {
    return apiClient.get<ApiResponse<Bangsal[]>>(`${this.baseUrl}/by-floor?floor=${floor}`);
  }

  async getBangsalByType(type: string): Promise<ApiResponse<Bangsal[]>> {
    return apiClient.get<ApiResponse<Bangsal[]>>(`${this.baseUrl}/by-type?type=${encodeURIComponent(type)}`);
  }

  async getAvailableBangsal(): Promise<ApiResponse<Bangsal[]>> {
    return apiClient.get<ApiResponse<Bangsal[]>>(`${this.baseUrl}/available`);
  }

  async searchBangsal(query: string): Promise<ApiResponse<Bangsal[]>> {
    return apiClient.get<ApiResponse<Bangsal[]>>(`${this.baseUrl}/search?q=${encodeURIComponent(query)}`);
  }

  // Room Management
  async getBangsalRooms(bangsalId: number): Promise<ApiResponse<KamarBangsal[]>> {
    return apiClient.get<ApiResponse<KamarBangsal[]>>(`${this.baseUrl}/${bangsalId}/rooms`);
  }

  async addRoom(bangsalId: number, roomData: Partial<KamarBangsal>): Promise<ApiResponse<KamarBangsal>> {
    return apiClient.post<ApiResponse<KamarBangsal>>(`${this.baseUrl}/${bangsalId}/rooms`, roomData);
  }

  async updateRoom(bangsalId: number, roomId: number, roomData: Partial<KamarBangsal>): Promise<ApiResponse<KamarBangsal>> {
    return apiClient.put<ApiResponse<KamarBangsal>>(`${this.baseUrl}/${bangsalId}/rooms/${roomId}`, roomData);
  }

  async deleteRoom(bangsalId: number, roomId: number): Promise<ApiResponse<any>> {
    return apiClient.delete<ApiResponse<any>>(`${this.baseUrl}/${bangsalId}/rooms/${roomId}`);
  }

  // Capacity Management
  async updateCapacity(bangsalId: number, capacityData: { kapasitas_total: number }): Promise<ApiResponse<Bangsal>> {
    return apiClient.put<ApiResponse<Bangsal>>(`${this.baseUrl}/${bangsalId}/capacity`, capacityData);
  }

  async syncCapacityFromRooms(bangsalId: number): Promise<ApiResponse<Bangsal>> {
    return apiClient.post<ApiResponse<Bangsal>>(`${this.baseUrl}/${bangsalId}/sync-capacity`, {});
  }

  // Validation
  async validateBangsal(bangsalId: number): Promise<ApiResponse<any>> {
    return apiClient.get<ApiResponse<any>>(`${this.baseUrl}/${bangsalId}/validate`);
  }
}

export const bangsalService = new BangsalService();
export default bangsalService;
