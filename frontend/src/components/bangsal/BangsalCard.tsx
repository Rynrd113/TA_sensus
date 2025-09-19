import React from 'react';
import { Bangsal } from '../../types/Common';
import { 
  BuildingIcon, 
  UsersIcon, 
  CheckCircleIcon, 
  ExclamationTriangleIcon,
  MapPinIcon,
  PhoneIcon
} from '../icons';

interface BangsalCardProps {
  bangsal: Bangsal;
  onClick?: (bangsal: Bangsal) => void;
  showActions?: boolean;
  onEdit?: (bangsal: Bangsal) => void;
  onDelete?: (bangsal: Bangsal) => void;
  onViewRooms?: (bangsal: Bangsal) => void;
}

export const BangsalCard: React.FC<BangsalCardProps> = ({
  bangsal,
  onClick,
  showActions = false,
  onEdit,
  onDelete,
  onViewRooms
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Aktif':
        return 'bg-green-100 text-green-800';
      case 'Maintenance':
        return 'bg-yellow-100 text-yellow-800';
      case 'Tutup Sementara':
        return 'bg-red-100 text-red-800';
      case 'Renovasi':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeColor = (type: string) => {
    const colors = {
      'ICU': 'bg-red-50 text-red-700 border-red-200',
      'NICU': 'bg-purple-50 text-purple-700 border-purple-200',
      'PICU': 'bg-pink-50 text-pink-700 border-pink-200',
      'VIP': 'bg-blue-50 text-blue-700 border-blue-200',
      'VVIP': 'bg-indigo-50 text-indigo-700 border-indigo-200',
      'Emergency': 'bg-orange-50 text-orange-700 border-orange-200',
      'Isolasi': 'bg-yellow-50 text-yellow-700 border-yellow-200'
    };
    return colors[type as keyof typeof colors] || 'bg-gray-50 text-gray-700 border-gray-200';
  };

  const occupancyPercentage = Math.round(bangsal.occupancy_rate);
  const isHighOccupancy = occupancyPercentage >= 80;
  const isCriticalOccupancy = occupancyPercentage >= 95;

  return (
    <div 
      className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow ${
        onClick ? 'cursor-pointer hover:border-blue-300' : ''
      }`}
      onClick={() => onClick?.(bangsal)}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <BuildingIcon className="w-5 h-5 text-gray-400" />
            <h3 className="text-lg font-semibold text-gray-900">
              {bangsal.nama_bangsal}
            </h3>
            {bangsal.is_emergency_ready && (
              <CheckCircleIcon className="w-5 h-5 text-green-500" />
            )}
          </div>
          
          <p className="text-sm text-gray-600 mb-2">
            <span className="font-medium">{bangsal.kode_bangsal}</span> • {bangsal.departemen}
          </p>

          <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getTypeColor(bangsal.jenis_bangsal)}`}>
            {bangsal.jenis_bangsal}
          </div>
        </div>

        <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(bangsal.status_operasional)}`}>
          {bangsal.status_operasional}
        </div>
      </div>

      {/* Capacity Info */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <UsersIcon className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-600">Kapasitas</span>
          </div>
          <span className={`text-sm font-medium ${isCriticalOccupancy ? 'text-red-600' : isHighOccupancy ? 'text-yellow-600' : 'text-green-600'}`}>
            {occupancyPercentage}%
          </span>
        </div>
        
        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
          <div 
            className={`h-2 rounded-full transition-all ${
              isCriticalOccupancy ? 'bg-red-500' : isHighOccupancy ? 'bg-yellow-500' : 'bg-green-500'
            }`}
            style={{ width: `${Math.min(occupancyPercentage, 100)}%` }}
          />
        </div>

        <div className="flex justify-between text-sm text-gray-600">
          <span>{bangsal.jumlah_terisi} terisi</span>
          <span>{bangsal.jumlah_tersedia} tersedia</span>
          <span>{bangsal.kapasitas_total} total</span>
        </div>
      </div>

      {/* Location & Contact */}
      <div className="space-y-2 mb-4">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <MapPinIcon className="w-4 h-4" />
          <span>Lantai {bangsal.lantai}</span>
          {bangsal.lokasi_detail && (
            <span className="text-gray-400">• {bangsal.lokasi_detail}</span>
          )}
        </div>
        
        {bangsal.pic_bangsal && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <PhoneIcon className="w-4 h-4" />
            <span>{bangsal.pic_bangsal}</span>
            {bangsal.kontak_pic && (
              <span className="text-gray-400">• {bangsal.kontak_pic}</span>
            )}
          </div>
        )}
      </div>

      {/* Rooms Info */}
      {bangsal.rooms && bangsal.rooms.length > 0 && (
        <div className="mb-4 p-3 bg-gray-50 rounded-md">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">
              {bangsal.rooms.length} kamar
            </span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onViewRooms?.(bangsal);
              }}
              className="text-xs text-blue-600 hover:text-blue-800"
            >
              Lihat Detail
            </button>
          </div>
        </div>
      )}

      {/* Warnings */}
      {(isCriticalOccupancy || bangsal.status_operasional !== 'Aktif') && (
        <div className="mb-4 p-2 bg-yellow-50 border border-yellow-200 rounded-md">
          <div className="flex items-center gap-2">
            <ExclamationTriangleIcon className="w-4 h-4 text-yellow-600" />
            <span className="text-xs text-yellow-800">
              {isCriticalOccupancy && 'Kapasitas hampir penuh'}
              {isCriticalOccupancy && bangsal.status_operasional !== 'Aktif' && ' • '}
              {bangsal.status_operasional !== 'Aktif' && 'Status tidak aktif'}
            </span>
          </div>
        </div>
      )}

      {/* Actions */}
      {showActions && (
        <div className="flex gap-2 pt-4 border-t border-gray-100">
          {onEdit && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onEdit(bangsal);
              }}
              className="flex-1 px-3 py-2 text-sm text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors"
            >
              Edit
            </button>
          )}
          {onViewRooms && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onViewRooms(bangsal);
              }}
              className="flex-1 px-3 py-2 text-sm text-gray-600 bg-gray-50 rounded-md hover:bg-gray-100 transition-colors"
            >
              Kamar
            </button>
          )}
          {onDelete && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(bangsal);
              }}
              className="px-3 py-2 text-sm text-red-600 bg-red-50 rounded-md hover:bg-red-100 transition-colors"
            >
              Hapus
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default BangsalCard;