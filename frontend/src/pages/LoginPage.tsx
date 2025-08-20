import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Card from '../components/ui/Card';
import { UsersIcon } from '../components/icons/index';
import { secureStorage, sanitizeInput } from '../utils/security';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    // Sanitize input to prevent XSS
    const sanitizedValue = sanitizeInput(value);
    
    setFormData(prev => ({
      ...prev,
      [name]: sanitizedValue
    }));
    setError(''); // Clear error when user types
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // For demo purposes, accept any username/password
      if (formData.username && formData.password) {
        const userData = JSON.stringify({
          username: formData.username,
          role: 'admin',
          loginTime: new Date().toISOString()
        });
        
        // Use secure storage
        if (secureStorage.set('user', userData)) {
          navigate('/dashboard');
        } else {
          setError('Gagal menyimpan data login. Silakan coba lagi.');
        }
      } else {
        setError('Username dan password harus diisi');
      }
    } catch (err) {
      setError('Gagal login. Silakan coba lagi.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto w-20 h-20 bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl flex items-center justify-center shadow-xl">
            <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
          <h2 className="mt-6 text-3xl font-bold bg-gradient-to-r from-blue-700 to-blue-900 bg-clip-text text-transparent">
            SENSUS-RS
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Sistem Prediksi Indikator Rumah Sakit
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Masuk untuk mengakses dashboard
          </p>
        </div>

        {/* Login Form */}
        <Card variant="elevated" className="mt-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <Input
                label="Username"
                name="username"
                type="text"
                value={formData.username}
                onChange={handleChange}
                placeholder="Masukkan username"
                leftIcon={<UsersIcon className="w-4 h-4" />}
                variant="medical"
                required
              />
            </div>

            <div>
              <Input
                label="Password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="Masukkan password"
                leftIcon={
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                }
                variant="medical"
                required
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <Button
              type="submit"
              variant="primary"
              loading={loading}
              className="w-full"
              size="lg"
            >
              {loading ? 'Sedang Login...' : 'Masuk ke Dashboard'}
            </Button>
          </form>

          {/* Demo Credentials */}
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm font-medium text-blue-800 mb-2">Demo Login:</p>
            <div className="text-xs text-blue-700 space-y-1">
              <p>Username: <span className="font-mono bg-blue-100 px-1 rounded">admin</span></p>
              <p>Password: <span className="font-mono bg-blue-100 px-1 rounded">password</span></p>
              <p className="text-blue-600 mt-2 italic">* Atau gunakan username/password apa saja</p>
            </div>
          </div>
        </Card>

        {/* Footer */}
        <div className="text-center text-xs text-gray-500 space-y-1">
          <p>© 2025 SENSUS-RS - Sistem Prediksi BOR</p>
          <p>🏥 Tugas Akhir | 🤖 SARIMA Model | ⚡ React + FastAPI</p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
