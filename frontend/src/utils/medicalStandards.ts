// Medical Standards Constants - Sinkron dengan backend
export interface MedicalThresholds {
  optimal_min: number;
  optimal_max: number;
  critical_high?: number;
  critical_low?: number;
  warning_low?: number;
  warning_high?: number;
}

export interface MedicalStandardsType {
  BOR: MedicalThresholds;
  LOS: MedicalThresholds;
  BTO: MedicalThresholds;
  TOI: MedicalThresholds;
}

// Default standards (akan di-sync dengan backend via API)
export const DEFAULT_MEDICAL_STANDARDS: MedicalStandardsType = {
  BOR: {
    optimal_min: 60.0,
    optimal_max: 85.0,
    critical_high: 90.0,
    warning_low: 50.0
  },
  LOS: {
    optimal_min: 6.0,
    optimal_max: 9.0,
    critical_high: 12.0,
    warning_low: 3.0
  },
  BTO: {
    optimal_min: 40.0,
    optimal_max: 50.0,
    critical_low: 30.0,
    warning_high: 60.0
  },
  TOI: {
    optimal_min: 1.0,
    optimal_max: 3.0,
    critical_high: 5.0,
    warning_low: 0.5
  }
};

export type EvaluationStatus = 'optimal' | 'warning' | 'critical' | 'low' | 'high';
export type EvaluationLevel = 'success' | 'warning' | 'danger' | 'info';

export interface EvaluationResult {
  status: EvaluationStatus;
  level: EvaluationLevel;
  message: string;
  recommendation: string;
}

export class MedicalStandardsEvaluator {
  private standards: MedicalStandardsType;

  constructor(standards: MedicalStandardsType = DEFAULT_MEDICAL_STANDARDS) {
    this.standards = standards;
  }

  updateStandards(newStandards: MedicalStandardsType) {
    this.standards = newStandards;
  }

  evaluateBOR(borValue: number): EvaluationResult {
    const bor = this.standards.BOR;
    
    if (borValue >= (bor.critical_high || 90)) {
      return {
        status: 'critical',
        level: 'danger',
        message: `BOR ${borValue.toFixed(1)}% sangat tinggi - Risiko overkapasitas`,
        recommendation: 'Tambah kapasitas atau percepat discharge'
      };
    } else if (borValue > bor.optimal_max) {
      return {
        status: 'warning',
        level: 'warning',
        message: `BOR ${borValue.toFixed(1)}% di atas optimal`,
        recommendation: 'Monitor kapasitas dan siapkan rencana darurat'
      };
    } else if (borValue >= bor.optimal_min) {
      return {
        status: 'optimal',
        level: 'success',
        message: `BOR ${borValue.toFixed(1)}% dalam rentang optimal`,
        recommendation: 'Pertahankan tingkat utilisasi ini'
      };
    } else {
      return {
        status: 'low',
        level: 'info',
        message: `BOR ${borValue.toFixed(1)}% rendah`,
        recommendation: 'Evaluasi strategi pemasaran/rujukan'
      };
    }
  }

  evaluateLOS(losValue: number): EvaluationResult {
    const los = this.standards.LOS;
    
    if (losValue >= (los.critical_high || 12)) {
      return {
        status: 'critical',
        level: 'danger',
        message: `LOS ${losValue.toFixed(1)} hari terlalu panjang`,
        recommendation: 'Review protokol discharge dan case management'
      };
    } else if (losValue > los.optimal_max) {
      return {
        status: 'warning',
        level: 'warning',
        message: `LOS ${losValue.toFixed(1)} hari di atas optimal`,
        recommendation: 'Evaluasi efisiensi perawatan'
      };
    } else if (losValue >= los.optimal_min) {
      return {
        status: 'optimal',
        level: 'success',
        message: `LOS ${losValue.toFixed(1)} hari dalam rentang optimal`,
        recommendation: 'Pertahankan kualitas perawatan'
      };
    } else {
      return {
        status: 'low',
        level: 'info',
        message: `LOS ${losValue.toFixed(1)} hari pendek`,
        recommendation: 'Monitor kualitas outcome pasien'
      };
    }
  }

  evaluateBTO(btoValue: number): EvaluationResult {
    const bto = this.standards.BTO;
    
    if (btoValue >= (bto.warning_high || 60)) {
      return {
        status: 'high',
        level: 'warning',
        message: `BTO ${btoValue.toFixed(1)} sangat tinggi`,
        recommendation: 'Evaluasi kualitas perawatan dan patient satisfaction'
      };
    } else if (btoValue >= bto.optimal_min) {
      return {
        status: 'optimal',
        level: 'success',
        message: `BTO ${btoValue.toFixed(1)} dalam rentang optimal`,
        recommendation: 'Pertahankan efisiensi turnover'
      };
    } else {
      return {
        status: 'low',
        level: 'info',
        message: `BTO ${btoValue.toFixed(1)} rendah`,
        recommendation: 'Evaluasi strategi admission dan discharge'
      };
    }
  }

  getStatusColor(level: EvaluationLevel): string {
    switch (level) {
      case 'success': return 'text-green-600 bg-green-50 border-green-200';
      case 'warning': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'danger': return 'text-red-600 bg-red-50 border-red-200';
      case 'info': return 'text-blue-600 bg-blue-50 border-blue-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  }

  getStatusIcon(level: EvaluationLevel): string {
    switch (level) {
      case 'success': return '✅';
      case 'warning': return '⚠️';
      case 'danger': return '🚨';
      case 'info': return 'ℹ️';
      default: return '❓';
    }
  }
}

// Singleton instance untuk use di seluruh app
export const medicalStandardsEvaluator = new MedicalStandardsEvaluator();

// Hook untuk fetch standards dari API dan update evaluator
export const useMedicalStandards = () => {
  const fetchStandards = async () => {
    try {
      const API_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api/v1';
      const response = await fetch(`${API_URL}/standards/medical`);
      if (response.ok) {
        const result = await response.json();
        medicalStandardsEvaluator.updateStandards(result.data);
        return result.data;
      }
    } catch (error) {
      console.warn('Failed to fetch medical standards from API, using defaults:', error);
    }
    return DEFAULT_MEDICAL_STANDARDS;
  };

  return { fetchStandards };
};
