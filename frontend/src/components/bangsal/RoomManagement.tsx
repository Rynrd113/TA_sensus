import React, { useState, useEffect, useCallback } from 'react';
import { KamarBangsal, Bangsal } from '../../types/Common';
import RoomList from './RoomList';
import bangsalService from '../../services/bangsalService';

interface RoomManagementProps {
  bangsal: Bangsal;
  onBack?: () => void;
}

export const RoomManagement: React.FC<RoomManagementProps> = ({
  bangsal,
  onBack
}) => {
  const [rooms, setRooms] = useState<KamarBangsal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load rooms for this bangsal
  const loadRooms = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await bangsalService.getBangsalRooms(bangsal.id);
      
      if (response.status === 'success') {
        setRooms(response.data);
      } else {
        setError(response.message);
      }
    } catch (err) {
      console.error('Error loading rooms:', err);
      setError('Gagal memuat data kamar. Silakan coba lagi.');
    } finally {
      setLoading(false);
    }
  }, [bangsal.id]);

  // Initial load
  useEffect(() => {
    loadRooms();
  }, [loadRooms]);

  // Handle add room
  const handleAddRoom = () => {
    console.log('Add room to bangsal:', bangsal.id);
    // TODO: Open add room modal or form
  };

  // Handle edit room
  const handleEditRoom = (room: KamarBangsal) => {
    console.log('Edit room:', room);
    // TODO: Open edit room modal or form
  };

  // Handle delete room
  const handleDeleteRoom = async (room: KamarBangsal) => {
    if (!window.confirm(`Apakah Anda yakin ingin menghapus kamar ${room.nomor_kamar}?`)) {
      return;
    }

    try {
      await bangsalService.deleteRoom(bangsal.id, room.id);
      await loadRooms(); // Reload rooms after deletion
    } catch (err) {
      console.error('Error deleting room:', err);
      alert('Gagal menghapus kamar. Silakan coba lagi.');
    }
  };

  // Handle room click
  const handleRoomClick = (room: KamarBangsal) => {
    console.log('Room clicked:', room);
    // TODO: Show room detail modal or navigate to room detail
  };

  return (
    <div className="space-y-6">
      {/* Breadcrumb / Back Navigation */}
      <div className="flex items-center gap-2 text-sm">
        <button
          onClick={onBack}
          className="text-blue-600 hover:text-blue-800 font-medium"
        >
          ← Kembali ke Daftar Bangsal
        </button>
        <span className="text-gray-400">/</span>
        <span className="text-gray-600">Manajemen Kamar</span>
      </div>

      {/* Bangsal Info Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {bangsal.nama_bangsal}
            </h1>
            <p className="text-gray-600">
              {bangsal.kode_bangsal} • {bangsal.departemen} • {bangsal.jenis_bangsal}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              Lantai {bangsal.lantai} • Kapasitas Total: {bangsal.kapasitas_total} bed
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="text-sm text-gray-600">Okupansi Bangsal</div>
              <div className={`text-2xl font-bold ${
                bangsal.occupancy_rate >= 90 ? 'text-red-600' : 
                bangsal.occupancy_rate >= 80 ? 'text-yellow-600' : 'text-green-600'
              }`}>
                {Math.round(bangsal.occupancy_rate)}%
              </div>
            </div>
            
            <div className="w-16 h-16 relative">
              <svg className="w-16 h-16 transform -rotate-90">
                <circle
                  cx="32"
                  cy="32"
                  r="28"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="transparent"
                  className="text-gray-200"
                />
                <circle
                  cx="32"
                  cy="32"
                  r="28"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="transparent"
                  strokeDasharray={`${2 * Math.PI * 28}`}
                  strokeDashoffset={`${2 * Math.PI * 28 * (1 - bangsal.occupancy_rate / 100)}`}
                  className={`transition-all duration-300 ${
                    bangsal.occupancy_rate >= 90 ? 'text-red-500' : 
                    bangsal.occupancy_rate >= 80 ? 'text-yellow-500' : 'text-green-500'
                  }`}
                />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Room List */}
      <RoomList
        rooms={rooms}
        bangsalName={bangsal.nama_bangsal}
        loading={loading}
        error={error}
        onRefresh={loadRooms}
        onAddRoom={handleAddRoom}
        onEditRoom={handleEditRoom}
        onDeleteRoom={handleDeleteRoom}
        onRoomClick={handleRoomClick}
        showActions={true}
      />
    </div>
  );
};

export default RoomManagement;