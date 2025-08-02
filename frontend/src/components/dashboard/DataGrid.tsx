import React, { useState, useEffect } from 'react';
import { sensusService } from '../../services/sensusService';
import { SensusResponse } from '../../types/Sensus';
import Card from '../ui/Card';
import Button from '../ui/Button';
import { RefreshIcon, CalendarIcon } from '../icons/index';
import { formatDate, formatNumber } from '../../utils/format';

interface DataGridProps {
  refreshTrigger?: number;
  className?: string;
  pageSize?: number;
  showActions?: boolean;
}

interface Column<T> {
  key: keyof T;
  label: string;
  render?: (value: any, row: T) => React.ReactNode;
  className?: string;
  sortable?: boolean;
}

const DataGrid: React.FC<DataGridProps> = ({
  refreshTrigger,
  className,
  pageSize = 10,
  showActions = true
}) => {
  const [data, setData] = useState<SensusResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSensusData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await sensusService.getAllSensus();
      setData(response.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error fetching data');
    } finally {
      setLoading(false);
    }
  };

  // Fetch data once on mount
  useEffect(() => {
    fetchSensusData();
  }, []); // Empty dependency array - only fetch once

  // Refresh saat trigger berubah
  useEffect(() => {
    if (refreshTrigger && refreshTrigger > 0) {
      fetchSensusData();
    }
  }, [refreshTrigger]); // Only depend on refreshTrigger

  const columns: Column<SensusResponse>[] = [
    {
      key: 'tanggal',
      label: 'Tanggal',
      render: (value) => (
        <div className="flex items-center space-x-2">
          <CalendarIcon className="w-4 h-4 text-blue-500" />
          <span className="font-medium">{formatDate(value)}</span>
        </div>
      ),
      sortable: true
    },
    {
      key: 'bangsal_nama',
      label: 'Bangsal',
      render: (value) => (
        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
          {value || 'Unknown'}
        </span>
      )
    },
    {
      key: 'jumlah_tempat_tidur',
      label: 'Total TT',
      render: (value) => (
        <span className="font-mono text-sm">{formatNumber(value)}</span>
      ),
      className: 'text-center'
    },
    {
      key: 'tempat_tidur_terisi',
      label: 'TT Terisi',
      render: (value) => (
        <span className="font-mono text-sm">{formatNumber(value)}</span>
      ),
      className: 'text-center'
    },
    {
      key: 'pasien_masuk',
      label: 'Masuk',
      render: (value) => (
        <span className="font-mono text-sm text-primary-700">{formatNumber(value)}</span>
      ),
      className: 'text-center'
    },
    {
      key: 'pasien_keluar',
      label: 'Keluar',
      render: (value) => (
        <span className="font-mono text-sm text-vmeds-700">{formatNumber(value)}</span>
      ),
      className: 'text-center'
    },
    {
      key: 'bor',
      label: 'BOR (%)',
      render: (value) => {
        const borValue = Number(value);
        const colorClass = borValue > 85 ? 'text-red-700 bg-red-100' : 
                          borValue < 60 ? 'text-yellow-700 bg-yellow-100' : 
                          'text-primary-700 bg-primary-100';
        return (
          <span className={`px-2 py-1 rounded-full text-xs font-bold ${colorClass}`}>
            {formatNumber(borValue, 1)}%
          </span>
        );
      },
      className: 'text-center'
    },
    {
      key: 'alos',
      label: 'ALOS',
      render: (value) => (
        <span className="font-mono text-sm">{formatNumber(value, 1)} hari</span>
      ),
      className: 'text-center'
    },
    {
      key: 'bto',
      label: 'BTO',
      render: (value) => (
        <span className="font-mono text-sm">{formatNumber(value, 1)}x</span>
      ),
      className: 'text-center'
    },
    {
      key: 'toi',
      label: 'TOI',
      render: (value) => (
        <span className="font-mono text-sm">{formatNumber(value, 1)} hari</span>
      ),
      className: 'text-center'
    }
  ];

  if (loading) {
    return (
      <Card title="Data Sensus Terbaru" variant="default" className={className}>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <span className="ml-3 text-vmeds-600">Memuat data...</span>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="Data Sensus Terbaru" variant="default" className={className}>
        <div className="flex flex-col items-center justify-center h-64 space-y-4">
          <div className="text-red-500 text-lg">⚠️ Error</div>
          <p className="text-vmeds-600 text-center">{error}</p>
          <Button
            variant="primary"
            onClick={fetchSensusData}
            icon={<RefreshIcon className="w-4 h-4" />}
          >
            Coba Lagi
          </Button>
        </div>
      </Card>
    );
  }

  const sortedData = data?.sort((a, b) => 
    new Date(b.tanggal).getTime() - new Date(a.tanggal).getTime()
  ) || [];

  const displayData = sortedData.slice(0, pageSize);

  return (
    <Card 
      title="Data Sensus Terbaru" 
      variant="default" 
      className={className}
      header={
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="px-2 py-1 bg-primary-100 text-primary-800 rounded-full text-xs font-medium">
              {sortedData.length} record
            </span>
          </div>
          {showActions && (
            <Button
              variant="ghost"
              size="sm"
              onClick={fetchSensusData}
              icon={<RefreshIcon className="w-4 h-4" />}
              disabled={loading}
            >
              Refresh
            </Button>
          )}
        </div>
      }
    >
      {displayData.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-vmeds-400 text-6xl mb-4">📊</div>
          <p className="text-vmeds-600 text-lg">Belum ada data sensus</p>
          <p className="text-vmeds-500 text-sm mt-2">
            Silakan input data sensus untuk melihat tabel ini
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-primary-200">
            <thead className="bg-primary-50">
              <tr>
                {columns.map((column) => (
                  <th
                    key={String(column.key)}
                    className={`px-4 py-3 text-left text-xs font-medium text-vmeds-500 uppercase tracking-wider ${
                      column.className || ''
                    }`}
                  >
                    {column.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-primary-200">
              {displayData.map((row, index) => (
                <tr
                  key={row.id || index}
                  className="hover:bg-primary-50 transition-colors duration-150"
                >
                  {columns.map((column) => (
                    <td
                      key={String(column.key)}
                      className={`px-4 py-4 whitespace-nowrap text-sm ${
                        column.className || ''
                      }`}
                    >
                      {column.render
                        ? column.render(row[column.key], row)
                        : String(row[column.key] || '-')}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {sortedData.length > pageSize && (
        <div className="mt-4 flex justify-between items-center pt-4 border-t border-primary-200">
          <div className="text-sm text-vmeds-600">
            Menampilkan {Math.min(pageSize, sortedData.length)} dari {sortedData.length} data
          </div>
          <div className="text-xs text-vmeds-500">
            💡 Untuk melihat semua data, gunakan halaman Export atau Chart
          </div>
        </div>
      )}
    </Card>
  );
};

export default DataGrid;
