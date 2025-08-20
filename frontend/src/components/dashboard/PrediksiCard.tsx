// frontend/src/components/dashboard/PrediksiCard.tsx
import { useEffect, useState } from "react";
import { RefreshIcon, ExclamationIcon } from "../icons/index";

interface PrediksiItem {
  tanggal: string;
  bor: number;
}

interface PrediksiData {
  prediksi: PrediksiItem[];
  rekomendasi: string;
  status: string;
  error?: string;
}

export default function PrediksiCard() {
  const [prediksiData, setPrediksiData] = useState<PrediksiData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPrediksi = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch('http://localhost:8000/api/v1/prediksi/bor?hari=3');
      if (!response.ok) {
        throw new Error('Failed to fetch prediction data');
      }
      const data = await response.json();
      
      if (data.error) {
        setError(data.error);
        setPrediksiData(null);
      } else {
        setPrediksiData(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setPrediksiData(null);
    } finally {
      setLoading(false);
    }
  };

  const retrainModel = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/prediksi/retrain', {
        method: 'POST',
      });
      const result = await response.json();
      
      if (result.status === 'success') {
        // Refresh prediksi setelah retrain
        await fetchPrediksi();
      } else {
        setError(result.error || 'Gagal melatih ulang model');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error retraining model');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrediksi();
  }, []); // Empty dependency array - only fetch once on mount

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('id-ID', {
      weekday: 'short',
      day: 'numeric',
      month: 'short'
    });
  };

  const getBorColorClass = (bor: number) => {
    if (bor >= 90) return 'text-red-600 bg-red-50';
    if (bor >= 80) return 'text-yellow-600 bg-yellow-50';
    return 'text-green-600 bg-green-50';
  };

  const getRecommendationIcon = (bor: number) => {
    if (bor >= 90) return <ExclamationIcon className="w-5 h-5 text-red-500" />;
    if (bor >= 80) return <ExclamationIcon className="w-5 h-5 text-yellow-500" />;
    return (
      <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
      </svg>
    );
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
            <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900">
            Prediksi BOR 3 Hari ke Depan
          </h3>
        </div>
        
        <div className="flex space-x-2">
          <button
            onClick={fetchPrediksi}
            disabled={loading}
            className="p-2 text-gray-500 hover:text-gray-700 disabled:opacity-50"
            title="Refresh Prediksi"
          >
            <RefreshIcon className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          
          <button
            onClick={retrainModel}
            disabled={loading}
            className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 disabled:opacity-50"
            title="Latih Ulang Model"
          >
            {loading ? 'Loading...' : 'Retrain'}
          </button>
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
          <div className="flex items-center">
            <ExclamationIcon className="w-5 h-5 text-red-500 mr-2" />
            <p className="text-sm text-red-700">{error}</p>
          </div>
          <p className="text-xs text-red-600 mt-1">
            Pastikan model sudah dilatih dan data minimal 10 hari tersedia.
          </p>
        </div>
      )}

      {prediksiData && !loading && (
        <div className="space-y-4">
          {/* Prediksi List */}
          <div className="space-y-2">
            {prediksiData.prediksi.map((item, index) => {
              const maxBor = Math.max(...prediksiData.prediksi.map(p => p.bor));
              return (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    <div className="text-sm font-medium text-gray-900">
                      {formatDate(item.tanggal)}
                    </div>
                    {item.bor === maxBor && getRecommendationIcon(maxBor)}
                  </div>
                  
                  <div className={`px-3 py-1 rounded-full text-sm font-medium ${getBorColorClass(item.bor)}`}>
                    {item.bor}% BOR
                  </div>
                </div>
              );
            })}
          </div>

          {/* Rekomendasi */}
          {prediksiData.rekomendasi && (
            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start space-x-2">
                <svg className="w-5 h-5 text-blue-500 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                <div>
                  <p className="text-sm font-medium text-blue-900">Rekomendasi</p>
                  <p className="text-sm text-blue-700 mt-1">{prediksiData.rekomendasi}</p>
                </div>
              </div>
            </div>
          )}

          {/* Info Model */}
          <div className="text-xs text-gray-500 border-t pt-3">
            Model: SARIMA | Dengan komponen seasonal untuk akurasi prediksi yang lebih baik
          </div>
        </div>
      )}
    </div>
  );
}
