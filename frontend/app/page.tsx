'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import ConfigForm from '../components/ConfigForm';
import Dashboard from '../components/Dashboard';
import AnimatedBackground from '../components/AnimatedBackground';

interface ForecastEntry {
  hour: number;
  route: string;
  pallet_volume: number;
  threshold: number;
  alert: boolean;
}

interface DelayEntry {
  truck_id: number;
  route: string;
  delay_minutes: number;
}

interface PredictionResponse {
  forecast_table: ForecastEntry[];
  delay_summary: DelayEntry[];
  alerts: string[];
}

export default function Home() {
  const [predictionData, setPredictionData] = useState<PredictionResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleConfigChange = async (config: any) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setPredictionData(data);
    } catch (err) {
      console.error('Prediction failed:', err);
      setError(err instanceof Error ? err.message : 'Failed to generate prediction');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      <AnimatedBackground />
      <div className="relative z-10 p-4 max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Pallet Flow Diagnostic Dashboard
          </h1>
          <p className="text-gray-600">
            Real-Time Predictive Pallet Flow and Delay Estimation Platform
          </p>
        </motion.div>

        {error && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700"
          >
            <strong>Error:</strong> {error}
          </motion.div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Configuration Panel */}
          <div className="lg:col-span-1">
            <ConfigForm onConfigChange={handleConfigChange} />
          </div>

          {/* Dashboard Panel */}
          <div className="lg:col-span-1">
            {isLoading ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="bg-white bg-opacity-90 backdrop-blur-sm rounded-xl shadow-lg p-8 flex items-center justify-center"
              >
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                  <p className="text-gray-600">Generating prediction...</p>
                </div>
              </motion.div>
            ) : predictionData ? (
              <Dashboard
                forecastData={predictionData.forecast_table}
                delayData={predictionData.delay_summary}
                alerts={predictionData.alerts}
              />
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="bg-white bg-opacity-90 backdrop-blur-sm rounded-xl shadow-lg p-8 text-center"
              >
                <div className="text-gray-400 mb-4">
                  <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-700 mb-2">No Data Available</h3>
                <p className="text-gray-500">
                  Configure the system parameters and click "Generate Prediction" to see the dashboard.
                </p>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
} 