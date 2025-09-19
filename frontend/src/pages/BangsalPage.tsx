import { useState, useEffect, useCallback } from 'react';
import { Bangsal, BangsalStats as BangsalStatsType, BangsalFilter, LoadingState } from '../types/Common';
import { BangsalList, BangsalStats, DepartmentStats, TypeStats } from '../components/bangsal';
import bangsalService from '../services/bangsalService';

export default function BangsalPage() {
  const [bangsal, setBangsal] = useState<Bangsal[]>([]);
  const [stats, setStats] = useState<BangsalStatsType | null>(null);
  const [loadingState, setLoadingState] = useState<LoadingState>({
    loading: true,
    error: null
  });
  const [filter, setFilter] = useState<BangsalFilter>({});
  const [statsLoading, setStatsLoading] = useState(true);

  // Load bangsal data
  const loadBangsal = useCallback(async (currentFilter: BangsalFilter = {}) => {
    try {
      setLoadingState({ loading: true, error: null });
      const response = await bangsalService.getAllBangsal(currentFilter);
      
      if (response.status === 'success') {
        setBangsal(response.data);
      } else {
        setLoadingState({ loading: false, error: response.message });
      }
    } catch (error) {
      console.error('Error loading bangsal:', error);
      setLoadingState({ 
        loading: false, 
        error: 'Gagal memuat data bangsal. Silakan coba lagi.' 
      });
    } finally {
      setLoadingState(prev => ({ ...prev, loading: false }));
    }
  }, []);

  // Load statistics
  const loadStats = useCallback(async () => {
    try {
      setStatsLoading(true);
      const response = await bangsalService.getBangsalStatistics();
      
      if (response.status === 'success') {
        setStats(response.data);
      }
    } catch (error) {
      console.error('Error loading stats:', error);
    } finally {
      setStatsLoading(false);
    }
  }, []);

  // Initial data load
  useEffect(() => {
    loadBangsal();
    loadStats();
  }, [loadBangsal, loadStats]);

  // Handle filter changes
  const handleFilterChange = useCallback((newFilter: BangsalFilter) => {
    setFilter(newFilter);
    loadBangsal(newFilter);
  }, [loadBangsal]);

  // Handle refresh
  const handleRefresh = useCallback(() => {
    loadBangsal(filter);
    loadStats();
  }, [loadBangsal, loadStats, filter]);

  // Handle bangsal click
  const handleBangsalClick = (selectedBangsal: Bangsal) => {
    console.log('Bangsal clicked:', selectedBangsal);
    // TODO: Navigate to bangsal detail page or show modal
  };

  // Handle create bangsal
  const handleCreateBangsal = () => {
    console.log('Create bangsal clicked');
    // TODO: Open create bangsal modal or navigate to form
  };

  // Handle edit bangsal
  const handleEditBangsal = (bangsalToEdit: Bangsal) => {
    console.log('Edit bangsal:', bangsalToEdit);
    // TODO: Open edit bangsal modal or navigate to form
  };

  // Handle delete bangsal
  const handleDeleteBangsal = async (bangsalToDelete: Bangsal) => {
    if (!window.confirm(`Apakah Anda yakin ingin menghapus bangsal ${bangsalToDelete.nama_bangsal}?`)) {
      return;
    }

    try {
      await bangsalService.deleteBangsal(bangsalToDelete.id);
      handleRefresh();
    } catch (error) {
      console.error('Error deleting bangsal:', error);
      alert('Gagal menghapus bangsal. Silakan coba lagi.');
    }
  };

  // Handle view rooms
  const handleViewRooms = (bangsalForRooms: Bangsal) => {
    console.log('View rooms for bangsal:', bangsalForRooms);
    // TODO: Navigate to room management page or show modal
  };

  return (
    <div className="p-6 space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Manajemen Bangsal</h1>
        <p className="text-gray-600 mt-2">
          Kelola bangsal rumah sakit, kapasitas, dan ketersediaan tempat tidur
        </p>
      </div>

      {/* Statistics Section */}
      {stats && (
        <div className="space-y-6">
          <BangsalStats stats={stats} loading={statsLoading} />
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <DepartmentStats stats={stats} />
            <TypeStats stats={stats} />
          </div>
        </div>
      )}

      {/* Main Bangsal List */}
      <BangsalList
        bangsal={bangsal}
        loading={loadingState.loading}
        error={loadingState.error}
        onRefresh={handleRefresh}
        onCreateBangsal={handleCreateBangsal}
        onEditBangsal={handleEditBangsal}
        onDeleteBangsal={handleDeleteBangsal}
        onViewRooms={handleViewRooms}
        onBangsalClick={handleBangsalClick}
        showActions={true}
        filter={filter}
        onFilterChange={handleFilterChange}
      />
    </div>
  );
}