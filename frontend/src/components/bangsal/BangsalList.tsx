import React, { useState, useEffect } from 'react';
import { Bangsal, BangsalFilter } from '../../types/Common';
import BangsalCard from './BangsalCard';
import { PlusIcon, FilterIcon, SearchIcon, RefreshIcon, BuildingIcon } from '../icons';

interface BangsalListProps {
  bangsal?: Bangsal[];
  loading?: boolean;
  error?: string | null;
  onRefresh?: () => void;
  onCreateBangsal?: () => void;
  onEditBangsal?: (bangsal: Bangsal) => void;
  onDeleteBangsal?: (bangsal: Bangsal) => void;
  onViewRooms?: (bangsal: Bangsal) => void;
  onBangsalClick?: (bangsal: Bangsal) => void;
  showActions?: boolean;
  filter?: BangsalFilter;
  onFilterChange?: (filter: BangsalFilter) => void;
}

export const BangsalList: React.FC<BangsalListProps> = ({
  bangsal = [],
  loading = false,
  error = null,
  onRefresh,
  onCreateBangsal,
  onEditBangsal,
  onDeleteBangsal,
  onViewRooms,
  onBangsalClick,
  showActions = true,
  filter = {},
  onFilterChange
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredBangsal, setFilteredBangsal] = useState<Bangsal[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [localFilter, setLocalFilter] = useState<BangsalFilter>(filter);

  // Filter bangsal based on search query and filters
  useEffect(() => {
    let filtered = bangsal;

    // Apply search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(b =>
        b.nama_bangsal.toLowerCase().includes(query) ||
        b.kode_bangsal.toLowerCase().includes(query) ||
        b.departemen.toLowerCase().includes(query) ||
        b.jenis_bangsal.toLowerCase().includes(query)
      );
    }

    // Apply local filters
    if (localFilter.departemen) {
      filtered = filtered.filter(b => b.departemen === localFilter.departemen);
    }
    if (localFilter.jenis_bangsal) {
      filtered = filtered.filter(b => b.jenis_bangsal === localFilter.jenis_bangsal);
    }
    if (localFilter.lantai !== undefined) {
      filtered = filtered.filter(b => b.lantai === localFilter.lantai);
    }
    if (localFilter.status_operasional) {
      filtered = filtered.filter(b => b.status_operasional === localFilter.status_operasional);
    }
    if (localFilter.is_emergency_ready !== undefined) {
      filtered = filtered.filter(b => b.is_emergency_ready === localFilter.is_emergency_ready);
    }
    if (localFilter.min_capacity) {
      filtered = filtered.filter(b => b.kapasitas_total >= localFilter.min_capacity!);
    }
    if (localFilter.max_capacity) {
      filtered = filtered.filter(b => b.kapasitas_total <= localFilter.max_capacity!);
    }

    setFilteredBangsal(filtered);
  }, [bangsal, searchQuery, localFilter]);

  // Apply filters
  const applyFilters = () => {
    onFilterChange?.(localFilter);
    setShowFilters(false);
  };

  // Reset filters
  const resetFilters = () => {
    setLocalFilter({});
    setSearchQuery('');
    onFilterChange?.({});
  };

  // Get unique values for filter options
  const getDepartments = () => [...new Set(bangsal.map(b => b.departemen))];
  const getTypes = () => [...new Set(bangsal.map(b => b.jenis_bangsal))];
  const getFloors = () => [...new Set(bangsal.map(b => b.lantai))].sort((a, b) => a - b);

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="animate-pulse">
              <div className="flex justify-between items-start mb-4">
                <div className="space-y-2">
                  <div className="h-6 bg-gray-300 rounded w-48"></div>
                  <div className="h-4 bg-gray-300 rounded w-32"></div>
                </div>
                <div className="h-4 bg-gray-300 rounded w-20"></div>
              </div>
              <div className="space-y-2">
                <div className="h-4 bg-gray-300 rounded"></div>
                <div className="h-4 bg-gray-300 rounded w-3/4"></div>
              </div>
            </div>
          </div>
        ))}
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
      {/* Header with actions */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex-1">
          <h2 className="text-xl font-semibold text-gray-900">
            Daftar Bangsal ({filteredBangsal.length})
          </h2>
          {searchQuery || Object.keys(localFilter).length > 0 && (
            <p className="text-sm text-gray-600 mt-1">
              Menampilkan hasil filter dari {bangsal.length} total bangsal
            </p>
          )}
        </div>
        
        <div className="flex gap-2">
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="px-3 py-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <RefreshIcon className="w-4 h-4" />
            </button>
          )}
          
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`px-3 py-2 border rounded-lg transition-colors ${
              showFilters || Object.keys(localFilter).length > 0
                ? 'text-blue-600 bg-blue-50 border-blue-300'
                : 'text-gray-600 bg-white border-gray-300 hover:bg-gray-50'
            }`}
          >
            <FilterIcon className="w-4 h-4" />
          </button>
          
          {onCreateBangsal && showActions && (
            <button
              onClick={onCreateBangsal}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <PlusIcon className="w-4 h-4" />
              <span className="hidden sm:inline">Tambah Bangsal</span>
            </button>
          )}
        </div>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <SearchIcon className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
        <input
          type="text"
          placeholder="Cari bangsal, kode, departemen..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div className="bg-white border border-gray-300 rounded-lg p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-4">
            {/* Department Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Departemen
              </label>
              <select
                value={localFilter.departemen || ''}
                onChange={(e) => setLocalFilter({...localFilter, departemen: e.target.value || undefined})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Semua Departemen</option>
                {getDepartments().map(dept => (
                  <option key={dept} value={dept}>{dept}</option>
                ))}
              </select>
            </div>

            {/* Type Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Jenis Bangsal
              </label>
              <select
                value={localFilter.jenis_bangsal || ''}
                onChange={(e) => setLocalFilter({...localFilter, jenis_bangsal: e.target.value || undefined})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Semua Jenis</option>
                {getTypes().map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>

            {/* Floor Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Lantai
              </label>
              <select
                value={localFilter.lantai || ''}
                onChange={(e) => setLocalFilter({...localFilter, lantai: e.target.value ? parseInt(e.target.value) : undefined})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Semua Lantai</option>
                {getFloors().map(floor => (
                  <option key={floor} value={floor}>Lantai {floor}</option>
                ))}
              </select>
            </div>

            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                value={localFilter.status_operasional || ''}
                onChange={(e) => setLocalFilter({...localFilter, status_operasional: e.target.value || undefined})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Semua Status</option>
                <option value="Aktif">Aktif</option>
                <option value="Maintenance">Maintenance</option>
                <option value="Tutup Sementara">Tutup Sementara</option>
                <option value="Renovasi">Renovasi</option>
              </select>
            </div>

            {/* Capacity Range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Min Kapasitas
              </label>
              <input
                type="number"
                placeholder="0"
                value={localFilter.min_capacity || ''}
                onChange={(e) => setLocalFilter({...localFilter, min_capacity: e.target.value ? parseInt(e.target.value) : undefined})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Kapasitas
              </label>
              <input
                type="number"
                placeholder="100"
                value={localFilter.max_capacity || ''}
                onChange={(e) => setLocalFilter({...localFilter, max_capacity: e.target.value ? parseInt(e.target.value) : undefined})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Emergency Ready */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Emergency Ready
              </label>
              <select
                value={localFilter.is_emergency_ready !== undefined ? localFilter.is_emergency_ready.toString() : ''}
                onChange={(e) => setLocalFilter({
                  ...localFilter, 
                  is_emergency_ready: e.target.value ? e.target.value === 'true' : undefined
                })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Semua</option>
                <option value="true">Ya</option>
                <option value="false">Tidak</option>
              </select>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={applyFilters}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Terapkan Filter
            </button>
            <button
              onClick={resetFilters}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
            >
              Reset
            </button>
          </div>
        </div>
      )}

      {/* Bangsal Grid */}
      {filteredBangsal.length === 0 ? (
        <div className="text-center py-12">
          <BuildingIcon className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 mb-2">
            {searchQuery || Object.keys(localFilter).length > 0
              ? 'Tidak ada bangsal yang sesuai dengan filter'
              : 'Belum ada data bangsal'
            }
          </p>
          {onCreateBangsal && showActions && (
            <button
              onClick={onCreateBangsal}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Tambah Bangsal Pertama
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {filteredBangsal.map((bangsalItem) => (
            <BangsalCard
              key={bangsalItem.id}
              bangsal={bangsalItem}
              onClick={onBangsalClick}
              showActions={showActions}
              onEdit={onEditBangsal}
              onDelete={onDeleteBangsal}
              onViewRooms={onViewRooms}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default BangsalList;