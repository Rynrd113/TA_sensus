import React from 'react';
import { useForm } from '../../hooks/useForm';
import { sensusService } from '../../services/sensusService';
import { SensusCreate } from '../../types/Sensus';
import { Bangsal } from '../../types/Common';
import Button from '../ui/Button';
import Input, { Select } from '../ui/Input';
import Card from '../ui/Card';
import { CalendarIcon, UsersIcon, BedIcon } from '../icons/index';

interface SensusFormProps {
  onSuccess?: () => void;
  bangsalList?: Bangsal[];
  className?: string;
}

const SensusForm: React.FC<SensusFormProps> = ({ 
  onSuccess, 
  bangsalList = [],
  className 
}) => {
  const initialData: SensusCreate = {
    tanggal: new Date().toISOString().split('T')[0],
    jumlah_tempat_tidur: 0,
    tempat_tidur_terisi: 0,
    pasien_masuk: 0,
    pasien_keluar: 0,
    lama_rawat_rata_rata: 0,
    bangsal_id: bangsalList[0]?.id || 1
  };

  const validationRules = {
    tanggal: (value: string) => {
      if (!value) return 'Tanggal harus diisi';
      return null;
    },
    jumlah_tempat_tidur: (value: number) => {
      if (value < 1) return 'Jumlah tempat tidur minimal 1';
      if (value > 1000) return 'Jumlah tempat tidur maksimal 1000';
      return null;
    },
    tempat_tidur_terisi: (value: number) => {
      if (value < 0) return 'Tempat tidur terisi tidak boleh negatif';
      return null;
    },
    pasien_masuk: (value: number) => {
      if (value < 0) return 'Pasien masuk tidak boleh negatif';
      return null;
    },
    pasien_keluar: (value: number) => {
      if (value < 0) return 'Pasien keluar tidak boleh negatif';
      return null;
    },
    lama_rawat_rata_rata: (value: number) => {
      if (value < 0) return 'Lama rawat rata-rata tidak boleh negatif';
      return null;
    }
  };

  const {
    values,
    loading,
    errors,
    handleChange,
    handleSubmit,
    resetForm
  } = useForm<SensusCreate>({
    initialValues: initialData,
    validationRules,
    onSubmit: async (data) => {
      await sensusService.createSensus(data);
      resetForm();
      onSuccess?.();
    }
  });

  const bangsalOptions = bangsalList.length > 0 
    ? bangsalList.map(bangsal => ({
        value: bangsal.id,
        label: bangsal.nama_bangsal
      }))
    : [{ value: 1, label: 'Loading...' }];

  // Show loading state if no bangsal data yet
  if (bangsalList.length === 0) {
    return (
      <Card 
        title="Input Data Sensus Harian"
        subtitle="Memuat data bangsal..."
        variant="default"
        className={className}
      >
        <div className="flex justify-center py-8">
          <div className="animate-spin w-8 h-8 border-4 border-primary-200 border-t-primary-500 rounded-full"></div>
        </div>
      </Card>
    );
  }

  return (
    <Card 
      title="Input Data Sensus Harian"
      subtitle="Masukkan data sensus pasien untuk perhitungan indikator"
      variant="default"
      className={className}
    >
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Row 1: Tanggal & Bangsal */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Tanggal Sensus"
            name="tanggal"
            type="date"
            value={values.tanggal}
            onChange={handleChange('tanggal')}
            error={errors.tanggal}
            variant="medical"
            leftIcon={<CalendarIcon className="w-4 h-4" />}
            required
          />

          <Select
            label="Bangsal"
            name="bangsal_id"
            value={values.bangsal_id}
            onChange={handleChange('bangsal_id')}
            options={bangsalOptions}
            error={errors.bangsal_id}
            required
          />
        </div>

        {/* Row 2: Tempat Tidur */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Jumlah Tempat Tidur"
            name="jumlah_tempat_tidur"
            type="number"
            value={values.jumlah_tempat_tidur}
            onChange={handleChange('jumlah_tempat_tidur')}
            error={errors.jumlah_tempat_tidur}
            variant="medical"
            leftIcon={<BedIcon className="w-4 h-4" />}
            min="1"
            helperText="Total kapasitas tempat tidur"
            required
          />

          <Input
            label="Tempat Tidur Terisi"
            name="tempat_tidur_terisi"
            type="number"
            value={values.tempat_tidur_terisi}
            onChange={handleChange('tempat_tidur_terisi')}
            error={errors.tempat_tidur_terisi}
            variant="medical"
            leftIcon={<BedIcon className="w-4 h-4" />}
            min="0"
            max={values.jumlah_tempat_tidur}
            helperText="Jumlah tempat tidur yang terisi"
            required
          />
        </div>

        {/* Row 3: Pasien Masuk/Keluar */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Pasien Masuk"
            name="pasien_masuk"
            type="number"
            value={values.pasien_masuk}
            onChange={handleChange('pasien_masuk')}
            error={errors.pasien_masuk}
            variant="medical"
            min="0"
            helperText="Jumlah pasien yang masuk hari ini"
            required
          />

          <Input
            label="Pasien Keluar"
            name="pasien_keluar"
            type="number"
            value={values.pasien_keluar}
            onChange={handleChange('pasien_keluar')}
            error={errors.pasien_keluar}
            variant="medical"
            min="0"
            helperText="Jumlah pasien yang keluar hari ini"
            required
          />
        </div>

        {/* Row 4: Lama Rawat */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Lama Rawat Rata-rata (hari)"
            name="lama_rawat_rata_rata"
            type="number"
            step="0.1"
            value={values.lama_rawat_rata_rata}
            onChange={handleChange('lama_rawat_rata_rata')}
            error={errors.lama_rawat_rata_rata}
            variant="medical"
            min="0"
            helperText="Average Length of Stay dalam hari"
            required
          />
        </div>

        {/* Submit Button */}
        <div className="flex justify-end space-x-3 pt-4 border-t border-blue-200">
          <Button
            type="button"
            variant="ghost"
            onClick={resetForm}
            disabled={loading}
          >
            Reset
          </Button>
          
          <Button
            type="submit"
            variant="primary"
            loading={loading}
            icon={<UsersIcon className="w-4 h-4" />}
          >
            {loading ? 'Menyimpan...' : 'Simpan Data Sensus'}
          </Button>
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <div className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs font-bold">
              i
            </div>
            <div className="text-sm text-blue-700">
              <p className="font-medium mb-1">Informasi Penting:</p>
              <ul className="list-disc list-inside space-y-1 text-xs">
                <li>Data akan digunakan untuk menghitung BOR, BTO, ALOS, dan TOI</li>
                <li>Pastikan data yang dimasukkan akurat dan sesuai dengan kondisi aktual</li>
                <li>Tempat tidur terisi tidak boleh melebihi total kapasitas</li>
              </ul>
            </div>
          </div>
        </div>
      </form>
    </Card>
  );
};

export default SensusForm;
