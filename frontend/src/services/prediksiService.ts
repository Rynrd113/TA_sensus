import apiClient from './apiClient';
import { 
  PrediksiRequest, 
  PrediksiResponse, 
  PrediksiDashboard 
} from '../types/Prediksi';
import { ApiResponse } from '../types/Common';

export class PrediksiService {
  private baseUrl = '/prediksi';

  // Get BOR prediction
  async getPrediksi(request: PrediksiRequest): Promise<ApiResponse<PrediksiResponse>> {
    return apiClient.post<ApiResponse<PrediksiResponse>>(this.baseUrl, request);
  }

  // Get BOR prediction for specific days
  async getBORPrediksi(days: number = 7, bangsal_id?: number): Promise<ApiResponse<PrediksiResponse>> {
    const request: PrediksiRequest = {
      days,
      indikator: 'bor',
      bangsal_id
    };
    return this.getPrediksi(request);
  }

  // Get ALOS prediction
  async getALOSPrediksi(days: number = 7, bangsal_id?: number): Promise<ApiResponse<PrediksiResponse>> {
    const request: PrediksiRequest = {
      days,
      indikator: 'alos',
      bangsal_id
    };
    return this.getPrediksi(request);
  }

  // Get dashboard predictions (ringkasan untuk dashboard)
  async getDashboardPrediksi(bangsal_id?: number): Promise<ApiResponse<PrediksiDashboard>> {
    const params = new URLSearchParams();
    if (bangsal_id) params.append('bangsal_id', bangsal_id.toString());
    
    const queryString = params.toString();
    const url = queryString ? `${this.baseUrl}/dashboard?${queryString}` : `${this.baseUrl}/dashboard`;
    
    return apiClient.get<ApiResponse<PrediksiDashboard>>(url);
  }

  // Get model accuracy info
  async getModelAccuracy(): Promise<ApiResponse<any>> {
    return apiClient.get<ApiResponse<any>>(`${this.baseUrl}/model/accuracy`);
  }

  // Retrain model (jika diperlukan)
  async retrainModel(): Promise<ApiResponse<any>> {
    return apiClient.post<ApiResponse<any>>(`${this.baseUrl}/model/retrain`);
  }
}

// Export singleton instance
export const prediksiService = new PrediksiService();
export default prediksiService;
