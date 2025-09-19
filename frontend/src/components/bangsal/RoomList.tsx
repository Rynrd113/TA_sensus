import React, { useState } from 'react';
import { KamarBangsal } from '../../types/Common';
import RoomCard from './RoomCard';
import { PlusIcon, FilterIcon, SearchIcon, RefreshIcon } from '../icons';

interface RoomListProps {
  rooms: KamarBangsal[];
  bangsalName: string;
  loading?: boolean;
  error?: string | null;
  onRefresh?: () => void;
  onAddRoom?: () => void;
  onEditRoom?: (room: KamarBangsal) => void;
  onDeleteRoom?: (room: KamarBangsal) => void;
  onRoomClick?: (room: KamarBangsal) => void;
  showActions?: boolean;
}

type RoomFilter = {
  jenis_kamar?: string;
  status_kebersihan?: string;
  is_available?: boolean;
  search?: string;
};

export const RoomList: React.FC<RoomListProps> = ({
  rooms,
  bangsalName,
  loading = false,
  error = null,
  onRefresh,
  onAddRoom,
  onEditRoom,
  onDeleteRoom,
  onRoomClick,
  showActions = true
}) => {
  const [filter, setFilter] = useState<RoomFilter>({});
  const [showFilters, setShowFilters] = useState(false);

  // Filter rooms based on current filter
  const filteredRooms = rooms.filter(room => {
    if (filter.search) {
      const search = filter.search.toLowerCase();
      if (!room.nomor_kamar.toLowerCase().includes(search) && 
          !room.jenis_kamar.toLowerCase().includes(search)) {
        return false;
      }
    }
    
    if (filter.jenis_kamar && room.jenis_kamar !== filter.jenis_kamar) {
      return false;
    }
    
    if (filter.status_kebersihan && room.status_kebersihan !== filter.status_kebersihan) {
      return false;
    }
    
    if (filter.is_available !== undefined && room.is_available !== filter.is_available) {
      return false;
    }
    
    return true;
  });

  // Get unique values for filters
  const getUniqueTypes = () => [...new Set(rooms.map(r => r.jenis_kamar))];
  const getUniqueStatuses = () => [...new Set(rooms.map(r => r.status_kebersihan))];

  // Calculate statistics
  const stats = {
    total: rooms.length,
    available: rooms.filter(r => r.is_available && r.jumlah_terisi < r.kapasitas_kamar).length,
    occupied: rooms.filter(r => r.jumlah_terisi > 0).length,
    full: rooms.filter(r => r.jumlah_terisi >= r.kapasitas_kamar).length,
    maintenance: rooms.filter(r => r.status_kebersihan === 'Maintenance').length,
    totalCapacity: rooms.reduce((sum, r) => sum + r.kapasitas_kamar, 0),
    totalOccupied: rooms.reduce((sum, r) => sum + r.jumlah_terisi, 0)
  };

  const occupancyRate = stats.totalCapacity > 0 
    ? Math.round((stats.totalOccupied / stats.totalCapacity) * 100)
    : 0;

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-300 rounded mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-white rounded-lg shadow-sm border p-4">
                <div className="h-4 bg-gray-300 rounded mb-2"></div>
                <div className="h-3 bg-gray-300 rounded mb-3 w-3/4"></div>
                <div className="h-2 bg-gray-300 rounded mb-2"></div>
                <div className="h-8 bg-gray-300 rounded"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Coba Lagi
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Stats */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Kamar di {bangsalName}
            </h2>
            <p className="text-gray-600 mt-1">
              {filteredRooms.length} dari {rooms.length} kamar
            </p>
          </div>
          
          <div className="flex gap-2">
            {onRefresh && (
              <button
                onClick={onRefresh}
                className="px-3 py-2 text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                <RefreshIcon className="w-4 h-4" />
              </button>
            )}
            
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`px-3 py-2 rounded-lg transition-colors ${
                showFilters || Object.keys(filter).some(key => filter[key as keyof RoomFilter])
                  ? 'text-blue-600 bg-blue-100'
                  : 'text-gray-600 bg-gray-100 hover:bg-gray-200'
              }`}
            >
              <FilterIcon className="w-4 h-4" />
            </button>
            
            {onAddRoom && showActions && (
              <button
                onClick={onAddRoom}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
              >
                <PlusIcon className="w-4 h-4" />
                <span className="hidden sm:inline">Tambah Kamar</span>
              </button>
            )}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{stats.total}</div>
            <div className="text-sm text-gray-600">Total Kamar</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{stats.available}</div>
            <div className="text-sm text-gray-600">Tersedia</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600">{stats.occupied}</div>
            <div className="text-sm text-gray-600">Terisi</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{stats.full}</div>
            <div className="text-sm text-gray-600">Penuh</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{occupancyRate}%</div>
            <div className="text-sm text-gray-600">Okupansi</div>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <SearchIcon className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
        <input
          type="text"
          placeholder="Cari nomor kamar atau jenis..."
          value={filter.search || ''}
          onChange={(e) => setFilter({...filter, search: e.target.value || undefined})}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="bg-white border border-gray-300 rounded-lg p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Jenis Kamar
              </label>
              <select
                value={filter.jenis_kamar || ''}
                onChange={(e) => setFilter({...filter, jenis_kamar: e.target.value || undefined})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Semua Jenis</option>
                {getUniqueTypes().map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status Kebersihan
              </label>
              <select
                value={filter.status_kebersihan || ''}
                onChange={(e) => setFilter({...filter, status_kebersihan: e.target.value || undefined})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Semua Status</option>
                {getUniqueStatuses().map(status => (
                  <option key={status} value={status}>{status}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Ketersediaan
              </label>
              <select
                value={filter.is_available !== undefined ? filter.is_available.toString() : ''}
                onChange={(e) => setFilter({
                  ...filter, 
                  is_available: e.target.value ? e.target.value === 'true' : undefined
                })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Semua</option>
                <option value="true">Tersedia</option>
                <option value="false">Tidak Tersedia</option>
              </select>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => setShowFilters(false)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Terapkan
            </button>
            <button
              onClick={() => setFilter({})}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Reset
            </button>
          </div>
        </div>
      )}

      {/* Room Grid */}
      {filteredRooms.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
            <PlusIcon className="w-8 h-8 text-gray-400" />
          </div>
          <p className="text-gray-500 mb-4">
            {Object.keys(filter).some(key => filter[key as keyof RoomFilter])
              ? 'Tidak ada kamar yang sesuai dengan filter'
              : 'Belum ada kamar di bangsal ini'
            }
          </p>
          {onAddRoom && showActions && (
            <button
              onClick={onAddRoom}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Tambah Kamar Pertama
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredRooms.map((room) => (
            <RoomCard
              key={room.id}
              room={room}
              onClick={onRoomClick}
              onEdit={onEditRoom}
              onDelete={onDeleteRoom}
              showActions={showActions}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default RoomList;