// frontend/src/services/chartService.ts
import apiClient from './apiClient';

interface SensusData {
  tanggal: string;
  bor: number;
}

interface PrediksiData {
  tanggal: string;
  bor: number;
}

interface ChartDataResponse {
  aktual: SensusData[];
  prediksi: PrediksiData[];
}

export const chartService = {
  // Ambil data BOR aktual 7 hari terakhir
  async getBorChartData(days: number = 7): Promise<ChartDataResponse> {
    try {
      // Ambil data aktual - use correct URL with trailing slash  
      const allSensus = await apiClient.get('/sensus/') as any[];
      
      // Ambil 7 hari terakhir
      const recentSensus = allSensus
        .slice(-days)
        .map((item: any) => ({
          tanggal: item.tanggal,
          bor: item.bor
        }));

      // Ambil data prediksi - use hari parameter instead of undefined
      const prediksiData = await apiClient.get('/prediksi/bor?hari=7') as any;

      return {
        aktual: recentSensus,
        prediksi: prediksiData.prediksi || []
      };
    } catch (error) {
      console.error('Error fetching chart data:', error);
      throw error;
    }
  },

  // Gabungkan data aktual dan prediksi untuk chart
  combineChartData(aktual: SensusData[], prediksi: PrediksiData[]) {
    interface ChartDataPoint {
      tanggal: string;
      bor_aktual?: number;
      bor_prediksi?: number;
      label: string;
      isPrediksi: boolean;
    }

    const chartData: ChartDataPoint[] = [];

    // Tambahkan data aktual
    aktual.forEach(item => {
      chartData.push({
        tanggal: item.tanggal,
        bor_aktual: item.bor,
        bor_prediksi: undefined,
        label: item.tanggal,
        isPrediksi: false
      });
    });

    // Tambahkan data prediksi
    prediksi.forEach(item => {
      chartData.push({
        tanggal: item.tanggal,
        bor_aktual: undefined,
        bor_prediksi: item.bor,
        label: item.tanggal,
        isPrediksi: true
      });
    });

    // Urutkan berdasarkan tanggal
    return chartData.sort((a, b) => new Date(a.tanggal).getTime() - new Date(b.tanggal).getTime());
  }
};
