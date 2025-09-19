// frontend/src/components/dashboard/MedicalIndicatorCard.tsx
import React from 'react';
import { medicalStandardsEvaluator, EvaluationResult } from '../../utils/medicalStandards';

interface MedicalIndicatorCardProps {
  title: string;
  value: number;
  unit?: string;
  indicatorType: 'BOR' | 'LOS' | 'BTO' | 'TOI';
  icon?: React.ReactNode;
  className?: string;
  showRecommendation?: boolean;
}

const MedicalIndicatorCard: React.FC<MedicalIndicatorCardProps> = ({
  title,
  value,
  unit = '',
  indicatorType,
  icon,
  className = '',
  showRecommendation = true
}) => {
  // Evaluasi menggunakan medical standards
  const getEvaluation = (): EvaluationResult => {
    switch (indicatorType) {
      case 'BOR':
        return medicalStandardsEvaluator.evaluateBOR(value);
      case 'LOS':
        return medicalStandardsEvaluator.evaluateLOS(value);
      case 'BTO':
        return medicalStandardsEvaluator.evaluateBTO(value);
      default:
        return {
          status: 'optimal',
          level: 'info',
          message: `${indicatorType} ${value}${unit}`,
          recommendation: 'Monitor nilai ini secara berkala'
        };
    }
  };

  const evaluation = getEvaluation();
  const statusColor = medicalStandardsEvaluator.getStatusColor(evaluation.level);
  const statusIcon = medicalStandardsEvaluator.getStatusIcon(evaluation.level);

  return (
    <div className={`rounded-lg border p-6 shadow-sm hover:shadow-md transition-all duration-200 ${statusColor} ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {icon && <div className="text-xl">{icon}</div>}
          <h3 className="text-sm font-semibold">{title}</h3>
        </div>
        <div className="text-lg">{statusIcon}</div>
      </div>
      
      {/* Main Value */}
      <div className="mb-3">
        <span className="text-3xl font-bold">
          {Number.isInteger(value) ? value.toString() : value.toFixed(1)}
        </span>
        {unit && (
          <span className="text-lg font-medium ml-1 opacity-80">
            {unit}
          </span>
        )}
      </div>
      
      {/* Status Badge */}
      <div className="mb-3">
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
          evaluation.level === 'success' ? 'bg-green-100 text-green-800' :
          evaluation.level === 'warning' ? 'bg-yellow-100 text-yellow-800' :
          evaluation.level === 'danger' ? 'bg-red-100 text-red-800' :
          'bg-blue-100 text-blue-800'
        }`}>
          {evaluation.status.charAt(0).toUpperCase() + evaluation.status.slice(1)}
        </span>
      </div>

      {/* Status Message */}
      <p className="text-sm font-medium mb-2">
        {evaluation.message}
      </p>

      {/* Recommendation */}
      {showRecommendation && (
        <div className="pt-3 border-t border-current border-opacity-20">
          <p className="text-xs opacity-80">
            <strong>Rekomendasi:</strong> {evaluation.recommendation}
          </p>
        </div>
      )}
    </div>
  );
};

export default MedicalIndicatorCard;