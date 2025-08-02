// frontend/src/components/ui/AlertCard.tsx
import React from 'react';

interface AlertCardProps {
  alerts: string[];
  type?: 'warning' | 'error' | 'info';
}

export default function AlertCard({ alerts, type = 'warning' }: AlertCardProps) {
  if (!alerts || alerts.length === 0) {
    return (
      <div className="p-4 bg-green-50 border-l-4 border-green-400 rounded">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
            </svg>
          </div>
          <div className="ml-3">
            <p className="text-sm text-green-700">
              Semua indikator dalam kondisi normal
            </p>
          </div>
        </div>
      </div>
    );
  }

  const typeClasses = {
    warning: 'bg-yellow-50 border-yellow-400 text-yellow-700',
    error: 'bg-red-50 border-red-400 text-red-700',
    info: 'bg-blue-50 border-blue-400 text-blue-700'
  };

  const icons = {
    warning: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
    ),
    error: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    info: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    )
  };  return (
    <div className={`p-4 border-l-4 rounded ${typeClasses[type]}`}>
      <div className="flex">
        <div className="flex-shrink-0">
          <span className="text-xl">{icons[type]}</span>
        </div>
        <div className="ml-3">
          <h3 className="text-sm font-medium">
            {type === 'warning' ? 'Peringatan' : type === 'error' ? 'Masalah Kritis' : 'Informasi'}
          </h3>
          <div className="mt-2 text-sm">
            <ul className="list-disc list-inside space-y-1">
              {alerts.map((alert, index) => (
                <li key={index}>{alert}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
