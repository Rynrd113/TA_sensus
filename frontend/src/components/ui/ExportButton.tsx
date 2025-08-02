// frontend/src/components/ui/ExportButton.tsx
import React, { useState } from 'react';
import { exportService } from '../../services/exportService';

interface ExportButtonProps {
  bulan?: number;
  tahun?: number;
  variant?: 'current' | 'all';
  className?: string;
}

export default function ExportButton({ 
  bulan, 
  tahun, 
  variant = 'current',
  className = '' 
}: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleExport = async () => {
    try {
      setIsExporting(true);
      setError(null);

      let blob: Blob;
      let filename: string;

      if (variant === 'all') {
        blob = await exportService.exportAllToExcel();
        filename = `sensus_harian_all_${new Date().toISOString().split('T')[0]}.xlsx`;
      } else {
        const currentDate = new Date();
        const exportBulan = bulan || currentDate.getMonth() + 1;
        const exportTahun = tahun || currentDate.getFullYear();
        
        blob = await exportService.exportToExcel(exportBulan, exportTahun);
        filename = `sensus_harian_${exportBulan.toString().padStart(2, '0')}_${exportTahun}.xlsx`;
      }

      // Download file
      exportService.downloadBlob(blob, filename);

    } catch (err: any) {
      console.error('Export error:', err);
      setError('Gagal export ke Excel. Pastikan backend berjalan.');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="relative">
      <button
        onClick={handleExport}
        disabled={isExporting}
        className={`
          flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors
          ${isExporting 
            ? 'bg-gray-400 text-gray-700 cursor-not-allowed' 
            : 'bg-green-600 text-white hover:bg-green-700'
          }
          ${className}
        `}
      >
        {isExporting ? (
          <>
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            <span>Exporting...</span>
          </>
        ) : (
          <>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span>
              {variant === 'all' ? 'Export Semua Data' : 'Export ke Excel'}
            </span>
          </>
        )}
      </button>

      {error && (
        <div className="absolute top-full left-0 mt-2 p-2 bg-red-100 border border-red-300 rounded text-red-700 text-sm whitespace-nowrap z-10">
          {error}
        </div>
      )}
    </div>
  );
}
