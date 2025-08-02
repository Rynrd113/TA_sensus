// frontend/src/services/exportService.ts
import apiClient from './apiClient';

export const exportService = {
  // Export data bulan tertentu ke Excel
  async exportToExcel(bulan?: number, tahun?: number): Promise<Blob> {
    try {
      const params = new URLSearchParams();
      if (bulan) params.append('bulan', bulan.toString());
      if (tahun) params.append('tahun', tahun.toString());

      const response = await apiClient.get(
        `/export/excel?${params.toString()}`,
        {
          responseType: 'blob',
          headers: {
            'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
          }
        }
      );

      return response as Blob;
    } catch (error) {
      console.error('Error exporting to Excel:', error);
      throw error;
    }
  },

  // Export semua data ke Excel
  async exportAllToExcel(): Promise<Blob> {
    try {
      const response = await apiClient.get(
        `/export/excel/all`,
        {
          responseType: 'blob',
          headers: {
            'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
          }
        }
      );

      return response as Blob;
    } catch (error) {
      console.error('Error exporting all data to Excel:', error);
      throw error;
    }
  },

  // Helper function untuk download file
  downloadBlob(blob: Blob, filename: string) {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }
};
