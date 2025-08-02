// frontend/src/components/dashboard/ExportCard.tsx
import { useState } from 'react';

export default function ExportCard() {
  const [loading, setLoading] = useState<string | null>(null);
  const [bulan, setBulan] = useState(new Date().getMonth() + 1);
  const [tahun, setTahun] = useState(new Date().getFullYear());

  const handleExport = async (format: 'excel' | 'excel-prediksi' | 'csv') => {
    try {
      setLoading(format);
      
      const url = `http://localhost:8000/api/v1/export/${format}?bulan=${bulan}&tahun=${tahun}`;
      
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('Failed to export data');
      }

      // Download file
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      
      // Get filename from response headers
      const contentDisposition = response.headers.get('content-disposition');
      let filename = `sensus_${bulan}_${tahun}`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename=(.+)/);
        if (filenameMatch) {
          filename = filenameMatch[1].replace(/"/g, '');
        }
      }
      
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
      
    } catch (error) {
      console.error('Export error:', error);
      alert('Gagal mengexport data. Pastikan ada data untuk periode tersebut.');
    } finally {
      setLoading(null);
    }
  };

  const isLoading = (format: string) => loading === format;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
            <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900">
            Export Laporan
          </h3>
        </div>
      </div>

      {/* Period Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Periode Export
        </label>
        <div className="flex gap-2">
          <select 
            value={bulan} 
            onChange={(e) => setBulan(Number(e.target.value))}
            className="border border-gray-300 rounded px-3 py-2 text-sm flex-1"
          >
            {Array.from({ length: 12 }, (_, i) => (
              <option key={i + 1} value={i + 1}>
                {new Date(2025, i).toLocaleString('id-ID', { month: 'long' })}
              </option>
            ))}
          </select>
          <input
            type="number"
            value={tahun}
            onChange={(e) => setTahun(Number(e.target.value))}
            className="border border-gray-300 rounded px-3 py-2 w-24 text-sm"
            min="2020"
            max="2030"
          />
        </div>
      </div>

      {/* Export Buttons */}
      <div className="space-y-3">
        <button
          onClick={() => handleExport('excel-prediksi')}
          disabled={isLoading('excel-prediksi')}
          className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading('excel-prediksi') ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          ) : (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          )}
          <span>
            {isLoading('excel-prediksi') ? 'Mengexport...' : 'Excel Lengkap + Prediksi'}
          </span>
        </button>

        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={() => handleExport('excel')}
            disabled={isLoading('excel')}
            className="flex items-center justify-center space-x-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
          >
            {isLoading('excel') ? (
              <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white"></div>
            ) : (
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            )}
            <span>Excel Basic</span>
          </button>

          <button
            onClick={() => handleExport('csv')}
            disabled={isLoading('csv')}
            className="flex items-center justify-center space-x-2 px-3 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
          >
            {isLoading('csv') ? (
              <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white"></div>
            ) : (
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            )}
            <span>CSV</span>
          </button>
        </div>
      </div>

      {/* Description */}
      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
        <h4 className="text-sm font-medium text-gray-900 mb-2">Format Export:</h4>
        <ul className="text-xs text-gray-600 space-y-1">
          <li>• <strong>Excel Lengkap:</strong> Data sensus + prediksi BOR + ringkasan indikator (3 sheet)</li>
          <li>• <strong>Excel Basic:</strong> Data sensus harian saja</li>
          <li>• <strong>CSV:</strong> Format sederhana untuk analisis lanjut</li>
        </ul>
      </div>

      {/* File info */}
      <div className="mt-3 text-xs text-gray-500">
        <p>📁 File akan otomatis terdownload dengan nama:</p>
        <p className="font-mono bg-gray-100 px-2 py-1 rounded mt-1">
          laporan_sensus_prediksi_{bulan.toString().padStart(2, '0')}_{tahun}.xlsx
        </p>
      </div>
    </div>
  );
}
