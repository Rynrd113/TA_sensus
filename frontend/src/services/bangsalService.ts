import apiClient from './apiClient';
import { Bangsal, ApiResponse } from '../types/Common';

export class BangsalService {
  private baseUrl = '/bangsal';

  // Get all bangsal
  async getAllBangsal(): Promise<ApiResponse<Bangsal[]>> {
    return apiClient.get<ApiResponse<Bangsal[]>>(this.baseUrl);
  }

  // Get bangsal by ID
  async getBangsalById(id: number): Promise<ApiResponse<Bangsal>> {
    return apiClient.get<ApiResponse<Bangsal>>(`${this.baseUrl}/${id}`);
  }
}

export const bangsalService = new BangsalService();
export default bangsalService;
