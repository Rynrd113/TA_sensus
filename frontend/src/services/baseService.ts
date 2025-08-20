// frontend/src/services/baseService.ts
/**
 * Base Service Class
 * Implementasi DRY untuk semua service di frontend
 * Menerapkan prinsip inheritance dan reusable code
 */

import { ApiResponse } from '../types/Common';
import apiClient from './apiClient';

export abstract class BaseService<T, CreateType = Partial<T>, UpdateType = Partial<T>> {
  protected baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.startsWith('/') ? baseUrl : `/${baseUrl}`;
  }

  // Standard CRUD operations - DRY implementation
  async getAll(params?: Record<string, any>): Promise<ApiResponse<T[]>> {
    const queryString = params ? 
      `?${new URLSearchParams(params).toString()}` : '';
    return apiClient.get<ApiResponse<T[]>>(`${this.baseUrl}${queryString}`);
  }

  async getById(id: number | string): Promise<ApiResponse<T>> {
    return apiClient.get<ApiResponse<T>>(`${this.baseUrl}/${id}`);
  }

  async create(data: CreateType): Promise<ApiResponse<T>> {
    return apiClient.post<ApiResponse<T>>(this.baseUrl, data);
  }

  async update(id: number | string, data: UpdateType): Promise<ApiResponse<T>> {
    return apiClient.put<ApiResponse<T>>(`${this.baseUrl}/${id}`, data);
  }

  async delete(id: number | string): Promise<ApiResponse<null>> {
    return apiClient.delete<ApiResponse<null>>(`${this.baseUrl}/${id}`);
  }

  // Common utility methods
  protected buildQueryString(params?: Record<string, any>): string {
    if (!params) return '';
    const searchParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        searchParams.append(key, value.toString());
      }
    });
    
    return searchParams.toString() ? `?${searchParams.toString()}` : '';
  }

  protected async exportData(
    endpoint: string, 
    filters?: Record<string, any>, 
    format: 'csv' | 'excel' = 'csv'
  ): Promise<Blob> {
    const params = { ...filters, format };
    const queryString = this.buildQueryString(params);
    const url = `${endpoint}${queryString}`;
    
    return apiClient.get(url, {
      responseType: 'blob'
    }) as Promise<Blob>;
  }
}

// Error handler yang dapat digunakan ulang
export const handleServiceError = (error: any, context: string = 'Operation') => {
  console.error(`${context} failed:`, error);
  
  if (error?.response?.status === 404) {
    throw new Error('Data tidak ditemukan');
  }
  if (error?.response?.status === 400) {
    throw new Error(error?.response?.data?.message || 'Data tidak valid');
  }
  if (error?.response?.status >= 500) {
    throw new Error('Terjadi kesalahan server');
  }
  if (error?.message?.includes('Network Error')) {
    throw new Error('Koneksi terputus');
  }
  
  throw new Error(error?.response?.data?.message || `${context} gagal`);
};

export default BaseService;
