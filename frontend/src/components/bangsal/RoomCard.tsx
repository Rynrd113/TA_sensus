import React from 'react';
import { KamarBangsal } from '../../types/Common';
import { 
  BedIcon, 
  CheckCircleIcon, 
  ExclamationTriangleIcon, 
  PencilIcon,
  TrashIcon,
  UsersIcon
} from '../icons';

interface RoomCardProps {
  room: KamarBangsal;
  onClick?: (room: KamarBangsal) => void;
  onEdit?: (room: KamarBangsal) => void;
  onDelete?: (room: KamarBangsal) => void;
  showActions?: boolean;
}

export const RoomCard: React.FC<RoomCardProps> = ({
  room,
  onClick,
  onEdit,
  onDelete,
  showActions = false
}) => {
  const occupancyPercentage = room.kapasitas_kamar > 0 
    ? Math.round((room.jumlah_terisi / room.kapasitas_kamar) * 100) 
    : 0;
  
  const isAvailable = room.is_available && room.jumlah_terisi < room.kapasitas_kamar;
  const isFull = room.jumlah_terisi >= room.kapasitas_kamar;
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Bersih':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'Kotor':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'Maintenance':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTypeColor = (type: string) => {
    const colors = {
      'Single': 'bg-blue-50 text-blue-700',
      'Double': 'bg-purple-50 text-purple-700', 
      'Multi': 'bg-green-50 text-green-700',
      'Suite': 'bg-indigo-50 text-indigo-700',
      'ICU': 'bg-red-50 text-red-700',
      'Isolasi': 'bg-yellow-50 text-yellow-700'
    };
    return colors[type as keyof typeof colors] || 'bg-gray-50 text-gray-700';
  };

  return (
    <div 
      className={`bg-white rounded-lg shadow-sm border-2 p-4 transition-all hover:shadow-md ${
        !isAvailable ? 'border-red-200 bg-red-50' :
        isFull ? 'border-yellow-200 bg-yellow-50' : 
        'border-gray-200 hover:border-blue-300'
      } ${onClick ? 'cursor-pointer' : ''}`}
      onClick={() => onClick?.(room)}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <BedIcon className="w-4 h-4 text-gray-400" />
            <h3 className="font-semibold text-gray-900">
              {room.nomor_kamar}
            </h3>
            {!isAvailable && (
              <ExclamationTriangleIcon className="w-4 h-4 text-red-500" />
            )}
            {isAvailable && !isFull && (
              <CheckCircleIcon className="w-4 h-4 text-green-500" />
            )}
          </div>
          
          <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getTypeColor(room.jenis_kamar)}`}>
            {room.jenis_kamar}
          </div>
        </div>

        <div className={`px-2 py-1 rounded-md text-xs font-medium border ${getStatusColor(room.status_kebersihan)}`}>
          {room.status_kebersihan}
        </div>
      </div>

      {/* Capacity Info */}
      <div className="mb-3">
        <div className="flex items-center justify-between mb-1">
          <div className="flex items-center gap-1">
            <UsersIcon className="w-3 h-3 text-gray-400" />
            <span className="text-xs text-gray-600">Okupansi</span>
          </div>
          <span className={`text-xs font-medium ${
            isFull ? 'text-red-600' : occupancyPercentage > 80 ? 'text-yellow-600' : 'text-green-600'
          }`}>
            {occupancyPercentage}%
          </span>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-1.5">
          <div 
            className={`h-1.5 rounded-full transition-all ${
              isFull ? 'bg-red-500' : occupancyPercentage > 80 ? 'bg-yellow-500' : 'bg-green-500'
            }`}
            style={{ width: `${Math.min(occupancyPercentage, 100)}%` }}
          />
        </div>
        
        <div className="flex justify-between text-xs text-gray-600 mt-1">
          <span>{room.jumlah_terisi} terisi</span>
          <span>{room.kapasitas_kamar} kapasitas</span>
        </div>
      </div>

      {/* Tarif */}
      {room.tarif_per_hari && (
        <div className="mb-3 p-2 bg-blue-50 rounded-md">
          <div className="text-xs text-blue-600">
            Rp {room.tarif_per_hari.toLocaleString('id-ID')}/hari
          </div>
        </div>
      )}

      {/* Fasilitas */}
      {room.fasilitas_kamar && (
        <div className="mb-3">
          <p className="text-xs text-gray-600 line-clamp-2">
            <span className="font-medium">Fasilitas:</span> {room.fasilitas_kamar}
          </p>
        </div>
      )}

      {/* Keterangan */}
      {room.keterangan && (
        <div className="mb-3 p-2 bg-gray-50 rounded-md">
          <p className="text-xs text-gray-600">{room.keterangan}</p>
        </div>
      )}

      {/* Status Indicators */}
      <div className="flex gap-2 mb-3">
        <div className={`flex-1 text-center py-1 px-2 rounded-md text-xs font-medium ${
          isAvailable ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {isAvailable ? 'Tersedia' : 'Tidak Tersedia'}
        </div>
        <div className={`flex-1 text-center py-1 px-2 rounded-md text-xs font-medium ${
          isFull ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
        }`}>
          {isFull ? 'Penuh' : `${room.kapasitas_kamar - room.jumlah_terisi} bed kosong`}
        </div>
      </div>

      {/* Actions */}
      {showActions && (
        <div className="flex gap-2 pt-3 border-t border-gray-100">
          {onEdit && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onEdit(room);
              }}
              className="flex-1 flex items-center justify-center gap-1 px-2 py-1 text-xs text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors"
            >
              <PencilIcon className="w-3 h-3" />
              Edit
            </button>
          )}
          {onDelete && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(room);
              }}
              className="px-2 py-1 text-xs text-red-600 bg-red-50 rounded-md hover:bg-red-100 transition-colors"
            >
              <TrashIcon className="w-3 h-3" />
            </button>
          )}
        </div>
      )}

      {/* Updated timestamp */}
      <div className="mt-2 text-xs text-gray-400 text-center">
        Update: {new Date(room.updated_at).toLocaleDateString('id-ID')}
      </div>
    </div>
  );
};

export default RoomCard;