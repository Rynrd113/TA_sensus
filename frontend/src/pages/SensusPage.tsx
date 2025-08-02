import React, { useState, useEffect } from "react";
import SensusForm from "../components/forms/SensusForm";
import DataGrid from "../components/dashboard/DataGrid";
import Card from "../components/ui/Card";
import { bangsalService } from "../services/bangsalService";

const SensusPage: React.FC = () => {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [bangsalList, setBangsalList] = useState<any>(null);

  // Fetch bangsal list once on mount
  useEffect(() => {
    const fetchBangsalList = async () => {
      try {
        const data = await bangsalService.getAllBangsal();
        setBangsalList(data);
      } catch (error) {
        console.error('Error fetching bangsal list:', error);
      }
    };

    fetchBangsalList();
  }, []); // Empty dependency array - only fetch once

  const handleFormSuccess = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-primary-50 p-4 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Page Header */}
        <div className="bg-white rounded-lg border border-primary-200 p-6 shadow-sm">
          <h1 className="text-2xl font-bold text-vmeds-900 mb-2">Input Data Sensus Harian</h1>
          <p className="text-vmeds-600">
            Masukkan data sensus pasien untuk menghitung indikator rumah sakit (BOR, ALOS, BTO, TOI)
          </p>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Form Section */}
          <div className="lg:col-span-2">
            <SensusForm 
              onSuccess={handleFormSuccess}
              bangsalList={bangsalList?.data || []}
            />
          </div>

          {/* Info Card */}
          <div className="space-y-6">
            <Card 
              title="Panduan Input" 
              variant="default"
            >
            <div className="space-y-4 text-sm">
              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs font-bold">
                  1
                </div>
                <div>
                  <p className="font-medium text-gray-800">Pilih Tanggal & Bangsal</p>
                  <p className="text-gray-600 text-xs">Pastikan tanggal dan bangsal sudah benar</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs font-bold">
                  2
                </div>
                <div>
                  <p className="font-medium text-gray-800">Input Data Tempat Tidur</p>
                  <p className="text-gray-600 text-xs">Total TT dan TT terisi harus akurat</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs font-bold">
                  3
                </div>
                <div>
                  <p className="font-medium text-gray-800">Masukkan Data Pasien</p>
                  <p className="text-gray-600 text-xs">Pasien masuk dan keluar pada hari tersebut</p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs font-bold">
                  4
                </div>
                <div>
                  <p className="font-medium text-gray-800">Hitung ALOS</p>
                  <p className="text-gray-600 text-xs">Rata-rata lama rawat dalam hari</p>
                </div>
              </div>
            </div>

            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-yellow-800 text-xs font-medium">
                💡 <strong>Tips:</strong> Data yang akurat akan menghasilkan indikator yang lebih valid untuk pengambilan keputusan manajemen.
              </p>
            </div>
          </Card>

          <Card 
            title="Indikator Dihitung" 
            variant="default"
          >
            <div className="space-y-3 text-sm">
              <div className="flex justify-between items-center">
                <span className="font-medium text-gray-700">BOR</span>
                <span className="text-blue-600 text-xs">Bed Occupancy Rate</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="font-medium text-gray-700">ALOS</span>
                <span className="text-blue-600 text-xs">Average Length of Stay</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="font-medium text-gray-700">BTO</span>
                <span className="text-blue-600 text-xs">Bed Turn Over</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="font-medium text-gray-700">TOI</span>
                <span className="text-blue-600 text-xs">Turn Over Interval</span>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Data Grid Section */}
      <DataGrid 
        refreshTrigger={refreshTrigger} 
        showActions={true}
      />
    </div>
    </div>
  );
};

export default SensusPage;
