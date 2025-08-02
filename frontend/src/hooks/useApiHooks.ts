import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../services/apiClient';

// Dashboard data hook
export const useDashboard = (bulan: number, tahun: number) => {
  return useQuery({
    queryKey: ['dashboard', bulan, tahun],
    queryFn: async () => {
      const response = await apiClient.get(`/dashboard/stats?bulan=${bulan}&tahun=${tahun}`);
      return response;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (cacheTime renamed to gcTime in v5)
    retry: 2,
    refetchOnWindowFocus: false,
  });
};

// Sensus data hook
export const useSensusData = (filters?: any) => {
  return useQuery({
    queryKey: ['sensus', filters],
    queryFn: async () => {
      const params = new URLSearchParams(filters).toString();
      const response = await apiClient.get(`/sensus/?${params}`);
      return response;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });
};

// Prediksi data hook
export const usePrediksiData = (days: number = 7) => {
  return useQuery({
    queryKey: ['prediksi', days],
    queryFn: async () => {
      const response = await apiClient.get(`/prediksi/bor?days=${days}`);
      return response;
    },
    staleTime: 15 * 60 * 1000, // 15 minutes (prediksi tidak sering berubah)
    gcTime: 30 * 60 * 1000, // 30 minutes
    retry: 1,
  });
};

// Chart data hook
export const useChartData = (days: number = 7) => {
  return useQuery({
    queryKey: ['chart', days],
    queryFn: async () => {
      // Gabungkan data aktual dan prediksi
      const [sensusRes, prediksiRes] = await Promise.all([
        apiClient.get(`/sensus/?limit=${days}`),
        apiClient.get(`/prediksi/bor?days=${days}`)
      ]);
      
      return {
        aktual: (sensusRes as any)?.data || [],
        prediksi: (prediksiRes as any)?.prediksi || []
      };
    },
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
    retry: 2,
  });
};

// Mutation for creating sensus data
export const useCreateSensus = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: any) => {
      return await apiClient.post('/sensus/', data);
    },
    onSuccess: () => {
      // Invalidate and refetch sensus data
      queryClient.invalidateQueries({ queryKey: ['sensus'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard'] });
      queryClient.invalidateQueries({ queryKey: ['chart'] });
    },
  });
};

// Export error handler
export const handleApiError = (error: any) => {
  if (error?.response?.status === 404) {
    return 'Data tidak ditemukan';
  }
  if (error?.response?.status >= 500) {
    return 'Terjadi kesalahan server';
  }
  if (error?.message?.includes('Network Error')) {
    return 'Koneksi terputus';
  }
  return error?.response?.data?.message || 'Terjadi kesalahan';
};
