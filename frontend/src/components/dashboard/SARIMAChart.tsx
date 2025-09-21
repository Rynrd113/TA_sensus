/**
 * SARIMA Prediction Component
 * Sesuai dengan penelitian: "Peramalan Indikator Rumah Sakit Berbasis Sensus Harian Rawat Inap dengan Model SARIMA"
 * 
 * Features:
 * - Training model SARIMA dengan m          <div className="flex gap-4">
            <Button
              onClick={trainModel}
              disabled={isTraining || loading}
              variant={modelTrained ? "secondary" : "primary"}
            >
              {isTraining ? (
                <div className="flex items-center gap-2">
                  <MedicalLoadingSpinner size="sm" />
                  <span>Training...</span>
                </div>
              ) : '🎯 Train Model'}
            </Button>
            {modelTrained && (
              <Button
                onClick={() => generatePrediction()}
                disabled={loading || isTraining}
                variant="primary"
              >
                {loading ? (
                  <div className="flex items-center gap-2">
                    <MedicalLoadingSpinner size="sm" />
                    <span>Predicting...</span>
                  </div>
                ) : '📈 Predict'}
              </Button>
            )}
          </div>ins
 * - Visualisasi prediksi BOR dengan confidence interval  
 * - Evaluasi performa model (RMSE, MAE, MAPE < 10%)
 * - Interpretasi klinis dan rekomendasi manajemen
 * - Performance optimization dengan debouncing dan caching
 */

import React, { useState, useEffect } from 'react';
import { 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  ReferenceLine,
  ComposedChart
} from 'recharts';
import { apiClient } from '../../services/apiClient';
import { Card, Button } from '../ui';
import { MedicalLoadingSpinner } from '../ui/LoadingStates';

interface SARIMAPrediction {
  values: number[];
  dates: string[];
  confidence_interval?: {
    lower: number[];
    upper: number[];
  };
  average_predicted_bor: number;
}

interface ModelPerformance {
  last_training_mape: number;
  meets_journal_criteria: boolean;
  model_parameters: {
    order: number[];
    seasonal_order: number[];
  };
}

interface ClinicalAlerts {
  high_occupancy_warning: boolean;
  low_occupancy_warning: boolean;
  recommendations: string[];
}

interface ClinicalInterpretation {
  high_risk_days: number;
  low_utilization_days: number;
  optimal_days: number;
  average_predicted_bor: number;
  warnings: {
    overutilization_risk: boolean;
    underutilization_risk: boolean;
  };
  recommendations: string[];
}

interface SARIMAResponse {
  status: string;
  forecast_period: number;
  predictions: SARIMAPrediction;
  interpretation: ClinicalInterpretation;
  model_performance: ModelPerformance;
  clinical_alerts: ClinicalAlerts;
}

interface TrainingResponse {
  status: string;
  message: string;
  performance_metrics: {
    rmse: number;
    mae: number;
    mape: number;
    r_squared: number;
  };
  journal_compliance: {
    meets_mape_criteria: boolean;
    actual_mape: string;
  };
}

const SARIMAChart: React.FC = () => {
  const [prediction, setPrediction] = useState<SARIMAResponse | null>(null);
  const [trainingResults, setTrainingResults] = useState<TrainingResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [isTraining, setIsTraining] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modelTrained, setModelTrained] = useState(false);

  // Check model status on component mount
  useEffect(() => {
    checkModelStatus();
  }, []);

  const checkModelStatus = async () => {
    try {
      const response = await apiClient.get('/sarima/status') as any;
      if (response && typeof response.model_trained === 'boolean') {
        setModelTrained(response.model_trained);
      } else {
        console.warn('Invalid response from /sarima/status:', response);
        setModelTrained(false);
      }
    } catch (error) {
      console.error('Error checking model status:', error);
      setModelTrained(false);
    }
  };

  const trainModel = async () => {
    setIsTraining(true);
    setError(null);
    
    try {
      const response = await apiClient.post('/sarima/train', {
        days_back: 90,
        optimize_parameters: true,
        target_column: 'bor'
      }) as any;
      
      setTrainingResults(response);
      setModelTrained(true);
      
      // Auto predict after training if successful
      if (response.journal_compliance?.meets_mape_criteria) {
        await generatePrediction();
      }
      
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Error training model');
      console.error('Training error:', error);
    } finally {
      setIsTraining(false);
    }
  };

  const generatePrediction = async (daysAhead: number = 7) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiClient.get('/sarima/predict', {
        params: {
          days_ahead: daysAhead,
          include_confidence: true
        }
      }) as any;
      
      setPrediction(response);
      
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Error generating prediction');
      console.error('Prediction error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Prepare chart data
  const chartData = prediction ? prediction.predictions.dates.map((date, index) => ({
    date: new Date(date).toLocaleDateString('id-ID', { 
      day: '2-digit', 
      month: 'short' 
    }),
    fullDate: date,
    predicted_bor: prediction.predictions.values[index],
    lower_bound: prediction.predictions.confidence_interval?.lower[index],
    upper_bound: prediction.predictions.confidence_interval?.upper[index]
  })) : [];

  const getPerformanceColor = (mape: number) => {
    if (mape < 5) return 'bg-green-100 border-green-300';
    if (mape < 10) return 'bg-blue-100 border-blue-300';
    return 'bg-orange-100 border-orange-300';
  };

  const getPerformanceLevel = (mape: number) => {
    if (mape < 5) return 'Excellent';
    if (mape < 10) return 'Good';
    return 'Needs Improvement';
  };

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <Card className="p-6">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              🧠 Prediksi BOR - Model SARIMA
            </h2>
            <p className="text-gray-600 mt-1">
              Seasonal ARIMA untuk peramalan indikator rumah sakit
            </p>
          </div>
          <div className="flex space-x-3">
            <Button
              onClick={trainModel}
              disabled={isTraining}
              variant={modelTrained ? 'secondary' : 'primary'}
            >
              {isTraining ? '⏳ Training...' : '🎯 Train Model'}
            </Button>
            {modelTrained && (
              <Button
                onClick={() => generatePrediction()}
                disabled={loading}
                variant="primary"
              >
                {loading ? '📊 Loading...' : '📈 Predict'}
              </Button>
            )}
          </div>
        </div>

        {/* Training Results */}
        {trainingResults && (
          <div className={`p-4 rounded-lg border-2 ${
            trainingResults.journal_compliance.meets_mape_criteria ? 
            'bg-green-50 border-green-200' : 
            'bg-orange-50 border-orange-200'
          }`}>
            <div className="grid grid-cols-4 gap-4">
              <div className="text-center">
                <p className="text-sm font-medium text-gray-600">MAPE</p>
                <p className={`text-xl font-bold ${
                  trainingResults.performance_metrics.mape < 10 ? 'text-green-600' : 'text-orange-600'
                }`}>
                  {trainingResults.performance_metrics.mape.toFixed(2)}%
                </p>
                <p className="text-xs text-gray-500">Target: &lt; 10%</p>
              </div>
              <div className="text-center">
                <p className="text-sm font-medium text-gray-600">RMSE</p>
                <p className="text-xl font-bold text-blue-600">
                  {trainingResults.performance_metrics.rmse.toFixed(3)}
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm font-medium text-gray-600">MAE</p>
                <p className="text-xl font-bold text-purple-600">
                  {trainingResults.performance_metrics.mae.toFixed(3)}
                </p>
              </div>
              <div className="text-center">
                <p className="text-sm font-medium text-gray-600">Journal Compliance</p>
                <div className="flex items-center justify-center space-x-1">
                  <span className={`text-lg ${
                    trainingResults.journal_compliance.meets_mape_criteria ? '✅' : '⚠️'
                  }`}>
                    {trainingResults.journal_compliance.meets_mape_criteria ? '✅' : '⚠️'}
                  </span>
                  <span className={`text-sm font-medium ${
                    trainingResults.journal_compliance.meets_mape_criteria ? 'text-green-600' : 'text-orange-600'
                  }`}>
                    {trainingResults.journal_compliance.meets_mape_criteria ? 'Met' : 'Not Met'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </Card>

      {/* Prediction Chart */}
      {loading && (
        <Card className="p-6">
          <div className="text-center py-8">
            <MedicalLoadingSpinner 
              size="lg" 
              message="Memproses prediksi SARIMA..." 
            />
          </div>
        </Card>
      )}
      
      {prediction && !loading && (
        <Card className="p-6">
          <h3 className="text-xl font-semibold mb-4">
            📊 Prediksi BOR - {prediction.forecast_period} Hari
          </h3>
          <div className="h-96 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }}
                />
                <YAxis 
                  domain={[0, 100]} 
                  tick={{ fontSize: 12 }}
                  label={{ value: 'BOR (%)', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip 
                  formatter={(value: any, name: string) => [
                    `${Number(value).toFixed(1)}%`,
                    name === 'predicted_bor' ? 'Prediksi BOR' :
                    name === 'lower_bound' ? 'Batas Bawah' : 
                    name === 'upper_bound' ? 'Batas Atas' : name
                  ]}
                  labelFormatter={(label) => `Tanggal: ${label}`}
                />
                <Legend />
                
                {/* Reference lines untuk BOR optimal */}
                <ReferenceLine 
                  y={85} 
                  stroke="#ef4444" 
                  strokeDasharray="5 5" 
                  label="Overutilization (85%)"
                />
                <ReferenceLine 
                  y={60} 
                  stroke="#f59e0b" 
                  strokeDasharray="5 5" 
                  label="Underutilization (60%)"
                />
                
                {/* Confidence interval */}
                <Line 
                  type="monotone" 
                  dataKey="lower_bound" 
                  stroke="#94A3B8" 
                  strokeWidth={1}
                  strokeDasharray="5 5"
                  dot={false}
                  name="CI Lower"
                />
                <Line 
                  type="monotone" 
                  dataKey="upper_bound" 
                  stroke="#94A3B8" 
                  strokeWidth={1}
                  strokeDasharray="5 5"
                  dot={false}
                  name="CI Upper"
                />
                
                {/* Main prediction line */}
                <Line 
                  type="monotone" 
                  dataKey="predicted_bor" 
                  stroke="#3B82F6" 
                  strokeWidth={3}
                  dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
                  name="Prediksi BOR"
                />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </Card>
      )}

      {/* Clinical Interpretation */}
      {prediction && (
        <div className="grid md:grid-cols-2 gap-6">
          {/* Performance Summary */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              🎯 Model Performance
            </h3>
            <div className={`p-4 rounded-lg border-2 ${getPerformanceColor(prediction.model_performance.last_training_mape)}`}>
              <div className="flex justify-between items-center">
                <span className="font-medium">MAPE Score</span>
                <span className="text-xl font-bold">
                  {prediction.model_performance.last_training_mape.toFixed(2)}%
                </span>
              </div>
              <div className="flex justify-between items-center mt-1">
                <span className="text-sm">Performance Level</span>
                <span className="text-sm font-medium">
                  {getPerformanceLevel(prediction.model_performance.last_training_mape)}
                </span>
              </div>
            </div>
            
            <div className="text-sm space-y-2 mt-4">
              <p><strong>Model Parameters:</strong></p>
              <p>• Order: {prediction.model_performance.model_parameters.order.join(', ')}</p>
              <p>• Seasonal Order: {prediction.model_performance.model_parameters.seasonal_order.join(', ')}</p>
              <p>• Methodology: Box-Jenkins SARIMA</p>
            </div>
          </Card>

          {/* Clinical Alerts & Interpretation */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center">
              ℹ️ Interpretasi Klinis
            </h3>
            <div className="grid grid-cols-3 gap-3 text-center mb-4">
              <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                <div className="text-xl font-bold text-green-600">
                  {prediction.interpretation.optimal_days}
                </div>
                <div className="text-xs text-green-700">Hari Optimal</div>
                <div className="text-xs text-gray-500">(60-85%)</div>
              </div>
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <div className="text-xl font-bold text-red-600">
                  {prediction.interpretation.high_risk_days}
                </div>
                <div className="text-xs text-red-700">Risiko Tinggi</div>
                <div className="text-xs text-gray-500">(&gt;85%)</div>
              </div>
              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="text-xl font-bold text-yellow-600">
                  {prediction.interpretation.low_utilization_days}
                </div>
                <div className="text-xs text-yellow-700">Utilisasi Rendah</div>
                <div className="text-xs text-gray-500">(&lt;60%)</div>
              </div>
            </div>

            <div className="space-y-2">
              <p className="font-medium text-gray-700">📋 Rekomendasi:</p>
              <ul className="text-sm space-y-1">
                {prediction.clinical_alerts.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <span className="text-blue-500 mt-1">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Alerts */}
            {(prediction.clinical_alerts.high_occupancy_warning || prediction.clinical_alerts.low_occupancy_warning) && (
              <div className="p-3 border-l-4 border-amber-400 bg-amber-50 mt-4">
                <div className="flex items-center space-x-2">
                  <span className="text-xl">⚠️</span>
                  <span className="font-medium text-amber-800">Clinical Alerts</span>
                </div>
                <div className="text-sm text-amber-700 mt-1">
                  {prediction.clinical_alerts.high_occupancy_warning && (
                    <p>⚠️ High occupancy warning detected</p>
                  )}
                  {prediction.clinical_alerts.low_occupancy_warning && (
                    <p>⚠️ Low utilization warning detected</p>
                  )}
                </div>
              </div>
            )}
          </Card>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <Card className="p-6 border-red-200 bg-red-50">
          <div className="flex items-center space-x-2 text-red-600">
            <span className="text-xl">⚠️</span>
            <span className="font-medium">Error</span>
          </div>
          <p className="text-red-700 mt-2">{error}</p>
        </Card>
      )}
    </div>
  );
};

export default SARIMAChart;